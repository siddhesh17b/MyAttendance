# Custom Timetable Upload - Implementation Summary

## ✅ What's Been Added

### 1. **New Files Created**
- `TIMETABLE_UPLOAD_GUIDE.md` - Comprehensive guide for users on CSV format and upload process
- `timetable_template.csv` - Sample CSV template with default timetable structure

### 2. **Updated Files**

#### `data_manager.py`
- Added `CUSTOM_TIMETABLE_FILE` constant for custom timetable storage
- **New Functions**:
  - `get_active_timetable()` - Returns custom timetable if exists, otherwise default
  - `export_timetable_to_csv()` - Export current timetable to CSV file
  - `import_timetable_from_csv()` - Import CSV and validate format
  - `reset_to_default_timetable()` - Delete custom timetable and restore default
- Updated `parse_timetable_csv()` to use active timetable
- Updated `get_subjects_for_day()` to use active timetable

#### `setup_tab.py`
- Added **Timetable Management Section** with 3 buttons:
  - 📥 Import Custom Timetable
  - 📤 Export Timetable Template  
  - 🔄 Reset to Default
- **New Methods**:
  - `import_timetable()` - Handles import and reinitializes subjects
  - `export_timetable()` - Calls export function
  - `reset_timetable()` - Resets to default and reinitializes subjects
- Imports: `export_timetable_to_csv`, `import_timetable_from_csv`, `reset_to_default_timetable`

#### `timetable_tab.py`
- Changed import from `TIMETABLE_DATA` to `get_active_timetable`
- Updated `get_subject_for_slot()` to use active timetable

#### `.gitignore`
- Added `custom_timetable.json` to ignore custom user timetables
- Updated to exclude data.json properly

## 📋 How It Works

### User Workflow:

1. **Export Template** (Optional):
   - User clicks "📤 Export Timetable Template" in Setup tab
   - Gets current timetable as CSV file
   - Can modify this CSV with their schedule

2. **Prepare CSV**:
   - Create CSV with columns: Day, Time, Subject
   - Follow format in `TIMETABLE_UPLOAD_GUIDE.md`
   - Include all 6 days (MONDAY-SATURDAY)
   - Use 8 hourly time slots (09:00-05:00)

3. **Import Custom Timetable**:
   - Click "📥 Import Custom Timetable" in Setup tab
   - Select CSV file
   - App validates:
     - ✅ Correct columns (Day, Time, Subject)
     - ✅ Valid days (MONDAY-SATURDAY)
     - ✅ Valid time slots (09:00-10:00, etc.)
     - ✅ Shows preview with subject count
   - User confirms import
   - Timetable saved to `custom_timetable.json`
   - Subjects automatically reinitialized
   - **Restart app** to apply changes

4. **Reset to Default**:
   - Click "🔄 Reset to Default"
   - Deletes `custom_timetable.json`
   - Reverts to hardcoded default timetable
   - Restart app to apply

### Technical Flow:

```
User Action → UI Button Click
    ↓
setup_tab.py method called
    ↓
data_manager.py function executed
    ↓
CSV validated/processed
    ↓
custom_timetable.json saved/deleted
    ↓
Subjects reinitialized with parse_timetable_csv()
    ↓
All tabs refreshed
    ↓
User sees updated timetable
```

### Data Structure:

**custom_timetable.json**:
```json
{
  "MONDAY": {
    "09:00-10:00": "Math",
    "10:00-11:00": "Physics",
    ...
  },
  "TUESDAY": { ... },
  ...
}
```

Same structure as hardcoded `TIMETABLE_DATA` dictionary.

## 🎯 Key Features

### ✅ Validation
- Checks CSV format (3 columns)
- Validates days (MONDAY-SATURDAY)
- Validates time slots (8 slots from 09:00-17:00)
- Shows preview before import
- Confirmation dialogs

### ✅ Backward Compatible
- Default timetable still works if no custom timetable
- `get_active_timetable()` handles fallback automatically
- No code changes needed in other modules (attendance_calendar, summary_tab)

### ✅ User-Friendly
- Clear instructions in guide
- Export template feature
- Preview and confirmation dialogs
- Success/error messages
- Reset to default option

### ✅ Batch-Aware
- Supports B1/B3 and B2/B4 batch labs
- Format: `Subject (Location) (B1&B3) / Subject (Location) (B2&B4)`
- Automatically filters based on selected batch

## 📝 CSV Format Rules

### Required Structure:
```csv
Day,Time,Subject
MONDAY,09:00-10:00,Math
MONDAY,10:00-11:00,Physics
...
```

### Time Slots (8 required per day):
- 09:00-10:00
- 10:00-11:00
- 11:00-12:00
- 12:00-01:00
- 01:00-02:00
- 02:00-03:00
- 03:00-04:00
- 04:00-05:00

### Subject Formats:
- Simple: `Math`, `Physics`, `Chemistry`
- Clean names: `DM`, `DAA`, `TOC`, `CN`
- Labs: `CN Lab`, `DAA Lab`, `Software Lab`
- Batch-specific: `CN Lab (B1&B3) / DAA Lab (B2&B4)`
- Special: `Lunch Break`, `Minor`, `MDM`, `OE`, `HONORS`

### Subject Name Handling:
The app keeps all subject names as-is (NO EXTRACTION):
- `Data Structures` → `Data Structures` (kept as-is)
- `Math 101` → `Math 101` (kept as-is)
- Only excludes names containing "Lunch"

## 🔧 Error Handling

### Import Errors:
- **Invalid CSV format**: Shows error, asks for correct format
- **Missing columns**: Shows error with required columns
- **Invalid day**: Shows warning, skips that row
- **Invalid time**: Shows warning, skips that row
- **Missing days**: Asks user to confirm or cancel

### Export Errors:
- **File write error**: Shows error message
- **No permission**: Shows error message

### Runtime:
- **Custom file corrupt**: Falls back to default timetable
- **Custom file missing**: Uses default timetable

## 📚 Documentation

### For Users:
- `TIMETABLE_UPLOAD_GUIDE.md` - Complete upload guide
- `timetable_template.csv` - Working example
- In-app instructions in Setup tab

### For Developers:
- All functions have docstrings
- Code comments explain logic
- Follows existing code style

## 🚀 Testing Checklist

✅ Export template works
✅ Import valid CSV works
✅ Import invalid CSV shows errors
✅ Reset to default works
✅ Timetable tab shows custom timetable
✅ Attendance marking works with custom subjects
✅ Summary tab shows custom subjects
✅ Batch-aware labs work with custom timetable
✅ Fallback to default if custom file missing
✅ Subject reinitialization preserves existing data

## 💡 Future Enhancements

Possible improvements:
- 📝 In-app CSV editor (no need for external file)
- 🌐 Import from Google Calendar
- 📱 QR code sharing (share timetable via QR)
- ☁️ Cloud storage integration
- 🔄 Timetable versioning (multiple semesters)
- 📊 Timetable comparison tool
- 🎨 Visual timetable builder (drag-and-drop)

## 📞 Support

For issues:
1. Check `TIMETABLE_UPLOAD_GUIDE.md`
2. Verify CSV format with template
3. Try export then re-import to test
4. Reset to default if issues persist
5. Check GitHub Issues

---

**Author**: Siddhesh Bisen  
**GitHub**: https://github.com/siddhesh17b  
**Project**: MyAttendance - Smart Attendance Tracker
