"""Self-update from GitHub releases.

Flow: fetch_latest() -> is_newer() -> download() (size + SHA-256 check)
-> verify_exe() (runs the new exe with --report-version) -> install()
(rename running exe to *.old.exe, new one into its place) -> relaunch().
The new instance removes the *.old.exe with cleanup_old().
"""
import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence, Tuple

from version import __version__

log = logging.getLogger(__name__)

REPO = 'zGLados/go-to-bed'
ASSET_NAME = 'GotoBed.exe'
RELEASES_PAGE = f'https://github.com/{REPO}/releases/latest'
TIMEOUT = 30  # seconds per network request


class UpdateError(Exception):
    """An update step failed; the message is shown to the user."""


@dataclass
class Release:
    """The parts of a GitHub release the updater needs."""
    version: str
    download_url: str
    size: int
    sha256: Optional[str]


def api_url() -> str:
    """GitHub API endpoint for the latest release (overridable for tests)."""
    return os.getenv('GOTOBED_UPDATE_URL', f'https://api.github.com/repos/{REPO}/releases/latest')


def parse_version(text: str) -> Tuple[int, ...]:
    """'v3.1.0' -> (3, 1, 0). Raises ValueError for anything else."""
    parts = text.strip().lstrip('vV').split('.')
    if len(parts) != 3:
        raise ValueError(f'not a version: {text!r}')
    return tuple(int(p) for p in parts)


def is_newer(release: Release, current: str = __version__) -> bool:
    """Return whether the release is newer than the running version."""
    return parse_version(release.version) > parse_version(current)


def is_supported() -> bool:
    """Only the built exe can replace itself (Windows; other platforms only for local testing)."""
    frozen = bool(getattr(sys, 'frozen', False))
    return frozen and (sys.platform == 'win32' or bool(os.getenv('GOTOBED_UPDATE_ANY_PLATFORM')))


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={
        'User-Agent': f'GotoBed/{__version__}',
        'Accept': 'application/vnd.github+json',
    })


def parse_release(data: dict) -> Optional[Release]:
    """Turn the GitHub API answer into a Release, or None if it has no usable exe."""
    try:
        version = '.'.join(map(str, parse_version(data['tag_name'])))
    except (KeyError, ValueError, TypeError):
        return None
    for asset in data.get('assets', []):
        if asset.get('name') == ASSET_NAME:
            digest = asset.get('digest') or ''
            return Release(
                version=version,
                download_url=asset['browser_download_url'],
                size=int(asset['size']),
                sha256=digest.split(':', 1)[1].lower() if digest.startswith('sha256:') else None
            )
    return None


def fetch_latest() -> Optional[Release]:
    """Ask GitHub for the latest release. Raises UpdateError on network problems."""
    try:
        with urllib.request.urlopen(_request(api_url()), timeout=TIMEOUT) as response:
            data = json.load(response)
    except Exception as e:
        raise UpdateError(f'Could not check for updates: {e}') from e
    return parse_release(data)


def exe_paths(current_exe: Path) -> Tuple[Path, Path]:
    """Paths for the downloaded and the replaced exe, next to the running one."""
    return (current_exe.with_name(current_exe.stem + '.new.exe'),
            current_exe.with_name(current_exe.stem + '.old.exe'))


def download(release: Release, target: Path) -> None:
    """Download the exe to `target`, checking size and SHA-256."""
    partial = target.with_name(target.name + '.part')
    sha = hashlib.sha256()
    size = 0
    try:
        with urllib.request.urlopen(_request(release.download_url), timeout=TIMEOUT) as response, \
                open(partial, 'wb') as f:
            while chunk := response.read(1 << 16):
                f.write(chunk)
                sha.update(chunk)
                size += len(chunk)
    except Exception as e:
        partial.unlink(missing_ok=True)
        raise UpdateError(f'Download failed: {e}') from e

    if size != release.size:
        partial.unlink(missing_ok=True)
        raise UpdateError(f'Download incomplete ({size} of {release.size} bytes)')
    if release.sha256 and sha.hexdigest() != release.sha256:
        partial.unlink(missing_ok=True)
        raise UpdateError('Downloaded file is damaged (checksum mismatch)')
    if os.name != 'nt':
        partial.chmod(0o755)  # Windows needs no execute bit; needed for local tests elsewhere
    os.replace(partial, target)
    log.info("Downloaded v%s to %s", release.version, target)


def child_env(**extra: str) -> dict:
    """Environment for starting another GotoBed.exe from this one.

    PYINSTALLER_RESET_ENVIRONMENT makes the child a fresh, independent
    PyInstaller process instead of reusing this process's unpacked files.
    """
    return {**os.environ, 'PYINSTALLER_RESET_ENVIRONMENT': '1', **extra}


def verify_exe(exe: Path, expected_version: str) -> None:
    """Start the new exe once and check that it runs and reports the expected version."""
    with tempfile.TemporaryDirectory(prefix='gotobed-update-') as tmp:
        report = Path(tmp) / 'version.txt'
        try:
            result = subprocess.run(
                [str(exe), '--report-version', str(report)],
                env=child_env(GOTOBED_DATA_DIR=tmp),
                timeout=120
            )
        except Exception as e:
            raise UpdateError(f'The new version could not be started: {e}') from e
        reported = report.read_text(encoding='utf-8').strip() if report.exists() else ''
        if result.returncode != 0 or reported != expected_version:
            raise UpdateError(
                f'The new version failed its check (exit code {result.returncode}, version {reported or "?"})'
            )
    log.info("Verified %s (v%s)", exe, expected_version)


def install(new_exe: Path, current_exe: Path) -> None:
    """Put `new_exe` in place of the running `current_exe`.

    A running exe cannot be overwritten on Windows, but it can be renamed.
    """
    _, old_exe = exe_paths(current_exe)
    try:
        old_exe.unlink(missing_ok=True)
        os.replace(current_exe, old_exe)
    except OSError as e:
        raise UpdateError(f'Cannot replace {current_exe.name} (no write access to {current_exe.parent}?): {e}') from e
    try:
        os.replace(new_exe, current_exe)
    except OSError as e:
        os.replace(old_exe, current_exe)  # roll back
        raise UpdateError(f'Cannot install the new version: {e}') from e
    log.info("Installed new version at %s", current_exe)


def relaunch(exe: Path, args: Sequence[str] = ()) -> None:
    """Start `exe` as an independent process."""
    flags = 0
    if sys.platform == 'win32':
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([str(exe), *args], env=child_env(), creationflags=flags, close_fds=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def cleanup_old(current_exe: Path, attempts: int = 10, delay: float = 3.0) -> None:
    """Delete leftovers of an update. The old exe may still be exiting, so retry."""
    new_exe, old_exe = exe_paths(current_exe)
    for path in (new_exe, new_exe.with_name(new_exe.name + '.part'), old_exe):
        for attempt in range(attempts):
            try:
                path.unlink(missing_ok=True)
                break
            except OSError:
                if attempt == attempts - 1:
                    log.warning("Could not delete %s", path)
                else:
                    time.sleep(delay)


def update_to(release: Release, current_exe: Path) -> None:
    """Download, verify and install `release`. Does not restart."""
    new_exe, _ = exe_paths(current_exe)
    download(release, new_exe)
    try:
        verify_exe(new_exe, release.version)
    except UpdateError:
        new_exe.unlink(missing_ok=True)
        raise
    install(new_exe, current_exe)
