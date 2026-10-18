"""Main entry point for Go-to-Bed app.

Threading model: Tk runs on the main thread with a hidden root window and all
windows are Toplevels of it. The tray icon and the scheduler run on their own
threads and hand work to the Tk thread via `call_ui`, because Tk is not
thread-safe.
"""
import argparse
import logging
import logging.handlers
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from config import Config, resource_path, APP_NAME
import installer
import instance
from reminder import ReminderWindow
from scheduler import BedtimeScheduler
from settings import SettingsWindow
from stats import StatsWindow
import updater
from version import __version__

log = logging.getLogger('gotobed')


def setup_logging(log_file) -> None:
    """Log to a file in the data folder (and to the console when there is one)."""
    handlers = [logging.handlers.RotatingFileHandler(log_file, maxBytes=200_000, backupCount=1, encoding='utf-8')]
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=handlers
    )


def enable_dpi_awareness() -> None:
    """Prevent blurry windows on high-DPI Windows displays."""
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


class GotoBedApp:
    """Main application class."""

    UPDATE_FIRST_CHECK_MS = 3 * 1000  # check right after start
    UPDATE_INTERVAL_MS = 24 * 60 * 60 * 1000
    UPDATE_RETRY_MS = 60 * 1000

    def __init__(self, config: Config = None, updated_from: str = None, installed_from: str = None,
                 replaced: list = None):
        """Initialize the application."""
        self.config = config or Config()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title('Go-to-Bed')

        self.tray_icon = None
        self.scheduler = BedtimeScheduler(
            self.config,
            on_bedtime=lambda: self.call_ui(self._show_bedtime_reminder),
            on_prewarning=lambda: self.call_ui(self._show_prewarning_reminder)
        )
        self._ui_queue = queue.Queue()
        self._snooze_job = None
        self._settings_window = None
        self._stats_window = None
        self._reminder_window = None
        self._updated_from = updated_from
        self._installed_from = installed_from
        self._replaced = [Path(p) for p in replaced or []]
        self._pending_update = None   # Release waiting for "Install Update" (auto update off)
        self._update_running = False
        self._update_version = None   # version being downloaded and installed

    # ------------------------------------------------------------------ threading

    def call_ui(self, func, *args) -> None:
        """Run `func(*args)` on the Tk thread. Safe to call from any thread."""
        self._ui_queue.put((func, args))

    def _process_ui_queue(self) -> None:
        """Execute pending UI calls; reschedules itself."""
        while True:
            try:
                func, args = self._ui_queue.get_nowait()
            except queue.Empty:
                break
            try:
                func(*args)
            except Exception:
                log.exception("Error in UI call %s", getattr(func, '__name__', func))
        self.root.after(100, self._process_ui_queue)

    # ------------------------------------------------------------------ autostart

    def _setup_autostart(self) -> None:
        """Add or remove the Windows autostart entry according to the config."""
        if sys.platform != 'win32':
            return
        if not getattr(sys, 'frozen', False):
            log.info("Running from source - autostart is only managed for the .exe")
            return
        try:
            installer.set_autostart(self.config.get('autostart'), Path(sys.executable))
            log.info("Autostart %s", 'enabled: ' + sys.executable if self.config.get('autostart') else 'disabled')
        except Exception:
            log.exception("Error setting up autostart")

    # ------------------------------------------------------------------ tray

    @staticmethod
    def _create_icon_image() -> Image.Image:
        """Load the tray icon, falling back to a generated moon."""
        icon_path = resource_path('assets', 'icon.ico')
        try:
            image = Image.open(icon_path)
            image.size = max(image.info.get('sizes', [image.size]))
            return image.convert('RGBA')
        except Exception as e:
            log.warning("Could not load icon from %s: %s", icon_path, e)

        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, 56, 56], fill='gold')
        draw.ellipse([20, 4, 64, 52], fill=(0, 0, 0, 0))
        return image

    def _create_menu(self) -> pystray.Menu:
        """Create the system tray menu. Texts are evaluated whenever it opens."""
        return pystray.Menu(
            item(lambda _: f"Bedtime: {self.config.get('bedtime')}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Reminders enabled', self._on_tray(self._toggle_enabled),
                 checked=lambda _: self.config.get('enabled')),
            pystray.Menu.SEPARATOR,
            item('Settings', self._on_tray(self._open_settings), default=True),
            item('Statistics', self._on_tray(self._open_stats)),
            pystray.Menu.SEPARATOR,
            item('Test Reminder', self._on_tray(self._show_bedtime_reminder)),
            item('Show Data Folder', self._on_tray(self._open_data_folder)),
            pystray.Menu.SEPARATOR,
            item(lambda _: f'Install Update v{self._pending_update.version}' if self._pending_update else '',
                 self._on_tray(self._install_pending_update),
                 visible=lambda _: self._pending_update is not None),
            item('Check for Updates', self._on_tray(lambda: self._check_for_updates(manual=True))),
            pystray.Menu.SEPARATOR,
            item(f'Quit (v{__version__})', self._on_tray(self._quit_app))
        )

    def _on_tray(self, func):
        """Wrap a UI method so it can be used as a pystray callback."""
        return lambda icon, menu_item: self.call_ui(func)

    def _notify(self, title: str, message: str) -> None:
        """Show a Windows toast notification via the tray icon."""
        if self.tray_icon is None:
            return
        try:
            self.tray_icon.notify(message, title)
        except Exception as e:
            log.info("Notification not available: %s", e)

    def _play_sound(self) -> None:
        """Play a short notification sound if enabled."""
        if not self.config.get('sound_enabled'):
            return
        try:
            if sys.platform == 'win32':
                import winsound
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            else:
                self.root.bell()
        except Exception:
            pass

    # ------------------------------------------------------------------ actions (Tk thread)

    def _toggle_enabled(self) -> None:
        """Toggle reminders on/off."""
        new_state = not self.config.get('enabled')
        self.config.save({'enabled': new_state})
        if not new_state:
            self._cancel_snooze()
        self._refresh_tray()
        log.info("Reminders %s", 'enabled' if new_state else 'disabled')

    def _refresh_tray(self) -> None:
        """Make the tray menu pick up config changes."""
        if self.tray_icon is not None:
            self.tray_icon.update_menu()

    def _save_settings(self, new_config) -> bool:
        """Save settings from the settings window."""
        if not self.config.save(new_config):
            return False
        self._setup_autostart()
        if not self.config.get('enabled'):
            self._cancel_snooze()
        self._refresh_tray()
        return True

    def _open_settings(self) -> None:
        """Open settings window (or focus the open one)."""
        if self._settings_window and self._settings_window.exists():
            self._settings_window.focus()
            return
        self._settings_window = SettingsWindow(self.root, self.config.get_all(), self._save_settings,
                                               on_check_updates=lambda: self._check_for_updates(manual=True))

    def _open_stats(self) -> None:
        """Open statistics window, replacing an open one so the numbers are current."""
        if self._stats_window and self._stats_window.exists():
            self._stats_window.window.destroy()
        self._stats_window = StatsWindow(self.root, self.config.get_stats())

    def _open_data_folder(self) -> None:
        """Open the data folder in the file manager."""
        path = str(self.config.data_dir)
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def _show_reminder(self, **kwargs) -> None:
        """Replace any open reminder window with a new one."""
        if self._reminder_window:
            self._reminder_window.close()
        self._reminder_window = ReminderWindow(self.root, **kwargs)
        self._play_sound()

    def _show_prewarning_reminder(self) -> None:
        """Show pre-warning reminder."""
        minutes = self.config.get('pre_warning_minutes', 15)
        self._notify('Bedtime Soon', f'Your bedtime is in {minutes} minutes. Time to wind down!')
        self._show_reminder(
            snooze_minutes=self.config.get('snooze_minutes', 10),
            on_snooze=lambda: None,
            on_dismiss=lambda: None,
            is_prewarning=True,
            minutes_left=minutes
        )

    def _show_bedtime_reminder(self) -> None:
        """Show bedtime reminder."""
        self._cancel_snooze()
        self._notify('Time to Go to Bed!', 'Sweet dreams! 😴')
        self.config.add_stat_entry('showed')
        self._show_reminder(
            snooze_minutes=self.config.get('snooze_minutes', 10),
            on_snooze=self._handle_snooze,
            on_dismiss=self._handle_dismiss
        )

    def _handle_snooze(self) -> None:
        """Handle snooze action."""
        minutes = self.config.get('snooze_minutes', 10)
        log.info("Snoozed for %s minutes", minutes)
        self.config.add_stat_entry('snoozed')
        self._cancel_snooze()
        self._snooze_job = self.root.after(minutes * 60 * 1000, self._snooze_expired)

    def _snooze_expired(self) -> None:
        """Show the reminder again after snoozing."""
        self._snooze_job = None
        if self.config.get('enabled'):
            self._show_bedtime_reminder()

    def _cancel_snooze(self) -> None:
        """Cancel a pending snooze."""
        if self._snooze_job is not None:
            self.root.after_cancel(self._snooze_job)
            self._snooze_job = None

    def _handle_dismiss(self) -> None:
        """Handle dismiss action."""
        log.info("User went to bed")
        self.config.add_stat_entry('dismissed')

    # ------------------------------------------------------------------ updates

    def _schedule_update_check(self, delay_ms: int) -> None:
        """Check for updates after `delay_ms`, then once a day."""
        def check():
            self._check_for_updates(manual=False)
            self._schedule_update_check(self.UPDATE_INTERVAL_MS)
        self.root.after(delay_ms, check)

    def _check_for_updates(self, manual: bool) -> None:
        """Ask GitHub for a newer release in the background."""
        if self._update_running:
            if manual:
                messagebox.showinfo('Go-to-Bed', f'Version {self._update_version} is being downloaded and installed.\n\n'
                                    'Go-to-Bed restarts by itself when it is done '
                                    '(not while a reminder or the settings are open).')
            return

        def worker():
            try:
                release = updater.fetch_latest()
                error = None
            except updater.UpdateError as e:
                release, error = None, str(e)
            self.call_ui(self._on_update_checked, release, error, manual)

        threading.Thread(target=worker, name='update-check', daemon=True).start()

    def _on_update_checked(self, release, error, manual: bool) -> None:
        """Handle the result of an update check (Tk thread)."""
        if error:
            log.warning(error)
            if manual:
                messagebox.showerror('Go-to-Bed', error)
            return
        if release is None or not updater.is_newer(release):
            log.info("No update available (running v%s)", __version__)
            if manual:
                messagebox.showinfo('Go-to-Bed', f'You are using the latest version (v{__version__}).')
            return

        log.info("Update available: v%s", release.version)
        if not updater.is_supported():
            if manual and messagebox.askyesno(
                    'Go-to-Bed', f'Version {release.version} is available.\n\n'
                    'Automatic updates only work in GotoBed.exe. Open the download page?'):
                webbrowser.open(updater.RELEASES_PAGE)
            return

        if manual:
            if messagebox.askyesno('Go-to-Bed', f'Version {release.version} is available (you have {__version__}).\n\n'
                                   'Install it now? Go-to-Bed restarts afterwards.'):
                self._start_update(release, manual=True)
        elif self.config.get('auto_update'):
            self._start_update(release, manual=False)
        else:
            self._pending_update = release
            self._refresh_tray()
            if messagebox.askyesno('Go-to-Bed', f'Version {release.version} is available (you have {__version__}).\n\n'
                                   'Install it now? Go-to-Bed restarts afterwards.\n\n'
                                   '(Later: tray icon → Install Update)'):
                self._start_update(release, manual=True)

    def _install_pending_update(self) -> None:
        """Tray entry 'Install Update vX.Y.Z'."""
        if self._pending_update:
            self._start_update(self._pending_update, manual=True)

    def _start_update(self, release, manual: bool) -> None:
        """Download and install `release` in the background, then restart."""
        if self._update_running:
            return
        self._update_running = True
        self._update_version = release.version
        self._pending_update = None
        self._refresh_tray()
        current_exe = Path(sys.executable)
        log.info("Downloading v%s", release.version)
        self._notify('Updating Go-to-Bed', f'Downloading version {release.version}. '
                     'Go-to-Bed restarts by itself when it is done.')

        def worker():
            try:
                new_exe, _ = updater.exe_paths(current_exe)
                updater.download(release, new_exe)
                updater.verify_exe(new_exe, release.version)
            except updater.UpdateError as e:
                updater.cleanup_old(current_exe, attempts=1)
                self.call_ui(self._on_update_failed, str(e), manual)
                return
            self.call_ui(self._finish_update_when_idle, release, new_exe, manual)

        threading.Thread(target=worker, name='update', daemon=True).start()

    def _is_busy(self) -> bool:
        """True while a reminder or the settings are open or a snooze is pending - don't restart then."""
        reminder_open = self._reminder_window is not None and self._reminder_window.exists()
        settings_open = self._settings_window is not None and self._settings_window.exists()
        return reminder_open or settings_open or self._snooze_job is not None

    def _finish_update_when_idle(self, release, new_exe: Path, manual: bool) -> None:
        """Swap the exe and restart, but not in the middle of a reminder."""
        if self._is_busy():
            log.info("Update ready, waiting until no reminder or settings window is open")
            self.root.after(self.UPDATE_RETRY_MS, lambda: self._finish_update_when_idle(release, new_exe, manual))
            return
        current_exe = Path(sys.executable)
        try:
            updater.install(new_exe, current_exe)
            updater.relaunch(current_exe, ['--updated-from', __version__])
        except Exception as e:
            self._on_update_failed(str(e), manual)
            return
        log.info("Restarting into v%s", release.version)
        self._exit_for_restart()

    def _on_update_failed(self, error: str, manual: bool) -> None:
        """Report a failed update; the running version stays untouched."""
        log.error("Update failed: %s", error)
        self._update_running = False
        if manual:
            if messagebox.askyesno('Go-to-Bed', f'The update failed:\n{error}\n\nOpen the download page instead?'):
                webbrowser.open(updater.RELEASES_PAGE)
        else:
            self._notify('Update failed', 'Go-to-Bed could not update itself. See the log for details.')

    def _finish_install(self) -> None:
        """Replace old copies of Go-to-Bed with shortcuts and tell the user (background thread)."""
        replaced = installer.replace_legacy(self._replaced, Path(sys.executable)) if self._replaced else []
        if replaced:
            message = 'The old version was replaced. Find Go-to-Bed in the Start menu.'
        else:
            message = 'Find it in the Start menu. You can delete the downloaded file.'
        self.call_ui(lambda: self.root.after(2000, lambda: self._notify('Go-to-Bed installed', message)))

    @staticmethod
    def _register_install(exe: Path) -> None:
        """Refresh Start menu shortcut and "Apps & features" entry (background thread)."""
        try:
            installer.register(exe)
        except Exception:
            log.exception("Could not register the installation")

    def _exit_for_restart(self) -> None:
        """Exit at once so the new version can start.

        root.quit() only ends the main loop after an open message box is closed
        (e.g. "Check for Updates" during the download) - the new instance would
        give up waiting for the single-instance lock in the meantime.
        """
        log.info("Quitting Go-to-Bed for the restart...")
        self.scheduler.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        logging.shutdown()
        os._exit(0)

    def _quit_app(self) -> None:
        """Quit the application."""
        log.info("Quitting Go-to-Bed...")
        self.scheduler.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()

    # ------------------------------------------------------------------ run

    def run(self) -> None:
        """Run the application (blocks until quit)."""
        log.info("Go-to-Bed v%s starting, data folder: %s", __version__, self.config.data_dir)

        self._setup_autostart()
        self.scheduler.start()

        self.tray_icon = pystray.Icon(APP_NAME, self._create_icon_image(), 'Go-to-Bed', menu=self._create_menu())
        threading.Thread(target=self.tray_icon.run, name='tray', daemon=True).start()

        if self.config.is_first_run:
            log.info("First run detected - opening settings")
            self.config.save()
            self.root.after(500, self._open_settings)

        instance.watch_quit_signal(lambda: self.call_ui(self._quit_app))
        if updater.is_supported():
            exe = Path(sys.executable)
            threading.Thread(target=updater.cleanup_old, args=(exe,), name='update-cleanup', daemon=True).start()
            if installer.is_installed(exe):
                threading.Thread(target=self._register_install, args=(exe,), name='register', daemon=True).start()
        if self._installed_from:
            log.info("Started from install folder (installed from %s)", self._installed_from)
            threading.Thread(target=self._finish_install, name='replace-legacy', daemon=True).start()
        self._schedule_update_check(self.UPDATE_FIRST_CHECK_MS)
        if self._updated_from:
            log.info("Started after update from v%s", self._updated_from)
            self.root.after(3000, lambda: self._notify(
                'Go-to-Bed updated', f'Updated from {self._updated_from} to {__version__}.'))

        self.root.after(100, self._process_ui_queue)
        self.root.mainloop()

    def self_test(self) -> None:
        """Open every window once and close it again. Raises on failure."""
        self._create_icon_image()
        pystray.Icon(APP_NAME, self._create_icon_image(), 'Go-to-Bed', menu=self._create_menu())
        self.scheduler.check()

        self._open_settings()
        self._open_stats()
        self._show_prewarning_reminder()
        self._show_bedtime_reminder()
        self.root.update()
        assert self._reminder_window._photo is not None, 'reminder image missing'

        self._reminder_window.close()
        self._settings_window.window.destroy()
        self._stats_window.window.destroy()
        self.root.destroy()


def report_version(path: Path) -> int:
    """Check that the bundled files are usable and write the version to `path`."""
    try:
        with Image.open(resource_path('assets', 'icon.ico')) as icon:
            icon.load()
        with Image.open(resource_path('assets', 'horse-sleeping-on-grass.png')) as image:
            image.load()
        path.write_text(__version__, encoding='utf-8')
    except Exception:
        return 1
    return 0


def update_now() -> int:
    """Command line update: install a newer release and start it (no windows)."""
    if not updater.is_supported():
        log.error("Updating only works in GotoBed.exe")
        return 1
    try:
        release = updater.fetch_latest()
        if release is None or not updater.is_newer(release):
            log.info("No update available (running v%s)", __version__)
            return 0
        current_exe = Path(sys.executable)
        updater.update_to(release, current_exe)
        updater.relaunch(current_exe, ['--updated-from', __version__])
    except updater.UpdateError as e:
        log.error("Update failed: %s", e)
        return 1
    log.info("Updated to v%s, new instance started", release.version)
    return 0


def show_message(text: str, kind: str = 'info'):
    """Show a message box without the app running. Returns the answer for 'yesno'."""
    root = tk.Tk()
    root.withdraw()
    try:
        if kind == 'yesno':
            return messagebox.askyesno('Go-to-Bed', text)
        getattr(messagebox, 'showerror' if kind == 'error' else 'showinfo')('Go-to-Bed', text)
    finally:
        root.destroy()


def uninstall(config: Config, quiet: bool) -> int:
    """Remove Go-to-Bed (called from "Apps & features" or with --uninstall)."""
    if not quiet and not show_message('Remove Go-to-Bed from this computer?', 'yesno'):
        return 0
    delete_data = not quiet and show_message(
        'Also delete your settings and statistics?\n\n'
        f'({config.data_dir})', 'yesno')

    instance.request_quit()
    lock = instance.acquire_lock(wait_seconds=20)
    if lock is None:
        log.error("Uninstall: the running Go-to-Bed did not quit")
        if not quiet:
            show_message('Go-to-Bed is still running. Quit it from the tray icon and try again.', 'error')
        return 1

    try:
        installer.uninstall(Path(sys.executable), config.data_dir if delete_data else None)
    except Exception as e:
        if not quiet:
            show_message(f'Uninstall failed: {e}', 'error')
        return 1
    if not quiet:
        show_message('Go-to-Bed has been removed.')
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Go-to-Bed bedtime reminder')
    parser.add_argument('--self-test', action='store_true',
                        help='open all windows once and exit (exit code 0 = OK)')
    parser.add_argument('--report-version', metavar='FILE',
                        help='write the version to FILE and exit (used to verify a downloaded update)')
    parser.add_argument('--update-now', action='store_true',
                        help='install a newer release if there is one, restart and exit')
    parser.add_argument('--uninstall', action='store_true',
                        help='remove Go-to-Bed (shortcut, autostart, Apps & features entry, program files)')
    parser.add_argument('--quiet', action='store_true',
                        help='with --uninstall: no questions, keep settings and statistics')
    parser.add_argument('--updated-from', metavar='VERSION', help=argparse.SUPPRESS)
    parser.add_argument('--installed-from', metavar='PATH', help=argparse.SUPPRESS)
    parser.add_argument('--replaced', metavar='PATH', action='append', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.report_version:
        return report_version(Path(args.report_version))

    config = Config()
    setup_logging(config.log_file)
    enable_dpi_awareness()

    if args.self_test:
        try:
            GotoBedApp(config).self_test()
        except Exception:
            log.exception("Self-test failed")
            return 1
        log.info("Self-test passed")
        return 0

    if args.uninstall:
        return uninstall(config, quiet=args.quiet)

    restarted = bool(args.updated_from or args.installed_from)
    # After an update the old instance may still be closing: 3.1.0 only quits once
    # an open message box is closed, so wait generously for it.
    lock = instance.acquire_lock(wait_seconds=600 if restarted else 0)
    if args.update_now:
        if lock is None:
            log.error("Go-to-Bed is running - quit it before using --update-now")
            return 1
        return update_now()
    exe = Path(sys.executable)
    stopped = []
    if not restarted and installer.needs_install(exe):
        # First start of a downloaded exe: replace an older running version (e.g. 3.0.0)
        stopped = installer.take_over(exe)
        if stopped is None:
            show_message('The same or a newer version of Go-to-Bed is already running.\n'
                         'Look for the icon in the system tray.')
            return 0
        if lock is None:
            lock = instance.acquire_lock(wait_seconds=15)
    if lock is None:
        show_message('Go-to-Bed is already running.\nLook for the icon in the system tray.')
        return 0

    if not restarted and installer.needs_install(exe):
        try:
            legacy = installer.legacy_exes(exe, [*(stopped or []), installer.autostart_path()])
            target = installer.install_self(exe)
            instance.release_lock(lock)
            updater.relaunch(target, ['--installed-from', str(exe)] + [a for p in legacy for a in ('--replaced', str(p))])
            return 0
        except (installer.InstallError, OSError) as e:
            log.error("Installation failed, running from %s instead: %s", exe, e)

    try:
        GotoBedApp(config, updated_from=args.updated_from, installed_from=args.installed_from,
                   replaced=args.replaced).run()
    except Exception:
        log.exception("Fatal error")
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
