# Resumes

This folder starts fresh with one active resume.

## Active files

- `base/JZ_resume.tex` is the source.
- `base/JZ_resume.pdf` is the compiled two-page master. It is not a Polar attach.
- `base/evidence_bank.md` lists what the base resume may claim.
- `families/swe/swe_v1.tex`, `families/ml_ai/ml_ai_v1.tex`, `families/ai_infra/ai_infra_v1.tex`, and `families/health_ai/health_ai_v1.tex` are the frozen production one-pagers from Resume Stack BUILD. Polar is not wired to them yet. Registry rows stay inactive until an owner activates them. Do not put production Health AI under `resumes/health_ai/`. That path is a deleted cluster directory.
- `Perfect Resume/perfect_resume.tex` is Junyi's supervised gold copy. Do not regenerate it from BUILD.

`role_cluster` and `resume_cluster` stay job taxonomy (`cloud_swe`, `data_ml`, `health_ai`). They are not files here. Do not recreate those folders.

## How Polar attaches a resume

If a resume is already visible on the widget, leave it.

If Polar must upload a file, use `Perfect Resume/perfect_resume.pdf`.
That includes an empty widget, Copilot leaving the widget empty, Copilot
incompatible with the ATS resume control, or uncertainty about which
family file to pick.

Do not upload `base/JZ_resume.pdf`. Do not invent a new resume for every job.
Canonical rule: `knowledge/polar_resume_attach.yaml`.

## Compile

Source-controlled family TeX keeps a sanitized email placeholder. That is
intentional. Do not commit the application mailbox.

```bash
./scripts/compile_resume.sh
./scripts/compile_resume.sh resumes/base/JZ_resume.tex
./scripts/compile_resume.sh resumes/families/swe/swe_v1.tex
python3 scripts/export_resume.py --family swe
```

`export_resume.py` writes the application PDF under `generated/resumes/export/`
using `RESUME_EMAIL` or `SIMPLIFY_EMAIL`. Do not use `HARVARD_EMAIL`. Upload
that export PDF, not the sanitized compile next to the `.tex`.

The page limit for `resumes/base/` is 2. That gate is for the master resume.
It is not a claim that Polar must upload this PDF. The script fails if the PDF
is longer, unless you pass `--allow-overflow`.

Upload the `.pdf` next to the `.tex`. Do not upload the `.tex` to an ATS.

## Historical versions

Applied ledger rows keep the `resume_version` string that was submitted.

Inactive rows stay in `data/resume_versions.csv`. Their files are gone from this folder. Git history still has them.

```bash
git log -- resumes/data_ml/2026-07-20_data-ml_v1.1.pdf
git checkout <sha> -- resumes/data_ml/2026-07-20_data-ml_v1.1.pdf
```

Do not recreate cluster folders or `scripts/build_clusters.py`.
