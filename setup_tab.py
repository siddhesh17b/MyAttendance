"""
Setup Tab - Configuration interface
Batch selection, semester dates, holidays, and reset functionality

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from data_manager import get_app_data, save_data, parse_timetable_csv, \
    export_timetable_to_csv, import_timetable_from_csv, reset_to_default_timetable, \
    get_subjects_for_day, get_active_timetable
from calculations import parse_date
import re

class SetupTab:
    def __init__(self, notebook, refresh_callback):
        self.notebook = notebook
        self.refresh_all_tabs = refresh_callback
        self.batch_var = None
        self.batch_frame = None
        self.batch_container = None
        self.start_date_cal = None
        self.end_date_cal = None
        self.holidays_tree = None
        self.skipped_tree = None
        # Setup mode tracking - forces user to select batch & dates after import
        self.setup_mode = False
        self.setup_step = 0  # 0=batch, 1=dates, 2=complete
        # Frame references for enable/disable
        self.left_column = None
        self.dates_frame = None
        self.holidays_frame = None
        self.timetable_frame = None
        self.skipped_frame = None
        self.reset_frame = None
        self.setup_banner = None
    
    def create(self):
        """Create setup tab"""
        tab = ttk.Frame(self.notebook)
        
        # Scrollable frame
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def _configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable frame fill canvas width for responsive layout
            canvas.itemconfig(canvas_window, width=event.width)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", _configure_scroll)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling (local binding only)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind to all child widgets when they enter
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        app_data = get_app_data()
        
        # Create 2-column layout for better space usage
        self.left_column = ttk.Frame(scrollable_frame)
        self.left_column.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        right_column = ttk.Frame(scrollable_frame)
        right_column.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Batch Selection (LEFT)
        self.batch_frame = tk.LabelFrame(self.left_column, text="Batch Selection", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        self.batch_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Container for dynamic batch options
        self.batch_container = ttk.Frame(self.batch_frame)
        self.batch_container.pack(fill=tk.X)
        
        # Initialize batch selection
        self.batch_var = tk.StringVar(value=app_data.get("batch", ""))
        self.update_batch_options()
        
        ttk.Button(self.batch_frame, text="Update Batch", command=self.on_batch_update).pack(pady=5)
        
        # Setup mode banner (hidden by default)
        self.setup_banner = tk.Frame(self.left_column, bg="#fff3cd")
        # Will be shown/hidden as needed
        
        # Semester Dates (LEFT)
        self.dates_frame = tk.LabelFrame(self.left_column, text="Semester Dates", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        self.dates_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start Date Calendar
        tk.Label(self.dates_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        start_date = datetime.now()
        if app_data.get("semester_start"):
            try:
                start_date = datetime.strptime(app_data["semester_start"], "%Y-%m-%d")
            except:
                pass
        
        self.start_date_cal = Calendar(
            self.dates_frame,
            selectmode='day',
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.start_date_cal.grid(row=1, column=0, padx=5, pady=5)
        
        # End Date Calendar
        tk.Label(self.dates_frame, text="End Date:", font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        end_date = datetime.now()
        if app_data.get("semester_end"):
            try:
                end_date = datetime.strptime(app_data["semester_end"], "%Y-%m-%d")
            except:
                pass
        
        self.end_date_cal = Calendar(
            self.dates_frame,
            selectmode='day',
            year=end_date.year,
            month=end_date.month,
            day=end_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.end_date_cal.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(self.dates_frame, text="Save Dates", command=self.on_dates_update).grid(
            row=2, column=0, columnspan=2, pady=10)
        
        # Holidays (LEFT)
        self.holidays_frame = tk.LabelFrame(self.left_column, text="Holiday Periods", 
                                      font=("Arial", 11, "bold"), padx=10, pady=10)
        self.holidays_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.holidays_tree = ttk.Treeview(self.holidays_frame, columns=("Name", "Start", "End"), 
                                         show="headings", height=6)
        self.holidays_tree.heading("Name", text="Holiday Name")
        self.holidays_tree.heading("Start", text="Start Date")
        self.holidays_tree.heading("End", text="End Date")
        self.holidays_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Enable mouse wheel scrolling on holidays tree
        def _on_holidays_mousewheel(event):
            self.holidays_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        self.holidays_tree.bind("<MouseWheel>", _on_holidays_mousewheel)
        
        btn_frame = tk.Frame(self.holidays_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="➕ Add Holiday Period", command=self.add_holiday).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="➖ Remove Holiday", command=self.remove_holiday).pack(side=tk.LEFT, padx=5)
        
        # Timetable Management Section (RIGHT)
        self.timetable_frame = tk.LabelFrame(right_column, text="Custom Timetable Management", 
                                        font=("Arial", 11, "bold"), padx=10, pady=10)
        self.timetable_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            self.timetable_frame, 
            text="📚 Upload your own timetable CSV or export the current one as a template.\nSee COMPLETE_GUIDE.md for format details.",
            font=("Arial", 9),
            foreground="#007bff",
            justify=tk.LEFT
        ).pack(pady=5)
        
        timetable_btn_frame = tk.Frame(self.timetable_frame)
        timetable_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            timetable_btn_frame, 
            text="📥 Import Custom Timetable", 
            command=self.import_timetable
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            timetable_btn_frame, 
            text="📤 Export Timetable Template", 
            command=self.export_timetable
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            timetable_btn_frame, 
            text="🔄 Reset to Default", 
            command=self.reset_timetable
        ).pack(side=tk.LEFT, padx=5)
        
        # Skipped Days (RIGHT)
        self.skipped_frame = tk.LabelFrame(right_column, text="Completely Skipped Days (e.g., Sick Leave)", 
                                      font=("Arial", 11, "bold"), padx=10, pady=10)
        self.skipped_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            self.skipped_frame, 
            text="📅 Days when you were completely absent (all classes marked absent)",
            font=("Arial", 9),
            foreground="#dc3545",
            justify=tk.LEFT
        ).pack(pady=5)
        
        self.skipped_tree = ttk.Treeview(self.skipped_frame, columns=("Name", "Start", "End"), 
                                         show="headings", height=4)
        self.skipped_tree.heading("Name", text="Reason")
        self.skipped_tree.heading("Start", text="Start Date")
        self.skipped_tree.heading("End", text="End Date")
        self.skipped_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Enable mouse wheel scrolling on skipped days tree
        def _on_skipped_mousewheel(event):
            self.skipped_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        self.skipped_tree.bind("<MouseWheel>", _on_skipped_mousewheel)
        
        skipped_btn_frame = tk.Frame(self.skipped_frame)
        skipped_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(skipped_btn_frame, text="➕ Add Skipped Period", command=self.add_skipped_days).pack(side=tk.LEFT, padx=5)
        ttk.Button(skipped_btn_frame, text="➖ Remove Skipped Period", command=self.remove_skipped_days).pack(side=tk.LEFT, padx=5)
        
        # Reset Data Section (RIGHT)
        self.reset_frame = tk.LabelFrame(right_column, text="Reset Data", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        self.reset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            self.reset_frame, 
            text="⚠️ Warning: This will clear all holidays and absent dates.\nSemester dates and batch will be preserved.",
            font=("Arial", 9),
            foreground="#dc3545",
            justify=tk.LEFT
        ).pack(pady=5)
        
        ttk.Button(
            self.reset_frame, 
            text="🔄 Reset All Data", 
            command=self.reset_data
        ).pack(pady=5)
        
        # GitHub link at bottom (inside scrollable frame)
        github_frame = ttk.Frame(scrollable_frame)
        github_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        github_label = tk.Label(
            github_frame,
            text="Made by Siddhesh Bisen | GitHub: https://github.com/siddhesh17b",
            font=("Segoe UI", 9),
            foreground="#666666",
            cursor="hand2"
        )
        github_label.pack()
        
        # Make link clickable
        def open_github(event):
            import webbrowser
            webbrowser.open("https://github.com/siddhesh17b")
        github_label.bind("<Button-1>", open_github)
        
        self.refresh()
        return tab
    
    def refresh(self):
        """Refresh holidays and skipped days lists"""
        app_data = get_app_data()
        
        # Refresh holidays
        for item in self.holidays_tree.get_children():
            self.holidays_tree.delete(item)
        for holiday in app_data.get("holidays", []):
            self.holidays_tree.insert("", tk.END, values=(holiday["name"], holiday["start"], holiday["end"]))
        
        # Refresh skipped days
        for item in self.skipped_tree.get_children():
            self.skipped_tree.delete(item)
        for skipped in app_data.get("skipped_days", []):
            self.skipped_tree.insert("", tk.END, values=(skipped["name"], skipped["start"], skipped["end"]))
    
    def extract_batch_names(self):
        """
        Extract all unique batch names from timetable
        
        Scans timetable for entries like:
        - \"CN Lab (B1&B3) / DAA Lab (B2&B4)\" → Extracts: B1&B3, B2&B4
        - \"Software Lab (Group A) / Software Lab (Group B)\" → Extracts: Group A, Group B
        
        How it works:
        1. Uses regex \\(([^)]+)\\) to find text inside parentheses
        2. Filters out common words like \"Lab\", \"Tutorial\"
        3. Returns unique sorted batch names
        4. Falls back to default B1/B3, B2/B4 if none found
        
        To modify:
        - Add more filter words to the exclusion list [\"Lab\", \"Tutorial\", ...]
        - Change regex pattern for different parentheses formats
        - Update fallback batch names
        
        Returns:
            list: Sorted list of unique batch names
        """
        batch_names = set()
        try:
            active_timetable = get_active_timetable()
            
            # Scan all days and time slots
            for day, time_slots_dict in active_timetable.items():
                for time_slot, cell_value in time_slots_dict.items():
                    # Skip empty cells and lunch breaks
                    if not cell_value or "Lunch" in cell_value:
                        continue
                        
                    # Extract all text inside parentheses using regex
                    # Pattern: \(([^)]+)\) matches anything between ( and )
                    matches = re.findall(r'\(([^)]+)\)', cell_value)
                    
                    for match in matches:
                        # Clean whitespace and validate
                        batch_name = match.strip()
                        # Exclude common non-batch words
                        if batch_name and batch_name not in ["Lab", "Tutorial"]:
                            batch_names.add(batch_name)
                            
        except Exception as e:
            print(f"Error extracting batch names: {e}")
        
        # Fallback: Use default batches if none detected
        if not batch_names:
            batch_names = {"B1/B3", "B2/B4"}
        
        return sorted(batch_names)
    
    def update_batch_options(self):
        """Update batch selection radio buttons dynamically"""
        # Clear existing widgets
        for widget in self.batch_container.winfo_children():
            widget.destroy()
        
        # Get batch names from timetable
        batch_names = self.extract_batch_names()
        
        # Get current batch or default to first option
        app_data = get_app_data()
        current_batch = app_data.get("batch", "")
        
        # If current batch not in options, default to first
        if not current_batch or current_batch not in batch_names:
            self.batch_var.set(batch_names[0])
        else:
            self.batch_var.set(current_batch)
        
        # Create radio buttons for each batch
        for batch_name in batch_names:
            ttk.Radiobutton(
                self.batch_container, 
                text=batch_name, 
                variable=self.batch_var, 
                value=batch_name
            ).pack(anchor=tk.W, pady=2)
    
    def on_batch_update(self):
        app_data = get_app_data()
        new_batch = self.batch_var.get()
        
        # Validate batch selection
        if not new_batch:
            messagebox.showerror("Error", "Please select a batch/group before updating!")
            return
        
        if new_batch != app_data.get("batch"):
            app_data["batch"] = new_batch
            weekly_counts = parse_timetable_csv(new_batch)
            
            # Validate that subjects exist for this batch
            if not weekly_counts:
                messagebox.showerror("Error", f"No subjects found for batch '{new_batch}'!\nPlease check your timetable.")
                return
            
            existing_subjects = {s["name"]: s for s in app_data["subjects"]}
            app_data["subjects"] = []
            for subject, count in weekly_counts.items():
                if subject in existing_subjects:
                    existing_subjects[subject]["weekly_count"] = count
                    app_data["subjects"].append(existing_subjects[subject])
                else:
                    app_data["subjects"].append({"name": subject, "weekly_count": count, "total_override": None, "attendance_override": None, "absent_dates": []})
            
            save_data()
            self.refresh_all_tabs()
            
            # Check if setup is complete (batch + dates set)
            if self.setup_mode:
                if self.check_setup_complete():
                    messagebox.showinfo("Setup Complete", "Batch and dates configured! All features are now available.")
                else:
                    messagebox.showinfo("Next Step", "Batch updated! Now please set your semester start and end dates.")
            else:
                messagebox.showinfo("Success", "Batch updated successfully!")
    
    def on_dates_update(self):
        app_data = get_app_data()
        start_date = self.start_date_cal.get_date()
        end_date = self.end_date_cal.get_date()
        
        # Validate semester dates
        if start_date >= end_date:
            messagebox.showerror("Error", "Start date must be before end date!")
            return
        
        app_data["semester_start"] = start_date
        app_data["semester_end"] = end_date
        save_data()
        self.refresh_all_tabs()
        
        # Check if setup is complete (batch + dates set)
        if self.setup_mode:
            if self.check_setup_complete():
                messagebox.showinfo("Setup Complete", "Batch and dates configured! All features are now available.")
            else:
                messagebox.showinfo("Next Step", "Dates saved! Now please select your batch and click 'Update Batch'.")
        else:
            messagebox.showinfo("Success", "Semester dates updated!")
    
    def add_holiday(self):
        """Add a holiday period"""
        app_data = get_app_data()
        dialog = tk.Toplevel()
        dialog.title("Add Holiday Period")
        dialog.resizable(True, True)
        
        # Center the dialog window with increased size
        width = 500
        height = 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create scrollable container
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Reason (e.g., Sick, Personal):", font=("Segoe UI", 10, "bold")).pack(pady=5)
        tk.Label(scrollable_frame, text="Holiday Name:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        name_entry = ttk.Entry(scrollable_frame, width=30)
        name_entry.pack()
        
        # Start date calendar
        tk.Label(scrollable_frame, text="Start Date:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        start_cal = Calendar(scrollable_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        start_cal.pack(pady=5)
        
        # End date calendar
        tk.Label(scrollable_frame, text="End Date:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        end_cal = Calendar(scrollable_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        end_cal.pack(pady=5)
        
        def save_holiday():
            name = name_entry.get().strip()
            start = start_cal.get_date()
            end = end_cal.get_date()
            
            if not name or not start or not end:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if not parse_date(start) or not parse_date(end):
                messagebox.showerror("Error", "Invalid date format")
                return
            
            # Validate dates are within semester range
            semester_start = app_data.get("semester_start")
            semester_end = app_data.get("semester_end")
            if semester_start and semester_end:
                if start < semester_start or end > semester_end:
                    messagebox.showerror(
                        "Error", 
                        f"Holiday dates must be within semester period:\n"
                        f"Semester: {semester_start} to {semester_end}\n"
                        f"You entered: {start} to {end}"
                    )
                    return
            
            app_data["holidays"].append({"name": name, "start": start, "end": end})
            save_data()
            self.refresh()
            self.refresh_all_tabs()
            dialog.destroy()
        
        ttk.Button(scrollable_frame, text="Save", command=save_holiday).pack(pady=10)
    
    def remove_holiday(self):
        """Remove selected holiday"""
        app_data = get_app_data()
        selected = self.holidays_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a holiday to remove")
            return
        
        try:
            index = self.holidays_tree.index(selected[0])
            if 0 <= index < len(app_data.get("holidays", [])):
                del app_data["holidays"][index]
            else:
                messagebox.showerror("Error", "Invalid holiday selection")
                return
        except (tk.TclError, IndexError) as e:
            messagebox.showerror("Error", f"Failed to remove holiday: {str(e)}")
            return
        save_data()
        self.refresh()
        self.refresh_all_tabs()
    
    def add_skipped_days(self):
        """Add a skipped days period"""
        app_data = get_app_data()
        dialog = tk.Toplevel()
        dialog.title("Add Skipped Period")
        dialog.resizable(True, True)
        
        # Center the dialog window with increased size
        width = 500
        height = 700
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create scrollable container
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Reason (e.g., Sick, Personal):", font=("Segoe UI", 10, "bold")).pack(pady=5)
        name_entry = ttk.Entry(scrollable_frame, width=30)
        name_entry.pack()
        
        # Start date calendar
        tk.Label(scrollable_frame, text="Start Date:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        start_cal = Calendar(scrollable_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        start_cal.pack(pady=5)
        
        # End date calendar
        tk.Label(scrollable_frame, text="End Date:", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))
        end_cal = Calendar(scrollable_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        end_cal.pack(pady=5)
        
        tk.Label(
            scrollable_frame, 
            text="⚠️ All classes in this period will be marked absent",
            font=("Arial", 9),
            foreground="#dc3545"
        ).pack(pady=5)
        
        def save_skipped():
            name = name_entry.get().strip()
            start = start_cal.get_date()
            end = end_cal.get_date()
            
            if not name or not start or not end:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if not parse_date(start) or not parse_date(end):
                messagebox.showerror("Error", "Invalid date format")
                return
            
            # Validate dates are within semester range
            semester_start = app_data.get("semester_start")
            semester_end = app_data.get("semester_end")
            if semester_start and semester_end:
                if start < semester_start or end > semester_end:
                    messagebox.showerror(
                        "Error", 
                        f"Skipped days must be within semester period:\n"
                        f"Semester: {semester_start} to {semester_end}\n"
                        f"You entered: {start} to {end}"
                    )
                    return
            
            # Validate dates are not in the future
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            if start > today:
                messagebox.showerror(
                    "Error", 
                    f"Cannot mark future dates as skipped!\n"
                    f"Start date {start} is in the future.\n"
                    f"Today is {today}."
                )
                return
            
            # Initialize skipped_days if not exists
            if "skipped_days" not in app_data:
                app_data["skipped_days"] = []
            
            app_data["skipped_days"].append({"name": name, "start": start, "end": end})
            
            # Mark all subjects as absent for this period
            from datetime import datetime, timedelta
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                dialog.destroy()
                return
            
            current = start_date
            batch = app_data.get("batch", "B1/B3")
            
            while current <= end_date:
                date_str = current.strftime("%Y-%m-%d")
                day_name = current.strftime("%A").upper()
                subjects = get_subjects_for_day(day_name, batch)
                
                # For each subject occurrence (handles multi-occurrence subjects)
                # subjects list may contain duplicates for subjects appearing multiple times
                for subject in subjects:
                    subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
                    if subject_data:
                        if "absent_dates" not in subject_data:
                            subject_data["absent_dates"] = []
                        # Append date for EACH occurrence (allows duplicates)
                        subject_data["absent_dates"].append(date_str)
                
                current += timedelta(days=1)
            
            save_data()
            self.refresh()
            self.refresh_all_tabs()
            dialog.destroy()
            messagebox.showinfo("Success", f"Marked all classes as absent from {start} to {end}")
        
        ttk.Button(scrollable_frame, text="Save", command=save_skipped).pack(pady=10)
    
    def remove_skipped_days(self):
        """Remove selected skipped period and its absence marks"""
        app_data = get_app_data()
        selected = self.skipped_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a skipped period to remove")
            return
        
        if "skipped_days" not in app_data or not app_data["skipped_days"]:
            messagebox.showinfo("Info", "No skipped days to remove")
            return
        
        try:
            index = self.skipped_tree.index(selected[0])
            if not (0 <= index < len(app_data["skipped_days"])):
                messagebox.showerror("Error", "Invalid skipped period selection")
                return
            
            skipped = app_data["skipped_days"][index]
        except (tk.TclError, IndexError, KeyError) as e:
            messagebox.showerror("Error", f"Failed to access skipped period: {str(e)}")
            return
        
        # Automatically remove absence marks for this period
        from datetime import datetime, timedelta
        try:
            start_date = datetime.strptime(skipped["start"], "%Y-%m-%d")
            end_date = datetime.strptime(skipped["end"], "%Y-%m-%d")
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error", f"Invalid date format in skipped period: {str(e)}")
            return
        current = start_date
        batch = app_data.get("batch", "B1/B3")
        
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            day_name = current.strftime("%A").upper()
            subjects = get_subjects_for_day(day_name, batch)
            
            # For each subject occurrence (handles multi-occurrence subjects)
            for subject in subjects:
                subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
                # Remove ONE occurrence per loop iteration (matches how they were added)
                if subject_data and date_str in subject_data.get("absent_dates", []):
                    subject_data["absent_dates"].remove(date_str)
            
            current += timedelta(days=1)
        
        del app_data["skipped_days"][index]
        save_data()
        self.refresh()
        self.refresh_all_tabs()
    
    def reset_data(self):
        """Reset all user data (holidays and absent dates)"""
        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "This will clear:\n\n"
            "• All holidays\n"
            "• All skipped days\n"
            "• All absent dates for all subjects\n"
            "• All total overrides\n\n"
            "Batch and semester dates will be preserved.\n\n"
            "Are you sure you want to continue?",
            icon="warning"
        )
        
        if not confirm:
            return
        
        app_data = get_app_data()
        
        # Clear holidays and skipped days
        app_data["holidays"] = []
        if "skipped_days" in app_data:
            app_data["skipped_days"] = []
        
        # Clear absent dates and total overrides for all subjects
        for subject in app_data.get("subjects", []):
            subject["absent_dates"] = []
            subject["total_override"] = None
            subject["attendance_override"] = None
        
        # Save changes
        save_data()
        
        # Refresh all tabs
        self.refresh()
        self.refresh_all_tabs()
        
        messagebox.showinfo("Success", "All data has been reset successfully!")
    
    def set_frame_state(self, frame, state):
        """Enable or disable all children in a frame recursively"""
        for child in frame.winfo_children():
            try:
                child.configure(state=state)
            except tk.TclError:
                pass  # Widget doesn't support state
            # Recursively handle nested frames
            if isinstance(child, (tk.Frame, ttk.Frame, tk.LabelFrame)):
                self.set_frame_state(child, state)
    
    def enter_setup_mode(self):
        """Enter setup mode after timetable import - disable non-essential sections"""
        self.setup_mode = True
        self.setup_step = 0  # Start with batch selection
        
        # Show setup banner
        self.setup_banner.pack(fill=tk.X, padx=10, pady=(5, 0), before=self.dates_frame)
        for widget in self.setup_banner.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.setup_banner,
            text="⚠️ Setup Required: Select your batch, then set semester dates to continue",
            font=("Arial", 10, "bold"),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=8, padx=10)
        
        # Disable all sections except batch and dates
        self.set_frame_state(self.holidays_frame, "disabled")
        self.set_frame_state(self.skipped_frame, "disabled")
        self.set_frame_state(self.reset_frame, "disabled")
        # Timetable frame stays enabled for export/reset
        
        # Update visual appearance
        self.holidays_frame.configure(fg="gray")
        self.skipped_frame.configure(fg="gray")
        self.reset_frame.configure(fg="gray")
    
    def exit_setup_mode(self):
        """Exit setup mode - enable all sections"""
        self.setup_mode = False
        self.setup_step = 2
        
        # Hide setup banner
        self.setup_banner.pack_forget()
        
        # Enable all sections
        self.set_frame_state(self.holidays_frame, "normal")
        self.set_frame_state(self.skipped_frame, "normal")
        self.set_frame_state(self.reset_frame, "normal")
        
        # Restore visual appearance
        self.holidays_frame.configure(fg="black")
        self.skipped_frame.configure(fg="black")
        self.reset_frame.configure(fg="black")
    
    def check_setup_complete(self):
        """Check if batch and dates are set, if so exit setup mode"""
        app_data = get_app_data()
        batch = app_data.get("batch", "")
        start = app_data.get("semester_start", "")
        end = app_data.get("semester_end", "")
        subjects = app_data.get("subjects", [])
        
        if batch and start and end and len(subjects) > 0:
            self.exit_setup_mode()
            return True
        return False
    
    def import_timetable(self):
        """Import custom timetable from CSV and enter setup mode"""
        # Confirm reset
        confirm = messagebox.askyesno(
            "Confirm Import",
            "Importing a new timetable will RESET all data:\n\n"
            "• All attendance records\n"
            "• All holidays\n"
            "• All skipped days\n"
            "• All manual overrides\n\n"
            "Continue?",
            icon="warning"
        )
        
        if not confirm:
            return
        
        success = import_timetable_from_csv()
        if success:
            # Reset ALL data
            app_data = get_app_data()
            app_data["holidays"] = []
            app_data["skipped_days"] = []
            app_data["batch"] = ""  # Clear batch to force re-selection
            app_data["subjects"] = []  # Clear subjects until batch is selected
            
            save_data()
            
            # Update batch selection UI with new timetable
            self.update_batch_options()
            self.batch_var.set("")  # Clear batch selection
            
            # Enter setup mode
            self.enter_setup_mode()
            
            self.refresh()
            self.refresh_all_tabs()
    
    def export_timetable(self):
        """Export current timetable to CSV template"""
        export_timetable_to_csv()
    
    def reset_timetable(self):
        """Reset to default hardcoded timetable"""
        success = reset_to_default_timetable()
        if success:
            # Reinitialize subjects with default timetable
            app_data = get_app_data()
            batch = app_data.get("batch", "B1/B3")
            subject_counts = parse_timetable_csv(batch)
            
            # Update subjects
            existing_subjects = {s["name"]: s for s in app_data.get("subjects", [])}
            app_data["subjects"] = []
            
            for subject_name, weekly_count in subject_counts.items():
                if subject_name in existing_subjects:
                    existing_subjects[subject_name]["weekly_count"] = weekly_count
                    app_data["subjects"].append(existing_subjects[subject_name])
                else:
                    app_data["subjects"].append({
                        "name": subject_name,
                        "weekly_count": weekly_count,
                        "total_override": None,
                        "attendance_override": None,
                        "absent_dates": []
                    })
            
            save_data()
            self.refresh_all_tabs()
            messagebox.showinfo("Success", "Timetable reset to default successfully!\nAll tabs have been updated.")
