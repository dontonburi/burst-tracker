#!/usr/bin/env python3
"""
Burst Tracker - Data Ingest Script
Usage:
  python scripts/ingest.py <new_excel_file.xlsx>        # Append new data
  python scripts/ingest.py <new_excel_file.xlsx> --replace  # Full replace
  python scripts/ingest.py --validate                   # Check database integrity
"""

import argparse
import pandas as pd
import numpy as np
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "database.csv"
SHEET_NAME = "DATABASE"
EXPECTED_COLUMNS = [
    "DATE", "Lot Code", "Film Manufacturer", "PO", "Machine",
    "Master Roll 1", "Master Roll 2", "Weight", "Tested By", "Lane",
    "Pressure1", "Pressure2", "Pressure3", "Pressure4", "Pressure5", "Pressure6",
    "PressureAverage", "PressureMIN", "PressureMAX"
]


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and clean incoming data."""
    df = df.copy()

    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]

    # DATE
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Strip whitespace from string fields
    for col in ["Film Manufacturer", "Machine", "Tested By", "Weight"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace("nan", "")

    # Normalize Weight variants
    weight_map = {"2.0OZ": "2.0 OZ", "2OZ": "2.0 OZ", "2.0 Oz": "2.0 OZ", "2.0 oz": "2.0 OZ"}
    df["Weight"] = df["Weight"].str.upper()
    for k, v in weight_map.items():
        df["Weight"] = df["Weight"].str.replace(k.upper(), v, regex=False)

    # PO and Lot Code as clean strings
    def safe_int_str(x):
        if pd.isna(x) or str(x).strip() in ("", "nan"):
            return ""
        try:
            return str(int(float(str(x))))
        except Exception:
            return str(x).strip()

    df["PO"] = df["PO"].apply(safe_int_str)
    df["Lot Code"] = df["Lot Code"].apply(safe_int_str)

    # Round PressureAverage
    df["PressureAverage"] = pd.to_numeric(df["PressureAverage"], errors="coerce").round(2)

    # Ensure all expected columns exist
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[EXPECTED_COLUMNS]


def load_db() -> pd.DataFrame:
    if not DB_PATH.exists():
        print(f"[INFO] No existing database found at {DB_PATH}. Starting fresh.")
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    df = pd.read_csv(DB_PATH, dtype=str)
    return df


def dedup_key(df: pd.DataFrame) -> pd.Series:
    """Composite key for deduplication: DATE + Lot Code + Machine + Lane + Weight."""
    def s(col):
        return df[col].astype(str).fillna("").str.strip()
    return s("DATE") + "|" + s("Lot Code") + "|" + s("Machine") + "|" + s("Lane") + "|" + s("Weight")


def ingest(excel_path: str, replace: bool = False):
    path = Path(excel_path)
    if not path.exists():
        print(f"[ERROR] File not found: {excel_path}")
        sys.exit(1)

    print(f"[INFO] Reading {path.name} ...")
    try:
        new_df = pd.read_excel(path, sheet_name=SHEET_NAME, header=0)
    except Exception as e:
        print(f"[ERROR] Could not read sheet '{SHEET_NAME}': {e}")
        sys.exit(1)

    new_df = clean_df(new_df)
    print(f"[INFO] Loaded {len(new_df)} rows from new file.")

    if replace:
        new_df.to_csv(DB_PATH, index=False)
        print(f"[OK] Database replaced with {len(new_df)} rows → {DB_PATH}")
        return

    existing_df = load_db()
    print(f"[INFO] Existing database: {len(existing_df)} rows.")

    if len(existing_df) == 0:
        combined = new_df
    else:
        existing_keys = set(dedup_key(existing_df))
        new_keys = dedup_key(new_df)
        truly_new = new_df[~new_keys.isin(existing_keys)]
        duplicates = len(new_df) - len(truly_new)
        print(f"[INFO] {len(truly_new)} new rows | {duplicates} duplicates skipped.")
        combined = pd.concat([existing_df, truly_new], ignore_index=True)

    # Sort by DATE descending
    combined["DATE"] = pd.to_datetime(combined["DATE"], errors="coerce")
    combined = combined.sort_values("DATE", ascending=False, na_position="last")
    combined["DATE"] = combined["DATE"].dt.strftime("%Y-%m-%d")

    combined.to_csv(DB_PATH, index=False)
    print(f"[OK] Database updated → {len(combined)} total rows → {DB_PATH}")


def validate():
    df = load_db()
    print(f"\n{'='*50}")
    print(f"  Burst Tracker Database Validation")
    print(f"{'='*50}")
    print(f"  Total rows:     {len(df)}")
    print(f"  Date range:     {df['DATE'].min()} → {df['DATE'].max()}")
    print(f"  Machines:       {sorted(df['Machine'].dropna().unique().tolist())}")
    print(f"  Manufacturers:  {sorted(df['Film Manufacturer'].dropna().unique().tolist())}")
    print(f"  Weights:        {sorted(df['Weight'].dropna().unique().tolist())}")
    print(f"  Unique POs:     {df['PO'].nunique()}")
    print(f"\n  Null counts (key fields):")
    for col in ["DATE", "Machine", "Lot Code", "PO", "PressureAverage"]:
        nulls = df[col].replace("", pd.NA).isna().sum()
        print(f"    {col:<20} {nulls} nulls")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Burst Tracker ingest tool")
    parser.add_argument("excel", nargs="?", help="Path to Excel file (.xlsx)")
    parser.add_argument("--replace", action="store_true", help="Replace entire database instead of appending")
    parser.add_argument("--validate", action="store_true", help="Print database stats and exit")
    args = parser.parse_args()

    if args.validate:
        validate()
    elif args.excel:
        ingest(args.excel, replace=args.replace)
    else:
        parser.print_help()
