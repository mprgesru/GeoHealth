# Workflow

Detailed phase-by-phase procedure for `explainable-geoai-health`. The order matters: define the outcome and exposure window before downloading rasters, and freeze the feature list before modelling.

## Phase 0 — Scope and configuration

Write a one-page configuration record and keep it in the repository:

```yaml
country: Bangladesh
survey: BDHS 2022
population: children under 5
outcome: ARI (cough + rapid/chest breathing)
outcome_window: 2 weeks
admin_unit: upazila
exposure_year: 2022
exposures: [pm25, lst, ndvi]
pm25_product: MAIAC MCD19A2 (AOD x 120 + 15)
buffers_km: {urban: 2, rural: 5}
buffer_sensitivity: {urban: [1, 3], rural: [3, 7]}
validation: {primary: leave-one-upazila-out, secondary: cluster-grouped-5fold}
model: RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=10, class_weight=balanced)
interpretation: [TreeSHAP, logistic GAM]
```

Acceptance check: every field is filled and the outcome window is compatible with the exposure window.

## Phase 1 — Data governance and acquisition

1. Register with the DHS Program (or MICS/STEPS/cohort custodian).
2. Confirm the data-use agreement and IRB status.
3. Download only the files you need:
   - Children: KR (children's recode), PR (household member recode), GE (geographic).
   - Women: IR (individual recode), HR (household recode), GE.
   - Older adults: biomarker/BP/glucose files if available; otherwise see `older-adults.md`.
4. Record file names, versions, and dates in `data_manifest.csv`.
5. Create a private working directory outside Git; add DHS patterns to `.gitignore`.

Acceptance check: you can name the exact file that contains each variable, and no restricted file is in Git.

## Phase 2 — Cohort construction

### 2.1 Merge

- Link children to mothers/households using the DHS identifiers (`v001`, `v002`, `v003`, `b16`, `caseid`).
- Merge cluster GPS by `DHSCLUST`/`hv001`.
- Spatially join clusters to admin polygons with GeoPandas (`sjoin`), repairing invalid geometries first.

### 2.2 Outcome

Define the outcome before exclusions. For child ARI in BDHS 2022:

- Cough: `h31b == 1`.
- Rapid/chest breathing: `h31c` in {chest only, both}.
- `h31d` is missing in BDHS 2022 and is not used.
- ARI = cough AND rapid/chest breathing.
- Missing/"don't know" → excluded, and the count is reported.

### 2.3 Exclusions

Report a flow: screened → eligible → linked → complete → analysed. For the reference study: 8,943 → −147 missing/DK → −12 unmatched cluster → 8,784.

### 2.4 Survey design

Keep `v005` (weight), `v021` (PSU), `v022`/`v023` (strata). Use them for weighted prevalence and design-based standard errors. The model may ignore them, but say so.

Acceptance check: one row per child, no duplicate IDs, prevalence matches a hand calculation, exclusion counts add up.

## Phase 3 — Exposure extraction

### 3.1 Earth Engine

- Upload the DHS cluster shapefile (points) to your own asset; record the asset ID in config.
- Build annual composites:
  - MAIAC `MODIS/061/MCD19A2_GRANULES`, band `Optical_Depth_047`, annual mean.
  - LST `MODIS/061/MOD11A2`, band `LST_Day_1km`, scale 0.02, Kelvin → °C.
  - NDVI `MODIS/061/MOD13A2`, band `NDVI`, scale 0.0001.
- Optional: ozone from Sentinel-5P/OMI/CAMS; nightlights from VNP46A2.

### 3.2 PM2.5

Two paths:

- **Reference path (replication):** `PM2.5 = AOD × 120 + 15`. Report the calibration source and its validation (Dhaka CAMS: RMSE 12.4, MAE 9.8, n = 36 station-days).
- **Preferred path (new study):** use a validated global product (V5.GL.04, CHAP) or fit a local calibration with ground monitors and meteorology. Compare both and report the difference.

### 3.3 Buffers

- Urban: 2 km; rural: 5 km.
- Sensitivity: urban 1–3 km; rural 3–7 km.
- Use `reduceRegions` with `ee.Reducer.mean()` at 1 km scale.
- Report the median change across buffer specifications.

### 3.4 Admin zonal statistics

- Compute mean, min, max, SD per upazila for mapping.
- Keep the cluster-level table for modelling; keep the admin table for maps.

Acceptance check: exposure ranges are plausible, no missing clusters, buffer sensitivity is reported, and an independent product/monitor comparison exists.

## Phase 4 — Feature matrix and leakage control

- Features: PM2.5, LST, NDVI, wealth quintile dummies, and pre-specified confounders.
- Dummy-code wealth with the poorest as reference.
- Check `|r|` between exposures; report VIF if linear models are used.
- Record the level of each feature (cluster, upazila, household, individual).
- If exposures are admin-level, the CV must hold out admin units.

Acceptance check: a feature dictionary with source, level, type, missingness, and transformation.

## Phase 5 — Modelling

Baseline:

```python
RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_leaf=10,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)
```

- Fit on the training folds only.
- Save `predict_proba`, not just `predict`.
- Optional sensitivity: XGBoost with the same features and CV.
- Do not tune on the test folds; use nested CV if tuning.

Acceptance check: the model runs from a frozen feature list and a fixed seed, and predictions are reproducible.

## Phase 6 — Validation

### 6.1 Cluster-grouped CV

`GroupKFold(n_splits=5)` with `groups=cluster_id`. Children in one cluster stay together.

### 6.2 Spatial CV

`GroupKFold` with `groups=upazila_pcode`, or leave-one-upazila-out. This is the honest metric when exposures are shared within upazilas.

### 6.3 Metrics

- AUC-ROC, PR-AUC.
- Precision, recall, F1 at a stated threshold.
- Brier score.
- Calibration slope and intercept; calibration plot.
- Bootstrap 95% CI (1,000 resamples, clustered).

### 6.4 Calibration by risk quintile

Aggregate predicted risk to upazila, sort into quintiles, and report observed prevalence per quintile. The reference study: 0.4%, 0.6%, 1.0%, 1.8%, 2.8%.

### 6.5 Spatial diagnostics

- Moran's I on upazila residuals.
- Spearman correlation between predicted and observed upazila prevalence (reference: ρ = 0.48).

Acceptance check: both CV designs are reported, with PR-AUC and calibration, not only AUC/accuracy.

## Phase 7 — Explainability

### 7.1 TreeSHAP

- `shap.TreeExplainer(rf)`; isolate the positive class.
- Global: mean absolute SHAP bar plot.
- Dependence: SHAP value vs feature, with LOWESS.
- Interaction: SHAP interaction values for PM2.5 × temperature.

### 7.2 GAM

- Logistic GAM with `s(pm25, bs="cr", k=4)` plus covariates.
- Predict on a grid, convert link → probability, add 95% CI.
- Report the inflection region, not a single threshold.
- Bootstrap 1,000 times for stability.

Acceptance check: SHAP values are recomputed, the GAM CI is shown, and no causal or burden language is used.

## Phase 8 — Mapping and prioritisation

- Aggregate predicted probability and uncertainty to admin units.
- Join to boundaries; repair geometry; project for area calculations.
- Map: exposure, observed prevalence, predicted prevalence, uncertainty.
- Flag units with <5 clusters or no DHS coverage.
- Report the top/bottom deciles and the share of cases in the top risk quintiles.

Acceptance check: maps have scale bar, north arrow, legend, source note, and a coverage mask.

## Phase 9 — Manuscript and reproducibility

- Use `templates/manuscript_outline.md`.
- Keep a figure/table register with the script that produced each one.
- Report limitations explicitly.
- Publish code + manifest + aggregates; never microdata or GPS.

Acceptance check: a reader can rerun the analysis from the repository plus their own licensed data.
