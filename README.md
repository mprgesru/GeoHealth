# GeoHealth

**Explainable geospatial AI for environmental health.** A small, reproducible skill repository for linking satellite-derived environmental exposures to population health outcomes from geocoded surveys — with Bangladesh as the fully specified default and an explicit extension path for older adults and women's health.

This repository is intentionally *not* a data repository. It contains methods, checklists, and runnable templates. Survey microdata (especially DHS GPS) stay under the data provider's terms and are never redistributed here.

## What is here

```text
GeoHealth/
├── skills/
│   ├── README.md                      # skill registry and sub-skill convention
│   └── explainable-geoai-health/      # the origin skill
│       ├── SKILL.md
│       ├── references/
│       │   ├── workflow.md
│       │   ├── bangladesh.md
│       │   ├── older-adults.md
│       │   ├── data-sources.md
│       │   ├── methodology.md
│       │   ├── qa-checklist.md
│       │   ├── licenses.md
│       │   ├── figure-style.md
│       │   └── prompt-playbook.md
│       ├── templates/
│       │   ├── gee_exposure_extraction.js
│       │   ├── build_dhs_cohort.py
│       │   ├── rf_shap.py
│       │   ├── spatial_cv.py
│       │   ├── gam_exposure_response.py
│       │   ├── map_risk.py
│       │   ├── manuscript_outline.md
│       │   └── data_manifest.template.csv
│       ├── scripts/
│       │   ├── qa_cohort.py
│       │   └── validate_exposure.py
│       └── examples/
│           ├── bangladesh_child_ari.md
│           └── bangladesh_older_adults.md
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE
└── .gitignore
```

## The origin study

The skill is distilled from:

> Moniruzzaman, M. (2026). *Explainable geospatial AI reveals associations between ambient air quality and thermal predictors of child respiratory disease in Bangladesh.* GeoHealth, 10, e2026GH002051. https://doi.org/10.1029/2026GH002051

The paper integrates 1 km MODIS MAIAC PM2.5, MOD11A2 land surface temperature, and MOD13A2 NDVI with the 2022 Bangladesh DHS (8,784 children under five, 344 upazilas), fits a class-balanced Random Forest, interprets it with TreeSHAP and a logistic GAM, and maps predicted ARI prevalence plus tree-level uncertainty.

The skill keeps the paper's workflow and fixes the parts that are hard to reproduce: random child-level cross-validation, hard-coded SHAP values, a heuristic AOD-to-PM2.5 conversion, and a private Earth Engine asset.

## Install the skill

### Option A — this repository

The skill is at `.opencode/skills/explainable-geoai-health/` once copied into a project, or reference the directory directly:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["/path/to/GeoHealth/skills"]
}
```

### Option B — global install

```bash
mkdir -p ~/.config/opencode/skills
cp -r skills/explainable-geoai-health ~/.config/opencode/skills/
```

OpenCode discovers `SKILL.md` automatically.

## Quick start (Bangladesh child ARI)

1. Register at https://dhsprogram.com and request **BDHS 2022** (KR, PR, GE, IR files).
2. Read `references/bangladesh.md` and `references/licenses.md` first.
3. Upload the DHS cluster shapefile to your own Earth Engine asset; never use someone else's asset ID.
4. Run `templates/gee_exposure_extraction.js` with your asset and year.
5. Run `templates/build_dhs_cohort.py` to create the analysis table.
6. Run `templates/rf_shap.py` and `templates/spatial_cv.py`.
7. Run `templates/gam_exposure_response.py` and `templates/map_risk.py`.
8. Use `references/qa-checklist.md` before writing anything.

## Older adults and women's health

- `references/older-adults.md` documents what DHS does and does not contain for people aged 60+, the three feasible designs (DHS biomarker, GBD burden mapping, ageing cohort), and a minimal protocol for measured hypertension/diabetes.
- The skill is structured so sub-skills can be added under `skills/<name>/` without forking the origin. See `skills/README.md`.

## Data and licence

- **Code and documentation:** MIT (see `LICENSE`).
- **DHS data:** restricted; registration, IRB, and no redistribution of GPS or cluster coordinates.
- **MODIS / NASA EarthData:** open, cite the product DOIs.
- **GBD / IHME:** subject to IHME terms.
- **Administrative boundaries:** check the source licence (BBS, GADM, HDX, OSM).

Nothing in this repository grants rights to redistribute survey microdata.

## Citation

See `CITATION.cff`. If you use the workflow, cite the origin paper and this repository.
