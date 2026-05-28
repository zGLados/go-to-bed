"""Reminder window for Go-to-Bed app."""
import tkinter as tk
from tkinter import ttk
from typing import Callable
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False


class ReminderWindow:
    """Bedtime reminder window."""
    
    def __init__(self, snooze_minutes: int, on_snooze: Callable, on_dismiss: Callable, is_prewarning: bool = False):
        """Initialize reminder window.
        
        Args:
            snooze_minutes: Minutes for snooze
            on_snooze: Callback when user snoozes
            on_dismiss: Callback when user dismisses
            is_prewarning: Whether this is a pre-warning
        """
        self.snooze_minutes = snooze_minutes
        self.on_snooze = on_snooze
        self.on_dismiss = on_dismiss
        self.is_prewarning = is_prewarning
        self.window = None
    
    def show(self):
        """Show the reminder window."""
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Tk()
        self.window.title('Bedtime Reminder')
        self.window.geometry('450x250')
        self.window.resizable(False, False)
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        # Main container
        container = ttk.Frame(self.window, padding=30)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Icon and message
        if self.is_prewarning:
            icon_label = ttk.Label(container, text='⏰', font=('Arial', 48))
            message = f'Bedtime in {self.snooze_minutes} minutes!'
            submessage = 'Time to start winding down.'
        else:
            icon_label = ttk.Label(container, text='😴', font=('Arial', 48))
            message = 'Time to go to bed!'
            submessage = 'Get some rest for tomorrow.'
        
        icon_label.pack(pady=(0, 15))
        
        message_label = ttk.Label(
            container,
            text=message,
            font=('Arial', 18, 'bold'),
            justify=tk.CENTER
        )
        message_label.pack(pady=(0, 5))
        
        submessage_label = ttk.Label(
            container,
            text=submessage,
            font=('Arial', 11),
            foreground='gray'
        )
        submessage_label.pack(pady=(0, 25))
        
        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X)
        
        if not self.is_prewarning:
            snooze_btn = ttk.Button(
                button_frame,
                text=f'Snooze ({self.snooze_minutes} min)',
                command=self._handle_snooze
            )
            snooze_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        dismiss_text = 'OK' if self.is_prewarning else "Okay, I'm going!"
        dismiss_btn = ttk.Button(
            button_frame,
            text=dismiss_text,
            command=self._handle_dismiss
        )
        dismiss_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f'+{x}+{y}')
        
        # Flash taskbar to get attention
        self.window.after(100, lambda: self.window.attributes('-topmost', False))
        self.window.after(200, lambda: self.window.attributes('-topmost', True))
        
        self.window.protocol('WM_DELETE_WINDOW', self._handle_dismiss)
        self.window.mainloop()
    
    def _handle_snooze(self):
        """Handle snooze button click."""
        self.window.destroy()
        self.on_snooze()
    
    def _handle_dismiss(self):
        """Handle dismiss button click."""
        self.window.destroy()
        self.on_dismiss()
    
    @staticmethod
    def show_notification(title: str, message: str, timeout: int = 10):
        """Show a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            timeout: Timeout in seconds
        """
        if PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name='Go-to-Bed',
                    timeout=timeout
                )
            except Exception as e:
                print(f"Error showing notification: {e}")
