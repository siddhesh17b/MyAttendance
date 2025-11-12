"""
Summary Dashboard - Overall attendance statistics and reporting

Features:
- Quick stats cards showing key metrics
- Sortable table with all subjects
- Color-coded status indicators  
- Export report functionality

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from data_manager import get_app_data
from calculations import (
    calculate_weeks_elapsed, 
    calculate_total_classes, 
    calculate_attendance, 
    calculate_safe_skip, 
    get_attendance_status
)

# Color scheme
COLOR_SAFE = "#28a745"    # Green - safe attendance (≥75%)
COLOR_RISK = "#dc3545"    # Red - at risk (<75%)
COLOR_INFO = "#007bff"    # Blue - informational
COLOR_BG_DARK = "#e9ecef" # Light gray background


class SummaryTab:
    """Dashboard showing overall attendance statistics"""
    def __init__(self, notebook, refresh_callback):
        self.notebook = notebook
        self.refresh_all_tabs = refresh_callback
        self.stats_frame = None
        self.summary_tree = None
    
    def create(self):
        """Create the summary dashboard tab"""
        tab = ttk.Frame(self.notebook)
        
        # Header
        tk.Label(
            tab, 
            text="Overall Attendance Summary", 
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)
        
        # Stats cards frame
        self.stats_frame = tk.Frame(tab, bg=COLOR_BG_DARK)
        self.stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Summary table
        columns = ("Subject", "Present", "Total", "Attendance %", "Status", "Safe to Skip")
        self.summary_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.summary_tree.heading(col, text=col)
            # Set column widths
            if col == "Subject":
                width = 150
            else:
                width = 100
            self.summary_tree.column(col, width=width)
        
        self.summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Export button
        ttk.Button(
            tab, 
            text="📄 Export Report", 
            command=self.export_report
        ).pack(pady=10)
        
        # Initial data load
        self.refresh()
        
        return tab
    
    def refresh(self):
        """Refresh summary display"""
        app_data = get_app_data()
        
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
        safe_count = 0
        
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
            
            # Calculate total classes
            if subject_data.get("total_override") is not None:
                total = subject_data["total_override"]
            else:
                total = calculate_total_classes(subject_data["weekly_count"], weeks)
            
            # Calculate present classes (total - absent)
            absent_count = len(subject_data.get("absent_dates", []))
            present = max(0, total - absent_count)
            
            attendance_pct = calculate_attendance(present, total)
            safe_skip = calculate_safe_skip(present, total)
            status, color = get_attendance_status(attendance_pct)
            
            total_attendance_pct += attendance_pct
            if attendance_pct < 75:
                at_risk_count += 1
            else:
                safe_count += 1
            
            item = self.summary_tree.insert(
                "", tk.END,
                values=(name, present, total, f"{attendance_pct:.1f}%", status, safe_skip)
            )
            
            if attendance_pct < 75:
                self.summary_tree.item(item, tags=("risk",))
            else:
                self.summary_tree.item(item, tags=("safe",))
        
        self.summary_tree.tag_configure("risk", foreground=COLOR_RISK)
        self.summary_tree.tag_configure("safe", foreground=COLOR_SAFE)
        
        # Display stats cards
        num_subjects = len(app_data.get("subjects", []))
        avg_attendance = total_attendance_pct / num_subjects if num_subjects > 0 else 0
        
        stats_info = [
            ("Total Subjects", num_subjects, COLOR_INFO),
            ("Average Attendance", f"{avg_attendance:.1f}%", COLOR_INFO),
            ("Safe Subjects", safe_count, COLOR_SAFE),
            ("At-Risk Subjects", at_risk_count, COLOR_RISK if at_risk_count > 0 else COLOR_INFO)
        ]
        
        for label, value, color in stats_info:
            # Create card frame
            frame = tk.Frame(self.stats_frame, bg=COLOR_BG_DARK)
            frame.pack(side=tk.LEFT, expand=True, padx=10, pady=10)
            
            # Label
            tk.Label(
                frame, 
                text=label, 
                font=("Segoe UI", 10), 
                bg=COLOR_BG_DARK
            ).pack()
            
            # Value
            tk.Label(
                frame, 
                text=str(value), 
                font=("Segoe UI", 16, "bold"), 
                fg=color, 
                bg=COLOR_BG_DARK
            ).pack()
    
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
                    
                    if subject_data.get("total_override") is not None:
                        total = subject_data["total_override"]
                    else:
                        total = calculate_total_classes(subject_data["weekly_count"], weeks)
                    
                    absent_count = len(subject_data.get("absent_dates", []))
                    present = max(0, total - absent_count)
                    
                    attendance_pct = calculate_attendance(present, total)
                    status, _ = get_attendance_status(attendance_pct)
                    
                    f.write(f"{name:<20} {present:>10} {total:>10} {attendance_pct:>7.1f}% {status:>10}\n")
                
                f.write("-" * 70 + "\n")
            
            messagebox.showinfo("Success", f"Report exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
