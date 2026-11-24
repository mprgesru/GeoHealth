#!/usr/bin/env python3
"""
Spatial validation: leave-one-upazila-out, grouped k-fold, Moran's I, and
predicted-observed correlation.

Example
-------
python spatial_cv.py --data outputs/cohort_bdhs2022.csv \
  --outcome ari_outcome --spatial upazila_pcode --cluster dhsclust \
  --admin data/BGD_adm3.shp --outdir outputs/spatial
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold

warnings.filterwarnings("ignore")

CORE = ["pm25_ug", "temp_mean", "ndvi_mean"]


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y).astype(int)
    p = np.asarray(p).astype(float)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, (p >= 0.5).astype(int), average="binary", zero_division=0
    )
    return {
        "n": int(len(y)),
        "cases": int(y.sum()),
        "auc_roc": float(roc_auc_score(y, p)) if len(np.unique(y)) > 1 else float("nan"),
        "pr_auc": float(average_precision_score(y, p)) if y.sum() > 0 else float("nan"),
        "brier": float(brier_score_loss(y, p)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def model(seed: int = 42) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=100, max_depth=10, min_samples_leaf=10,
        class_weight="balanced", random_state=seed, n_jobs=-1,
    )


def leave_one_group_out(X, y, groups, max_groups: int | None = None) -> np.ndarray:
    groups = pd.Series(groups).astype(str).values
    uniq = np.unique(groups)
    if max_groups is not None:
        uniq = uniq[:max_groups]
    oof = np.full(len(y), np.nan)
    for g in uniq:
        test = groups == g
        train = ~test
        if y[train].sum() == 0 or len(np.unique(y[train])) < 2:
            continue
        m = model()
        m.fit(X[train], y[train])
        oof[test] = m.predict_proba(X[test])[:, 1]
    return oof


def grouped_kfold(X, y, groups, n_splits: int = 5) -> np.ndarray:
    groups = pd.Series(groups).astype(str).values
    n_splits = min(n_splits, len(np.unique(groups)))
    oof = np.full(len(y), np.nan)
    for train, test in GroupKFold(n_splits=n_splits).split(X, y, groups):
        m = model()
        m.fit(X[train], y[train])
        oof[test] = m.predict_proba(X[test])[:, 1]
    return oof


def morans_i(values: np.ndarray, coords: np.ndarray, k: int = 6) -> dict:
    """k-nearest-neighbour Moran's I without extra dependencies."""
    from scipy.spatial import cKDTree

    values = np.asarray(values, dtype=float)
    ok = np.isfinite(values)
    values, coords = values[ok], coords[ok]
    if len(values) < 10:
        return {"morans_i": float("nan"), "p_norm": float("nan")}

    tree = cKDTree(coords)
    _, idx = tree.query(coords, k=k + 1)
    idx = idx[:, 1:]
    n = len(values)
    w = np.zeros((n, n))
    for i in range(n):
        w[i, idx[i]] = 1
    w = (w + w.T) / 2
    w /= w.sum(axis=1, keepdims=True)

    z = values - values.mean()
    num = np.sum(w * np.outer(z, z))
    den = np.sum(z ** 2)
    i_stat = (n / w.sum()) * (num / den) if den > 0 else float("nan")
    expected = -1.0 / (n - 1)
    return {"morans_i": float(i_stat), "expected": float(expected)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--outcome", default="ari_outcome")
    ap.add_argument("--spatial", default="upazila_pcode")
    ap.add_argument("--cluster", default="dhsclust")
    ap.add_argument("--features", nargs="*", default=None)
    ap.add_argument("--wealth", default="v190")
    ap.add_argument("--admin", type=Path, default=None)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--max-groups", type=int, default=None,
                    help="Cap leave-one-out groups for a quick run")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data, low_memory=False)
    df = df.dropna(subset=[args.outcome]).copy()

    features = args.features or CORE
    if args.wealth in df.columns:
        dummies = pd.get_dummies(
            df[args.wealth].astype("Int64"), prefix="wealth", drop_first=True, dtype=int
        )
        df = pd.concat([df, dummies], axis=1)
        features = features + list(dummies.columns)

    X = df[features].astype(float).values
    y = df[args.outcome].astype(int).values
    results = {}

    if args.cluster in df.columns:
        oof = grouped_kfold(X, y, df[args.cluster])
        results["cluster_grouped_5fold"] = metrics(y, oof)
        df["pred_cluster"] = oof

    if args.spatial in df.columns:
        oof = leave_one_group_out(X, y, df[args.spatial], args.max_groups)
        ok = np.isfinite(oof)
        results["leave_one_upazila_out"] = metrics(y[ok], oof[ok])
        df["pred_spatial"] = oof

        # Upazila-level aggregation
        agg = df.dropna(subset=["pred_spatial"]).groupby(args.spatial).agg(
            observed=(args.outcome, "mean"),
            predicted=("pred_spatial", "mean"),
            n=(args.outcome, "size"),
        ).reset_index()
        agg.to_csv(args.outdir / "upazila_predictions.csv", index=False)

        if len(agg) > 2:
            from scipy.stats import spearmanr
            rho, pval = spearmanr(agg["predicted"], agg["observed"])
            results["spearman"] = {"rho": float(rho), "p": float(pval)}

    # Moran's I on upazila residuals
    if args.admin is not None and args.spatial in df.columns:
        try:
            import geopandas as gpd
            from shapely.geometry import Point

            admin = gpd.read_file(args.admin).to_crs(4326)
            admin["geometry"] = admin.geometry.buffer(0)
            admin = admin.rename(columns={args.spatial: "spatial_id"})
            if "spatial_id" not in admin.columns:
                raise KeyError("admin layer lacks the spatial id column")

            agg = df.dropna(subset=["pred_spatial"]).groupby(args.spatial).agg(
                observed=(args.outcome, "mean"),
                predicted=("pred_spatial", "mean"),
            ).reset_index().rename(columns={args.spatial: "spatial_id"})
            merged = admin.merge(agg, on="spatial_id", how="inner")
            merged["residual"] = merged["observed"] - merged["predicted"]
            centroids = merged.geometry.centroid
            coords = np.column_stack([centroids.x, centroids.y])
            results["morans_i_residual"] = morans_i(
                merged["residual"].values, coords
            )
        except Exception as exc:
            results["morans_i_residual"] = {"error": str(exc)}

    (args.outdir / "spatial_metrics.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
