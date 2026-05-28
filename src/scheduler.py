"""Bedtime scheduler for Go-to-Bed app."""
import threading
import time
from datetime import datetime
from typing import Callable


class BedtimeScheduler:
    """Schedules and checks for bedtime."""
    
    def __init__(self, config, on_bedtime: Callable, on_prewarning: Callable = None):
        """Initialize scheduler.
        
        Args:
            config: Configuration manager
            on_bedtime: Callback when bedtime is reached
            on_prewarning: Optional callback for pre-warning
        """
        self.config = config
        self.on_bedtime = on_bedtime
        self.on_prewarning = on_prewarning
        self.running = False
        self.thread = None
        self._last_check_minute = None
        self._prewarning_shown = False
        self._bedtime_shown = False
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("✓ Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("✓ Scheduler stopped")
    
    def _run_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                self._check_time()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(60)
    
    def _check_time(self):
        """Check if it's time for a reminder."""
        if not self.config.get('enabled'):
            return
        
        now = datetime.now()
        current_minute = now.strftime('%H:%M')
        current_weekday = now.isoweekday()  # 1=Monday, 7=Sunday
        
        # Reset daily flags if we're past bedtime
        bedtime = self.config.get('bedtime')
        if current_minute < bedtime:
            self._prewarning_shown = False
            self._bedtime_shown = False
        
        # Only check once per minute
        if self._last_check_minute == current_minute:
            return
        
        self._last_check_minute = current_minute
        
        # Check if today is an active day
        active_days = self.config.get('weekdays', [])
        if current_weekday not in active_days:
            return
        
        # Check for pre-warning
        pre_warning_minutes = self.config.get('pre_warning_minutes', 0)
        if pre_warning_minutes > 0 and self.on_prewarning and not self._prewarning_shown:
            prewarning_time = self._subtract_minutes(bedtime, pre_warning_minutes)
            if current_minute == prewarning_time:
                print(f"⏰ Pre-warning time: {current_minute}")
                self._prewarning_shown = True
                self.on_prewarning()
                return
        
        # Check for bedtime
        if current_minute == bedtime and not self._bedtime_shown:
            print(f"😴 Bedtime: {current_minute}")
            self._bedtime_shown = True
            self.on_bedtime()
    
    @staticmethod
    def _subtract_minutes(time_str: str, minutes: int) -> str:
        """Subtract minutes from a time string.
        
        Args:
            time_str: Time in HH:MM format
            minutes: Minutes to subtract
            
        Returns:
            New time in HH:MM format
        """
        hours, mins = map(int, time_str.split(':'))
        total_minutes = hours * 60 + mins - minutes
        
        # Handle negative wraparound
        if total_minutes < 0:
            total_minutes += 24 * 60
        
        new_hours = (total_minutes // 60) % 24
        new_mins = total_minutes % 60
        
        return f'{new_hours:02d}:{new_mins:02d}'
