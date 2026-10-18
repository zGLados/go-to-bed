"""Reminder window for Go-to-Bed app."""
import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageTk

from config import resource_path
from ui import center_window, set_window_icon, FONT

log = logging.getLogger(__name__)


class ReminderWindow:
    """Bedtime reminder window. Must be created on the Tk thread."""

    IMAGE_SIZE = (300, 200)
    GOOD_NIGHT_MS = 3000  # how long "Good night!" stays before the window closes

    def __init__(self, master: tk.Tk, snooze_minutes: int, on_snooze: Callable, on_dismiss: Callable,
                 is_prewarning: bool = False, minutes_left: int = 0):
        """Initialize reminder window.

        Args:
            master: Hidden Tk root
            snooze_minutes: Minutes for snooze
            on_snooze: Callback when user snoozes
            on_dismiss: Callback when user dismisses
            is_prewarning: Whether this is a pre-warning
            minutes_left: Minutes until bedtime (pre-warning only)
        """
        self.snooze_minutes = snooze_minutes
        self.on_snooze = on_snooze
        self.on_dismiss = on_dismiss
        self.is_prewarning = is_prewarning
        self.minutes_left = minutes_left
        self._photo = None
        self._text_widgets = []
        self.window = tk.Toplevel(master)
        self._build()

    def exists(self) -> bool:
        """Return whether the window is still open."""
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def close(self):
        """Close the window without triggering a callback."""
        if self.exists():
            self.window.destroy()

    def _load_image(self):
        """Load the sleeping horse picture, or None if unavailable."""
        try:
            image = Image.open(resource_path('assets', 'horse-sleeping-on-grass.png'))
            image.thumbnail(self.IMAGE_SIZE)
            return ImageTk.PhotoImage(image, master=self.window)
        except Exception as e:
            log.warning("Could not load reminder image: %s", e)
            return None

    def _build(self):
        """Create the widgets."""
        self.window.title('Bedtime Reminder')
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        set_window_icon(self.window)

        container = ttk.Frame(self.window, padding=25)
        container.pack(fill=tk.BOTH, expand=True)

        if self.is_prewarning:
            message = f'Bedtime in {self.minutes_left} minutes!'
            submessage = 'Time to start winding down.'
        else:
            message = 'Time to go to bed! 😴'
            submessage = 'Get some rest for tomorrow.'

        self._photo = self._load_image()
        if self._photo:
            ttk.Label(container, image=self._photo).pack(pady=(0, 15))

        self._container = container
        self._show_text(message, submessage)

        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X)
        self._text_widgets.append(button_frame)

        if not self.is_prewarning:
            ttk.Button(
                button_frame,
                text=f'Snooze ({self.snooze_minutes} min)',
                command=self._handle_snooze
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        dismiss_btn = ttk.Button(
            button_frame,
            text='OK' if self.is_prewarning else "Okay, I'm going!",
            command=self._handle_dismiss if self.is_prewarning else self._handle_going
        )
        dismiss_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.window.protocol('WM_DELETE_WINDOW', self._handle_dismiss)
        center_window(self.window)
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        dismiss_btn.focus_set()

    def _show_text(self, message: str, submessage: str):
        """Show the headline and the grey line below the picture."""
        for widget in self._text_widgets:
            widget.destroy()
        self._text_widgets = [
            ttk.Label(self._container, text=message, font=(FONT, 16, 'bold'), justify=tk.CENTER),
            ttk.Label(self._container, text=submessage, font=(FONT, 10), foreground='gray'),
        ]
        self._text_widgets[0].pack(pady=(0, 5))
        self._text_widgets[1].pack(pady=(0, 20))

    def _handle_going(self):
        """Handle "Okay, I'm going!": count it, say good night, then close."""
        self.on_dismiss()
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self._show_text('Good night! 🌙', 'Sleep well.')
        self.window.after(self.GOOD_NIGHT_MS, self.close)

    def _handle_snooze(self):
        """Handle snooze button click."""
        self.window.destroy()
        self.on_snooze()

    def _handle_dismiss(self):
        """Handle dismiss button click (or closing the window)."""
        self.window.destroy()
        self.on_dismiss()
