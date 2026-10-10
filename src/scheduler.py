"""Bedtime scheduler for Go-to-Bed app."""
import logging
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional

log = logging.getLogger(__name__)


class BedtimeScheduler:
    """Checks periodically whether a pre-warning or the bedtime reminder is due.

    The configuration is read on every check, so settings changes take effect
    without restarting the scheduler. A reminder that was missed by up to
    GRACE (e.g. because the PC was asleep) is still shown, but each reminder
    fires at most once per night.
    """

    CHECK_INTERVAL = 10  # seconds
    GRACE = timedelta(minutes=5)

    def __init__(self, config, on_bedtime: Callable, on_prewarning: Optional[Callable] = None):
        """Initialize scheduler.

        Args:
            config: Configuration manager
            on_bedtime: Callback when bedtime is reached
            on_prewarning: Optional callback for pre-warning
        """
        self.config = config
        self.on_bedtime = on_bedtime
        self.on_prewarning = on_prewarning
        self._fired = set()
        self._stop_event = threading.Event()
        self.thread = None

    def start(self):
        """Start the scheduler."""
        if self.thread and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, name='scheduler', daemon=True)
        self.thread.start()
        log.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
        log.info("Scheduler stopped")

    def _run_loop(self):
        """Main scheduler loop."""
        while not self._stop_event.is_set():
            try:
                self.check()
            except Exception:
                log.exception("Error in scheduler")
            self._stop_event.wait(self.CHECK_INTERVAL)

    def check(self, now: Optional[datetime] = None):
        """Fire due reminders. `now` can be passed in for testing."""
        if not self.config.get('enabled'):
            return
        now = now or datetime.now()

        hours, minutes = map(int, self.config.get('bedtime').split(':'))
        active_days = self.config.get('weekdays', [])
        pre_warning = int(self.config.get('pre_warning_minutes', 0))

        events = [('bedtime', 0, self.on_bedtime)]
        if pre_warning > 0 and self.on_prewarning:
            events.insert(0, ('prewarning', pre_warning, self.on_prewarning))

        # Look at today's and tomorrow's bedtime, so a pre-warning before a
        # bedtime shortly after midnight is handled correctly.
        today = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        for bedtime in (today, today + timedelta(days=1)):
            if bedtime.isoweekday() not in active_days:
                continue
            for name, minutes_before, callback in events:
                due = bedtime - timedelta(minutes=minutes_before)
                # A pre-warning is pointless once bedtime has arrived
                end = min(due + self.GRACE, bedtime) if minutes_before else due + self.GRACE
                key = (name, bedtime.date())
                if due <= now < end and key not in self._fired:
                    self._fired.add(key)
                    log.info("%s due (bedtime %s)", name, bedtime)
                    callback()

        # Forget old entries
        cutoff = now.date() - timedelta(days=2)
        self._fired = {k for k in self._fired if k[1] >= cutoff}
