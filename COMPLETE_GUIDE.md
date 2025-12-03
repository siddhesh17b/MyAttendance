# Custom Timetable Guide

Want to use your own class schedule instead of the default? Here's how.

---

## Quick Steps

1. **Setup Tab** → **Export Timetable Template** (saves a sample CSV)
2. Open CSV in Excel/Notepad, replace with your classes
3. **Setup Tab** → **Import Custom Timetable**
4. Select your batch when prompted
5. Done! Check **Timetable Tab** to verify

---

## CSV Format Rules

Your CSV file needs exactly **3 columns** in this order:

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Day | Time | Subject |
| `MONDAY` | `09:00-10:00` | `Mathematics` |

### Rules:
- **No header row** (don't put "Day,Time,Subject" at the top)
- **Days must be uppercase**: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY
- **Time can be any format**: 09:00-10:00, 9-10, 0900-1000 (flexible)
- **Subject name**: Anything except "Lunch" (lunch periods are skipped)

---

## Batch-Specific Classes

If different batches have different classes at the same time, write both in one cell:

```
MONDAY,02:00-04:00,Physics Lab (B1) / Chemistry Lab (B2)
```

The app reads the batch in parentheses and shows the right one for you.

**Format:** `Subject1 (Batch1) / Subject2 (Batch2)`

You can use any batch names: B1, B2, Group A, Section X, etc.

---

## Example CSV

```
MONDAY,09:00-10:00,Mathematics
MONDAY,10:00-11:00,Physics
MONDAY,11:00-12:00,Chemistry
MONDAY,12:00-01:00,Lunch
MONDAY,02:00-04:00,Physics Lab (B1) / Chemistry Lab (B2)
TUESDAY,09:00-10:00,English
TUESDAY,10:00-11:00,Computer Science
```

---

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Invalid day name" | Day not uppercase | Change `Monday` to `MONDAY` |
| "No subjects found" | Wrong batch selected | Re-import and pick correct batch |
| Subject not showing | Typo in subject name | Check spelling in CSV |
| Import failed | CSV has header row | Delete the first row if it says "Day,Time,Subject" |

---

## Reset to Default

Made a mistake? **Setup Tab** → **Reset to Default Timetable**

This removes your custom timetable and brings back the built-in schedule.

---

## After Import

- Your old attendance data is **cleared** (fresh start with new timetable)
- Go to **Timetable Tab** to verify your schedule looks correct
- Start marking attendance in **Attendance Tab**
