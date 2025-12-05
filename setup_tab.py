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
        
        # Scrollable frame with white background
        canvas = tk.Canvas(tab, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')
        
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
        
        # Create 2-column layout for better space usage with white backgrounds
        self.left_column = tk.Frame(scrollable_frame, bg='#ffffff')
        self.left_column.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        right_column = tk.Frame(scrollable_frame, bg='#ffffff')
        right_column.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Batch Selection (LEFT) - Enhanced with icons and better styling
        self.batch_frame = tk.Frame(self.left_column, bg="#e3f2fd", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#1976d2")
        self.batch_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Batch header with icon
        batch_header = tk.Frame(self.batch_frame, bg="#1976d2", height=50)
        batch_header.pack(fill=tk.X)
        batch_header.pack_propagate(False)
        tk.Label(
            batch_header,
            text="👥 Batch Selection",
            font=("Segoe UI", 15, "bold"),
            bg="#1976d2",
            fg="white",
            padx=20,
            pady=12
        ).pack(side=tk.LEFT)
        
        # Batch content area
        batch_content = tk.Frame(self.batch_frame, bg="#e3f2fd", padx=20, pady=20)
        batch_content.pack(fill=tk.X)
        
        tk.Label(
            batch_content,
            text="Select your batch/section for accurate timetable filtering:",
            font=("Segoe UI", 12),
            bg="#e3f2fd",
            fg="#1565c0"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Container for dynamic batch options with card-like styling
        self.batch_container = tk.Frame(batch_content, bg="#e3f2fd")
        self.batch_container.pack(fill=tk.X, pady=5)
        
        # Initialize batch selection
        self.batch_var = tk.StringVar(value=app_data.get("batch", ""))
        self.update_batch_options()
        
        # Update button with better styling
        update_btn_frame = tk.Frame(batch_content, bg="#e3f2fd")
        update_btn_frame.pack(fill=tk.X, pady=(15, 5))
        
        update_btn = tk.Button(
            update_btn_frame, 
            text="✓ Update Batch", 
            font=("Segoe UI", 11, "bold"),
            bg="#1976d2",
            fg="white",
            activebackground="#1565c0",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.on_batch_update
        )
        update_btn.pack(side=tk.LEFT)
        
        # Setup mode banner (hidden by default)
        self.setup_banner = tk.Frame(self.left_column, bg="#fff3cd")
        # Will be shown/hidden as needed
        
        # Semester Dates (LEFT) - Enhanced with better styling
        self.dates_frame = tk.Frame(self.left_column, bg="#ffffff", relief=tk.RIDGE, bd=1)
        self.dates_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Dates header with icon
        dates_header = tk.Frame(self.dates_frame, bg="#388e3c", height=50)
        dates_header.pack(fill=tk.X)
        dates_header.pack_propagate(False)
        tk.Label(
            dates_header,
            text="📅 Semester Dates",
            font=("Segoe UI", 15, "bold"),
            bg="#388e3c",
            fg="white",
            padx=20,
            pady=12
        ).pack(side=tk.LEFT)
        
        # Dates content area
        dates_content = tk.Frame(self.dates_frame, bg="#e8f5e9", padx=20, pady=20)
        dates_content.pack(fill=tk.X)
        
        # Info text
        tk.Label(
            dates_content,
            text="Set your semester start and end dates for accurate attendance calculation.",
            font=("Segoe UI", 12),
            bg="#e8f5e9",
            fg="#2e7d32"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Calendars container
        calendars_container = tk.Frame(dates_content, bg="#e8f5e9")
        calendars_container.pack(fill=tk.X)
        
        # Start Date Calendar
        start_frame = ttk.LabelFrame(calendars_container, text="Start Date", padding=5)
        start_frame.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, expand=True)
        
        start_date = datetime.now()
        if app_data.get("semester_start"):
            try:
                start_date = datetime.strptime(app_data["semester_start"], "%Y-%m-%d")
            except:
                pass
        
        self.start_date_cal = Calendar(
            start_frame,
            selectmode='day',
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.start_date_cal.pack(pady=5)
        
        # End Date Calendar
        end_frame = ttk.LabelFrame(calendars_container, text="End Date", padding=5)
        end_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        end_date = datetime.now()
        if app_data.get("semester_end"):
            try:
                end_date = datetime.strptime(app_data["semester_end"], "%Y-%m-%d")
            except:
                pass
        
        self.end_date_cal = Calendar(
            end_frame,
            selectmode='day',
            year=end_date.year,
            month=end_date.month,
            day=end_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.end_date_cal.pack(pady=5)
        
        # Save button
        save_btn_frame = tk.Frame(dates_content, bg="#e8f5e9")
        save_btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_dates_btn = tk.Button(
            save_btn_frame, 
            text="✓ Save Semester Dates", 
            font=("Segoe UI", 11, "bold"),
            bg="#388e3c",
            fg="white",
            activebackground="#2e7d32",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.on_dates_update
        )
        save_dates_btn.pack(side=tk.LEFT)
        
        # Holidays (LEFT) - Enhanced with better styling
        self.holidays_frame = tk.Frame(self.left_column, bg="#fff8e1", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#f57c00")
        self.holidays_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Holidays header with icon
        holidays_header = tk.Frame(self.holidays_frame, bg="#f57c00", height=50)
        holidays_header.pack(fill=tk.X)
        holidays_header.pack_propagate(False)
        tk.Label(
            holidays_header,
            text="🏖️ Holiday Periods",
            font=("Segoe UI", 15, "bold"),
            bg="#f57c00",
            fg="white",
            padx=20,
            pady=12
        ).pack(side=tk.LEFT)
        
        # Holidays content area
        holidays_content = tk.Frame(self.holidays_frame, bg="#fff8e1", padx=20, pady=20)
        holidays_content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            holidays_content,
            text="Add holidays when no classes are held (these dates won't affect attendance).",
            font=("Segoe UI", 12),
            bg="#fff8e1",
            fg="#e65100"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        self.holidays_tree = ttk.Treeview(holidays_content, columns=("No", "Name", "Date"), 
                                         show="headings", height=6)
        self.holidays_tree.heading("No", text="#")
        self.holidays_tree.heading("Name", text="Holiday Name")
        self.holidays_tree.heading("Date", text="Date")
        self.holidays_tree.column("No", width=40, minwidth=30, stretch=False)
        self.holidays_tree.column("Name", width=200, minwidth=150)
        self.holidays_tree.column("Date", width=120, minwidth=100)
        self.holidays_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Enable isolated mouse wheel scrolling on holidays tree
        # Uses Enter/Leave binding to prevent scrolling the whole tab
        def _on_holidays_mousewheel(event):
            self.holidays_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Stop event propagation
        
        def _bind_holidays_mousewheel(event):
            self.holidays_tree.bind_all("<MouseWheel>", _on_holidays_mousewheel)
        
        def _unbind_holidays_mousewheel(event):
            self.holidays_tree.unbind_all("<MouseWheel>")
        
        self.holidays_tree.bind("<Enter>", _bind_holidays_mousewheel)
        self.holidays_tree.bind("<Leave>", _unbind_holidays_mousewheel)
        
        btn_frame = tk.Frame(holidays_content, bg="#fff8e1")
        btn_frame.pack(fill=tk.X, pady=(10, 5))
        
        add_holiday_btn = tk.Button(
            btn_frame, 
            text="➕ Add Holiday Period", 
            font=("Segoe UI", 10, "bold"),
            bg="#f57c00",
            fg="white",
            activebackground="#e65100",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.add_holiday
        )
        add_holiday_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        remove_holiday_btn = tk.Button(
            btn_frame, 
            text="➖ Remove Selected", 
            font=("Segoe UI", 10),
            bg="#ffcc80",
            fg="#e65100",
            activebackground="#ffb74d",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.remove_holiday
        )
        remove_holiday_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        remove_all_btn = tk.Button(
            btn_frame, 
            text="🗑️ Remove All", 
            font=("Segoe UI", 10),
            bg="#ffcc80",
            fg="#e65100",
            activebackground="#ffb74d",
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.remove_all_holidays
        )
        remove_all_btn.pack(side=tk.LEFT)
        
        # Timetable Management Section (RIGHT) - Enhanced with better styling
        self.timetable_frame = tk.Frame(right_column, bg="#e8eaf6", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#5c6bc0")
        self.timetable_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Timetable header with icon
        timetable_header = tk.Frame(self.timetable_frame, bg="#5c6bc0", height=50)
        timetable_header.pack(fill=tk.X)
        timetable_header.pack_propagate(False)
        tk.Label(
            timetable_header,
            text="📚 Custom Timetable",
            font=("Segoe UI", 15, "bold"),
            bg="#5c6bc0",
            fg="white",
            padx=20,
            pady=12
        ).pack(side=tk.LEFT)
        
        # Timetable content area
        timetable_content = tk.Frame(self.timetable_frame, bg="#e8eaf6", padx=20, pady=20)
        timetable_content.pack(fill=tk.X)
        
        tk.Label(
            timetable_content, 
            text="Upload your own timetable CSV or export the current one as a template.\nSee COMPLETE_GUIDE.md for format details.",
            font=("Segoe UI", 12),
            bg="#e8eaf6",
            fg="#3949ab",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 15))
        
        timetable_btn_frame = tk.Frame(timetable_content, bg="#e8eaf6")
        timetable_btn_frame.pack(fill=tk.X, pady=8)
        
        tk.Button(
            timetable_btn_frame, 
            text="📥 Import CSV", 
            command=self.import_timetable,
            font=("Segoe UI", 10, "bold"),
            bg="#5c6bc0",
            fg="white",
            activebackground="#3949ab",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            timetable_btn_frame, 
            text="📤 Export Template", 
            command=self.export_timetable,
            font=("Segoe UI", 10, "bold"),
            bg="#5c6bc0",
            fg="white",
            activebackground="#3949ab",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            timetable_btn_frame, 
            text="🔄 Reset to Default", 
            command=self.reset_timetable,
            font=("Segoe UI", 10, "bold"),
            bg="#5c6bc0",
            fg="white",
            activebackground="#3949ab",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Skipped Days (RIGHT)
        # Skipped Days (RIGHT) - Enhanced with better styling
        self.skipped_frame = tk.Frame(right_column, bg="#fce4ec", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#c2185b")
        self.skipped_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Skipped days header with icon
        skipped_header = tk.Frame(self.skipped_frame, bg="#c2185b")
        skipped_header.pack(fill=tk.X)
        tk.Label(
            skipped_header,
            text="🤒 Skipped Days (Sick Leave, etc.)",
            font=("Segoe UI", 15, "bold"),
            bg="#c2185b",
            fg="white",
            padx=20,
            pady=12
        ).pack(side=tk.LEFT)
        
        # Skipped days content area
        skipped_content = tk.Frame(self.skipped_frame, bg="#fce4ec", padx=20, pady=20)
        skipped_content.pack(fill=tk.X)
        
        tk.Label(
            skipped_content, 
            text="Days when you were completely absent (all classes marked absent).",
            font=("Segoe UI", 12),
            bg="#fce4ec",
            fg="#ad1457",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.skipped_tree = ttk.Treeview(skipped_content, columns=("No", "Name", "Date"), 
                                         show="headings", height=4)
        self.skipped_tree.heading("No", text="#")
        self.skipped_tree.heading("Name", text="Reason")
        self.skipped_tree.heading("Date", text="Date")
        self.skipped_tree.column("No", width=40, minwidth=30, stretch=False)
        self.skipped_tree.column("Name", width=200, minwidth=150)
        self.skipped_tree.column("Date", width=120, minwidth=100)
        self.skipped_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Enable isolated mouse wheel scrolling on skipped days tree
        # Uses Enter/Leave binding to prevent scrolling the whole tab
        def _on_skipped_mousewheel(event):
            self.skipped_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Stop event propagation
        
        def _bind_skipped_mousewheel(event):
            self.skipped_tree.bind_all("<MouseWheel>", _on_skipped_mousewheel)
        
        def _unbind_skipped_mousewheel(event):
            self.skipped_tree.unbind_all("<MouseWheel>")
        
        self.skipped_tree.bind("<Enter>", _bind_skipped_mousewheel)
        self.skipped_tree.bind("<Leave>", _unbind_skipped_mousewheel)
        
        skipped_btn_frame = tk.Frame(skipped_content, bg="#fce4ec")
        skipped_btn_frame.pack(fill=tk.X, pady=8)
        tk.Button(
            skipped_btn_frame, 
            text="➕ Add Skipped Period", 
            command=self.add_skipped_days,
            font=("Segoe UI", 10, "bold"),
            bg="#c2185b",
            fg="white",
            activebackground="#ad1457",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            skipped_btn_frame, 
            text="➖ Remove Selected", 
            command=self.remove_skipped_days,
            font=("Segoe UI", 10, "bold"),
            bg="#c2185b",
            fg="white",
            activebackground="#ad1457",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            skipped_btn_frame, 
            text="🗑️ Remove All", 
            command=self.remove_all_skipped_days,
            font=("Segoe UI", 10, "bold"),
            bg="#c2185b",
            fg="white",
            activebackground="#ad1457",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Reset Data Section (RIGHT) - Enhanced with red/warning theme
        self.reset_frame = tk.Frame(right_column, bg="#ffebee", relief=tk.FLAT, bd=0, highlightthickness=2, highlightbackground="#d32f2f")
        self.reset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Red header bar
        reset_header = tk.Frame(self.reset_frame, bg="#d32f2f", height=48)
        reset_header.pack(fill=tk.X)
        reset_header.pack_propagate(False)
        
        tk.Label(
            reset_header,
            text="⚠️ Reset Data",
            font=("Segoe UI", 15, "bold"),
            bg="#d32f2f",
            fg="white"
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Light red content area
        reset_content = tk.Frame(self.reset_frame, bg="#ffebee", padx=20, pady=20)
        reset_content.pack(fill=tk.X)
        
        tk.Label(
            reset_content, 
            text="This will clear all holidays, skipped days, and absent dates.\nSemester dates and batch selection will be preserved.",
            font=("Segoe UI", 12),
            bg="#ffebee",
            fg="#c62828",
            justify=tk.LEFT
        ).pack(pady=(0, 10), anchor="w")
        
        # Warning icon box
        warning_box = tk.Frame(reset_content, bg="#ffcdd2", padx=12, pady=10, relief=tk.FLAT, bd=1)
        warning_box.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            warning_box,
            text="⚡ This action cannot be undone!",
            font=("Segoe UI", 11, "bold"),
            bg="#ffcdd2",
            fg="#b71c1c"
        ).pack(anchor="w")
        
        tk.Button(
            reset_content, 
            text="🔄 Reset All Data", 
            command=self.reset_data,
            font=("Segoe UI", 11, "bold"),
            bg="#d32f2f",
            fg="white",
            activebackground="#c62828",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(pady=8)
        
        self.refresh()
        return tab
    
    def refresh(self):
        """Refresh holidays and skipped days lists with serial numbers"""
        app_data = get_app_data()
        
        # Refresh holidays with serial numbers (individual date format)
        for item in self.holidays_tree.get_children():
            self.holidays_tree.delete(item)
        for idx, holiday in enumerate(app_data.get("holidays", []), start=1):
            # Support both old format {name, start, end} and new format {name, date}
            date_val = holiday.get("date", holiday.get("start", ""))
            self.holidays_tree.insert("", tk.END, values=(idx, holiday["name"], date_val))
        
        # Refresh skipped days with serial numbers (individual date format)
        for item in self.skipped_tree.get_children():
            self.skipped_tree.delete(item)
        for idx, skipped in enumerate(app_data.get("skipped_days", []), start=1):
            # Support both old format {name, start, end} and new format {reason, date}
            date_val = skipped.get("date", skipped.get("start", ""))
            reason = skipped.get("reason", skipped.get("name", ""))
            self.skipped_tree.insert("", tk.END, values=(idx, reason, date_val))
    
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
        """Update batch selection radio buttons dynamically with enhanced styling"""
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
        
        # Configure ttk style for larger radio buttons
        style = ttk.Style()
        style.configure(
            "Batch.TRadiobutton",
            font=("Segoe UI", 12),
            background="#e3f2fd",
            padding=(5, 8)
        )
        
        # Create radio buttons for each batch with enhanced styling
        for batch_name in batch_names:
            ttk.Radiobutton(
                self.batch_container, 
                text=batch_name, 
                variable=self.batch_var, 
                value=batch_name,
                style="Batch.TRadiobutton"
            ).pack(anchor=tk.W, pady=4, padx=5)
    
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
        """Add a holiday period with improved dialog layout"""
        app_data = get_app_data()
        dialog = tk.Toplevel()
        dialog.title("Add Holiday Period")
        dialog.resizable(True, True)
        
        # Center the dialog window with compact size
        width = 620
        height = 420
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main container with padding
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="🏖️ Add Holiday Period", 
                               font=("Segoe UI", 14, "bold"), fg="#007bff")
        title_label.pack(pady=(0, 15))
        
        # Holiday name input
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill="x", pady=(0, 15))
        tk.Label(name_frame, text="Holiday Name:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        name_entry = ttk.Entry(name_frame, width=40, font=("Segoe UI", 10))
        name_entry.pack(side="left", fill="x", expand=True)
        name_entry.insert(0, "")
        name_entry.focus_set()
        
        # Calendars side by side
        calendars_frame = ttk.Frame(main_frame)
        calendars_frame.pack(fill="both", expand=True, pady=10)
        
        # Start date calendar (left)
        start_frame = ttk.LabelFrame(calendars_frame, text="Start Date", padding=10)
        start_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        start_cal = Calendar(start_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        start_cal.pack()
        
        # End date calendar (right)
        end_frame = ttk.LabelFrame(calendars_frame, text="End Date", padding=10)
        end_frame.pack(side="left", fill="both", expand=True)
        end_cal = Calendar(end_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        end_cal.pack()
        
        # Button frame at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(15, 0))
        
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
            
            if start > end:
                messagebox.showerror("Error", "Start date must be before or equal to end date")
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
            
            # Add each day as individual holiday entry
            from datetime import datetime, timedelta
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                return
            
            # Check for existing holidays on these dates
            existing_holidays = set(h.get("date", h.get("start", "")) for h in app_data.get("holidays", []))
            added_count = 0
            skipped_count = 0
            
            current = start_date
            while current <= end_date:
                date_str = current.strftime("%Y-%m-%d")
                if date_str not in existing_holidays:
                    app_data["holidays"].append({"name": name, "date": date_str})
                    added_count += 1
                else:
                    skipped_count += 1
                current += timedelta(days=1)
            
            save_data()
            self.refresh()
            self.refresh_all_tabs()
            dialog.destroy()
            
            if skipped_count > 0:
                messagebox.showinfo("Success", f"Added {added_count} holiday(s).\n{skipped_count} date(s) were already holidays.")
            else:
                messagebox.showinfo("Success", f"Added {added_count} holiday(s).")
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="✓ Save Holiday", command=save_holiday).pack(side="right", padx=5)
    
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
    
    def remove_all_holidays(self):
        """Remove all holidays after confirmation"""
        app_data = get_app_data()
        
        if not app_data.get("holidays"):
            messagebox.showinfo("Info", "No holidays to remove")
            return
        
        count = len(app_data["holidays"])
        confirm = messagebox.askyesno(
            "Confirm Remove All",
            f"Are you sure you want to remove all {count} holiday(s)?\n\nThis action cannot be undone.",
            icon="warning"
        )
        
        if confirm:
            app_data["holidays"] = []
            save_data()
            self.refresh()
            self.refresh_all_tabs()
            messagebox.showinfo("Success", f"Removed all {count} holiday(s)")
    
    def add_skipped_days(self):
        """Add a skipped days period with improved dialog layout"""
        app_data = get_app_data()
        dialog = tk.Toplevel()
        dialog.title("Add Skipped Period")
        dialog.resizable(True, True)
        
        # Center the dialog window with compact size
        width = 620
        height = 460
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Main container with padding
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="📅 Add Skipped Period", 
                               font=("Segoe UI", 14, "bold"), fg="#dc3545")
        title_label.pack(pady=(0, 10))
        
        # Warning message
        warning_label = tk.Label(
            main_frame, 
            text="⚠️ All classes in this period will be marked absent",
            font=("Segoe UI", 10),
            fg="#dc3545"
        )
        warning_label.pack(pady=(0, 10))
        
        # Reason input
        reason_frame = ttk.Frame(main_frame)
        reason_frame.pack(fill="x", pady=(0, 15))
        tk.Label(reason_frame, text="Reason:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        name_entry = ttk.Entry(reason_frame, width=40, font=("Segoe UI", 10))
        name_entry.pack(side="left", fill="x", expand=True)
        name_entry.insert(0, "")
        name_entry.focus_set()
        
        # Placeholder hint
        tk.Label(reason_frame, text="(e.g., Sick, Personal, Family)", 
                 font=("Segoe UI", 10), fg="#6c757d").pack(side="left", padx=5)
        
        # Calendars side by side
        calendars_frame = ttk.Frame(main_frame)
        calendars_frame.pack(fill="both", expand=True, pady=10)
        
        # Start date calendar (left)
        start_frame = ttk.LabelFrame(calendars_frame, text="Start Date", padding=10)
        start_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        start_cal = Calendar(start_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        start_cal.pack()
        
        # End date calendar (right)
        end_frame = ttk.LabelFrame(calendars_frame, text="End Date", padding=10)
        end_frame.pack(side="left", fill="both", expand=True)
        end_cal = Calendar(end_frame, selectmode='day', date_pattern='yyyy-mm-dd')
        end_cal.pack()
        
        # Button frame at bottom
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(15, 0))
        
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
            
            if start > end:
                messagebox.showerror("Error", "Start date must be before or equal to end date")
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
            from datetime import datetime, timedelta
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
            
            # Get existing holidays and skipped days to check for overlaps
            existing_holidays = set(h.get("date", h.get("start", "")) for h in app_data.get("holidays", []))
            existing_skipped = set(s.get("date", s.get("start", "")) for s in app_data.get("skipped_days", []))
            
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format")
                dialog.destroy()
                return
            
            current = start_date
            batch = app_data.get("batch", "B1/B3")
            added_count = 0
            skipped_holiday = 0
            skipped_duplicate = 0
            
            while current <= end_date:
                date_str = current.strftime("%Y-%m-%d")
                
                # Skip if date is a holiday (holidays take priority)
                if date_str in existing_holidays:
                    skipped_holiday += 1
                    current += timedelta(days=1)
                    continue
                
                # Skip if already marked as skipped
                if date_str in existing_skipped:
                    skipped_duplicate += 1
                    current += timedelta(days=1)
                    continue
                
                # Add this date as a skipped day
                app_data["skipped_days"].append({"reason": name, "date": date_str})
                added_count += 1
                
                # Mark all subjects as absent for this date
                day_name = current.strftime("%A").upper()
                subjects = get_subjects_for_day(day_name, batch)
                
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
            
            # Build result message
            msg_parts = [f"Marked {added_count} day(s) as absent."]
            if skipped_holiday > 0:
                msg_parts.append(f"{skipped_holiday} day(s) skipped (already holidays).")
            if skipped_duplicate > 0:
                msg_parts.append(f"{skipped_duplicate} day(s) skipped (already marked).")
            messagebox.showinfo("Success", "\n".join(msg_parts))
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="✓ Save & Mark Absent", command=save_skipped).pack(side="right", padx=5)
    
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
        
        # Get the date from new format or fallback to old format
        date_str = skipped.get("date", skipped.get("start", ""))
        if not date_str:
            messagebox.showerror("Error", "Invalid skipped day entry - no date found")
            return
        
        # Remove absence marks for this single date
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date format: {str(e)}")
            return
        
        batch = app_data.get("batch", "B1/B3")
        day_name = date_obj.strftime("%A").upper()
        subjects = get_subjects_for_day(day_name, batch)
        
        # Count occurrences of each subject on this day
        subject_counts = {}
        for subject in subjects:
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        # Remove ALL occurrences for each subject (matches how they were added)
        for subject, count in subject_counts.items():
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if subject_data:
                # Remove 'count' occurrences of this date from absent_dates
                for _ in range(count):
                    if date_str in subject_data.get("absent_dates", []):
                        subject_data["absent_dates"].remove(date_str)
        
        del app_data["skipped_days"][index]
        save_data()
        self.refresh()
        self.refresh_all_tabs()
    
    def remove_all_skipped_days(self):
        """Remove all skipped days and their absence marks after confirmation"""
        app_data = get_app_data()
        
        if not app_data.get("skipped_days"):
            messagebox.showinfo("Info", "No skipped days to remove")
            return
        
        count = len(app_data["skipped_days"])
        confirm = messagebox.askyesno(
            "Confirm Remove All",
            f"Are you sure you want to remove all {count} skipped day(s)?\n\n"
            "This will also restore the attendance marks for those days.\n\n"
            "This action cannot be undone.",
            icon="warning"
        )
        
        if not confirm:
            return
        
        # Remove absence marks for all skipped days
        from datetime import datetime
        batch = app_data.get("batch", "B1/B3")
        
        for skipped in app_data.get("skipped_days", []):
            date_str = skipped.get("date", skipped.get("start", ""))
            if not date_str:
                continue
            
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = date_obj.strftime("%A").upper()
                subjects = get_subjects_for_day(day_name, batch)
                
                # Count occurrences of each subject on this day
                subject_counts = {}
                for subject in subjects:
                    subject_counts[subject] = subject_counts.get(subject, 0) + 1
                
                # Remove ALL occurrences for each subject
                for subject, count in subject_counts.items():
                    subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
                    if subject_data:
                        for _ in range(count):
                            if date_str in subject_data.get("absent_dates", []):
                                subject_data["absent_dates"].remove(date_str)
            except (ValueError, KeyError):
                continue
        
        # Clear all skipped days
        app_data["skipped_days"] = []
        save_data()
        self.refresh()
        self.refresh_all_tabs()
        messagebox.showinfo("Success", f"Removed all {count} skipped day(s) and restored attendance marks")
    
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
            text="⚠️ SETUP REQUIRED: Select your batch, then set semester dates to continue",
            font=("Segoe UI", 12, "bold"),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=10, padx=15)
        
        # Disable all sections except batch and dates
        self.set_frame_state(self.holidays_frame, "disabled")
        self.set_frame_state(self.skipped_frame, "disabled")
        self.set_frame_state(self.reset_frame, "disabled")
        # Timetable frame stays enabled for export/reset
        
        # Update visual appearance - dim the disabled frames
        self.holidays_frame.configure(highlightbackground="#cccccc")
        self.skipped_frame.configure(highlightbackground="#cccccc")
        self.reset_frame.configure(highlightbackground="#cccccc")
    
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
        
        # Restore visual appearance - restore original border colors
        self.holidays_frame.configure(highlightbackground="#f57c00")
        self.skipped_frame.configure(highlightbackground="#c2185b")
        self.reset_frame.configure(highlightbackground="#d32f2f")
    
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
