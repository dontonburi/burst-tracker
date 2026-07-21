# Pops Film Burst Tracker — Alamance Foods

Static dashboard + database for tracking incoming film burst-pressure QC checks.
All files live at the repo root; GitHub Actions deploys to Pages on every push to `main`.

## Files
- `index.html` — dashboard  ·  `scan.html` — AI photo scan  ·  `report.html` — monthly report
- `data/database.csv` — master database  ·  `scripts/ingest.py` — command-line Excel merge

## Updating data — two ways
1. **In the dashboard:** click **📂 Upload Data**, pick an Excel export (`.xlsx`) or a `database.csv`.
   It auto-cleans, de-duplicates and merges, then click **⬇ Download updated database.csv** and commit that file to `data/`.
2. **Command line:** `python scripts/ingest.py new_export.xlsx` then commit `data/database.csv`.
