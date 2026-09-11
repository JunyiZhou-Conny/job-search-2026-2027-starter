# Resumes

This folder starts fresh with one active resume.

## Active files

- `base/JZ_resume.tex` is the source.
- `base/JZ_resume.pdf` is the compiled two-page master. It is not a Polar attach.
- `base/evidence_bank.md` lists what the base resume may claim.
- `families/ai_infra/ai_infra_v1.tex` is the first frozen production one-pager from Resume Stack BUILD. Polar is not wired to it yet.

`role_cluster` and `resume_cluster` stay job taxonomy (`cloud_swe`, `data_ml`, `health_ai`). They are not files here. Do not recreate those folders.

## How Polar attaches a resume

Prefer the Simplify resume already attached.

If the widget is empty, do not upload `resumes/base/JZ_resume.pdf`.
Mark REVIEW_READY with blocker `missing_production_resume` and continue the batch.

Do not invent a new resume for every job.

## Compile

Source-controlled family TeX keeps a sanitized email placeholder. That is
intentional. Do not commit the application mailbox.

```bash
./scripts/compile_resume.sh
./scripts/compile_resume.sh resumes/base/JZ_resume.tex
./scripts/compile_resume.sh resumes/families/ai_infra/ai_infra_v1.tex
python3 scripts/export_resume.py --family ai_infra
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
