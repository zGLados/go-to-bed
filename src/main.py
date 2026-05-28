"""Main entry point for Go-to-Bed app."""
import sys
import os
import threading
import time
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from config import Config
from settings import SettingsWindow
from reminder import ReminderWindow
from stats import StatsWindow
from scheduler import BedtimeScheduler


class GotoBedApp:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.tray_icon = None
        self.scheduler = None
        self.snooze_timer = None
        
        # Set up autostart on Windows
        if sys.platform == 'win32':
            self._setup_autostart()
    
    def _setup_autostart(self):
        """Set up Windows autostart."""
        try:
            import winreg
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            app_name = 'GotoBed'
            
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            
            if self.config.get('autostart', True):
                # Add to startup
                exe_path = sys.executable
                if getattr(sys, 'frozen', False):
                    # Running as compiled executable
                    exe_path = sys.executable
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                print(f"✓ Autostart enabled: {exe_path}")
            else:
                # Remove from startup
                try:
                    winreg.DeleteValue(key, app_name)
                    print("✓ Autostart disabled")
                except FileNotFoundError:
                    pass
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error setting up autostart: {e}")
    
    def _create_icon_image(self):
        """Create a system tray icon."""
        # Try to load existing icon from assets
        icon_path = Path(__file__).parent.parent / 'assets' / 'tray-icon.png'
        
        if icon_path.exists():
            try:
                image = Image.open(icon_path)
                print(f"✓ Loaded tray icon from {icon_path}")
                return image
            except Exception as e:
                print(f"Warning: Could not load icon from {icon_path}: {e}")
        
        # Fallback: Create a simple moon icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), 'black')
        draw = ImageDraw.Draw(image)
        
        # Draw a crescent moon
        draw.ellipse([8, 8, 56, 56], fill='white')
        draw.ellipse([16, 8, 64, 56], fill='black')
        
        print("✓ Using generated moon icon")
        return image
    
    def _create_menu(self):
        """Create the system tray menu."""
        bedtime = self.config.get('bedtime')
        enabled = self.config.get('enabled')
        
        status_text = f"{'✓ Enabled' if enabled else '✗ Disabled'}"
        
        return pystray.Menu(
            item(f'Bedtime: {bedtime}', lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item(status_text, self._toggle_enabled, checked=lambda _: enabled),
            pystray.Menu.SEPARATOR,
            item('Settings', self._open_settings),
            item('Statistics', self._open_stats),
            pystray.Menu.SEPARATOR,
            item('Test Reminder', self._test_reminder),
            item('Show Data Folder', self._open_data_folder),
            pystray.Menu.SEPARATOR,
            item('Quit', self._quit_app)
        )
    
    def _toggle_enabled(self, icon, item):
        """Toggle reminders on/off."""
        new_state = not self.config.get('enabled')
        self.config.save({'enabled': new_state})
        
        if new_state:
            self._start_scheduler()
        else:
            self._stop_scheduler()
        
        # Update menu
        icon.menu = self._create_menu()
        print(f"✓ Reminders {'enabled' if new_state else 'disabled'}")
    
    def _open_settings(self):
        """Open settings window."""
        def save_callback(new_config):
            success = self.config.save(new_config)
            if success:
                # Update autostart
                if sys.platform == 'win32':
                    self._setup_autostart()
                
                # Restart scheduler
                self._stop_scheduler()
                if self.config.get('enabled'):
                    self._start_scheduler()
                
                # Update tray menu
                self.tray_icon.menu = self._create_menu()
            return success
        
        threading.Thread(
            target=lambda: SettingsWindow(self.config.get_all(), save_callback).show(),
            daemon=True
        ).start()
    
    def _open_stats(self):
        """Open statistics window."""
        threading.Thread(
            target=lambda: StatsWindow(self.config.get_stats()).show(),
            daemon=True
        ).start()
    
    def _test_reminder(self):
        """Test the reminder."""
        self._show_bedtime_reminder()
    
    def _open_data_folder(self):
        """Open the data folder."""
        import subprocess
        path = str(self.config.data_dir)
        
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    
    def _quit_app(self):
        """Quit the application."""
        print("Quitting Go-to-Bed...")
        self._stop_scheduler()
        if self.tray_icon:
            self.tray_icon.stop()
    
    def _start_scheduler(self):
        """Start the bedtime scheduler."""
        if self.scheduler:
            self.scheduler.stop()
        
        self.scheduler = BedtimeScheduler(
            self.config,
            on_bedtime=self._show_bedtime_reminder,
            on_prewarning=self._show_prewarning_reminder
        )
        self.scheduler.start()
    
    def _stop_scheduler(self):
        """Stop the bedtime scheduler."""
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler = None
    
    def _show_prewarning_reminder(self):
        """Show pre-warning reminder."""
        pre_warning_minutes = self.config.get('pre_warning_minutes', 15)
        
        # Show notification
        ReminderWindow.show_notification(
            'Bedtime Soon',
            f'Your bedtime is in {pre_warning_minutes} minutes. Time to wind down!'
        )
        
        # Show window
        def show():
            ReminderWindow(
                snooze_minutes=pre_warning_minutes,
                on_snooze=lambda: None,
                on_dismiss=lambda: None,
                is_prewarning=True
            ).show()
        
        threading.Thread(target=show, daemon=True).start()
    
    def _show_bedtime_reminder(self):
        """Show bedtime reminder."""
        snooze_minutes = self.config.get('snooze_minutes', 10)
        
        # Show notification
        ReminderWindow.show_notification(
            'Time to Go to Bed!',
            'Sweet dreams! 😴'
        )
        
        # Add stat
        self.config.add_stat_entry('showed')
        
        def show():
            ReminderWindow(
                snooze_minutes=snooze_minutes,
                on_snooze=self._handle_snooze,
                on_dismiss=self._handle_dismiss,
                is_prewarning=False
            ).show()
        
        threading.Thread(target=show, daemon=True).start()
    
    def _handle_snooze(self):
        """Handle snooze action."""
        snooze_minutes = self.config.get('snooze_minutes', 10)
        print(f"💤 Snoozed for {snooze_minutes} minutes")
        
        self.config.add_stat_entry('snoozed')
        
        # Cancel existing snooze timer
        if self.snooze_timer:
            self.snooze_timer.cancel()
        
        # Set new snooze timer
        self.snooze_timer = threading.Timer(
            snooze_minutes * 60,
            self._show_bedtime_reminder
        )
        self.snooze_timer.daemon = True
        self.snooze_timer.start()
    
    def _handle_dismiss(self):
        """Handle dismiss action."""
        print("✓ User went to bed")
        self.config.add_stat_entry('dismissed')
    
    def run(self):
        """Run the application."""
        print("=" * 50)
        print("🌙 Go-to-Bed v3.0 (Python Edition)")
        print("=" * 50)
        print(f"Config: {self.config.config_file}")
        print(f"Stats: {self.config.stats_file}")
        print("=" * 50)
        
        # Start scheduler if enabled
        if self.config.get('enabled'):
            self._start_scheduler()
        
        # Show settings on first run
        if self.config.is_first_run:
            print("First run detected - opening settings...")
            threading.Thread(
                target=lambda: SettingsWindow(
                    self.config.get_all(),
                    lambda cfg: self.config.save(cfg)
                ).show(),
                daemon=True
            ).start()
        
        # Create and run system tray icon
        icon_image = self._create_icon_image()
        self.tray_icon = pystray.Icon(
            'GotoBed',
            icon_image,
            'Go-to-Bed',
            menu=self._create_menu()
        )
        
        print("✓ System tray icon created")
        print("✓ App running in background")
        print("=" * 50)
        
        # Run (blocks until quit)
        self.tray_icon.run()


def main():
    """Main entry point."""
    app = GotoBedApp()
    app.run()


if __name__ == '__main__':
    main()
