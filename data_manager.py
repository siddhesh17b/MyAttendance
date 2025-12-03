"""
Data Manager - Timetable and JSON persistence
Handles hardcoded timetable data and subject management

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import json
import os
import csv
from tkinter import messagebox, filedialog
from collections import defaultdict

DATA_FILE = "data.json"
CUSTOM_TIMETABLE_FILE = "custom_timetable.json"
TIMETABLE_DATA = {
    "MONDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "DM",
        "11:00-12:00": "DAA",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "TOC",
        "02:00-03:00": "CN",
        "03:00-04:00": "",
        "04:00-05:00": ""
    },
    "TUESDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "CN",
        "11:00-12:00": "TOC",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "DAA",
        "02:00-03:00": "",
        "03:00-04:00": "",
        "04:00-05:00": ""
    },
    "WEDNESDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "",
        "11:00-12:00": "",
        "12:00-01:00": "DM",
        "01:00-02:00": "Lunch Break",
        "02:00-03:00": "DAA",
        "03:00-04:00": "CN Lab (B1&B3) / DAA Lab (B2&B4)",
        "04:00-05:00": "CN Lab (B1&B3) / DAA Lab (B2&B4)"
    },
    "THURSDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "",
        "11:00-12:00": "DM",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "TOC",
        "02:00-03:00": "CN Lab (B2&B4) / DAA Lab (B1&B3)",
        "03:00-04:00": "CN Lab (B2&B4) / DAA Lab (B1&B3)",
        "04:00-05:00": ""
    },
    "FRIDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "Software Lab (B1&B3) / Software Lab (B2&B4)",
        "11:00-12:00": "Software Lab (B1&B3) / Software Lab (B2&B4)",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "CN",
        "02:00-03:00": "Technical Skill",
        "03:00-04:00": "Technical Skill",
        "04:00-05:00": ""
    },
    "SATURDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "OE",
        "11:00-12:00": "Mentor-Mentee Meeting",
        "12:00-01:00": "HONORS",
        "01:00-02:00": "HONORS",
        "02:00-03:00": "HONORS",
        "03:00-04:00": "HONORS",
        "04:00-05:00": ""
    }
}

app_data = {
    "batch": None,
    "semester_start": None,
    "semester_end": None,
    "holidays": [],
    "subjects": []
}

def extract_subject_name(cell_value):
    """Extract subject name - now keeps full names, only excludes lunch/empty"""
    if not cell_value or cell_value.strip() == "":
        return None
    cell_value = cell_value.strip()
    
    # Only exclude Lunch Break and empty cells
    if "Lunch" in cell_value:
        return None
    
    # Return the full subject name as-is (no more code extraction)
    # This allows ANY subject name, batch name, or course name
    return cell_value


def parse_timetable_csv(batch):
    """
    Parse timetable and count weekly classes for each subject based on batch
    
    How it works:
    1. Scans entire week's timetable
    2. For shared slots with "/", extracts subject for selected batch only
    3. Counts occurrences of each subject across the week
    
    Timetable cell formats:
    - Single subject: "DAA" → Counted for all batches
    - Batch-specific: "CN Lab (B1&B3) / DAA Lab (B2&B4)" → Filters by batch
    
    Args:
        batch: Selected batch name (e.g., "B1/B3", "Group A")
    
    Returns:
        dict: {subject_name: weekly_count}
        Example: {"DAA": 3, "CN": 2, "CN Lab": 2}
    
    To modify batch matching:
    - Change the condition: if f"({batch})" in part or batch in part
    - Update format parsing in split operations
    """
    subject_counts = defaultdict(int)
    try:
        if not batch:
            return {}
        
        # Get active timetable (custom or default)
        active_timetable = get_active_timetable()
        
        # Iterate through all days and time slots
        for day, time_slots_dict in active_timetable.items():
            for time_slot, cell_value in time_slots_dict.items():
                # Skip empty cells and lunch breaks
                if not cell_value or cell_value == "Lunch Break":
                    continue
                    
                subject = extract_subject_name(cell_value)
                if subject:
                    # Check if this is a batch-specific entry (contains "/" and "()")
                    if "/" in cell_value and "(" in cell_value:
                        # Split by "/" to separate batch-specific subjects
                        # Format: "Subject1 (Batch1) / Subject2 (Batch2)"
                        parts = cell_value.split("/")
                        for part in parts:
                            # Flexible batch matching: handles multiple formats
                            # B1/B3 matches B1&B3, Group A matches GroupA, Group-A, etc.
                            # Normalize both batch and part for comparison (remove spaces, hyphens, slashes)
                            normalized_batch = batch.replace("/", "").replace(" ", "").replace("-", "").upper()
                            normalized_part = part.replace("&", "").replace(" ", "").replace("-", "").upper()
                            
                            # Check if normalized batch appears in the normalized part
                            if normalized_batch in normalized_part:
                                # Extract subject name (remove batch info)
                                lab_subject = extract_subject_name(part.split("(")[0])
                                if lab_subject:
                                    subject_counts[lab_subject] += 1
                                    break  # Found match, move to next slot
                    else:
                        # Common subject for all batches
                        subject_counts[subject] += 1
                        
        return dict(subject_counts)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse timetable: {str(e)}")
        return {}


def get_subjects_for_day(day_name, batch):
    subjects = []
    if not day_name or not batch:
        return []
    
    day_upper = day_name.upper()
    active_timetable = get_active_timetable()
    if day_upper not in active_timetable:
        return []
    try:
        time_slots_dict = active_timetable[day_upper]
        for time_slot, cell_value in time_slots_dict.items():
            if not cell_value or cell_value == "Lunch Break":
                continue
            subject = extract_subject_name(cell_value)
            if subject:
                if "/" in cell_value and "(" in cell_value:
                    # Dynamic batch matching - handle B1/B3 matching B1&B3
                    parts = cell_value.split("/")
                    for part in parts:
                        # Flexible batch matching: handles multiple formats
                        # B1/B3 matches B1&B3, Group A matches GroupA, Group-A, etc.
                        # Normalize both batch and part for comparison (remove spaces, hyphens, slashes)
                        normalized_batch = batch.replace("/", "").replace(" ", "").replace("-", "").upper()
                        normalized_part = part.replace("&", "").replace(" ", "").replace("-", "").upper()
                        
                        # Check if normalized batch appears in the normalized part
                        if normalized_batch in normalized_part:
                            lab_subject = extract_subject_name(part.split("(")[0])
                            if lab_subject and lab_subject not in subjects:
                                subjects.append(lab_subject)
                                break
                else:
                    if subject not in subjects:
                        subjects.append(subject)
    except Exception as e:
        print(f"Error reading timetable for day {day_name}: {e}")
    return subjects

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(app_data, f, indent=2)
    except IOError as e:
        messagebox.showerror("Error", f"Failed to write to file (permission denied or disk full): {str(e)}")
    except TypeError as e:
        messagebox.showerror("Error", f"Invalid data format (cannot serialize): {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data: {str(e)}")

def load_data():
    global app_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                app_data = json.load(f)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            return False
    return False

def get_app_data():
    return app_data


def get_active_timetable():
    """Get the active timetable (custom if exists, otherwise default)"""
    if os.path.exists(CUSTOM_TIMETABLE_FILE):
        try:
            with open(CUSTOM_TIMETABLE_FILE, 'r') as f:
                custom_timetable = json.load(f)
                # Validate structure - must be dict with day keys
                if not isinstance(custom_timetable, dict):
                    print("Error: Custom timetable is not a dictionary")
                    return TIMETABLE_DATA
                # Validate each day has time slots dict
                for day, time_slots in custom_timetable.items():
                    if not isinstance(time_slots, dict):
                        print(f"Error: Day {day} does not have valid time slots")
                        return TIMETABLE_DATA
                return custom_timetable
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading custom timetable: {e}")
            messagebox.showerror("Error", f"Corrupted timetable file. Using default timetable.\n{str(e)}")
            return TIMETABLE_DATA
        except Exception as e:
            print(f"Unexpected error loading custom timetable: {e}")
            return TIMETABLE_DATA
    return TIMETABLE_DATA


def export_timetable_to_csv(filepath=None):
    """Export current timetable to CSV format"""
    if not filepath:
        filepath = filedialog.asksaveasfilename(
            title="Export Timetable",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="my_timetable.csv"
        )
    
    if not filepath:
        return False
    
    try:
        active_timetable = get_active_timetable()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Day', 'Time', 'Subject'])
            
            days_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
            
            for day in days_order:
                if day in active_timetable:
                    # Sort time slots in 24-hour chronological order
                    def sort_time_key(time_slot):
                        try:
                            start_time = time_slot.split("-")[0].strip()
                            hour, minute = start_time.split(":")
                            hour = int(hour)
                            # Convert 01:00-05:00 to PM times (13:00-17:00) for proper sorting
                            if 1 <= hour <= 5:
                                hour += 12
                            return hour * 60 + int(minute)
                        except:
                            return 9999  # Put invalid slots at end
                    
                    time_slots = sorted(active_timetable[day].keys(), key=sort_time_key)
                    for time_slot in time_slots:
                        subject = active_timetable[day].get(time_slot, '')
                        writer.writerow([day, time_slot, subject])
        
        messagebox.showinfo("Success", f"Timetable exported successfully to:\n{filepath}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export timetable: {str(e)}")
        return False


def import_timetable_from_csv(filepath=None):
    """Import custom timetable from CSV file"""
    if not filepath:
        filepath = filedialog.askopenfilename(
            title="Import Custom Timetable",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
    
    if not filepath:
        return False
    
    try:
        new_timetable = {}
        required_days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
        
        # Initialize structure (no fixed time slots - dynamic based on CSV)
        for day in required_days:
            new_timetable[day] = {}
        
        # Read CSV
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers exist
            if not reader.fieldnames:
                messagebox.showerror("Error", "CSV file is empty or has no headers")
                return False
            
            # Validate required columns
            if not all(col in reader.fieldnames for col in ['Day', 'Time', 'Subject']):
                messagebox.showerror("Error", "CSV must have columns: Day, Time, Subject")
                return False
            
            row_count = 0
            for row in reader:
                row_count += 1
                # Validate row has required fields
                if not row.get('Day') or not row.get('Time'):
                    messagebox.showwarning("Warning", f"Row {row_count}: Missing Day or Time. Skipping...")
                    continue
                
                day = row['Day'].strip().upper()
                time = row['Time'].strip()
                subject = row.get('Subject', '').strip()  # Subject can be empty
                
                if day not in required_days:
                    messagebox.showwarning("Warning", f"Invalid day: {day}. Skipping...")
                    continue
                
                # Accept ANY time format (including 08:00-09:00, custom times, etc.)
                # No validation - full flexibility
                new_timetable[day][time] = subject
        
        # Validate all days present
        for day in required_days:
            if day not in new_timetable or not new_timetable[day]:
                response = messagebox.askyesno(
                    "Missing Days",
                    f"Day {day} is missing or incomplete. Continue anyway?"
                )
                if not response:
                    return False
        
        # Preview and confirm
        subject_count = sum(1 for day in new_timetable.values() 
                          for subject in day.values() 
                          if subject and subject != 'Lunch Break')
        
        response = messagebox.askyesno(
            "Confirm Import",
            f"Timetable loaded successfully!\n\n"
            f"Days: {len(new_timetable)}\n"
            f"Subjects found: {subject_count}\n\n"
            f"This will replace your current timetable.\n"
            f"Continue?"
        )
        
        if response:
            # Save custom timetable
            with open(CUSTOM_TIMETABLE_FILE, 'w') as f:
                json.dump(new_timetable, f, indent=2)
            
            return True
        
        return False
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import timetable:\n{str(e)}")
        return False


def reset_to_default_timetable():
    """Reset to the default hardcoded timetable"""
    if os.path.exists(CUSTOM_TIMETABLE_FILE):
        response = messagebox.askyesno(
            "Confirm Reset",
            "This will delete your custom timetable and restore the default.\n"
            "Continue?"
        )
        if response:
            try:
                os.remove(CUSTOM_TIMETABLE_FILE)
                messagebox.showinfo("Success", "Timetable reset to default.\nRestart the app to apply changes.")
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset timetable: {str(e)}")
                return False
    else:
        messagebox.showinfo("Info", "Already using default timetable.")
        return False
