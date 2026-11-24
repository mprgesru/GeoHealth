# Templates

Run order and dependencies. All paths are relative to the skill directory.

| Step | File | Needs |
|---|---|---|
| 1 | `gee_exposure_extraction.js` | Earth Engine, your DHS cluster asset, admin asset |
| 2 | `build_dhs_cohort.py` | DHS KR/PR/GE, `pandas`, `pyreadstat`, optional `geopandas` |
| 3 | `rf_shap.py` | cohort + exposures, `scikit-learn`, `shap`, `statsmodels` |
| 4 | `spatial_cv.py` | same, for leave-one-upazila-out and Moran's I |
| 5 | `gam_exposure_response.py` | same, `statsmodels`, `patsy` |
| 6 | `map_risk.py` | predictions + admin boundaries, `geopandas` |
| 7 | `manuscript_outline.md` | results and figures |

## Minimal environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas numpy scikit-learn shap statsmodels matplotlib scipy pyreadstat geopandas
```

`pyreadstat` is only needed for `.dta`/`.sav`; `geopandas` is only needed for the spatial join and maps.

## Conventions

- Every script takes `--outdir` and writes its own outputs.
- Every script prints a JSON summary; redirect it if you need a log.
- Random seeds are fixed at 42 unless overridden.
- No script writes coordinates or microdata to a public path.

## Not included

- DHS microdata.
- Boundaries.
- Raster tiles.
- Any private Earth Engine asset.

Bring your own licensed data.
