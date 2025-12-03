# Timetable Upload Guide

## Overview
MyAttendance now supports custom timetable upload! Users can create their own timetable CSV file and import it into the application.

## CSV Format

### Structure
Your CSV file should follow this structure:
- **Column 1**: Day of the week (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY)
- **Column 2**: Time slot (format: HH:MM-HH:MM, e.g., 09:00-10:00)
- **Column 3**: Subject details

### Example CSV:
```csv
Day,Time,Subject
MONDAY,09:00-10:00,Minor
MONDAY,10:00-11:00,DM
MONDAY,11:00-12:00,DAA
MONDAY,12:00-01:00,Lunch Break
MONDAY,01:00-02:00,TOC
MONDAY,02:00-03:00,CN
TUESDAY,09:00-10:00,Minor
TUESDAY,10:00-11:00,CN
...
```

### Important Rules:

1. **Time Slots**: ✅ **FLEXIBLE** - Use ANY time format you want!
   - Common: 09:00-10:00, 10:00-11:00, etc.
   - **Early classes**: 08:00-09:00, 07:00-08:00
   - **Custom times**: 09:30-10:30, 14:15-15:15
   - **Any duration**: 08:00-10:00, 13:00-16:00
   - No limit on number of slots per day

2. **Subject Names**: ✅ **FULLY FLEXIBLE** - Use ANY subject name!
   - **No more code extraction** - Names are kept as-is
   - Simple: `Math`, `Physics`, `Chemistry`
   - With codes: `CS101 - Data Structures`, `MATH201`
   - With details: `Advanced Java Programming (Lab 3)`
   - **Custom names**: Anything you want!

3. **Batch Names**: ✅ **CUSTOM BATCHES** - Not limited to B1/B3 or B2/B4!
   - Still supports: `(B1&B3) / (B2&B4)` format
   - Also works with: `(GroupA) / (GroupB)`, `(Section1) / (Section2)`
   - **Any batch names** in parentheses

4. **Special Entries**:
   - `Lunch Break` or anything with "Lunch" - Ignored for attendance
   - Empty slots: Leave subject blank or use empty string
   - **All other names are tracked** - No restrictions!

5. **Batch-Aware Classes**:
   - Format: `Subject1 (BatchA) / Subject2 (BatchB)`
   - Example: `CN Lab (B1&B3) / DAA Lab (B2&B4)`
   - Works with custom batch names too!

## How to Upload

1. **Prepare Your CSV**:
   - Create a CSV file with structure above
   - Save as `my_timetable.csv` or any name you prefer
   - Ensure all days (MONDAY-SATURDAY) are included

2. **Export Template** (Optional):
   - Open MyAttendance app
   - Go to **Setup Tab**
   - Click **"Export Timetable Template"** button
   - This generates a CSV with current timetable format

3. **Import Your Timetable**:
   - Go to **Setup Tab**
   - Click **"Import Custom Timetable"** button
   - Select your CSV file
   - Review the preview/confirmation
   - Click **"Confirm Import"**

4. **Verify**:
   - Go to **Timetable Tab** to view imported schedule
   - Check **Mark Attendance Tab** to ensure subjects are listed correctly
   - Go to **Summary Tab** to see all tracked subjects

## Subject Naming

✅ **NEW: Full Flexibility!**
The app now keeps subject names exactly as you enter them:
- `Data Structures and Algorithms` → `Data Structures and Algorithms` (kept as-is)
- `Math 101` → `Math 101`
- `DM`, `DAA`, `TOC`, `CN` → Kept as-is
- **Use ANY naming convention** you prefer!

## Troubleshooting

### CSV Format Errors
- **Error**: "Invalid CSV format"
  - **Fix**: Ensure CSV has 3 columns: Day, Time, Subject
  - Check for missing commas or extra columns

### Time Slot Issues
- **Error**: "Invalid time format"
  - **Fix**: Use format HH:MM-HH:MM (24-hour format)
  - Example: `09:00-10:00`, `01:00-02:00`

### Missing Days
- **Error**: "Missing required days"
  - **Fix**: Include all days from MONDAY to SATURDAY
  - Each day must have all 8 time slots

### Subjects Not Appearing
- **Issue**: Subject not showing in attendance
  - **Check**: Subject name is not "Lunch Break", "Minor", "OE", or "Mentor-Mentee"
  - **Fix**: Rename subject if it contains excluded keywords

## Sample CSV Files

### Minimal Example (One Day):
```csv
Day,Time,Subject
MONDAY,09:00-10:00,Math
MONDAY,10:00-11:00,Physics
MONDAY,11:00-12:00,Chemistry
MONDAY,12:00-01:00,Lunch Break
MONDAY,01:00-02:00,Biology
MONDAY,02:00-03:00,English
MONDAY,03:00-04:00,
MONDAY,04:00-05:00,
```

### Full Week Example:
Available in the exported template from the app.

## Best Practices

1. ✅ **Backup First**: Export current timetable before importing new one
2. ✅ **Test Import**: Import and verify before deleting backup
3. ✅ **Consistent Naming**: Use same subject names throughout (e.g., "DAA" not "daa" or "Data Structures")
4. ✅ **Include All Days**: Always include Saturday even if no classes
5. ✅ **Clear Formatting**: Remove special characters that might cause parsing issues

## Advanced: Batch-Specific Schedule

If different batches have different labs:
```csv
Day,Time,Subject
WEDNESDAY,03:00-04:00,CN Lab (DT105) (B1&B3) / DAA Lab (DT111) (B2&B4)
WEDNESDAY,04:00-05:00,CN Lab (DT105) (B1&B3) / DAA Lab (DT111) (B2&B4)
```

This will show:
- **B1/B3 students**: CN Lab on Wednesday 3-5pm
- **B2/B4 students**: DAA Lab on Wednesday 3-5pm

## Support

For issues or questions:
- Check this guide first
- Review the exported template for correct format
- Ensure CSV encoding is UTF-8
- Contact: [GitHub Issues](https://github.com/siddhesh17b/MyAttendance/issues)

---

**Author**: Siddhesh Bisen  
**GitHub**: https://github.com/siddhesh17b  
**Project**: MyAttendance - Smart Attendance Tracker
