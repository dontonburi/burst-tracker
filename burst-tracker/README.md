# 🗂️ Burst Tracker

A GitHub-hosted database and live dashboard for tracking incoming check burst pressure data across film manufacturers, machines, and lot codes.

---

## 📁 Repository Structure

```
burst-tracker/
├── data/
│   └── database.csv          # Master database (all records)
├── dashboard/
│   └── index.html            # Live dashboard (GitHub Pages)
├── scripts/
│   └── ingest.py             # CLI tool to merge new Excel uploads
├── .github/
│   └── workflows/
│       └── deploy.yml        # Auto-deploys dashboard on push
└── README.md
```

---

## 🚀 Setup (First Time)

### 1. Create the GitHub repo
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/burst-tracker.git
git add .
git commit -m "Initial database and dashboard"
git push -u origin main
```

### 2. Enable GitHub Pages
- Go to **Settings → Pages**
- Set **Source** to `GitHub Actions`
- Push any change to `main` — the dashboard will deploy automatically

Your live dashboard will be at:
`https://YOUR_USERNAME.github.io/burst-tracker/`

---

## 🔄 Updating the Database (New Excel File)

### Option A — Append new rows (most common)
```bash
python scripts/ingest.py path/to/new_data.xlsx
```
Deduplicates by `DATE + Lot Code + Machine + Lane + Weight`. Only truly new rows are added.

### Option B — Full replace
```bash
python scripts/ingest.py path/to/new_data.xlsx --replace
```
Replaces the entire `data/database.csv` with the new file's data.

### Option C — CSV upload in the dashboard
Open the live dashboard and click **Upload New Excel**. For `.csv` files, data merges instantly in-browser. For `.xlsx`, use Option A/B above.

### After updating, push to GitHub:
```bash
git add data/database.csv
git commit -m "Update database - $(date +%Y-%m-%d)"
git push
```
The GitHub Action auto-deploys the updated dashboard within ~30 seconds.

---

## ✅ Validate the Database
```bash
python scripts/ingest.py --validate
```

---

## 📊 Dashboard Features

- **KPI cards**: Total tests, Avg/Min/Max pressure, unique POs, lot codes, date range
- **Charts**:
  - Avg burst pressure over time (trend line)
  - Pressure by lane (bar)
  - Tests by machine (doughnut)
  - Pressure by manufacturer (bar)
  - Pressure distribution histogram
- **Filters**: Date range, Machine, Manufacturer, User, PO, Lane
- **Sortable table** with pagination (50 rows/page)
- **Color-coded pressure** values (green = good, amber = borderline, red = low)

---

## 📋 Database Schema (`data/database.csv`)

| Column | Description |
|---|---|
| DATE | Test date (YYYY-MM-DD) |
| Lot Code | Film lot identifier |
| Film Manufacturer | Supplier (Hong Kong, TKT, BMP GROUP) |
| PO | Purchase order number |
| Machine | Machine 1 or Machine 2 |
| Master Roll 1 / 2 | Roll identifiers |
| Weight | Film weight (2.0 OZ) |
| Tested By | Operator name |
| Lane | Lane number (1–12) |
| Pressure1–6 | Individual pressure readings |
| PressureAverage | Mean of available readings |
| PressureMIN | Minimum reading |
| PressureMAX | Maximum reading |

---

## 🛠️ Requirements (for ingest script)

```bash
pip install pandas openpyxl
```
