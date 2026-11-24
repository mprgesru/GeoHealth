# Prompt playbook

Reusable prompts for driving the skill in OpenCode. Keep the config block at the top of every session; it is the contract.

## 0. Session contract

```text
Use the explainable-geoai-health skill.
Country: Bangladesh
Survey: BDHS 2022
Population: children under 5
Outcome: ARI (h31b + h31c)
Exposure window: 2022 annual mean
Admin unit: upazila
Buffers: urban 2 km, rural 5 km
Validation: leave-one-upazila-out + cluster-grouped 5-fold
Deliverables: cohort table, metrics, SHAP, GAM, maps, manuscript outline
Rules: no GPS in Git; no causal claims; recompute SHAP; report PR-AUC and calibration.
```

## 1. Scope

```text
Read references/bangladesh.md and references/workflow.md.
Write a one-page scope/config record for the study below.
List every decision that must be fixed before data download, and flag any outcome
whose recall window is incompatible with the proposed exposure window.
Study: <one paragraph>
```

## 2. Cohort

```text
Using templates/build_dhs_cohort.py, build the BDHS 2022 child cohort.
Outcome: cough (h31b) plus rapid/chest breathing (h31c), excluding missing/don't know.
Merge KR, PR, and GE; report the flow (screened, eligible, linked, complete, analysed).
Keep v005, v021, v022/v023 for survey design.
Output: master CSV, QA JSON, weighted and unweighted prevalence.
Do not write raw microdata or coordinates to the repository.
```

## 3. Exposure

```text
Using templates/gee_exposure_extraction.js, extract 2022 annual PM2.5, LST, and NDVI
for DHS clusters with urban 2 km and rural 5 km buffers.
Use my own Earth Engine asset: <asset-id>.
Also compute 1–3 km urban and 3–7 km rural sensitivity buffers.
Export cluster means and upazila zonal statistics.
Report the PM2.5 calibration equation and compare with <independent product>.
```

## 4. Modelling

```text
Using templates/rf_shap.py, fit the pre-specified Random Forest (100 trees, depth 10,
leaf 10, balanced) on the frozen feature list.
Report cluster-grouped and leave-one-upazila-out CV, AUC-ROC, PR-AUC, precision,
recall, F1, Brier, calibration slope/intercept, and bootstrap CIs.
Compute TreeSHAP; do not hard-code values.
Save predicted probabilities and tree-level SD by upazila.
```

## 5. Validation audit

```text
Audit this analysis for leakage and optimistic validation:
- Are exposures assigned at a coarser level than the CV folds?
- Are clusters or upazilas split across folds?
- Is the reported AUC from random or grouped CV?
- Are rare-event metrics and calibration reported?
Return a table of issues with severity and a fix.
```

## 6. Explainability

```text
Fit the logistic GAM with s(pm25, bs="cr", k=4) plus LST, NDVI, and wealth as a factor.
Plot the exposure–response curve with 95% CI and a rug plot.
Bootstrap 1,000 times and report the inflection region, not a single threshold.
Then produce SHAP global, dependence, and PM2.5 × temperature interaction plots.
Use association language throughout.
```

## 7. Mapping

```text
Aggregate predicted prevalence and tree-SD uncertainty to upazilas.
Map exposure, observed prevalence, predicted prevalence, and uncertainty with a
coverage mask, scale bar, north arrow, legend, and source note.
Flag upazilas with fewer than five clusters.
Report quintile calibration and Spearman predicted–observed correlation.
```

## 8. Manuscript

```text
Using templates/manuscript_outline.md, draft the methods and results for this study.
Include: cohort flow, exposure calibration, model specification, CV design, metrics,
SHAP ranking, GAM inflection, spatial patterns, limitations.
Do not claim causation or attributable burden.
State the DHS age restriction and the displacement buffers.
```

## 9. Older-adults sub-skill

```text
Create a sub-skill at skills/older-adults-bangladesh/.
Delta from the origin:
- population: adults 50+ in the BDHS 2022 biomarker subsample
- outcomes: measured hypertension and diabetes (medication-aware)
- exposure window: annual + 3-year mean PM2.5
- confounders: smoking, biomass fuel, BMI, medication
- validation: cluster and upazila grouped CV
Reuse the origin templates by relative path.
Document what DHS cannot provide (COPD, IHD, stroke, lung cancer, dementia)
and the GBD/cohort alternatives.
```

## 10. Women's-health sub-skill

```text
Create a sub-skill at skills/women-health-bangladesh/.
Delta from the origin:
- population: women 15-49 (DHS women's module)
- outcomes: <anaemia, hypertension, mental health, reproductive outcomes>
- exposure window: annual + seasonal PM2.5, heat, biomass fuel
- confounders: wealth, education, parity, BMI, iron/folate, cooking fuel
- validation: cluster and upazila grouped CV
Reuse the origin templates; add the anaemia/biomarker variables.
State the DHS restrictions on biomarkers and domestic-violence data.
```

## 11. Reviewer response

```text
A reviewer says the model is overfit because AUC drops from 0.667 to 0.544.
Draft a response that: explains cluster vs spatial CV, cites the rare-event
literature, reports PR-AUC and calibration, and reframes the model as a spatial
prioritisation tool rather than an individual classifier.
```

## 12. Reproducibility check

```text
Given this repository, list every input needed to reproduce the figures.
Flag any hard-coded value, private asset, missing seed, or manual step.
Produce a data manifest and a run order.
```
