"""End-to-end test of self-install and uninstall with a real build.

Usage: python tools/e2e_install.py EXE

Copies EXE into a fake "Downloads" folder and starts it. Passes when it
installs itself into a temporary install folder (GOTOBED_INSTALL_DIR), the
installed copy starts and registers itself (on Windows: Start menu shortcut,
"Apps & features" entry, autostart), and `--uninstall --quiet` makes the
running app quit and removes all of it again while keeping the data folder.

On Windows this touches the real HKCU registry and Start menu of the current
user - meant for CI runners, not for a PC that has Go-to-Bed installed.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WINDOWS = sys.platform == 'win32'
UNINSTALL_KEY = r'Software\Microsoft\Windows\CurrentVersion\Uninstall\GotoBed'
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'


def wait_for(condition, timeout: float, what: str) -> None:
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            sys.exit(f'FAIL: timed out waiting for {what}')
        time.sleep(1)


def registry_has(key_path: str, value: str = None) -> bool:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            if value:
                winreg.QueryValueEx(key, value)
        return True
    except FileNotFoundError:
        return False


def shortcut() -> Path:
    return Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Go-to-Bed.lnk'


def app_running() -> bool:
    if WINDOWS:
        out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq GotoBed.exe', '/NH'], capture_output=True, text=True)
        return 'GotoBed.exe' in out.stdout
    return subprocess.run(['pgrep', '-f', 'Programs/GotoBed'], capture_output=True).returncode == 0


def stop_app(exe: Path) -> None:
    if WINDOWS:
        subprocess.run(['taskkill', '/F', '/IM', 'GotoBed.exe'], capture_output=True)
    else:
        subprocess.run(['pkill', '-f', str(exe)], capture_output=True)


def main() -> None:
    exe = Path(sys.argv[1]).resolve()
    tmp = Path(tempfile.mkdtemp(prefix='gotobed-e2e-install-'))
    downloads, install_dir, data = tmp / 'Downloads', tmp / 'Programs' / 'GotoBed', tmp / 'data'
    downloads.mkdir()
    downloaded = downloads / exe.name
    shutil.copy2(exe, downloaded)
    installed = install_dir / 'GotoBed.exe'

    os.environ.update({
        'GOTOBED_INSTALL_DIR': str(install_dir),
        'GOTOBED_DATA_DIR': str(data),
        'GOTOBED_ANY_PLATFORM': '1',
        'GOTOBED_UPDATE_URL': 'http://127.0.0.1:1/none',  # never reach GitHub from the test
    })
    log_file = data / 'gotobed.log'

    def log_text() -> str:
        return log_file.read_text(encoding='utf-8', errors='replace') if log_file.exists() else ''

    def fail(message: str) -> None:
        print(log_text())
        if WINDOWS:
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
                    print('Run values:', [winreg.EnumValue(key, i) for i in range(winreg.QueryInfoKey(key)[1])])
            except OSError as e:
                print('Run key:', e)
        sys.exit(f'FAIL: {message}')

    try:
        # 1. Start the downloaded exe: it installs itself and starts the installed copy
        result = subprocess.run([str(downloaded)], timeout=180)
        if result.returncode != 0:
            print(log_text())
            sys.exit(f'FAIL: first start exited with {result.returncode}')
        wait_for(lambda: 'Started from install folder' in log_text(), 90, 'installed copy to start')
        if not installed.exists():
            fail('exe not installed')
        if WINDOWS:
            wait_for(lambda: registry_has(UNINSTALL_KEY) and shortcut().exists(), 60,
                     'shortcut and Apps & features entry')
            if not registry_has(RUN_KEY, 'GotoBed'):
                fail('autostart entry missing')
        print('install OK')

        # 2. Uninstall quietly while the installed copy is running
        result = subprocess.run([str(installed), '--uninstall', '--quiet'], timeout=120)
        if result.returncode != 0:
            print(log_text())
            sys.exit(f'FAIL: uninstall exited with {result.returncode}')
        wait_for(lambda: not install_dir.exists(), 90, 'program folder to be removed')
        if WINDOWS:
            wait_for(lambda: not app_running(), 30, 'running app to quit')
            if registry_has(UNINSTALL_KEY) or registry_has(RUN_KEY, 'GotoBed') or shortcut().exists():
                fail('registry entries or shortcut left behind')
        if not (data / 'config.json').exists():
            fail('--quiet must keep the data folder')
        print(log_text())
        print('PASS: installed, registered, uninstalled; data kept')
    finally:
        stop_app(installed)


if __name__ == '__main__':
    main()
