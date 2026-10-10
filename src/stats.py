"""Statistics window for Go-to-Bed app."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from ui import center_window, set_window_icon, FONT


class StatsWindow:
    """Statistics display window. Must be created on the Tk thread."""

    ACTION_LABELS = {
        'showed': '🔔 Reminder shown',
        'dismissed': '✓ Went to bed',
        'snoozed': '⏰ Snoozed',
    }

    def __init__(self, master: tk.Tk, stats_data: Dict[str, Any]):
        """Initialize statistics window.

        Args:
            master: Hidden Tk root
            stats_data: Statistics data
        """
        self.stats = stats_data
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
        self.window.title('Go-to-Bed - Statistics')
        set_window_icon(self.window)

        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text='📊 Your Bedtime Statistics', font=(FONT, 16, 'bold')).pack(pady=(0, 15))

        summary_frame = ttk.LabelFrame(container, text='Summary', padding=12)
        summary_frame.pack(fill=tk.X, pady=(0, 10))

        total = self.stats.get('total_reminders', 0)
        snoozed = self.stats.get('snoozed', 0)
        dismissed = self.stats.get('dismissed', 0)
        compliance_rate = (dismissed / total * 100) if total > 0 else 0

        rows = [
            ('Reminders shown:', total),
            ('Times snoozed:', snoozed),
            ('Times followed:', dismissed),
            ('Compliance rate:', f'{compliance_rate:.1f}%'),
        ]
        for row, (label, value) in enumerate(rows):
            ttk.Label(summary_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=(0, 20))
            ttk.Label(summary_frame, text=str(value), font=(FONT, 10, 'bold')).grid(row=row, column=1, sticky=tk.W)

        history_frame = ttk.LabelFrame(container, text='Recent Activity', padding=12)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('Date', 'Time', 'Action')
        tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=12)
        for column, width in zip(columns, (110, 90, 180)):
            tree.heading(column, text=column)
            tree.column(column, width=width)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Most recent first
        for entry in reversed(self.stats.get('history', [])[-50:]):
            action = entry.get('action', '')
            tree.insert('', tk.END, values=(
                entry.get('date', ''),
                entry.get('time', ''),
                self.ACTION_LABELS.get(action, action.capitalize())
            ))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(container, text='Close', command=self.window.destroy).pack(side=tk.RIGHT)
        self.window.bind('<Escape>', lambda _: self.window.destroy())

        center_window(self.window)
        self.focus()
