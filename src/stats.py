"""Statistics window for Go-to-Bed app."""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from datetime import datetime


class StatsWindow:
    """Statistics display window."""
    
    def __init__(self, stats_data: Dict[str, Any]):
        """Initialize statistics window.
        
        Args:
            stats_data: Statistics data
        """
        self.stats = stats_data
        self.window = None
    
    def show(self):
        """Show the statistics window."""
        if self.window and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Tk()
        self.window.title('Go-to-Bed - Statistics')
        self.window.geometry('600x500')
        self.window.resizable(False, False)
        
        # Main container
        container = ttk.Frame(self.window, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(container, text='📊 Your Bedtime Statistics', font=('Arial', 18, 'bold'))
        title.pack(pady=(0, 20))
        
        # Summary frame
        summary_frame = ttk.LabelFrame(container, text='Summary', padding=15)
        summary_frame.pack(fill=tk.X, pady=(0, 15))
        
        total = self.stats.get('total_reminders', 0)
        snoozed = self.stats.get('snoozed', 0)
        dismissed = self.stats.get('dismissed', 0)
        
        compliance_rate = (dismissed / total * 100) if total > 0 else 0
        
        stats_text = f"""
Total reminders: {total}
Times snoozed: {snoozed}
Times followed: {dismissed}
Compliance rate: {compliance_rate:.1f}%
        """.strip()
        
        stats_label = ttk.Label(
            summary_frame,
            text=stats_text,
            font=('Courier', 11),
            justify=tk.LEFT
        )
        stats_label.pack(anchor=tk.W)
        
        # History frame
        history_frame = ttk.LabelFrame(container, text='Recent Activity', padding=15)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create treeview for history
        columns = ('Date', 'Time', 'Action')
        tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=12)
        
        tree.heading('Date', text='Date')
        tree.heading('Time', text='Time')
        tree.heading('Action', text='Action')
        
        tree.column('Date', width=120)
        tree.column('Time', width=100)
        tree.column('Action', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Add history entries (most recent first)
        history = self.stats.get('history', [])
        for entry in reversed(history[-50:]):  # Show last 50
            action_text = entry['action'].capitalize()
            if entry['action'] == 'dismissed':
                action_text = '✓ Went to bed'
            elif entry['action'] == 'snoozed':
                action_text = '⏰ Snoozed'
            
            tree.insert('', 0, values=(entry['date'], entry['time'], action_text))
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = ttk.Button(
            container,
            text='Close',
            command=self.window.destroy
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f'+{x}+{y}')
        
        self.window.mainloop()
