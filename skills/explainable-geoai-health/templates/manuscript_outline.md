# Manuscript outline

A GeoHealth-style empirical paper. Adapt the section names to the target journal, but keep the reporting items.

## Title

State the population, exposure, outcome, and setting. Example:

> Explainable geospatial AI reveals associations between ambient air quality and thermal predictors of child respiratory disease in Bangladesh

Avoid causal verbs ("causes", "reduces") unless the design supports them.

## Abstract (structured)

- **Background:** burden, gap, why geospatial AI.
- **Methods:** survey, N, clusters, admin units, exposure products and buffers, model, validation.
- **Results:** prevalence and cases; exposure range; CV AUC (cluster and spatial); top SHAP predictors; exposure-response pattern; priority areas.
- **Conclusions:** spatial prioritisation, not individual prediction or causal burden.

## 1. Introduction

1. Burden of the outcome.
2. Why this setting.
3. Limits of ground monitoring and fine-scale health data.
4. Satellite exposure assessment.
5. Explainable ML and SHAP.
6. Gap and aims.

## 2. Materials

### 2.1 Study area
Boundaries, admin hierarchy, climate, population, why the spatial unit was chosen.

### 2.2 Data sources
Survey files, EO products, boundaries. Table with N, resolution, variables, year.

### 2.3 Nested denominators
Official units vs mapped units vs units with survey coverage vs analysed sample. Explain every difference.

## 3. Methods

### 3.1 Satellite processing
Products, bands, scale factors, annual composites, PM2.5 conversion and validation.

### 3.2 Survey integration
GPS displacement, buffers, spatial linkage, weights/strata/PSU.

### 3.3 Outcome definition
Exact questions and codes; missing/"don't know"; recall window.

### 3.4 Inclusion/exclusion
Flow and counts.

### 3.5 Model
Algorithm, hyperparameters, class weighting, feature list, seed.

### 3.6 Validation
Cluster CV, spatial/leave-one-admin-out CV, metrics, calibration, bootstrap.

### 3.7 Explainability
TreeSHAP, dependence, interaction, GAM specification, inflection definition.

### 3.8 Mapping
Aggregation, uncertainty, coverage mask.

### 3.9 Ethics and data availability
DHS registration/IRB; no redistribution; AI disclosure if relevant.

## 4. Results

1. Population characteristics (Table 1).
2. Exposure patterns (Figure: PM2.5 map).
3. Observed outcome (Figure: prevalence map).
4. Exposure-response (GAM; Figure).
5. Model performance (Table: cluster vs spatial CV; PR curve).
6. Feature importance and SHAP (Table; Figures).
7. Interaction (Figure).
8. Predicted risk and uncertainty (Figure).
9. Calibration and priority areas.

## 5. Discussion

1. Principal findings.
2. Comparison with prior evidence.
3. Why temperature/NDVI may outrank PM2.5 (if they do).
4. Spatial pattern and plausible sources.
5. Implications for surveillance and targeting.
6. Strengths.
7. Limitations (see below).
8. Future research.

## 6. Limitations

- Cross-sectional design; no temporality.
- Exposure window vs outcome recall mismatch.
- Displaced coordinates and buffer smoothing.
- AOD-to-PM2.5 conversion error; 1 km smoothing.
- Unmeasured confounding (indoor air, occupation, smoking, access).
- Rare-event instability; low precision.
- Ecological fallacy; admin-level exposures.
- Generalisability to other settings.
- No ground-truth outcome validation.

## 7. Conclusion

Three sentences: what was done, what was found, what it means for prioritisation. No causal claim.

## 8. Data and code availability

Name the survey, access route, EO products, and repository. Do not include coordinates.

## Reporting checklists

- **TRIPOD+AI** for prediction-model reporting.
- **PROBAST** for risk-of-bias assessment.
- **RECORD**-style flow for observational data.
- **STROBE** for the epidemiological skeleton.

## Tables and figures

| Item | Content |
|---|---|
| Table 1 | Population and exposure descriptives |
| Table 2 | Model performance (cluster and spatial CV) |
| Table 3 | Feature importance (impurity and mean \|SHAP\|) |
| Table S1 | Full metrics per fold |
| Table S2 | Threshold/robustness analyses |
| Table S3 | Top/bottom admin units |
| Figure 1 | Study area |
| Figure 2 | Workflow |
| Figure 3 | Exposure map |
| Figure 4 | Observed outcome map |
| Figure 5 | GAM exposure-response |
| Figure 6 | SHAP global + interaction |
| Figure 7 | SHAP dependence |
| Figure 8 | Predicted risk + uncertainty |

## Writing rules

- Use "association", "predictor", "contribution".
- Do not write "safe threshold", "attributable cases", "caused by", "protects".
- Report the honest spatial CV next to the optimistic cluster CV.
- State the prevalence and case count in every results subsection.
- Give units and denominators everywhere.
