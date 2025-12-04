# Complete Guide - MyAttendance

A step-by-step walkthrough of every feature in the app.

---

## First Launch - Setup Wizard

When you run the app for the first time, a setup wizard appears:

### Step 1: Import Timetable (Optional)
- Click **"📥 Import Timetable CSV"** to upload your custom schedule
- Or skip this to use the default timetable
- If you import, batch options will auto-detect from your CSV

### Step 2: Select Your Batch
- Choose your batch/group (B1/B3, B2/B4, or custom names from CSV)
- Click **"Continue"**

The app opens with 4 tabs. Let's go through each one.

---

## Tab 1: ⚙️ Setup

This tab is split into left and right columns.

### Left Column

#### Batch Selection
- Radio buttons showing available batches
- Select your batch and click **"Update Batch"**
- Changing batch will recalculate all subjects

#### Semester Dates
- Two calendar widgets side by side
- **Left calendar**: Semester start date
- **Right calendar**: Semester end date
- Click **"Save Dates"** after selecting both

#### Holiday Periods
- List of all holidays (Diwali break, exam week, etc.)
- **"➕ Add Holiday Period"** → Opens dialog:
  1. Enter holiday name
  2. Pick start date from calendar
  3. Pick end date from calendar
  4. Click **"Save"**
- **"➖ Remove Holiday"** → Select a holiday and delete it
- Holidays don't count toward attendance (excluded from total)

### Right Column

#### Custom Timetable Management
- **"📥 Import Custom Timetable"** → Upload CSV file
  - ⚠️ This resets ALL attendance data (confirms first)
  - Subjects and batch options update automatically
- **"📤 Export Timetable Template"** → Download current timetable as CSV
  - Use this as a template to edit
- **"🔄 Reset to Default"** → Delete custom timetable, use built-in default

#### Skipped Days (Sick Leave, etc.)
- Track periods when you were completely absent
- **"➕ Add Skipped Period"** → Opens dialog:
  1. Enter reason (Sick, Personal, etc.)
  2. Pick start date
  3. Pick end date
  4. Click **"Save"**
  - ⚠️ All classes in this period are auto-marked absent
- **"➖ Remove Skipped Period"** → Removes period AND restores attendance marks

#### Reset Data
- **"🔄 Reset All Data"** → Clears:
  - All holidays
  - All skipped days
  - All absent dates
  - All manual overrides
- Keeps: Batch selection and semester dates

---

## Tab 2: 📋 Timetable

Read-only display of your weekly schedule.

### Layout
- Rows: Monday to Saturday
- Columns: Time slots (dynamic - shows all times from your timetable)
- Each cell shows the subject for that day/time

### Colors
- Each subject gets a unique color (hash-based)
- Same subject = same color everywhere
- "LUNCH" cells are gray

### Notes
- Saturday is treated as a working day (has classes)
- Only Sunday is a weekend
- Batch-specific subjects show only for your selected batch

---

## Tab 3: 📅 Mark Attendance (Main Tab)

Google Calendar-style monthly grid.

### Navigation
- **"◀ Prev"** → Previous month
- **"Next ▶"** → Next month
- **"Today"** → Jump to current month

### Calendar Colors
| Color | Meaning |
|-------|---------|
| 🟢 Soft Green | All classes present |
| 🩵 Cyan | Some classes absent |
| 🔴 Dark Red | Completely skipped (all absent) |
| 🟡 Yellow | Holiday |
| 🔵 Light Blue | Today |
| ⚪ White | Future (outside semester) |
| 🟣 Soft Purple | Future (within semester) |
| ⬜ Light Gray | Sunday (no classes) |

### Left-Click a Date
Opens side panel with:

1. **Date header** - Shows "December 04, 2024 (Wednesday)"
2. **Close button (✕)** - Clears selection
3. **"🏖️ Mark as Holiday"** button - Toggle this day as holiday
4. **Checkboxes for each subject**:
   - ✅ Checked = Present (default)
   - ⬜ Unchecked = Absent
   - If a subject has multiple classes that day, shows:
     - "Physics Lab (Class #1)"
     - "Physics Lab (Class #2)"
5. **"💾 Save Attendance"** button - Saves your changes

### Right-Click a Date
Quick toggle for entire day:
- **Right-click normal day** → Marks ALL subjects absent (completely skipped)
- **Right-click skipped day** → Marks ALL subjects present (removes absences)
- Also adds/removes entry in "Skipped Days" list in Setup tab

### Restrictions
- ❌ Cannot mark future dates (shows info message)
- ❌ Cannot mark dates outside semester period

---

## Tab 4: 📊 Summary (Dashboard)

Your attendance headquarters.

### Semester Progress Bar
- Visual bar showing semester completion %
- Color changes: Green (early) → Yellow (mid) → Red (ending soon)
- Shows "X days left" badge

### Stats Cards (Top Row)
| Card | Shows |
|------|-------|
| 📚 Total Subjects | Number of subjects |
| 📊 Average | Overall attendance % |
| ✅ Excellent/Safe | Subjects at 75%+ |
| ⚠️ At Risk | Subjects below 75% |

### Subject Table
| Column | Meaning |
|--------|---------|
| Subject | Subject name |
| Attended | Classes you attended |
| Total | Classes held so far |
| Remaining | Future classes till semester end |
| Percentage | Your attendance % |
| Progress | Visual bar with 🟢🟡🔴 |
| Status | 🟢 Excellent (≥85%) / 🟡 Safe (75-84%) / 🔴 At Risk (<75%) |
| Can Skip | How many more you can miss |
| Action | "✏️ Edit" or "📝 Manual" if override active |

### Sorting
- Click any column header to sort
- Click again to reverse order

### Subject Details Panel (Right Side)
**Single-click any row** to see:
- Subject name
- Statistics (attended/total/remaining/weekly count)
- Status indicator (🟢🟡🔴)
- **Absent Dates List** - All dates you were absent (scrollable)
- **Recovery Calculation** - If at risk, shows "Need X more classes to reach 75%"
- **"✏️ Edit Attendance"** button

### Manual Override
**Double-click any row** to open override dialog:

1. Shows current calculated values
2. Enter **Total Classes Held** (actual number)
3. Enter **Classes Attended** (actual number)
4. Click **"💾 Save Override"**

Use this when:
- Professor cancelled classes
- Extra classes were held
- You attended makeup classes
- Timetable doesn't match reality

To remove override:
- Double-click subject
- Click **"🔄 Clear Override"**

### Export Report
- Click **"📄 Export Report"** button
- Saves `attendance_report_YYYYMMDD_HHMMSS.txt` file
- Contains all subjects with present/total/percentage/status

---

## Custom Timetable Format

### Template Files Included
Two ready-to-use templates are included:

| Template | Description |
|----------|-------------|
| `timetable_template_simple.csv` | Standard hourly slots (09:00-10:00), your actual college timetable |
| `timetable_template_flexible.csv` | Custom time slots (07:30-09:00, 08:30-10:00), Group A/B batches |

### CSV Structure (3 columns with header)
```
Day,Time,Subject
MONDAY,09:00-10:00,Mathematics
```

### Example
```
Day,Time,Subject
MONDAY,09:00-10:00,Mathematics
MONDAY,10:00-11:00,Physics
MONDAY,11:00-12:00,Lunch
MONDAY,02:00-04:00,CN Lab (B1&B3) / DAA Lab (B2&B4)
TUESDAY,09:00-10:00,Chemistry
TUESDAY,10:00-12:00,Software Lab (Group A) / Hardware Lab (Group B)
```

### Rules

| Element | Requirement |
|---------|-------------|
| Day | UPPERCASE: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY |
| Time | Any format: 09:00-10:00, 9-10, 0900-1000, 2:00 PM-4:00 PM |
| Subject | Any name - kept exactly as entered |
| Lunch | Name it "Lunch" - automatically skipped |
| Batches | Format: `Subject1 (Batch1) / Subject2 (Batch2)` |

### Batch-Specific Classes
For classes that differ by batch:
```
CN Lab (B1&B3) / DAA Lab (B2&B4)
```
- If you select B1&B3 → Shows "CN Lab"
- If you select B2&B4 → Shows "DAA Lab"

Batch names are auto-detected from parentheses in your CSV.

---

## The 75% Formula

### Safe to Skip Calculation
```
Safe to Skip = floor((Attended - 0.75 × Total) / 0.25)
```

### Example
- Attended: 30 classes
- Total: 36 classes
- Calculation: (30 - 27) / 0.25 = 12
- **Result: You can skip 12 more classes**

### Recovery Calculation (When Below 75%)
```
Classes Needed = ceil((0.75 × Total - Attended) / 0.25)
```

### Example
- Attended: 20 classes
- Total: 36 classes
- Current: 55.6%
- Calculation: (27 - 20) / 0.25 = 28
- **Result: Need 28 more classes without absence to reach 75%**

---

## Mouse & Keyboard Actions

| Action | How |
|--------|-----|
| Mark single subjects absent | Left-click date → Uncheck subjects → Save |
| Mark entire day absent | Right-click date |
| Mark entire day present | Right-click already-skipped date |
| View subject details | Single-click row in Summary table |
| Override attendance | Double-click row in Summary table |
| Sort table | Click column header |
| Reverse sort | Click same header again |
| Scroll dashboard | Mouse wheel (when cursor outside table) |
| Scroll table | Mouse wheel (when cursor over table) |
| Navigate months | "◀ Prev" / "Next ▶" buttons |
| Jump to today | "Today" button |

---

## Data Files

| File | What It Stores | Safe to Delete? |
|------|----------------|-----------------|
| `data.json` | All attendance data, holidays, settings | ❌ NO - loses everything |
| `custom_timetable.json` | Your imported timetable | ✅ Yes - reverts to default |

### Backup
Copy `data.json` to backup your data.

### Full Reset
Delete both files and restart the app for fresh install.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't start | Run `pip install tkcalendar` |
| ModuleNotFoundError | Run from inside MyAttendance folder |
| Wrong attendance % | Check semester dates in Setup tab |
| Subject missing | Import timetable with your subjects |
| "0 classes" everywhere | Semester hasn't started yet |
| "Remaining" shows 0 | Semester ended or date calculation issue |
| Import fails | Check CSV format - days UPPERCASE, no header |
| Batch not appearing | CSV needs format: `Subject (BatchName)` |
| Future dates locked | By design - can't mark future attendance |
| Scroll not working | Move cursor to table area for table scroll |
| Want fresh start | Setup Tab → Reset Data |
| Complete reset | Delete data.json + custom_timetable.json |

---

## Tips

1. **Mark absences daily** - Easier than remembering later
2. **Use right-click** for sick days - Faster than clicking each subject
3. **Check "Can Skip"** before bunking - Know your limits
4. **Export reports** before exams - Keep a record
5. **Backup data.json** monthly - Don't lose your data
6. **Double-click to fix** - Use override when timetable doesn't match reality

---

Made by **Siddhesh Bisen** • [GitHub](https://github.com/siddhesh17b)
