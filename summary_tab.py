"""
Summary Dashboard - Enhanced attendance statistics and reporting

Features:
- Enhanced stats cards with visual progress indicators
- Table with progress bars and color-coded rows
- Sortable columns by clicking headers
- Visual warning indicators for at-risk subjects
- Export report functionality
- Manual override via double-click

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from data_manager import get_app_data, count_subject_classes
from calculations import (
    calculate_weeks_elapsed, 
    calculate_total_classes, 
    calculate_attendance, 
    calculate_safe_skip, 
    get_attendance_status
)

# Enhanced color scheme
COLOR_SAFE = "#28a745"        # Green - safe attendance (≥75%)
COLOR_RISK = "#dc3545"        # Red - at risk (<75%)
COLOR_WARNING = "#ffc107"     # Yellow - warning (75-80%)
COLOR_INFO = "#007bff"        # Blue - informational
COLOR_BG_SAFE = "#d4edda"     # Light green background
COLOR_BG_WARNING = "#fff3cd"  # Light yellow background
COLOR_BG_RISK = "#f8d7da"     # Light red background
COLOR_BG_DARK = "#e9ecef"     # Light gray background
COLOR_BG_CARD = "#ffffff"     # White card background


class SummaryTab:
    """Enhanced dashboard with visual attendance statistics"""
    def __init__(self, notebook, refresh_callback):
        self.notebook = notebook
        self.refresh_all_tabs = refresh_callback
        self.stats_frame = None
        self.summary_tree = None
        self.canvas_frame = None
        self.sort_column = None
        self.sort_reverse = False
    
    def create(self):
        """Create the enhanced summary dashboard tab"""
        tab = ttk.Frame(self.notebook)
        
        # Main container with scrollbar
        main_container = tk.Frame(tab)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.canvas_frame = tk.Frame(canvas)
        
        # Fill full width instead of centering
        canvas_window = canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")
        
        def _configure_canvas(event):
            # Update scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make frame fill the entire canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", _configure_canvas)
        self.canvas_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # GitHub link at bottom
        github_frame = ttk.Frame(tab)
        github_frame.pack(side="bottom", fill=tk.X, pady=(5, 5))
        
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
        
        # Header with icon
        header_frame = tk.Frame(self.canvas_frame, bg="#ffffff")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            header_frame, 
            text="📊 Attendance Dashboard", 
            font=("Segoe UI", 20, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(pady=15)
        
        # Stats cards frame (enhanced)
        self.stats_frame = tk.Frame(self.canvas_frame, bg="#f8f9fa")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))
        
        # Table frame with border
        table_container = tk.Frame(self.canvas_frame, bg="#dee2e6", bd=1, relief=tk.SOLID)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Table label
        tk.Label(
            table_container,
            text="Subject-wise Attendance Details",
            font=("Segoe UI", 13, "bold"),
            bg="#ffffff",
            fg="#495057",
            anchor=tk.W
        ).pack(fill=tk.X, padx=2, pady=(2, 5))
        
        # Summary table with enhanced styling
        columns = ("Subject", "Attended", "Total", "Remaining", "Percentage", "Progress", "Status", "Skip", "Action")
        self.summary_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)
        
        # Configure larger font for treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        # Configure column headers with sort functionality
        column_configs = {
            "Subject": (180, "Subject Name", tk.W),
            "Attended": (90, "Present", tk.CENTER),
            "Total": (90, "Total", tk.CENTER),
            "Remaining": (90, "Remaining", tk.CENTER),
            "Percentage": (100, "Attendance", tk.CENTER),
            "Progress": (160, "Visual Progress", tk.CENTER),
            "Status": (110, "Status", tk.CENTER),
            "Skip": (90, "Can Skip", tk.CENTER),
            "Action": (120, "Action", tk.CENTER)
        }
        
        for col, (width, heading, anchor) in column_configs.items():
            self.summary_tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.summary_tree.column(col, width=width, anchor=anchor)
        
        # Scrollbar for table
        tree_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.summary_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 2), padx=(0, 2))
        
        # Enable mouse wheel scrolling on treeview
        def _on_tree_mousewheel(event):
            self.summary_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        self.summary_tree.bind("<MouseWheel>", _on_tree_mousewheel)
        
        # Bind double-click to open override dialog
        self.summary_tree.bind("<Double-Button-1>", self.on_row_double_click)
        
        # Tips and actions frame
        action_frame = tk.Frame(self.canvas_frame, bg="#f8f9fa")
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Info labels
        tips_frame = tk.Frame(action_frame, bg="#f8f9fa")
        tips_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            tips_frame,
            text="💡 Double-click any row to manually override attendance data",
            font=("Segoe UI", 10),
            foreground="#6c757d",
            bg="#f8f9fa",
            anchor=tk.W
        ).pack(anchor=tk.W, pady=2)
        
        tk.Label(
            tips_frame,
            text="📌 Click column headers to sort • Color coding: 🟢 Safe • 🟡 Warning • 🔴 At Risk",
            font=("Segoe UI", 10),
            foreground="#6c757d",
            bg="#f8f9fa",
            anchor=tk.W
        ).pack(anchor=tk.W, pady=2)
        
        # Export button (enhanced)
        ttk.Button(
            action_frame, 
            text="📄 Export Report", 
            command=self.export_report
        ).pack(side=tk.RIGHT, padx=5)
        
        # Initial data load
        self.refresh()
        
        return tab
    
    def sort_by_column(self, col):
        """Sort treeview by column when header clicked"""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        
        # Get all items
        items = [(self.summary_tree.set(item, col), item) for item in self.summary_tree.get_children('')]
        
        # Sort based on column type
        if col in ("Attended", "Total", "Remaining", "Skip"):
            items.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=self.sort_reverse)
        elif col == "Percentage":
            items.sort(key=lambda x: float(x[0].strip('%')) if '%' in x[0] else 0, reverse=self.sort_reverse)
        else:
            items.sort(reverse=self.sort_reverse)
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.summary_tree.move(item, '', index)
    
    def create_progress_bar(self, percentage):
        """Create visual progress bar representation"""
        bar_length = 10
        filled = int((percentage / 100) * bar_length)
        
        if percentage >= 85:
            symbol = "█"
            color = "🟢"
        elif percentage >= 75:
            symbol = "█"
            color = "🟡"
        else:
            symbol = "█"
            color = "🔴"
        
        bar = symbol * filled + "░" * (bar_length - filled)
        return f"{color} {bar}"
    
    def refresh(self):
        """Refresh summary display with enhanced visualizations"""
        app_data = get_app_data()
        
        # Optimize UI updates
        self.summary_tree.update_idletasks()
        
        # Clear existing items
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        if not app_data.get("semester_start"):
            return
        
        # Calculate metrics
        total_attendance_pct = 0
        at_risk_count = 0
        warning_count = 0
        safe_count = 0
        
        # CRITICAL: Use TODAY as end date, not semester end
        # This ensures future dates within semester are NOT counted in attendance
        today = datetime.now().strftime("%Y-%m-%d")
        semester_end = app_data.get("semester_end")
        
        # Calculate weeks only up to TODAY (ignore future dates)
        calculation_end_date = today
        if semester_end and today > semester_end:
            # If semester already ended, use semester end date
            calculation_end_date = semester_end
        
        weeks = calculate_weeks_elapsed(
            app_data["semester_start"],
            calculation_end_date,
            app_data.get("holidays", [])
        )
        
        # Calculate remaining weeks till semester end
        total_weeks = 0
        remaining_weeks = 0
        if semester_end:
            total_weeks = calculate_weeks_elapsed(
                app_data["semester_start"],
                semester_end,
                app_data.get("holidays", [])
            )
            if today <= semester_end:
                remaining_weeks = total_weeks - weeks
            # else remaining_weeks = 0 (semester already ended)
        
        subject_data_list = []
        
        for subject_data in app_data.get("subjects", []):
            name = subject_data["name"]
            
            # Check if manual override exists
            if subject_data.get("attendance_override") is not None:
                override_data = subject_data["attendance_override"]
                present = override_data["attended"]
                total = override_data["total"]
                action_text = "📝 Manual"
            else:
                # Calculate total classes using ACCURATE day-by-day counting
                # This counts actual occurrences of the subject's scheduled days
                # instead of simple weekly_count × weeks estimation
                if subject_data.get("total_override") is not None:
                    total = subject_data["total_override"]
                else:
                    batch = app_data.get("batch", "")
                    holidays = app_data.get("holidays", [])
                    total = count_subject_classes(
                        name, 
                        batch, 
                        app_data["semester_start"], 
                        calculation_end_date, 
                        holidays
                    )
                
                # Calculate present classes (total - absent)
                # CRITICAL: Only count absences up to TODAY (ignore future dates)
                # Exclude dates that fall on holidays from absent count
                from calculations import parse_date, is_date_in_holidays
                all_absent_dates = subject_data.get("absent_dates", [])
                absent_count = 0
                holidays = app_data.get("holidays", [])
                for date_str in all_absent_dates:
                    # Ignore future dates - only count past absences
                    if date_str > today:
                        continue
                    date_obj = parse_date(date_str)
                    if date_obj and not is_date_in_holidays(date_obj, holidays):
                        absent_count += 1
                
                present = max(0, total - absent_count)
                action_text = "✏️ Edit"
            
            attendance_pct = calculate_attendance(present, total)
            safe_skip = calculate_safe_skip(present, total)
            status, color = get_attendance_status(attendance_pct)
            
            # Create progress bar
            progress_bar = self.create_progress_bar(attendance_pct)
            
            # Determine status icon and category
            if attendance_pct >= 85:
                status_icon = "🟢 Excellent"
                tag = "safe"
                safe_count += 1
            elif attendance_pct >= 75:
                status_icon = "🟡 Safe"
                tag = "warning"
                warning_count += 1
            else:
                status_icon = "🔴 At Risk"
                tag = "risk"
                at_risk_count += 1
            
            total_attendance_pct += attendance_pct
            
            # Calculate remaining classes till semester end using accurate counting
            # Count from tomorrow to semester end
            if semester_end and today < semester_end:
                from datetime import timedelta
                tomorrow = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                remaining_classes = count_subject_classes(
                    name,
                    app_data.get("batch", ""),
                    tomorrow,
                    semester_end,
                    app_data.get("holidays", [])
                )
            else:
                remaining_classes = 0
            
            item = self.summary_tree.insert(
                "", tk.END,
                values=(name, present, total, remaining_classes, f"{attendance_pct:.1f}%", progress_bar, status_icon, safe_skip, action_text)
            )
            
            self.summary_tree.item(item, tags=(tag,))
            subject_data_list.append((name, attendance_pct, present, total))
        
        # Configure tags with background colors
        self.summary_tree.tag_configure("safe", background=COLOR_BG_SAFE, foreground="#155724")
        self.summary_tree.tag_configure("warning", background=COLOR_BG_WARNING, foreground="#856404")
        self.summary_tree.tag_configure("risk", background=COLOR_BG_RISK, foreground="#721c24")
        
        # Display enhanced stats cards
        subjects_list = app_data.get("subjects", [])
        num_subjects = len(subjects_list)
        avg_attendance = total_attendance_pct / num_subjects if num_subjects > 0 else 0
        
        # Determine average color
        if avg_attendance >= 85:
            avg_color = COLOR_SAFE
        elif avg_attendance >= 75:
            avg_color = COLOR_WARNING
        else:
            avg_color = COLOR_RISK
        
        stats_info = [
            ("📚", "Total Subjects", num_subjects, COLOR_INFO, "#cce5ff"),
            ("📊", "Average", f"{avg_attendance:.1f}%", avg_color, self.get_bg_color(avg_attendance)),
            ("✅", "Excellent/Safe", safe_count + warning_count, COLOR_SAFE, COLOR_BG_SAFE),
            ("⚠️", "At Risk", at_risk_count, COLOR_RISK if at_risk_count > 0 else "#6c757d", COLOR_BG_RISK if at_risk_count > 0 else "#f8f9fa")
        ]
        
        for icon, label, value, text_color, bg_color in stats_info:
            self.create_stat_card(icon, label, value, text_color, bg_color)
    
    def get_bg_color(self, percentage):
        """Get background color based on percentage"""
        if percentage >= 85:
            return COLOR_BG_SAFE
        elif percentage >= 75:
            return COLOR_BG_WARNING
        else:
            return COLOR_BG_RISK
    
    def create_stat_card(self, icon, label, value, text_color, bg_color):
        """Create enhanced stat card with icon and styling"""
        # Card container with shadow effect
        card_container = tk.Frame(self.stats_frame, bg="#dee2e6", bd=1, relief=tk.SOLID)
        card_container.pack(side=tk.LEFT, expand=True, padx=8, pady=8)
        
        # Inner card
        card = tk.Frame(card_container, bg=bg_color)
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Icon
        tk.Label(
            card,
            text=icon,
            font=("Segoe UI", 28),
            bg=bg_color
        ).pack(pady=(15, 5))
        
        # Value
        tk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 26, "bold"),
            fg=text_color,
            bg=bg_color
        ).pack()
        
        # Label
        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 11),
            fg="#495057",
            bg=bg_color
        ).pack(pady=(5, 15))
    
    def export_report(self):
        """Export attendance report to text file"""
        app_data = get_app_data()
        
        if not app_data.get("subjects"):
            messagebox.showwarning("Warning", "No data to export")
            return
        
        try:
            filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w') as f:
                # Header
                f.write("=" * 70 + "\n")
                f.write("MYATTENDANCE - ATTENDANCE REPORT\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Batch: {app_data.get('batch', 'N/A')}\n")
                f.write(f"Semester: {app_data.get('semester_start', 'N/A')} to {app_data.get('semester_end', 'N/A')}\n\n")
                
                f.write("-" * 70 + "\n")
                f.write(f"{'Subject':<20} {'Present':>10} {'Total':>10} {'%':>8} {'Status':>10}\n")
                f.write("-" * 70 + "\n")
                
                end_date = datetime.now().strftime("%Y-%m-%d")
                if app_data.get("semester_end"):
                    end_date = min(end_date, app_data["semester_end"])
                
                weeks = calculate_weeks_elapsed(
                    app_data["semester_start"],
                    end_date,
                    app_data.get("holidays", [])
                )
                
                for subject_data in app_data.get("subjects", []):
                    name = subject_data["name"]
                    
                    # Check if manual override exists
                    if subject_data.get("attendance_override") is not None:
                        override_data = subject_data["attendance_override"]
                        present = override_data["attended"]
                        total = override_data["total"]
                    else:
                        if subject_data.get("total_override") is not None:
                            total = subject_data["total_override"]
                        else:
                            total = calculate_total_classes(subject_data["weekly_count"], weeks)
                        
                        # Exclude dates that fall on holidays from absent count
                        from calculations import parse_date, is_date_in_holidays
                        all_absent_dates = subject_data.get("absent_dates", [])
                        absent_count = 0
                        holidays = app_data.get("holidays", [])
                        for date_str in all_absent_dates:
                            date_obj = parse_date(date_str)
                            if date_obj and not is_date_in_holidays(date_obj, holidays):
                                absent_count += 1
                        
                        present = max(0, total - absent_count)
                    
                    attendance_pct = calculate_attendance(present, total)
                    status, _ = get_attendance_status(attendance_pct)
                    
                    f.write(f"{name:<20} {present:>10} {total:>10} {attendance_pct:>7.1f}% {status:>10}\n")
                
                f.write("-" * 70 + "\n")
            
            messagebox.showinfo("Success", f"Report exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def on_row_double_click(self, event):
        """Handle double-click on tree row to open override dialog"""
        selection = self.summary_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.summary_tree.item(item, "values")
        if not values:
            return
        
        subject_name = values[0]
        self.open_override_dialog(subject_name)
    
    def open_override_dialog(self, subject_name):
        """Open dialog to manually override attendance data"""
        from data_manager import get_app_data, save_data
        
        app_data = get_app_data()
        subject_data = None
        
        # Find the subject
        for subj in app_data.get("subjects", []):
            if subj["name"] == subject_name:
                subject_data = subj
                break
        
        if not subject_data:
            messagebox.showerror("Error", "Subject not found")
            return
        
        # Create dialog
        dialog = tk.Toplevel()
        dialog.title(f"Manual Override - {subject_name}")
        dialog.geometry("500x450")
        dialog.resizable(True, True)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        dialog.transient(self.notebook.master)
        dialog.grab_set()
        
        # Header
        tk.Label(
            dialog,
            text=f"📝 Manual Attendance Override",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text=f"Subject: {subject_name}",
            font=("Segoe UI", 11)
        ).pack(pady=5)
        
        # Calculate current values
        end_date = datetime.now().strftime("%Y-%m-%d")
        if app_data.get("semester_end"):
            end_date = min(end_date, app_data["semester_end"])
        
        weeks = calculate_weeks_elapsed(
            app_data["semester_start"],
            end_date,
            app_data.get("holidays", [])
        )
        
        # Check for existing override
        has_override = subject_data.get("attendance_override") is not None
        if has_override:
            current_attended = subject_data["attendance_override"]["attended"]
            current_total = subject_data["attendance_override"]["total"]
        else:
            if subject_data.get("total_override") is not None:
                current_total = subject_data["total_override"]
            else:
                current_total = calculate_total_classes(subject_data["weekly_count"], weeks)
            
            # Exclude dates that fall on holidays from absent count
            from calculations import parse_date, is_date_in_holidays
            all_absent_dates = subject_data.get("absent_dates", [])
            absent_count = 0
            holidays = app_data.get("holidays", [])
            for date_str in all_absent_dates:
                date_obj = parse_date(date_str)
                if date_obj and not is_date_in_holidays(date_obj, holidays):
                    absent_count += 1
            
            current_attended = max(0, current_total - absent_count)
        
        # Current data frame
        current_frame = tk.LabelFrame(dialog, text="📊 Current Data", font=("Segoe UI", 10, "bold"))
        current_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            current_frame,
            text=f"Attended: {current_attended} classes",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        tk.Label(
            current_frame,
            text=f"Total: {current_total} classes",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        current_pct = calculate_attendance(current_attended, current_total)
        status_color = COLOR_SAFE if current_pct >= 75 else COLOR_RISK
        
        tk.Label(
            current_frame,
            text=f"Attendance: {current_pct:.1f}%",
            font=("Segoe UI", 10, "bold"),
            foreground=status_color
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        if has_override:
            tk.Label(
                current_frame,
                text="⚠️ Manual override is active",
                font=("Segoe UI", 9),
                foreground="#ff9800"
            ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Override inputs frame
        input_frame = tk.LabelFrame(dialog, text="✏️ Override Attendance", font=("Segoe UI", 10, "bold"))
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Enter actual attendance data:",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Total classes input
        tk.Label(input_frame, text="Total Classes Held:", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=10, pady=(10, 0))
        total_entry = tk.Entry(input_frame, font=("Segoe UI", 10), width=15)
        total_entry.insert(0, str(current_total))
        total_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Attended classes input
        tk.Label(input_frame, text="Classes Attended:", font=("Segoe UI", 9)).pack(anchor=tk.W, padx=10, pady=(10, 0))
        attended_entry = tk.Entry(input_frame, font=("Segoe UI", 10), width=15)
        attended_entry.insert(0, str(current_attended))
        attended_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Info label
        tk.Label(
            dialog,
            text="💡 Use this when actual attendance differs from timetable\n(cancellations, rescheduling, extra classes, etc.)",
            font=("Arial", 8),
            foreground="#6c757d",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Buttons frame
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        def save_override():
            try:
                total = int(total_entry.get())
                attended = int(attended_entry.get())
                
                if total < 0 or attended < 0:
                    messagebox.showerror("Error", "Values must be non-negative")
                    return
                
                if attended > total:
                    messagebox.showerror("Error", "Attended cannot be greater than total")
                    return
                
                # Save override
                subject_data["attendance_override"] = {
                    "total": total,
                    "attended": attended
                }
                
                save_data()
                self.refresh_all_tabs()
                dialog.destroy()
                messagebox.showinfo("Success", f"Manual override applied for {subject_name}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        def clear_override():
            if not has_override:
                messagebox.showinfo("Info", "No override exists for this subject")
                return
            
            if messagebox.askyesno("Confirm", "Remove manual override and use calculated attendance?"):
                subject_data["attendance_override"] = None
                save_data()
                self.refresh_all_tabs()
                dialog.destroy()
                messagebox.showinfo("Success", f"Manual override removed for {subject_name}")
        
        ttk.Button(btn_frame, text="💾 Save Override", command=save_override).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Clear Override", command=clear_override).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
