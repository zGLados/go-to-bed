const { ipcRenderer } = require('electron');

async function loadStats() {
  try {
    const stats = await ipcRenderer.invoke('get-stats');
    
    document.getElementById('totalReminders').textContent = stats.totalReminders;
    document.getElementById('dismissed').textContent = stats.dismissed;
    document.getElementById('snoozed').textContent = stats.snoozed;
    
    // Calculate compliance rate
    let complianceRate = 0;
    if (stats.totalReminders > 0) {
      complianceRate = Math.round((stats.dismissed / stats.totalReminders) * 100);
    }
    document.getElementById('complianceRate').textContent = complianceRate + '%';
    
    // Display history
    const historyList = document.getElementById('historyList');
    
    if (stats.history && stats.history.length > 0) {
      historyList.innerHTML = '';
      
      // Show last 20 entries
      const recentHistory = stats.history.slice(-20).reverse();
      
      recentHistory.forEach(entry => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const icon = entry.action === 'dismissed' ? '✓' : 
                     entry.action === 'snoozed' ? '⏰' : '📌';
        
        const actionText = entry.action === 'dismissed' ? 'Complied' :
                           entry.action === 'snoozed' ? 'Snoozed' : 'Shown';
        
        historyItem.innerHTML = `
          <span class="history-icon">${icon}</span>
          <span class="history-date">${entry.date}</span>
          <span class="history-time">${entry.time}</span>
          <span class="history-action">${actionText}</span>
        `;
        
        historyList.appendChild(historyItem);
      });
    } else {
      historyList.innerHTML = '<div class="empty-state">No activity yet</div>';
    }
  } catch (error) {
    console.error('Error loading stats:', error);
  }
}

// Load stats when page loads
window.addEventListener('DOMContentLoaded', loadStats);
