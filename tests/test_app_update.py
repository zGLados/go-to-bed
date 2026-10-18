"""Tests for the update flow inside the running app (needs a display for Tk)."""
import gc
import sys
import threading
import time

import pytest

tk = pytest.importorskip('tkinter')

import main
import updater
from config import Config


@pytest.fixture(scope='module')
def shared_app(tmp_path_factory):
    """One app (= one Tk interpreter) for all tests: creating several Tk
    instances in one process fails sporadically on Windows."""
    try:
        application = main.GotoBedApp(Config(tmp_path_factory.mktemp('data')))
    except tk.TclError as e:
        pytest.skip(f'Tk not available: {e}')
    application.root.after(100, application._process_ui_queue)
    yield application
    application.root.destroy()
    del application
    gc.collect()  # free Tk objects here on the main thread


@pytest.fixture
def app(shared_app, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(sys, 'executable', str(tmp_path / 'GotoBed.exe'))
    monkeypatch.setattr(updater, 'is_supported', lambda: True)
    monkeypatch.setattr(updater, 'download', lambda release, target: calls.append('download'))
    monkeypatch.setattr(updater, 'verify_exe', lambda path, version: calls.append('verify'))
    monkeypatch.setattr(updater, 'install', lambda new, current: calls.append('install'))
    monkeypatch.setattr(updater, 'relaunch', lambda exe, args: calls.append(('relaunch', tuple(args))))
    monkeypatch.setattr(shared_app, '_quit_app', lambda: calls.append('quit'))
    shared_app.calls = calls
    shared_app.config.config['auto_update'] = True
    yield shared_app
    # Let worker threads finish, then reset the state for the next test
    for thread in threading.enumerate():
        if thread.name.startswith('update'):
            thread.join(timeout=10)
    shared_app.root.update()
    shared_app._cancel_snooze()
    shared_app._pending_update = None
    shared_app._update_running = False
    shared_app.__dict__.pop('UPDATE_RETRY_MS', None)


def pump(app, until, timeout=15.0):
    deadline = time.monotonic() + timeout
    while not until() and time.monotonic() < deadline:
        app.root.update()
        time.sleep(0.01)


RELEASE = updater.Release('99.0.0', 'http://example/GotoBed.exe', 1, None)


def test_auto_update_installs_and_restarts(app):
    app._on_update_checked(RELEASE, None, manual=False)
    pump(app, lambda: 'quit' in app.calls)
    assert app.calls == ['download', 'verify', 'install', ('relaunch', ('--updated-from', main.__version__)), 'quit']


def test_update_waits_while_snoozed(app):
    app.UPDATE_RETRY_MS = 50
    app._snooze_job = app.root.after(60_000, lambda: None)
    app._on_update_checked(RELEASE, None, manual=False)
    pump(app, lambda: 'verify' in app.calls)
    pump(app, lambda: False, timeout=0.3)
    assert 'install' not in app.calls
    app._cancel_snooze()
    pump(app, lambda: 'quit' in app.calls)
    assert app.calls[-1] == 'quit'


def test_auto_update_off_asks_and_later_keeps_tray_entry(app, monkeypatch):
    questions = []
    monkeypatch.setattr(main.messagebox, 'askyesno', lambda *a, **k: questions.append(a) or False)
    app.config.config['auto_update'] = False
    app._on_update_checked(RELEASE, None, manual=False)
    assert len(questions) == 1
    assert app._pending_update == RELEASE
    assert app.calls == []


def test_auto_update_off_asks_and_yes_installs(app, monkeypatch):
    monkeypatch.setattr(main.messagebox, 'askyesno', lambda *a, **k: True)
    app.config.config['auto_update'] = False
    app._on_update_checked(RELEASE, None, manual=False)
    pump(app, lambda: 'quit' in app.calls)
    assert app.calls[-1] == 'quit'


def test_first_check_happens_at_start():
    assert main.GotoBedApp.UPDATE_FIRST_CHECK_MS <= 5000


def test_older_release_is_ignored(app):
    app._on_update_checked(updater.Release('0.0.1', 'u', 1, None), None, manual=False)
    pump(app, lambda: False, timeout=0.2)
    assert app.calls == [] and app._pending_update is None


def test_going_to_bed_says_good_night_then_closes(app, monkeypatch):
    import reminder
    monkeypatch.setattr(reminder.ReminderWindow, 'GOOD_NIGHT_MS', 200)
    monkeypatch.setattr(app, '_notify', lambda title, message: None)
    app.config.config['sound_enabled'] = False
    dismissed = app.config.get_stats()['dismissed']
    app._show_bedtime_reminder()
    window = app._reminder_window
    window._handle_going()
    assert app.config.get_stats()['dismissed'] == dismissed + 1
    assert window.exists()
    assert window._text_widgets[0].cget('text').startswith('Good night!')
    pump(app, lambda: not window.exists(), timeout=5)
    assert not window.exists()
