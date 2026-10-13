"""Per-user installation, Windows integration and uninstall.

GotoBed.exe installs itself on first start to %LOCALAPPDATA%\\Programs\\GotoBed
(always writable without admin rights, so the self-updater works), adds a
Start menu shortcut and an "Apps & features" entry, and can remove all of
that again with --uninstall.
"""
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import instance
import updater
from config import APP_NAME
from version import __version__

log = logging.getLogger(__name__)

EXE_NAME = 'GotoBed.exe'
DISPLAY_NAME = 'Go-to-Bed'
PUBLISHER = 'zGLados'
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
UNINSTALL_KEY = rf'Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}'
CREATE_NO_WINDOW = 0x08000000


class InstallError(Exception):
    """Installing failed; the app can still run from where it is."""


def install_dir() -> Path:
    """Where Go-to-Bed installs itself (GOTOBED_INSTALL_DIR overrides it for tests)."""
    override = os.getenv('GOTOBED_INSTALL_DIR')
    if override:
        return Path(override)
    base = os.getenv('LOCALAPPDATA') or str(Path.home() / 'AppData' / 'Local')
    return Path(base) / 'Programs' / APP_NAME


def installed_exe() -> Path:
    return install_dir() / EXE_NAME


def shortcut_path() -> Path:
    appdata = os.getenv('APPDATA') or str(Path.home() / 'AppData' / 'Roaming')
    return Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / f'{DISPLAY_NAME}.lnk'


def _same_file(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def is_installed(exe: Path) -> bool:
    """Whether `exe` is the installed copy."""
    return _same_file(exe, installed_exe())


def needs_install(exe: Path) -> bool:
    """Whether this exe should install itself before running."""
    return updater.is_supported() and not is_installed(exe)


def install_self(exe: Path) -> Path:
    """Copy `exe` to the install folder unless the same or a newer version is already there.

    Returns the installed exe, which the caller should start.
    """
    target = installed_exe()
    if target.exists():
        existing = updater.version_of(target)
        if existing and updater.parse_version(existing) >= updater.parse_version(__version__):
            log.info("v%s already installed at %s - starting it", existing, target)
            return target
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        new_exe, _ = updater.exe_paths(target)
        shutil.copy2(exe, new_exe)
        if target.exists():
            updater.install(new_exe, target)
        else:
            os.replace(new_exe, target)
    except (OSError, updater.UpdateError) as e:
        raise InstallError(f'Could not install to {target.parent}: {e}') from e
    log.info("Installed v%s to %s", __version__, target)
    return target


# ---------------------------------------------------------------------- taking over from older versions

def running_instances() -> List[Tuple[int, Path]]:
    """(pid, exe path) of all running Go-to-Bed processes (including this one)."""
    if sys.platform == 'win32':
        try:
            out = subprocess.run(
                ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
                 "Get-CimInstance Win32_Process -Filter \"Name='GotoBed.exe'\" | "
                 "ForEach-Object { \"$($_.ProcessId)|$($_.ExecutablePath)\" }"],
                capture_output=True, text=True, timeout=60, creationflags=CREATE_NO_WINDOW,
                stdin=subprocess.DEVNULL
            ).stdout
        except Exception as e:
            log.warning("Could not list processes: %s", e)
            return []
        result = []
        for line in out.splitlines():
            pid, _, path = line.strip().partition('|')
            if pid.isdigit() and path:
                result.append((int(pid), Path(path)))
        return result
    result = []  # other platforms: local tests with a Linux build
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            exe = Path(os.readlink(proc / 'exe'))
        except OSError:
            continue
        if exe.name in ('GotoBed', EXE_NAME):
            result.append((int(proc.name), exe))
    return result


def _kill(pid: int) -> None:
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True, creationflags=CREATE_NO_WINDOW)
    else:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def plan_takeover(running: Dict[Path, Optional[str]], own_version: str = __version__) -> Optional[List[Path]]:
    """Decide which running instances to stop: all of them, unless one is the same or a newer version.

    `running` maps exe path -> reported version (None = too old to report one, e.g. 3.0.0).
    Returns the paths to stop, or None if this exe must not take over.
    """
    for version in running.values():
        if version is not None and updater.parse_version(version) >= updater.parse_version(own_version):
            return None
    return list(running)


def take_over(own_exe: Path) -> Optional[List[Path]]:
    """Stop running older Go-to-Bed instances so this exe can install itself.

    Returns the stopped exes (empty list if none could be found), or None if a
    same or newer version is running and must be left alone.
    """
    others = [(pid, path) for pid, path in running_instances() if not _same_file(path, own_exe)]
    if not others:
        return []
    paths = {os.path.normcase(str(path)): path for _, path in others}
    versions = {path: updater.version_of(path) if path.exists() else None for path in paths.values()}
    if plan_takeover(versions) is None:
        log.info("A same or newer version is running: %s", versions)
        return None

    log.info("Stopping older running version(s): %s", list(paths.values()))
    # 3.1+ listens for the quit signal and exits cleanly; 3.0.0 has none and is stopped right away
    deadline = time.monotonic() + (10 if instance.request_quit() else 0)
    pids = {pid for pid, _ in others}
    while time.monotonic() < deadline and pids & {pid for pid, _ in running_instances()}:
        time.sleep(1)
    for pid in pids & {pid for pid, _ in running_instances()}:
        _kill(pid)  # 3.0.0 has no quit signal
    return list(paths.values())


def autostart_path() -> Optional[Path]:
    """The exe the autostart entry currently points to."""
    if sys.platform != 'win32':
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
    except OSError:
        return None
    return Path(str(value).strip().strip('"')) if value else None


def legacy_exes(own_exe: Path, candidates: Iterable[Optional[Path]]) -> List[Path]:
    """Old, not installed Go-to-Bed exes among `candidates` that the installation replaces."""
    result = []
    for path in candidates:
        if (path is None or not path.exists() or path.suffix.lower() not in ('.exe', '')
                or _same_file(path, own_exe) or is_installed(path) or any(_same_file(path, p) for p in result)):
            continue
        version = updater.version_of(path)
        if version is None or updater.parse_version(version) < updater.parse_version(__version__):
            result.append(path)
    return result


def replace_legacy(paths: Iterable[Path], installed: Path) -> List[Path]:
    """Delete old exes and put a shortcut to the installed one in their place. Returns the replaced paths."""
    replaced = []
    for path in paths:
        for _ in range(30):  # the old process may still be exiting
            try:
                path.unlink(missing_ok=True)
                break
            except OSError:
                time.sleep(1)
        if path.exists():
            log.warning("Could not delete old version %s", path)
            continue
        if sys.platform == 'win32':
            try:
                create_shortcut(path.parent / f'{DISPLAY_NAME}.lnk', installed)
            except Exception as e:
                log.warning("Could not create shortcut in %s: %s", path.parent, e)
        replaced.append(path)
        log.info("Replaced old version %s", path)
    return replaced


# ---------------------------------------------------------------------- Windows integration

def set_autostart(enabled: bool, exe: Path) -> None:
    """Add or remove the autostart entry for `exe`."""
    if sys.platform != 'win32':
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass


def _powershell(script: str, wait: bool = True, **env: str) -> None:
    """Run a PowerShell snippet without a window; values are passed via environment variables."""
    args = ['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-Command', script]
    full_env = {**os.environ, **env}
    if wait:
        subprocess.run(args, env=full_env, creationflags=CREATE_NO_WINDOW, timeout=60, check=True,
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen(args, env=full_env, creationflags=CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def register(exe: Path) -> None:
    """Create/refresh the Start menu shortcut and the "Apps & features" entry. Safe to call on every start."""
    if sys.platform != 'win32':
        return
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY) as key:
        values = {
            'DisplayName': DISPLAY_NAME,
            'DisplayVersion': __version__,
            'Publisher': PUBLISHER,
            'DisplayIcon': f'{exe},0',
            'InstallLocation': str(exe.parent),
            'UninstallString': f'"{exe}" --uninstall',
            'QuietUninstallString': f'"{exe}" --uninstall --quiet',
            'URLInfoAbout': f'https://github.com/{updater.REPO}',
        }
        for name, value in values.items():
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.SetValueEx(key, 'NoModify', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'NoRepair', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'EstimatedSize', 0, winreg.REG_DWORD, exe.stat().st_size // 1024)

    if not shortcut_path().exists():
        create_shortcut(shortcut_path(), exe)
    log.info("Registered %s (Start menu, Apps & features)", exe)


def create_shortcut(link: Path, exe: Path) -> None:
    """Create a Windows .lnk shortcut to `exe`."""
    _powershell(
        '$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:GTB_LINK);'
        '$s.TargetPath = $env:GTB_EXE; $s.WorkingDirectory = $env:GTB_DIR;'
        '$s.Description = "Bedtime reminder"; $s.Save()',
        GTB_LINK=str(link), GTB_EXE=str(exe), GTB_DIR=str(exe.parent)
    )


def uninstall(exe: Path, data_dir: Optional[Path]) -> None:
    """Remove autostart, shortcut, "Apps & features" entry and - after this process exits - the program files.

    `data_dir` is deleted too if given (settings and statistics).
    """
    if sys.platform == 'win32':
        import winreg
        set_autostart(False, exe)
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_KEY)
        except FileNotFoundError:
            pass
        shortcut_path().unlink(missing_ok=True)

    # A running exe cannot delete itself on Windows: a hidden PowerShell waits
    # until this process (and the PyInstaller bootloader) has exited.
    program_dir = exe.parent if is_installed(exe) else None
    if sys.platform == 'win32':
        _powershell(
            'Start-Sleep -Seconds 2;'
            'for ($i = 0; $i -lt 30; $i++) {'
            '  Remove-Item -LiteralPath $env:GTB_EXE -Force -ErrorAction SilentlyContinue;'
            '  if (-not (Test-Path -LiteralPath $env:GTB_EXE)) { break }; Start-Sleep -Seconds 1 };'
            'if ($env:GTB_DIR) { Remove-Item -LiteralPath $env:GTB_DIR -Recurse -Force -ErrorAction SilentlyContinue };'
            'if ($env:GTB_DATA) { Remove-Item -LiteralPath $env:GTB_DATA -Recurse -Force -ErrorAction SilentlyContinue }',
            wait=False,
            GTB_EXE=str(exe), GTB_DIR=str(program_dir or ''), GTB_DATA=str(data_dir or '')
        )
    else:
        exe.unlink(missing_ok=True)  # allowed while running on other platforms (local tests)
        if program_dir:
            shutil.rmtree(program_dir, ignore_errors=True)
        if data_dir:
            shutil.rmtree(data_dir, ignore_errors=True)
    log.info("Uninstalled %s (data %s)", exe, 'deleted' if data_dir else 'kept')
