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
        self.refresh()
        return self.frame
    
    def create_timetable_view(self):
        container = ttk.Frame(self.frame)
        container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        self.timetable_frame = ttk.Frame(canvas)
        canvas.configure(xscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        canvas_frame = canvas.create_window((0, 0), window=self.timetable_frame, anchor="nw")
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, height=event.height)
        self.timetable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Enable mouse wheel horizontal scrolling (only when hovering over canvas)
        def _on_mousewheel(event):
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
    
    def refresh(self):
        app_data = get_app_data()
        batch = app_data.get("batch", "B1/B3")
        self.batch_label.config(text=f"Current Batch: {batch}")
        
        # Optimize widget destruction
        self.timetable_frame.update_idletasks()
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
        
        # GitHub link at bottom
        github_frame = ttk.Frame(self.frame)
        github_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
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
    
    def get_subject_for_slot(self, day, time_slot, batch):
        """Get subject for a specific day/time slot, handling batch-specific entries"""
        day_upper = day.upper()
        active_timetable = get_active_timetable()
        if day_upper not in active_timetable:
            return ""
        
        subject_cell = active_timetable[day_upper].get(time_slot, "")
        if not subject_cell:
            return ""
        if "Lunch" in subject_cell:
            return "LUNCH"
        
        # Handle batch-specific entries: "Subject (BatchA) / Subject (BatchB)"
        if "/" in subject_cell and "(" in subject_cell:
            parts = subject_cell.split("/")
            # Normalize batch for comparison (remove spaces, slashes, hyphens)
            normalized_batch = batch.replace("/", "").replace(" ", "").replace("-", "").replace("&", "").upper()
            
            for part in parts:
                # Normalize part for comparison
                normalized_part = part.replace("&", "").replace(" ", "").replace("-", "").upper()
                
                # Check if normalized batch appears in the normalized part
                if normalized_batch in normalized_part:
                    # Extract subject name (before the parenthesis)
                    if "(" in part:
                        return self.extract_subject_name(part.split("(")[0].strip())
                    return self.extract_subject_name(part.strip())
            return ""  # Batch not found in any part
        
        return self.extract_subject_name(subject_cell)
    
    def extract_subject_name(self, cell_value):
        if not cell_value or cell_value.strip() == "":
            return ""
        try:
            if "-" in cell_value:
                parts = cell_value.split("-")
                if len(parts) > 1 and parts[1]:
                    # Safely extract subject name
                    subject_part = parts[1]
                    if "(" in subject_part:
                        return subject_part.split("(")[0].strip()
                    return subject_part.strip()
            return cell_value.strip()
        except (IndexError, AttributeError) as e:
            print(f"Error extracting subject name from '{cell_value}': {e}")
            return cell_value.strip() if cell_value else ""
    
    def get_subject_colors(self, subject, time_slot):
        """
        Generate unique, visually distinct colors for each subject
        
        Algorithm:
        1. Creates 3 different hash values from subject name (normal, reverse, char sum)
        2. Combines hashes to generate hue (0-360 degrees on color wheel)
        3. Uses high saturation (0.6-0.8) for vibrant colors
        4. Uses high value/brightness (0.85-0.95) for readability
        5. Same subject always gets same color (deterministic hash)
        
        To modify colors:
        - Adjust saturation range: Currently 0.6-0.8 (0=gray, 1=vivid)
        - Adjust value range: Currently 0.85-0.95 (0=black, 1=white)
        - Change hash multipliers (37, 17, 7) for different color distribution
        
        Args:
            subject: Subject name string
            time_slot: Time slot (unused, kept for compatibility)
        
        Returns:
            tuple: (background_color, text_color) as hex strings
        """
        # Special cases: Lunch breaks and empty slots
        if subject in ["BREAK", "LUNCH"]:
            return "#F5F5F5", "#757575"  # Light gray background, dark gray text
        if not subject:
            return "#FFFFFF", "#000000"  # White background, black text
        
        # Import color conversion library
        import colorsys
        
        # Generate 3 different hash components for better distribution
        hash1 = hash(subject)                    # Standard hash
        hash2 = hash(subject[::-1])              # Reversed string hash
        hash3 = sum(ord(c) for c in subject)    # Sum of character codes
        
        # Combine hashes to get hue (0-360 degrees, converted to 0-1 range)
        # Multipliers (37, 17, 7) are primes for better distribution
        hue = ((hash1 * 37 + hash2 * 17 + hash3 * 7) % 360) / 360.0
        
        # Saturation: How vivid the color is (0.6-0.8 = vibrant but not neon)
        saturation = 0.6 + ((hash2 % 20) / 100.0)  # Range: 0.6 to 0.8
        
        # Value: How bright the color is (0.85-0.95 = light but colorful)
        value = 0.85 + ((hash3 % 10) / 100.0)      # Range: 0.85 to 0.95
        
        # Convert HSV to RGB, then to hex color code
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        bg_color = "#{:02x}{:02x}{:02x}".format(
            int(rgb[0] * 255), 
            int(rgb[1] * 255), 
            int(rgb[2] * 255)
        )
        
        # Generate contrasting text color (darker version of same hue)
        text_rgb = colorsys.hsv_to_rgb(hue, min(1.0, saturation + 0.2), 0.3)
        fg_color = "#{:02x}{:02x}{:02x}".format(
            int(text_rgb[0] * 255), 
            int(text_rgb[1] * 255), 
            int(text_rgb[2] * 255)
        )
        
        return bg_color, fg_color
