const { ipcRenderer } = require('electron');

function setupTitlebar() {
  // Minimize button
  const minimizeBtn = document.getElementById('minimize-btn');
  if (minimizeBtn) {
    minimizeBtn.addEventListener('click', () => {
      ipcRenderer.send('window-minimize');
    });
  }

  // Close button
  const closeBtn = document.getElementById('close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      ipcRenderer.send('window-close');
    });
  }
}

// Setup when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setupTitlebar);
} else {
  setupTitlebar();
}
