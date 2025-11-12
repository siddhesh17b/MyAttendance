"""
Attendance Calculations - Math and date logic
Handles attendance percentage, safe skip calculations, and date utilities

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

from datetime import datetime

# Color constants
COLOR_SAFE = "#28a745"
COLOR_RISK = "#dc3545"


def parse_date(date_str):
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None


def is_date_in_holidays(date, holidays):
    """Check if a date falls within any holiday period"""
    for holiday in holidays:
        start = parse_date(holiday['start'])
        end = parse_date(holiday['end'])
        if start and end:
            if start <= date <= end:
                return True
    return False


def calculate_weeks_elapsed(start_date_str, end_date_str, holidays):
    """Calculate number of weeks between start and end, excluding holidays"""
    start = parse_date(start_date_str)
    end = parse_date(end_date_str)
    
    if not start or not end:
        return 0
    
    # Count total days
    total_days = (end - start).days + 1
    
    # Subtract holiday days
    holiday_days = 0
    for holiday in holidays:
        h_start = parse_date(holiday['start'])
        h_end = parse_date(holiday['end'])
        if h_start and h_end:
            # Find overlap with semester period
            overlap_start = max(start, h_start)
            overlap_end = min(end, h_end)
            if overlap_start <= overlap_end:
                holiday_days += (overlap_end - overlap_start).days + 1
    
    effective_days = total_days - holiday_days
    weeks = effective_days / 7.0
    return weeks


def calculate_total_classes(weekly_count, weeks):
    """Calculate total classes based on weekly count and weeks elapsed"""
    return int(weekly_count * weeks)


def calculate_attendance(attended, total):
    """Calculate attendance percentage"""
    if total == 0:
        return 0.0
    return (attended / total) * 100


def calculate_safe_skip(attended, total, threshold=75):
    """Calculate how many classes can be safely skipped"""
    if total == 0:
        return 0
    
    # Formula: safe_skip = floor((attended - 0.75 * (total + skips)) / 0.25)
    # Rearranging: skips = (attended - 0.75 * total) / 0.75
    safe = int((attended - threshold/100 * total) / (threshold/100))
    return max(0, safe)


def get_attendance_status(percentage):
    """Get status text and color based on percentage"""
    if percentage >= 75:
        return ("Safe", COLOR_SAFE)
    else:
        return ("At Risk", COLOR_RISK)
