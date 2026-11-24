#!/usr/bin/env python3
"""
Cohort QA: counts, prevalence, duplicates, missingness, cluster coverage, and
sparse-unit flags.

Example
-------
python qa_cohort.py --data outputs/cohort_bdhs2022.csv \
  --outcome ari_outcome --cluster dhsclust --spatial upazila_pcode \
  --out outputs/cohort_qa.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--outcome", default="ari_outcome")
    ap.add_argument("--cluster", default="dhsclust")
    ap.add_argument("--spatial", default="upazila_pcode")
    ap.add_argument("--id", default="caseid")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    df = pd.read_csv(args.data, low_memory=False)
    report: dict = {"file": str(args.data), "rows": int(len(df))}

    if args.outcome in df.columns:
        y = df[args.outcome].dropna()
        report["outcome"] = args.outcome
        report["cases"] = int(y.sum())
        report["prevalence"] = float(y.mean()) if len(y) else None
        report["missing_outcome"] = int(df[args.outcome].isna().sum())

    if args.id in df.columns:
        report["duplicate_ids"] = int(df[args.id].duplicated().sum())
    else:
        report["duplicate_ids"] = "id column absent"

    report["missing_by_column"] = {
        c: int(df[c].isna().sum()) for c in df.columns
    }
    report["missing_pct_by_column"] = {
        c: round(float(df[c].isna().mean() * 100), 2) for c in df.columns
    }

    if args.cluster in df.columns:
        sizes = df.groupby(args.cluster).size()
        report["n_clusters"] = int(sizes.size)
        report["cluster_size"] = {
            "min": int(sizes.min()), "median": float(sizes.median()),
            "max": int(sizes.max()),
        }

    if args.spatial in df.columns:
        by = df.groupby(args.spatial).agg(
            n=(args.outcome, "size") if args.outcome in df else (args.spatial, "size"),
            cases=(args.outcome, "sum") if args.outcome in df else (args.spatial, "size"),
        )
        report["n_spatial_units"] = int(by.shape[0])
        report["sparse_units_lt5"] = int((by["n"] < 5).sum())
        report["units_no_cases"] = int((by["cases"] == 0).sum())

    # Exposure sanity ranges
    for c in ["pm25_ug", "temp_mean", "ndvi_mean"]:
        if c in df.columns:
            s = df[c].dropna()
            report[c] = {
                "min": float(s.min()), "max": float(s.max()),
                "mean": float(s.mean()), "sd": float(s.std()),
                "missing": int(df[c].isna().sum()),
            }

    # Wealth distribution
    for c in ["v190", "wealth_index"]:
        if c in df.columns:
            report[f"{c}_distribution"] = {
                str(k): int(v) for k, v in df[c].value_counts().sort_index().items()
            }
            break

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
