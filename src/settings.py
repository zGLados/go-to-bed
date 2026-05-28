"""Settings window for Go-to-Bed app."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any


class SettingsWindow:
    """Settings GUI window."""
    
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    def __init__(self, config_data: Dict[str, Any], on_save: Callable):
        """Initialize settings window.
        
        Args:
            config_data: Current configuration
            on_save: Callback function to save config
        """
        self.config = config_data
        self.on_save = on_save
        self.window = None
        
    def show(self):
        """Show the settings window."""
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Tk()
        self.window.title('Go-to-Bed - Settings')
        self.window.geometry('500x600')
        self.window.resizable(False, False)
        
        # Main container
        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(container, text='🌙 Bedtime Settings', font=('Arial', 18, 'bold'))
        title.pack(pady=(0, 20))
        
        # Enabled checkbox
        self.enabled_var = tk.BooleanVar(value=self.config.get('enabled', True))
        enabled_check = ttk.Checkbutton(
            container, 
            text='Enable bedtime reminders',
            variable=self.enabled_var,
            command=self._on_enabled_change
        )
        enabled_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Bedtime section
        bedtime_frame = ttk.LabelFrame(container, text='Bedtime', padding=15)
        bedtime_frame.pack(fill=tk.X, pady=(0, 15))
        
        time_frame = ttk.Frame(bedtime_frame)
        time_frame.pack(fill=tk.X)
        
        ttk.Label(time_frame, text='Time:').pack(side=tk.LEFT)
        
        # Parse current bedtime
        current_time = self.config.get('bedtime', '22:00').split(':')
        
        self.hour_var = tk.StringVar(value=current_time[0])
        hour_spin = ttk.Spinbox(
            time_frame, from_=0, to=23, width=5,
            textvariable=self.hour_var, format='%02.0f'
        )
        hour_spin.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(time_frame, text=':').pack(side=tk.LEFT)
        
        self.minute_var = tk.StringVar(value=current_time[1])
        minute_spin = ttk.Spinbox(
            time_frame, from_=0, to=59, width=5,
            textvariable=self.minute_var, format='%02.0f'
        )
        minute_spin.pack(side=tk.LEFT, padx=5)
        
        # Pre-warning
        prewarning_frame = ttk.Frame(bedtime_frame)
        prewarning_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(prewarning_frame, text='Pre-warning:').pack(side=tk.LEFT)
        
        self.prewarning_var = tk.IntVar(value=self.config.get('pre_warning_minutes', 15))
        prewarning_spin = ttk.Spinbox(
            prewarning_frame, from_=0, to=60, width=5,
            textvariable=self.prewarning_var
        )
        prewarning_spin.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(prewarning_frame, text='minutes before').pack(side=tk.LEFT)
        
        # Weekdays section
        weekday_frame = ttk.LabelFrame(container, text='Active Days', padding=15)
        weekday_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.weekday_vars = []
        active_days = self.config.get('weekdays', [1, 2, 3, 4, 5])
        
        for i, day in enumerate(self.WEEKDAYS, start=1):
            var = tk.BooleanVar(value=i in active_days)
            self.weekday_vars.append((i, var))
            check = ttk.Checkbutton(weekday_frame, text=day, variable=var)
            check.pack(anchor=tk.W)
        
        # Snooze section
        snooze_frame = ttk.LabelFrame(container, text='Snooze', padding=15)
        snooze_frame.pack(fill=tk.X, pady=(0, 15))
        
        snooze_inner = ttk.Frame(snooze_frame)
        snooze_inner.pack(fill=tk.X)
        
        ttk.Label(snooze_inner, text='Snooze duration:').pack(side=tk.LEFT)
        
        self.snooze_var = tk.IntVar(value=self.config.get('snooze_minutes', 10))
        snooze_spin = ttk.Spinbox(
            snooze_inner, from_=1, to=60, width=5,
            textvariable=self.snooze_var
        )
        snooze_spin.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(snooze_inner, text='minutes').pack(side=tk.LEFT)
        
        # Additional options
        options_frame = ttk.LabelFrame(container, text='Options', padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.autostart_var = tk.BooleanVar(value=self.config.get('autostart', True))
        autostart_check = ttk.Checkbutton(
            options_frame,
            text='Start with system',
            variable=self.autostart_var
        )
        autostart_check.pack(anchor=tk.W)
        
        self.sound_var = tk.BooleanVar(value=self.config.get('sound_enabled', True))
        sound_check = ttk.Checkbutton(
            options_frame,
            text='Play notification sound',
            variable=self.sound_var
        )
        sound_check.pack(anchor=tk.W)
        
        # Save button
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_btn = ttk.Button(
            button_frame,
            text='Save Settings',
            command=self._save_settings
        )
        save_btn.pack(side=tk.RIGHT)
        
        cancel_btn = ttk.Button(
            button_frame,
            text='Cancel',
            command=self.window.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f'+{x}+{y}')
        
        self.window.mainloop()
    
    def _on_enabled_change(self):
        """Handle enabled checkbox change."""
        pass  # Can add visual feedback if needed
    
    def _save_settings(self):
        """Save settings and close window."""
        try:
            # Collect weekdays
            weekdays = [day for day, var in self.weekday_vars if var.get()]
            
            if not weekdays:
                messagebox.showwarning('Invalid Settings', 'Please select at least one active day.')
                return
            
            # Build config
            new_config = {
                'bedtime': f'{int(self.hour_var.get()):02d}:{int(self.minute_var.get()):02d}',
                'weekdays': weekdays,
                'enabled': self.enabled_var.get(),
                'snooze_minutes': self.snooze_var.get(),
                'pre_warning_minutes': self.prewarning_var.get(),
                'autostart': self.autostart_var.get(),
                'sound_enabled': self.sound_var.get()
            }
            
            # Call save callback
            if self.on_save(new_config):
                messagebox.showinfo('Success', 'Settings saved successfully!')
                self.window.destroy()
            else:
                messagebox.showerror('Error', 'Failed to save settings.')
        except Exception as e:
            messagebox.showerror('Error', f'Error saving settings: {e}')
