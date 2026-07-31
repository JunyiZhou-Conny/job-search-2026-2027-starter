# /apply-queue

Build and serve today's apply queue — the one screen used during the daily applying hour.

## Steps

1. Confirm a triage file exists for the date (`generated/discovery_triage_YYYY-MM-DD.csv`).
   If it is missing, say so and offer `/triage-discovery` instead of inventing rows.
   The server falls back to the newest available date and prints which one it used.
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
- **Undo** (toast, or `U`) → reverses the last Applied/Pass for that role. An undo journal
  (`data/queue_undo_journal.json`, gitignored) snapshots every field the click touched, so the
  row is restored exactly — and a row the queue itself created is removed rather than left
  behind as a phantom `discovered` role.
- Neither action submits anything to an employer.

## Interaction

- **Swipe right** = Applied · **swipe left** = Pass. Both are undoable for 8 seconds.
- Keys: `J`/`K` move · `O` open · `A` applied · `P` pass · `U` undo · `?` shortcuts.
- The date switcher at the top loads any day that has a triage CSV.
- The page listens on `/api/events`; if a CSV changes on disk (another tab, another script,
  a `git pull`) the queue re-reads state within about a second.

## Where the code lives

| Path | Role |
|---|---|
| `scripts/generate_apply_queue.py` | collects + classifies items, renders from the template |
| `scripts/serve_apply_queue.py` | HTTP layer: page, static assets, JSON API, SSE |
| `scripts/queue_writeback.py` | the only place a click becomes repo state |
| `scripts/queue_watch.py` | mtime fingerprint behind the SSE stream |
| `templates/apply_queue/index.html` | markup |
| `static/apply_queue/{styles.css,app.js,spring.js}` | visual system, behaviour, motion |

Do not put HTML back into Python strings — that is what this layout exists to prevent.

## Static-file fallback

Only if the server cannot run: regenerate the page, let the user click, then import.
The generated file inlines its CSS/JS so it still works over `file://`.

```bash
python3 scripts/generate_apply_queue.py --date YYYY-MM-DD
python3 scripts/sync_queue_decisions.py --file ~/Downloads/queue_decisions_YYYY-MM-DD.json
```

## Tests

```bash
python3 tests/test_queue_api.py
```

## Afterwards

Suggest `python3 scripts/refresh_resume_stats.py` so resume-version conversion stays honest.
Do not ingest, label, or email anything as part of this command.
