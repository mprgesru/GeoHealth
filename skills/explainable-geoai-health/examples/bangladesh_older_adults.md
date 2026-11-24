# Example: older adults in Bangladesh

A feasibility memo for extending the origin skill to people aged 50+/60+. Read `references/older-adults.md` for the full inventory.

## 1. The core finding

**BDHS 2022 does not interview people aged 60+.** The individual questionnaire is for ever-married women 15–49, and there is no men's recode. The survey does contain a biomarker subsample that measured blood pressure, fasting glucose, and anthropometry in adults 18+, so DHS can support a study of **measured hypertension and diabetes in older adults** — not COPD, IHD, stroke, lung cancer, or dementia.

| Data need | BDHS 2022 |
|---|---|
| 60+ individual interview | No |
| 60+ measured BP / glucose / BMI | Yes (1/6 households; adults 18+) |
| 60+ self-reported chronic disease | No (module is for women 15–49) |
| COPD / IHD / stroke / lung cancer / dementia | No |
| Household roster + wealth + cluster GPS | Yes |
| Verbal autopsy | Under-5 deaths, partial |

## 2. Three designs

### A. DHS biomarker extension — start here

**Question:** Are ambient PM2.5, ozone, LST, and vegetation associated with measured hypertension and diabetes in adults 50+?

- **Population:** adults 50+ in the biomarker subsample; 60+ as a sensitivity analysis.
- **Outcomes:** measured hypertension (mean SBP ≥140 or DBP ≥90, or medication); measured diabetes (fasting glucose ≥7.0 mmol/L, or diagnosed/medication).
- **Exposures:** annual + 3-year mean PM2.5; optional O3; LST; NDVI.
- **Confounders:** age, sex, wealth, education, urban/rural, BMI, smoking, cooking fuel, comorbidity.
- **Model:** Random Forest + SHAP; cluster- and upazila-grouped CV; survey weights for prevalence.
- **Why it works:** measured outcomes, national coverage, existing governance, direct reuse of the pipeline.
- **Limits:** prevalent not incident outcomes; modest 60+ sample; no COPD/dementia; BP/glucose only in 1/6 of households.

### B. GBD burden mapping — for the full disease list

Use GBD 2021 prevalence/mortality for COPD, IHD, stroke, lung cancer, and dementia, plus PM2.5/O3 rasters and relative-risk functions, to map attributable burden. This is an ecological burden study, not an individual ML study. It answers a different question and should not be presented as a survey association.

### C. Ageing cohort — for measured COPD, cognition, and events

| Dataset | Coverage | Access |
|---|---|---|
| MHPD 2023 + Population Aging Module | ~5,500 interviews, ~2,000 aged 60+; rural panel | BRAC/ADB/custodian |
| BELIEVE | 73,883 adults ≥11; Mirpur, Bauniabadh, Matlab | Study team |
| Matlab HDSS/MHSS | Matlab; longitudinal | icddr,b |
| WHO STEPS 2018 | National 18–69; 400 PSUs | WHO/BBS |
| GBD 2021 | National/subnational modelled | IHME |

## 3. Minimal protocol for Design A

### 3.1 Variables to extract

From the BDHS 2022 biomarker files (BP/glucose/anthropometry) and household recode:

- Identifiers: `v001`, `v002`, `v003`, `caseid`, `dhsclust`.
- Age, sex, weight, height, BMI.
- SBP and DBP (mean of 2nd and 3rd readings where available).
- Fasting glucose.
- Hypertension diagnosis, medication, and control.
- Diabetes diagnosis and medication.
- Wealth (`v190`), education, urban/rural.
- Smoking, cooking fuel, occupation if available.

### 3.2 Outcome definitions

```text
hypertension_measured = (mean_SBP >= 140) OR (mean_DBP >= 90)
hypertension_any      = hypertension_measured OR on_antihypertensive
diabetes_measured     = fasting_glucose >= 7.0 mmol/L
diabetes_any          = diabetes_measured OR diagnosed OR on_medication
```

Report both definitions. Do not silently include or exclude medication.

### 3.3 Exposure

- 1 km PM2.5, LST, NDVI (origin template).
- Annual mean plus 3-year mean (2020–2022).
- Optional O3 from Sentinel-5P/CAMS.
- Urban 2 km / rural 5 km buffers, with sensitivity.

### 3.4 Model and validation

- Random Forest, class-balanced, same hyperparameters as the origin.
- Cluster-grouped and leave-one-upazila-out CV.
- Report prevalence, PR-AUC (diabetes may be ~10–20%, so PR-AUC is still useful), calibration, SHAP.
- Weighted prevalence with `v005` and design variables.

### 3.5 Mapping

Aggregate predicted hypertension/diabetes prevalence and uncertainty to upazilas. Compare with STEPS 2018 and GBD. Flag the 1/6 subsample limitation on the map caption.

## 4. What to expect

- The 60+ sample is much smaller than the child cohort; events per variable may be limiting.
- Hypertension prevalence in older adults is high (often 40–60%), so the rare-event problem is less severe than child ARI.
- Diabetes may be underdiagnosed; measured glucose is preferable to self-report.
- The biomarker subsample is not a simple random sample; use the provided weights and state the design.
- PM2.5–hypertension associations are plausibly small; a null or weak result is informative.

## 5. What not to do

- Do not use the chronic-disease module (women 15–49) as if it described 60+.
- Do not claim COPD, dementia, or cancer from DHS.
- Do not pool children and older adults.
- Do not call a cross-sectional association causal.
- Do not map 60+ prevalence without flagging the biomarker subsample.

## 6. Sub-skill

Create `skills/older-adults-bangladesh/` with the files below (paths relative to the new sub-skill):

- `SKILL.md`: delta from the origin (population, outcomes, window, confounders).
- `references/variables.md`: exact DHS variable names and codes.
- `templates/build_older_cohort.py`: BP/glucose extraction and outcome definitions.
- `templates/older_rf_shap.py`: reuse the origin model with the new outcomes.

Link back to the origin for exposure extraction, validation, and mapping; do not duplicate them.

## 7. Decision guide

| Goal | Design |
|---|---|
| Publish quickly with national data | A (DHS biomarker) |
| Cover COPD/IHD/stroke/lung cancer/dementia | B (GBD) or C (cohort) |
| Causal or longitudinal inference | C (cohort) |
| Policy burden estimate | B (GBD) |
| Methods paper / replication | A + origin pipeline |
