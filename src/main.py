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
from tkinter import messagebox

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from config import Config, resource_path, APP_NAME
from reminder import ReminderWindow
from scheduler import BedtimeScheduler
from settings import SettingsWindow
from stats import StatsWindow
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


def acquire_single_instance_lock():
    """Return a mutex handle, or None if another instance is already running (Windows only)."""
    if sys.platform != 'win32':
        return True
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    handle = kernel32.CreateMutexW(None, False, f'Local\\{APP_NAME}SingleInstance')
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        return None
    return handle


class GotoBedApp:
    """Main application class."""

    def __init__(self, config: Config = None):
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
            import winreg
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if self.config.get('autostart'):
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{sys.executable}"')
                    log.info("Autostart enabled: %s", sys.executable)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                        log.info("Autostart disabled")
                    except FileNotFoundError:
                        pass
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
        self._settings_window = SettingsWindow(self.root, self.config.get_all(), self._save_settings)

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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Go-to-Bed bedtime reminder')
    parser.add_argument('--self-test', action='store_true',
                        help='open all windows once and exit (exit code 0 = OK)')
    args = parser.parse_args()

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

    lock = acquire_single_instance_lock()
    if lock is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('Go-to-Bed', 'Go-to-Bed is already running.\nLook for the icon in the system tray.')
        root.destroy()
        return 0

    try:
        GotoBedApp(config).run()
    except Exception:
        log.exception("Fatal error")
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
