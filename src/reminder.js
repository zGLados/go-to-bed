const { ipcRenderer } = require('electron');

// Update current time
function updateTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false
  });
  document.getElementById('currentTime').textContent = timeString;
}

// Load config to show snooze minutes
async function loadConfig() {
  try {
    const config = await ipcRenderer.invoke('get-config');
    document.getElementById('snoozeMinutes').textContent = config.snoozeMinutes;
  } catch (error) {
    console.error('Error loading config:', error);
  }
}

async function snooze() {
  try {
    const snoozeMinutes = await ipcRenderer.invoke('snooze-reminder');
    // Window will be closed by main process
  } catch (error) {
    console.error('Error snoozing:', error);
    window.close();
  }
}

async function dismiss() {
  try {
    await ipcRenderer.invoke('dismiss-reminder');
    // Window will be closed by main process
  } catch (error) {
    console.error('Error dismissing:', error);
    window.close();
  }
}

// Initialize
window.addEventListener('DOMContentLoaded', () => {
  updateTime();
  setInterval(updateTime, 1000);
  loadConfig();
});
