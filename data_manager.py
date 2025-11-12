"""
Data Manager - Timetable and JSON persistence
Handles hardcoded timetable data and subject management

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

import json
import os
from tkinter import messagebox
from collections import defaultdict

DATA_FILE = "data.json"
TIMETABLE_DATA = {
    "MONDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "24HS03TH0301-DM (DT203)",
        "11:00-12:00": "24CS01TH0302-DAA (DT203)",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "24CS01TH0301-TOC (DT203)",
        "02:00-03:00": "24CS01TH0304-CN (DT203)",
        "03:00-04:00": "",
        "04:00-05:00": ""
    },
    "TUESDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "24CS01TH0304-CN (DT203)",
        "11:00-12:00": "24CS01TH0301-TOC (DT203)",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "24CS01TH0302-DAA (DT203)",
        "02:00-03:00": "",
        "03:00-04:00": "",
        "04:00-05:00": ""
    },
    "WEDNESDAY": {
        "09:00-10:00": "Minor",
        "10:00-11:00": "",
        "11:00-12:00": "",
        "12:00-01:00": "24HS03TH0301-DM (DT203)",
        "01:00-02:00": "Lunch Break",
        "02:00-03:00": "24CS01TH0302-DAA (DT203)",
        "03:00-04:00": "24CS01PR0304-CN Lab (DT105) (B1&B3) / DAA Lab (DT111) (B2&B4)",
        "04:00-05:00": "24CS01PR0304-CN Lab (DT105) (B1&B3) / DAA Lab (DT111) (B2&B4)"
    },
    "THURSDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "",
        "11:00-12:00": "24HS03TH0301-DM (DT203)",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "24CS01TH0301-TOC (DT304)",
        "02:00-03:00": "24CS01PR0304-CN Lab (DT105) (B2&B4) / DAA Lab (DT111) (B1&B3)",
        "03:00-04:00": "24CS01PR0304-CN Lab (DT105) (B2&B4) / DAA Lab (DT111) (B1&B3)",
        "04:00-05:00": ""
    },
    "FRIDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "24CS01PR0303-Software Lab (DT105) (B1&B3) / Software Lab (DT111) (B2&B4)",
        "11:00-12:00": "24CS01PR0303-Software Lab (DT105) (B1&B3) / Software Lab (DT111) (B2&B4)",
        "12:00-01:00": "Lunch Break",
        "01:00-02:00": "24CS01TH0304-CN (DT212)",
        "02:00-03:00": "Technical Skill session (DT109)",
        "03:00-04:00": "Technical Skill session (DT109)",
        "04:00-05:00": ""
    },
    "SATURDAY": {
        "09:00-10:00": "MDM",
        "10:00-11:00": "OE",
        "11:00-12:00": "Mentor-Mentee Meeting Slot",
        "12:00-01:00": "HONORS (DT301)",  # 12:00-12:30 Lunch, 12:30-1:00 HONORS
        "01:00-02:00": "HONORS (DT301)",
        "02:00-03:00": "HONORS (DT301)",
        "03:00-04:00": "HONORS (DT301)",  # Ends at 3:30
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
    if not cell_value or cell_value.strip() == "":
        return None
    cell_value = cell_value.strip()
    if "Lunch" in cell_value or cell_value == "":
        return None
    if cell_value in ["Minor", "OE"] or "Mentor-Mentee" in cell_value:
        return None
    if cell_value == "MDM":
        return "MDM"
    if "HONORS" in cell_value:
        return "HONORS"
    if "Technical Skill" in cell_value:
        return "Technical Skill"
    if "-" in cell_value:
        parts = cell_value.split("-")
        if len(parts) >= 2:
            subject = parts[1].split("(")[0].strip()
            if "Lab" in subject:
                return subject.split("DT")[0].strip()
            return subject
    return cell_value


def parse_timetable_csv(batch):
    subject_counts = defaultdict(int)
    try:
        for day, time_slots_dict in TIMETABLE_DATA.items():
            for time_slot, cell_value in time_slots_dict.items():
                if not cell_value or cell_value == "Lunch Break":
                    continue
                subject = extract_subject_name(cell_value)
                if subject:
                    if "/" in cell_value and ("B1&B3" in cell_value or "B2&B4" in cell_value):
                        parts = cell_value.split("/")
                        for part in parts:
                            if batch in ["B1/B3", "B1", "B3"] and "B1&B3" in part:
                                lab_subject = extract_subject_name(part.split("(")[0])
                                if lab_subject:
                                    subject_counts[lab_subject] += 1
                                    break
                            elif batch in ["B2/B4", "B2", "B4"] and "B2&B4" in part:
                                lab_subject = extract_subject_name(part.split("(")[0])
                                if lab_subject:
                                    subject_counts[lab_subject] += 1
                                    break
                    else:
                        subject_counts[subject] += 1
        return dict(subject_counts)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse timetable: {str(e)}")
        return {}


def get_subjects_for_day(day_name, batch):
    subjects = []
    day_upper = day_name.upper()
    if day_upper not in TIMETABLE_DATA:
        return []
    try:
        time_slots_dict = TIMETABLE_DATA[day_upper]
        for time_slot, cell_value in time_slots_dict.items():
            if not cell_value or cell_value == "Lunch Break":
                continue
            subject = extract_subject_name(cell_value)
            if subject:
                if "/" in cell_value and ("B1&B3" in cell_value or "B2&B4" in cell_value):
                    parts = cell_value.split("/")
                    for part in parts:
                        if batch in ["B1/B3", "B1", "B3"] and "B1&B3" in part:
                            lab_subject = extract_subject_name(part.split("(")[0])
                            if lab_subject and lab_subject not in subjects:
                                subjects.append(lab_subject)
                                break
                        elif batch in ["B2/B4", "B2", "B4"] and "B2&B4" in part:
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
