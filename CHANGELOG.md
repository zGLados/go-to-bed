# Changelog

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
