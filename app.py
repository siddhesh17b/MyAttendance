"""
Bunkmeter
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
        self.root.title("Bunkmeter")
        
        # Center the main window
        width = 1400
        height = 1000
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1200, 800)  # Minimum window size to prevent squishing
        self.root.configure(bg=COLOR_BG_LIGHT)
        
        # Optimize rendering
        self.root.update_idletasks()
        
        # Load data first, then check if setup is needed
        # Note: load_data() updates app_data in-place, so we must call it BEFORE get_app_data()
        data_loaded = load_data()
        app_data = get_app_data()  # Now get reference to the loaded data
        
        if not data_loaded or not app_data.get("batch"):
            self.show_first_time_setup()
        
        # Create main UI
        self.create_ui()
        # Initial tab will refresh on its own during creation
    
    def show_first_time_setup(self):
        """
        First-time setup wizard shown when app launches for the first time
        Allows users to:
        1. Import custom timetable CSV (optional)
        2. Select their batch/group
        
        Note: Batch names are auto-detected from timetable entries with format:
        "Subject (BatchA) / Subject (BatchB)"
        """
        # Create modal dialog window
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Welcome to Bunkmeter!")
        setup_window.geometry("500x350")
        setup_window.transient(self.root)  # Set as child of main window
        setup_window.grab_set()  # Make window modal (blocks interaction with parent)
        
        # Center the window on screen
        setup_window.update_idletasks()
        width = 500
        height = 350
        x = (setup_window.winfo_screenwidth() // 2) - (width // 2)
        y = (setup_window.winfo_screenheight() // 2) - (height // 2)
        setup_window.geometry(f"{width}x{height}+{x}+{y}")
        
        tk.Label(setup_window, text="Welcome to Bunkmeter!", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Import timetable section
        import_frame = ttk.LabelFrame(setup_window, text="Step 1: Import Your Timetable (Optional)", padding=10)
        import_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(import_frame, text="Upload your CSV timetable to auto-detect batches", font=("Arial", 9)).pack()
        
        def import_timetable_firsttime():
            from data_manager import import_timetable_from_csv
            from tkinter import filedialog
            filepath = filedialog.askopenfilename(
                title="Import Custom Timetable",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filepath:
                if import_timetable_from_csv(filepath):
                    # Refresh batch detection
                    update_batch_options()
        
        ttk.Button(import_frame, text="📥 Import Timetable CSV", command=import_timetable_firsttime).pack(pady=5)
        
        # Batch selection section
        batch_frame = ttk.LabelFrame(setup_window, text="Step 2: Select Your Batch/Group", padding=10)
        batch_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        batch_container = ttk.Frame(batch_frame)
        batch_container.pack(fill=tk.BOTH, expand=True)
        
        batch_var = tk.StringVar()
        
        def update_batch_options():
            """
            Dynamically detect and display batch options from timetable
            
            How it works:
            1. Scans all timetable entries for format: "Subject (BatchName) / Subject (BatchName2)"
            2. Extracts batch names from parentheses using regex
            3. Creates radio buttons for each unique batch found
            4. Falls back to default B1/B3, B2/B4 if no batches detected
            
            To modify batch detection:
            - Change regex pattern in re.findall() to match your format
            - Update fallback batch names in the 'if not batch_names' block
            """
            # Clear existing radio buttons before recreating them
            for widget in batch_container.winfo_children():
                widget.destroy()
            
            # Get active timetable (custom if imported, otherwise default)
            from data_manager import get_active_timetable
            import re
            active_timetable = get_active_timetable()
            batch_names = set()
            
            # Scan timetable for batch names in parentheses
            for day_data in active_timetable.values():
                for cell_value in day_data.values():
                    if "/" in cell_value and "(" in cell_value:
                        # Extract batch names from format: "Subject (GroupA) / Subject (GroupB)"
                        # Regex \(([^)]+)\) matches text inside parentheses
                        matches = re.findall(r'\(([^)]+)\)', cell_value)
                        batch_names.update(matches)
            
            # Fallback: If no batches found, use default batches
            if not batch_names:
                batch_names = ["B1/B3", "B2/B4"]
            else:
                batch_names = sorted(list(batch_names))
            
            # Safe access - ensure batch_names is not empty before accessing
            if batch_names:
                batch_var.set(batch_names[0])
            else:
                batch_var.set("B1/B3")
                batch_names = ["B1/B3", "B2/B4"]  # Fallback to defaults
            
            for batch_name in batch_names:
                ttk.Radiobutton(batch_container, text=batch_name, variable=batch_var, value=batch_name).pack(anchor=tk.W, pady=2)
        
        # Initial batch detection
        update_batch_options()
        
        def save_and_close():
            """
            Validate selection and initialize app data
            
            Validation steps:
            1. Check if batch is selected
            2. Parse timetable to get subjects for selected batch
            3. Ensure subjects exist (prevents empty subject list)
            4. Initialize all subjects with empty absent_dates (present by default)
            
            To add custom validation:
            - Add checks before the app_data initialization
            - Show error messages using messagebox.showerror()
            """
            from tkinter import messagebox
            
            selected_batch = batch_var.get()
            
            # Validation 1: Ensure batch is selected
            if not selected_batch:
                messagebox.showerror("Error", "Please select a batch/group before continuing!")
                return
            
            # Parse timetable to extract subjects for this batch
            # Returns dict: {subject_name: weekly_class_count}
            weekly_counts = parse_timetable_csv(selected_batch)
            
            # Validation 2: Ensure subjects exist for selected batch
            if not weekly_counts:
                messagebox.showerror(
                    "Error", 
                    f"No subjects found for batch '{selected_batch}'!\n\n"
                    f"Please import a valid timetable or check your batch selection."
                )
                return
            
            app_data = get_app_data()
            app_data["batch"] = selected_batch
            app_data["subjects"] = [
                {
                    "name": subject,
                    "weekly_count": count,
                    "total_override": None,
                    "attendance_override": None,
                    "absent_dates": []  # All classes present by default
                }
                for subject, count in weekly_counts.items()
            ]
            save_data()
            setup_window.destroy()
        
        ttk.Button(setup_window, text="Continue", command=save_and_close).pack(pady=10)
        
        self.root.wait_window(setup_window)
    
    def create_ui(self):
        """Create main tabbed interface"""
        # Title
        title_frame = tk.Frame(self.root, bg=COLOR_INFO, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="Bunkmeter",
            font=("Arial", 18, "bold"),
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
        # Defer refresh to avoid blocking UI
        self.root.after(10, self._do_refresh)
    
    def _do_refresh(self):
        """Actual refresh logic with optimized order"""
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
