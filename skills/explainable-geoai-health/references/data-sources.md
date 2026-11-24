# Data sources

A working inventory. Check the licence and version before use; URLs change.

## 1. Health surveys

| Source | What it gives | Geography | Access | Notes |
|---|---|---|---|---|
| **DHS Program** | Household, child, women's, men's, biomarker, GPS | Cluster (displaced), admin | Registration, IRB, data-use agreement | Standard interviews: women 15–49, men 15–49/54/59; children <5 |
| **MICS** (UNICEF) | Household, women, children, GPS | Cluster | Registration | Similar design; useful where DHS is absent |
| **WHO STEPS** | NCD risk factors, BP, glucose, 18–69 | PSU/district | WHO/BBS request | Bangladesh 2018: 8,185 participants, 400 PSUs |
| **WHO SAGE** | Ageing, health, cognition | National | Registration | Wave 1/2 did not include Bangladesh |
| **MHPD / Population Aging Module** | Older-adult health, cognition, well-being | Rural panel | Custodian (BRAC/ADB) | ~5,500 interviews, ~2,000 aged 60+ |
| **BELIEVE** | CVD events, risk factors, adults ≥11 | 3 sites | Study team | 73,883 participants; Mirpur, Bauniabadh, Matlab |
| **Matlab HDSS / MHSS** | Longitudinal health, mortality | Matlab | icddr,b / custodians | Cause-specific mortality |
| **HRS family** (LASI, CHARLS, SHARE, ELSA, KLoSA, MHAS) | Ageing cohorts | National | Registration | Use for methods transfer, not Bangladesh |
| **GBD / IHME** | Modelled prevalence, mortality, risk factors | National/subnational | IHME terms | For COPD, IHD, stroke, lung cancer, dementia |

DHS recode names for Bangladesh 2022: `BDKR81`, `BDPR81`, `BDGE81`, `BDIR81`, `BDHR81`, `BDVA81`.

## 2. Earth observation

| Dataset | Variable | Resolution | Product ID / access | Licence |
|---|---|---|---|---|
| MAIAC AOD | Aerosol optical depth | 1 km, daily | `MODIS/061/MCD19A2_GRANULES` | NASA open |

> MAIAC AOD is stored as scaled integers. Apply `× 0.001` before any AOD→PM2.5 conversion. The released code for the origin paper omits this step and produces implausible values (tens of thousands of µg/m³).
| MOD11A2 | Land surface temperature | 1 km, 8-day | `MODIS/061/MOD11A2` | NASA open |
| MOD13A2 | NDVI / EVI | 1 km, 16-day | `MODIS/061/MOD13A2` | NASA open |
| VNP46A2 | Nighttime lights | 500 m, daily | `NOAA/VIIRS/001/VNP46A2` | NASA open |
| Sentinel-5P | NO2, O3, SO2, CO, aerosol | 3.5 × 5.5 km | `COPERNICUS/S5P/OFFL/...` | Copernicus open |
| OMI | Ozone, NO2 | 13 × 24 km | `NASA/OMI/...` | NASA open |
| MERRA-2 | Meteorology, PM2.5 components | 0.5° × 0.625° | `NASA/MERRA2/...` | NASA open |
| CAMS | Global atmospheric composition | ~0.4° | ECMWF ADS | Copernicus licence |
| CHAP | ChinaHighPM2.5 (and other pollutants) | 1 km | Zenodo / DOI | Check paper licence |
| V5.GL.04 | Global PM2.5 (Washington) | 0.01° | WashU / NASA | Check terms |
| GHSL | Built-up surface, settlement | 10–100 m | JRC | Copernicus open |
| WorldPop | Population | 100 m | WorldPop | CC BY 4.0 |
| ERA5 | Temperature, precipitation, wind | 0.25° | Copernicus CDS | Copernicus licence |

Earth Engine collection IDs change with versions; pin the collection and date in the script.

## 3. Administrative boundaries

| Source | Levels | Notes |
|---|---|---|
| Bangladesh Bureau of Statistics (BBS) | Division, district, upazila | `BGD_adm3`; 463 polygons in the paper |
| GADM | 0–3 | Consistent cross-country; check names |
| HDX / OCHA | 0–3 | Humanitarian boundaries |
| OSM | Variable | Good for local detail; check completeness |

Always validate geometry (`.is_valid`), dissolve duplicates, and compare counts to the official list before joining.

## 4. Ground validation

| Source | Use |
|---|---|
| OpenAQ | PM2.5/PM10 monitors; sparse in Bangladesh |
| US Embassy Dhaka | Reference PM2.5 |
| CAMS / EANET | Regional background |
| BBS/BMD | National meteorology and air quality |
| Local campaign | Best for AOD→PM2.5 calibration |

For PM2.5 calibration, a defensible minimum is 30–50 collocated station-days across seasons, not one season in one city.

## 5. Exposure products and their trade-offs

| Product | Strength | Weakness |
|---|---|---|
| MAIAC AOD × heuristic | Transparent, easy in GEE | Crude; regional; misses composition and vertical distribution |
| V5.GL.04 | Global, long record, validated | 0.01° (~1 km) but smoothed; may miss local peaks |
| CHAP | 1 km, daily, China-focused | Not Bangladesh; transfer needs validation |
| CAMS | Composition, ozone | Coarse (~0.4°) |
| Sentinel-5P | Ozone, NO2, daily | Coarse; cloud gaps |

Report at least one independent comparison (monitor or product) and the calibration equation.

## 6. Minimum data manifest

| Field | Example |
|---|---|
| `dataset` | BDHS 2022 |
| `file` | BDKR81FL.DTA |
| `version` | DHS-8 |
| `source_url` | https://dhsprogram.com |
| `access_date` | 2026-11-24 |
| `licence` | DHS data-use agreement |
| `geography` | National, cluster |
| `variables` | h31b, h31c, v190, v005 |
| `notes` | GPS displaced; no redistribution |

Use `templates/data_manifest.template.csv`.
