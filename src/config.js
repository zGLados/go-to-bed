const fs = require('fs');
const path = require('path');
const { app } = require('electron');

class Config {
  constructor() {
    this.configPath = path.join(app.getPath('userData'), 'config.json');
    this.statsPath = path.join(app.getPath('userData'), 'stats.json');
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
        const data = fs.readFileSync(this.configPath, 'utf8');
        return { ...this.defaultConfig, ...JSON.parse(data) };
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
    return { ...this.defaultConfig };
  }

  save(newConfig) {
    try {
      this.config = { ...this.config, ...newConfig };
      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
      return true;
    } catch (error) {
      console.error('Error saving config:', error);
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
      fs.writeFileSync(this.statsPath, JSON.stringify(this.stats, null, 2));
    } catch (error) {
      console.error('Error saving stats:', error);
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
      time: new Date().toLocaleTimeString('de-DE')
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
