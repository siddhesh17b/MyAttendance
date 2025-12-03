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
    export_timetable_to_csv, import_timetable_from_csv, reset_to_default_timetable
from calculations import parse_date

class SetupTab:
    def __init__(self, notebook, refresh_callback):
        self.notebook = notebook
        self.refresh_all_tabs = refresh_callback
        self.batch_var = None
        self.start_date_cal = None
        self.end_date_cal = None
        self.holidays_tree = None
    
    def create(self):
        """Create setup tab"""
        tab = ttk.Frame(self.notebook)
        
        # Scrollable frame
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
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
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        app_data = get_app_data()
        
        # Create 2-column layout for better space usage
        left_column = ttk.Frame(scrollable_frame)
        left_column.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        right_column = ttk.Frame(scrollable_frame)
        right_column.grid(row=0, column=1, sticky=(tk.N, tk.W, tk.E), padx=5, pady=5)
        
        scrollable_frame.columnconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Batch Selection (LEFT)
        batch_frame = tk.LabelFrame(left_column, text="Batch Selection", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        batch_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.batch_var = tk.StringVar(value=app_data.get("batch", "B1/B3"))
        ttk.Radiobutton(batch_frame, text="B1/B3", variable=self.batch_var, value="B1/B3").pack(anchor=tk.W)
        ttk.Radiobutton(batch_frame, text="B2/B4", variable=self.batch_var, value="B2/B4").pack(anchor=tk.W)
        ttk.Button(batch_frame, text="Update Batch", command=self.on_batch_update).pack(pady=5)
        
        # Semester Dates (LEFT)
        dates_frame = tk.LabelFrame(left_column, text="Semester Dates", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        dates_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start Date Calendar
        tk.Label(dates_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=5)
        
        start_date = datetime.now()
        if app_data.get("semester_start"):
            try:
                start_date = datetime.strptime(app_data["semester_start"], "%Y-%m-%d")
            except:
                pass
        
        self.start_date_cal = Calendar(
            dates_frame,
            selectmode='day',
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.start_date_cal.grid(row=1, column=0, padx=5, pady=5)
        
        # End Date Calendar
        tk.Label(dates_frame, text="End Date:", font=("Arial", 10, "bold")).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        end_date = datetime.now()
        if app_data.get("semester_end"):
            try:
                end_date = datetime.strptime(app_data["semester_end"], "%Y-%m-%d")
            except:
                pass
        
        self.end_date_cal = Calendar(
            dates_frame,
            selectmode='day',
            year=end_date.year,
            month=end_date.month,
            day=end_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.end_date_cal.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(dates_frame, text="Save Dates", command=self.on_dates_update).grid(
            row=2, column=0, columnspan=2, pady=10)
        
        # Holidays (LEFT)
        holidays_frame = tk.LabelFrame(left_column, text="Holiday Periods", 
                                      font=("Arial", 11, "bold"), padx=10, pady=10)
        holidays_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.holidays_tree = ttk.Treeview(holidays_frame, columns=("Name", "Start", "End"), 
                                         show="headings", height=6)
        self.holidays_tree.heading("Name", text="Holiday Name")
        self.holidays_tree.heading("Start", text="Start Date")
        self.holidays_tree.heading("End", text="End Date")
        self.holidays_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_frame = tk.Frame(holidays_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="➕ Add Holiday", command=self.add_holiday).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="➖ Remove Holiday", command=self.remove_holiday).pack(side=tk.LEFT, padx=5)
        
        # Timetable Management Section (RIGHT)
        timetable_frame = tk.LabelFrame(right_column, text="Custom Timetable Management", 
                                        font=("Arial", 11, "bold"), padx=10, pady=10)
        timetable_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            timetable_frame, 
            text="📚 Upload your own timetable CSV or export the current one as a template.\nSee TIMETABLE_UPLOAD_GUIDE.md for format details.",
            font=("Arial", 9),
            foreground="#007bff",
            justify=tk.LEFT
        ).pack(pady=5)
        
        timetable_btn_frame = tk.Frame(timetable_frame)
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
        
        # Reset Data Section (RIGHT)
        reset_frame = tk.LabelFrame(right_column, text="Reset Data", 
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        reset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            reset_frame, 
            text="⚠️ Warning: This will clear all holidays and absent dates.\nSemester dates and batch will be preserved.",
            font=("Arial", 9),
            foreground="#dc3545",
            justify=tk.LEFT
        ).pack(pady=5)
        
        ttk.Button(
            reset_frame, 
            text="🔄 Reset All Data", 
            command=self.reset_data
        ).pack(pady=5)
        
        self.refresh()
        return tab
    
    def refresh(self):
        """Refresh holidays list"""
        app_data = get_app_data()
        for item in self.holidays_tree.get_children():
            self.holidays_tree.delete(item)
        
        for holiday in app_data.get("holidays", []):
            self.holidays_tree.insert("", tk.END, values=(holiday["name"], holiday["start"], holiday["end"]))
    
    def on_batch_update(self):
        app_data = get_app_data()
        new_batch = self.batch_var.get()
        if new_batch != app_data.get("batch"):
            app_data["batch"] = new_batch
            weekly_counts = parse_timetable_csv(new_batch)
            existing_subjects = {s["name"]: s for s in app_data["subjects"]}
            app_data["subjects"] = []
            for subject, count in weekly_counts.items():
                if subject in existing_subjects:
                    existing_subjects[subject]["weekly_count"] = count
                    app_data["subjects"].append(existing_subjects[subject])
                else:
                    app_data["subjects"].append({"name": subject, "weekly_count": count, "total_override": None, "absent_dates": []})
            
            save_data()
            self.refresh_all_tabs()
            messagebox.showinfo("Success", "Batch updated successfully!")
    
    def on_dates_update(self):
        app_data = get_app_data()
        app_data["semester_start"] = self.start_date_cal.get_date()
        app_data["semester_end"] = self.end_date_cal.get_date()
        save_data()
        self.refresh_all_tabs()
        messagebox.showinfo("Success", "Semester dates updated!")
    
    def add_holiday(self):
        """Add a holiday period"""
        app_data = get_app_data()
        dialog = tk.Toplevel()
        dialog.title("Add Holiday")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Holiday Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack()
        
        tk.Label(dialog, text="Start Date (YYYY-MM-DD):").pack(pady=5)
        start_entry = ttk.Entry(dialog, width=30)
        start_entry.pack()
        
        tk.Label(dialog, text="End Date (YYYY-MM-DD):").pack(pady=5)
        end_entry = ttk.Entry(dialog, width=30)
        end_entry.pack()
        
        def save_holiday():
            name = name_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()
            
            if not name or not start or not end:
                messagebox.showerror("Error", "All fields are required")
                return
            
            if not parse_date(start) or not parse_date(end):
                messagebox.showerror("Error", "Invalid date format")
                return
            
            app_data["holidays"].append({"name": name, "start": start, "end": end})
            save_data()
            self.refresh()
            self.refresh_all_tabs()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_holiday).pack(pady=10)
    
    def remove_holiday(self):
        """Remove selected holiday"""
        app_data = get_app_data()
        selected = self.holidays_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a holiday to remove")
            return
        
        index = self.holidays_tree.index(selected[0])
        del app_data["holidays"][index]
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
            "• All absent dates for all subjects\n"
            "• All total overrides\n\n"
            "Batch and semester dates will be preserved.\n\n"
            "Are you sure you want to continue?",
            icon="warning"
        )
        
        if not confirm:
            return
        
        app_data = get_app_data()
        
        # Clear holidays
        app_data["holidays"] = []
        
        # Clear absent dates and total overrides for all subjects
        for subject in app_data.get("subjects", []):
            subject["absent_dates"] = []
            subject["total_override"] = None
        
        # Save changes
        save_data()
        
        # Refresh all tabs
        self.refresh()
        self.refresh_all_tabs()
        
        messagebox.showinfo("Success", "All data has been reset successfully!")
    
    def import_timetable(self):
        """Import custom timetable from CSV"""
        success = import_timetable_from_csv()
        if success:
            # Reinitialize subjects based on new timetable
            app_data = get_app_data()
            batch = app_data.get("batch", "B1/B3")
            subject_counts = parse_timetable_csv(batch)
            
            # Update or add subjects
            existing_subjects = {s["name"]: s for s in app_data.get("subjects", [])}
            app_data["subjects"] = []
            
            for subject_name, weekly_count in subject_counts.items():
                if subject_name in existing_subjects:
                    # Preserve existing data
                    app_data["subjects"].append(existing_subjects[subject_name])
                else:
                    # Add new subject
                    app_data["subjects"].append({
                        "name": subject_name,
                        "weekly_count": weekly_count,
                        "total_override": None,
                        "absent_dates": []
                    })
            
            save_data()
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
                    app_data["subjects"].append(existing_subjects[subject_name])
                else:
                    app_data["subjects"].append({
                        "name": subject_name,
                        "weekly_count": weekly_count,
                        "total_override": None,
                        "absent_dates": []
                    })
            
            save_data()
            self.refresh_all_tabs()
