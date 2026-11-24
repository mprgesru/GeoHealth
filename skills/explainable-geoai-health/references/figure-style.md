# Figure style

Aim for figures that survive greyscale printing and a 2-column journal layout.

## 1. Standards

- Resolution: 300 dpi minimum; 600 dpi for line art.
- Format: PNG for raster, PDF/SVG for vector; keep a 300 dpi PNG fallback.
- Width: 90 mm (single column) or 190 mm (double column).
- Font: sans-serif (Arial/Helvetica), 7–9 pt at final size.
- Colour: colour-blind-safe palette (Okabe–Ito or viridis); check greyscale.
- No chartjunk: remove top/right spines, use light gridlines, label units.
- Every map: scale bar, north arrow, legend, source note, projection.
- Every plot: sample size, outcome definition, and model in the caption.

## 2. Figure set

| Figure | Content | Notes |
|---|---|---|
| 1 | Study area + clusters + admin units | Show coverage mask |
| 2 | Workflow | Cohort flow + exposure + model + SHAP |
| 3 | Exposure map (PM2.5) | Diverging or sequential; WHO guideline note |
| 4 | Observed outcome map | Mask sparse units |
| 5 | GAM exposure–response | 95% CI; rug plot; inflection band |
| 6 | SHAP global + interaction | Bar + heatmap/scatter |
| 7 | SHAP dependence | PM2.5, LST, NDVI, wealth |
| 8 | Predicted risk + uncertainty | Two panels, same extent |
| S1 | Correlation matrix | Exposures and confounders |
| S2 | Precision–recall curve | Rare-event performance |
| S3 | Buffer sensitivity | Median change across buffers |
| S4 | Calibration by quintile | Predicted vs observed |

## 3. Colour

```python
# Okabe–Ito
OKABE = ["#000000", "#E69F00", "#56B4E9", "#009E73",
         "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
```

- Sequential exposure: `viridis` or `cividis`.
- Predicted risk: `Purples`; uncertainty: `Oranges`.
- Diverging (anomaly): `RdBu_r` with a symmetric range.
- Never use red–green alone.

## 4. Maps

```python
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

gdf = gpd.read_file("bgd_adm3.shp").to_crs(4326)

fig, ax = plt.subplots(figsize=(7, 8), dpi=300)
gdf.plot(ax=ax, color="#E6E6E6", edgecolor="white", linewidth=0.3)
gdf.dropna(subset=["predicted_prev"]).plot(
    ax=ax, column="predicted_prev", cmap="Purples",
    legend=True, edgecolor="gray", linewidth=0.3,
    legend_kwds={"label": "Predicted prevalence (%)", "shrink": 0.6},
)
ax.set_axis_off()
ax.text(0.02, 0.02, "Source: BDHS 2022; MODIS MAIAC",
        transform=ax.transAxes, fontsize=6, color="#444")
```

Add a scale bar in projected coordinates (e.g., EPSG:32646 for Bangladesh) rather than approximate degrees. Add a north arrow with a simple `ax.annotate`.

## 5. SHAP

- Global bar: sort descending, label with units, show mean |SHAP|.
- Dependence: scatter with alpha 0.25, LOWESS line in black, zero line dashed.
- Interaction: 2D heatmap or binned scatter; label axes with units.
- Do not hard-code values; compute them.

## 6. Captions

Include:

1. What is shown.
2. Data source and year.
3. Sample size and case count.
4. Model and validation design.
5. Any mask or exclusion.
6. The uncertainty definition.

Example:

> **Figure 8.** Predicted ARI prevalence (left) and tree-level prediction uncertainty (right) across 344 upazilas with DHS coverage, Bangladesh, 2022. Predictions from a class-balanced Random Forest; spatial cross-validation AUC–ROC = 0.544. Grey areas have no DHS cluster. Uncertainty is the standard deviation of predicted probabilities across 100 trees.

## 7. Accessibility

- Minimum 6 pt text.
- Do not encode the same information by colour alone; use shape or labels.
- Provide alt text in the manuscript or repository.
- Check the figure at 100% and at print size.
