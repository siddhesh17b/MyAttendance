# Bunkmeter

**Know exactly how many classes you can safely skip while staying above the attendance thresholds.**

---

## Install & Run

```bash
git clone https://github.com/siddhesh17b/Bunkmeter.git
cd Bunkmeter
pip install tkcalendar
python app.py
```

First run shows a setup wizard. Pick your batch, set semester dates, done.

---

## What it is

Desktop app to calculate how many classes you can skip while staying above attendance thresholds.

**Dual Threshold System:**
- **60% minimum per subject** - Each subject must stay above 60%
- **75% overall attendance** - Your average across all subjects must stay above 75%

It focuses on accuracy (day-by-day counting), minimal input (present-by-default), and practical controls (holiday handling, batch-aware timetables, quick full-day marking).

---

## Highlights

- Accurate, day-by-day class counting (no rough weekly estimates).
- Present-by-default model: you only record absences.
- Flexible CSV import: any time-slot format and batch syntax supported.
- Holiday and skipped-day aware: holidays and whole-day absences don't penalize attendance.
- Fast marking: left-click for per-class adjustments; right-click to mark/unmark whole day.
- Manual overrides and exportable reports for auditability.

---

## Key Features

| Feature | Description |
|---------|-------------|
| **60% Per-Subject** | Each subject tracked against 60% minimum |
| **75% Overall** | Average attendance must stay above 75% |
| **Accurate Counting** | Counts actual class occurrences (not estimates) |
| **Holiday Aware** | Holidays don't count against attendance |
| **Present by Default** | Only tracks absences - less clicking |
| **Multiple Classes/Day** | Handles subjects appearing twice (labs, tutorials) |
| **Custom Timetable** | Import your own schedule via CSV |
| **Any Batch Names** | Works with B1/B3, Group A/B, Section X, anything |
| **Any Time Slots** | 8am-9am, 2pm-4pm, any format works |
| **Manual Override** | Set exact attended/total when auto-calc is wrong |
| **Semester Progress** | Visual progress bar with days remaining |
| **Subject Details** | Click any subject to see absent dates & recovery info |
| **Responsive UI** | Resizes with window, works on any screen |
| **Offline** | No internet needed, all data stored locally |

---

## Custom Timetable

Don't want the default schedule? Import your own:

1. Check the template files included:
   - [`timetable_template_simple.csv`](timetable_template_simple.csv) - Basic format (your actual timetable)
   - [`timetable_template_flexible.csv`](timetable_template_flexible.csv) - Advanced format (custom times, batch groups)
2. Edit a template or create your own CSV
3. **Setup Tab** → **Import Custom Timetable**

### CSV Format:
```
Day,Time,Subject
MONDAY,09:00-10:00,Mathematics
MONDAY,10:00-11:00,Physics
MONDAY,02:00-04:00,CN Lab (B1&B3) / DAA Lab (B2&B4)
```

**Rules:**
- Days must be UPPERCASE (MONDAY, TUESDAY...)
- Time format is flexible (08:00-09:00, 8-9, 07:30-09:00)
- Batch-specific: `Subject1 (Batch1) / Subject2 (Batch2)`
- Lunch rows are auto-skipped

📖 See **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** for full details.

---

## Files

| File | What It Does |
|------|-------------|
| `app.py` | **Run this** |
| `data.json` | Your attendance data (auto-created) |
| `custom_timetable.json` | Your imported timetable |
| `timetable_template_simple.csv` | Simple CSV template (standard slots) |
| `timetable_template_flexible.csv` | Advanced CSV template (custom times, groups) |
| `COMPLETE_GUIDE.md` | Full step-by-step guide |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Won't start | `pip install tkcalendar` |
| ModuleNotFoundError | Run from inside the Bunkmeter folder |
| Wrong attendance | Check semester dates in Setup tab |
| Subject missing | Import a timetable with your subjects |
| Need fresh start | Setup Tab → Reset Data |

---

Made by **Siddhesh Bisen** • [GitHub](https://github.com/siddhesh17b)
