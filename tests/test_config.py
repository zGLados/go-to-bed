"""Tests for the configuration manager."""
import json

from config import Config


def test_defaults_and_first_run(tmp_path):
    cfg = Config(tmp_path)
    assert cfg.is_first_run
    assert cfg.get('bedtime') == '21:40'
    assert cfg.save()
    assert not Config(tmp_path).is_first_run


def test_save_and_reload(tmp_path):
    Config(tmp_path).save({'bedtime': '23:30', 'weekdays': [6, 7], 'snooze_minutes': 5})
    cfg = Config(tmp_path)
    assert cfg.get('bedtime') == '23:30'
    assert cfg.get('weekdays') == [6, 7]
    assert cfg.get('snooze_minutes') == 5


def test_invalid_values_are_repaired(tmp_path):
    (tmp_path / 'config.json').write_text(json.dumps({
        'bedtime': '25:99', 'weekdays': [0, 3, 9], 'snooze_minutes': 'x', 'pre_warning_minutes': -5
    }))
    cfg = Config(tmp_path)
    assert cfg.get('bedtime') == '21:40'
    assert cfg.get('weekdays') == [3]
    assert cfg.get('snooze_minutes') == 10
    assert cfg.get('pre_warning_minutes') == 0


def test_corrupt_file_falls_back_to_defaults(tmp_path):
    (tmp_path / 'config.json').write_text('{not json')
    (tmp_path / 'stats.json').write_text('{not json')
    cfg = Config(tmp_path)
    assert cfg.get('bedtime') == '21:40'
    assert cfg.get_stats()['total_reminders'] == 0


def test_stats_counting(tmp_path):
    cfg = Config(tmp_path)
    for action in ['showed', 'snoozed', 'showed', 'dismissed']:
        cfg.add_stat_entry(action)
    stats = Config(tmp_path).get_stats()
    assert (stats['total_reminders'], stats['snoozed'], stats['dismissed']) == (2, 1, 1)
    assert len(stats['history']) == 4
