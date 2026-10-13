"""Tests for the self-updater (no network, no GUI)."""
import functools
import hashlib
import http.server
import sys
import threading

import pytest

import updater


@pytest.fixture
def server(tmp_path):
    """Serve tmp_path/www over HTTP; yields the base URL."""
    www = tmp_path / 'www'
    www.mkdir()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(www))
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield www, f'http://127.0.0.1:{httpd.server_address[1]}'
    httpd.shutdown()


def api_answer(tag, url, size, digest=None, name='GotoBed.exe'):
    asset = {'name': name, 'browser_download_url': url, 'size': size}
    if digest:
        asset['digest'] = digest
    return {'tag_name': tag, 'assets': [asset]}


def test_parse_version():
    assert updater.parse_version('v3.1.0') == (3, 1, 0)
    assert updater.parse_version('10.0.2') == (10, 0, 2)
    for bad in ('3.1', 'v3.1.0-beta', 'latest'):
        with pytest.raises(ValueError):
            updater.parse_version(bad)


def test_is_newer():
    release = updater.Release('3.0.10', 'u', 1, None)
    assert updater.is_newer(release, '3.0.9')
    assert not updater.is_newer(release, '3.0.10')
    assert not updater.is_newer(release, '3.1.0')


def test_parse_release():
    release = updater.parse_release(api_answer('v3.1.0', 'http://x/GotoBed.exe', 42, 'sha256:ABC'))
    assert release == updater.Release('3.1.0', 'http://x/GotoBed.exe', 42, 'abc')
    assert updater.parse_release(api_answer('v3.1.0', 'u', 1, name='other.zip')) is None
    assert updater.parse_release(api_answer('nightly', 'u', 1)) is None
    assert updater.parse_release({}) is None


def test_fetch_latest(server, monkeypatch):
    www, base = server
    (www / 'latest.json').write_text(
        '{"tag_name": "v9.9.9", "assets": [{"name": "GotoBed.exe", "browser_download_url": "u", "size": 1}]}')
    monkeypatch.setenv('GOTOBED_UPDATE_URL', f'{base}/latest.json')
    assert updater.fetch_latest().version == '9.9.9'


def test_fetch_latest_network_error(monkeypatch):
    monkeypatch.setenv('GOTOBED_UPDATE_URL', 'http://127.0.0.1:1/latest.json')
    with pytest.raises(updater.UpdateError):
        updater.fetch_latest()


def test_download_checks_size_and_hash(server, tmp_path):
    www, base = server
    data = b'new exe' * 1000
    (www / 'GotoBed.exe').write_bytes(data)
    good = updater.Release('9.9.9', f'{base}/GotoBed.exe', len(data), hashlib.sha256(data).hexdigest())

    target = tmp_path / 'GotoBed.new.exe'
    updater.download(good, target)
    assert target.read_bytes() == data

    for bad in (updater.Release('9.9.9', good.download_url, len(data) + 1, None),
                updater.Release('9.9.9', good.download_url, len(data), '0' * 64)):
        target.unlink(missing_ok=True)
        with pytest.raises(updater.UpdateError):
            updater.download(bad, target)
        assert not target.exists()
        assert not list(tmp_path.glob('*.part'))


def test_install_swaps_files(tmp_path):
    current = tmp_path / 'GotoBed.exe'
    new, old = updater.exe_paths(current)
    current.write_text('old')
    new.write_text('new')
    updater.install(new, current)
    assert current.read_text() == 'new'
    assert old.read_text() == 'old'
    assert not new.exists()


def test_install_rolls_back_when_new_exe_missing(tmp_path):
    current = tmp_path / 'GotoBed.exe'
    new, old = updater.exe_paths(current)
    current.write_text('old')
    with pytest.raises(updater.UpdateError):
        updater.install(new, current)
    assert current.read_text() == 'old'
    assert not old.exists()


def test_cleanup_old(tmp_path):
    current = tmp_path / 'GotoBed.exe'
    new, old = updater.exe_paths(current)
    for path in (current, new, old):
        path.write_text('x')
    updater.cleanup_old(current, attempts=1)
    assert current.exists() and not new.exists() and not old.exists()


@pytest.mark.skipif(sys.platform == 'win32', reason='uses a shell script as fake exe')
@pytest.mark.parametrize('reported, ok', [('9.9.9', True), ('1.0.0', False)])
def test_verify_exe(tmp_path, reported, ok):
    fake = tmp_path / 'GotoBed.new.exe'
    fake.write_text(f'#!/bin/sh\n[ "$1" = "--report-version" ] && printf {reported} > "$2"\n')
    fake.chmod(0o755)
    if ok:
        updater.verify_exe(fake, '9.9.9')
    else:
        with pytest.raises(updater.UpdateError):
            updater.verify_exe(fake, '9.9.9')
