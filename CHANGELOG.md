# Changelog

## [3.1.0] – 2026-10-13

Upgrading from 3.0.0: see [docs/upgrade-from-3.0.md](docs/upgrade-from-3.0.md).

### Added
- **Auto-update:** checks GitHub at every start and daily, downloads and installs new versions and restarts – never while a reminder is open or a snooze is running. Downloads are checked against the SHA-256 checksum from GitHub, and the new version must pass a start test before it replaces the old one.
- Setting **Install updates automatically** (default on); when off, Go-to-Bed asks whether to install, and the tray keeps **Install Update vX.Y.Z** if you say no.
- **Check for Updates** button in the settings (new *Updates* section with the installed version) and in the tray.
- **Self-installation per user:** the downloaded exe installs itself to `%LOCALAPPDATA%\Programs\GotoBed` (no admin rights; updates always work), adds a Start menu entry and an *Apps & features* entry.
- **One-click upgrade from 3.0.0:** starting the downloaded 3.1.0 stops a running older version, takes over settings and autostart and replaces the old exe with a shortcut.
- **Uninstall** via *Apps & features* (or `--uninstall [--quiet]`): quits the running app, removes program, shortcut, autostart and – if you want – your settings.
- Screenshots in the README.
- Command line options `--update-now`, `--report-version FILE`, `--uninstall [--quiet]`; `build.py --dist DIR`.
- Tests for updater and installer; end-to-end update, install/uninstall and migration (real 3.0.0 → new) tests in CI; `tools/screenshots.py`.

### Fixed
- Autostart could not be turned on in a Windows user profile without the `Run` registry key (now created when missing).

## [3.0.0] – 2026-10-10

Python version made reliable and built automatically.

### Fixed
- Random crashes on Windows: all windows now share one Tk instance on the main thread.
- The exe could not find its icon and images; assets are now bundled.
- Reminders were lost when the PC was asleep in the exact minute (now shown up to 5 minutes late) and could repeat after saving settings.
- Autostart from source registered `python.exe` without the script; now only the exe registers itself.
- Snoozes were counted twice in the statistics.
- The *Play notification sound* setting had no effect.

### Added
- Only one instance can run at a time.
- Sharp windows on high-DPI displays.
- Log file `gotobed.log` in the data folder.
- Horse picture in the reminder window; horse icon in the tray.
- Input validation in the settings; broken config files are repaired automatically.
- `--self-test` option, unit tests, GitHub Actions workflow that builds and tests `GotoBed.exe` and publishes releases.

### Removed
- `plyer` and `schedule` dependencies, `QUICKSTART.md`, `test_dependencies.py`.

## Earlier versions

- **Before 2.0 (April 2026)** – Go version.
- **2.x (April 2026)** – PowerShell/WPF version with an Inno Setup installer.
- **May 2026** – old app removed, Python rewrite (tkinter + pystray) – the basis for 3.0.0.
