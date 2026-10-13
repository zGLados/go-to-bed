"""Tests for the per-user installation (file logic only; registry/shortcut need Windows)."""
import sys

import pytest

import installer
import updater
from version import __version__

pytestmark = pytest.mark.skipif(sys.platform == 'win32', reason='uses shell scripts as fake exes')


@pytest.fixture
def install_dir(tmp_path, monkeypatch):
    target = tmp_path / 'Programs' / 'GotoBed'
    monkeypatch.setenv('GOTOBED_INSTALL_DIR', str(target))
    return target


def fake_exe(path, version):
    """A script that behaves like `GotoBed.exe --report-version FILE`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/bin/sh\n[ "$1" = "--report-version" ] && printf {version} > "$2"\n')
    path.chmod(0o755)
    return path


def test_fresh_install(tmp_path, install_dir):
    downloaded = fake_exe(tmp_path / 'Downloads' / 'GotoBed.exe', __version__)
    target = installer.install_self(downloaded)
    assert target == install_dir / 'GotoBed.exe'
    assert target.read_text() == downloaded.read_text()
    assert downloaded.exists()  # the downloaded file is left alone


@pytest.mark.parametrize('existing, replaced', [('0.0.1', True), (__version__, False), ('999.0.0', False)])
def test_existing_install(tmp_path, install_dir, existing, replaced):
    fake_exe(install_dir / 'GotoBed.exe', existing)
    downloaded = fake_exe(tmp_path / 'GotoBed.exe', __version__)
    target = installer.install_self(downloaded)
    assert updater.version_of(target) == (__version__ if replaced else existing)


def test_broken_install_is_replaced(tmp_path, install_dir):
    (install_dir).mkdir(parents=True)
    (install_dir / 'GotoBed.exe').write_text('broken')
    downloaded = fake_exe(tmp_path / 'GotoBed.exe', __version__)
    assert updater.version_of(installer.install_self(downloaded)) == __version__


def test_needs_install(tmp_path, install_dir, monkeypatch):
    monkeypatch.setattr(updater, 'is_supported', lambda: True)
    assert installer.needs_install(tmp_path / 'Downloads' / 'GotoBed.exe')
    assert not installer.needs_install(install_dir / 'GotoBed.exe')
    monkeypatch.setattr(updater, 'is_supported', lambda: False)
    assert not installer.needs_install(tmp_path / 'Downloads' / 'GotoBed.exe')


@pytest.mark.parametrize('delete_data', [True, False])
def test_uninstall_removes_program_and_optionally_data(tmp_path, install_dir, delete_data):
    exe = fake_exe(install_dir / 'GotoBed.exe', __version__)
    data = tmp_path / 'data'
    data.mkdir()
    (data / 'config.json').write_text('{}')
    installer.uninstall(exe, data if delete_data else None)
    assert not install_dir.exists()
    assert data.exists() != delete_data
