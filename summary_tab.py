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
from tkinter import ttk
from datetime import datetime

from data_manager import get_app_data, count_subject_classes
from modern_dialogs import messagebox
from calculations import (
    calculate_attendance, 
    calculate_safe_skip, 
    get_attendance_status,
    get_subject_status,
    get_overall_status,
    SUBJECT_THRESHOLD,
    OVERALL_THRESHOLD
)

# Enhanced color scheme
COLOR_SAFE = "#28a745"        # Green - excellent attendance (≥75% subject / ≥85% overall)
COLOR_RISK = "#dc3545"        # Red - at risk (<60% subject / <75% overall)
COLOR_WARNING = "#ffc107"     # Yellow - safe but needs attention (60-75% subject / 75-85% overall)
COLOR_INFO = "#007bff"        # Blue - informational
COLOR_BG_SAFE = "#d4edda"     # Light green background
COLOR_BG_WARNING = "#fff3cd"  # Light yellow background
COLOR_BG_RISK = "#f8d7da"     # Light red background
COLOR_BG_DARK = "#ffffff"     # White background for modern look
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
        self.semester_progress_frame = None
        self.details_panel = None
        self.subject_data_cache = {}  # Cache for quick lookup
        self.overall_warning_frame = None  # Warning for overall attendance <75%
    
    def create(self):
        """Create the enhanced summary dashboard tab"""
        tab = ttk.Frame(self.notebook)
        
        # Main container with scrollbar
        main_container = tk.Frame(tab, bg='#ffffff')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container, highlightthickness=0, bg='#ffffff')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.canvas_frame = tk.Frame(canvas, bg='#ffffff')
        
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
        
        # Store canvas reference for mousewheel management
        self.main_canvas = canvas
        
        # Mouse wheel scrolling for main dashboard
        def _on_canvas_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_canvas_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_canvas_mousewheel)
        
        def _unbind_canvas_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Store these for use by table area
        self._bind_canvas_scroll = _bind_canvas_mousewheel
        self._unbind_canvas_scroll = _unbind_canvas_mousewheel
        
        # Bind to canvas to capture mouse entering/leaving
        canvas.bind("<Enter>", _bind_canvas_mousewheel)
        canvas.bind("<Leave>", _unbind_canvas_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # GitHub link at bottom
        github_frame = ttk.Frame(tab)
        github_frame.pack(side="bottom", fill=tk.X, pady=(5, 5))
        
        github_label = tk.Label(
            github_frame,
            text="Made by Siddhesh Bisen | GitHub: https://github.com/siddhesh17b",
            font=("Segoe UI", 10),
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
        
        # Semester Progress Bar Section
        self.semester_progress_frame = tk.Frame(self.canvas_frame, bg="#ffffff")
        self.semester_progress_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Stats cards frame (enhanced)
        self.stats_frame = tk.Frame(self.canvas_frame, bg="#f8f9fa")
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))
        
        # Table frame with border
        table_container = tk.Frame(self.canvas_frame, bg="#dee2e6", bd=1, relief=tk.SOLID)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create a horizontal split: table on left, details panel on right
        # Use grid for better responsive control
        table_split = tk.Frame(table_container, bg="#ffffff")
        table_split.pack(fill=tk.BOTH, expand=True)
        table_split.columnconfigure(0, weight=3)  # Table gets 3x space
        table_split.columnconfigure(1, weight=1, minsize=280)  # Details panel min 280px
        table_split.rowconfigure(0, weight=1)
        
        # Left side: Table
        table_left = tk.Frame(table_split, bg="#ffffff")
        table_left.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Table label
        tk.Label(
            table_left,
            text="Subject-wise Attendance Details",
            font=("Segoe UI", 13, "bold"),
            bg="#ffffff",
            fg="#495057",
            anchor=tk.W
        ).pack(fill=tk.X, padx=2, pady=(2, 5))
        
        # Summary table with enhanced styling
        columns = ("Subject", "Attended", "Total", "Remaining", "Percentage", "Progress", "Status", "Skip", "Action")
        self.summary_tree = ttk.Treeview(table_left, columns=columns, show="headings", height=12)
        
        # Configure larger font for treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        # Configure column headers with sort functionality
        # Use minwidth for responsiveness - columns can grow but not shrink below min
        column_configs = {
            "Subject": (180, 120, "Subject Name", tk.W),
            "Attended": (80, 60, "Present", tk.CENTER),
            "Total": (80, 60, "Total", tk.CENTER),
            "Remaining": (80, 60, "Remaining", tk.CENTER),
            "Percentage": (90, 70, "Attendance", tk.CENTER),
            "Progress": (140, 100, "Visual Progress", tk.CENTER),
            "Status": (100, 80, "Status", tk.CENTER),
            "Skip": (80, 60, "Can Skip", tk.CENTER),
            "Action": (100, 80, "Action", tk.CENTER)
        }
        
        for col, (width, minwidth, heading, anchor) in column_configs.items():
            self.summary_tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.summary_tree.column(col, width=width, minwidth=minwidth, anchor=anchor, stretch=True)
        
        # Scrollbar for table
        tree_scroll = ttk.Scrollbar(table_left, orient="vertical", command=self.summary_tree.yview)
        self.summary_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.summary_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0), pady=(0, 2))
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 2), padx=(0, 2))
        
        # Right side: Details Panel (responsive with minimum width)
        self.details_panel = tk.Frame(table_split, bg="#f8f9fa")
        self.details_panel.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(5, 2), pady=2)
        
        # Initial placeholder for details panel
        self.show_details_placeholder()
        
        # Mouse wheel scrolling for treeview - takes priority over dashboard scroll
        def _on_tree_mousewheel(event):
            self.summary_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # Prevent event from propagating to dashboard
        
        def _bind_tree_mousewheel(event):
            # Unbind dashboard scroll and bind table scroll
            self.main_canvas.unbind_all("<MouseWheel>")
            self.summary_tree.bind_all("<MouseWheel>", _on_tree_mousewheel)
        
        def _unbind_tree_mousewheel(event):
            # Unbind table scroll and restore dashboard scroll
            self.summary_tree.unbind_all("<MouseWheel>")
            self._bind_canvas_scroll(None)
        
        # Bind Enter/Leave on treeview and table container
        self.summary_tree.bind("<Enter>", _bind_tree_mousewheel)
        self.summary_tree.bind("<Leave>", _unbind_tree_mousewheel)
        table_left.bind("<Enter>", _bind_tree_mousewheel)
        table_left.bind("<Leave>", _unbind_tree_mousewheel)
        
        # Bind double-click to open override dialog
        self.summary_tree.bind("<Double-Button-1>", self.on_row_double_click)
        
        # Bind single-click to show details panel
        self.summary_tree.bind("<<TreeviewSelect>>", self.on_row_select)
        
        # Tips and actions frame
        action_frame = tk.Frame(self.canvas_frame, bg="#f8f9fa")
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Info labels
        tips_frame = tk.Frame(action_frame, bg="#f8f9fa")
        tips_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Override feature highlight box
        override_hint_frame = tk.Frame(tips_frame, bg="#e3f2fd", padx=10, pady=8)
        override_hint_frame.pack(anchor=tk.W, pady=(0, 8), fill=tk.X)
        
        tk.Label(
            override_hint_frame,
            text="✏️ MANUAL OVERRIDE: Double-click any subject row to manually set attended/total classes",
            font=("Segoe UI", 10, "bold"),
            foreground="#1565c0",
            bg="#e3f2fd",
            anchor=tk.W
        ).pack(anchor=tk.W)
        
        tk.Label(
            override_hint_frame,
            text="      Use this when classes were cancelled, rescheduled, or you need to correct attendance data",
            font=("Segoe UI", 10),
            foreground="#1976d2",
            bg="#e3f2fd",
            anchor=tk.W
        ).pack(anchor=tk.W)
        
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
        """Create visual progress bar representation
        Uses 60% threshold for per-subject status"""
        bar_length = 10
        filled = int((percentage / 100) * bar_length)
        
        if percentage >= 75:
            symbol = "█"
            color = "🟢"
        elif percentage >= 60:
            symbol = "█"
            color = "🟡"
        else:
            symbol = "█"
            color = "🔴"
        
        bar = symbol * filled + "░" * (bar_length - filled)
        return f"{color} {bar}"
    
    def show_details_placeholder(self):
        """Show placeholder text in details panel"""
        for widget in self.details_panel.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.details_panel,
            text="📋 Subject Details",
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#495057"
        ).pack(pady=(15, 10))
        
        tk.Label(
            self.details_panel,
            text="Click a subject row\nto view details",
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            fg="#6c757d",
            justify=tk.CENTER
        ).pack(pady=20)
        
        # Override hint in placeholder
        hint_frame = tk.Frame(self.details_panel, bg="#fff3cd", padx=8, pady=6)
        hint_frame.pack(pady=15, padx=10, fill=tk.X)
        
        tk.Label(
            hint_frame,
            text="💡 Tip",
            font=("Segoe UI", 9, "bold"),
            bg="#fff3cd",
            fg="#856404"
        ).pack(anchor=tk.W)
        
        tk.Label(
            hint_frame,
            text="Double-click any row\nto override attendance",
            font=("Segoe UI", 10),
            bg="#fff3cd",
            fg="#856404",
            justify=tk.LEFT
        ).pack(anchor=tk.W)
    
    def on_row_select(self, event):
        """Handle single-click on row to show details panel"""
        selection = self.summary_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.summary_tree.item(item, "values")
        if not values:
            return
        
        subject_name = values[0]
        self.show_subject_details(subject_name)
    
    def show_subject_details(self, subject_name):
        """Display detailed information about a subject in the side panel"""
        # Clear panel
        for widget in self.details_panel.winfo_children():
            widget.destroy()
        
        app_data = get_app_data()
        subject_data = None
        
        # Find subject
        for subj in app_data.get("subjects", []):
            if subj["name"] == subject_name:
                subject_data = subj
                break
        
        if not subject_data:
            self.show_details_placeholder()
            return
        
        # Header with close button
        header = tk.Frame(self.details_panel, bg="#f8f9fa")
        header.pack(fill=tk.X, padx=5, pady=(10, 5))
        
        tk.Label(
            header,
            text="📋 Subject Details",
            font=("Segoe UI", 11, "bold"),
            bg="#f8f9fa",
            fg="#495057"
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header,
            text="✕",
            font=("Segoe UI", 10),
            bg="#f8f9fa",
            fg="#666",
            bd=0,
            cursor="hand2",
            command=self.show_details_placeholder
        ).pack(side=tk.RIGHT)
        
        # Subject name
        tk.Label(
            self.details_panel,
            text=subject_name,
            font=("Segoe UI", 13, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50",
            wraplength=260
        ).pack(pady=(5, 10), padx=5)
        
        # Get cached data or calculate
        today = datetime.now().strftime("%Y-%m-%d")
        semester_end = app_data.get("semester_end")
        end_date = today
        if semester_end and today > semester_end:
            end_date = semester_end
        
        # Calculate values
        if subject_data.get("attendance_override"):
            present = subject_data["attendance_override"]["attended"]
            total = subject_data["attendance_override"]["total"]
            is_override = True
        else:
            total = count_subject_classes(
                subject_name,
                app_data.get("batch", ""),
                app_data["semester_start"],
                end_date,
                app_data.get("holidays", [])
            )
            
            from calculations import parse_date, is_date_in_holidays
            absent_dates = subject_data.get("absent_dates", [])
            holidays = app_data.get("holidays", [])
            absent_count = 0
            for date_str in absent_dates:
                if date_str > today:
                    continue
                date_obj = parse_date(date_str)
                if date_obj and not is_date_in_holidays(date_obj, holidays):
                    absent_count += 1
            
            present = max(0, total - absent_count)
            is_override = False
        
        attendance_pct = calculate_attendance(present, total)
        safe_skip = calculate_safe_skip(present, total)
        
        # Stats frame
        stats_frame = tk.LabelFrame(self.details_panel, text="Statistics", font=("Segoe UI", 9, "bold"), bg="#f8f9fa")
        stats_frame.pack(fill=tk.X, padx=8, pady=5)
        
        stats = [
            ("Classes Attended", f"{present} / {total}"),
            ("Attendance", f"{attendance_pct:.1f}%"),
            ("Can Skip", f"{safe_skip} classes"),
            ("Weekly Count", f"{subject_data.get('weekly_count', 'N/A')}x/week"),
        ]
        
        for label, value in stats:
            row = tk.Frame(stats_frame, bg="#f8f9fa")
            row.pack(fill=tk.X, padx=5, pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 10), bg="#f8f9fa", fg="#666").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#333").pack(side=tk.RIGHT)
        
        if is_override:
            tk.Label(
                stats_frame,
                text="⚠️ Manual Override Active",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#ff9800"
            ).pack(pady=(5, 2))
        
        # Status indicator (60% threshold for subjects)
        if attendance_pct >= 75:
            status_text = "🟢 Excellent"
            status_color = COLOR_SAFE
        elif attendance_pct >= 60:
            status_text = "🟡 Safe"
            status_color = COLOR_WARNING
        else:
            status_text = "🔴 At Risk"
            status_color = COLOR_RISK
            # Show classes needed to reach 60%
            if total > 0:
                # Formula: (present + x) / (total + x) >= 0.60
                # Solving: present + x >= 0.60 * (total + x)
                # x >= (0.60*total - present) / 0.40
                classes_needed = max(0, int((0.60 * total - present) / 0.40) + 1)
                tk.Label(
                    self.details_panel,
                    text=f"📈 Need {classes_needed} more classes\nwithout absence to reach 60%",
                    font=("Segoe UI", 10),
                    bg="#f8f9fa",
                    fg=COLOR_RISK,
                    justify=tk.CENTER
                ).pack(pady=5)
        
        tk.Label(
            self.details_panel,
            text=status_text,
            font=("Segoe UI", 14, "bold"),
            bg="#f8f9fa",
            fg=status_color
        ).pack(pady=10)
        
        # Absent dates section
        absent_dates = subject_data.get("absent_dates", [])
        if absent_dates:
            dates_frame = tk.LabelFrame(self.details_panel, text=f"Absent Dates ({len(absent_dates)})", 
                                        font=("Segoe UI", 9, "bold"), bg="#f8f9fa")
            dates_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
            
            # Scrollable list
            dates_canvas = tk.Canvas(dates_frame, bg="#f8f9fa", height=100, highlightthickness=0)
            dates_scrollbar = ttk.Scrollbar(dates_frame, orient="vertical", command=dates_canvas.yview)
            dates_list = tk.Frame(dates_canvas, bg="#f8f9fa")
            
            dates_canvas.configure(yscrollcommand=dates_scrollbar.set)
            dates_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            dates_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            dates_canvas.create_window((0, 0), window=dates_list, anchor="nw")
            dates_list.bind("<Configure>", lambda e: dates_canvas.configure(scrollregion=dates_canvas.bbox("all")))
            
            # Sort dates (most recent first)
            sorted_dates = sorted(absent_dates, reverse=True)
            for date_str in sorted_dates[:15]:  # Show max 15 dates
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted = date_obj.strftime("%b %d, %Y (%a)")
                    tk.Label(
                        dates_list,
                        text=f"• {formatted}",
                        font=("Segoe UI", 10),
                        bg="#f8f9fa",
                        fg="#666",
                        anchor=tk.W
                    ).pack(anchor=tk.W, padx=5)
                except:
                    pass
            
            if len(absent_dates) > 15:
                tk.Label(
                    dates_list,
                    text=f"... and {len(absent_dates) - 15} more",
                    font=("Segoe UI", 8, "italic"),
                    bg="#f8f9fa",
                    fg="#999"
                ).pack(anchor=tk.W, padx=5)
        else:
            tk.Label(
                self.details_panel,
                text="✨ No absences recorded!",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg=COLOR_SAFE
            ).pack(pady=10)
        
        # Edit button
        ttk.Button(
            self.details_panel,
            text="✏️ Edit Attendance",
            command=lambda: self.open_override_dialog(subject_name)
        ).pack(pady=10)
    
    def update_semester_progress(self):
        """Update the semester progress bar and days left display"""
        # Clear existing
        for widget in self.semester_progress_frame.winfo_children():
            widget.destroy()
        
        app_data = get_app_data()
        semester_start = app_data.get("semester_start")
        semester_end = app_data.get("semester_end")
        
        if not semester_start or not semester_end:
            return
        
        try:
            start_date = datetime.strptime(semester_start, "%Y-%m-%d")
            end_date = datetime.strptime(semester_end, "%Y-%m-%d")
            today = datetime.now()
            
            total_days = (end_date - start_date).days
            elapsed_days = (today - start_date).days
            remaining_days = (end_date - today).days
            
            # Clamp values
            elapsed_days = max(0, min(elapsed_days, total_days))
            remaining_days = max(0, remaining_days)
            
            progress_pct = (elapsed_days / total_days * 100) if total_days > 0 else 0
            
            # Container
            container = tk.Frame(self.semester_progress_frame, bg="#ffffff")
            container.pack(fill=tk.X, padx=10, pady=5)
            
            # Header row
            header_row = tk.Frame(container, bg="#ffffff")
            header_row.pack(fill=tk.X)
            
            tk.Label(
                header_row,
                text="📅 Semester Progress",
                font=("Segoe UI", 11, "bold"),
                bg="#ffffff",
                fg="#495057"
            ).pack(side=tk.LEFT)
            
            # Days remaining badge
            if remaining_days > 0:
                days_text = f"📆 {remaining_days} days left"
                days_color = "#28a745" if remaining_days > 30 else ("#ffc107" if remaining_days > 14 else "#dc3545")
            else:
                days_text = "✅ Semester Complete"
                days_color = "#28a745"
            
            tk.Label(
                header_row,
                text=days_text,
                font=("Segoe UI", 10, "bold"),
                bg="#ffffff",
                fg=days_color
            ).pack(side=tk.RIGHT)
            
            # Progress bar container
            progress_container = tk.Frame(container, bg="#e9ecef", height=20)
            progress_container.pack(fill=tk.X, pady=(8, 5))
            progress_container.pack_propagate(False)
            
            # Filled portion
            fill_width = max(1, int(progress_pct))
            if progress_pct >= 75:
                bar_color = "#dc3545"  # Red - semester almost over
            elif progress_pct >= 50:
                bar_color = "#ffc107"  # Yellow - halfway
            else:
                bar_color = "#28a745"  # Green - early
            
            progress_fill = tk.Frame(progress_container, bg=bar_color)
            progress_fill.place(relwidth=progress_pct/100, relheight=1)
            
            # Progress text overlay
            tk.Label(
                progress_container,
                text=f"{progress_pct:.0f}%",
                font=("Segoe UI", 9, "bold"),
                bg=bar_color if progress_pct > 50 else "#e9ecef",
                fg="white" if progress_pct > 50 else "#333"
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            # Date labels
            date_row = tk.Frame(container, bg="#ffffff")
            date_row.pack(fill=tk.X)
            
            tk.Label(
                date_row,
                text=start_date.strftime("%b %d"),
                font=("Segoe UI", 10),
                bg="#ffffff",
                fg="#666"
            ).pack(side=tk.LEFT)
            
            tk.Label(
                date_row,
                text=f"Day {elapsed_days} of {total_days}",
                font=("Segoe UI", 10),
                bg="#ffffff",
                fg="#666"
            ).pack(side=tk.LEFT, expand=True)
            
            tk.Label(
                date_row,
                text=end_date.strftime("%b %d"),
                font=("Segoe UI", 10),
                bg="#ffffff",
                fg="#666"
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Error updating semester progress: {e}")

    def refresh(self):
        """Refresh summary display with enhanced visualizations"""
        app_data = get_app_data()
        
        # Optimize UI updates
        self.summary_tree.update_idletasks()
        
        # Update semester progress bar
        self.update_semester_progress()
        
        # Clear existing items
        for item in self.summary_tree.get_children():
            self.summary_tree.delete(item)
        
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Clear overall warning frame if exists
        if self.overall_warning_frame:
            self.overall_warning_frame.destroy()
            self.overall_warning_frame = None
        
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
            
            # Determine status icon and category (60% threshold for subjects)
            if attendance_pct >= 75:
                status_icon = "🟢 Excellent"
                tag = "safe"
                safe_count += 1
            elif attendance_pct >= 60:
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
        
        # Configure tags with background colors
        self.summary_tree.tag_configure("safe", background=COLOR_BG_SAFE, foreground="#155724")
        self.summary_tree.tag_configure("warning", background=COLOR_BG_WARNING, foreground="#856404")
        self.summary_tree.tag_configure("risk", background=COLOR_BG_RISK, foreground="#721c24")
        
        # Display enhanced stats cards
        subjects_list = app_data.get("subjects", [])
        num_subjects = len(subjects_list)
        avg_attendance = total_attendance_pct / num_subjects if num_subjects > 0 else 0
        
        # Determine average color (75% threshold for overall)
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
        
        # Add overall attendance warning if below 75%
        if avg_attendance < 75:
            self.overall_warning_frame = tk.Frame(self.stats_frame.master, bg="#f8d7da")
            self.overall_warning_frame.pack(fill=tk.X, padx=10, pady=(5, 0))
            tk.Label(
                self.overall_warning_frame,
                text=f"⚠️ Overall attendance ({avg_attendance:.1f}%) is below 75% minimum!",
                font=("Segoe UI", 10, "bold"),
                bg="#f8d7da",
                fg="#721c24"
            ).pack(pady=5)
    
    def get_bg_color(self, percentage):
        """Get background color based on percentage (60% threshold for subjects)"""
        if percentage >= 75:
            return COLOR_BG_SAFE
        elif percentage >= 60:
            return COLOR_BG_WARNING
        else:
            return COLOR_BG_RISK
    
    def create_stat_card(self, icon, label, value, text_color, bg_color):
        """Create enhanced stat card with icon and styling - compact version"""
        # Card container with shadow effect
        card_container = tk.Frame(self.stats_frame, bg="#dee2e6", bd=1, relief=tk.SOLID)
        card_container.pack(side=tk.LEFT, expand=True, padx=6, pady=4)
        
        # Inner card
        card = tk.Frame(card_container, bg=bg_color)
        card.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Icon
        tk.Label(
            card,
            text=icon,
            font=("Segoe UI", 20),
            bg=bg_color
        ).pack(pady=(8, 2))
        
        # Value
        tk.Label(
            card,
            text=str(value),
            font=("Segoe UI", 20, "bold"),
            fg=text_color,
            bg=bg_color
        ).pack()
        
        # Label
        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 10),
            fg="#495057",
            bg=bg_color
        ).pack(pady=(2, 8))
    
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
                f.write("BUNKMETER - ATTENDANCE REPORT\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Batch: {app_data.get('batch', 'N/A')}\n")
                f.write(f"Semester: {app_data.get('semester_start', 'N/A')} to {app_data.get('semester_end', 'N/A')}\n\n")
                
                f.write("-" * 70 + "\n")
                f.write(f"{'Subject':<20} {'Present':>10} {'Total':>10} {'%':>8} {'Status':>10}\n")
                f.write("-" * 70 + "\n")
                
                # Use TODAY as end date for calculations (not semester end)
                today = datetime.now().strftime("%Y-%m-%d")
                end_date = today
                if app_data.get("semester_end") and today > app_data["semester_end"]:
                    end_date = app_data["semester_end"]
                
                for subject_data in app_data.get("subjects", []):
                    name = subject_data["name"]
                    
                    # Check if manual override exists
                    if subject_data.get("attendance_override") is not None:
                        override_data = subject_data["attendance_override"]
                        present = override_data["attended"]
                        total = override_data["total"]
                    else:
                        # Use accurate day-by-day counting
                        if subject_data.get("total_override") is not None:
                            total = subject_data["total_override"]
                        else:
                            total = count_subject_classes(
                                name,
                                app_data.get("batch", ""),
                                app_data["semester_start"],
                                end_date,
                                app_data.get("holidays", [])
                            )
                        
                        # Exclude dates that fall on holidays and future dates from absent count
                        from calculations import parse_date, is_date_in_holidays
                        all_absent_dates = subject_data.get("absent_dates", [])
                        absent_count = 0
                        holidays = app_data.get("holidays", [])
                        for date_str in all_absent_dates:
                            # Ignore future dates
                            if date_str > today:
                                continue
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
        
        # Create dialog with proper sizing
        dialog = tk.Toplevel()
        dialog.title(f"Manual Override - {subject_name}")
        dialog.resizable(True, True)
        
        # Set size and center the dialog
        width = 500
        height = 500
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        dialog.minsize(400, 400)  # Minimum size
        
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
        
        # Calculate current values using TODAY as end date
        today = datetime.now().strftime("%Y-%m-%d")
        end_date = today
        if app_data.get("semester_end") and today > app_data["semester_end"]:
            end_date = app_data["semester_end"]
        
        # Check for existing override
        has_override = subject_data.get("attendance_override") is not None
        if has_override:
            current_attended = subject_data["attendance_override"]["attended"]
            current_total = subject_data["attendance_override"]["total"]
        else:
            # Use accurate day-by-day counting
            if subject_data.get("total_override") is not None:
                current_total = subject_data["total_override"]
            else:
                current_total = count_subject_classes(
                    subject_name,
                    app_data.get("batch", ""),
                    app_data["semester_start"],
                    end_date,
                    app_data.get("holidays", [])
                )
            
            # Exclude dates that fall on holidays and future dates from absent count
            from calculations import parse_date, is_date_in_holidays
            all_absent_dates = subject_data.get("absent_dates", [])
            absent_count = 0
            holidays = app_data.get("holidays", [])
            for date_str in all_absent_dates:
                # Ignore future dates
                if date_str > today:
                    continue
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
                font=("Segoe UI", 10),
                foreground="#ff9800"
            ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Override inputs frame
        input_frame = tk.LabelFrame(dialog, text="✏️ Override Attendance", font=("Segoe UI", 10, "bold"))
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            input_frame,
            text="Enter actual attendance data:",
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, padx=10, pady=5)
        
        # Total classes input
        tk.Label(input_frame, text="Total Classes Held:", font=("Segoe UI", 10)).pack(anchor=tk.W, padx=10, pady=(10, 0))
        total_entry = tk.Entry(input_frame, font=("Segoe UI", 10), width=15)
        total_entry.insert(0, str(current_total))
        total_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Attended classes input
        tk.Label(input_frame, text="Classes Attended:", font=("Segoe UI", 10)).pack(anchor=tk.W, padx=10, pady=(10, 0))
        attended_entry = tk.Entry(input_frame, font=("Segoe UI", 10), width=15)
        attended_entry.insert(0, str(current_attended))
        attended_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Info label
        tk.Label(
            dialog,
            text="💡 Use this when actual attendance differs from timetable\n(cancellations, rescheduling, extra classes, etc.)",
            font=("Segoe UI", 10),
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
