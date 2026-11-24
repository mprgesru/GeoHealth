# Older adults: what DHS has, what it does not, and how to design the study

This reference exists because the child-ARI pipeline does **not** transfer unchanged to older adults. The outcome, exposure window, confounders, and data source all change.

## 1. Bottom line

**Standard DHS does not interview people aged 60+.** Bangladesh 2022 is ever-married women 15–49, with no men's individual questionnaire. The survey does, however, contain a biomarker subsample that measured blood pressure, fasting glucose, and anthropometry in adults 18+, including people 50+ and 60+.

So DHS Bangladesh 2022 can support a study of **measured hypertension, diabetes, and obesity in older adults** — not COPD, ischaemic heart disease, stroke, lung cancer, or dementia.

## 2. DHS 2022 elderly data inventory

| Data need | Available? | Detail |
|---|---|---|
| Individual interview 60+ | **No** | Woman's Questionnaire: ever-married women 15–49 |
| Men's individual interview | **No** | No `BDMR81` file for 2022 |
| Measured BP 60+ | **Yes** | 1/6 of households; all adults 18+; ~8,156 women + 6,853 men eligible |
| Fasting glucose 60+ | **Yes** | Same subsample; ~95% of women and ~91% of men measured |
| Height/weight/BMI 60+ | **Yes** | Women 50+ and men 18+ in the subsample |
| Self-reported chronic disease 60+ | **No** | Chronic Disease module fielded only to women 15–49 |
| COPD / IHD / stroke / lung cancer / dementia | **No** | Not collected at any age |
| Disability 60+ | **No** | DHS Disability module exists but was not fielded in BDHS 2022 |
| Mental health 60+ | **No** | Module is for women 15–49 |
| Household roster, wealth, education | **Yes** | All household members; elderly can be characterised |
| Cluster geolocation | **Yes** | GE81; displaced; same buffer rules |
| Cause of death 60+ | **Partial** | Verbal autopsy file; primarily under-5 |

The household roster (`BDPR81`/`BDHR81`) lets you describe older household members and link them to the household environment, but it does **not** give you their health outcomes.

## 3. Outcome mapping

| Outcome | What you need | DHS 2022 | Feasible alternative |
|---|---|---|---|
| Hypertension | Measured SBP/DBP or diagnosis + medication | **Yes** (biomarker subsample) | STEPS 2018; MHPD |
| Diabetes | Fasting glucose, diagnosis, or medication | **Yes** (biomarker subsample) | STEPS 2018; MHPD |
| Obesity | Measured height/weight | **Yes** | STEPS; MHPD |
| COPD | Spirometry or physician diagnosis | **No** | GBD; clinical cohort; primary survey |
| Ischaemic heart disease | Medical record, self-report, or GBD | **No** | BELIEVE; GBD |
| Stroke | Medical record, self-report, or GBD | **No** | BELIEVE; GBD |
| Lung cancer | Cancer registry or GBD | **No** | GBD; registry |
| Dementia | Cognitive screen (e.g., 10/66, CSI-D) | **No** | Ageing cohort; GBD |
| Pneumonia | Clinical record; DHS child ARI is under-5 only | **No** | Hospital data; GBD |
| Disability | WHODAS or DHS Disability module | **No** in 2022 | STEPS; MHPD |

## 4. Three feasible designs

### Design A — DHS biomarker extension (feasible now)

**Question:** Are ambient PM2.5, ozone, LST, and vegetation associated with measured hypertension and diabetes in adults 50+ in Bangladesh?

- **Population:** adults 50+ (primary) and 60+ (sensitivity) in the BDHS 2022 biomarker subsample.
- **Outcomes:** measured hypertension (mean SBP ≥140 or DBP ≥90, or on medication); measured diabetes (fasting plasma glucose ≥7.0 mmol/L, or diagnosed/on medication). Report medication-aware and measurement-only definitions.
- **Exposures:** annual and 3-year mean PM2.5; optional O3; LST; NDVI. Use 1 km products.
- **Confounders:** age, sex, wealth, education, urban/rural, BMI, smoking, cooking fuel, comorbidity.
- **Model:** Random Forest + TreeSHAP; cluster- and upazila-grouped CV; survey weights for prevalence.
- **Strengths:** nationally representative, measured outcomes, existing DHS governance, direct reuse of the origin pipeline.
- **Limits:** prevalent not incident outcomes; modest 60+ sample; no COPD/dementia; BP/glucose only in 1/6 of households.

### Design B — GBD burden mapping (feasible now, different design)

**Question:** What is the spatial distribution of PM2.5/O3-attributable COPD, IHD, stroke, lung cancer, and dementia burden in older adults?

- **Data:** GBD 2021 national/subnational estimates; PM2.5 and O3 rasters; population; relative-risk functions.
- **Method:** attributable burden mapping (AF × prevalence/mortality), not individual ML.
- **Strengths:** covers the diseases DHS lacks; policy-relevant.
- **Limits:** ecological; depends on GBD and RR assumptions; not a survey-based association study.

### Design C — Ageing cohort (best for the full disease list)

| Dataset | Coverage | Outcomes | Access |
|---|---|---|---|
| MHPD 2023 (Mahbub Hossain Panel Data + Population Aging Module) | ~5,500 interviews, ~2,000 aged 60+; rural panel | Health, cognition, well-being, economic status | BRAC / ADB / custodian agreement |
| BELIEVE | 73,883 adults ≥11; Mirpur, Bauniabadh, Matlab | CVD events, risk factors | Study team application |
| Matlab HDSS / MHSS | Matlab; longitudinal | Cause-specific mortality, health, disability | icddr,b / custodians |
| WHO STEPS 2018 | National, 18–69; 8,185 participants, 400 PSUs | NCD risk factors, BP, glucose, self-reported diagnosis | WHO/BBS; request microdata |
| GBD 2021 | National/subnational modelled | COPD, IHD, stroke, lung cancer, dementia | IHME terms |

WHO SAGE wave 1/2 did not include Bangladesh; check the current country list before relying on it.

## 5. Exposure windows

| Outcome | Suggested window | Rationale |
|---|---|---|
| Hypertension / diabetes | Annual + 3-year mean | Subclinical effects accumulate over years |
| COPD | 5–10 year mean | Long latency; smoking is the dominant confounder |
| IHD / stroke | 5–10 year mean | Atherosclerosis latency |
| Lung cancer | 10–20 year mean | Long induction |
| Dementia | 10+ year mean | Very long latency; difficult to identify |
| Pneumonia (elderly) | Weeks | Acute; not available in DHS |

Do not reuse the child-ARI 2-week recall window for chronic outcomes. If only one year of exposure is available, say so and interpret as a cross-sectional association.

## 6. Confounders that matter more in older adults

- Age (continuous and spline), sex.
- Smoking status, pack-years, second-hand smoke.
- Household cooking fuel (biomass vs clean) and ventilation.
- Occupational exposure (dust, fumes, traffic).
- BMI, waist circumference.
- Blood pressure, fasting glucose, lipids (where measured).
- Comorbidity and medication use.
- Wealth, education, urban/rural, healthcare access.
- Indoor air pollution is a first-order confounder for COPD and pneumonia; do not omit it silently.

## 7. Statistical considerations

- **Prevalent vs incident outcomes:** DHS and STEPS are cross-sectional. Use "association" and "prevalence", not "risk" or "incidence".
- **Survey design:** weights, strata, PSUs. Report weighted prevalence; use design-based SEs or cluster bootstrap.
- **Rare outcomes:** report events per variable; consider penalised regression (Firth) or a GAM; avoid deep trees.
- **Age/sex stratification:** report sex-specific models or interactions; do not assume the same exposure response.
- **Competing risk:** for mortality outcomes, use competing-risk models, not naive logistic regression.
- **Small-area smoothing:** consider BYM2/INLA for admin maps; do not over-smooth away real hotspots.
- **Spatial autocorrelation:** Moran's I on residuals; spatial CV by upazila/PSU.
- **Multiple comparisons:** pre-specify primary outcomes; adjust or flag exploratory ones.

## 8. Minimal protocol for Design A

```yaml
population: adults 50+ in BDHS 2022 biomarker subsample
outcomes:
  hypertension: mean(SBP) >= 140 or mean(DBP) >= 90 or on antihypertensive medication
  diabetes: fasting glucose >= 7.0 mmol/L or diagnosed/on medication
exposures: [pm25_annual, pm25_3yr, lst, ndvi, o3_optional]
buffers: {urban: 2, rural: 5}
confounders: [age, sex, wealth, education, urban_rural, bmi, smoking, cooking_fuel]
model: RandomForestClassifier(class_weight=balanced)
validation: [cluster_grouped_5fold, leave_one_upazila_out]
reporting: [prevalence, PR-AUC, calibration, SHAP, GAM]
```

Steps:

1. Extract the biomarker subsample from `BDHR81`/BP-glucose files; keep `v001`, `v002`, `v003`, age, sex, weight, height, SBP, DBP, glucose, medication.
2. Define hypertension and diabetes with and without medication.
3. Merge cluster GPS and upazila.
4. Extract 1 km exposures with the origin GEE template; add 3-year means.
5. Fit RF + SHAP; validate by cluster and upazila.
6. Map predicted prevalence and uncertainty; compare with STEPS/GBD.
7. Report the 60+ sample size and power explicitly.

## 9. Quality gates

Stop if:

- The chronic-disease module (women 15–49) is used as if it described 60+.
- COPD, dementia, or cancer is claimed from DHS.
- Children and older adults are pooled without stratification.
- Hypertension/diabetes definitions ignore medication.
- The 1/6 biomarker subsample is treated as a simple random sample of all adults.
- Only random CV is reported.
- A cross-sectional association is written as a causal effect.
- The exposure window is shorter than the outcome's plausible latency without acknowledgment.

## 10. Manuscript framing

Use "environmental correlates of measured hypertension/diabetes among older adults", not "air pollution causes COPD". State the DHS age restriction in the methods, the biomarker subsample in the limitations, and the absence of COPD/dementia outcomes in the discussion. If the goal is the full chronic-disease list, pair Design A with Design B (GBD burden) or move to Design C (cohort).
