"""End-to-end test of the self-updater with two real builds.

Usage: python tools/e2e_update.py OLD_EXE NEW_EXE

"Installs" OLD_EXE into a temp folder, serves NEW_EXE as a fake GitHub
release on localhost and runs `OLD_EXE --update-now`. Passes when the
installed file has been replaced by NEW_EXE, the new version has started
("Started after update" in its log) and the old exe has been cleaned up.
"""
import functools
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report_version(exe: Path, tmp: Path) -> str:
    out = tmp / 'version.txt'
    env = {**os.environ, 'GOTOBED_DATA_DIR': str(tmp / 'version-data')}
    subprocess.run([str(exe), '--report-version', str(out)], env=env, check=True, timeout=120)
    return out.read_text(encoding='utf-8').strip()


def wait_for(condition, timeout: float, what: str) -> None:
    deadline = time.monotonic() + timeout
    while not condition():
        if time.monotonic() > deadline:
            sys.exit(f'FAIL: timed out waiting for {what}')
        time.sleep(1)


def stop_app(exe: Path) -> None:
    if sys.platform == 'win32':
        subprocess.run(['taskkill', '/F', '/IM', exe.name], capture_output=True)
    else:
        subprocess.run(['pkill', '-f', str(exe)], capture_output=True)


def main() -> None:
    old_exe, new_exe = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    tmp = Path(tempfile.mkdtemp(prefix='gotobed-e2e-'))
    install_dir, www, data = tmp / 'install', tmp / 'www', tmp / 'data'
    for d in (install_dir, www, data):
        d.mkdir()

    old_version, new_version = report_version(old_exe, tmp), report_version(new_exe, tmp)
    print(f'old: {old_version}  new: {new_version}')

    installed = install_dir / old_exe.name
    shutil.copy2(old_exe, installed)
    asset_name = 'GotoBed.exe'
    shutil.copy2(new_exe, www / asset_name)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(www))
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{httpd.server_address[1]}'
    (www / 'latest.json').write_text(json.dumps({
        'tag_name': f'v{new_version}',
        'assets': [{
            'name': asset_name,
            'browser_download_url': f'{base}/{asset_name}',
            'size': new_exe.stat().st_size,
            'digest': f'sha256:{sha256(new_exe)}',
        }],
    }))

    os.environ.update({
        'GOTOBED_UPDATE_URL': f'{base}/latest.json',
        'GOTOBED_DATA_DIR': str(data),
        'GOTOBED_UPDATE_ANY_PLATFORM': '1',
    })
    log_file = data / 'gotobed.log'
    old_leftover = installed.with_name(installed.stem + '.old.exe')
    try:
        result = subprocess.run([str(installed), '--update-now'], timeout=300)
        print(log_file.read_text(encoding='utf-8', errors='replace') if log_file.exists() else '(no log)')
        if result.returncode != 0:
            sys.exit(f'FAIL: --update-now exited with {result.returncode}')
        if sha256(installed) != sha256(new_exe):
            sys.exit('FAIL: installed exe was not replaced')

        marker = f'Started after update from v{old_version}'
        wait_for(lambda: marker in log_file.read_text(encoding='utf-8', errors='replace'), 90, 'new instance to start')
        wait_for(lambda: not old_leftover.exists(), 90, 'old exe to be deleted')
        print(f'PASS: updated {old_version} -> {new_version}, new instance running, old exe removed')
    finally:
        stop_app(installed)
        httpd.shutdown()


if __name__ == '__main__':
    main()
