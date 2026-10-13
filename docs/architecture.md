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
| `updater.py` | Self-update from GitHub releases: check, download, verify, swap the exe, restart |
| `installer.py` | Per-user installation to `%LOCALAPPDATA%\Programs\GotoBed`, autostart, Start menu shortcut, *Apps & features* entry, uninstall |
| `instance.py` | Single-instance mutex and the named "quit" event other processes use to stop the running app |
| `ui.py` | Shared helpers: `center_window`, `set_window_icon`, `FONT` |
| `version.py` | `__version__` – must match the release tag |

## Threading model

Tk is not thread-safe, and several `tk.Tk()` instances in different threads crash on Windows. Therefore:

```
main thread ── Tk mainloop (hidden root) ── all windows are Toplevels of it
   ▲   polls queue every 100 ms (_process_ui_queue)
   │
   ├── thread "tray"      pystray.Icon.run  ── menu click ──► call_ui(func)
   ├── thread "scheduler" BedtimeScheduler  ── reminder due ──► call_ui(func)
   ├── threads "update-check" / "update"    ── network + file work ──► call_ui(result)
   └── thread "quit-signal"  waits for the named quit event (uninstall) ──► call_ui(_quit_app)
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

- `config.json` – keys `bedtime` (`HH:MM`), `weekdays` (1 = Monday … 7 = Sunday), `enabled`, `snooze_minutes` (1–120), `pre_warning_minutes` (0–120), `autostart`, `sound_enabled`, `auto_update`. Unknown keys are ignored; invalid values fall back to defaults (`Config._validate`).
- `stats.json` – counters `total_reminders` (shown), `snoozed`, `dismissed` and the last 100 `history` entries.
- Files are written to a `.tmp` file first and then replaced, so a crash cannot leave a broken file.
- `gotobed.log` – rotating log (200 KB + 1 backup). The windowed exe has no console, so this is the place to look for errors.

## Self-update

`updater.py` holds the steps as plain functions; `GotoBedApp` (methods under `# updates` in `main.py`) runs them on background threads and decides *when*.

```
start ──3 s──► check ──every 24 h──► check        (+ "Check for Updates": tray entry / settings button)
check:   GET api.github.com/repos/zGLados/go-to-bed/releases/latest
         tag vX.Y.Z > __version__ and asset "GotoBed.exe" present?
           ├─ auto_update on  (or manual "Install") ─► download ─► verify ─► wait until idle ─► install ─► relaunch ─► quit
           └─ auto_update off ─► ask "Install it now?" ─ yes ─► (as above)
                                                     └ no ──► tray entry "Install Update vX.Y.Z"
```

| Step | What happens | On failure |
|---|---|---|
| `fetch_latest` | GitHub API (`GOTOBED_UPDATE_URL` overrides), 30 s timeout | logged; message only for a manual check |
| `download` | to `GotoBed.new.exe.part` next to the exe, then checks size and the `sha256:` digest GitHub publishes for the asset, then renames to `GotoBed.new.exe` | partial file deleted |
| `verify_exe` | runs `GotoBed.new.exe --report-version FILE` with a temporary data folder; the new exe loads its bundled assets and writes its version, which must equal the release version | new exe deleted |
| wait until idle | no restart while a reminder window is open or a snooze is pending; re-checks every minute | – |
| `install` | renames the running `GotoBed.exe` → `GotoBed.old.exe` (allowed on Windows while running), then `GotoBed.new.exe` → `GotoBed.exe` | rolled back, old exe keeps running |
| `relaunch` | starts the new exe detached with `--updated-from <old version>` and `PYINSTALLER_RESET_ENVIRONMENT=1` (so it unpacks itself instead of reusing the old process's files); the old instance quits | – |
| new instance | waits up to 30 s for the single-instance mutex of the old one, deletes `GotoBed.old.exe` (retries while the old process is exiting), shows "Go-to-Bed updated" | leftovers are retried at the next start |

Only the frozen Windows exe updates itself (`is_supported()`); from source, *Check for Updates* only offers the download page. Thanks to the per-user installation (see below) the exe's folder is always writable. The autostart entry keeps pointing at the same path, so it stays valid. `GotoBed.exe --update-now` runs the same steps without UI (used by the end-to-end test).

## Installation

There is no separate installer: `GotoBed.exe` installs itself for the current user, so it always lives in a folder the user can write to and the self-update never needs admin rights.

```
GotoBed.exe started from anywhere (e.g. Downloads)
  └─ another instance running? ─► "already running" message (hint: quit it to install this file)
  └─ install_self(): installed copy exists with the same or a newer version? ─► keep it
                     otherwise copy to …\Programs\GotoBed\GotoBed.new.exe and swap it in (rename trick, see Self-update)
  └─ release the mutex, start the installed copy with --installed-from <path>, exit
installed copy
  └─ waits for the mutex, register(): Start menu shortcut (via PowerShell / WScript.Shell, only if missing)
     and HKCU …\Uninstall\GotoBed (DisplayVersion refreshed on every start, so it matches after updates);
     autostart now points here; notification "Go-to-Bed installed"
```

- The install folder is `%LOCALAPPDATA%\Programs\GotoBed` (`GOTOBED_INSTALL_DIR` overrides it for tests). The data folder stays `%APPDATA%\GotoBed`, so settings survive reinstalling.
- Self-install is skipped for `--updated-from` / `--installed-from` restarts, `--self-test`, `--report-version`, `--update-now`, `--uninstall` and when running from source. If it fails, the app logs the error and simply runs from where it is.
- **Uninstall** (`--uninstall`, which *Apps & features* calls): asks (unless `--quiet`) whether to remove the app and whether to delete the data folder → sets the named event `Local\GotoBedQuit` so a running app quits → waits for the mutex → removes autostart, shortcut and *Apps* entry → starts a hidden PowerShell that deletes the exe (and program/data folder) once this process has exited, because a running exe cannot delete itself.

## Windows integration

- **Autostart:** value `GotoBed` under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, set or removed on start and when settings are saved (`installer.set_autostart`). Only done for the frozen exe – running from source never touches the registry.
- **Apps & features:** key `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\GotoBed` with `UninstallString` = `"…\GotoBed.exe" --uninstall` (and `QuietUninstallString` with `--quiet`).
- **Start menu:** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Go-to-Bed.lnk`.
- **Single instance:** named mutex `Local\GotoBedSingleInstance`; **quit request:** named event `Local\GotoBedQuit` (`instance.py`).
- **Notifications:** `pystray.Icon.notify` (Windows toast). **Sound:** `winsound.MessageBeep`.
- **High DPI:** `SetProcessDpiAwareness(1)` at start.

## Build

`python build.py` runs PyInstaller with `--onefile --windowed`, bundles `assets/` (found at runtime via `sys._MEIPASS` in `resource_path()`), uses `assets/icon.ico` as the exe icon and adds the hidden imports `pystray._win32` and `PIL._tkinter_finder`. Output: `dist/GotoBed.exe` (~16 MB). PyInstaller builds for the OS it runs on, so a Windows exe needs Windows (or CI).

## Tests and self-test

- `tests/` – pytest tests; `pytest.ini` puts `src` on the path.
  - `test_scheduler.py`, `test_config.py`, `test_updater.py` – no GUI; the updater tests use a local HTTP server.
  - `test_installer.py` – install/keep newer/replace broken installation and uninstall with fake exes (shell scripts, skipped on Windows).
  - `test_app_update.py` – the update flow inside the app (auto update, waiting while snoozed, auto update off with "yes"/"no" answer, check at start) with the file and network steps mocked; needs a display, skipped without one.
- `tools/e2e_update.py OLD_EXE NEW_EXE` – end-to-end test with two real builds: installs the old one in a temp folder, serves the new one as a fake release on localhost, runs `--update-now` and checks that the file was replaced, the new instance started and the old exe was removed.
- `tools/e2e_install.py EXE` – end-to-end test of self-install and uninstall: starts the exe from a fake Downloads folder, checks the installed copy runs and registered itself (shortcut, *Apps* entry, autostart), then runs `--uninstall --quiet` and checks that the app quit and everything except the data folder is gone. Changes the current user's registry – CI only on Windows.
- `tools/screenshots.py` – regenerates `docs/screenshots/*.png` with sample data (Windows only, uses `PIL.ImageGrab`).
- `GotoBed.exe --self-test` (or `python src/main.py --self-test`) creates the tray icon object, opens every window once, checks that the bundled image loads, closes everything and exits with code 0 (1 on error, details in the log).

## CI / release pipeline

`.github/workflows/build.yml` runs on `windows-latest` for pushes to `main`, pull requests, `v*` tags and manual runs:

1. Install `requirements-dev.txt` (Python 3.12, pip cache)
2. For tags: fail if the tag is not `v` + `src/version.py`
3. `pytest` → self-test from source → `build.py` → self-test of the built exe (exit code via `Start-Process -Wait -PassThru`, log printed) → end-to-end update test (builds a second exe with version 0.0.1 into `dist-old`, then `tools/e2e_update.py`) → end-to-end install / uninstall test (`tools/e2e_install.py`)
4. Upload `GotoBed.exe` as artifact `GotoBed-windows`
5. For tags: create the GitHub release with the exe and generated notes
