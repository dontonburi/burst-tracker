# 🗂️ BurstTrack — Alamance Foods Film Burst Pressure Tracker

A GitHub-hosted database and live dashboard for tracking incoming film check burst pressure data across suppliers, machines, lot codes, and purchase orders.

**Live Dashboard:** `https://dontonburi.github.io/burst-tracker/`

---

## 📋 How to Read a Burst Pressure Check

### What Is a Burst Pressure Test?

When a roll of film (packaging material) arrives from a supplier, Alamance Foods performs a **Film Compression (Burst) Test** to verify the film meets quality standards before it is used on production machines.

### Test Setup

Each test involves **one machine, one lot code, one roll of film**.

| Field | Description |
|---|---|
| Film Manufacturer | Supplier who made the film (e.g. Hong Kong, TKT, BMP GROUP) |
| Lot Code | Unique identifier for the film roll batch |
| PO # | Purchase Order number tied to this receipt |
| Machine # | Which sealing machine was used (Machine 1 / Machine 2) |
| Master Roll | Roll number(s) sampled from |
| Tested By | Operator who performed the test |
| Date of Test | When the test was performed |

### The 36-Reading Structure

Each test produces exactly **36 individual pressure readings**:

```
12 lanes × 3 pressure readings per lane = 36 total readings
```

| Component | Detail |
|---|---|
| Lanes | 12 lanes across the machine (Lane 1–12) |
| Readings per lane | 3 readings (up to 6 if more pops tested) |
| Total readings | 36 (minimum) per test |

**Example (Lane 1):**
```
Lane 1 | Flavor: Mango | Pressure 1: 1223 | Pressure 2: 950 | Pressure 3: 709
```

### How Average, Min, and Max Are Calculated

> ⚠️ **Important:** Average, Min, and Max are calculated from **all 36 individual readings** across all 12 lanes — NOT from per-lane averages.

```
All 36 readings → single Average / Min / Max for the test
```

This is the correct method because averaging-of-averages would skew results when lanes have different numbers of readings.

**Example:**
- 12 lanes × 3 readings = 36 pressure values
- Average = sum of all 36 ÷ 36
- Min = lowest single reading across all 36
- Max = highest single reading across all 36

### Interpreting Results

| Avg Pressure | Interpretation |
|---|---|
| ≥ 1000 psi | ✅ Good — film meets quality standard |
| 800–999 psi | ⚠️ Borderline — flag for review |
| < 800 psi | ❌ Concern — may indicate weak film or alignment issue |

Readings above **2,000 psi** or where both Min and Max are 0 are automatically excluded as data entry errors.

### Comments Field

Operators note any anomalies on the physical form, for example:
- `"Bag was sticky, 3 had bag header stained"`
- `"565 & 492 = pinholes, 232 & 580 ripped on the side"` — asterisked (*) readings indicate flagged pops

---

## 📁 Repository Structure

```
burst-tracker/
├── burst-tracker/
│   ├── data/
│   │   └── database.csv          # Master database (all records)
│   ├── dashboard/
│   │   └── index.html            # Live dashboard (GitHub Pages)
│   ├── scripts/
│   │   └── ingest.py             # CLI tool to merge new Excel uploads
│   └── README.md
└── .github/
    └── workflows/
        └── deploy.yml            # Auto-deploys dashboard on push
```

---

## 🚀 First-Time GitHub Setup

```bash
git init
git remote add origin https://github.com/dontonburi/burst-tracker.git
git add .
git commit -m "Initial load"
git push -u origin main
```

**Enable GitHub Pages:** Settings → Pages → Source: **GitHub Actions**

Dashboard will be live at: `https://dontonburi.github.io/burst-tracker/`

---

## 🔄 Updating the Database (New Excel File)

### Option A — Append new rows from Excel (most common)
```bash
python burst-tracker/scripts/ingest.py path/to/new_data.xlsx
```
Deduplicates automatically. Only new rows are added.

### Option B — Full database replace
```bash
python burst-tracker/scripts/ingest.py path/to/new_data.xlsx --replace
```

### Option C — Upload CSV in the dashboard
Open the dashboard → click **Upload New CSV** → select updated `database.csv`.

### After any update, push to GitHub:
```bash
git add burst-tracker/data/database.csv
git commit -m "Update data - $(date +%Y-%m-%d)"
git push
```
Dashboard auto-refreshes within ~30 seconds.

---

## ✅ Validate the Database
```bash
python burst-tracker/scripts/ingest.py --validate
```

---

## 📊 Dashboard Features

### Filters
- Date range (From / To)
- Machine (Machine 1, Machine 2)
- Manufacturer / Supplier
- Tested By (operator)
- PO #

### KPI Cards
| Card | What It Shows |
|---|---|
| Total Tests | Lane-level records matching current filters |
| Incoming Checks | Unique PO receipts (DATE + PO combinations) |
| Avg Pressure | Mean across all test-level averages |
| Min Pressure | Lowest single reading in filtered set |
| Max Pressure | Highest single reading in filtered set |
| Unique POs | Distinct purchase orders |
| Lot Codes | Distinct lot codes |

### Last 10 Tests Table
Shows the 10 most recently conducted tests with:
- Date, PO / Lot Code, Manufacturer, Machine, Tested By
- Total reading count, Test Avg, Min, Max

### Charts
| Chart | Description |
|---|---|
| Avg Pressure Over Time | Trend line — one data point per test |
| Bell Curve by Supplier | Normal distribution of pressure readings per manufacturer |
| Avg Pressure by Manufacturer | Bar chart comparing supplier averages |
| Tests by Machine | Bar chart showing test volume per machine |

### All Records Table
Full paginated table (50 rows/page) with all lane-level records. Sortable by any column. PO and Lot Code shown together for easy traceability.

**Pressure color coding:**
- 🟢 Green = ≥ 1000 psi (good)
- 🟡 Amber = 800–999 psi (borderline)
- 🔴 Red = < 800 psi (concern)

---


### Quality Monitoring Features

| Feature | What It Does |
|---|---|
| Pass/Fail Rate | Tracks % of individual readings at or above the adjustable threshold (default 800 psi). Threshold control is in the filter bar. |
| Control Chart (SPC) | Plots each test average against ±3σ control limits with the process mean. Auto-flags out-of-control signals using Western Electric rules: points beyond 3σ, 7-point downward runs, and 2-of-3 below 2σ. |
| Supplier Scorecard | Ranks suppliers by a composite quality score (avg pressure 40%, pass rate 35%, consistency 25%) with letter grades A–F, standard deviation, pass rate, and rising/falling trend. |
| Monthly Report | One click generates a printable HTML report for the most recent month: KPIs, supplier performance, tests below threshold, and a full test log. Saves as `burst-report_YYYY-MM.html`. |

## 📋 Database Schema (`data/database.csv`)

| Column | Description |
|---|---|
| DATE | Test date (YYYY-MM-DD) |
| Lot Code | Film lot identifier |
| Film Manufacturer | Supplier name |
| PO | Purchase Order number |
| Machine | Machine identifier |
| Master Roll 1 / 2 | Roll identifiers |
| Weight | Film weight (2.0 OZ) |
| Tested By | Operator name |
| Lane | Lane number (1–12) |
| Pressure1–Pressure6 | Individual pressure readings for this lane |
| PressureAverage | **Test-level** average (all 36 readings across all lanes) |
| PressureMIN | **Test-level** minimum reading |
| PressureMAX | **Test-level** maximum reading |

> Note: PressureAverage/MIN/MAX are the same value across all 12 lane rows belonging to the same test — they represent the full test, not the individual lane.

---

## 🛠️ Requirements (for ingest script)

```bash
pip install pandas openpyxl
```
