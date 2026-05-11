# 🌙 Go-to-Bed v2.0

A modern Windows application with system tray integration that reminds you to go to bed on time.

## ✨ Features

- 🖥️ **System Tray Integration** - Runs in the background, always ready
- ⏰ **Flexible Scheduling** - Set your bedtime and active weekdays
- 😴 **Snooze Function** - Postpone reminders for a few minutes
- 📊 **Statistics** - Track how often you follow the reminders
- 🎨 **Modern UI** - Beautiful, intuitive design
- 🚀 **Autostart** - Automatically starts with Windows (optional)
- 💾 **Persistent Settings** - Your configuration is saved

## 📦 Installation

### Prerequisites

- Node.js (Version 18 or higher)
- npm (comes with Node.js)

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Start Application (Development Mode)

```bash
npm start
```

### Step 3: Create Installer

```bash
npm run build:win
```

The installer will be created in the `dist` folder.

## 🎯 Usage

### Getting Started

1. Start the application
2. The system tray icon appears in the taskbar
3. Right-click on the icon → "Settings"
4. Set your bedtime and active weekdays
5. Click "Save"

### Features

**Settings:**
- Enable/Disable reminders
- Set your bedtime
- Select active weekdays (e.g., weekdays only)
- Adjust snooze duration (1-60 minutes)
- Start with Windows

**Reminder:**
- When the set time is reached, a reminder window appears
- **Snooze**: Postpone the reminder by X minutes
- **Okay, I'm going!**: Confirm that you're going to bed

**Statistics:**
- See how many reminders you received
- How often you followed the reminder
- Your compliance rate
- Recent activity

### System Tray Menu

- **Bedtime**: Shows your current bedtime
- **Enabled/Disabled**: Toggle reminders on/off
- **Settings**: Open the settings window
- **Statistics**: Open the statistics view
- **Show Data Folder**: Open the folder containing config files
- **Test Reminder**: Test the reminder manually
- **Quit**: Close the application

## 🛠️ Development

### Project Structure

```
go-to-bed/
├── src/
│   ├── main.js         # Main Electron process
│   ├── config.js       # Configuration manager
│   ├── settings.html   # Settings window
│   ├── settings.js     # Settings logic
│   ├── reminder.html   # Reminder window
│   ├── reminder.js     # Reminder logic
│   ├── stats.html      # Statistics window
│   ├── stats.js        # Statistics logic
│   ├── styles.css      # Shared styles
│   ├── titlebar.css    # Custom titlebar styles
│   └── titlebar.js     # Titlebar functionality
├── assets/
│   ├── icon.ico        # Windows icon (multi-size)
│   ├── tray-icon.png   # System tray icon (16x16)
│   └── horse-sleeping-on-grass.png  # Source image
├── package.json
└── README.md
```

### Creating Icons

The icon.ico is created from the horse-sleeping-on-grass.png using ImageMagick:

```bash
# Create square icon with multiple sizes
convert assets/horse-sleeping-on-grass.png -gravity center -extent 500x500 -resize 256x256 assets/icon-256.png
convert assets/horse-sleeping-on-grass.png -gravity center -extent 500x500 -resize 48x48 assets/icon-48.png
convert assets/horse-sleeping-on-grass.png -gravity center -extent 500x500 -resize 32x32 assets/icon-32.png
convert assets/horse-sleeping-on-grass.png -gravity center -extent 500x500 -resize 16x16 assets/icon-16.png
convert assets/icon-16.png assets/icon-32.png assets/icon-48.png assets/icon-256.png assets/icon.ico
```

### Autostart Configuration

The application can be set to start automatically with Windows:

1. Press `Win + R`
2. Enter: `shell:startup`
3. Create a shortcut to the executable file in this folder

Or use the installer, which offers this option automatically.

## 🔧 Technologies

- **Electron** - Desktop app framework
- **Node.js** - Backend logic
- **HTML/CSS/JavaScript** - Frontend
- **electron-builder** - Installer creation
- **NSIS** - Windows installer

## 📝 Configuration

Configuration files are stored in the user directory:

```
C:\Users\[Username]\AppData\Roaming\go-to-bed\
├── config.json    # Settings
└── stats.json     # Statistics
```

You can quickly access this folder via the system tray menu: **Show Data Folder**

## 🐛 Troubleshooting

**Application doesn't start:**
- Make sure Node.js is installed
- Run `npm install` to install all dependencies

**Tray icon is not displayed:**
- Make sure `assets/tray-icon.png` exists
- Check if the icon is properly created

**Reminders don't work:**
- Check if reminders are enabled (system tray menu)
- Make sure the current weekday is activated
- The app checks every minute if it's time

**Settings are not saved:**
- Open the system tray menu → "Show Data Folder"
- Check if config.json exists
- Look at the console for error messages (F12 in settings window)

## 📄 License

MIT License - see LICENSE file

## 🤝 Contributing

Feedback and contributions are welcome! Open an issue or pull request on GitHub.

## 🎉 Thanks

Thanks for using Go-to-Bed! Sleep well! 😴🌙
