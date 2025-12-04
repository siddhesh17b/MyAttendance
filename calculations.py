"""
Attendance Calculations - Math and date logic
Handles attendance percentage, safe skip calculations, and date utilities

Author: Siddhesh Bisen
GitHub: https://github.com/siddhesh17b
"""

from datetime import datetime

# Threshold constants
SUBJECT_THRESHOLD = 60   # Minimum attendance per subject
OVERALL_THRESHOLD = 75   # Minimum overall attendance

# Color constants
COLOR_SAFE = "#28a745"
COLOR_WARNING = "#ffc107"
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
    """Check if a date falls within any holiday period
    
    Args:
        date: datetime object to check
        holidays: List of holiday dicts with 'start' and 'end' keys
    
    Returns:
        bool: True if date is within any holiday period
    """
    if not date or not holidays:
        return False
    
    for holiday in holidays:
        try:
            start = parse_date(holiday.get('start'))
            end = parse_date(holiday.get('end'))
            if start and end and start <= date <= end:
                return True
        except (KeyError, TypeError, AttributeError):
            # Skip malformed holiday entries
            continue
    return False


def calculate_attendance(attended, total):
    """Calculate attendance percentage"""
    if total == 0:
        return 0.0
    return (attended / total) * 100


def calculate_safe_skip(attended, total, threshold=SUBJECT_THRESHOLD):
    """
    Calculate how many classes can be safely skipped while maintaining threshold
    
    Formula derivation:
    - Requirement: attendance% >= threshold (60% per-subject, 75% overall)
    - After skipping 'x' classes: attended / (total + x) >= threshold%
    - Rearranging: attended >= threshold% * (total + x)
    - Solve for x: x <= (attended - threshold% * total) / threshold%
    
    Args:
        attended: Number of classes attended so far
        total: Total classes conducted so far
        threshold: Minimum attendance percentage required (default 60% for subjects)
    
    Returns:
        int: Maximum number of classes that can be skipped safely
    
    Example (60% threshold):
        Attended: 80 classes, Total: 100 classes
        Current %: 80%
        Safe skip: (80 - 0.60*100) / 0.60 = (80 - 60) / 0.60 = 33.3 ≈ 33 classes
        After skipping 33: 80/(100+33) = 60.15% (still safe)
    """
    # Edge case validation
    if total == 0 or attended < 0 or total < 0:
        return 0
    
    if threshold <= 0 or threshold > 100:
        threshold = 75  # Default fallback
    
    # Calculate maximum classes that can be skipped
    # Formula: skips = (attended - threshold% * total) / threshold%
    try:
        threshold_decimal = threshold / 100.0
        safe = int((attended - threshold_decimal * total) / threshold_decimal)
        return max(0, safe)  # Never return negative
    except (ZeroDivisionError, OverflowError):
        return 0


def get_attendance_status(percentage, is_overall=False):
    """
    Get status text and color based on percentage
    
    Args:
        percentage: Attendance percentage
        is_overall: If True, use 75% threshold (overall); else use 60% (per-subject)
    
    Returns:
        tuple: (status_text, color)
    """
    threshold = OVERALL_THRESHOLD if is_overall else SUBJECT_THRESHOLD
    
    if percentage >= threshold + 10:  # 10% buffer = Excellent
        return ("Safe", COLOR_SAFE)
    elif percentage >= threshold:
        return ("Warning", COLOR_WARNING)
    else:
        return ("At Risk", COLOR_RISK)


def get_subject_status(percentage):
    """Get status for individual subject (60% threshold)"""
    if percentage >= 75:
        return ("Excellent", COLOR_SAFE)
    elif percentage >= 60:
        return ("Safe", COLOR_WARNING)
    else:
        return ("At Risk", COLOR_RISK)


def get_overall_status(percentage):
    """Get status for overall attendance (75% threshold)"""
    if percentage >= 85:
        return ("Excellent", COLOR_SAFE)
    elif percentage >= 75:
        return ("Safe", COLOR_WARNING)
    else:
        return ("At Risk", COLOR_RISK)
