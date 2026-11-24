# Changelog

## 0.1.0 — 2026-11-24

Initial origin release, distilled from Moniruzzaman (2026), *GeoHealth* 10, e2026GH002051.

Added:

- `skills/explainable-geoai-health/SKILL.md` with scope, principles, phases, output contract, quality gates.
- `references/workflow.md`, `bangladesh.md`, `older-adults.md`, `data-sources.md`, `methodology.md`, `qa-checklist.md`, `licenses.md`, `figure-style.md`, `prompt-playbook.md`.
- `templates/gee_exposure_extraction.js`, `build_dhs_cohort.py`, `rf_shap.py`, `spatial_cv.py`, `gam_exposure_response.py`, `map_risk.py`, `manuscript_outline.md`, `data_manifest.template.csv`.
- `scripts/qa_cohort.py`, `validate_exposure.py`.
- `examples/bangladesh_child_ari.md`, `bangladesh_older_adults.md`.
- Repository README, skill registry, MIT licence, citation metadata.
- Reproducibility notes: the MAIAC AOD 0.001 scale is applied in the GEE template; the public Zenodo master CSV is flagged as not matching the paper's Table 2.

Known gaps to close in later releases:

- A runnable notebook using the public Zenodo master CSV (no GPS) for the modelling half.
- A women's-health sub-skill (menstrual/reproductive outcomes, biomass fuel, heat).
- A true leave-one-upazila-out implementation benchmarked against the paper's reported 0.544.
