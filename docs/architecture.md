# Architecture

Go-to-Bed is a small Python 3.12 desktop app for Windows: a system-tray icon ([pystray](https://github.com/moses-palmer/pystray)), windows in tkinter/ttk, images via Pillow. It is packed into a single `GotoBed.exe` with PyInstaller.

## Modules

All code is in `src/` as flat modules (no package); `src/main.py` is the entry point.

| Module | Responsibility |
|---|---|
| `main.py` | `GotoBedApp`: hidden Tk root, tray icon and menu, all user actions, snooze timer, autostart, single-instance lock, logging, `--self-test`; `main()` parses arguments |
| `config.py` | `Config`: loads, validates and atomically saves `config.json` and `stats.json`; `resource_path()` finds bundled assets; `default_data_dir()` |
| `scheduler.py` | `BedtimeScheduler`: background thread that decides when the pre-warning and the bedtime reminder are due |
| `settings.py` | Settings window (input validation) |
| `reminder.py` | Reminder window (pre-warning and bedtime) with the horse picture |
| `stats.py` | Statistics window |
| `ui.py` | Shared helpers: `center_window`, `set_window_icon`, `FONT` |
| `version.py` | `__version__` – must match the release tag |

## Threading model

Tk is not thread-safe, and several `tk.Tk()` instances in different threads crash on Windows. Therefore:

```
main thread ── Tk mainloop (hidden root) ── all windows are Toplevels of it
   ▲   polls queue every 100 ms (_process_ui_queue)
   │
   ├── thread "tray"      pystray.Icon.run  ── menu click ──► call_ui(func)
   └── thread "scheduler" BedtimeScheduler  ── reminder due ──► call_ui(func)
```

- `GotoBedApp.call_ui(func, *args)` is the only way for other threads to reach the UI; it puts the call into a `queue.Queue`.
- Window classes create their `Toplevel` in `__init__` and must only be instantiated on the Tk thread.
- The snooze timer uses `root.after`, so it runs on the Tk thread as well.

## Scheduler rules

`BedtimeScheduler.check(now)` runs every 10 seconds and reads the configuration on every call, so settings changes need no restart.

- For the bedtime of *today* and *tomorrow* (to handle pre-warnings before a bedtime after midnight) it checks: is the bedtime's weekday active, and is `now` within `[due, due + 5 min)`? Then the callback fires.
- Each event is remembered as `(name, bedtime date)` and fires at most once; entries older than two days are dropped.
- A pre-warning is never shown once bedtime has arrived.
- `check()` takes `now` as a parameter, which makes it easy to test (`tests/test_scheduler.py`).

## Data and configuration

The data folder is `%APPDATA%\GotoBed` (Linux: `~/.local/share/gotobed`), or `GOTOBED_DATA_DIR` if set.

- `config.json` – keys `bedtime` (`HH:MM`), `weekdays` (1 = Monday … 7 = Sunday), `enabled`, `snooze_minutes` (1–120), `pre_warning_minutes` (0–120), `autostart`, `sound_enabled`. Unknown keys are ignored; invalid values fall back to defaults (`Config._validate`).
- `stats.json` – counters `total_reminders` (shown), `snoozed`, `dismissed` and the last 100 `history` entries.
- Files are written to a `.tmp` file first and then replaced, so a crash cannot leave a broken file.
- `gotobed.log` – rotating log (200 KB + 1 backup). The windowed exe has no console, so this is the place to look for errors.

## Windows integration

- **Autostart:** value `GotoBed` under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, set or removed on start and when settings are saved. Only done for the frozen exe – running from source never touches the registry.
- **Single instance:** named mutex `Local\GotoBedSingleInstance`.
- **Notifications:** `pystray.Icon.notify` (Windows toast). **Sound:** `winsound.MessageBeep`.
- **High DPI:** `SetProcessDpiAwareness(1)` at start.

## Build

`python build.py` runs PyInstaller with `--onefile --windowed`, bundles `assets/` (found at runtime via `sys._MEIPASS` in `resource_path()`), uses `assets/icon.ico` as the exe icon and adds the hidden imports `pystray._win32` and `PIL._tkinter_finder`. Output: `dist/GotoBed.exe` (~16 MB). PyInstaller builds for the OS it runs on, so a Windows exe needs Windows (or CI).

## Tests and self-test

- `tests/` – pytest tests for scheduler and config; no GUI needed. `pytest.ini` puts `src` on the path.
- `GotoBed.exe --self-test` (or `python src/main.py --self-test`) creates the tray icon object, opens every window once, checks that the bundled image loads, closes everything and exits with code 0 (1 on error, details in the log).

## CI / release pipeline

`.github/workflows/build.yml` runs on `windows-latest` for pushes to `main`, pull requests, `v*` tags and manual runs:

1. Install `requirements-dev.txt` (Python 3.12, pip cache)
2. For tags: fail if the tag is not `v` + `src/version.py`
3. `pytest` → self-test from source → `build.py` → self-test of the built exe (exit code via `Start-Process -Wait -PassThru`, log printed)
4. Upload `GotoBed.exe` as artifact `GotoBed-windows`
5. For tags: create the GitHub release with the exe and generated notes
