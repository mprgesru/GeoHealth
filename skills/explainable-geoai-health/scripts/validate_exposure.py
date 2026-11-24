#!/usr/bin/env python3
"""
Validate extracted exposures: ranges, missingness, correlations, and agreement
with an independent product or monitor file.

Example
-------
python validate_exposure.py --clusters outputs/cluster_exposures.csv \
  --benchmark data/cams_dhaka_daily.csv --value pm25_ug --bench-value pm25 \
  --out outputs/exposure_qa.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clusters", required=True, type=Path)
    ap.add_argument("--benchmark", type=Path)
    ap.add_argument("--value", default="pm25_ug")
    ap.add_argument("--bench-value", default="pm25")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    df = pd.read_csv(args.clusters, low_memory=False)
    report: dict = {"file": str(args.clusters), "rows": int(len(df))}

    for c in ["pm25_ug", "temp_mean", "ndvi_mean", "o3_mol_m2"]:
        if c in df.columns:
            s = pd.to_numeric(df[c], errors="coerce")
            report[c] = {
                "min": float(s.min()), "max": float(s.max()),
                "mean": float(s.mean()), "sd": float(s.std()),
                "missing": int(s.isna().sum()),
                "n": int(s.notna().sum()),
            }

    numeric = [c for c in ["pm25_ug", "temp_mean", "ndvi_mean"] if c in df.columns]
    if len(numeric) > 1:
        report["correlation"] = df[numeric].corr().round(3).to_dict()

    if "pm25_ug" in report:
        if report["pm25_ug"]["max"] > 500:
            report["pm25_flag"] = (
                "PM2.5 max > 500; the MAIAC AOD 0.001 scale is probably missing."
            )
        elif report["pm25_ug"]["max"] < 1:
            report["pm25_flag"] = "PM2.5 max < 1; check the AOD band and units."

    if args.benchmark is not None and args.value in df.columns:
        b = pd.read_csv(args.benchmark, low_memory=False)
        if args.bench_value not in b.columns:
            report["benchmark_error"] = f"{args.bench_value!r} not in benchmark"
        else:
            # Compare distributions; for point matches, merge on a key first.
            x = pd.to_numeric(df[args.value], errors="coerce").dropna()
            y = pd.to_numeric(b[args.bench_value], errors="coerce").dropna()
            report["benchmark"] = {
                "model_mean": float(x.mean()),
                "benchmark_mean": float(y.mean()),
                "bias": float(x.mean() - y.mean()),
                "pct_bias": float((x.mean() - y.mean()) / y.mean() * 100),
                "model_sd": float(x.std()),
                "benchmark_sd": float(y.std()),
            }
            if abs(report["benchmark"]["pct_bias"]) > 20:
                report["flag"] = "Mean difference exceeds 20%; investigate calibration."

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, default=float))
    print(json.dumps(report, indent=2, default=float))


if __name__ == "__main__":
    main()
