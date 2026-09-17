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
| `queue` | KEEP. One row per discovered job. Targeted lookups only. Not apply FIFO. |
| `writing_log` | KEEP. One row per nontrivial free-response answer while `writing_observation_mode` is true. |
| `heartbeat` | KEEP. Locked-screen scheduler proof. Not a job row. |
| `run_log` | KEEP. One row per workflow invocation. `simplify_attempted` / `simplify_fallback_count` are ARCHIVE: leave blank. |
| `incident_log` | KEEP. One row per material event. Fence `pre_jobright` as history, not current reliability. |
| `control` | SIMPLIFY. KEEP `github_write_canary`. ARCHIVE `polar_browser` mutex and `env_simplify_copilot`. Do not delete those rows. |
| `learning_reports` | KEEP. Sanitized daily production-learning Markdown. |

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
| `NEW` | Seen and written. Claimable when Jobright shows the card. |
| `READY_REGULAR` | Historical inventory, regular weight. Not silent apply FIFO. |
| `READY_PRIORITY` | Historical inventory, prioritized writing depth. Not silent apply FIFO. |
| `IN_PROGRESS` | This run owns the job via `claim_run_id`. Different jobs may be `IN_PROGRESS` at the same time. |
| `REVIEW_READY` | Form is complete but Polar stopped for a missing owner fact or explicit hold. |
| `SUBMITTED` | Submit clicked and verification succeeded. |
| `SUBMISSION_UNKNOWN` | Submit may have happened. Verify before any retry. |
| `BLOCKED` | This job cannot finish a required job-specific step. The queue continues. Missing Copilot is not `BLOCKED`. |
| `SKIP` | Hard skip, closed posting, or owner skip. |

## `last_stage` values

`discovered`, `source_resolved`, `application_open`, `authenticated`, `form_filled`, `reviewed`, `submit_clicked`, `confirmation_seen`, `jobright_ack`.

## Recovery

Read targeted Sheet rows. Do not dump every READY_* row. Do not trust a leftover browser tab.

1. Filter `SUBMISSION_UNKNOWN`. Open the employer portal, confirmation page, or application Outlook. Never blindly resubmit.
2. Resume abandoned or self-owned `IN_PROGRESS` rows. Do not steal a live foreign claim.
3. Do not FIFO `READY_*`. New work comes from Jobright recommendations. `legacy_ready_disposition` is `inventory_only`.
4. Lookup `BLOCKED` / `SUBMITTED` / unknown by `job_key` or company+role+location. Jobright can re-surface a blocked card. Skip it.

## Schema-safe writes

Read the live header row. Map field names to columns. Write by name. Write explicit blanks. Never omit `apply_url_confidence`. After an important queue write, read back `job_key`, `status`, `last_stage`, and `claim_run_id`.

## Work claim

If the live queue header has no `claim_run_id`, do not append it from apply or discover. Run `polar-sheet-migration` once. That workflow appends the header at the far right when it is missing and leaves it unchanged when it already exists exactly once.

`job_key` is unique. `plan_queue_upsert_by_job_key` locates every visible row with that key. Zero → append once. One → update that row. Two or more → abort that job, incident `duplicate_job_key`, do not claim, do not Submit.

`apply-ready-jobs` is one worker. Before it upserts `PARTIAL`, it queries `run_log` for every open apply `PARTIAL` (`apply-ready-jobs`, `apply-agent-jobs`, or `grok-apply-jobs`) with blank `ended_at`. Do not filter that QUERY to young `started_at`. `start_apply_run_action` without `this_workflow` classifies: `NO_WORK` when another apply is still live (`started_at` younger than `work_claim.ttl_minutes`); `stale_close` when a crashed PARTIAL is older than that TTL or `started_at` is unparseable. Close the other row with `stale_apply_close_fields`, then Polar upserts this run `PARTIAL` so the mutex stays held. Grok must write its own live `PARTIAL` after `stale_close` too. `grok-production-learning-daily` is not an apply and must not call `start_apply_run_action`. Do not acquire `polar_browser`. Do not create `grok_browser`.

Draft `apply-agent-jobs` may call `start_apply_run_action(..., this_workflow=apply-agent-jobs)`. That path may return `resume` when the live `PARTIAL` is also Polar `apply-agent-jobs`, and it classifies Agent liveness by last Sheet write by that run. It still `NO_WORK`s when `apply-ready-jobs` or Grok is live. It does not change `apply-ready-jobs` `:20` uniqueness. Do not flip live `apply_entry` while that recommend worker is open.

Cheap SKIP is first-class. Card-level or Sheet-memory skips write `SKIP` or leave the existing terminal row without `IN_PROGRESS`, without Generate Resume, without Apply Now, and without opening the employer ATS. Open the employer JD only when the Jobright card cannot decide eligibility.

Recovery uses `select_next_apply_job`. New work is a Jobright card that survived cheap SKIP. It claims that `job_key` by writing `status=IN_PROGRESS` and `claim_run_id=<this run>`, then processes it. A lost claim does not consume the considered budget. Do not write `SKIPPED_LOCKED`. Before Submit, reread `claim_run_id` and rerun `requisition_submit_blocked` on the live sibling rows. If this run lost the claim or is no longer the canonical survivor, do not Submit.

Do not create `scratch_*` tabs. A QUERY that returns `#N/A` or `#REF!` is a lookup miss (`sheet_query_na`), not a license to dump the queue.

Same employer requisition uses `pick_canonical_requisition_row`. Only that survivor continues toward Submit. The other sibling is `SKIP`.

Write `updated_at` with `datetime.isoformat()`. An unreadable `updated_at` on a live `claim_run_id` is not abandoned.

`discover-jobs-hourly` must not overwrite `status`, `claim_run_id`, or other execution fields on `IN_PROGRESS`, `SUBMITTED`, `SUBMISSION_UNKNOWN`, `REVIEW_READY`, or `BLOCKED` rows.

Recover `IN_PROGRESS` only when `claim_run_id` is empty, the owner run_log is no longer `PARTIAL`, or a parseable `updated_at` is older than `work_claim.ttl_minutes`.

`polar_browser` remains on the `control` tab as historical state. Do not acquire it. A stale owner there must not stop discovery or apply.

Claim ids carry an executor prefix. Polar Local mints `R-` and the Grok Bot sibling mints `G-` through `polar_policy.mint_run_id(executor=...)`; `polar_policy.executor_from_run_id` reads it back. Both executors claim through this same `claim_run_id` column, one `job_key` at a time, with the same write-then-readback protocol. Grok writes the same `queue`, `run_log`, `incident_log`, and `writing_log` tabs with `run_log.workflow` `grok-apply-jobs` or `grok-production-learning-daily`. There is no Grok tab, no Grok column, no second Sheet. Grok never touches `control`, `heartbeat`, `learning_reports`, or an `R-` row. A different Jobright surface does not remove collision; the claim does. See `docs/automation/GROKBOT.md`.

If the Mac slept while Job 6 was `IN_PROGRESS` and the claim is abandoned or self-owned, resume Job 6. Do not start over from Job 1.

## Autofill owner

Jobright extension owns autofill on the apply path. Do not click Simplify Copilot Autofill. Missing Copilot does not stop the run. After Autofill, read the form DOM: identity, contact, sponsorship vs future-sponsorship, referral. Trust the form, not the extension sidebar.

`env_simplify_copilot` is ARCHIVE observational state, not an apply gate. Locate control rows by key. Never write these fields into the `polar_browser` row.

## Dedup

Match `job_key` first. If Jobright id is missing, match normalized company + role + location. After the employer application is resolved, also match `employer_requisition_id`, `ats_job_id`, or canonical employer `apply_url`. Keep one canonical row. Mark siblings `SKIP`.

## What the Sheet is not

The Sheet is not the long-term application ledger. Cursor later reconciles verified results into `data/applications.csv` and `data/apply_attempts.csv`. Polar must not invent ledger ids.
