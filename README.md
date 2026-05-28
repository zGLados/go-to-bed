# 🌙 Go-to-Bed v3.0 (Python Edition)

A lightweight bedtime reminder app with system tray integration that helps you maintain a healthy sleep schedule.

**🪟 Windows Application** - Designed for Windows 10/11. Builds to a standalone .exe file.

## ✨ Features

- 🖥️ **System Tray Integration** - Runs quietly in the background
- ⏰ **Flexible Scheduling** - Set bedtime and choose active weekdays
- 🔔 **Pre-Warnings** - Optional gentle reminder before bedtime
- 😴 **Snooze Function** - Postpone reminders when needed
- 📊 **Statistics** - Track your bedtime compliance
- 🚀 **Autostart** - Automatically starts with Windows
- 💾 **Persistent Settings** - Configuration saved automatically
- 🪶 **Lightweight** - ~15-20MB RAM usage (vs 80-100MB for Electron)

## 🎯 Why Python Version?

This is a complete rewrite of the original Electron version with significant improvements:

- **90% smaller memory footprint** (~20MB vs ~100MB)
- **75% smaller installation size** (~15MB vs ~60MB)
- **Faster startup time**
- **Native OS integration**
- **Simpler, more maintainable code**

## 📦 Installation

### Option 1: Download Pre-built Executable (Easiest)

1. Download `GotoBed.exe` from the releases
2. Run it - that's it! 🎉

### Option 2: Run from Source (Windows)

#### Prerequisites

- **Windows 10 or 11**
- Python 3.8 or higher
- pip (comes with Python)

#### Steps

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python src/main.py
   ```

**Note:** Linux is not officially supported due to system tray limitations. Development and building should be done on Windows.

### Option 3: Build Your Own Executable (Windows Required)

**⚠️ Must be done on Windows!** PyInstaller creates native executables for the OS it runs on.

1. **On Windows: Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run build script**
   ```bash
   python build.py
   ```

3. **Find executable in `dist/` folder**
   ```
   dist/GotoBed.exe
   ```

The resulting .exe is completely standalone - no Python installation needed!

## 🎯 Usage

### First Run

On first launch, the app will:
1. Create a system tray icon (moon icon)
2. Open the settings window automatically
3. Ask you to configure your bedtime preferences

### Settings

Configure your sleep schedule:
- **Bedtime** - When you want to go to bed (HH:MM format)
- **Pre-warning** - Get a gentle reminder X minutes before bedtime
- **Active Days** - Select which days the reminder should be active
- **Snooze Duration** - How many minutes to postpone reminders
- **Autostart** - Launch automatically with Windows
- **Sound** - Enable notification sounds

### System Tray Menu

Right-click the tray icon to access:
- **Bedtime: XX:XX** - Shows your configured bedtime
- **✓ Enabled / ✗ Disabled** - Toggle reminders on/off
- **Settings** - Open settings window
- **Statistics** - View your bedtime tracking stats
- **Test Reminder** - Preview the reminder window
- **Show Data Folder** - Open folder with config files
- **Quit** - Exit the application

### Reminder Window

When it's bedtime (or pre-warning time):
1. A window appears with a friendly reminder
2. A system notification is shown
3. You can either:
   - **Snooze** - Postpone for configured minutes
   - **Okay, I'm going!** - Confirm and close

## 📊 Statistics

Track your sleep habits:
- Total reminders received
- Times snoozed vs followed
- Compliance rate percentage
- Recent activity history

Access via **Statistics** in the tray menu.

## 🗂️ Project Structure

```
python/
├── src/
│   ├── main.py         # Entry point & system tray
│   ├── config.py       # Configuration manager
│   ├── settings.py     # Settings GUI window
│   ├── reminder.py     # Reminder window & notifications
│   ├── stats.py        # Statistics window
│   └── scheduler.py    # Bedtime checker
├── assets/
│   └── icon.ico        # Application icon
├── requirements.txt    # Python dependencies
├── build.py           # PyInstaller build script
└── README.md          # This file
```

## 🔧 Technical Details

### Dependencies

- **pystray** - System tray integration
- **Pillow** - Icon generation
- **plyer** - Native OS notifications
- **schedule** - Time-based scheduling
- **tkinter** - GUI (included with Python)

### Data Storage

Configuration and statistics are stored in:
- **Windows**: `%APPDATA%\GotoBed\`
- **Linux**: `~/.local/share/gotobed/`

Files:
- `config.json` - Your settings
- `stats.json` - Statistics and history

## 🐛 Troubleshooting

### App won't start
- Make sure you have Python 3.8+ installed
- Try running from command line to see error messages:
  ```bash
  python src/main.py
  ```

### Can't see tray icon
- Check system tray settings (Windows: Show all icons)
- Look for a moon icon 🌙

### Notifications not working
- Install plyer: `pip install plyer`
- Check Windows notification settings
- Make sure notifications are allowed for the app

### Build fails
- Update PyInstaller: `pip install --upgrade pyinstaller`
- Delete `build/` and `dist/` folders and try again
- Run as administrator if permission errors occur

## 🚀 Development

### Running in Development

```bash
cd python
python src/main.py
```

### Testing

```bash
# Test reminder immediately
# Right-click tray icon → Test Reminder
```

### Building

```bash
python build.py
```

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! This is a simple, focused app - let's keep it that way.

## 💡 Tips

- Set pre-warning to 15-30 minutes for best results
- Use weekday selection for work/school nights only
- Check statistics weekly to track improvement
- Adjust snooze duration based on your needs

## 🎨 Customization

Want to customize the app?
- Edit icon: Replace `assets/icon.ico`
- Change colors: Modify GUI files in `src/`
- Add features: Python code is simple and well-commented

## ⭐ Comparison: Python vs Electron

| Feature | Python | Electron (Old) |
|---------|--------|----------------|
| Memory Usage | ~20MB | ~100MB |
| Install Size | ~15MB | ~60MB |
| Startup Time | <1s | ~2-3s |
| Native Feel | ✓ | ~ |
| Maintenance | Easy | Complex |

---

Made with ❤️ for better sleep habits

Sweet dreams! 😴🌙
