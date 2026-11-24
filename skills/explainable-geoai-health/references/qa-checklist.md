# QA checklist

Run this before, during, and after the analysis. A "no" is a stop sign, not a note.

## A. Scope and configuration

- [ ] Country, survey round, and year are pinned.
- [ ] Outcome is defined from the questionnaire wording, not from an assumed label.
- [ ] Outcome recall/latency window is stated.
- [ ] Population and age range are stated.
- [ ] Spatial unit and admin level are stated.
- [ ] Exposure products, versions, and averaging window are pinned.
- [ ] Buffer radii and sensitivity range are stated.
- [ ] Primary CV design is stated (leave-one-admin-out preferred).
- [ ] Model and interpretation methods are pre-specified.

## B. Data governance

- [ ] DHS/MICS/cohort registration and IRB are in place.
- [ ] Data-use terms are read and recorded.
- [ ] Restricted files are outside Git.
- [ ] `.gitignore` covers `*GE81*`, `*KR81*`, `*PR81*`, `*.dta`, and raw CSV.
- [ ] No cluster coordinates, GPS, or microdata are in a public asset or repository.
- [ ] The Earth Engine asset is owned by the project, not borrowed.

## C. Cohort

- [ ] The cohort flow (screened → eligible → linked → complete → analysed) adds up.
- [ ] One row per person; no duplicate IDs.
- [ ] Prevalence matches a hand calculation.
- [ ] Missing/"don't know" handling is documented and counted.
- [ ] Unmatched clusters are counted and reported.
- [ ] Survey weights, strata, and PSUs are retained.
- [ ] Weighted and unweighted prevalence are both reported.

## D. Exposure

- [ ] Annual composite uses the correct date range and band.
- [ ] Scale factors are applied (LST ×0.02 − 273.15; NDVI ×0.0001; AOD ×0.001).
- [ ] PM2.5 conversion is documented and validated.
- [ ] PM2.5 is in a plausible range (roughly 5–300 µg/m³), not tens of thousands.
- [ ] An independent product or monitor comparison is reported.
- [ ] Buffer sensitivity is reported (median change).
- [ ] No cluster has missing exposure without a flag.
- [ ] Exposure ranges are plausible for the country and season.
- [ ] Admin zonal statistics use the same raster version.

## E. Features and leakage

- [ ] Feature dictionary lists source, level, type, missingness, transformation.
- [ ] Categorical variables are dummy-coded with a stated reference.
- [ ] Correlations/VIF are checked.
- [ ] The level of each feature is recorded.
- [ ] Admin-level features are held out at the admin level.
- [ ] No outcome-derived variable leaks into the predictors.
- [ ] Feature list is frozen before modelling.

## F. Model

- [ ] Seed is fixed.
- [ ] Class imbalance is handled explicitly.
- [ ] Probabilities are saved, not just labels.
- [ ] Hyperparameters are pre-specified or tuned with nested CV.
- [ ] A sensitivity model (XGBoost or similar) is reported.

## G. Validation

- [ ] Cluster-grouped CV is reported.
- [ ] Leave-one-admin-out or spatial CV is reported.
- [ ] AUC-ROC, PR-AUC, precision, recall, F1, Brier are reported.
- [ ] Calibration slope/intercept and plot are reported.
- [ ] Bootstrap CIs resample clusters.
- [ ] Quintile calibration is reported.
- [ ] Moran's I on residuals is reported.
- [ ] Predicted–observed Spearman correlation is reported.
- [ ] Sparse units (<5 clusters) are flagged.

## H. Explainability

- [ ] SHAP values are recomputed from the fitted model.
- [ ] Global importance uses mean absolute SHAP.
- [ ] Dependence plots use the actual data, not hard-coded values.
- [ ] Interaction plot is labelled as model behaviour, not mechanism.
- [ ] GAM uses a spline and reports 95% CI.
- [ ] Inflection is reported as a region, with bootstrap stability.
- [ ] No causal or attributable-burden language.

## I. Mapping

- [ ] Boundaries are valid and deduplicated.
- [ ] Units without survey coverage are masked or hatched.
- [ ] Projection is appropriate for area calculations.
- [ ] Scale bar, north arrow, legend, and source note are present.
- [ ] Predicted and observed maps use comparable legends.
- [ ] Uncertainty map accompanies the prediction map.
- [ ] Priority areas are described with their data density.

## J. Manuscript

- [ ] Abstract reports prevalence, N, CV design, and the honest AUC.
- [ ] Methods state the survey, outcome, exposure, buffers, model, and CV.
- [ ] Results separate association from prediction.
- [ ] Limitations cover cross-sectional design, displacement, exposure error, confounding, rare-event instability, and generalisability.
- [ ] Data-availability statement respects DHS terms.
- [ ] Figures are 300–600 dpi and readable in greyscale.
- [ ] Tables have units and denominators.

## K. Repository

- [ ] `README.md` explains how to rerun.
- [ ] `data_manifest.csv` is complete.
- [ ] Scripts run from a clean environment with pinned packages.
- [ ] Figures/tables are reproducible from scripts.
- [ ] Licence and citation are present.
- [ ] No secrets, tokens, or private asset IDs are committed.
