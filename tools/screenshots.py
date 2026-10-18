"""Take the screenshots used in the README (Windows only).

Usage: python tools/screenshots.py [OUT_DIR]   (default: docs/screenshots)

Opens each window with sample data in a temporary data folder, captures it
including the title bar and closes it again. Windows flash up on the screen
for a few seconds - don't touch the mouse meanwhile.
"""
import ctypes
import ctypes.wintypes
import os
import sys
import tempfile
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
os.environ['GOTOBED_DATA_DIR'] = tempfile.mkdtemp(prefix='gotobed-shots-')

from PIL import ImageGrab  # noqa: E402

import main  # noqa: E402
from config import Config  # noqa: E402


def sample_config() -> Config:
    config = Config()
    config.save({'bedtime': '22:30', 'weekdays': [1, 2, 3, 4, 7], 'pre_warning_minutes': 15})
    history = []
    for days_ago in range(9, -1, -1):
        day = (date.today() - timedelta(days=days_ago)).isoformat()
        history.append({'date': day, 'time': '22:30:00', 'action': 'showed'})
        if days_ago % 3 == 0:
            history.append({'date': day, 'time': '22:31:12', 'action': 'snoozed'})
            history.append({'date': day, 'time': '22:40:00', 'action': 'showed'})
        history.append({'date': day, 'time': '22:41:05' if days_ago % 3 == 0 else '22:32:40', 'action': 'dismissed'})
    config.stats.update({
        'history': history,
        'total_reminders': sum(e['action'] == 'showed' for e in history),
        'snoozed': sum(e['action'] == 'snoozed' for e in history),
        'dismissed': sum(e['action'] == 'dismissed' for e in history),
    })
    return config


def window_rect(window):
    """Screen rectangle of the window including its title bar, without the drop shadow."""
    hwnd = int(window.wm_frame(), 16)
    rect = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect))  # extended frame bounds
    return rect.left, rect.top, rect.right, rect.bottom


def capture(app, window, path: Path) -> None:
    window.attributes('-topmost', True)
    window.lift()
    window.focus_force()
    for _ in range(20):
        app.root.update()
        time.sleep(0.05)
    ImageGrab.grab(window_rect(window), all_screens=True).save(path)
    print(f'saved {path}')
    window.destroy()
    app.root.update()


def main_() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'docs' / 'screenshots'
    out.mkdir(parents=True, exist_ok=True)

    main.enable_dpi_awareness()
    app = main.GotoBedApp(sample_config())
    app._play_sound = lambda: None

    app._open_settings()
    capture(app, app._settings_window.window, out / 'settings.png')
    app._open_stats()
    capture(app, app._stats_window.window, out / 'statistics.png')
    app._show_prewarning_reminder()
    capture(app, app._reminder_window.window, out / 'prewarning.png')
    app._show_reminder(snooze_minutes=10, on_snooze=lambda: None, on_dismiss=lambda: None)
    capture(app, app._reminder_window.window, out / 'reminder.png')
    app._show_reminder(snooze_minutes=10, on_snooze=lambda: None, on_dismiss=lambda: None)
    app._reminder_window.GOOD_NIGHT_MS = 60_000  # keep it open while capturing
    app._reminder_window._handle_going()
    capture(app, app._reminder_window.window, out / 'good-night.png')
    app.root.destroy()


if __name__ == '__main__':
    if sys.platform != 'win32':
        sys.exit('Screenshots need Windows (run with a Windows Python).')
    main_()
