# Polar queue schema

This file is the reference for the Polar Local Google Sheet. GitHub stays configuration and audit. The Sheet is runtime checkpoint state.

Do not build a database, Redis, or a second `data/applications.csv`.

Import the header rows from:

- `generated/polar/queue_schema.csv`
- `generated/polar/writing_log_schema.csv`
- `generated/polar/heartbeat_schema.csv`
- `generated/polar/run_log_schema.csv`
- `generated/polar/incident_log_schema.csv`
- `generated/polar/control_schema.csv`
- `generated/polar/learning_reports_schema.csv`

Canonical field lists live in `knowledge/polar_operator.yaml`.

## Tabs

| Tab | Purpose |
|---|---|
| `queue` | One row per discovered job. Recovery reads this tab. |
| `writing_log` | One row per nontrivial free-response answer while `writing_observation_mode` is true. |
| `heartbeat` | Locked-screen scheduler proof. Not a job row. |
| `run_log` | One row per workflow invocation. |
| `incident_log` | One row per material event. No secrets. |
| `control` | Historical `polar_browser` row, GitHub write canary, and `env_simplify_copilot`. |
| `learning_reports` | Sanitized daily production-learning Markdown. |

## `queue` columns

| Column | Meaning |
|---|---|
| `job_key` | Stable id. Prefer the Jobright job id, the last path segment of `https://jobright.ai/jobs/info/<id>`. |
| `discovered_at` | ISO timestamp when Polar first wrote the row. America/New_York or UTC with a `Z`. |
| `company` | Employer name from the listing. |
| `role` | Role title from the listing. |
| `location` | Board location. Leave blank when the board is blank. |
| `track` | `internship_if_eligible` or `new_grad_2027_start`. |
| `source_url` | Where Polar found the row. Usually the Jobright job URL. |
| `apply_url` | Employer application URL when known. May stay empty. |
| `apply_url_confidence` | `exact`, `strong`, `weak`, or `none`. |
| `weight` | `regular` or `prioritized`. |
| `priority_reason` | Short signal list, such as `fde` or `gtc_2026`. Blank on regular rows. |
| `lane` | `core`, `broad`, or `practice`. Suggestion until Junyi confirms. |
| `resume_cluster` | Job taxonomy only. `cloud_swe`, `data_ml`, or `health_ai`. Not a resume file. |
| `status` | One value from the status table below. |
| `last_stage` | Coarse checkpoint. Not a second status machine. |
| `attempt_count` | How many times Polar opened this job for execution. Start at 0. |
| `blocker` | Why the row is `BLOCKED`, or blank. |
| `writing_summary` | Short note of free-response work. Full text lives in `writing_log`. |
| `submitted_at` | When Submit was clicked, or blank. |
| `confirmation` | Banner text, application id, or `unknown`. |
| `updated_at` | Last Sheet write for this row. |
| `employer_requisition_id` | Employer requisition id when known. Blank until apply-ready-jobs resolves it. |
| `ats_job_id` | ATS job id when known. Blank until apply-ready-jobs resolves it. |
| `claim_run_id` | The apply run that currently owns an `IN_PROGRESS` row. Blank when the row is not claimed. |

## Status values

| Status | Meaning |
|---|---|
| `NEW` | Seen and written. Not yet READY. |
| `READY_REGULAR` | Keep, regular weight, eligible to execute. |
| `READY_PRIORITY` | Keep, prioritized weight, eligible to execute with deeper writing. |
| `IN_PROGRESS` | This run owns the job via `claim_run_id`. Different jobs may be `IN_PROGRESS` at the same time. |
| `REVIEW_READY` | Form is complete but Polar stopped for a missing owner fact or explicit hold. |
| `SUBMITTED` | Submit clicked and verification succeeded. |
| `SUBMISSION_UNKNOWN` | Submit may have happened. Verify before any retry. |
| `BLOCKED` | This job cannot finish a required job-specific step. The queue continues. Missing Copilot is not `BLOCKED`. |
| `SKIP` | Hard skip, closed posting, or owner skip. |

## `last_stage` values

`discovered`, `source_resolved`, `application_open`, `authenticated`, `form_filled`, `reviewed`, `submit_clicked`, `confirmation_seen`.

## Recovery

Read the Sheet. Do not trust a leftover browser tab.

1. Inspect every `SUBMISSION_UNKNOWN` row. Open the employer portal, confirmation page, or mail. Never blindly resubmit.
2. Resume abandoned or self-owned `IN_PROGRESS` rows. Do not steal a live foreign claim.
3. If `READY_PRIORITY` exists, reserve one new-execution slot for it.
4. Use remaining new-execution slots for `READY_REGULAR`.

## Schema-safe writes

Read the live header row. Map field names to columns. Write by name. Write explicit blanks. Never omit `apply_url_confidence`. After an important queue write, read back `job_key`, `status`, `last_stage`, and `claim_run_id`.

## Work claim

If the live queue header has no `claim_run_id`, do not append it from apply or discover. Run `polar-sheet-migration` once. That workflow appends the header at the far right when it is missing and leaves it unchanged when it already exists exactly once.

`apply-ready-jobs` is one worker. It selects the next job, claims that `job_key` by writing `status=IN_PROGRESS` and `claim_run_id=<this run>`, then processes it. A lost claim does not consume the per-run budget. The worker then selects another READY job. Do not write `SKIPPED_LOCKED`. Before Submit, reread `claim_run_id` and rerun `requisition_submit_blocked` on the live sibling rows. If this run lost the claim or is no longer the canonical survivor, do not Submit.

Same employer requisition uses `pick_canonical_requisition_row`. Only that survivor continues toward Submit. The other sibling is `SKIP`.

Write `updated_at` with `datetime.isoformat()`. An unreadable `updated_at` on a live `claim_run_id` is not abandoned.

`discover-jobs-hourly` must not overwrite `status`, `claim_run_id`, or other execution fields on `IN_PROGRESS`, `SUBMITTED`, `SUBMISSION_UNKNOWN`, `REVIEW_READY`, or `BLOCKED` rows.

Recover `IN_PROGRESS` only when `claim_run_id` is empty, the owner run_log is no longer `PARTIAL`, or a parseable `updated_at` is older than `work_claim.ttl_minutes`.

`polar_browser` remains on the `control` tab as historical state. Do not acquire it. A stale owner there must not stop discovery or apply.

If the Mac slept while Job 6 was `IN_PROGRESS` and the claim is abandoned or self-owned, resume Job 6. Do not start over from Job 1.

## Environment Copilot row

`apply-ready-jobs` upserts the control key `env_simplify_copilot` after it checks the employer page.

This row is not a lease. Leave `expires_at` empty. Locate the row by key. Never write these fields into the `polar_browser` row.

States are `PRESENT`, `MISSING`, and `UNKNOWN`. `MISSING` or `UNKNOWN` stops the apply run. It does not mark the queue job `BLOCKED`. Restore the job to its prior `READY_REGULAR` or `READY_PRIORITY` status. Clear `claim_run_id`. Write `run_log` result `OWNER_ACTION_REQUIRED`. The next apply run checks the employer page again.

## Dedup

Match `job_key` first. If Jobright id is missing, match normalized company + role + location. After Original Job Post is resolved, also match `employer_requisition_id`, `ats_job_id`, or canonical employer `apply_url`. Keep one canonical row. Mark siblings `SKIP`.

## What the Sheet is not

The Sheet is not the long-term application ledger. Cursor later reconciles verified results into `data/applications.csv` and `data/apply_attempts.csv`. Polar must not invent ledger ids.
