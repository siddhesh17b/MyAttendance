"""
MyAttendance - Smart Attendance Tracker
Main application entry point

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk

from data_manager import load_data, save_data, get_app_data, parse_timetable_csv
from setup_tab import SetupTab
from timetable_tab import TimetableTab
from attendance_calendar import AttendanceCalendar
from summary_tab import SummaryTab

# Color scheme
COLOR_INFO = "#007bff"
COLOR_BG_LIGHT = "#f8f9fa"


class BunkBuddyApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MyAttendance - Smart Attendance Tracker")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLOR_BG_LIGHT)
        
        # Load data
        app_data = get_app_data()
        if not load_data() or not app_data.get("batch"):
            self.show_first_time_setup()
        
        # Create main UI
        self.create_ui()
        self.refresh_all_tabs()
    
    def show_first_time_setup(self):
        """Show setup wizard for first-time users"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Welcome to MyAttendance!")
        setup_window.geometry("400x200")
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        tk.Label(setup_window, text="Welcome to MyAttendance!", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(setup_window, text="Please select your batch:", font=("Arial", 11)).pack(pady=5)
        
        batch_var = tk.StringVar(value="B1/B3")
        ttk.Radiobutton(setup_window, text="B1/B3", variable=batch_var, value="B1/B3").pack()
        ttk.Radiobutton(setup_window, text="B2/B4", variable=batch_var, value="B2/B4").pack()
        
        def save_and_close():
            app_data = get_app_data()
            app_data["batch"] = batch_var.get()
            # Initialize subjects from timetable
            weekly_counts = parse_timetable_csv(app_data["batch"])
            app_data["subjects"] = [
                {
                    "name": subject,
                    "weekly_count": count,
                    "total_override": None,
                    "absent_dates": []  # All classes present by default
                }
                for subject, count in weekly_counts.items()
            ]
            save_data()
            setup_window.destroy()
        
        ttk.Button(setup_window, text="Continue", command=save_and_close).pack(pady=20)
        
        self.root.wait_window(setup_window)
    
    def create_ui(self):
        """Create main tabbed interface"""
        # Title
        title_frame = tk.Frame(self.root, bg=COLOR_INFO, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🎓 MyAttendance - Smart Attendance Tracker",
            font=("Arial", 16, "bold"),
            bg=COLOR_INFO,
            fg="white"
        ).pack(pady=15)
        
        # Tab control
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = SetupTab(self.notebook, self.refresh_all_tabs)
        self.notebook.add(self.setup_tab.create(), text="⚙️ Setup")
        
        self.timetable_tab = TimetableTab(self.notebook, self.refresh_all_tabs)
        self.notebook.add(self.timetable_tab.create(), text="📋 Timetable")
        
        self.attendance_calendar = AttendanceCalendar(self.notebook, self.refresh_all_tabs)
        self.notebook.add(self.attendance_calendar.create(), text="📅 Mark Attendance")
        
        self.summary_tab = SummaryTab(self.notebook, self.refresh_all_tabs)
        self.notebook.add(self.summary_tab.create(), text="📊 Summary")
    
    def refresh_all_tabs(self):
        """Refresh all tab displays"""
        if hasattr(self, 'setup_tab'):
            self.setup_tab.refresh()
        if hasattr(self, 'timetable_tab'):
            self.timetable_tab.refresh()
        if hasattr(self, 'attendance_calendar'):
            self.attendance_calendar.refresh()
        if hasattr(self, 'summary_tab'):
            self.summary_tab.refresh()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BunkBuddyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
