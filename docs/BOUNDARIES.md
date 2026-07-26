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

## 3. Daily auto-run needs an OS scheduler

`.cursor/rules` and `.cursor/commands` do **not** fire on a timer.

- Phase 1: `python3 scripts/daily_job_search.py` via launchd / Task Scheduler / cron (`docs/automation_*.md`)
- Phase 2 (later): Cursor CLI / Background Agents / MCP — still proposal-first, private repo, no secrets

## 4. Credentials never enter chat or git

- Do **not** paste Jobright/Simplify/LinkedIn passwords, 2FA codes, or cookies into Cursor.
- Browser automation experiments use **local** saved sessions you create (`secrets/`, gitignored).
- See `docs/automation-experiment.md` for the safe experiment ladder (A→E).
