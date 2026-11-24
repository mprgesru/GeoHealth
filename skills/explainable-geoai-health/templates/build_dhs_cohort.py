#!/usr/bin/env python3
"""
Build the BDHS 2022 child ARI cohort.

This is a starting point, not a black box. DHS recode variable names and codes
can differ by phase and country; verify against the official codebook before
trusting the output.

Example
-------
python build_dhs_cohort.py \
  --kr BDKR81FL.DTA --pr BDPR81FL.DTA --ge BDGE81FL.DTA \
  --admin BGD_adm3.shp --out outputs/cohort_bdhs2022.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


# DHS h31c codes: 1 = chest only, 2 = nose only, 3 = both, 8 = don't know.
# Confirm against your codebook before changing.
CHEST_CODES = {1, 3}


def read_any(path: Path) -> pd.DataFrame:
    """Read .dta/.sav/.csv and lower-case the column names."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, low_memory=False)
    elif suffix in {".dta", ".sav"}:
        try:
            import pyreadstat
        except ImportError as exc:
            raise ImportError("pip install pyreadstat to read .dta/.sav files") from exc
        if suffix == ".dta":
            df, _ = pyreadstat.read_dta(str(path), apply_value_formats=False)
        else:
            df, _ = pyreadstat.read_sav(str(path), apply_value_formats=False)
    else:
        raise ValueError(f"Unsupported file type: {path}")
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def require(df: pd.DataFrame, cols: list[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{label} is missing required columns: {missing}")


def build_outcome(df: pd.DataFrame, strict: bool = True) -> pd.DataFrame:
    """Cough + rapid/chest breathing, excluding missing/don't know."""
    require(df, ["h31b", "h31c"], "child recode")
    cough = df["h31b"]
    rapid = df["h31c"]

    valid = cough.isin([0, 1]) & rapid.isin([0, 1, 2, 3])
    ari = (cough == 1) & rapid.isin(list(CHEST_CODES))

    df = df.copy()
    df["ari_outcome"] = np.where(valid, ari.astype(int), np.nan)
    if strict:
        df = df[df["ari_outcome"].notna()].copy()
    return df


def attach_geography(df: pd.DataFrame, ge: pd.DataFrame) -> pd.DataFrame:
    """Merge cluster-level geography by DHSCLUST / hv001."""
    ge = ge.copy()
    if "dhsclust" not in ge.columns and "hv001" in ge.columns:
        ge = ge.rename(columns={"hv001": "dhsclust"})
    require(ge, ["dhsclust"], "geographic file")
    keep = [c for c in ["dhsclust", "urban_rural", "latnum", "longnum",
                        "admin1", "admin2", "upazila_pcode"] if c in ge.columns]
    ge = ge[keep].drop_duplicates("dhsclust")
    df = df.copy()
    if "v001" not in df.columns:
        raise KeyError("child recode is missing v001 (cluster)")
    df["dhsclust"] = pd.to_numeric(df["v001"], errors="coerce").astype("Int64")
    ge["dhsclust"] = pd.to_numeric(ge["dhsclust"], errors="coerce").astype("Int64")
    ge = ge.dropna(subset=["dhsclust"])
    return df.merge(ge, on="dhsclust", how="left")


def spatial_join(df: pd.DataFrame, admin_path: Path) -> pd.DataFrame:
    """Attach upazila attributes when LATNUM/LONGNUM and an admin layer exist."""
    try:
        import geopandas as gpd
    except ImportError:
        print("[warn] geopandas not installed; skipping spatial join")
        return df
    if not {"latnum", "longnum"}.issubset(df.columns):
        print("[warn] LATNUM/LONGNUM absent; skipping spatial join")
        return df

    admin = gpd.read_file(admin_path)
    if admin.crs is None:
        admin.crs = "EPSG:4326"
    admin = admin.to_crs(4326)
    admin["geometry"] = admin.geometry.buffer(0)

    pts = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(df["longnum"], df["latnum"]),
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(pts, admin, how="left", predicate="within")
    joined = joined.drop(columns=["geometry", "index_right"], errors="ignore")
    return pd.DataFrame(joined)


def weighted_prevalence(df: pd.DataFrame, weight: str = "v005") -> float:
    if weight not in df.columns:
        return float(df["ari_outcome"].mean())
    w = df[weight].astype(float)
    w = w / 1_000_000.0 if w.max() > 100 else w
    return float(np.average(df["ari_outcome"], weights=w))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kr", required=True, type=Path, help="Children's recode")
    ap.add_argument("--pr", type=Path, help="Household member recode (optional)")
    ap.add_argument("--ge", required=True, type=Path, help="Geographic data")
    ap.add_argument("--admin", type=Path, help="Admin boundary layer (optional)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--year", default=2022, type=int)
    args = ap.parse_args()

    kr = read_any(args.kr)
    ge = read_any(args.ge)

    # Child age: b19 (months) is standard in KR; fall back to hw1.
    if "b19" not in kr.columns and "hw1" in kr.columns:
        kr["b19"] = kr["hw1"]
    require(kr, ["v001", "v002", "v003", "h31b", "h31c"], "child recode")

    n0 = len(kr)
    kr = build_outcome(kr, strict=True)
    n1 = len(kr)

    # Optional household covariates from PR (household size, cooking fuel).
    if args.pr is not None:
        pr = read_any(args.pr)
        hh_cols = [c for c in ["hv001", "hv002", "hv009", "hv226"] if c in pr.columns]
        if {"hv001", "hv002"}.issubset(hh_cols):
            pr_hh = pr[hh_cols].drop_duplicates(["hv001", "hv002"])
            kr = kr.merge(
                pr_hh, left_on=["v001", "v002"], right_on=["hv001", "hv002"], how="left"
            )

    kr = attach_geography(kr, ge)
    n2 = len(kr)

    if args.admin is not None:
        kr = spatial_join(kr, args.admin)

    # Keep a compact analysis table; add your confounders deliberately.
    keep = [
        c for c in [
            "caseid", "v001", "v002", "v003", "v005", "v021", "v022", "v023",
            "v190", "b19", "h31b", "h31c", "h31d", "ari_outcome",
            "dhsclust", "urban_rural", "latnum", "longnum",
            "hv009", "hv226", "upazila_pcode", "upazila_name",
        ] if c in kr.columns
    ]
    out = kr[keep].copy()

    # Do not write coordinates to a public repository. This CSV is for private use.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)

    qa = {
        "year": args.year,
        "n_child_records": int(n0),
        "n_after_outcome_filter": int(n1),
        "n_after_geography_merge": int(n2),
        "excluded_missing_outcome": int(n0 - n1),
        "n_analysed": int(len(out)),
        "cases": int(out["ari_outcome"].sum()),
        "prevalence": float(out["ari_outcome"].mean()),
        "weighted_prevalence": weighted_prevalence(out),
        "n_clusters": int(out["dhsclust"].nunique()) if "dhsclust" in out else None,
        "n_upazilas": int(out["upazila_pcode"].nunique())
        if "upazila_pcode" in out else None,
        "missing_by_column": {c: int(out[c].isna().sum()) for c in out.columns},
    }
    qa_path = args.out.with_suffix(".qa.json")
    qa_path.write_text(json.dumps(qa, indent=2))
    print(json.dumps(qa, indent=2))
    print(f"wrote {args.out} and {qa_path}")


if __name__ == "__main__":
    main()
