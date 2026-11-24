# Example: Bangladesh child ARI (BDHS 2022)

A replication and extension guide for the origin study. Read `references/bangladesh.md` first.

## 1. What you are reproducing

Moniruzzaman (2026) linked 1 km MODIS PM2.5, LST, and NDVI to 8,784 children under five in 344 upazilas, fitted a class-balanced Random Forest, interpreted it with TreeSHAP and a logistic GAM, and mapped predicted ARI prevalence plus tree-level uncertainty.

Reference values:

| Quantity | Value |
|---|---|
| Children | 8,784 |
| ARI cases | 95 (1.08%) |
| Clusters / upazilas | 673 / 344 |
| PM2.5 | 34.8–92.7 µg/m³ (mean 67.5) |
| LST / NDVI | 27.2 °C / 0.508 |
| Cluster CV AUC | 0.667 |
| Spatial CV AUC | 0.544 |
| SHAP: LST / NDVI / PM2.5 | 0.105 / 0.090 / 0.075 |
| GAM inflection | ~55–65 µg/m³ |
| Predicted prevalence | 0.2–3.8% |

## 2. Access

1. Register at https://dhsprogram.com.
2. Request **Bangladesh 2022** standard DHS: KR, PR, GE, IR, HR.
3. Download `BDKR81FL.DTA`, `BDPR81FL.DTA`, `BDGE81FL.DTA`.
4. Read the data-use agreement and confirm IRB.
5. Get `BGD_adm3` from BBS (or GADM/HDX) and check the upazila count.

Do not commit any of these files. The repository `.gitignore` blocks the common patterns, but check manually.

## 3. Build the cohort

```bash
python skills/explainable-geoai-health/templates/build_dhs_cohort.py \
  --kr data/BDKR81FL.DTA \
  --pr data/BDPR81FL.DTA \
  --ge data/BDGE81FL.DTA \
  --admin data/BGD_adm3.shp \
  --out outputs/cohort_bdhs2022.csv
```

Check the QA JSON:

- 8,943 children in KR.
- 147 excluded for missing/don't know.
- 12 excluded for an unmatched cluster.
- 8,784 analysed; 95 cases; 1.08%.

If your counts differ, stop and reconcile before modelling. Common causes: wrong recode, value labels applied as strings, or a different cluster ID field.

## 4. Extract exposures

Edit `templates/gee_exposure_extraction.js`:

```javascript
assetId: 'users/YOUR_USERNAME/BDGE81FL_2022',
adminAssetId: 'users/YOUR_USERNAME/BGD_adm3',
year: 2022,
buffers: { urban: 2000, rural: 5000 },
pm25: { slope: 120, intercept: 15 }
```

Run it in the Earth Engine Code Editor. Export `DHS_2022_cluster_exposures.csv` and `DHS_2022_upazila_exposures.csv` to Drive.

Merge the cluster exposures into the cohort on `DHSCLUST`/`dhsclust`. The cohort script does not do this automatically because the GEE export is a separate step; add a merge or run a short pandas join.

Validate:

```bash
python skills/explainable-geoai-health/scripts/validate_exposure.py \
  --clusters outputs/cluster_exposures.csv \
  --out outputs/exposure_qa.json
```

Check that PM2.5 spans roughly 35–93 µg/m³. If it is in the tens of thousands, the MAIAC AOD scale factor (0.001) is missing. If it is much lower or higher, the AOD band or calibration is wrong.

## 5. Model and SHAP

```bash
python skills/explainable-geoai-health/templates/rf_shap.py \
  --data outputs/cohort_with_exposures.csv \
  --outcome ari_outcome --cluster dhsclust --spatial upazila_pcode \
  --outdir outputs/rf
```

Expected: the paper reports cluster CV AUC 0.667 and spatial CV 0.544. On the public Zenodo master CSV the same model yields ~0.48–0.55, because that CSV is not the paper's exact analytical table (see `references/bangladesh.md`). Treat 0.667 as the paper's result, not a target. If both CVs are ~0.9, you have leakage. If both are ~0.5, check the feature merge and the AOD scale.

Inspect:

- `feature_importance.csv` — LST > NDVI > PM2.5.
- `calibration_quintiles.csv` — monotonic 0.4 → 2.8%.
- `shap_dependence_*.png` — PM2.5 rising above ~60; LST U-shaped; NDVI negative.

## 6. Spatial validation

```bash
python skills/explainable-geoai-health/templates/spatial_cv.py \
  --data outputs/cohort_with_exposures.csv \
  --outcome ari_outcome --spatial upazila_pcode --cluster dhsclust \
  --admin data/BGD_adm3.shp --outdir outputs/spatial
```

The leave-one-upazila-out AUC is the honest number. Do not headline the cluster CV.

## 7. GAM

```bash
python skills/explainable-geoai-health/templates/gam_exposure_response.py \
  --data outputs/cohort_with_exposures.csv \
  --outcome ari_outcome --exposure pm25_ug --cluster dhsclust \
  --outdir outputs/gam
```

Report the peak-slope region and the bootstrap 95% CI. Do not call it a safe threshold.

## 8. Maps

```bash
python skills/explainable-geoai-health/templates/map_risk.py \
  --admin data/BGD_adm3.shp --pred outputs/rf/predictions.csv \
  --spatial upazila_pcode --outcome ari_outcome --outdir outputs/maps
```

Mask the 119 upazilas without DHS coverage. The northwest (Rangpur) should stand out.

## 9. What to improve

- Replace `AOD × 120 + 15` with V5.GL.04/CHAP or a local calibration; report both.
- Add fuel, crowding, maternal education, and vaccination if the data allow.
- Use a 2-week lagged exposure if a gap-filled daily product is available.
- Add a spatial random effect or a BYM2 model for the map.
- Report PR-AUC and calibration, not only AUC.
- Bootstrap the GAM and the map.

## 10. Output checklist

- [ ] Cohort CSV + QA JSON.
- [ ] Cluster and upazila exposure CSVs.
- [ ] `metrics.json` with cluster and spatial CV.
- [ ] `feature_importance.csv`.
- [ ] SHAP global, dependence, interaction.
- [ ] GAM curve + bootstrap.
- [ ] Risk and uncertainty maps.
- [ ] Data manifest.
- [ ] Manuscript outline.

## 11. Common failures

| Symptom | Likely cause |
|---|---|
| 0 cases | Wrong `h31c` coding, or outcome filtered out |
| AUC ~0.5 | Exposure merge failed; all PM2.5 missing |
| AUC ~0.99 | Outcome leakage or child-level CV |
| PM2.5 ~10 µg/m³ | AOD band/scale wrong or calibration not applied |
| Empty map | Spatial key mismatch (`adm3_pcode` vs `upazila_pcode`) |
| GAM error | `v190` read as string; cast or use `C(v190)` |
