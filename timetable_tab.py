"""
Timetable Tab - Weekly schedule display
Visual color-coded timetable grid with batch-aware lab schedules

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import tkinter as tk
from tkinter import ttk
from data_manager import get_app_data, get_active_timetable

class TimetableTab:
    def __init__(self, parent, refresh_callback=None):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.frame = None
        
    def create(self):
        self.frame = ttk.Frame(self.parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        title_frame = ttk.Frame(self.frame)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        ttk.Label(title_frame, text="📅 Weekly Timetable", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.batch_label = ttk.Label(title_frame, text="", font=("Segoe UI", 10))
        self.batch_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.create_timetable_view()
        self.create_legend()
        self.refresh()
        return self.frame
    
    def create_timetable_view(self):
        container = ttk.Frame(self.frame)
        container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.timetable_frame = ttk.Frame(canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas_frame = canvas.create_window((0, 0), window=self.timetable_frame, anchor="nw")
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=event.width)
        self.timetable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def create_legend(self):
        legend_frame = ttk.LabelFrame(self.frame, text="Legend", padding="10")
        legend_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        legends = [("Theory", "#E3F2FD"), ("Lab", "#F3E5F5"), ("Minor/MDM/OE/Honors", "#FFF3E0"), ("Break", "#F5F5F5")]
        for idx, (label, bg) in enumerate(legends):
            tk.Label(legend_frame, text="  ", bg=bg, relief="solid", borderwidth=1, width=3).grid(row=0, column=idx*2, padx=(0, 5))
            ttk.Label(legend_frame, text=label).grid(row=0, column=idx*2+1, padx=(0, 20))
    
    def refresh(self):
        app_data = get_app_data()
        batch = app_data.get("batch", "B1/B3")
        self.batch_label.config(text=f"Current Batch: {batch}")
        for widget in self.timetable_frame.winfo_children():
            widget.destroy()
        
        # Get dynamic time slots from active timetable
        active_timetable = get_active_timetable()
        time_slots_set = set()
        for day_data in active_timetable.values():
            time_slots_set.update(day_data.keys())
        
        # Sort time slots by 24-hour format (convert 12-hour to 24-hour for sorting)
        def sort_time_slot(slot):
            start_time = slot.split("-")[0].strip()
            # Convert to 24-hour format for sorting
            if ":" in start_time:
                hour, minute = start_time.split(":")
                hour = int(hour)
                # If it's 01:00-05:00, it's PM (13:00-17:00)
                if 1 <= hour <= 5:
                    hour += 12
                return hour * 60 + int(minute)
            return 0
        
        time_slots = sorted(list(time_slots_set), key=sort_time_slot)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        ttk.Label(self.timetable_frame, text="Day", font=("Segoe UI", 10, "bold"), background="#ECEFF1", relief="solid", borderwidth=1, padding=8).grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
        
        for col_idx, time_slot in enumerate(time_slots, 1):
            ttk.Label(self.timetable_frame, text=time_slot, font=("Segoe UI", 9, "bold"), background="#ECEFF1", relief="solid", borderwidth=1, padding=6, wraplength=80).grid(row=0, column=col_idx, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
        for row_idx, day in enumerate(days, 1):
            ttk.Label(self.timetable_frame, text=day, font=("Segoe UI", 10, "bold"), background="#ECEFF1", relief="solid", borderwidth=1, padding=8).grid(row=row_idx, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
            for col_idx, time_slot in enumerate(time_slots, 1):
                subject = self.get_subject_for_slot(day, time_slot, batch)
                bg_color, fg_color = self.get_subject_colors(subject, time_slot)
                tk.Label(self.timetable_frame, text=subject, font=("Segoe UI", 8, "bold" if subject not in ["BREAK", "LUNCH", ""] else "normal"), background=bg_color, foreground=fg_color, relief="solid", borderwidth=1, padx=8, pady=8, wraplength=100, justify="center").grid(row=row_idx, column=col_idx, sticky=(tk.W, tk.E, tk.N, tk.S), padx=1, pady=1)
        for col in range(len(time_slots) + 1):
            self.timetable_frame.columnconfigure(col, weight=1, minsize=90)
    
    def get_subject_for_slot(self, day, time_slot, batch):
        day_upper = day.upper()
        active_timetable = get_active_timetable()
        if day_upper in active_timetable:
            subject_cell = active_timetable[day_upper].get(time_slot, "")
            if "Lunch" in subject_cell:
                return "LUNCH"
            if not subject_cell:
                return ""
            if "/" in subject_cell and ("B1&B3" in subject_cell or "B2&B4" in subject_cell):
                parts = subject_cell.split("/")
                if batch in ["B1/B3", "B1", "B3"] and "B1&B3" in subject_cell:
                    for part in parts:
                        if "B1&B3" in part:
                            return self.extract_subject_name(part.split("(")[0].strip())
                elif batch in ["B2/B4", "B2", "B4"] and "B2&B4" in subject_cell:
                    for part in parts:
                        if "B2&B4" in part:
                            return self.extract_subject_name(part.split("(")[0].strip())
                return ""
            return self.extract_subject_name(subject_cell)
        return ""
    
    def extract_subject_name(self, cell_value):
        if not cell_value or cell_value.strip() == "":
            return ""
        if "-" in cell_value:
            parts = cell_value.split("-")
            if len(parts) > 1:
                return parts[1].split("(")[0].strip()
        return cell_value.strip()
    
    def get_subject_colors(self, subject, time_slot):
        if subject in ["BREAK", "LUNCH"]:
            return "#F5F5F5", "#757575"
        if not subject:
            return "#FFFFFF", "#000000"
        if "Lab" in subject:
            return "#F3E5F5", "#7B1FA2"
        if any(k in subject for k in ["Minor", "MDM", "OE", "HONORS"]):
            return "#FFF3E0", "#E65100"
        return "#E3F2FD", "#1976D2"
