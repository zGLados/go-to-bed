# 🌙 Go-to-Bed

A lightweight bedtime reminder for Windows that lives in the system tray and helps you keep a healthy sleep schedule.

## ✨ Features

- 🖥️ **System tray app** - runs quietly in the background (double-click the icon for settings)
- ⏰ **Flexible schedule** - bedtime plus active weekdays
- 🔔 **Pre-warning** - optional reminder X minutes before bedtime
- 😴 **Snooze** - postpone the reminder for a configurable time
- 🔊 **Sound & Windows notifications**
- 📊 **Statistics** - track how often you actually went to bed
- 🚀 **Autostart** - optionally starts with Windows
- 💤 **Sleep-safe** - reminders missed by up to 5 minutes (e.g. PC was asleep) are still shown

## 📦 Download

Every push to `main` is built automatically by GitHub Actions:

- **Releases**: download `GotoBed.exe` from the [latest release](../../releases/latest) (built for every `v*` tag)
- **Latest build**: open the newest run under [Actions](../../actions/workflows/build.yml) and download the `GotoBed-windows` artifact

The .exe is standalone - no Python needed. Just run it.

> Windows SmartScreen may warn because the .exe is not code-signed: click *More info → Run anyway*.

## 🎯 Usage

On first launch the settings window opens. Afterwards the app sits in the tray:

| Tray menu | |
|---|---|
| **Bedtime: HH:MM** | Your configured bedtime |
| **Reminders enabled** | Turn reminders on/off |
| **Settings** | Bedtime, pre-warning, weekdays, snooze, autostart, sound |
| **Statistics** | Reminders shown / snoozed / followed |
| **Test Reminder** | Show the reminder now |
| **Show Data Folder** | Opens `%APPDATA%\GotoBed` (config, stats, log) |
| **Quit** | Exit the app |

Only one instance runs at a time; starting it again shows a hint instead.

## 🛠️ Development

Requires Python 3.12 on Windows.

```bash
pip install -r requirements-dev.txt
python -m pytest            # unit tests (scheduler, config)
python src/main.py          # run the app
python src/main.py --self-test   # open every window once and exit (0 = OK)
python build.py             # build dist/GotoBed.exe
```

Set `GOTOBED_DATA_DIR` to use a different data folder (handy for testing).

### Releasing

1. Bump `__version__` in `src/version.py`
2. Commit, then `git tag v3.0.1 && git push origin main --tags`
3. GitHub Actions tests, builds, self-tests the .exe and attaches it to a new release

### Project structure

```
src/
├── main.py        # Entry point, tray icon, app logic
├── config.py      # Config + statistics (JSON in %APPDATA%\GotoBed)
├── scheduler.py   # Decides when reminders are due
├── settings.py    # Settings window
├── reminder.py    # Reminder window
├── stats.py       # Statistics window
├── ui.py          # Shared Tk helpers
└── version.py
tests/             # pytest tests
assets/            # icon + reminder image (bundled into the .exe)
build.py           # PyInstaller build
.github/workflows/build.yml
```

Tk runs on the main thread; the tray icon and scheduler run on background threads and hand work to Tk via a queue (`GotoBedApp.call_ui`).

## 📝 License

MIT License - feel free to use and modify!

Sweet dreams! 😴🌙
