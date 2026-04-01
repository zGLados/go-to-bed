# Changelog

All notable changes to this project will be documented in this file.

## [2.1.1] - 2026-04-01

### Fixed
- 🐛 Removed "Start now" option after installation (service starts on next boot/autostart)
- 🪟 PowerShell window now properly hidden when opening settings GUI
- 🎨 Desktop shortcut configured to run silently

### Changed
- Settings GUI launches without visible console window
- Cleaner post-installation experience

## [2.1.0] - 2026-04-01

### ✨ New Features
- 🎨 **Beautiful WPF Configuration GUI** - Modern, user-friendly settings interface
- 🖱️ **Desktop icon opens settings** - Double-click to configure instead of starting service
- 🎯 **Quick-select buttons** - Easy day selection (Every Day, Weekdays, Weekend)
- 📱 **Better UX** - Intuitive hour/minute input with validation
- 💾 **Live preview** - See your settings before saving

### Changed
- README no longer opens automatically after installation
- Desktop shortcut labeled as "Settings" for clarity
- Improved installer UI with better descriptions and icons

### Technical
- Complete rewrite of configure.ps1 with WPF
- Better icon usage in installer
- Cleaner user experience throughout

## [2.0.3] - 2026-04-01

### Fixed
- 🐛 Fixed VBS script module error
- Shortcuts now use PowerShell directly with hidden window
- Autostart uses VBS for completely silent execution
- Added multiple launcher methods (VBS, BAT, PS1) for maximum compatibility

## [2.0.2] - 2026-04-01

### Fixed
- 🐛 Fixed VBS file execution (code 193 error)
- VBS files now properly launched via wscript.exe
- Fixed autostart, shortcuts, and post-install launch

## [2.0.1] - 2026-04-01

### Fixed
- 🐛 Fixed installer runtime error at line 156 (FindComponent issue)
- Fixed label creation in configuration wizard page

## [2.0.0] - PowerShell Rewrite

### 🎯 Major Change: Complete PowerShell Rewrite
- ✨ **No more Go/Fyne** - Complete rewrite in PowerShell
- 🖥️ **WPF UI** - Beautiful native Windows fullscreen banner
- ⚡ **No compilation** - PowerShell scripts run directly
- 🚀 **Fast builds** - GitHub Actions builds in ~30 seconds (was 5+ minutes)
- 📦 **Smaller installer** - <1MB vs >50MB
- 🔧 **Easier maintenance** - Pure PowerShell, no CGO dependencies

### Features
- WPF-based fullscreen banner with modern UI
- Background service using PowerShell
- Silent launcher (VBScript) for hidden execution
- Live config reloading (no restart needed)
- System notifications + fullscreen banner
- Auto-close banner after 2 minutes

### Technical
- `GoToBed.ps1` - Main background service
- `Show-Banner.ps1` - WPF fullscreen banner UI
- `Start-GoToBed.vbs` - Silent launcher (hides console)
- Removed Go, Fyne, CGO dependencies
- Simplified GitHub Actions workflow
- Native Windows .NET Framework (WPF)

## [1.3.0] - Installer Configuration Wizard

### 🎯 Major Feature: In-Installer Configuration
- ✨ **Custom wizard page** - Configure bedtime and weekdays during installation
- ⏰ **Time selection** - Hour and minute input fields
- 📅 **Weekday selection** - Every day, weekdays, weekend, or custom
- ✅ **Input validation** - Ensures valid time and at least one day selected
- 💾 **Auto-save** - Configuration saved automatically after installation

### Changed
- 🌍 **English documentation** - All docs translated for international use
- 📝 README, QUICKSTART, and CHANGELOG now in English
- 🗑️ Removed German-only installer messages

### Technical
- Pascal Script code for custom wizard pages
- JSON config file creation during installation
- No longer requires manual PowerShell configuration script
- Quick-select buttons (Every day, Weekdays, Weekend)

## [1.2.0] - Windows Installer Release

### 🎯 Major Feature: One-Click Windows Installer
- ✨ **Inno Setup based installer** (GoToBed-Setup.exe)
- 🚀 Optional automatic startup at Windows start
- ⚙️ Guided configuration wizard during installation
- 🗑️ Clean uninstallation via Windows Control Panel
- 📋 Start menu integration (Program + Configuration)
- 🔧 Registry integration for autostart

### Changed
- 🎯 Focus on Windows (Linux/macOS temporarily paused)
- 📖 Complete README rewrite for Windows
- 🔨 Build with -ldflags "-H windowsgui" (hides console)

### Technical
- Inno Setup script for installer generation
- GitHub Actions builds installer automatically on each release
- Registry integration for autostart
- Mutex check for single instance (in installer)

## [1.1.0] - Weekday Selection Feature

### Added
- 📅 **Weekday selection** - Choose when to show reminder (every day, weekdays, weekend, custom)
- 🔧 Interactive configuration script with 4 options:
  - Every day (Monday to Sunday)
  - Weekdays (Monday to Friday)
  - Weekend (Saturday and Sunday)
  - Custom (select individual days)
- 💻 PowerShell configuration script for Windows (`configure.ps1`)
- 📝 JSON-based configuration file for better structure

### Changed
- ⚙️ Configuration file format from simple text to JSON
- 📖 README extended with detailed configuration examples
- 🔄 Automatic migration from old configurations to new format

### Technical
- Config structure extended with `weekdays` array
- Weekday validation in main loop
- Extended logging for active weekdays

## [1.0.0] - Initial Release

### Added
- 🌙 Fullscreen banner at bedtime
- ⏰ Configurable bedtime
- 👤 Personalized message with username
- 🔄 Background service (systemd for Linux)
- 📦 Multi-platform support (Linux, macOS, Windows)
- 🚀 GitHub Actions for automatic builds
- 📝 Complete documentation
- 🛠️ Simple installation script
