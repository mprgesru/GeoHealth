#!/usr/bin/env python3
"""
Map observed prevalence, predicted prevalence, and prediction uncertainty.

Example
-------
python map_risk.py --admin data/BGD_adm3.shp --pred outputs/rf/predictions.csv \
  --spatial upazila_pcode --outcome ari_outcome --outdir outputs/maps
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def add_map_furniture(ax, gdf, title, column, cmap, label, mask_color="#E6E6E6"):
    gdf.plot(ax=ax, color=mask_color, edgecolor="white", linewidth=0.3)
    plot = gdf.dropna(subset=[column])
    if len(plot):
        plot.plot(
            ax=ax, column=column, cmap=cmap, legend=True, edgecolor="gray",
            linewidth=0.3,
            legend_kwds={"label": label, "shrink": 0.6, "orientation": "horizontal"},
        )
    ax.set_title(title, fontsize=11)
    ax.set_axis_off()


def scale_bar(ax, gdf, length_km=100):
    """Draw a scale bar in projected coordinates."""
    minx, miny, maxx, maxy = gdf.total_bounds
    x0 = minx + 0.06 * (maxx - minx)
    y0 = miny + 0.06 * (maxy - miny)
    ax.plot([x0, x0 + length_km * 1000], [y0, y0], color="black", lw=2.5, zorder=5)
    ax.plot([x0, x0], [y0, y0 + 4000], color="black", lw=1, zorder=5)
    ax.plot([x0 + length_km * 1000, x0 + length_km * 1000],
            [y0, y0 + 4000], color="black", lw=1, zorder=5)
    ax.text(x0 + length_km * 500, y0 - 3000, f"{length_km} km",
            ha="center", va="top", fontsize=7)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--admin", required=True, type=Path)
    ap.add_argument("--pred", required=True, type=Path)
    ap.add_argument("--spatial", default="upazila_pcode")
    ap.add_argument("--outcome", default="ari_outcome")
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--title", default="Environmental health risk")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    admin = gpd.read_file(args.admin)
    if admin.crs is None:
        admin.crs = "EPSG:4326"
    admin = admin.to_crs(admin.estimate_utm_crs())
    admin["geometry"] = admin.geometry.buffer(0)

    df = pd.read_csv(args.pred, low_memory=False)
    if args.spatial not in df.columns:
        raise KeyError(f"{args.spatial!r} not in predictions")

    agg = df.groupby(args.spatial).agg(
        observed=(args.outcome, "mean"),
        predicted=("pred_final", "mean") if "pred_final" in df else ("pred_spatial", "mean"),
        uncertainty=("pred_tree_sd", "mean") if "pred_tree_sd" in df else ("pred_spatial", "std"),
        n=("pred_final", "size") if "pred_final" in df else ("pred_spatial", "size"),
    ).reset_index()
    agg = agg.rename(columns={args.spatial: "spatial_id"})

    admin_key = None
    for cand in [args.spatial, "adm3_pcode", "ADM3_PCODE", "upazila_pcode"]:
        if cand in admin.columns:
            admin_key = cand
            break
    if admin_key is None:
        raise KeyError(f"No spatial key found in admin layer; tried {args.spatial}")

    merged = admin.merge(agg, left_on=admin_key, right_on="spatial_id", how="left")
    merged["observed_pct"] = merged["observed"] * 100
    merged["predicted_pct"] = merged["predicted"] * 100

    fig, axes = plt.subplots(1, 3, figsize=(18, 7), dpi=300)
    add_map_furniture(axes[0], merged, "(a) Observed prevalence", "observed_pct",
                      "Purples", "Observed (%)")
    add_map_furniture(axes[1], merged, "(b) Predicted prevalence", "predicted_pct",
                      "Purples", "Predicted (%)")
    add_map_furniture(axes[2], merged, "(c) Uncertainty (tree SD)", "uncertainty",
                      "Oranges", "SD")

    scale_bar(axes[0], merged)
    axes[0].annotate("N", xy=(0.93, 0.95), xycoords="axes fraction",
                     ha="center", va="top", fontsize=11, fontweight="bold")

    fig.suptitle(args.title, fontsize=14, y=0.98)
    fig.text(0.5, 0.02,
             "Grey = no survey coverage. Predictions are model-based associations, not diagnoses.",
             ha="center", fontsize=8, color="#444")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(args.outdir / "risk_maps.png", dpi=300, bbox_inches="tight")
    plt.savefig(args.outdir / "risk_maps.pdf", bbox_inches="tight")
    plt.close()

    merged.drop(columns="geometry").to_csv(args.outdir / "upazila_risk_table.csv", index=False)
    print(f"wrote {args.outdir}/risk_maps.png and .pdf")


if __name__ == "__main__":
    main()
