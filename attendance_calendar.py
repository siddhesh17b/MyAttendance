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
COLOR_PRESENT = "#E8F5E9"  # Light green - all classes present
COLOR_ABSENT = "#FFEBEE"   # Light red - some classes absent  
COLOR_HOLIDAY = "#FFF9C4"  # Light yellow - holiday
COLOR_TODAY = "#E3F2FD"    # Light blue - current day
COLOR_WEEKEND = "#F5F5F5"  # Light gray - weekend
COLOR_FUTURE = "#FAFAFA"   # Very light gray - future dates


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
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=1)
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
        
        legends = [
            ("All Present", COLOR_PRESENT),
            ("Some Absent", COLOR_ABSENT),
            ("Holiday", COLOR_HOLIDAY),
            ("Today", COLOR_TODAY),
            ("Weekend/Future", COLOR_WEEKEND)
        ]
        
        for idx, (label, color) in enumerate(legends):
            frame = ttk.Frame(legend_frame)
            frame.pack(side=tk.LEFT, padx=10)
            
            color_box = tk.Label(
                frame, text="  ", bg=color, 
                relief="solid", borderwidth=1, width=3
            )
            color_box.pack(side=tk.LEFT, padx=3)
            
            ttk.Label(frame, text=label, font=("Segoe UI", 9)).pack(side=tk.LEFT)
    
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
        """Handle left-click on date - show subjects panel"""
        app_data = get_app_data()
        
        # Validate semester dates
        if not app_data.get("semester_start") or not app_data.get("semester_end"):
            messagebox.showwarning("Warning", "Please set semester dates in Setup tab first")
            return
        
        if not (app_data["semester_start"] <= date_str <= app_data["semester_end"]):
            messagebox.showinfo("Info", "Selected date is outside semester period")
            return
        
        # Check if future date
        today = datetime.now().strftime("%Y-%m-%d")
        if date_str > today:
            messagebox.showinfo("Info", "Cannot mark attendance for future dates")
            return
        
        # Get subjects for this day
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
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
        """Handle right-click on date - mark all classes as absent"""
        app_data = get_app_data()
        
        # Get subjects for this day
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A").upper()
        batch = app_data.get("batch", "B1/B3")
        subjects = get_subjects_for_day(day_name, batch)
        
        if not subjects:
            return
        
        # Mark all subjects as absent for this date
        for subject in subjects:
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if subject_data:
                if "absent_dates" not in subject_data:
                    subject_data["absent_dates"] = []
                if date_str not in subject_data["absent_dates"]:
                    subject_data["absent_dates"].append(date_str)
        
        save_data()
        self.refresh()
        self.refresh_all_tabs()
        messagebox.showinfo("Success", f"Marked all classes as absent for {date_str}")
    
    def show_subjects_panel(self, date_str, subjects):
        """Display subjects with checkboxes in side panel"""
        app_data = get_app_data()
        
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
            font=("Segoe UI", 9), 
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
        
        # Create checkboxes for each subject
        for subject in subjects:
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            
            # Check if currently marked absent
            is_present = True
            if subject_data and date_str in subject_data.get("absent_dates", []):
                is_present = False
            
            # Create and store checkbox variable
            var = tk.BooleanVar(value=is_present)
            self.check_vars[subject] = var
            
            frame = ttk.Frame(subjects_frame)
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            cb = ttk.Checkbutton(frame, text=subject, variable=var)
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
        """Save attendance for the selected date"""
        app_data = get_app_data()
        
        # Update absent_dates for each subject based on checkbox state
        for subject, var in self.check_vars.items():
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if not subject_data:
                continue
            
            if "absent_dates" not in subject_data:
                subject_data["absent_dates"] = []
            
            is_present = var.get()
            
            if not is_present:
                # Mark as absent - add to absent_dates if not already there
                if date_str not in subject_data["absent_dates"]:
                    subject_data["absent_dates"].append(date_str)
            else:
                # Mark as present - remove from absent_dates if exists
                if date_str in subject_data["absent_dates"]:
                    subject_data["absent_dates"].remove(date_str)
        
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
        
        # Check if date is already a holiday
        existing_holiday = None
        for holiday in holidays:
            if holiday["start"] == date_str and holiday["end"] == date_str:
                existing_holiday = holiday
                break
        
        if existing_holiday:
            # Remove holiday
            holidays.remove(existing_holiday)
            messagebox.showinfo("Updated", "Date marked as regular day")
        else:
            # Add as single-day holiday
            holidays.append({
                "start": date_str,
                "end": date_str,
                "name": "Holiday"
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
            start = holiday["start"]
            end = holiday["end"]
            if start <= date_str <= end:
                return True
        return False
    
    def get_day_status(self, date_str):
        """Get the status of a day (present/absent/holiday/no_class)"""
        if self.is_holiday_date(date_str):
            return "holiday"
        
        app_data = get_app_data()
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A").upper()
        batch = app_data.get("batch", "B1/B3")
        subjects = get_subjects_for_day(day_name, batch)
        
        if not subjects:
            return "no_class"
        
        # Check if any subject has absence on this date
        has_absent = False
        for subject in subjects:
            subject_data = next((s for s in app_data["subjects"] if s["name"] == subject), None)
            if subject_data and date_str in subject_data.get("absent_dates", []):
                has_absent = True
                break
        
        return "absent" if has_absent else "present"
    
    def draw_calendar(self):
        """Draw the monthly calendar grid"""
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
                width=15, 
                height=2
            )
            label.grid(row=0, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
        
        # Get calendar data for the month
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = datetime.now().date()
        
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
                elif day_idx >= 5:  # Saturday/Sunday
                    bg_color = COLOR_WEEKEND
                elif date_obj <= today:
                    status = self.get_day_status(date_str)
                    if status == "holiday":
                        bg_color = COLOR_HOLIDAY
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
                    width=15, 
                    height=5,
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
