"""Shared Tk helpers for Go-to-Bed windows."""
import sys
import tkinter as tk

from config import resource_path

FONT = 'Segoe UI' if sys.platform == 'win32' else 'TkDefaultFont'


def center_window(window: tk.Misc) -> None:
    """Center a window on the screen."""
    window.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 3
    window.geometry(f'+{max(x, 0)}+{max(y, 0)}')


def set_window_icon(window: tk.Misc) -> None:
    """Use the app icon for a window (taskbar + title bar)."""
    icon = resource_path('assets', 'icon.ico')
    if sys.platform == 'win32' and icon.exists():
        try:
            window.iconbitmap(default=str(icon))
        except tk.TclError:
            pass
