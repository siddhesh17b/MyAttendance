"""
Attendance Calendar - Google Calendar-style monthly view
Features:
- Monthly grid layout with color-coded days
- Click date to mark individual subjects absent/present
- Right-click date to mark all classes as absent
- Holiday toggle functionality

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, date

from data_manager import get_app_data, save_data, get_subjects_for_day

# Color scheme for day status
COLOR_PRESENT = "#ACDAAD"  #  all classes present
COLOR_ABSENT = "#8CDEE9"   # some classes absent
COLOR_SKIPPED = "#EF5350"  # ALL classes absent (completely skipped)
COLOR_HOLIDAY = "#FCF3A7"  # holiday
COLOR_TODAY = "#A7D9FD"    # current day
COLOR_WEEKEND = "#C9C9C9"  # weekend
COLOR_FUTURE = "#FFFFFF"   # future dates (outside semester)
COLOR_FUTURE_IN_SEM = "#C0C8F8"  #  future dates within semester


class AttendanceCalendar:
    """Google Calendar-style monthly attendance view"""
    
    def __init__(self, notebook, refresh_callback):
        self.notebook = notebook
        self.refresh_all_tabs = refresh_callback
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.selected_date = None
        self.calendar_frame = None
        self.subjects_panel = None
        self.day_buttons = {}
        self.check_vars = {}  # Store checkbox variables at class level
    
    def create(self):
        """Create the main tab with calendar and side panel"""
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(0, weight=3, minsize=700)  # Calendar area
        tab.columnconfigure(1, weight=1, minsize=300)  # Side panel
        tab.rowconfigure(1, weight=1)
        
        # Header with month navigation
        self.create_header(tab)
        
        # Calendar grid container
        self.create_calendar_container(tab)
        
        # Side panel for subjects
        self.create_side_panel(tab)
        
        # Legend
        self.create_legend(tab)
        
        # Initial render
        self.refresh()
        
        return tab
    
    def create_header(self, parent):
        """Create header with month navigation"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        ttk.Button(header_frame, text="◀ Prev", width=8, 
                  command=self.prev_month).pack(side=tk.LEFT, padx=5)
        
        self.month_label = ttk.Label(header_frame, text="", 
                                     font=("Segoe UI", 16, "bold"))
        self.month_label.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(header_frame, text="Next ▶", width=8, 
                  command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(header_frame, text="Today", width=8,
                  command=self.go_to_today).pack(side=tk.LEFT, padx=20)
        
        # Hint for right-click functionality
        hint_label = ttk.Label(header_frame, 
                              text="💡 Tip: Right-click any date to instantly mark entire day as absent",
                              foreground="#666666",
                              font=("Segoe UI", 10))
        hint_label.pack(side=tk.LEFT, padx=30)
    
    def create_calendar_container(self, parent):
        """Create scrollable calendar grid container"""
        calendar_container = ttk.Frame(parent)
        calendar_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Canvas with scrollbar
        canvas = tk.Canvas(calendar_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(calendar_container, orient="vertical", command=canvas.yview)
        self.calendar_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas_window = canvas.create_window((0, 0), window=self.calendar_frame, anchor="nw")
        
        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=event.width)
        
        self.calendar_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", configure_scroll)
        
        # Enable mouse wheel scrolling on calendar
        def _on_calendar_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_calendar_mousewheel)
        self.calendar_frame.bind("<MouseWheel>", _on_calendar_mousewheel)
    
    def create_side_panel(self, parent):
        """Create side panel for subject selection"""
        self.subjects_panel = ttk.LabelFrame(parent, text="Selected Date", padding=10)
        self.subjects_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)
        
        # Initial placeholder
        tk.Label(
            self.subjects_panel, 
            text="Click a date to view\nand mark attendance",
            font=("Segoe UI", 11), 
            foreground="gray"
        ).pack(expand=True, pady=50)
    
    def create_legend(self, parent):
        """Create color legend"""
        legend_frame = ttk.LabelFrame(parent, text="Legend", padding=10)
        legend_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        legend_items = [
            ("All Present", COLOR_PRESENT),
            ("Some Absent", COLOR_ABSENT),
            ("Completely Skipped", COLOR_SKIPPED),
            ("Holiday", COLOR_HOLIDAY),
            ("Today", COLOR_TODAY),
            ("Future (In Semester)", COLOR_FUTURE_IN_SEM),
            ("Sunday / Outside Semester", COLOR_FUTURE),
            ("Weekend (Sunday)", COLOR_WEEKEND)
        ]
        
        for idx, (label, color) in enumerate(legend_items):
            frame = ttk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=8)
            
            color_box = tk.Label(
                frame, text="  ", bg=color, 
                relief="solid", borderwidth=1, width=3
            )
            color_box.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(frame, text=label, font=("Segoe UI", 10)).pack(side=tk.LEFT)
    
    def prev_month(self):
        """Navigate to previous month"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.refresh()
    
    def next_month(self):
        """Navigate to next month"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.refresh()
    
    def go_to_today(self):
        """Jump to current month"""
        now = datetime.now()
        self.current_month = now.month
        self.current_year = now.year
        self.refresh()
    
    def on_date_clicked(self, date_str):
        """Handle date click - show subjects for that date"""
        app_data = get_app_data()
        
        # Check if date is in the future
        today = datetime.now().strftime("%Y-%m-%d")
        if date_str > today:
            messagebox.showinfo("Info", "Cannot mark attendance for future dates.\nYou can still mark holidays using the holiday button.")
            return
        
        # Validate semester dates
        semester_start = app_data.get("semester_start")
        semester_end = app_data.get("semester_end")
        if semester_start and semester_end:
            if not (semester_start <= date_str <= semester_end):
                messagebox.showinfo("Info", "Cannot mark attendance outside semester period")
                return
        
        # Get subjects for this day
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return
        
        day_name = date_obj.strftime("%A").upper()
        batch = app_data.get("batch", "B1/B3")
        subjects = get_subjects_for_day(day_name, batch)
        
        print(f"Date: {date_str}, Day: {day_name}, Batch: {batch}, Subjects: {subjects}")
        
        if not subjects:
            messagebox.showinfo("Info", "No classes scheduled on this day")
            self.clear_subjects_panel()
            return
        
        self.selected_date = date_str
        self.show_subjects_panel(date_str, subjects)
    
    def on_date_right_clicked(self, date_str):
        """Handle right-click on date - toggle between all absent and all present"""
        app_data = get_app_data()
        
        # Check if date is in the future - use date objects for accurate comparison
        today = date.today()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return
        
        if date_obj > today:
            messagebox.showinfo("Info", "Cannot mark attendance for future dates.\nYou can mark holidays, but not attendance.")
            return
        
        # Validate semester dates
        semester_start = app_data.get("semester_start")
        semester_end = app_data.get("semester_end")
        if semester_start and semester_end:
            if not (semester_start <= date_str <= semester_end):
                messagebox.showinfo("Info", "Cannot mark attendance outside semester period")
                return
        
        # Get subjects for this day
        day_name = date_obj.strftime("%A").upper()
        batch = app_data.get("batch", "B1/B3")
        subjects = get_subjects_for_day(day_name, batch)
        
        if not subjects:
            return
        
        # Check if ALL subjects (including multiple occurrences) are already absent
        all_absent = True
        for subject in subjects:
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if subject_data:
                absent_dates = subject_data.get("absent_dates", [])
                # For subjects with multiple classes, check if date appears correct number of times
                subject_count_on_day = subjects.count(subject)
                absent_count_for_date = absent_dates.count(date_str)
                if absent_count_for_date < subject_count_on_day:
                    all_absent = False
                    break
            else:
                all_absent = False
                break
        
        # Initialize skipped_days if not exists
        if "skipped_days" not in app_data:
            app_data["skipped_days"] = []
        
        # Check if this date is already a holiday (holidays take priority)
        existing_holidays = set(h.get("date", h.get("start", "")) for h in app_data.get("holidays", []))
        is_holiday = date_str in existing_holidays
        
        if all_absent:
            # Already completely skipped - make all present (remove ALL absences for this date)
            for subject in subjects:
                subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
                if subject_data:
                    # Remove ALL occurrences of this date (in case subject appears multiple times)
                    while date_str in subject_data.get("absent_dates", []):
                        subject_data["absent_dates"].remove(date_str)
            
            # Remove from skipped_days list (new format: {reason, date})
            app_data["skipped_days"] = [
                skipped for skipped in app_data["skipped_days"]
                if skipped.get("date", skipped.get("start", "")) != date_str
            ]
        else:
            # Check if this date is a holiday - if so, don't allow marking absent
            if is_holiday:
                messagebox.showinfo("Info", "This date is a holiday. Cannot mark as absent.")
                return
            
            # Check if already a skipped day
            existing_skipped = set(s.get("date", s.get("start", "")) for s in app_data.get("skipped_days", []))
            if date_str in existing_skipped:
                messagebox.showinfo("Info", "This date is already marked as skipped.")
                return
            
            # Not completely skipped - mark ALL occurrences of all subjects as absent
            for subject in subjects:
                subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
                if subject_data:
                    if "absent_dates" not in subject_data:
                        subject_data["absent_dates"] = []
                    # Add date (will be added once per occurrence in subjects list)
                    subject_data["absent_dates"].append(date_str)
            
            # Add to skipped_days list (new format: {reason, date})
            formatted_date = date_obj.strftime("%d %b %Y")
            app_data["skipped_days"].append({
                "reason": f"Right-click: {formatted_date}",
                "date": date_str
            })
        
        save_data()
        self.refresh()
        self.refresh_all_tabs()
    
    def show_subjects_panel(self, date_str, subjects):
        """Display subjects with checkboxes in side panel"""
        app_data = get_app_data()
        
        # Validate inputs
        if not subjects or not isinstance(subjects, list):
            self.clear_subjects_panel()
            return
        
        # Validate app_data has subjects
        if not app_data.get("subjects"):
            messagebox.showerror("Error", "No subjects found in app data. Please reconfigure in Setup tab.")
            self.clear_subjects_panel()
            return
        
        # Clear panel
        for widget in self.subjects_panel.winfo_children():
            widget.destroy()
        
        # Clear old checkbox variables
        self.check_vars.clear()
        
        # Header with date and close button
        header_frame = ttk.Frame(self.subjects_panel)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        date_display = date_obj.strftime("%B %d, %Y")
        day_name = date_obj.strftime("%A")
        
        date_label_frame = ttk.Frame(header_frame)
        date_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            date_label_frame, 
            text=date_display, 
            font=("Segoe UI", 12, "bold")
        ).pack(anchor=tk.W)
        
        tk.Label(
            date_label_frame, 
            text=day_name, 
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W)
        
        # Close button
        ttk.Button(
            header_frame, 
            text="✕", 
            width=3,
            command=self.clear_subjects_panel
        ).pack(side=tk.RIGHT)
        
        # Holiday toggle button
        is_holiday = self.is_holiday_date(date_str)
        holiday_text = "🏖️ Mark as Regular Day" if is_holiday else "🏖️ Mark as Holiday"
        
        ttk.Button(
            self.subjects_panel, 
            text=holiday_text, 
            command=lambda: self.toggle_holiday(date_str)
        ).pack(pady=5)
        
        ttk.Separator(self.subjects_panel, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Subjects section
        tk.Label(
            self.subjects_panel, 
            text="Classes:", 
            font=("Segoe UI", 11, "bold")
        ).pack(pady=5)
        
        tk.Label(
            self.subjects_panel, 
            text="Uncheck to mark ABSENT", 
            font=("Segoe UI", 10), 
            foreground="gray"
        ).pack(pady=2)
        
        # Scrollable subjects list
        subjects_container = ttk.Frame(self.subjects_panel)
        subjects_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        subjects_canvas = tk.Canvas(
            subjects_container, 
            bg="white", 
            highlightthickness=0, 
            height=300
        )
        subjects_scrollbar = ttk.Scrollbar(
            subjects_container, 
            orient="vertical", 
            command=subjects_canvas.yview
        )
        subjects_frame = ttk.Frame(subjects_canvas)
        
        subjects_canvas.configure(yscrollcommand=subjects_scrollbar.set)
        subjects_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        subjects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas_frame = subjects_canvas.create_window((0, 0), window=subjects_frame, anchor="nw")
        
        def configure_subjects_scroll(event):
            subjects_canvas.configure(scrollregion=subjects_canvas.bbox("all"))
            subjects_canvas.itemconfig(canvas_frame, width=event.width)
        
        subjects_frame.bind("<Configure>", configure_subjects_scroll)
        subjects_canvas.bind("<Configure>", configure_subjects_scroll)
        
        # Enable mouse wheel scrolling on subjects panel
        def _on_mousewheel(event):
            subjects_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        subjects_canvas.bind("<MouseWheel>", _on_mousewheel)
        subjects_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Create checkboxes for each subject (with occurrence tracking for duplicates)
        # Count occurrences of each subject and track absent counts
        subject_occurrence_count = {}
        subject_absent_count = {}  # Track how many absences already accounted for
        
        for idx, subject in enumerate(subjects):
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            
            # Track occurrence number for subjects that appear multiple times
            occurrence = subject_occurrence_count.get(subject, 0) + 1
            subject_occurrence_count[subject] = occurrence
            
            # Create unique key for subjects that appear multiple times
            subject_key = f"{subject}__occurrence_{occurrence}" if subjects.count(subject) > 1 else subject
            
            # Check if currently marked absent
            # For subjects with multiple occurrences, we need to count how many times
            # this date appears in absent_dates and match against occurrences
            is_present = True
            if subject_data:
                absent_dates = subject_data.get("absent_dates", [])
                # Count total absences for this date
                total_absences_for_date = absent_dates.count(date_str)
                # How many have we already accounted for?
                already_counted = subject_absent_count.get(subject, 0)
                
                # This occurrence is absent if there are more absences than we've counted
                if already_counted < total_absences_for_date:
                    is_present = False
                    subject_absent_count[subject] = already_counted + 1
            
            # Create and store checkbox variable with unique key
            var = tk.BooleanVar(value=is_present)
            self.check_vars[subject_key] = var
            
            frame = ttk.Frame(subjects_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Show occurrence number if subject appears multiple times
            display_text = f"{subject} (Class #{occurrence})" if subjects.count(subject) > 1 else subject
            cb = ttk.Checkbutton(frame, text=display_text, variable=var)
            cb.pack(side=tk.LEFT)
            
            # Status indicator
            status = "✓" if is_present else "✗"
            color = "#28a745" if is_present else "#dc3545"
            
            tk.Label(
                frame, 
                text=status, 
                font=("Segoe UI", 12), 
                foreground=color
            ).pack(side=tk.RIGHT)
        
        # Save button at bottom
        save_frame = ttk.Frame(self.subjects_panel)
        save_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        ttk.Button(
            save_frame, 
            text="💾 Save Attendance", 
            command=lambda: self.save_attendance(date_str)
        ).pack(fill=tk.X)
    
    def save_attendance(self, date_str):
        """Save attendance for the selected date
        
        Also syncs with skipped_days list:
        - If ALL subjects are marked absent → add to skipped_days
        - If ANY subject is marked present → remove from skipped_days
        """
        app_data = get_app_data()
        
        # Initialize skipped_days if not exists
        if "skipped_days" not in app_data:
            app_data["skipped_days"] = []
        
        # Track if all subjects will be absent after save
        all_will_be_absent = True
        
        # Update absent_dates for each subject based on checkbox state
        # Handle subjects with multiple occurrences (e.g., "Physics Lab__occurrence_1")
        for subject_key, var in self.check_vars.items():
            # Extract actual subject name (remove occurrence suffix if present)
            subject_name = subject_key.split("__occurrence_")[0] if "__occurrence_" in subject_key else subject_key
            
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject_name), None)
            if not subject_data:
                continue
            
            if "absent_dates" not in subject_data:
                subject_data["absent_dates"] = []
            
            is_present = var.get()
            
            if is_present:
                all_will_be_absent = False
            
            if not is_present:
                # Mark as absent - add to absent_dates (can have multiple entries for same date)
                subject_data["absent_dates"].append(date_str)
            else:
                # Mark as present - remove ONE occurrence from absent_dates if exists
                if date_str in subject_data["absent_dates"]:
                    subject_data["absent_dates"].remove(date_str)
        
        # Sync with skipped_days list
        # Check if this date is already in skipped_days
        existing_skipped_dates = set(
            s.get("date", s.get("start", "")) for s in app_data.get("skipped_days", [])
        )
        is_already_skipped = date_str in existing_skipped_dates
        
        if all_will_be_absent and not is_already_skipped:
            # All subjects absent - add to skipped_days
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d %b %Y")
                app_data["skipped_days"].append({
                    "reason": f"All absent: {formatted_date}",
                    "date": date_str
                })
            except ValueError:
                pass
        elif not all_will_be_absent and is_already_skipped:
            # Some subjects now present - remove from skipped_days
            app_data["skipped_days"] = [
                s for s in app_data["skipped_days"]
                if s.get("date", s.get("start", "")) != date_str
            ]
        
        # Save to file
        save_data()
        
        # Refresh all displays
        self.refresh()
        self.refresh_all_tabs()
        
        messagebox.showinfo("Success", "Attendance saved successfully!")
    
    def clear_subjects_panel(self):
        """Clear the subjects panel and show placeholder"""
        self.selected_date = None
        self.check_vars.clear()
        
        for widget in self.subjects_panel.winfo_children():
            widget.destroy()
        
        # Show placeholder text
        tk.Label(
            self.subjects_panel, 
            text="Click a date to view\nand mark attendance",
            font=("Segoe UI", 11), 
            foreground="gray"
        ).pack(expand=True, pady=50)
    
    def toggle_holiday(self, date_str):
        """Toggle a date as holiday"""
        app_data = get_app_data()
        holidays = app_data.get("holidays", [])
        
        # Check if date is already a holiday (support both old and new format)
        existing_idx = None
        for idx, holiday in enumerate(holidays):
            # New format: {name, date} or Old format: {name, start, end}
            holiday_date = holiday.get("date", holiday.get("start", ""))
            if holiday_date == date_str:
                existing_idx = idx
                break
        
        if existing_idx is not None:
            # Remove holiday
            del holidays[existing_idx]
            messagebox.showinfo("Updated", "Date marked as regular day")
        else:
            # Validate date is within semester when adding
            semester_start = app_data.get("semester_start")
            semester_end = app_data.get("semester_end")
            if semester_start and semester_end:
                if not (semester_start <= date_str <= semester_end):
                    messagebox.showerror(
                        "Error",
                        f"Cannot mark holiday outside semester period.\n"
                        f"Semester: {semester_start} to {semester_end}"
                    )
                    return
            
            # Add as single-day holiday (new format)
            holidays.append({
                "name": "Holiday",
                "date": date_str
            })
            messagebox.showinfo("Updated", "Date marked as holiday")
        
        save_data()
        self.refresh()
        self.refresh_all_tabs()
    
    def is_holiday_date(self, date_str):
        """Check if a date is marked as holiday"""
        app_data = get_app_data()
        holidays = app_data.get("holidays", [])
        
        for holiday in holidays:
            # Support both new format {name, date} and old format {name, start, end}
            if "date" in holiday:
                if holiday["date"] == date_str:
                    return True
            elif "start" in holiday and "end" in holiday:
                if holiday["start"] <= date_str <= holiday["end"]:
                    return True
        return False
    
    def get_day_status(self, date_str):
        """Get the status of a day (present/absent/skipped/holiday/no_class)"""
        app_data = get_app_data()
        
        # Check if date is within semester range
        semester_start = app_data.get("semester_start")
        semester_end = app_data.get("semester_end")
        if semester_start and semester_end:
            if not (semester_start <= date_str <= semester_end):
                return "no_class"  # Outside semester range
        
        if self.is_holiday_date(date_str):
            return "holiday"
        
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A").upper()
        batch = app_data.get("batch", "B1/B3")
        subjects = get_subjects_for_day(day_name, batch)
        
        if not subjects:
            return "no_class"
        
        # Check if ALL subjects are absent (completely skipped day)
        # For subjects with multiple classes per day, need to check count matches
        all_absent = True
        has_absent = False
        for subject in subjects:
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if subject_data:
                absent_dates = subject_data.get("absent_dates", [])
                # Count how many times this subject appears on this day
                subject_count_on_day = subjects.count(subject)
                # Count how many times this date appears in absent_dates for this subject
                absent_count_for_date = absent_dates.count(date_str)
                
                if absent_count_for_date > 0:
                    has_absent = True
                # Only considered fully absent if ALL occurrences are marked absent
                if absent_count_for_date < subject_count_on_day:
                    all_absent = False
            else:
                all_absent = False
        
        if all_absent and has_absent:
            return "skipped"  # All subjects absent
        
        return "absent" if has_absent else "present"
    
    def draw_calendar(self):
        """Draw the monthly calendar grid"""
        # Defer widget destruction for smoother rendering
        self.calendar_frame.update_idletasks()
        
        # Clear existing calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        self.day_buttons = {}
        
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        # Day headers (Mon-Sun)
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days_of_week):
            label = tk.Label(
                self.calendar_frame, 
                text=day, 
                font=("Segoe UI", 10, "bold"),
                bg="#ECEFF1", 
                relief="solid", 
                borderwidth=1,
                padx=10,
                pady=8
            )
            label.grid(row=0, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
            self.calendar_frame.columnconfigure(col, weight=1, minsize=80)  # Responsive columns
        
        # Get calendar data for the month
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now().date()
        
        # Configure rows to be responsive (header row + up to 6 week rows)
        for row in range(7):
            self.calendar_frame.rowconfigure(row, weight=1, minsize=40)
        
        # Draw date cells
        for week_idx, week in enumerate(cal, start=1):
            for day_idx, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in this month
                    label = tk.Label(
                        self.calendar_frame, 
                        text="", 
                        bg="#FAFAFA",
                        relief="solid", 
                        borderwidth=1
                    )
                    label.grid(
                        row=week_idx, 
                        column=day_idx, 
                        sticky=(tk.W, tk.E, tk.N, tk.S),
                        padx=1, 
                        pady=1
                    )
                    continue
                
                # Create date object
                date_obj = date(self.current_year, self.current_month, day)
                date_str = date_obj.strftime("%Y-%m-%d")
                
                # Determine background color based on status
                bg_color = COLOR_FUTURE
                
                if date_obj == today:
                    bg_color = COLOR_TODAY
                elif day_idx == 6:  # Sunday only (Saturday has classes)
                    bg_color = COLOR_WEEKEND
                elif date_obj > today:
                    # Future dates - different colors for in-semester vs outside
                    app_data = get_app_data()
                    semester_start = app_data.get("semester_start")
                    semester_end = app_data.get("semester_end")
                    if semester_start and semester_end and semester_start <= date_str <= semester_end:
                        # Future date within semester - use distinct color
                        if self.is_holiday_date(date_str):
                            bg_color = COLOR_HOLIDAY  # Show holidays even in future
                        else:
                            bg_color = COLOR_FUTURE_IN_SEM  # Light indigo for future dates in semester
                    else:
                        bg_color = COLOR_FUTURE  # White for outside semester
                else:
                    # Past dates - show actual status
                    status = self.get_day_status(date_str)
                    if status == "no_class":
                        bg_color = COLOR_FUTURE  # Outside semester or no classes
                    elif status == "holiday":
                        bg_color = COLOR_HOLIDAY
                    elif status == "skipped":
                        bg_color = COLOR_SKIPPED  # All classes absent
                    elif status == "absent":
                        bg_color = COLOR_ABSENT
                    elif status == "present":
                        bg_color = COLOR_PRESENT
                
                # Create clickable button for the date
                btn = tk.Button(
                    self.calendar_frame, 
                    text=str(day),
                    font=("Segoe UI", 11, "bold" if date_obj == today else "normal"),
                    bg=bg_color, 
                    relief="solid", 
                    borderwidth=1,
                    cursor="hand2",
                    padx=10,
                    pady=20,
                    command=lambda d=date_str: self.on_date_clicked(d)
                )
                btn.grid(
                    row=week_idx, 
                    column=day_idx, 
                    sticky=(tk.W, tk.E, tk.N, tk.S),
                    padx=1, 
                    pady=1
                )
                
                # Add right-click binding
                btn.bind("<Button-3>", lambda e, d=date_str: self.on_date_right_clicked(d))
                
                self.day_buttons[date_str] = btn
    
    def refresh(self):
        """Refresh the entire calendar display"""
        self.draw_calendar()
        
        # If a date is currently selected and it's in the current month, refresh the panel
        if self.selected_date:
            date_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
            if date_obj.month == self.current_month and date_obj.year == self.current_year:
                app_data = get_app_data()
                day_name = date_obj.strftime("%A").upper()
                batch = app_data.get("batch", "B1/B3")
                subjects = get_subjects_for_day(day_name, batch)
                if subjects:
                    self.show_subjects_panel(self.selected_date, subjects)