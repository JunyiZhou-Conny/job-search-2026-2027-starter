# Job Search 2026–2027 Operating System

Local strategy layer on top of Simplify / discovery tools.  
**Audit:** `docs/AUDIT_PHASE0.md` · **Migration:** `docs/MIGRATION.md` · **Delivery:** `docs/DELIVERY.md`

## Daily loop

```bash
# After applying via Simplify, drop export here:
# data/imports/simplify/YYYY-MM-DD.csv

python3 scripts/daily_job_search.py
```

Then open:

- `generated/daily/YYYY-MM-DD.md`
- `generated/outreach/YYYY-MM-DD.md`
- `generated/dashboard.md`
- `generated/analytics/dashboard.md`

## Core commands

```bash
python3 scripts/migrate_schema.py
python3 scripts/validate_data.py
python3 scripts/dedupe_applications.py
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/label_job.py --job-id J... --jd-text "..."
python3 scripts/label_job.py --job-id J... --jd-text "..." --apply   # after you confirm
python3 scripts/generate_calendar.py          # dry-run
python3 scripts/generate_calendar.py --write
python3 -m unittest tests/test_core.py
./scripts/compile_resume.sh
```

## Resumes (do not dilute base)

- Quality baseline: `resumes/base/JZ_resume.tex`
- Active clusters: `*_v1.1.pdf` under `cloud_swe` / `data_ml` / `health_ai`
- Versions registry: `data/resume_versions.csv`

## Rules

- Sponsorship ≠ hard eligibility
- Manual labels (`label_source=manual`) are not auto-overwritten
- No auto-send of applications, LinkedIn, email, or calendar events without confirmation
- No sensitive ID documents or passwords in the repo

## Cursor commands

See `.cursor/commands/` (`daily-plan`, `sync-simplify`, `label-job`, `validate-data`, `audit-system`).
