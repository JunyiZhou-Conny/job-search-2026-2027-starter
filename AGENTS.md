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
- Apply **weight** is separate: `regular` | `prioritized` (GTC 2026 / startup / prestige).
  See `knowledge/application_priority.yaml`. Prioritized: more Why-us care,
  JD-tuned resume from the evidence bank only, **hold public Submit**
  until referral / insider-page risk is checked. Labels stay suggestions
  until Junyi confirms.

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

## Collaborators

Friends set up a **personal fork** (own Simplify, own Cloud Agents, own ledger).
Do not overwrite the template owner's identity on upstream `main`.
Runbook: `docs/collaborators/SETUP.md`. Kickoff: `docs/collaborators/AGENT_KICKOFF.md`.
Command: `/collaborator-setup`. Reset (fork only): `scripts/init_personal_copy.py`.

## Apply harness (Cloud Agent autofill)

Opening ATS tabs is not enough. Autofill needs Chromium + Simplify Copilot +
a personal session on **this** VM. That harness is not in git and dies with
the pod unless the personal environment was snapshotted after a human login.

Before any 10-tab / autofill run:

```bash
python3 scripts/automation/check_apply_harness.py
```

If it exits 1, stop and follow `docs/automation/APPLY_HARNESS.md`. Do not
treat Greenhouse’s MyGreenhouse button as Simplify. Do not type identity
fields by hand to fake a Copilot pass. Do not Submit.

Copilot “need review” that matches empty form fields is a **gap**, not a
license to invent. Record it in `knowledge/autofill_obstacles.yaml`
(`docs/apply/OBSTACLES.md`). Ask Junyi later. Do not invent GPA, SAT/ACT,
clearance, or citizenship.

In apply notes, **Copilot = Simplify Copilot** (Chrome extension), not
Cursor. The extension does not read this repo. A YAML fact can stay
unused on the form.

If an apply URL is gone (closed, 404, Greenhouse “no longer open”):
close that tab, write `decision=closed` in `data/job_decisions.csv`,
do not pick a sibling from the employer’s current openings.

Free-response drafts (why company, week structure, and similar) go in
`docs/apply/written_answers/`. Answer the prompt on the page. Do not
paste education + three projects into every Why-us. Ideology in
`knowledge/written_response_bank.yaml` is for week / meaning / culture
questions only. A file there is not a submit.

Copilot “Completed” on phone or resume is not proof the widget has a
value. Look at the page. Especially on prioritized companies.

## Automation safety

- `label_source=manual` must not be auto-overwritten.
- Auto labels need confidence + evidence; low confidence → `needs_review` / `generated/label_suggestions.csv`.
- Daily scripts generate files only; never send outreach or submit applications.
- Calendar defaults to dry-run (`generate_calendar.py --write` to emit ICS).
- Knowledge files live under `knowledge/`; do not store sensitive ID documents.
