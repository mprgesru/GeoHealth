# Licences and data governance

This is a practical summary, not legal advice. Read the actual terms before publishing.

## 1. DHS / MICS microdata

- Access requires registration, a research purpose, and acceptance of the data-use agreement.
- GPS/cluster coordinates are **restricted** and displaced. Do not attempt to re-identify clusters or individuals.
- Do not redistribute microdata, recodes, GPS files, or cluster-level identifiers.
- Publish only aggregate results (e.g., upazila estimates) and the minimum necessary variable list.
- Cite the DHS Program and the specific survey (e.g., NIPORT & ICF, BDHS 2022).
- Some DHS files have additional restrictions (biomarkers, HIV, domestic violence). Check each file.

If a co-author or reviewer asks for the cluster table, share the code and aggregate outputs, not the coordinates.

## 2. NASA / MODIS / Earthdata

- MODIS products are open; cite the product DOI and the LP DAAC.
- MCD19A2.061: https://doi.org/10.5067/MODIS/MCD19A2.061
- MOD11A2.061: https://doi.org/10.5067/MODIS/MOD11A2.061
- MOD13A2.061: https://doi.org/10.5067/MODIS/MOD13A2.061
- Keep the product version and processing date in the manifest.

## 3. Copernicus / ECMWF

- Sentinel-5P, ERA5, and CAMS are generally open with attribution.
- Check the Copernicus licence and the specific dataset terms (some CAMS products have registration requirements).
- Do not redistribute derived products in a way that implies endorsement.

## 4. GBD / IHME

- GBD results are available under IHME's terms; registration may be required.
- Cite GBD 2021 and the specific risk factor.
- Do not present GBD estimates as primary survey data.
- If you compute attributable burden, state the relative-risk function and counterfactual.

## 5. Administrative boundaries

| Source | Typical licence | Note |
|---|---|---|
| BBS Bangladesh | Government data; check terms | Official upazila layer |
| GADM | Free for non-commercial use; check version | Do not redistribute modified boundaries without attribution |
| HDX / OCHA | Usually CC BY or ODbL | Check per dataset |
| OpenStreetMap | ODbL | Attribution and share-alike for derived data |

## 6. Code and documentation

- This repository is MIT (see `LICENSE`).
- You may reuse, modify, and redistribute the code with attribution.
- The MIT licence does **not** grant rights to the data.

## 7. Figures and text from the origin paper

- Moniruzzaman (2026) is CC BY 4.0. You may reuse figures with attribution.
- Do not imply the original author endorses your study.
- If you adapt a figure, state "adapted from" and cite the DOI.

## 8. AI disclosure

- Many journals require disclosure of generative-AI use in writing or analysis.
- The origin paper discloses ChatGPT (GPT-4) for language editing.
- If you use an AI assistant for code or drafting, disclose it in the methods or acknowledgements, and verify all outputs.

## 9. Reproducibility package

Publish:

- code;
- a data manifest;
- non-restricted aggregates;
- figure/table scripts;
- a README with the exact commands.

Do **not** publish:

- DHS microdata or GPS;
- cluster coordinates;
- individual-level predictions that could be linked to a person;
- private Earth Engine asset IDs or tokens.

## 10. Attribution template

> This study uses data from the 2022 Bangladesh Demographic and Health Survey (BDHS), implemented by the National Institute of Population Research and Training (NIPORT) and ICF, and made available by the DHS Program. MODIS products were obtained from the NASA EASE-NASA LP DAAC. The analysis code is available at [repository]. The findings do not represent the views of the data providers.
