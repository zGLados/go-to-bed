"""Settings window for Go-to-Bed app."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from ui import center_window, set_window_icon, FONT


class SettingsWindow:
    """Settings GUI window. Must be created on the Tk thread."""

    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def __init__(self, master: tk.Tk, config_data: Dict[str, Any], on_save: Callable[[Dict[str, Any]], bool]):
        """Initialize settings window.

        Args:
            master: Hidden Tk root
            config_data: Current configuration
            on_save: Callback function to save config, returns success
        """
        self.config = config_data
        self.on_save = on_save
        self.window = tk.Toplevel(master)
        self._build()

    def exists(self) -> bool:
        """Return whether the window is still open."""
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def focus(self):
        """Bring the window to the front."""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def _build(self):
        """Create the widgets."""
        self.window.title('Go-to-Bed - Settings')
        self.window.resizable(False, False)
        set_window_icon(self.window)

        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text='🌙 Bedtime Settings', font=(FONT, 16, 'bold')).pack(pady=(0, 15))

        self.enabled_var = tk.BooleanVar(value=self.config.get('enabled', True))
        ttk.Checkbutton(
            container,
            text='Enable bedtime reminders',
            variable=self.enabled_var
        ).pack(anchor=tk.W, pady=(0, 10))

        # Bedtime section
        bedtime_frame = ttk.LabelFrame(container, text='Bedtime', padding=12)
        bedtime_frame.pack(fill=tk.X, pady=(0, 10))

        time_frame = ttk.Frame(bedtime_frame)
        time_frame.pack(fill=tk.X)
        ttk.Label(time_frame, text='Time:').pack(side=tk.LEFT)

        hours, minutes = self.config.get('bedtime', '22:00').split(':')
        self.hour_var = tk.StringVar(value=hours)
        ttk.Spinbox(
            time_frame, from_=0, to=23, width=4, wrap=True,
            textvariable=self.hour_var, format='%02.0f'
        ).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(time_frame, text=':').pack(side=tk.LEFT)
        self.minute_var = tk.StringVar(value=minutes)
        ttk.Spinbox(
            time_frame, from_=0, to=59, width=4, wrap=True,
            textvariable=self.minute_var, format='%02.0f'
        ).pack(side=tk.LEFT, padx=5)

        prewarning_frame = ttk.Frame(bedtime_frame)
        prewarning_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(prewarning_frame, text='Pre-warning:').pack(side=tk.LEFT)
        self.prewarning_var = tk.StringVar(value=str(self.config.get('pre_warning_minutes', 15)))
        ttk.Spinbox(
            prewarning_frame, from_=0, to=120, width=4,
            textvariable=self.prewarning_var
        ).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(prewarning_frame, text='minutes before (0 = off)').pack(side=tk.LEFT)

        # Weekdays section
        weekday_frame = ttk.LabelFrame(container, text='Active Days', padding=12)
        weekday_frame.pack(fill=tk.X, pady=(0, 10))

        self.weekday_vars = []
        active_days = self.config.get('weekdays', [1, 2, 3, 4, 5])
        for i, day in enumerate(self.WEEKDAYS, start=1):
            var = tk.BooleanVar(value=i in active_days)
            self.weekday_vars.append((i, var))
            ttk.Checkbutton(weekday_frame, text=day, variable=var).grid(
                row=(i - 1) // 4, column=(i - 1) % 4, sticky=tk.W, padx=(0, 12)
            )

        # Snooze section
        snooze_frame = ttk.LabelFrame(container, text='Snooze', padding=12)
        snooze_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(snooze_frame, text='Snooze duration:').pack(side=tk.LEFT)
        self.snooze_var = tk.StringVar(value=str(self.config.get('snooze_minutes', 10)))
        ttk.Spinbox(
            snooze_frame, from_=1, to=120, width=4,
            textvariable=self.snooze_var
        ).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(snooze_frame, text='minutes').pack(side=tk.LEFT)

        # Additional options
        options_frame = ttk.LabelFrame(container, text='Options', padding=12)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        self.autostart_var = tk.BooleanVar(value=self.config.get('autostart', True))
        ttk.Checkbutton(
            options_frame,
            text='Start with Windows',
            variable=self.autostart_var
        ).pack(anchor=tk.W)

        self.sound_var = tk.BooleanVar(value=self.config.get('sound_enabled', True))
        ttk.Checkbutton(
            options_frame,
            text='Play notification sound',
            variable=self.sound_var
        ).pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text='Save Settings', command=self._save_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text='Cancel', command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 10))

        self.window.bind('<Return>', lambda _: self._save_settings())
        self.window.bind('<Escape>', lambda _: self.window.destroy())

        center_window(self.window)
        self.focus()

    def _int(self, var: tk.Variable, name: str, low: int, high: int) -> int:
        """Read an integer from a variable or raise ValueError with a friendly message."""
        try:
            value = int(str(var.get()).strip())
        except ValueError:
            raise ValueError(f'{name} must be a number.')
        if not low <= value <= high:
            raise ValueError(f'{name} must be between {low} and {high}.')
        return value

    def _save_settings(self):
        """Save settings and close window."""
        try:
            new_config = {
                'bedtime': '{:02d}:{:02d}'.format(
                    self._int(self.hour_var, 'Hour', 0, 23),
                    self._int(self.minute_var, 'Minute', 0, 59)
                ),
                'weekdays': [day for day, var in self.weekday_vars if var.get()],
                'enabled': self.enabled_var.get(),
                'snooze_minutes': self._int(self.snooze_var, 'Snooze duration', 1, 120),
                'pre_warning_minutes': self._int(self.prewarning_var, 'Pre-warning', 0, 120),
                'autostart': self.autostart_var.get(),
                'sound_enabled': self.sound_var.get()
            }
        except ValueError as e:
            messagebox.showwarning('Invalid Settings', str(e), parent=self.window)
            return

        if not new_config['weekdays']:
            messagebox.showwarning('Invalid Settings', 'Please select at least one active day.', parent=self.window)
            return

        if self.on_save(new_config):
            self.window.destroy()
        else:
            messagebox.showerror('Error', 'Failed to save settings.', parent=self.window)
