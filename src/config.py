"""Configuration manager for Go-to-Bed app."""
import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)

APP_NAME = 'GotoBed'


def resource_path(*parts: str) -> Path:
    """Return the path of a bundled resource (works from source and in the .exe)."""
    base = getattr(sys, '_MEIPASS', None)
    if base is None:
        base = Path(__file__).resolve().parent.parent
    return Path(base).joinpath(*parts)


def default_data_dir() -> Path:
    """Return the directory where config and stats are stored."""
    override = os.getenv('GOTOBED_DATA_DIR')
    if override:
        return Path(override)
    if os.name == 'nt':
        appdata = os.getenv('APPDATA')
        return (Path(appdata) if appdata else Path.home()) / APP_NAME
    return Path.home() / '.local' / 'share' / 'gotobed'


class Config:
    """Manages application configuration and statistics."""

    DEFAULT_CONFIG = {
        'bedtime': '21:40',
        'weekdays': [1, 2, 3, 4, 5],  # Monday to Friday (1=Mon, 7=Sun)
        'enabled': True,
        'snooze_minutes': 10,
        'pre_warning_minutes': 15,
        'autostart': True,
        'sound_enabled': True,
        'auto_update': True
    }

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize config manager with default values."""
        self.data_dir = Path(data_dir) if data_dir else default_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / 'config.json'
        self.stats_file = self.data_dir / 'stats.json'
        self.log_file = self.data_dir / 'gotobed.log'

        self.is_first_run = not self.config_file.exists()
        self.config = self._load_config()
        self.stats = self._load_stats()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        config = dict(self.DEFAULT_CONFIG)
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    config.update({k: v for k, v in loaded.items() if k in config})
        except Exception as e:
            log.warning("Error loading config: %s", e)
        return self._validate(config)

    @classmethod
    def _validate(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Fix up invalid values so the rest of the app can rely on them."""
        defaults = cls.DEFAULT_CONFIG
        try:
            hours, minutes = map(int, str(config['bedtime']).split(':'))
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError
            config['bedtime'] = f'{hours:02d}:{minutes:02d}'
        except ValueError:
            config['bedtime'] = defaults['bedtime']

        weekdays = config.get('weekdays')
        if not isinstance(weekdays, list):
            weekdays = defaults['weekdays']
        config['weekdays'] = sorted({int(d) for d in weekdays if str(d).isdigit() and 1 <= int(d) <= 7})

        for key, low, high in (('snooze_minutes', 1, 120), ('pre_warning_minutes', 0, 120)):
            try:
                config[key] = min(max(int(config[key]), low), high)
            except (TypeError, ValueError):
                config[key] = defaults[key]

        for key in ('enabled', 'autostart', 'sound_enabled', 'auto_update'):
            config[key] = bool(config[key])
        return config

    def _write_json(self, path: Path, data: Any) -> None:
        """Write JSON atomically so a crash never leaves a half-written file."""
        tmp = path.with_suffix(path.suffix + '.tmp')
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)

    def save(self, new_config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file."""
        try:
            if new_config:
                self.config = self._validate({**self.config, **new_config})
            self._write_json(self.config_file, self.config)
            log.info("Config saved to %s", self.config_file)
            return True
        except Exception as e:
            log.error("Error saving config: %s", e)
            return False

    def get(self, key: str, default=None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return dict(self.config)

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        stats = {
            'total_reminders': 0,
            'snoozed': 0,
            'dismissed': 0,
            'history': []
        }
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    stats.update(loaded)
        except Exception as e:
            log.warning("Error loading stats: %s", e)
        return stats

    def _save_stats(self) -> bool:
        """Save statistics to file."""
        try:
            self._write_json(self.stats_file, self.stats)
            return True
        except Exception as e:
            log.error("Error saving stats: %s", e)
            return False

    def add_stat_entry(self, action: str) -> None:
        """Add a statistics entry ('showed', 'snoozed' or 'dismissed')."""
        if action == 'showed':
            self.stats['total_reminders'] += 1
        elif action == 'snoozed':
            self.stats['snoozed'] += 1
        elif action == 'dismissed':
            self.stats['dismissed'] += 1

        now = datetime.now()
        self.stats['history'].append({
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'action': action
        })

        # Keep only last 100 entries
        self.stats['history'] = self.stats['history'][-100:]

        self._save_stats()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        return {**self.stats, 'history': list(self.stats['history'])}
