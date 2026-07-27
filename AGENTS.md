# Project Instructions

This repository is a job-search **strategy and memory layer**, not a second Simplify tracker.

## Core behavior

- Treat `data/applications.csv`, `data/job_decisions.csv`, and `data/activity_log.csv` as structured records.
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
3. **Scheduled discovery is a Cursor Automation**, driven by `docs/automation/DAILY_JOB_DISCOVERY.md`
   in a fresh cloud checkout of `main`. Rules and commands are not timers, and no OS scheduler is
   wired — uncommitted work is invisible to the run.

## Automation safety

- `label_source=manual` must not be auto-overwritten.
- Auto labels need confidence + evidence; low confidence → `needs_review` / `generated/label_suggestions.csv`.
- Daily scripts generate files only; never send outreach or submit applications.
- Calendar defaults to dry-run (`generate_calendar.py --write` to emit ICS).
- Knowledge files live under `knowledge/`; do not store sensitive ID documents.
