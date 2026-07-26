# Project Instructions

This repository is a job-search **strategy and memory layer**, not a second Simplify tracker.

## Core behavior

- Treat `data/applications.csv`, `data/networking.csv`, and `data/activity_log.csv` as structured records.
- Never invent application status, recruiter responses, sponsorship facts, graduation eligibility, dates, metrics, or referral outcomes.
- Distinguish verified facts from inference and unknowns.
- Preserve existing IDs and append history rather than rewriting it.
- Every active record should have one concrete `next_action` and, where useful, a `next_action_date`.
- Prefer a few role-cluster resumes plus targeted bullet edits over creating a completely new resume for every job.
- Do not submit an application, send a message, or claim an action was completed unless the user explicitly confirms it.

## Eligibility and sponsorship

- Hard eligibility ≠ sponsorship probability. See `docs/eligibility.md`.
- Never mark a role `ineligible` only because sponsorship is `no` or `unclear`.
- Use `pursuit_lane`: `core` | `broad` | `practice`.
- Keep practice-lane applications roughly 15–25% of applied volume unless funnel data justifies a change.

## Platforms

- Discovery: Jobright / LinkedIn / Handshake / career pages.
- Base ledger: Simplify.
- Local repo: resume version, lane, sponsorship signal, auth Q&A, networking, interview learning, next actions.
- Prefer one-way `import-simplify` over retyping every application. See `docs/platforms.md`.

## Three boundaries (see `docs/BOUNDARIES.md`)

1. **Labels are suggestions** until the user confirms (`confirm_labels.py` / `label_job.py --apply`).
2. **Skills live in the repo** (`knowledge/evidence_bank.yaml` + profile) — not in chat memory.
3. **Daily auto-run needs an OS scheduler** (`docs/automation_*.md`); rules/commands are not timers.

## Automation safety

- `label_source=manual` must not be auto-overwritten.
- Auto labels need confidence + evidence; low confidence → `needs_review` / `generated/label_suggestions.csv`.
- Daily scripts generate files only; never send outreach or submit applications.
- Calendar defaults to dry-run (`generate_calendar.py --write` to emit ICS).
- Knowledge files live under `knowledge/`; do not store sensitive ID documents.

## Cursor Cloud specific instructions

- Runtime is system Python 3 (3.12 present). The **core** pipeline uses only the standard library — no venv, build step, or install is needed to run scripts, tests, or the CLI. Run scripts directly, e.g. `python3 scripts/daily_job_search.py`, `python3 scripts/validate_data.py`, `python3 scripts/jobsearch.py dashboard`. Standard commands are in `README.md`.
- Tests: `python3 -m unittest tests/test_core.py` (stdlib only, no fixtures needed). There is no configured linter or git hook; `python3 -m py_compile scripts/*.py scripts/automation/*.py tests/*.py` is a quick syntax sanity check.
- Running the pipeline/CLI **mutates tracked files**: `data/applications.csv`, `data/activity_log.csv` (appended), and `generated/*` (dashboards, daily/outreach plans). `migrate_schema.py` also writes `data/backups/` and `data/discovery/*.csv` (both gitignored). After ad-hoc/test runs, `git checkout -- data/ generated/` before committing so test data isn't committed.
- `validate_data.py` prints data-quality `error`/`warn` lines but exits 0 — that is expected repo data noise, not a setup failure.
- `daily_job_search.py` reports `max_exit=1` when the optional automation discovery step can't run; the core pipeline still completes. Inspect the per-run log at `generated/logs/daily_*.log`.
- Automation tier (`scripts/automation/*`) is **optional**: `requirements-automation.txt` (playwright + python-dotenv) is installed by the startup update script, but browsers are not — run `python3 -m playwright install chromium` first. It also needs `secrets/.env` (copy from `secrets/.env.example`) and saved session JSON to log into Simplify/Jobright. The public Jobright feed (`export_jobright_discovery.py`) works without credentials.
