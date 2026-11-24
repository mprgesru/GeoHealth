# Methodology

## 1. Exposure assignment

For person \(i\) in cluster \(c\), the exposure is the mean of raster values \(X(s)\) inside a buffer \(B_c\):

\[
\bar{X}_{c} = \frac{1}{|B_c|}\int_{B_c} X(s)\,ds
\]

Buffers follow the DHS displacement protocol:

| Residence | Buffer | Sensitivity |
|---|---|---|
| Urban | 2 km | 1–3 km |
| Rural | 5 km | 3–7 km |

In Earth Engine, `reduceRegions` with `ee.Reducer.mean()` at the product scale (1,000 m for MODIS). In Python, `rasterstats.zonal_stats` or `exactextract`.

**Why buffers, not points:** displaced coordinates can be several kilometres from the true cluster. A buffer average is less sensitive to displacement than a point sample, at the cost of smoothing.

## 2. PM2.5 from AOD

The reference conversion is:

\[
\text{PM}_{2.5} = 120 \times \text{AOD}_{470} + 15
\]

This is a South Asia calibration, not a physical model. It ignores aerosol vertical distribution, hygroscopic growth, and composition. MAIAC stores AOD as scaled integers, so apply `AOD × 0.001` **before** the calibration; otherwise PM2.5 lands in the tens of thousands. Report:

- the calibration source and validation (Dhaka CAMS: RMSE 12.4, MAE 9.8, n = 36 station-days);
- a comparison with an independent product (V5.GL.04 or CHAP);
- the correlation and mean bias between the two;
- a sensitivity model using the independent product.

A better calibration, if monitors allow:

\[
\text{PM}_{2.5} = f(\text{AOD}, \text{RH}, \text{BLH}, \text{wind}, \text{season}, \text{land use})
\]

with a held-out station-year validation.

## 3. Outcome models

### 3.1 Random Forest

For \(y_i \in \{0,1\}\), the forest predicts

\[
\hat{p}_i = \frac{1}{T}\sum_{t=1}^{T} \hat{p}_{t}(x_i)
\]

Baseline: 100 trees, `max_depth=10`, `min_samples_leaf=10`, `class_weight="balanced"`. Balanced weights change the effective prior; calibrate probabilities before interpreting them as risk.

### 3.2 Logistic GAM

\[
\text{logit}(p_i) = \beta_0 + s(\text{PM}_{2.5,i}) + \beta_1 \text{LST}_i + \beta_2 \text{NDVI}_i + \gamma^\top z_i
\]

with a cubic regression spline, \(k=4\). The spline captures non-linearity; the CI is wider at the exposure extremes. Treat any inflection as exploratory.

### 3.3 XGBoost (sensitivity)

Use the same features and CV. Report whether the SHAP ranking and the inflection region change.

## 4. Cross-validation

### 4.1 Cluster-grouped k-fold

\[
\text{folds} = \text{GroupKFold}(k=5, \text{groups}=\text{cluster})
\]

Children in the same cluster share exposures and survey context; keeping them together prevents leakage.

### 4.2 Leave-one-upazila-out

For each upazila \(u\): train on all other upazilas, predict \(u\). This is the honest test when exposures are assigned at upazila level. It is more pessimistic than cluster CV and should be the headline.

### 4.3 Nested CV

If tuning, use an inner loop for hyperparameters and an outer loop for evaluation. Do not tune on the test fold.

## 5. Metrics

| Metric | Formula / note |
|---|---|
| Prevalence | \(\sum y_i / n\) |
| AUC-ROC | Rank-based; insensitive to prevalence |
| PR-AUC | Area under precision–recall; better for rare events |
| Precision | TP / (TP + FP) |
| Recall | TP / (TP + FN) |
| F1 | Harmonic mean of precision and recall |
| Brier | \(\frac{1}{n}\sum(\hat{p}_i-y_i)^2\) |
| Calibration slope | Regress \(y\) on logit(\(\hat{p}\)); slope 1 is ideal |
| Calibration intercept | Intercept of the same model; 0 is ideal |

Report bootstrap 95% CIs, resampling clusters rather than individuals.

## 6. Calibration by risk quintile

Aggregate \(\hat{p}\) to upazila, sort into quintiles, and compute observed prevalence per quintile. A monotonic gradient supports spatial stratification. The reference study: 0.4 / 0.6 / 1.0 / 1.8 / 2.8%.

## 7. SHAP

For feature \(j\) and observation \(i\), the Shapley value \(\phi_{ij}\) satisfies

\[
\hat{f}(x_i) = \phi_{i0} + \sum_j \phi_{ij}
\]

Global importance:

\[
I_j = \frac{1}{n}\sum_i |\phi_{ij}|
\]

Use `shap.TreeExplainer`; isolate the positive class; recompute after every model change. Dependence plots show \(\phi_{ij}\) vs \(x_{ij}\); LOWESS smoothing reduces the staircase artefact of tree models. Interaction values show whether the PM2.5 contribution depends on temperature.

**Interpretation:** SHAP explains the fitted model, not the biological effect. A positive value means the feature pushed the prediction up relative to the average, not that it caused the outcome.

## 8. Spatial diagnostics

### 8.1 Moran's I

\[
I = \frac{n}{\sum_{ij} w_{ij}} \frac{\sum_{ij} w_{ij}(z_i-\bar{z})(z_j-\bar{z})}{\sum_i (z_i-\bar{z})^2}
\]

Compute on upazila residuals. Significant positive autocorrelation means the model has left spatial structure unexplained; consider spatial random effects or a spatial model.

### 8.2 Predicted–observed correlation

Spearman \(\rho\) between predicted and observed upazila prevalence, with a permutation p-value. The reference study: 0.48.

## 9. Uncertainty

Two complementary measures:

1. **Tree dispersion:** \(\text{SD}_t(\hat{p}_{ti})\) across trees. Cheap, but reflects model variance, not sampling variance.
2. **Bootstrap:** resample clusters, refit, and compute the SD of predictions. More honest, more expensive.

Map the uncertainty and flag units with few clusters.

## 10. Survey design

Weighted prevalence:

\[
\hat{p} = \frac{\sum_i w_i y_i}{\sum_i w_i}
\]

Design-based variance uses strata and PSUs (R `survey` or Python `samplics`). If the ML model ignores weights, state it and report weighted prevalence alongside.

## 11. Sample size and rare events

With 95 events and ~7 predictors, events per variable is comfortable; with 20+ predictors it is not. Report:

- events per variable;
- the number of clusters and upazilas;
- the number of upazilas with fewer than 5 clusters;
- the precision–recall curve, not just AUC.

## 12. Older adults

Use the same machinery with four changes:

1. **Exposure window:** annual + 3-year (or 5–10 year) means.
2. **Outcome:** measured hypertension/diabetes, not ARI.
3. **Confounders:** smoking, biomass fuel, BMI, medication, comorbidity.
4. **Design:** age/sex stratification and design-based prevalence.

See `older-adults.md`.
