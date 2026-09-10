# Master evidence bank (companion)

Canonical structured record: `knowledge/evidence_bank.yaml`.
Last reviewed: 2026-09-10.

This file is a human-readable index of what `resumes/base/JZ_resume.tex` may claim.
It is not a generator. Future SWE / ML / AI-infra / Health-AI one-pagers should
select from the YAML and rewrite bullets. Do not mint a second source of truth.

## Architecture

```text
GitHub + artifacts
  -> knowledge/evidence_bank.yaml
  -> master resume (this folder)
  -> later role-specific one-page views
```

`resumes/base/` is the master resume. Polar still prefers the Simplify-attached
resume. The compiled `JZ_resume.pdf` is the empty-widget fallback, not proof that
every application uses this file.

## Projects on the master resume

| YAML key | Master role | Notes |
|---|---|---|
| `cellot_wyss` | speciesOT research | scGen and CellOT are components, not standalone resume projects |
| `autoresearch_cellot` | experiment system | Distinct from speciesOT. LLM path implemented, never exercised |
| `mixhvg_py` | scientific software | GPL-3 port. Do not vendor into speciesOT |
| `job_search_os` | systems / agents | Human-supervised. Not fully autonomous |
| `sseg_rlvr` | current capstone | Method + repo only. No training metrics |
| `alphafold_pipeline` | older HPC tooling | Kept, shortened |
| `compleg_uk_nz` | older SWE / ETL | Kept, shortened |
| `airway_chatbot` | product / RAG | Kept |

## Demoted from the master (still in YAML)

Transformer reimplementation and the four SHBT/BST coursework projects
(`cv_caltech101`, `cv_segmentation_voc`, `vlm_textvqa_lora`, `cv_pneumonia`).
They remain available for later ML one-pagers.

## Claim classes

Use `VERIFIED_MEASURED`, `VERIFIED_IMPLEMENTED`, `USER_REPORTED`, or `PLANNED`.
PLANNED items are not accomplishments.

Do not claim DatasetHandle, FrozenAE, JobPlan, CellOTModel, or ReferenceBundle
as shipped on speciesOT `main`. GitHub lists PRs 1-7 as MERGED. Those merge
commits are not on live `origin/main` `109bf12`. PRs 8-10 stay open.

A-D $R^2$ 0.85-0.90 / 0.65-0.67 is the AutoResearch LPS / rat-in-train prior.
It is not a Tabula atlas result.

Do not claim that an LLM directed AutoResearch runs.

Do not quote new speciesOT scorecard decimals until Junyi clears them.

## Polar attach

Prefer the Simplify resume already attached.
If the widget is empty, do not upload `resumes/base/JZ_resume.pdf`.
Mark REVIEW_READY with blocker `missing_production_resume`.
