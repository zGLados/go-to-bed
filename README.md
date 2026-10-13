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

On first launch the settings window opens. Afterwards the app sits in the system tray (if you don't see it, click the **^** arrow in the taskbar and drag the horse icon into the visible area). Double-click the icon to open the settings.

### Tray menu

| Entry | What it does |
|---|---|
| **Bedtime: HH:MM** | Shows your configured bedtime |
| **Reminders enabled** | Turns all reminders on/off (also cancels a running snooze) |
| **Settings** | Opens the settings window |
| **Statistics** | Reminders shown / snoozed / followed, recent activity |
| **Test Reminder** | Shows the bedtime reminder right now |
| **Show Data Folder** | Opens `%APPDATA%\GotoBed` (config, stats, log) |
| **Quit (vX.Y.Z)** | Exits the app and shows the installed version |

Only one instance runs at a time; starting it again shows a hint instead.

### Settings

| Setting | Default | Meaning |
|---|---|---|
| Enable bedtime reminders | on | Master switch, same as the tray entry |
| Bedtime | 22:00 | When the reminder appears |
| Pre-warning | 15 min | Extra reminder this many minutes before bedtime (0 = off, max 120) |
| Active Days | Mon–Fri | Days on which reminders are shown (at least one) |
| Snooze duration | 10 min | How long *Snooze* postpones the reminder (1–120) |
| Start with Windows | on | Starts `GotoBed.exe` automatically after login |
| Play notification sound | on | Windows sound when a reminder appears |

### How reminders work

- At **pre-warning time** a window ("Bedtime in N minutes!") and a Windows notification appear. Just click *OK*.
- At **bedtime** the reminder window appears on top of all other windows, with a notification and sound. You can choose:
  - **Snooze (N min)** – the reminder comes back after the snooze duration (as often as you like).
  - **Okay, I'm going!** – done for tonight. Closing the window counts the same.
- Each reminder appears **at most once per night**.
- If the PC was asleep or the app was started a little late, a reminder that is **up to 5 minutes overdue** is still shown; later ones are skipped.
- **Bedtimes after midnight** work: with bedtime 00:30 on *Tuesday*, the pre-warning appears on Monday evening if it falls before midnight. The active day is the day of the bedtime itself.
- Changing settings takes effect immediately, no restart needed.

### Statistics

- **Reminders shown** – every bedtime reminder, including those that come back after snoozing
- **Times snoozed / Times followed** – your clicks (closing the window counts as followed)
- **Compliance rate** – followed ÷ shown

The last 100 events are kept.

## 💾 Your data

Everything is stored in `%APPDATA%\GotoBed\` (tray → *Show Data Folder*):

| File | Contents |
|---|---|
| `config.json` | Your settings. Invalid values are repaired to defaults on start |
| `stats.json` | Statistics and history |
| `gotobed.log` | Log for troubleshooting (max. ~400 KB) |

To move to another PC, copy this folder.

## 🗑️ Uninstall

1. Tray → **Settings** → uncheck **Start with Windows** → *Save* (removes the autostart entry).
2. Tray → **Quit**.
3. Delete `GotoBed.exe` and the folder `%APPDATA%\GotoBed`.

If you already deleted the exe: the autostart entry is `GotoBed` under `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` – remove it there or in *Task Manager → Startup apps*.

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| SmartScreen blocks the start | *More info → Run anyway* (the exe is not code-signed) |
| No tray icon | Check the hidden icons (**^** in the taskbar) |
| "Go-to-Bed is already running" | It is already in the tray; quit it there first |
| No Windows notification | Windows *Settings → System → Notifications* – allow notifications, check *Do not disturb*. The reminder window appears anyway |
| Reminder did not appear | Is today an active day? Was the PC asleep for more than 5 minutes past the time? Look at `gotobed.log` |
| Anything else | Look at `gotobed.log` in the data folder and open an [issue](../../issues) with it |

## 🛠️ Development

Requires Python 3.12. The app targets Windows; on Linux (incl. WSLg) it runs for development only.

```bash
pip install -r requirements-dev.txt
python -m pytest                 # unit tests (scheduler, config)
python src/main.py               # run the app
python src/main.py --self-test   # open every window once and exit (0 = OK)
python build.py                  # build dist/GotoBed.exe (on Windows)
```

Set `GOTOBED_DATA_DIR` to use a different data folder (handy for testing).

How the code is organised, the threading model and the CI pipeline are described in **[docs/architecture.md](docs/architecture.md)**. Changes per version: **[CHANGELOG.md](CHANGELOG.md)**.

### Continuous integration

Every push to `main`, every pull request and every `v*` tag runs [`.github/workflows/build.yml`](.github/workflows/build.yml) on Windows: tests → self-test from source → build → self-test of the built `GotoBed.exe` → artifact upload (→ GitHub release for tags).

### Releasing

1. Bump `__version__` in `src/version.py` and add an entry to `CHANGELOG.md`; commit.
2. `git push origin main` and wait until CI is green.
3. `git tag vX.Y.Z && git push origin vX.Y.Z` – CI builds the exe and creates the release. The build fails if the tag does not match `src/version.py`.

## 📝 License

[MIT](LICENSE) – feel free to use and modify!

Sweet dreams! 😴🌙
