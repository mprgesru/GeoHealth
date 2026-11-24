#!/usr/bin/env python3
"""
Logistic GAM-style exposure-response curve with 95% CI and bootstrap stability.

Uses a cubic B-spline in statsmodels/patsy, so no R dependency. If you prefer
mgcv, the formula is: y ~ s(pm25, bs="cr", k=4) + temp_mean + ndvi_mean + wealth.

Example
-------
python gam_exposure_response.py --data outputs/cohort_bdhs2022.csv \
  --outcome ari_outcome --exposure pm25_ug --cluster dhsclust --outdir outputs/gam
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
import statsmodels.api as sm
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")


def fit(df: pd.DataFrame, outcome: str, exposure: str, covariates: list[str], df_spline: int):
    terms = [f"bs({exposure}, df={df_spline}, degree=3)"]
    for c in covariates:
        if c in df.columns:
            terms.append(f"C({c})" if df[c].dtype == object else c)
    formula = f"{outcome} ~ " + " + ".join(terms)
    return smf.glm(formula, data=df, family=sm.families.Binomial()).fit()


def predict_curve(model, df, exposure, grid, covariates):
    ref = {c: (df[c].mode()[0] if df[c].dtype == object else df[c].mean())
           for c in covariates if c in df.columns}
    new = pd.DataFrame({exposure: grid, **ref})
    pred = model.get_prediction(new)
    sf = pred.summary_frame(alpha=0.05)
    prob = 1 / (1 + np.exp(-sf["mean"].values))
    lo = 1 / (1 + np.exp(-sf["mean_ci_lower"].values))
    hi = 1 / (1 + np.exp(-sf["mean_ci_upper"].values))
    return prob, lo, hi


def inflection(grid, prob):
    d1 = np.gradient(prob, grid)
    peak = float(grid[int(np.argmax(d1))])
    thresh = 0.8 * np.nanmax(d1)
    region = grid[d1 >= thresh]
    return peak, (float(region.min()), float(region.max())) if len(region) else (np.nan, np.nan)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--outcome", default="ari_outcome")
    ap.add_argument("--exposure", default="pm25_ug")
    ap.add_argument("--covariates", nargs="*", default=["temp_mean", "ndvi_mean", "v190"])
    ap.add_argument("--cluster", default="dhsclust")
    ap.add_argument("--df-spline", default=4, type=int)
    ap.add_argument("--n-boot", default=200, type=int)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data, low_memory=False).dropna(subset=[args.outcome, args.exposure])

    covars = [c for c in args.covariates if c in df.columns]
    model = fit(df, args.outcome, args.exposure, covars, args.df_spline)
    grid = np.linspace(df[args.exposure].min(), df[args.exposure].max(), 300)
    prob, lo, hi = predict_curve(model, df, args.exposure, grid, covars)
    peak, region = inflection(grid, prob)

    # Cluster bootstrap for the inflection region
    boots = []
    if args.cluster in df.columns and args.n_boot > 0:
        rng = np.random.default_rng(42)
        clusters = df[args.cluster].astype(str).unique()
        for _ in range(args.n_boot):
            pick = rng.choice(clusters, size=len(clusters), replace=True)
            sample = pd.concat([df[df[args.cluster].astype(str) == c] for c in pick])
            try:
                m = fit(sample, args.outcome, args.exposure, covars, args.df_spline)
                p, _, _ = predict_curve(m, sample, args.exposure, grid, covars)
                boots.append(inflection(grid, p)[0])
            except Exception:
                continue

    result = {
        "n": int(len(df)),
        "cases": int(df[args.outcome].sum()),
        "prevalence": float(df[args.outcome].mean()),
        "peak_slope": peak,
        "rapid_rise_region": region,
        "bootstrap_peak_median": float(np.median(boots)) if boots else None,
        "bootstrap_peak_95ci": [
            float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
        ] if boots else None,
        "n_boot": len(boots),
        "formula": model.model.formula,
    }
    (args.outdir / "gam_results.json").write_text(json.dumps(result, indent=2))

    plt.figure(figsize=(7, 5))
    plt.fill_between(grid, lo * 100, hi * 100, color="#DBDBDB", alpha=0.8, label="95% CI")
    plt.plot(grid, prob * 100, color="black", lw=2.2, label="Predicted risk")
    plt.axvline(peak, color="black", ls="--", lw=1.2,
                label=f"Peak slope ~{peak:.0f}")
    plt.plot(df[args.exposure], np.full(len(df), 0.2), "|", color="gray", alpha=0.05)
    plt.xlabel(f"{args.exposure}")
    plt.ylabel("Predicted probability (%)")
    plt.title("Exposure-response (logistic spline)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(args.outdir / "gam_exposure_response.png", dpi=300)
    plt.close()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
