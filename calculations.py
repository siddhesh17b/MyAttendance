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
    """
    Calculate number of weeks between start and end dates, excluding holidays
    
    How it works:
    1. Calculate total days in semester
    2. Find overlapping days between holidays and semester period
    3. Subtract holiday days from total
    4. Convert effective days to weeks (divide by 7)
    
    Args:
        start_date_str: Semester start date (YYYY-MM-DD format)
        end_date_str: Current/end date (YYYY-MM-DD format)
        holidays: List of holiday dicts with 'start' and 'end' keys
    
    Returns:
        float: Number of effective weeks (excluding holidays)
    
    Example:
        Semester: Jan 1 - Jan 31 (31 days = 4.43 weeks)
        Holiday: Jan 15 - Jan 20 (6 days)
        Result: 25 effective days = 3.57 weeks
    """
    start = parse_date(start_date_str)
    end = parse_date(end_date_str)
    
    if not start or not end:
        return 0
    
    # Count total days in period (inclusive)
    total_days = (end - start).days + 1
    
    # Subtract holiday days that overlap with semester period
    holiday_days = 0
    for holiday in holidays:
        h_start = parse_date(holiday['start'])
        h_end = parse_date(holiday['end'])
        if h_start and h_end:
            # Find overlap: max of starts, min of ends
            overlap_start = max(start, h_start)
            overlap_end = min(end, h_end)
            # Only count if there's actual overlap
            if overlap_start <= overlap_end:
                holiday_days += (overlap_end - overlap_start).days + 1
    
    # Calculate effective teaching days
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
    """
    Calculate how many classes can be safely skipped while maintaining threshold
    
    Formula derivation:
    - Requirement: attendance% >= 75%
    - After skipping 'x' classes: attended / (total + x) >= 0.75
    - Rearranging: attended >= 0.75 * (total + x)
    - Solve for x: x <= (attended - 0.75 * total) / 0.75
    
    Args:
        attended: Number of classes attended so far
        total: Total classes conducted so far
        threshold: Minimum attendance percentage required (default 75%)
    
    Returns:
        int: Maximum number of classes that can be skipped safely
    
    Example:
        Attended: 80 classes, Total: 100 classes
        Current %: 80%
        Safe skip: (80 - 0.75*100) / 0.75 = (80 - 75) / 0.75 = 6.67 ≈ 6 classes
        After skipping 6: 80/(100+6) = 75.47% (still safe)
    """
    if total == 0:
        return 0
    
    # Calculate maximum classes that can be skipped
    # Formula: skips = (attended - threshold% * total) / threshold%
    safe = int((attended - threshold/100 * total) / (threshold/100))
    return max(0, safe)  # Never return negative


def get_attendance_status(percentage):
    """Get status text and color based on percentage"""
    if percentage >= 75:
        return ("Safe", COLOR_SAFE)
    else:
        return ("At Risk", COLOR_RISK)
