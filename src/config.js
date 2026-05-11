const fs = require('fs');
const path = require('path');
const { app } = require('electron');

class Config {
  constructor() {
    const userDataPath = app.getPath('userData');
    this.configPath = path.join(userDataPath, 'config.json');
    this.statsPath = path.join(userDataPath, 'stats.json');
    
    console.log('===== Go-to-Bed Config Paths =====');
    console.log('UserData Directory:', userDataPath);
    console.log('Config Path:', this.configPath);
    console.log('Stats Path:', this.statsPath);
    console.log('===================================');
    
    this.defaultConfig = {
      bedtime: '21:30',
      weekdays: [1, 2, 3, 4, 5], // Monday to Friday
      enabled: true,
      snoozeMinutes: 10,
      preWarningMinutes: 0, // 0 = disabled
      autostart: true // Start with Windows
    };
    this.config = this.load();
    this.stats = this.loadStats();
  }

  load() {
    try {
      if (fs.existsSync(this.configPath)) {
        console.log('Loading existing config from:', this.configPath);
        const data = fs.readFileSync(this.configPath, 'utf8');
        return { ...this.defaultConfig, ...JSON.parse(data) };
      } else {
        console.log('No config file found, using defaults');
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
    return { ...this.defaultConfig };
  }

  save(newConfig) {
    try {
      // Ensure userData directory exists
      const dir = path.dirname(this.configPath);
      if (!fs.existsSync(dir)) {
        console.log('Creating userData directory:', dir);
        fs.mkdirSync(dir, { recursive: true });
      }
      
      this.config = { ...this.config, ...newConfig };
      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
      console.log('✓ Config saved successfully to:', this.configPath);
      console.log('  Settings:', this.config);
      return true;
    } catch (error) {
      console.error('✗ Error saving config:', error);
      return false;
    }
  }

  get(key) {
    return this.config[key];
  }

  getAll() {
    return { ...this.config };
  }

  loadStats() {
    try {
      if (fs.existsSync(this.statsPath)) {
        const data = fs.readFileSync(this.statsPath, 'utf8');
        return JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
    return {
      totalReminders: 0,
      snoozed: 0,
      dismissed: 0,
      history: [] // Array of { date, action: 'snoozed'|'dismissed', time }
    };
  }

  saveStats() {
    try {
      // Ensure directory exists
      const dir = path.dirname(this.statsPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.statsPath, JSON.stringify(this.stats, null, 2));
      console.log('✓ Stats saved to:', this.statsPath);
    } catch (error) {
      console.error('✗ Error saving stats:', error);
    }
  }

  addStatEntry(action) {
    this.stats.totalReminders++;
    if (action === 'snoozed') {
      this.stats.snoozed++;
    } else if (action === 'dismissed') {
      this.stats.dismissed++;
    }
    
    this.stats.history.push({
      date: new Date().toISOString().split('T')[0],
      action: action,
      time: new Date().toLocaleTimeString('en-US')
    });

    // Keep only last 100 entries
    if (this.stats.history.length > 100) {
      this.stats.history = this.stats.history.slice(-100);
    }

    this.saveStats();
  }

  getStats() {
    return { ...this.stats };
  }
}

module.exports = Config;
