# Project Instructions

This repository is a job-search **strategy and memory layer**, not a second Simplify tracker.

## Core behavior

- Treat `data/applications.csv`, `data/job_decisions.csv`, and `data/activity_log.csv` as structured records.
- Never invent application status, recruiter responses, sponsorship facts, graduation eligibility, dates, metrics, or referral outcomes.
- Distinguish verified facts from inference and unknowns.
- Preserve existing IDs and append history rather than rewriting it.
- Every active record should have one concrete `next_action` and, where useful, a `next_action_date`.
- Prefer the approved base resume plus targeted bullet edits over creating a completely new resume for every job.
- Submit is governed by `docs/policy/SUBMIT_ROLLOUT.md`. Regular rows may be submitted autonomously once that ATS gate is open. Polar Local may also Submit prioritized rows after mandatory writing_log. Cursor Cloud prioritized rows still stop for a review packet. Never send a message on Junyi's behalf or claim an action was completed without evidence.

## Eligibility and sponsorship

- Hard eligibility ≠ sponsorship probability. See `docs/eligibility.md`.
- Never mark a role `ineligible` only because sponsorship is `no` or `unclear`.
- Do not self-reject on sponsorship, F-1, OPT, or a company that
  generally does not sponsor. Those are not discovery skips.
  Answer only the asked semantic from `knowledge/work_authorization.yaml`.
  Required future-sponsorship widget: **Yes** (`future_sponsorship_required`).
  Required H-1B-named widget: **No**. Required citizenship: **China**.
  Required visa type: **F-1**. Required any-employer authorization:
  **Yes**. Required currently-authorized: unknown, so BLOCK that job
  only. Optional identity/status fields: leave blank. Unasked
  immigration facts: do not disclose. Ambiguous required widgets:
  BLOCK that job only and continue the batch.
  Re-read these widgets after every autofill (Copilot set United
  States once). The fact `future_sponsorship_required: true` is
  unchanged.
- Graduation **date** widgets: **2026-12-18**. Year-only widgets: **2027**.
- Non-US work location (Belgrade, etc.) → skip. Do not Submit.
- Use `pursuit_lane`: `core` | `broad` | `practice`.
- Keep practice-lane applications roughly 15–25% of applied volume unless funnel data justifies a change.
- Apply **weight** is separate: `regular` | `prioritized` (GTC 2026 / startup / prestige / **FDE**).
  See `knowledge/application_priority.yaml` and `knowledge/role_families.yaml`.
  Forward Deployed / FDE titles → keep and mark. Polar may assign
  READY_PRIORITY when a strong configured signal is present (fde,
  gtc_2026, confirmed_prioritized, clear fortune_500_or_major, clear
  biotech_health_ai). Junyi does not confirm every priority label
  before the queue can move. Priority controls execution effort,
  writing depth, and post-submit writing audit. It is not permission to
  invent company facts. Weak signals (startup / prestige hints,
  personal_fit, generic data titles) stay regular unless clearly
  justified. Prioritized: more Why-us
  care, JD-tuned resume from the evidence bank only, full form prep,
  mandatory writing_log, then Polar Local may Submit
  (`docs/policy/SUBMIT_ROLLOUT.md`).
  Do not wait for a referral / insider page on regular rows (Junyi
  2026-08-24: those pages are rare; FIFO in the queue matters more).
  Do not claim FDE customer-on-site work already done.
- ITAR / EAR / U.S. Person / export compliance (rocket, defense): keep in
  discovery. Do not filter out. Care is low. No need to submit. Form
  answer: I am not a U.S. Person. Do not rewrite Why-us for this family.

## Platforms

- Discovery: Jobright, LinkedIn, Handshake, career pages. Polar Local is
  the production discovery operator on the Mac. Cursor Cloud discovery
  stays as shadow and fallback. See `docs/automation/POLAR.md`.
- Base ledger: Simplify. Polar runtime state lives in the Google Sheet,
  not a second `applications.csv`.
- Local repo: resume version, lane, sponsorship signal, auth Q&A, networking, interview learning, next actions.
- Browser execution has two environments. Cursor cloud Computer Use, and Polar on Junyi's machine. Polar reads `generated/polar/runtime/POLAR_RUNTIME.md`. Prefer a trusted `apply_url`. If the source is still Jobright, Polar uses **Original Job Post**, never **APPLY WITH AUTOFILL**. Polar apply requires visible Simplify Copilot on the employer ATS page. A simplify.jobs login is not proof. If Copilot is missing, Polar stops the apply run for owner action, keeps the queue job READY, and clears the job claim. Polar must not fall back to manual clicking. Pending PREFERENCES candidates keep a `pref_YYYYMMDD_NNN` id until a resolution row is on `main`.
- Prefer one-way `import-simplify` over retyping every application. See `docs/platforms.md`.

## Boundaries (see `docs/BOUNDARIES.md`)

1. **Labels are suggestions** until the user confirms (`confirm_labels.py` / `label_job.py --apply`).
2. **Skills live in the repo** (`knowledge/evidence_bank.yaml` + profile) — not in chat memory.
3. **Cloud scheduled discovery is a Cursor Automation**, driven by
   `docs/automation/DAILY_JOB_DISCOVERY.md` in a fresh checkout of
   `main`. Polar Local runs its own hourly Workflow. Cloud stays shadow
   during migration. Uncommitted work is invisible to the Cloud run.
4. **Credentials stay out of git and chat.** Polar sessions stay on Junyi's computer.
5. **Polar is the local production operator.** GitHub stays memory.
   Cursor stays engineer and Cloud-discovery fallback. Polar does
   hourly local discovery and application execution. See
   `docs/automation/POLAR.md`. Cloud discovery stays as shadow during
   the first 48 hours of Polar hourly discovery.

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
fields by hand to fake a Copilot pass. Submit only within an open gate of
`docs/policy/SUBMIT_ROLLOUT.md`.

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
paste education + three projects into every Why-us. Match ability to
the role; do not dump a DL tour onto a non-ML Why-us. Do not use em
dashes or hyphen asides in the text that goes on the form. Write like
a person. Ideology in `knowledge/written_response_bank.yaml` is for
week / meaning / culture questions only. A file there is not a submit.

Copilot “Completed” on phone or resume is not proof the widget has a
value. Look at the page. Especially on prioritized companies.

Computer Use is hands only. The parent compiles an action sheet through
`scripts/compile_cu_task.py` and `docs/automation/COMPUTER_USE_PROMPT.md`.
Do not spawn a clicker to rediscover, audit, or pretty-screenshot a form
you already understand. Leftover Why-us paste is still one execute/paste
spawn. See `knowledge/form_strategy.yaml` `leftover_typing_one_pass`.

## Automation safety

- `label_source=manual` must not be auto-overwritten.
- Auto labels need confidence + evidence; low confidence → `needs_review` / `generated/label_suggestions.csv`.
- Daily scripts generate files only; never send outreach or submit applications.
- Calendar defaults to dry-run (`generate_calendar.py --write` to emit ICS).
- Knowledge files live under `knowledge/`; do not store sensitive ID documents.
