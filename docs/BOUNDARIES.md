# Three operating boundaries

## 1. Labels are suggestions until you confirm

Cursor / scripts may produce:

```text
suggested value + confidence + evidence + needs_review
```

They must **not** silently finalize hard eligibility or overwrite `label_source=manual`.

- Default: write proposals to `generated/label_suggestions.csv` or show in CLI.
- Write to `applications.csv` only after you confirm (`label_job.py --apply` or `confirm_labels.py`).
- Limited auto-write (future): only if confidence ≥ 0.90, no hard-eligibility dispute, no auth dispute, no manual label, clear JD evidence.

## 2. Skills live in the repo, not in the model

Persistent context comes from:

- `config/profile.yaml`
- `knowledge/evidence_bank.yaml`
- `knowledge/target_roles.yaml`
- `knowledge/work_authorization.yaml`
- `.cursor/rules/` + `AGENTS.md`

The model does not remember your skills across chats unless these files are present and loaded.

## 3. Daily discovery runs as a Cursor Automation, from a committed file

`.cursor/rules` and `.cursor/commands` do **not** fire on a timer. The scheduled
run is a **Cursor Automation** ("Daily Job Discovery") on a weekday cron.

- The Automations UI holds only the short pointer in `docs/automation/UI_POINTER.md`.
- The real instructions live in `docs/automation/DAILY_JOB_DISCOVERY.md`; rule changes
  are a git push, not a UI edit.
- The Automation runs in a fresh cloud checkout of `main`. Anything uncommitted is invisible to it,
  including `secrets/` — so personalized Jobright Matches may be unavailable and the public
  board tables carry the run.
- It writes discovery + triage artifacts only. It never submits an application, sends outreach,
  or ingests into `applications.csv` without explicit confirmation in that run.

Local scripts (`scripts/daily_job_search.py` and friends) are run by hand when wanted; no OS
scheduler is wired.

## 4. Credentials never enter chat or git

- Do **not** paste Jobright/Simplify/LinkedIn passwords, 2FA codes, or cookies into Cursor.
- Browser automation uses **local** saved sessions you create (`secrets/`, gitignored).
- See `docs/archive/local-browser-automation.md` for the local session setup.
