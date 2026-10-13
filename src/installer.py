"""Per-user installation, Windows integration and uninstall.

GotoBed.exe installs itself on first start to %LOCALAPPDATA%\\Programs\\GotoBed
(always writable without admin rights, so the self-updater works), adds a
Start menu shortcut and an "Apps & features" entry, and can remove all of
that again with --uninstall.
"""
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

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

    link = shortcut_path()
    if not link.exists():
        _powershell(
            '$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:GTB_LINK);'
            '$s.TargetPath = $env:GTB_EXE; $s.WorkingDirectory = $env:GTB_DIR;'
            '$s.Description = "Bedtime reminder"; $s.Save()',
            GTB_LINK=str(link), GTB_EXE=str(exe), GTB_DIR=str(exe.parent)
        )
    log.info("Registered %s (Start menu, Apps & features)", exe)


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
