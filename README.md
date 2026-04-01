# 🌙 Go-to-Bed

A simple tool that reminds you to go to bed at a specific time!

**Windows Installer available!** - One-click installation with automatic autostart 🚀

## Features

- 🕐 Configurable bedtime
- 📅 **Weekday selection** - Choose which days the reminder appears
- 🖥️ Large fullscreen banner reminder
- 👤 Shows your username in the message
- 🔄 Runs in the background as a service
- 🚀 **Windows: One-click installer** - Automatic autostart and configuration
- 📦 Easy installation

## Installation

### Windows (Recommended) 🎯

**One-Click Installation:**

1. Download `GoToBed-Setup.exe` from the [Releases](../../releases/latest)
2. Double-click the downloaded file
3. Follow the installation wizard:
   - ⏰ **Set your bedtime** - Choose the hour and minute
   - 📅 **Select active days** - Every day, weekdays, weekend, or custom
   - ✅ **"Start automatically when Windows starts"** is recommended
4. **Done!** The program is now running in the background

**Installer Features:**
- ✨ Automatic installation to `Program Files\Go-to-Bed`
- 🚀 Optional autostart at Windows startup
- ⚙️ Guided configuration **during** installation
- 🗑️ Clean uninstallation via Windows Control Panel
- 📋 Start menu integration

**Change Configuration:**
- Start Menu → "Go-to-Bed" → "Configuration"
- Or run: `%ProgramFiles%\Go-to-Bed\configure.ps1`

---

### Linux & macOS (Currently Unavailable)

Development is currently focused on Windows. Linux and macOS versions are planned.

**Note:** Earlier versions supported Linux. If you need Linux, check older releases or build from source.

## Configuration

### Bedtime and Weekdays

During installation, you will be asked:
1. **When** your bedtime should be (e.g., 22:00)
2. **Which weekdays** the reminder should appear

The configuration wizard offers these options:
- **Every day** (Monday to Sunday) - for regular sleep schedules
- **Weekdays** (Monday to Friday) - work days only
- **Weekend** (Saturday and Sunday) - longer nights on weekends
- **Custom** - select individual days

### Manual Configuration

The configuration file is located at:
```
%USERPROFILE%\.go-to-bed.conf
```

It's in JSON format and can be edited directly:

```json
{
  "bedtime": "22:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

**Weekday codes:**
- `Mon` = Monday
- `Tue` = Tuesday
- `Wed` = Wednesday
- `Thu` = Thursday
- `Fri` = Friday
- `Sat` = Saturday
- `Sun` = Sunday

**Examples:**

Weekend only, later bedtime:
```json
{
  "bedtime": "01:00",
  "weekdays": ["Sat", "Sun"]
}
```

Weekdays only:
```json
{
  "bedtime": "22:00",
  "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

## Usage

After the service is installed and configured, it runs automatically in the background.

At the configured bedtime **on the selected weekdays**, it will show:
1. A system notification
2. A large fullscreen banner with your username

The banner displays:
```
🌙 [Your Name], it's time to go to bed! 🌙
Good night! 😴
```

You can close the banner by clicking "OK, I'm going to bed now", or it will automatically disappear after 2 minutes.

**Note:** On days not selected in your configuration, no reminder will appear.

## Development

### Prerequisites

- Go 1.21 or higher
- **For Windows:** Automatically supported by Go build tools

### Build from Source

1. Clone repository:
   ```bash
   git clone https://github.com/zGLados/go-to-bed.git
   cd go-to-bed
   ```

2. Install dependencies:
   ```bash
   go mod download
   ```

3. **Build for Windows:**
   ```bash
   # Standard build (with console window)
   go build -o go-to-bed.exe .
   
   # Background build (without console window)
   go build -ldflags "-H windowsgui" -o go-to-bed.exe .
   ```

4. **Build installer** (Windows with Inno Setup):
   ```bash
   # Install Inno Setup: https://jrsoftware.org/isinfo.php
   # Then:
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
   ```

### Test Locally

```bash
go run .
```

## GitHub Actions

This project uses GitHub Actions for automated installer builds:

- Every tag push (e.g., `v1.2.0`) automatically creates a Windows installer
- The installer is published as a release asset
- Anyone can download the latest version easily

### Create a Release

1. Create and push a tag:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

2. GitHub Actions automatically builds the installer
3. A new release is created with `GoToBed-Setup.exe`

## License

MIT License - see LICENSE file for details.

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## Known Issues

- **First run:** Windows Defender SmartScreen might show a warning (click "More info" → "Run anyway")
- **Configuration:** PowerShell Execution Policy must allow scripts (automatically bypassed with `-ExecutionPolicy Bypass`)

## Roadmap

- [x] **Windows Installer (.exe)** - One-click installation ✅
- [x] **Installer configuration wizard** - Time and day selection during setup ✅
- [ ] **Linux .deb/.rpm packages** - System package manager integration
- [ ] **macOS App Bundle (.app)** - Installable app with setup script
- [ ] System tray icon for Windows
- [ ] Multiple reminder times per day
- [ ] Snooze function
- [ ] Customizable messages
- [ ] GUI for configuration
- [x] Weekday selection ✅

## Support

For issues or questions, please open an issue on GitHub.

---

Good night! 🌙💤
