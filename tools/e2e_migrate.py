"""End-to-end test of the migration from a running 3.0.0 to the new version.

Usage: python tools/e2e_migrate.py LEGACY_EXE NEW_EXE

LEGACY_EXE is a build of v3.0.0 (no updater, no installer). It is started
from a fake Desktop folder, then NEW_EXE is started from a fake Downloads
folder - the only thing a user has to do. Passes when the new version stops
the old one, installs itself, takes over the settings and autostart and
replaces the old exe with a shortcut. Cleans up with --uninstall --quiet.

On Windows this touches the real HKCU registry, Start menu and processes
named GotoBed.exe - meant for CI runners only.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WINDOWS = sys.platform == 'win32'
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def wait_for(condition, timeout: float, what: str) -> None:
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            sys.exit(f'FAIL: timed out waiting for {what}')
        time.sleep(1)


def autostart_value() -> str:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            return str(winreg.QueryValueEx(key, 'GotoBed')[0]).strip('"')
    except OSError:
        return ''


def running(path: Path) -> bool:
    if WINDOWS:
        out = subprocess.run(
            ['powershell.exe', '-NoProfile', '-Command',
             "Get-CimInstance Win32_Process -Filter \"Name='GotoBed.exe'\" | ForEach-Object { $_.ExecutablePath }"],
            capture_output=True, text=True).stdout
        return any(os.path.normcase(line.strip()) == os.path.normcase(str(path)) for line in out.splitlines())
    for proc in Path('/proc').glob('[0-9]*'):  # match the program file, not the command line
        try:
            if os.readlink(proc / 'exe') == str(path):
                return True
        except OSError:
            pass
    return False


def main() -> None:
    legacy_src, new_src = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    tmp = Path(tempfile.mkdtemp(prefix='gotobed-e2e-migrate-'))
    desktop, downloads, install_dir, data = tmp / 'Desktop', tmp / 'Downloads', tmp / 'Programs' / 'GotoBed', tmp / 'data'
    for d in (desktop, downloads):
        d.mkdir()
    legacy = desktop / ('GotoBed.exe' if WINDOWS else 'GotoBed')
    downloaded = downloads / new_src.name
    shutil.copy2(legacy_src, legacy)
    shutil.copy2(new_src, downloaded)
    installed = install_dir / 'GotoBed.exe'

    os.environ.update({
        'GOTOBED_INSTALL_DIR': str(install_dir),
        'GOTOBED_DATA_DIR': str(data),
        'GOTOBED_ANY_PLATFORM': '1',
        'GOTOBED_UPDATE_URL': 'http://127.0.0.1:1/none',
    })
    log_file = data / 'gotobed.log'

    def log_text() -> str:
        return log_file.read_text(encoding='utf-8', errors='replace') if log_file.exists() else ''

    try:
        # The user's situation: 3.0.0 runs from the Desktop (with autostart, settings saved)
        subprocess.Popen([str(legacy)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        wait_for(lambda: (data / 'config.json').exists(), 60, 'old version to start')
        if WINDOWS:
            wait_for(lambda: os.path.normcase(autostart_value()) == os.path.normcase(str(legacy)), 30,
                     'old version to set autostart')
        print('old version running')

        # The only user action: start the downloaded new version
        result = subprocess.run([str(downloaded)], timeout=300)
        if result.returncode != 0:
            print(log_text())
            sys.exit(f'FAIL: new version exited with {result.returncode}')

        wait_for(lambda: 'Started from install folder' in log_text(), 90, 'installed copy to start')
        wait_for(lambda: not running(legacy), 30, 'old version to stop')
        wait_for(lambda: not legacy.exists(), 60, 'old exe to be replaced')
        if WINDOWS:
            wait_for(lambda: (desktop / 'Go-to-Bed.lnk').exists(), 30, 'shortcut in place of the old exe')
            wait_for(lambda: os.path.normcase(autostart_value()) == os.path.normcase(str(installed)), 30,
                     'autostart to point to the installed version')
        if not running(installed):
            sys.exit('FAIL: installed version is not running')
        if not (data / 'config.json').exists():
            sys.exit('FAIL: settings lost')
        print(log_text())
        print('PASS: 3.0.0 stopped and replaced, new version installed and running, settings kept')
    finally:
        if installed.exists():
            subprocess.run([str(installed), '--uninstall', '--quiet'], timeout=120)
        if WINDOWS:
            subprocess.run(['taskkill', '/F', '/IM', 'GotoBed.exe'], capture_output=True)
        else:
            subprocess.run(['pkill', '-f', str(tmp)], capture_output=True)


if __name__ == '__main__':
    main()
