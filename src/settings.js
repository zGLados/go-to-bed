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
    showMessage('Error loading settings: ' + error.message, 'error');
  }
}

async function saveSettings() {
  try {
    // Disable save button during save
    const saveBtn = document.querySelector('.btn-primary');
    const originalText = saveBtn.textContent;
    saveBtn.disabled = true;
    saveBtn.textContent = '💾 Saving...';
    
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
      showMessage('⚠️ Please select at least one weekday!', 'error');
      saveBtn.disabled = false;
      saveBtn.textContent = originalText;
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
      showMessage('✓ Settings saved successfully!', 'success');
      setTimeout(() => {
        window.close();
      }, 1500);
    } else {
      showMessage('❌ Error saving settings. Please try again.', 'error');
      saveBtn.disabled = false;
      saveBtn.textContent = originalText;
    }
  } catch (error) {
    showMessage('Error: ' + error.message, 'error');
    const saveBtn = document.querySelector('.btn-primary');
    saveBtn.disabled = false;
    saveBtn.textContent = '💾 Save';
  }
}

function selectWeekdays(days) {
  const checkboxes = document.querySelectorAll('.weekday-checkbox');
  checkboxes.forEach(cb => {
    cb.checked = days.includes(parseInt(cb.value));
  });
  
  // Visual feedback
  showMessage(`📅 ${days.length === 7 ? 'All days' : days.length === 5 ? 'Weekdays' : 'Weekend'} selected`, 'success');
}

function showMessage(text, type = 'info') {
  const messageDiv = document.getElementById('message');
  messageDiv.textContent = text;
  messageDiv.className = 'message ' + type;
  messageDiv.style.display = 'block';
  
  // Auto-hide after 3 seconds for success, keep error visible longer
  const hideDelay = type === 'success' ? 2000 : 5000;
  setTimeout(() => {
    messageDiv.style.display = 'none';
  }, hideDelay);
}

// Load settings when page loads
window.addEventListener('DOMContentLoaded', loadSettings);

// Make functions globally accessible for onclick handlers
window.selectWeekdays = selectWeekdays;
window.saveSettings = saveSettings;
