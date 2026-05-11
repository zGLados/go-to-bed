const { ipcRenderer } = require('electron');

let currentConfig = null;

async function loadSettings() {
  try {
    currentConfig = await ipcRenderer.invoke('get-config');
    
    document.getElementById('enabled').checked = currentConfig.enabled;
    document.getElementById('autostart').checked = currentConfig.autostart !== false;
    document.getElementById('bedtime').value = currentConfig.bedtime;
    document.getElementById('snoozeMinutes').value = currentConfig.snoozeMinutes;
    
    // Set weekdays
    const checkboxes = document.querySelectorAll('.weekday-checkbox');
    checkboxes.forEach(cb => {
      cb.checked = currentConfig.weekdays.includes(parseInt(cb.value));
    });
  } catch (error) {
    showMessage('Fehler beim Laden der Einstellungen: ' + error.message, 'error');
  }
}

async function saveSettings() {
  try {
    const enabled = document.getElementById('enabled').checked;
    const autostart = document.getElementById('autostart').checked;
    const bedtime = document.getElementById('bedtime').value;
    const snoozeMinutes = parseInt(document.getElementById('snoozeMinutes').value);
    
    // Get selected weekdays
    const weekdays = [];
    document.querySelectorAll('.weekday-checkbox:checked').forEach(cb => {
      weekdays.push(parseInt(cb.value));
    });

    if (weekdays.length === 0) {
      showMessage('Bitte wähle mindestens einen Wochentag aus!', 'error');
      return;
    }

    const newConfig = {
      enabled,
      autostart,
      bedtime,
      snoozeMinutes,
      weekdays
    };

    const success = await ipcRenderer.invoke('save-config', newConfig);
    
    if (success) {
      showMessage('✓ Einstellungen gespeichert!', 'success');
      setTimeout(() => {
        window.close();
      }, 1000);
    } else {
      showMessage('Fehler beim Speichern der Einstellungen', 'error');
    }
  } catch (error) {
    showMessage('Fehler: ' + error.message, 'error');
  }
}

function selectWeekdays(days) {
  const checkboxes = document.querySelectorAll('.weekday-checkbox');
  checkboxes.forEach(cb => {
    cb.checked = days.includes(parseInt(cb.value));
  });
}

function showMessage(text, type = 'info') {
  const messageDiv = document.getElementById('message');
  messageDiv.textContent = text;
  messageDiv.className = 'message ' + type;
  messageDiv.style.display = 'block';
  
  setTimeout(() => {
    messageDiv.style.display = 'none';
  }, 3000);
}

// Load settings when page loads
window.addEventListener('DOMContentLoaded', loadSettings);
