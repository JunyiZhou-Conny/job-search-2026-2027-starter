# /today-ops

Run today's job-search operations with the three boundaries:

1. Labels are suggestions until confirmed.
2. Skills come only from repo knowledge files.
3. This command does not schedule itself — the user triggers it. Scheduled discovery is a separate Cursor Automation (`docs/automation/DAILY_JOB_DISCOVERY.md`).

## Steps

1. Read `config/profile.yaml`, `knowledge/*`, applications/contacts/networking, latest Simplify import if any.
2. Run `python3 scripts/validate_data.py` and summarize `generated/review_queue.csv`.
3. Run `python3 scripts/confirm_labels.py --batch` and list high-priority rows needing confirmation (do not `--commit` unless user asks).
4. Run `python3 scripts/daily_job_search.py` (calendar dry-run).
5. Present:
   - hard deadlines next 48h
   - 3–5 application recommendations (lane, resume version, tailoring, minutes) — never auto-exclude for sponsorship
   - 2–3 outreach targets from `generated/outreach/YYYY-MM-DD.md` (do not send)
   - due follow-ups
   - one interview prep module
   - data gaps (missing resume_version / next_action / duplicates)
   - calendar proposal only
6. Distinguish fact / inference / recommendation. Do not invent skills or statuses.
