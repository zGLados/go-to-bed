const { app, BrowserWindow, Tray, Menu, ipcMain, nativeImage } = require('electron');
const path = require('path');
const Config = require('./config');

// Disable GPU acceleration to prevent GPU errors on Linux
app.disableHardwareAcceleration();

// Additional command line switches for better compatibility
app.commandLine.appendSwitch('disable-gpu');
app.commandLine.appendSwitch('disable-gpu-compositing');

let tray = null;
let settingsWindow = null;
let reminderWindow = null;
let statsWindow = null;
let config = null;
let checkInterval = null;
let snoozeTimeout = null;

// Ensure single instance
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // Focus settings window if someone tries to launch app again
    if (settingsWindow) {
      if (settingsWindow.isMinimized()) settingsWindow.restore();
      settingsWindow.focus();
    } else {
      createSettingsWindow();
    }
  });
}

function createTray() {
  // Create a simple tray icon (we'll use a basic icon for now)
  const iconPath = path.join(__dirname, '../assets/tray-icon.png');
  
  let trayIcon;
  try {
    if (require('fs').existsSync(iconPath)) {
      trayIcon = nativeImage.createFromPath(iconPath);
    } else {
      // Create a simple colored square as fallback (16x16)
      const canvas = require('electron').nativeImage.createEmpty();
      trayIcon = nativeImage.createFromDataURL(
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAhGVYSWZNTQAqAAAACAAFARIAAwAAAAEAAQAAARoABQAAAAEAAABKARsABQAAAAEAAABSASgAAwAAAAEAAgAAh2kABAAAAAEAAABaAAAAAAAAAEgAAAABAAAASAAAAAEAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAEKADAAQAAAABAAAAEAAAAADHbxzxAAAACXBIWXMAAAsTAAALEwEAmpwYAAACGmlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNi4wLjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgoZXuEHAAAAiUlEQVQ4Ee2SQQqAIBBFR4q6/1Vae4LCRRvBiEwHSYTMbfMYZvF5g+I/xRdAKXWhlKoYQ5Y5gRBChBCi1jqFEBpjcM7BO49SCs45CCHgnEMIAVJKlFJYa5FzRikFay2stcg5I6WElBKllJRSUkpJKSWllJRSUkpJKSWllJRSUkr5v5TyD/MCOXC7Q4xF3M8AAAAASUVORK5CYII='
      );
    }
  } catch (error) {
    // Create a simple colored icon as fallback
    trayIcon = nativeImage.createFromDataURL(
      'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAhGVYSWZNTQAqAAAACAAFARIAAwAAAAEAAQAAARoABQAAAAEAAABKARsABQAAAAEAAABSASgAAwAAAAEAAgAAh2kABAAAAAEAAABaAAAAAAAAAEgAAAABAAAASAAAAAEAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAEKADAAQAAAABAAAAEAAAAADHbxzxAAAACXBIWXMAAAsTAAALEwEAmpwYAAACGmlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNi4wLjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgoZXuEHAAAAiUlEQVQ4Ee2SQQqAIBBFR4q6/1Vae4LCRRvBiEwHSYTMbfMYZvF5g+I/xRdAKXWhlKoYQ5Y5gRBChBCi1jqFEBpjcM7BO49SCs45CCHgnEMIAVJKlFJYa5FzRikFay2stcg5I6WElBKllJRSUkpJKSWllJRSUkpJKSWllJRSUkr5v5TyD/MCOXC7Q4xF3M8AAAAASUVORK5CYII='
    );
  }
  
  tray = new Tray(trayIcon);
  tray.setToolTip('Go-to-Bed Reminder');
  
  updateTrayMenu();
}

function updateTrayMenu() {
  const isEnabled = config.get('enabled');
  const bedtime = config.get('bedtime');
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: `Schlafenszeit: ${bedtime}`,
      enabled: false
    },
    { type: 'separator' },
    {
      label: isEnabled ? '✓ Aktiviert' : '✗ Deaktiviert',
      type: 'checkbox',
      checked: isEnabled,
      click: () => {
        config.save({ enabled: !isEnabled });
        updateTrayMenu();
        if (config.get('enabled')) {
          startChecking();
        } else {
          stopChecking();
        }
      }
    },
    { type: 'separator' },
    {
      label: 'Einstellungen',
      click: createSettingsWindow
    },
    {
      label: 'Statistiken',
      click: createStatsWindow
    },
    { type: 'separator' },
    {
      label: 'Test Erinnerung',
      click: () => showReminder(false)
    },
    { type: 'separator' },
    {
      label: 'Beenden',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);
  
  tray.setContextMenu(contextMenu);
}

function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.focus();
    return;
  }

  settingsWindow = new BrowserWindow({
    width: 500,
    height: 600,
    title: 'Go-to-Bed Einstellungen',
    resizable: false,
    frame: false,
    backgroundColor: '#f0f0f0',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  settingsWindow.loadFile(path.join(__dirname, 'settings.html'));

  settingsWindow.on('closed', () => {
    settingsWindow = null;
  });
}

function createStatsWindow() {
  if (statsWindow) {
    statsWindow.focus();
    return;
  }

  statsWindow = new BrowserWindow({
    width: 600,
    height: 500,
    title: 'Go-to-Bed Statistiken',
    resizable: false,
    frame: false,
    backgroundColor: '#f0f0f0',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  statsWindow.loadFile(path.join(__dirname, 'stats.html'));

  statsWindow.on('closed', () => {
    statsWindow = null;
  });
}

function showReminder(isActual = true) {
  if (reminderWindow) {
    reminderWindow.focus();
    return;
  }

  reminderWindow = new BrowserWindow({
    width: 500,
    height: 300,
    title: 'Zeit ins Bett zu gehen!',
    resizable: false,
    frame: false,
    alwaysOnTop: true,
    backgroundColor: '#f0f0f0',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  reminderWindow.loadFile(path.join(__dirname, 'reminder.html'));

  reminderWindow.on('closed', () => {
    reminderWindow = null;
  });

  // Flash the window to get attention
  reminderWindow.flashFrame(true);
  reminderWindow.focus();

  if (isActual) {
    config.addStatEntry('showed');
  }
}

function checkBedtime() {
  if (!config.get('enabled')) {
    return;
  }

  const now = new Date();
  const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  
  const bedtime = config.get('bedtime');
  const activeWeekdays = config.get('weekdays');

  // Check if today is an active day
  if (!activeWeekdays.includes(currentDay)) {
    return;
  }

  // Check if it's bedtime
  if (currentTime === bedtime) {
    showReminder(true);
  }
}

function startChecking() {
  if (checkInterval) {
    clearInterval(checkInterval);
  }
  // Check every minute
  checkInterval = setInterval(checkBedtime, 60000);
  // Also check immediately
  checkBedtime();
}

function stopChecking() {
  if (checkInterval) {
    clearInterval(checkInterval);
    checkInterval = null;
  }
}

// IPC Handlers
ipcMain.handle('get-config', () => {
  return config.getAll();
});

ipcMain.handle('save-config', (event, newConfig) => {
  const success = config.save(newConfig);
  if (success) {
    updateTrayMenu();
    
    // Update autostart setting
    if (process.platform === 'win32' && newConfig.autostart !== undefined) {
      app.setLoginItemSettings({
        openAtLogin: newConfig.autostart,
        path: process.execPath
      });
    }
    
    if (config.get('enabled')) {
      startChecking();
    } else {
      stopChecking();
    }
  }
  return success;
});

ipcMain.handle('get-stats', () => {
  return config.getStats();
});

ipcMain.handle('snooze-reminder', () => {
  const snoozeMinutes = config.get('snoozeMinutes');
  
  if (reminderWindow) {
    reminderWindow.close();
  }

  config.addStatEntry('snoozed');

  // Set timeout to show reminder again
  if (snoozeTimeout) {
    clearTimeout(snoozeTimeout);
  }

  snoozeTimeout = setTimeout(() => {
    showReminder(true);
    snoozeTimeout = null;
  }, snoozeMinutes * 60 * 1000);

  return snoozeMinutes;
});

ipcMain.handle('dismiss-reminder', () => {
  if (reminderWindow) {
    reminderWindow.close();
  }
  config.addStatEntry('dismissed');
  return true;
});

// Window controls
ipcMain.on('window-minimize', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) win.minimize();
});

ipcMain.on('window-close', (event) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (win) win.close();
});

// App lifecycle
app.whenReady().then(() => {
  config = new Config();
  createTray();
  
  // Set autostart for Windows (can be toggled via settings)
  if (process.platform === 'win32') {
    const autostartEnabled = config.get('autostart') !== false; // Default true
    app.setLoginItemSettings({
      openAtLogin: autostartEnabled,
      path: process.execPath
    });
  }
  
  if (config.get('enabled')) {
    startChecking();
  }

  // Show settings on first run
  const isFirstRun = !config.configPath || !require('fs').existsSync(config.configPath);
  if (isFirstRun) {
    createSettingsWindow();
  }
});

app.on('window-all-closed', (e) => {
  // Don't quit when all windows are closed (keep running in tray)
  e.preventDefault();
});

app.on('before-quit', () => {
  stopChecking();
  if (snoozeTimeout) {
    clearTimeout(snoozeTimeout);
  }
});

app.on('activate', () => {
  createSettingsWindow();
});
