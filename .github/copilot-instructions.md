# MyAttendance – Smart Attendance Tracker

## Project Overview
Python desktop app helping students manage attendance and calculate safe class skips while maintaining 75% attendance threshold. Built with Tkinter using tabbed interface with **Google Calendar-style monthly attendance marking** where all classes are marked present by default. Students can left-click dates to mark individual subjects absent OR right-click to mark entire day absent. Timetable data is hardcoded (no CSV runtime dependency).

## File Structure (7 Files) - Total: ~65 KB
```
app.py                  # 4.5 KB  - Main entry point, 1400x900 window, first-run wizard
data_manager.py         # 7.2 KB  - Hardcoded timetable, subject extraction, JSON persistence
calculations.py         # 2.6 KB  - Attendance math, date calculations, weeks elapsed
setup_tab.py            # 8.5 KB  - Configuration UI: batch, semester dates, holidays, reset
timetable_tab.py        # 6.6 KB  - Visual weekly timetable display (read-only)
attendance_calendar.py  # 23.8 KB - Google Calendar-style monthly view (semester validation, Saturday fix)
summary_tab.py          # 8.7 KB  - Dashboard with statistics and report export
```
**Note**: Code prioritizes readability with proper spacing, comments, and docstrings

## Architecture Constraints
- **Minimal files**: 7 Python files organized by responsibility - no complex packages or deep nesting
- **Local-only storage**: Use JSON file (`data.json`) for persistence - no databases, no internet  
- **Standard libraries only**: Tkinter (ttk for tabs), datetime, json - use tkcalendar for calendar widget
- **Hardcoded Timetable**: TIMETABLE_DATA dictionary embedded in data_manager.py (no CSV runtime dependency)
- **Present by Default**: All classes marked present until today; users click to mark absences

## Import Patterns
**app.py imports:**
```python
from data_manager import load_data, save_data, get_app_data, parse_timetable_csv
from setup_tab import SetupTab
from timetable_tab import TimetableTab
from attendance_calendar import AttendanceCalendar
from summary_tab import SummaryTab
```

**Tab modules import:**
```python
# setup_tab.py
from data_manager import get_app_data, save_data
from calculations import calculate_weeks_elapsed
from tkcalendar import Calendar

# timetable_tab.py
from data_manager import get_app_data, TIMETABLE_DATA

# attendance_calendar.py
from data_manager import get_app_data, save_data, get_subjects_for_day
from tkcalendar import Calendar

# summary_tab.py
from data_manager import get_app_data
from calculations import calculate_attendance, calculate_safe_skip, calculate_weeks_elapsed
```

**Key principle:** `data_manager` and `calculations` are utility modules with no UI dependencies. Tab modules (`setup_tab`, `timetable_tab`, `attendance_calendar`, `summary_tab`) depend on utilities. `app.py` orchestrates tab creation.

## Core Business Logic

### Hardcoded Timetable Data
- TIMETABLE_DATA dictionary in data_manager.py contains weekly schedule (dictionary-based structure)
- Structure: `{"MONDAY": {"09:00-10:00": "Subject", "10:00-11:00": "Subject", ...}, ...}`
- Schedule runs from 9:00 AM to 5:00 PM, hourly slots (8 slots per day)
- Time slot keys: "09:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-01:00", "01:00-02:00", "02:00-03:00", "03:00-04:00", "04:00-05:00"
- Remove course codes (e.g., `24HS03TH0301-DM` → `DM`)
- Track theory and lab classes separately (e.g., "CN" and "CN Lab" as distinct subjects)
- Batch selection (B1/B3 or B2/B4) determines lab assignments on Wednesday/Thursday/Friday
- Track ALL entries including Minor, MDM, OE, HONORS as regular subjects
- Multi-hour classes (like labs 2-4pm) have same subject duplicated across consecutive time slots
- Source: timetable.md (detailed class schedule reference)
- Variable lunch timing: Monday/Tuesday/Thursday/Friday/Saturday at 12:00-01:00, Wednesday at 01:00-02:00

### Automatic Attendance Calculation
```python
# All classes are PRESENT by default until today
# Calculate total expected classes based on weekly count
weekly_count = TIMETABLE_DATA[day][time][subject_name]
weeks_elapsed = calculate_weeks(semester_start, today, holidays)
total_classes = weekly_count * weeks_elapsed

# Calculate attended by subtracting absences
absent_count = len([d for d in subject["absent_dates"] if d <= today])
attended_classes = total_classes - absent_count
```

**User Override**: Allow manual adjustment of total classes via override button; absences marked via calendar UI

### Attendance Calculation Formula
```python
# Present by default model
attended = total_classes - len(absent_dates_until_today)
attendance_percentage = (attended / total) * 100
safe_to_skip = floor((attended - 0.75 * (total + skips)) / 0.25)
```

### 75% Threshold Rule
- **Below 75%**: RED text/background - student at risk
- **75% or above**: GREEN indicator - safe zone
- Display exact number of classes safe to skip before dropping below 75%
- Real-time recalculation when any data changes (bunk marked, attendance edited, dates modified)

## Data Structure Pattern
Store in `data.json`:
```json
{
  "batch": "B1/B3",
  "semester_start": "2025-08-01",
  "semester_end": "2025-12-15",
  "holidays": [
    {"start": "2025-10-20", "end": "2025-10-27", "name": "Diwali Break"}
  ],
  "subjects": [
    {
      "name": "DM",
      "weekly_count": 3,
      "total_override": null,
      "absent_dates": ["2025-11-15", "2025-11-22"]
    }
  ]
}
```

**Key fields:**
- `absent_dates`: List of ISO dates when class was marked absent (PRESENT BY DEFAULT MODEL)
- `total_override`: If null, auto-calculate from weekly_count; if set, use manual value
- `weekly_count`: Parsed from TIMETABLE_DATA (how many times subject appears per week)
- Save after: setup changes, calendar absence marks, holiday additions

## Key UI Components (Tabbed Interface)

### Tab 1: Setup & Configuration (setup_tab.py)
- Batch selection radio buttons (B1/B3 or B2/B4)
- Side-by-side Calendar widgets for semester start/end date selection
- Holiday period management (add/remove date ranges with names)
- **Reset Data Section**: Clear all holidays, absent dates, and overrides with confirmation dialog
  - Preserves batch selection and semester dates
  - Shows warning message before reset
  - Success notification after completion
- Editable at any time, triggers recalculation on save

### Tab 2: Weekly Timetable View (timetable_tab.py)
- **READ-ONLY** visual display of weekly schedule
- Layout: Days in rows (Monday-Saturday), time slots in columns (09:00-17:00)
- Color-coded subjects:
  - Blue: Theory classes (DAA, TOC, CN, DM)
  - Purple: Lab sessions
  - Orange: Minor/MDM/OE/Honors (not tracked for attendance)
  - Gray: Lunch breaks
- Batch-aware: Shows correct labs based on B1/B3 or B2/B4 selection
- Legend at bottom explaining color scheme
- Automatically updates when batch changes
- Shows all 6 days including Saturday

### Tab 3: Google Calendar-Style Attendance (attendance_calendar.py)
- **PRIMARY INTERFACE**: Monthly grid view similar to Google Calendar
- **Present by Default**: All classes until today automatically marked present
- **Monthly Grid**: Shows entire month with 7-day week layout (Mon-Sun)
- **Navigation**: Previous/Next month buttons, "Today" button to jump to current month
- **Color-Coded Days**:
  - Light Green (#E8F5E9): All classes present
  - Light Red (#FFEBEE): Some classes marked absent
  - Light Yellow (#FFF9C4): Holiday
  - Light Blue (#E3F2FD): Today
  - Light Gray (#F5F5F5): Sunday only (Saturday has classes)
  - Very Light Gray (#FAFAFA): Future dates / Outside semester range
- **Interaction Methods**:
  - **Left-click date**: Open side panel to mark individual subjects
  - **Right-click date**: Mark ALL subjects for that day as absent instantly
- **Side Panel Features** (70/30 split layout):
  - Date and day name header
  - Close button (✕) to clear selection
  - Holiday toggle button (🏖️ Mark as Holiday/Regular Day)
  - List of subjects with checkboxes (PRE-CHECKED = present)
  - Uncheck subjects to mark as absent
  - Status indicators: ✓ (green) or ✗ (red)
  - Save button to update attendance
- **Key Implementation Details**:
  - `self.check_vars` is instance variable to persist checkbox states
  - `save_attendance()` method properly accesses check_vars for saving
  - Right-click bound with `<Button-3>` event
  - Validation prevents marking future dates or out-of-semester dates
  - Semester date validation: `get_day_status()` checks if date is within semester_start and semester_end
  - Weekend logic: Only Sunday (day_idx == 6) marked as weekend, Saturday has classes
- **Holiday Management**: Single-click toggle for marking individual days as holidays
- Confirmed absences save to absent_dates[] and update day colors
- Visual legend at bottom explaining color scheme

### Tab 4: Summary Dashboard (summary_tab.py)
- Consolidated view: all subjects in sortable table
- Columns: Subject | Attended | Total | Attendance % | Status | Safe Skips
- **Calculation**: Attended = Total - len(absent_dates_until_today)
- Status column: RED text if <75%, GREEN if ≥75%
- Quick stats cards: overall attendance average, subjects at risk count, total subjects
- Export report button (generates text file summary)

## Function Organization
Keep functions focused and named clearly:

**Timetable Parsing:**
- `parse_timetable_csv(batch) -> dict[subject: weekly_count]` (parses TIMETABLE_DATA dict, not CSV)
- `extract_subject_name(cell_value) -> clean_name` (removes course codes)
- `get_subjects_for_day(day_name, batch) -> list[subjects]`

**Date & Time Calculations:**
- `calculate_weeks_elapsed(start, end, holidays) -> int`
- `is_date_in_holidays(date, holidays) -> bool`
- `calculate_total_classes(weekly_count, weeks) -> int`

**Attendance Math:**
- `calculate_attendance(total, absent_dates) -> percentage` (attended = total - len(absent_dates))
- `calculate_safe_skip(attended, total, threshold=75) -> classes_to_skip`
- `get_attendance_status(percentage) -> ("Safe"|"At Risk", color)`

**Data Persistence:**
- `save_data()` / `load_data()` - JSON read/write
- `initialize_default_data()` - first-run setup

**UI Handlers:**
- `on_batch_select()`, `on_semester_dates_change()`, `on_holiday_add()` (setup_tab.py)
- `on_date_selected(date)` → show subjects with checkboxes (attendance_calendar.py)
- `show_subjects_for_date(date, subjects)` - pre-checked checkboxes, uncheck to mark absent
- `mark_absences(date, unchecked_subjects)` - add to absent_dates[] array
- `refresh()` - recalculate and redraw (each tab has own refresh method)

## Module Responsibilities

### `app.py` - Main Entry Point (~140 lines)
- Window initialization: 1400x900 pixels, "MyAttendance - Smart Attendance Tracker" title
- First-run setup wizard (batch selection dialog, initializes subjects with absent_dates=[])
- BunkBuddyApp class creates SetupTab, TimetableTab, AttendanceCalendar, SummaryTab
- `main()` function runs the application
- refresh_all_tabs() method to update all 4 tabs when data changes
- Readable code with proper docstrings and spacing

### `data_manager.py` - Data Layer (~250 lines)
- **TIMETABLE_DATA** - Hardcoded weekly schedule dictionary (dictionary-based: day -> time_slot -> subject)
- Structure: `{"MONDAY": {"09:00-10:00": "Minor", "10:00-11:00": "24HS03TH0301-DM (DT203)", ...}, ...}`
- Time slots: 9am-5pm using explicit keys like "09:00-10:00", "10:00-11:00", etc.
- `parse_timetable_csv(batch)` - Iterates dictionary structure to extract subjects with weekly counts
- `extract_subject_name(cell)` - Clean course codes (24CS01TH0302-DAA → DAA), excludes Minor/OE/Mentor-Mentee
- `get_subjects_for_day(day, batch)` - Returns list of subjects scheduled for a specific day
- `save_data()` / `load_data()` - JSON persistence
- `get_app_data()` - Global data accessor
- Manages app_data dict: {batch, semester_start, semester_end, holidays, subjects[{absent_dates}]}
- Clean code with proper error handling

### `calculations.py` - Math & Logic (~90 lines)
- `calculate_weeks_elapsed(start, end, holidays)` - Exclude holiday periods
- `calculate_total_classes(weekly_count, weeks)` - Auto-compute total
- `calculate_attendance(attended, total)` - Percentage calculation
- `calculate_safe_skip(attended, total)` - Classes safe to skip while staying ≥75%
- `get_attendance_status(percentage)` - Returns ("Safe"|"At Risk", color_code)
- `parse_date(str)` / `is_date_in_holidays(date, holidays)` - Date utilities
- Clean, focused utility functions with proper docstrings

### `setup_tab.py` - Configuration UI (~270 lines)
- `SetupTab` class with create() method
- Batch selection radio buttons (B1/B3 or B2/B4)
- Side-by-side Calendar widgets for start/end date selection
- Holiday management: TreeView list, add/delete buttons with dialog
- Event handlers: on_batch_update(), on_dates_update(), add_holiday(), delete_holiday()
- Saves to data.json and triggers refresh callback
- Returns tab frame for notebook.add()
- Readable code with proper spacing and comments

### `timetable_tab.py` - Weekly Timetable View (~150 lines)
- `TimetableTab` class with create() method
- Visual grid display: Days as rows (Monday-Saturday), time slots in columns (09:00-17:00)
- Canvas with scrollbar for large timetable
- Time slots: 8 hourly slots from 9am-5pm (matching TIMETABLE_DATA dictionary keys)
- get_subject_for_slot(day, time, batch) - Direct dictionary lookup: TIMETABLE_DATA[day][time_slot]
- extract_subject_name(cell) - Parses course codes from timetable data
- get_subject_colors(subject) - Returns color scheme based on subject type
- Color legend: Blue (theory), Purple (labs), Orange (minor/mdm/oe/honors), Gray (lunch)
- Batch-aware lab display (B1&B3 vs B2&B4) by parsing "/" separated entries
- Returns tab frame for notebook.add()
- Clean, well-commented code

### `attendance_calendar.py` - Google Calendar-Style Monthly View (~600 lines)
- `AttendanceCalendar` class with create() method
- **Google Calendar-style interface**: Monthly grid layout with day cells
- Month navigation: prev_month(), next_month(), go_to_today()
- Color-coded days: Green (present), Red (absent), Yellow (holiday), Blue (today), Gray (Sunday/future/outside semester)
- **Left-click**: on_date_clicked(date_str) - Shows subjects in side panel
- **Right-click**: on_date_right_clicked(date_str) - Marks ALL subjects absent instantly
- show_subjects_panel(date_str, subjects) - Side panel with PRE-CHECKED checkboxes
- save_attendance(date_str) - Saves checkbox states to absent_dates[] array
- clear_subjects_panel() - Closes side panel and shows placeholder
- toggle_holiday(date_str) - Mark/unmark single day as holiday
- is_holiday_date(date_str) - Check if date is in holiday list
- get_day_status(date_str) - Returns status: present/absent/holiday/no_class (validates semester dates)
- draw_calendar() - Renders monthly grid with 7-day week layout, binds click events (Saturday treated as weekday)
- **Layout**: 70/30 split (calendar grid + side panel)
- **Logic**: Checked = present (default), Unchecked = mark absent
- **Instance variables**: self.check_vars stores checkbox states for save_attendance()
- Close button (✕) to clear side panel selection
- Returns tab frame for notebook.add()
- Note: Longer file prioritizing readability with extensive documentation

### `summary_tab.py` - Dashboard UI (~270 lines)
- `SummaryTab` class with create() method
- Stats cards frame: Total subjects, Avg attendance %, Safe/At-risk counts
- TreeView table: Subject | Attended | Total | Attendance % | Status | Safe Skips
- **Calculation**: attended = total_classes - len(absent_dates)
- Color coding: RED text if <75%, GREEN if ≥75%
- export_report() - Generates timestamped "MyAttendance" text file
- refresh() method recalculates all statistics and reloads data
- display_stats() helper for rendering stats cards
- Returns tab frame for notebook.add()
- Well-documented with proper spacing and comments

## Development Workflow
- **Run**: `python app.py` - starts main window with 4 tabs
- **Test manually**: No automated tests - verify calendar-based attendance marking workflow
- **Debug**: Print statements or check data.json file contents (especially absent_dates arrays)
- **Dependencies**: `pip install tkcalendar` (only external dependency)
- **Data Model**: Remember all classes are PRESENT by default; only absences are tracked
- **Tab Order**: Setup → Timetable → Mark Attendance → Summary

## Code Quality Standards
- **Readability First**: Prioritize code clarity over brevity
- **Proper Documentation**: Include docstrings for classes and methods
- **Descriptive Names**: Use full variable names like `attendance_percentage` not `ap`
- **Proper Spacing**: Blank lines between functions, logical grouping of code
- **Comments**: Explain complex logic, business rules, and non-obvious code
- **No Unused Code**: Keep codebase clean - no commented-out code or unused imports
- **Consistent Formatting**: Use consistent indentation and style throughout
- **Group Related Code**: Keep related functions together (e.g., all UI handlers, all calculations)

## Edge Cases to Handle
- Division by zero when total classes = 0
- More absences than total classes possible (show warning, highlight in red)
- Calendar date selection before semester starts or after semester ends (show as gray/future - handled by get_day_status)
- Clicking date with no classes scheduled (show "No classes" message, clear side panel)
- Saturday treated as working day (only Sunday is weekend)
- Marking same date absent multiple times (prevent duplicates in absent_dates[])
- Overlapping holiday periods (validate before adding in setup, single-day toggle in calendar)
- First-time launch with no `data.json` file (create default + show setup wizard with absent_dates=[])
- Holiday period spanning multiple weeks (correctly subtract from total calculations)
- Future dates: Don't mark as present/absent yet (only calculate up to today, disable future date clicks)
- Subjects not tracked for attendance: Minor, OE, Mentor-Mentee Meeting (visible in timetable, excluded from tracking)

## Visual Design Guidelines
- Use `ttk` themed widgets for modern look (not plain Tkinter widgets)
- Color scheme:
  - **GREEN (#28a745)**: Safe attendance (≥75%)
  - **RED (#dc3545)**: At-risk (<75%)
  - **BLUE (#007bff)**: Neutral/info elements
  - **GRAY (#6c757d)**: Read-only/disabled fields
- Font sizes: Title=14 bold, Headers=11 bold, Body=10 regular
- Padding: Consistent 10px margins, 5px internal padding
- Tables: Alternating row colors for readability
- Buttons: Clear labels with icons (if possible using Unicode symbols)

## Development Workflow Priority
1. **Phase 1**: Hardcoded timetable + absent_dates data structure + basic UI skeleton ✅
2. **Phase 2**: Setup tab with Calendar widgets + semester configuration ✅
3. **Phase 3**: Calendar-based attendance marking (present by default) ✅
4. **Phase 4**: Summary dashboard with statistics ✅
5. **Phase 5**: Timetable view tab (read-only visual display) ✅
6. **Phase 6**: Complete system overhaul - dictionary-based timetable structure ✅
7. **Phase 7**: Code cleanup, optimization, bug fixes ✅
8. **Phase 8**: Readability improvements - proper spacing, comments, documentation ✅
9. **Phase 9**: Enhanced features - right-click marking, improved save logic ✅
10. **Phase 10**: Window resize to 1400x900, app rename to "MyAttendance" ✅
## Implemented Features
- ✅ **Google Calendar-Style UI**: Monthly grid with color-coded days
- ✅ **Left-Click Marking**: Open side panel to mark individual subjects
- ✅ **Right-Click Quick Mark**: Mark entire day absent with one click (NOT holiday)
- ✅ **Holiday Management**: Toggle individual days or add date ranges
- ✅ **Reset Functionality**: One-click reset of all holidays and absent dates with confirmation
- ✅ **Export Report**: Generate timestamped text file with attendance summary
- ✅ **Real-time Updates**: All tabs refresh when data changes
- ✅ **Present by Default**: Only absences tracked, all other classes marked present
- ✅ **Batch-Aware Labs**: Correct lab display based on B1/B3 or B2/B4 selection
- ✅ **Semester Date Validation**: Dates before semester start or after end shown as gray/future
- ✅ **Saturday Working Day**: Only Sunday treated as weekend (Saturday has classes)
- ✅ **Author Credits**: All 7 Python files include "Author: Siddhesh Bisen, GitHub: https://github.com/siddhesh17b"sent
- ✅ **Batch-Aware Labs**: Correct lab display based on B1/B3 or B2/B4 selection

## Optional Features (Future Enhancements)
- **What-If Simulator**: Temporary calculation showing projected attendance if X classes are skipped
- **Undo/Redo**: Revert recent attendance changes
- **Backup/Restore**: Export and import data.json for backup purposes
- **Multi-Semester History**: Track attendance across multiple semesters
- **Email Notifications**: Alert when attendance drops below threshold
- **Mobile App**: Companion mobile application
- **Cloud Sync**: Sync data across multiple devices
