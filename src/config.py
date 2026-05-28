"""Configuration manager for Go-to-Bed app."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class Config:
    """Manages application configuration and statistics."""
    
    def __init__(self):
        """Initialize config manager with default values."""
        # Use AppData on Windows, ~/.local/share on Linux
        if os.name == 'nt':
            self.data_dir = Path(os.getenv('APPDATA')) / 'GotoBed'
        else:
            self.data_dir = Path.home() / '.local' / 'share' / 'gotobed'
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / 'config.json'
        self.stats_file = self.data_dir / 'stats.json'
        
        self.default_config = {
            'bedtime': '22:00',
            'weekdays': [1, 2, 3, 4, 5],  # Monday to Friday (1=Mon, 7=Sun)
            'enabled': True,
            'snooze_minutes': 10,
            'pre_warning_minutes': 15,
            'autostart': True,
            'sound_enabled': True
        }
        
        self.config = self._load_config()
        self.stats = self._load_stats()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return {**self.default_config, **loaded}
        except Exception as e:
            print(f"Error loading config: {e}")
        return self.default_config.copy()
    
    def save(self, new_config: Dict[str, Any] = None) -> bool:
        """Save configuration to file."""
        try:
            if new_config:
                self.config.update(new_config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Config saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        default_stats = {
            'total_reminders': 0,
            'snoozed': 0,
            'dismissed': 0,
            'history': []
        }
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading stats: {e}")
        return default_stats
    
    def _save_stats(self) -> bool:
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving stats: {e}")
            return False
    
    def add_stat_entry(self, action: str) -> None:
        """Add a statistics entry."""
        self.stats['total_reminders'] += 1
        if action == 'snoozed':
            self.stats['snoozed'] += 1
        elif action == 'dismissed':
            self.stats['dismissed'] += 1
        
        self.stats['history'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'action': action
        })
        
        # Keep only last 100 entries
        if len(self.stats['history']) > 100:
            self.stats['history'] = self.stats['history'][-100:]
        
        self._save_stats()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return self.stats.copy()
    
    @property
    def is_first_run(self) -> bool:
        """Check if this is the first run."""
        return not self.config_file.exists()
