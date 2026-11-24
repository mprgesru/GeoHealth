---
name: Explainable GeoAI for Environmental Health
description: Plan, execute, validate, and write up an explainable geospatial-AI study that links satellite environmental exposures (PM2.5, ozone, land surface temperature, vegetation) to population health outcomes from geocoded surveys, with Bangladesh DHS defaults and an explicit older-adult extension.
license: MIT
compatibility: OpenCode V2
metadata:
  version: 0.1.0
  updated: 2026-11-24
  author: GeoHealth skill
---

# Explainable GeoAI for Environmental Health

Use this skill to produce a reproducible, publication-ready study that joins satellite environmental exposures to geocoded health-survey outcomes, fits an interpretable machine-learning model, validates it honestly, and maps spatial risk for prioritisation.

The reference implementation is the Bangladesh 2022 DHS child-ARI study by Moniruzzaman (2026, *GeoHealth*). The same pipeline transfers to other countries, other outcomes, and other age groups — but the exposure window, confounders, and validation design must change with the outcome.

## When to use

- Linking PM2.5, ozone, LST, NDVI, or nightlights to a geocoded survey outcome (ARI, hypertension, diabetes, asthma, mortality).
- Producing upazila/district-level risk maps with uncertainty from survey microdata.
- Reanalysing DHS, MICS, STEPS, or an ageing cohort with explainable ML.
- Replicating the Bangladesh child-ARI study or extending it to older adults or women's health.

## When not to use

- Causal effect estimation or attributable-burden calculation (use GAM/negative binomial with lagged exposures, g-computation, TMLE, or GBD).
- Clinical diagnosis, individual risk prediction, or screening tools.
- Studies without geocoded clusters or a reliable exposure surface.
- Situations where the outcome is not measured in the survey — do not substitute a different age group's outcome.

## Two tracks

| Track | Population | Outcome | Data | Status |
|---|---|---|---|---|
| **A. Child ARI** | Children <5 | Cough + rapid/chest breathing | BDHS 2022 KR/PR/GE | Fully specified, reference implementation |
| **B. Older adults** | 50+/60+ | Measured hypertension/diabetes; or GBD chronic disease | BDHS 2022 biomarker subsample; GBD; ageing cohorts | Feasibility documented; protocol in `references/older-adults.md` |

Sub-skills for women's health and country variants are added under `skills/<name>/` without forking this origin. See `skills/README.md`.

## Non-negotiable principles

1. **Match the exposure window to the outcome's latency.** A 2-week ARI recall needs a short-window or annual exposure with a sensitivity check; COPD, IHD, stroke, and dementia need multi-year means. Do not reuse the child-ARI window for chronic outcomes.
2. **Make group-aware or spatial cross-validation the headline metric.** Random child-level CV is optimistic when exposures are shared within clusters or upazilas. Report cluster-grouped and leave-one-upazila-out results.
3. **Do not use a heuristic AOD-to-PM2.5 conversion without local validation.** `AOD × 120 + 15` is a regional convenience, not a universal model. Compare with a validated product (V5.GL.04, CHAP, or a locally calibrated model) and report both.
4. **Respect DHS displacement.** Urban clusters are displaced up to 2 km, rural up to 5 km (about 1% up to 10 km). Use buffers accordingly and never attempt to re-identify clusters.
5. **Report rare-event metrics.** With prevalence near 1%, accuracy is misleading. Report prevalence, cases, PR-AUC, precision, recall, F1, Brier score, and calibration.
6. **SHAP is association, not causation.** Feature importance describes the fitted model, not a health burden or a policy effect. Do not derive attributable cases or a "safe" threshold.
7. **Control leakage.** If exposures are assigned at upazila level, hold out upazilas — not just clusters — and never let the same administrative unit appear in train and test.
8. **Weight descriptive statistics by the survey design.** Use weights, strata, and PSUs for prevalence and standard errors; state explicitly when the model ignores them.
9. **Stratify by age and sex.** Children, reproductive-age women, and older adults have different exposure windows, confounders, and outcome definitions. Do not pool them silently.
10. **Check spatial autocorrelation.** Report Moran's I on residuals and a spatial bootstrap; a model can rank well globally and fail locally.
11. **Keep a data manifest and a reproducibility trail.** Record file names, versions, dates, variable names, exclusions, and random seeds.
12. **Respect licences.** DHS GPS and microdata are restricted; MODIS is open; GBD and boundaries have their own terms. Never redistribute survey coordinates.

## Inputs to collect

| Input | Preferred source | Notes |
|---|---|---|
| Health outcome | DHS KR/PR, MICS, STEPS, ageing cohort | Define the outcome before touching exposures |
| Cluster geolocation | DHS GE (registered access) | Displaced; use buffers |
| PM2.5 | MAIAC MCD19A2 + validated product | 1 km; annual and multi-year means |
| Ozone (optional) | Sentinel-5P, OMI, CAMS, MERRA-2 | For COPD and respiratory chronic outcomes |
| LST | MOD11A2 | 1 km, 8-day composite |
| Vegetation | MOD13A2 NDVI/EVI | 1 km, 16-day composite |
| Nightlights / built-up | VIIRS VNP46A2, GHSL | Urbanisation confounder |
| Population | WorldPop, GHSL | Denominators and exposure weighting |
| Administrative boundaries | BBS, GADM, HDX, OSM | Match the survey's admin levels |
| Ground monitors | OpenAQ, CAMS, US Embassy | Calibration and validation |
| Confounders | Survey wealth, education, fuel, smoking, age, sex | Keep provenance |

## Workflow

### Phase 0 — Scope and configuration

Decide and write down:

1. Country and survey round.
2. Outcome and its recall/latency window.
3. Population and age range.
4. Spatial unit (cluster, union, upazila, district).
5. Exposure products and averaging window.
6. Buffer radii (urban/rural) and sensitivity range.
7. Validation design (cluster-grouped, leave-one-admin-out).
8. Model (RF baseline; XGBoost optional) and interpretation (SHAP, GAM).
9. Deliverables (tables, figures, maps, manuscript).

Read `references/workflow.md` for the full sequence and `references/bangladesh.md` for the default configuration.

### Phase 1 — Data governance and acquisition

- Register for DHS/MICS access; confirm IRB and data-use terms.
- Download the correct recodes (KR, PR, GE, IR, HR, VA as needed).
- Record file names, versions, and download dates.
- Do not upload restricted microdata to public repositories or Earth Engine assets you do not control.
- Read `references/licenses.md` before sharing anything.

### Phase 2 — Cohort construction

- Merge child/individual records to households and clusters.
- Apply inclusion/exclusion rules and report the flow (screened → eligible → analysed).
- Define the outcome exactly, including how "don't know" and missing are handled.
- Keep survey weights, strata, and PSU identifiers.
- Produce a master table with one row per person and a QA report.

### Phase 3 — Exposure extraction

- Upload your own cluster asset to Earth Engine.
- Build annual (and seasonal/monthly) composites.
- Buffer urban and rural clusters separately; extract means at the exposure resolution.
- Run buffer sensitivity (e.g., urban 1–3 km, rural 3–7 km).
- Validate against ground monitors and an independent product.
- Export cluster-level exposures and admin-level zonal statistics.

### Phase 4 — Feature matrix and leakage control

- Combine exposures, wealth, education, fuel, age, sex, and other confounders.
- Dummy-code categorical variables; keep a reference category.
- Check correlations and variance inflation.
- Decide the level at which each feature is assigned; if it is admin-level, hold out admin units.
- Freeze the feature list before modelling.

### Phase 5 — Modelling

- Fit a class-balanced Random Forest as the baseline (100 trees, depth 10, leaf 10 is a reasonable start).
- Tune only if you can afford nested CV; otherwise report the pre-specified configuration.
- Optional: XGBoost or gradient boosting as a sensitivity model.
- Save predicted probabilities, not just labels.
- Record the random seed.

### Phase 6 — Validation

- Cluster-grouped k-fold CV.
- Leave-one-upazila-out (or leave-one-admin-unit-out) spatial CV.
- Report AUC-ROC, PR-AUC, precision, recall, F1, Brier score, calibration slope/intercept.
- Bootstrap confidence intervals.
- Compare predicted and observed prevalence by risk quintile.
- Report Moran's I on residuals.

### Phase 7 — Explainability

- TreeSHAP global importance (mean absolute SHAP).
- SHAP dependence plots with LOWESS smoothing.
- SHAP interaction (PM2.5 × temperature, PM2.5 × NDVI).
- Logistic GAM with a cubic spline for the exposure–response curve; report 95% CI and an exploratory inflection region.
- Bootstrap the GAM to show threshold stability.
- State clearly that SHAP and GAM describe associations in the fitted model.

### Phase 8 — Mapping and prioritisation

- Aggregate predicted prevalence and uncertainty (tree SD or bootstrap SD) to admin units.
- Map predicted risk, observed prevalence, exposure, and uncertainty side by side.
- Report risk-quintile calibration and Spearman correlation between predicted and observed.
- Identify priority areas; flag sparse-data units.
- Do not label a model-derived inflection as a health-based threshold.

### Phase 9 — Manuscript and reproducibility

- Follow `templates/manuscript_outline.md`.
- Include a workflow figure, exposure map, outcome map, GAM curve, SHAP bar, SHAP dependence, interaction, predicted/uncertainty maps, calibration, and sensitivity.
- Report limitations: cross-sectional design, displaced coordinates, exposure error, unmeasured confounding, rare-event instability, generalisability.
- Publish code, a data manifest, and non-restricted aggregates; never publish GPS or microdata.
- Use `references/figure-style.md` and `references/qa-checklist.md`.

## Output contract

A complete study delivers:

1. A scope/config record (country, survey, outcome, window, buffers, CV design).
2. A cohort flow diagram and analysis-ready master table.
3. Cluster-level exposures and admin-level zonal statistics.
4. A feature dictionary with provenance and missingness.
5. Model outputs: predicted probabilities, metrics, calibration, uncertainty.
6. SHAP global/dependence/interaction outputs and a GAM exposure–response curve.
7. Admin-level risk and uncertainty maps.
8. A manuscript draft with limitations and a data-availability statement.
9. A reproducible code and manifest package.

## Quality gates

Stop before writing the manuscript if:

- The outcome definition does not match the survey question and recall window.
- More than 10% of eligible records are dropped without a documented reason.
- The exposure surface is coarser than the outcome's intended spatial scale, or is a 30 m DEM treated as a pollution surface.
- Annual mean PM2.5 differs from an independent product or monitor by more than ~20% without explanation.
- Only random CV is reported; no cluster or spatial CV.
- Prevalence is <5% and only accuracy/AUC are reported, with no PR-AUC or calibration.
- SHAP values are hard-coded or not recomputed from the fitted model.
- A "threshold" is presented as safe or clinical without external validation.
- The map shows predicted risk for admin units with no survey coverage without a flag.
- Restricted coordinates or microdata appear in the repository.

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Random child-level CV reported as validation | Use GroupKFold by cluster and leave-one-upazila-out |
| `AOD × 120 + 15` used without the 0.001 scale | PM2.5 in the tens of thousands | Apply `AOD × 0.001` before calibration |
| `AOD × 120 + 15` treated as a validated PM2.5 model | Compare with V5.GL.04/CHAP or a local calibration; report both |
| Hard-coded SHAP values in figure code | Recompute TreeSHAP from the fitted model |
| Wealth index treated as numeric in a GAM | Use a factor or quintile dummies |
| Accuracy reported for 1% prevalence | Report PR-AUC, precision, recall, Brier, calibration |
| PM2.5 inflection called a safe threshold | Call it an exploratory prioritisation marker |
| Children and older adults pooled | Stratify by age; separate exposure windows |
| DHS 15–49 chronic-disease module used for 60+ | Use the biomarker subsample or another survey |
| Private Earth Engine asset in code | Upload your own asset; keep the ID in config |
| Cluster coordinates committed to Git | Add DHS patterns to `.gitignore`; publish aggregates only |

## Bangladesh quick start

```text
1. references/bangladesh.md        # survey files, variables, buffers, benchmarks
2. references/licenses.md          # DHS terms before download
3. templates/gee_exposure_extraction.js
4. templates/build_dhs_cohort.py
5. templates/rf_shap.py
6. templates/spatial_cv.py
7. templates/gam_exposure_response.py
8. templates/map_risk.py
9. references/qa-checklist.md
```

Expected reference values (do not force them; use as sanity checks): 8,784 children, 95 ARI cases (1.08%), 673 clusters in 344 upazilas, cluster CV AUC ≈ 0.667, spatial CV AUC ≈ 0.544, PM2.5 34.8–92.7 µg/m³, SHAP temperature ≈ 0.105, NDVI ≈ 0.090, PM2.5 ≈ 0.075.

## Reuse and sub-skills

Copy the skill folder into a project:

```text
<project>/.opencode/skills/explainable-geoai-health/
```

Or point OpenCode at this repository's `skills/` directory. For a new population or outcome, create a sub-skill that states its delta from this origin; do not fork the pipeline. See `skills/README.md`.

## References

Read only what the task needs:

- `references/workflow.md` — phase-by-phase procedure.
- `references/bangladesh.md` — DHS 2022 configuration and replication targets.
- `references/older-adults.md` — what DHS has for 60+, three feasible designs, minimal protocol.
- `references/data-sources.md` — surveys, Earth Engine collections, boundaries, licences.
- `references/methodology.md` — exposure assignment, models, CV, metrics, SHAP, GAM.
- `references/qa-checklist.md` — pre-flight, cohort, exposure, model, map, manuscript checks.
- `references/licenses.md` — DHS, MODIS, GBD, boundaries, code.
- `references/figure-style.md` — publication figure standards.
- `references/prompt-playbook.md` — reusable prompts per phase.
- `templates/` — runnable starting points.
- `scripts/` — QA and exposure validation.
- `examples/bangladesh_child_ari.md` — replication guide.
- `examples/bangladesh_older_adults.md` — elderly feasibility memo.
