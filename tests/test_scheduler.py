"""Tests for the bedtime scheduler (no GUI needed)."""
from datetime import datetime

import pytest

from config import Config
from scheduler import BedtimeScheduler


@pytest.fixture
def config(tmp_path):
    cfg = Config(tmp_path)
    cfg.config.update({'bedtime': '22:00', 'weekdays': [1, 2, 3, 4, 5, 6, 7], 'pre_warning_minutes': 15})
    return cfg


@pytest.fixture
def events():
    return []


@pytest.fixture
def scheduler(config, events):
    return BedtimeScheduler(
        config,
        on_bedtime=lambda: events.append('bedtime'),
        on_prewarning=lambda: events.append('prewarning')
    )


def at(day, hhmm):
    """2026-10-05 is a Monday."""
    h, m = map(int, hhmm.split(':'))
    return datetime(2026, 10, 4 + day, h, m, 30)


def test_prewarning_and_bedtime_fire_once(scheduler, events):
    for t in ['21:40', '21:45', '21:45', '21:46', '21:59', '22:00', '22:00', '22:01', '22:30']:
        scheduler.check(at(1, t))
    assert events == ['prewarning', 'bedtime']


def test_fires_again_next_day(scheduler, events):
    scheduler.check(at(1, '22:00'))
    scheduler.check(at(2, '22:00'))
    assert events == ['bedtime', 'bedtime']


def test_missed_minute_within_grace_still_fires(scheduler, events):
    scheduler.check(at(1, '22:03'))
    assert events == ['bedtime']


def test_too_late_does_not_fire(scheduler, events):
    scheduler.check(at(1, '22:10'))
    assert events == []


def test_no_prewarning_after_bedtime(config, scheduler, events):
    config.config['pre_warning_minutes'] = 2
    scheduler.check(at(1, '22:01'))
    assert events == ['bedtime']


def test_inactive_weekday(config, scheduler, events):
    config.config['weekdays'] = [1, 2, 3, 4, 5]
    scheduler.check(at(6, '22:00'))  # Saturday
    assert events == []


def test_disabled(config, scheduler, events):
    config.config['enabled'] = False
    scheduler.check(at(1, '22:00'))
    assert events == []


def test_prewarning_before_midnight_for_bedtime_after_midnight(config, scheduler, events):
    config.config.update({'bedtime': '00:10', 'weekdays': [2]})  # Tuesday 00:10
    scheduler.check(at(1, '23:55'))  # Monday evening
    scheduler.check(at(2, '00:10'))
    assert events == ['prewarning', 'bedtime']


def test_prewarning_off(config, scheduler, events):
    config.config['pre_warning_minutes'] = 0
    scheduler.check(at(1, '21:45'))
    scheduler.check(at(1, '22:00'))
    assert events == ['bedtime']
