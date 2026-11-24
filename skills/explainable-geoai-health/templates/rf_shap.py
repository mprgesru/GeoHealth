#!/usr/bin/env python3
"""
Random Forest + TreeSHAP with cluster- and upazila-grouped validation.

Example
-------
python rf_shap.py --data outputs/cohort_bdhs2022.csv \
  --outcome ari_outcome --cluster dhsclust --spatial upazila_pcode \
  --outdir outputs/rf
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold

warnings.filterwarnings("ignore")

CORE = ["pm25_ug", "temp_mean", "ndvi_mean"]


def logit(p: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    p = np.clip(p, eps, 1 - eps)
    return np.log(p / (1 - p))


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y).astype(int)
    p = np.asarray(p).astype(float)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, (p >= 0.5).astype(int), average="binary", zero_division=0
    )
    out = {
        "n": int(len(y)),
        "cases": int(y.sum()),
        "prevalence": float(y.mean()),
        "auc_roc": float(roc_auc_score(y, p)) if len(np.unique(y)) > 1 else float("nan"),
        "pr_auc": float(average_precision_score(y, p)) if y.sum() > 0 else float("nan"),
        "brier": float(brier_score_loss(y, p)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }
    if len(np.unique(y)) > 1:
        cal = LogisticRegression(solver="lbfgs", max_iter=1000)
        cal.fit(logit(p).reshape(-1, 1), y)
        out["calibration_slope"] = float(cal.coef_[0, 0])
        out["calibration_intercept"] = float(cal.intercept_[0])
    return out


def grouped_cv(
    X: pd.DataFrame, y: pd.Series, groups: pd.Series, n_splits: int = 5, seed: int = 42
) -> tuple[np.ndarray, dict]:
    """Out-of-fold predictions with GroupKFold."""
    groups = pd.Series(groups).astype(str).values
    n_groups = len(np.unique(groups))
    n_splits = min(n_splits, n_groups)
    oof = np.full(len(y), np.nan)
    cv = GroupKFold(n_splits=n_splits)
    for train_idx, test_idx in cv.split(X, y, groups):
        model = RandomForestClassifier(
            n_estimators=100, max_depth=10, min_samples_leaf=10,
            class_weight="balanced", random_state=seed, n_jobs=-1,
        )
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        oof[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
    return oof, metrics(y.values, oof)


def bootstrap_ci(
    y: np.ndarray, p: np.ndarray, groups: np.ndarray, n_boot: int = 1000, seed: int = 42
) -> dict:
    """Cluster bootstrap for AUC and PR-AUC."""
    rng = np.random.default_rng(seed)
    groups = np.asarray(groups).astype(str)
    uniq = np.unique(groups)
    aucs, prs = [], []
    for _ in range(n_boot):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([np.where(groups == g)[0] for g in pick])
        yy, pp = y[idx], p[idx]
        if len(np.unique(yy)) < 2:
            continue
        aucs.append(roc_auc_score(yy, pp))
        prs.append(average_precision_score(yy, pp))
    return {
        "auc_95ci": [float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5))],
        "pr_auc_95ci": [float(np.percentile(prs, 2.5)), float(np.percentile(prs, 97.5))],
    }


def get_shap(model, X: pd.DataFrame):
    import shap

    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(X)
    if isinstance(values, list):
        return np.asarray(values[1])
    values = np.asarray(values)
    if values.ndim == 3:
        return values[:, :, 1]
    return values


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--outcome", default="ari_outcome")
    ap.add_argument("--cluster", default="dhsclust")
    ap.add_argument("--spatial", default="upazila_pcode")
    ap.add_argument("--features", nargs="*", default=None)
    ap.add_argument("--wealth", default="v190")
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--n-splits", default=5, type=int)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data, low_memory=False)
    if args.outcome not in df.columns:
        raise KeyError(f"outcome column {args.outcome!r} not found")

    # Feature matrix
    features = args.features or CORE
    if args.wealth in df.columns:
        dummies = pd.get_dummies(
            df[args.wealth].astype("Int64"), prefix="wealth", drop_first=True, dtype=int
        )
        df = pd.concat([df, dummies], axis=1)
        features = features + list(dummies.columns)

    missing = [c for c in features if c not in df.columns]
    if missing:
        raise KeyError(f"missing features: {missing}")

    data = df.dropna(subset=[args.outcome]).copy()
    X = data[features].astype(float)
    y = data[args.outcome].astype(int)

    results = {}

    # Cluster-grouped CV
    if args.cluster in data.columns:
        oof_c, m_c = grouped_cv(X, y, data[args.cluster], args.n_splits)
        results["cluster_cv"] = m_c
        results["cluster_cv"].update(
            bootstrap_ci(y.values, oof_c, data[args.cluster].values)
        )
        data["pred_cluster_cv"] = oof_c

    # Spatial CV
    if args.spatial in data.columns:
        oof_s, m_s = grouped_cv(X, y, data[args.spatial], args.n_splits)
        results["spatial_cv"] = m_s
        results["spatial_cv"].update(
            bootstrap_ci(y.values, oof_s, data[args.spatial].values)
        )
        data["pred_spatial_cv"] = oof_s

    # Final model + SHAP
    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, min_samples_leaf=10,
        class_weight="balanced", random_state=42, n_jobs=-1,
    )
    model.fit(X, y)
    data["pred_final"] = model.predict_proba(X)[:, 1]
    data["pred_tree_sd"] = np.std(
        [t.predict_proba(X)[:, 1] for t in model.estimators_], axis=0
    )

    shap_matrix = get_shap(model, X)
    importance = pd.DataFrame({
        "feature": features,
        "mean_abs_shap": np.abs(shap_matrix).mean(axis=0),
        "impurity": model.feature_importances_,
    }).sort_values("mean_abs_shap", ascending=False)
    importance.to_csv(args.outdir / "feature_importance.csv", index=False)

    # Global SHAP bar
    plt.figure(figsize=(8, max(3, 0.35 * len(importance))))
    top = importance.head(15).iloc[::-1]
    plt.barh(top["feature"], top["mean_abs_shap"], color="#4A148C")
    plt.xlabel("Mean |SHAP|")
    plt.title("Global feature importance")
    plt.tight_layout()
    plt.savefig(args.outdir / "shap_global.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Dependence plots
    for feat in [f for f in CORE if f in X.columns]:
        idx = features.index(feat)
        plt.figure(figsize=(6, 4.5))
        plt.scatter(X[feat], shap_matrix[:, idx], s=8, alpha=0.25, color="#0072B2")
        try:
            from statsmodels.nonparametric.smoothers_lowess import lowess
            sm = lowess(shap_matrix[:, idx], X[feat].values, frac=0.4)
            plt.plot(sm[:, 0], sm[:, 1], color="black", lw=2)
        except Exception:
            pass
        plt.axhline(0, color="gray", ls="--", lw=0.8)
        plt.xlabel(feat)
        plt.ylabel("SHAP value")
        plt.title(f"SHAP dependence: {feat}")
        plt.tight_layout()
        plt.savefig(args.outdir / f"shap_dependence_{feat}.png", dpi=300)
        plt.close()

    # Calibration by quintile (observed vs predicted)
    data["risk_quintile"] = pd.qcut(
        data["pred_final"], 5, labels=False, duplicates="drop"
    )
    cal = data.groupby("risk_quintile").agg(
        n=("pred_final", "size"),
        predicted=("pred_final", "mean"),
        observed=(args.outcome, "mean"),
    ).reset_index()
    cal.to_csv(args.outdir / "calibration_quintiles.csv", index=False)

    plt.figure(figsize=(4.5, 4.5))
    plt.plot([0, 1], [0, 1], ls="--", color="gray", lw=0.8)
    plt.plot(cal["predicted"], cal["observed"], "o-", color="#D55E00")
    plt.xlabel("Mean predicted prevalence")
    plt.ylabel("Observed prevalence")
    plt.title("Calibration by risk quintile")
    plt.tight_layout()
    plt.savefig(args.outdir / "calibration.png", dpi=300)
    plt.close()

    # Save outputs
    data.to_csv(args.outdir / "predictions.csv", index=False)
    (args.outdir / "metrics.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
