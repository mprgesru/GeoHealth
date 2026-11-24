# Bangladesh configuration

This is the fully specified default for the origin skill. Treat every number here as a **reference value to reproduce or explain**, not as a target to force.

## 1. Administrative frame

| Level | Count | Notes |
|---|---|---|
| Division | 8 | Barishal, Chattogram, Dhaka, Khulna, Mymensingh, Rajshahi, Rangpur, Sylhet |
| District | 64 | |
| Upazila | 499 official | The BBS `BGD_adm3` layer used in the paper has **463** polygons |
| Upazilas with DHS coverage | **344** | After linking 673 clusters |
| DHS clusters | **673 linked / 674 in GE81** | One cluster did not match an upazila |

Use upazila as the analytical unit because it matches the Upazila Health Complex and gives a stable balance between sample size and spatial resolution. Map all 463 polygons; analyse only the 344 with survey coverage and mask the rest.

Boundary source: Bangladesh Bureau of Statistics (BBS), `BGD_adm3`. Alternatives: GADM level 2/3, HDX, OSM. Always check the upazila count and names before joining — the 499 vs 463 mismatch is a known source of lost records.

## 2. Survey: BDHS 2022

| File | Content | N |
|---|---|---|
| `BDKR81` | Children's recode | 8,943 children under 5 |
| `BDPR81` | Household member recode | 132,463 household members; 16,367 under-5 |
| `BDGE81` | Geographic data | 674 clusters |
| `BDIR81` | Individual (women) recode | 30,078 women 15–49 |
| `BDHR81` | Household recode | 30,018 households |
| `BDVA81` | Verbal autopsy | Under-5 deaths |

Eligibility: ever-married women age 15–49. **There is no men's recode for BDHS 2022.** The biomarker subsample (1/6 of households) measured blood pressure, fasting glucose, and anthropometry among all adults 18+, including women 50+ and men 18+ — see `older-adults.md`.

Fieldwork: August–December 2022. Exposure year: 2022.

## 3. Outcome: child ARI

| Variable | Meaning | Coding |
|---|---|---|
| `h31b` | Cough in the last 2 weeks | 1 = yes |
| `h31c` | Rapid/chest breathing | chest only / both |
| `h31d` | Chest difficulty | **missing for all observations in BDHS 2022** — do not use |

Definition:

```text
ARI = (h31b == 1) AND (h31c in {chest only, both})
```

Exclude missing and "don't know". Nose-only rapid breathing is not ARI.

Flow: 8,943 − 147 (missing/DK) − 12 (unmatched cluster) = **8,784**. Cases: **95 (1.08%)**.

Descriptives: age 1.9 ± 1.5 years; 51.0% male; cough 5.1%.

## 4. Exposures

| Exposure | Product | Band | Transform |
|---|---|---|---|
| PM2.5 | `MODIS/061/MCD19A2_GRANULES` | `Optical_Depth_047` | annual mean; `AOD × 120 + 15` (µg/m³) |
| LST | `MODIS/061/MOD11A2` | `LST_Day_1km` | ×0.02 − 273.15 (°C) |
| NDVI | `MODIS/061/MOD13A2` | `NDVI` | ×0.0001 |

All at 1 km, 2022 annual means. Reference ranges: PM2.5 34.8–92.7 (mean 67.5 ± 11.3); LST 27.2 ± 1.1 °C; NDVI 0.508 ± 0.099.

**Caveat:** `AOD × 120 + 15` is a South Asia calibration, validated in the paper against Dhaka CAMS with RMSE 12.4 µg/m³ and MAE 9.8 µg/m³ on 36 station-days. It is not a universal model. For a new study, compare it with V5.GL.04 or CHAP, or fit a local calibration with meteorology and monitor data.

### Buffers

| Residence | Primary | Sensitivity |
|---|---|---|
| Urban | 2 km | 1–3 km |
| Rural | 5 km | 3–7 km |

Rationale: DHS displaces urban coordinates up to 2 km and rural up to 5 km (about 1% of rural up to 10 km). Report the median change across buffer specifications (the paper reports ±0.9%).

## 5. Earth Engine asset

The released script uses a **private** asset:

```javascript
projects/project-f3e92b4c-d579-4433-96d/assets/BDGE81FL_2022
```

You cannot use it. Upload your own DHS GE shapefile to your own project and set the asset ID in `templates/gee_exposure_extraction.js`.

## 6. Model and reference results

```python
RandomForestClassifier(
    n_estimators=100, max_depth=10, min_samples_leaf=10,
    class_weight="balanced", random_state=42
)
```

| Metric | Reference value |
|---|---|
| Cluster 5-fold AUC-ROC | 0.667 |
| Spatial (upazila) CV AUC-ROC | 0.544 |
| Accuracy | 0.93 (majority-class driven) |
| Precision | 0.04 |
| Recall | 0.24 |
| F1 | 0.07 |
| Impurity importance: LST / NDVI / PM2.5 | 0.328 / 0.293 / 0.279 |
| Mean absolute SHAP: LST / NDVI / PM2.5 | 0.105 / 0.090 / 0.075 |
| Predicted prevalence range | 0.2–3.8% |
| Tree-SD uncertainty | 0.012–0.089 (mean 0.034) |
| Quintile calibration (Q1→Q5) | 0.4 / 0.6 / 1.0 / 1.8 / 2.8% |
| Predicted–observed Spearman ρ | 0.48 (p < 0.001) |

GAM: logistic, cubic spline `s(pm25, bs="cr", k=4)`, covariates temperature, NDVI, wealth. Inflection region ~55–65 µg/m³; bootstrap median 59.4 (95% CI 52.1–67.8); XGBoost 61.2; dry-season 58. Treat 60 µg/m³ as a prioritisation marker, not a safe threshold.

## 7. Reproducibility note on the public files

The Zenodo master CSV is **not** an exact copy of the paper's analytical table:

| Quantity | Paper | Public master CSV |
|---|---|---|
| Clusters | 673 | 674 |
| Upazilas | 344 | 361 |
| PM2.5 mean | 67.5 | 88.5 |
| PM2.5 max | 92.7 | 124.7 |

Re-running the released model on the public CSV yields AUC ≈0.48–0.55 depending on CV and encoding, not 0.667. The released `GEE_data.csv` stores PM2.5 in the tens of thousands, consistent with a missing AOD scale factor. Use the public files to test the modelling code, not to verify the paper's numbers. Extract your own exposures for a real replication.

## 8. Known quirks in the released materials

| Quirk | Consequence | Fix |
|---|---|---|
| Private GEE asset | Script fails | Upload your own |
| AOD scale factor missing in the released GEE code | PM2.5 in the tens of thousands | Multiply AOD by 0.001 before calibration |
| `AOD × 120 + 15` | Regional, not universal | Compare with a validated product |
| Figure 8 code uses child-level `StratifiedKFold` | Reported 0.544 is not reproduced by that code | Implement leave-one-upazila-out |
| Figure 7 hard-codes mean \|SHAP\| | Figure does not update with data | Recompute from the model |
| GAM treats `wealth_index` as numeric | Misspecified covariate | Use a factor or dummies |
| `h31d` all missing | Cannot use the 3-symptom ARI definition | Use `h31b` + `h31c` |
| Boundary 463 vs 499 upazilas | Unmatched clusters and unmapped areas | Report both and mask |
| Master CSV lacks urban/rural, maternal education, breastfeeding | Cannot adjust for them | Add from PR/IR in a new study |
| Master CSV has `cluster_id` only | No coordinates in the public file | Request GE separately |

## 9. Public materials

- Paper: https://doi.org/10.1029/2026GH002051 (CC BY 4.0)
- Data/code: https://doi.org/10.5281/zenodo.22342590
  - `Master_Child_Environmental_Health_Bangladesh_2022.csv` (8,784 rows; no GPS)
  - `GEE_Code.txt`
  - `Python_Codes_for_Figures_5_6_7.txt`
- DHS: https://dhsprogram.com/data/available-datasets.cfm
- MODIS: MCD19A2.061, MOD11A2.061, MOD13A2.061 (NASA LP DAAC)

The Zenodo master CSV is enough to reproduce the modelling half (RF, SHAP, GAM, calibration) but not the exposure extraction or maps, which need the GE file and boundaries.

## 10. Replication checklist

- [ ] 8,784 children, 95 cases, 1.08%.
- [ ] 673 clusters in 344 upazilas.
- [ ] PM2.5 34.8–92.7, mean 67.5 (if your conversion matches the paper's scale).
- [ ] LST 27.2, NDVI 0.508.
- [ ] Cluster CV AUC reported as your own value; compare with 0.667, do not force it.
- [ ] Spatial CV AUC lower than cluster CV; compare with 0.544.
- [ ] SHAP ranking LST > NDVI > PM2.5.
- [ ] GAM inflection in 55–65.
- [ ] Quintile calibration monotonic.
- [ ] Maps mask the 119 upazilas without DHS coverage.
