# MyAttendance

**Track your college attendance and know exactly how many classes you can skip.**

Most colleges require **75% minimum attendance**. Fall below and you can't sit for exams. This app helps you stay above that line.

![Mark Attendance Tab](screenshots/mark_attendance_tab.png)

---

## What This Does

You tell it your class schedule. It tracks which days you were absent. It tells you:
- Your current attendance %
- How many more classes you can safely skip
- Which subjects are at risk (below 75%)

---

## First Time Setup

### Step 1: Install Python
Download from [python.org](https://python.org). During install, **check "Add Python to PATH"**.

### Step 2: Get the App
Download this folder (green "Code" button → "Download ZIP") and extract it.

### Step 3: Install the Calendar Widget
Open terminal in the app folder and run:
```
pip install tkcalendar
```

### Step 4: Run It
```
python app.py
```

---

## First Run: What You'll See

1. **Batch Selection Popup** - Choose your batch (like B1, B2, Group A, etc.)
   - *What's a batch?* If your class is divided into groups for labs, that's your batch
   - If your college doesn't have batches, just pick any option

2. **Setup Tab** - Set your semester dates
   - Pick semester start and end dates (check your college calendar)
   - Add holidays (Diwali break, etc.)

![Setup Tab](screenshots/setup_tab.png)

3. **You're done!** The app now knows your schedule.

---

## Daily Use

### Mark Absences (Attendance Tab)
- **Left-click a date** → Opens side panel to mark specific subjects absent
- **Right-click a date** → Marks the ENTIRE day absent (quick option when you bunked everything)

The calendar shows:
| Color | Meaning |
|-------|---------|
| Green | All classes attended |
| Pink | Some classes missed |
| Dark Red | Whole day absent |
| Yellow | Holiday |
| Blue | Today |

### Check Your Status (Summary Tab)
See all subjects with:
- Current attendance %
- Classes you can still skip
- 🟢 Safe / 🔴 At Risk indicators

---

## Your Weekly Schedule (Timetable Tab)

View your entire week at a glance. Each subject gets a unique color.

![Timetable Tab](screenshots/timetable_tab.png)

---

## Using Your Own Timetable

The app has a default timetable built-in. To use your own:

1. Go to **Setup Tab** → Click **Export Timetable Template**
2. Open the CSV file, edit it with your schedule
3. Click **Import Custom Timetable** and select your file

📖 **[Full Timetable Guide →](COMPLETE_GUIDE.md)** - Detailed CSV format, batch-specific classes, troubleshooting

### CSV Format (3 columns, no header row):
```
MONDAY,09:00-10:00,Mathematics
MONDAY,10:00-11:00,Physics
TUESDAY,09:00-10:00,Chemistry
```

For batch-specific classes:
```
MONDAY,02:00-04:00,Physics Lab (B1) / Chemistry Lab (B2)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Run `pip install tkcalendar` |
| Wrong attendance showing | Check semester dates in Setup tab |
| Subject missing | Your timetable might not have it - import a custom one |
| Data lost after restart | Make sure `data.json` exists in the app folder |

---

## Files

| File | What it does |
|------|--------------|
| `app.py` | Run this to start |
| `data.json` | Your attendance data (auto-created) |
| `custom_timetable.json` | Your uploaded timetable (if any) |

---

Made by **Siddhesh Bisen** • [GitHub](https://github.com/siddhesh17b)
