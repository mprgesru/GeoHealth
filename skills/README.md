# Skill registry

This repository uses one **origin skill** plus optional **sub-skills**. The origin owns the shared pipeline (exposure extraction, cohort construction, validation, explainability, mapping). A sub-skill owns only what changes for a new outcome or population.

## Origin

| Skill | Path | Status | Scope |
|---|---|---|---|
| Explainable GeoAI for Environmental Health | `explainable-geoai-health/` | **v0.1.0** | Satellite exposures + geocoded survey outcomes; Bangladesh DHS default; child ARI reference implementation |

## Sub-skills

| Sub-skill | Path | Status | What it changes |
|---|---|---|---|
| Child ARI (Bangladesh) | `child-ari-bangladesh/` | planned | Locks the origin to BDHS 2022, `h31b`/`h31c`, 2/5 km buffers; adds a replication checklist |
| Older adults | `older-adults-bangladesh/` | planned | New outcomes (measured hypertension/diabetes; GBD chronic disease), multi-year exposure windows, ageing cohorts |
| Women's health | `women-health-bangladesh/` | planned | Reproductive/maternal outcomes, biomass fuel, heat, anaemia; DHS women's module |

## Convention

A sub-skill is a directory with its own `SKILL.md` and may reference the origin:

```text
skills/
├── explainable-geoai-health/     # origin
└── older-adults-bangladesh/
    ├── SKILL.md
    ├── references/
    └── templates/
```

In `SKILL.md`, sub-skills should:

1. State the delta from the origin (outcome, population, exposure window, data source).
2. Reuse origin templates by relative path rather than copying them.
3. Carry only the new variables, quality gates, and manuscript framing.
4. Never duplicate the origin's data-governance and licence rules; link to them.

## Naming

- Use lower-case, hyphenated names.
- Prefix with the population or outcome, suffix with the country when the data source is national.
- Keep the origin name stable: `explainable-geoai-health`.
