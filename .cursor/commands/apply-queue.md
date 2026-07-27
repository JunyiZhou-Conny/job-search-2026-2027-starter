# /apply-queue

Build and serve today's apply queue — the one screen used during the daily applying hour.

## Steps

1. Confirm a triage file exists for the date (`generated/discovery_triage_YYYY-MM-DD.csv`).
   If it is missing, say so and offer `/triage-discovery` instead of inventing rows.
2. Start the live server (writes go straight to the repo):

```bash
python3 scripts/serve_apply_queue.py --date YYYY-MM-DD
```

3. Tell the user to open `http://127.0.0.1:8765/` — **not** the static HTML file.
4. Summarize what is in the queue: total, GTC sponsors, Boston/MA, Bay Area, big tech,
   and how many are backlog vs today's keeps.

## What the buttons do

- **Applied** → `status=applied` + `date_applied` + `resume_version` in `data/applications.csv`.
  Creates the application row when the role existed only in the triage CSV.
- **Pass** → `data/job_decisions.csv` + `status=passed`; the role stops resurfacing.
- Neither action submits anything to an employer.

## Static-file fallback

Only if the server cannot run: regenerate the page, let the user click, then import.

```bash
python3 scripts/generate_apply_queue.py --date YYYY-MM-DD
python3 scripts/sync_queue_decisions.py --file ~/Downloads/queue_decisions_YYYY-MM-DD.json
```

## Afterwards

Suggest `python3 scripts/refresh_resume_stats.py` so resume-version conversion stays honest.
Do not ingest, label, or email anything as part of this command.
