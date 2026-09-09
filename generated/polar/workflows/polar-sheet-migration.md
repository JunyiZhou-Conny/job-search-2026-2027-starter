# polar-sheet-migration

workflow: polar-sheet-migration
workflow_version: 2026-09-09.prod-learn+861a01032a6c
status: manual_once
enabled: false
needs_browser_lock: false
schedule: manual America/New_York
runtime_url: https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md
COMPILED ARTIFACT. Not canonical.

## Secrets ban

Never write passwords, cookies, OTP codes, 2FA secrets, session tokens,
street address values, or transcript contents into the Sheet, email, git, or a report.
Phone and email values stay in the local Polar profile.

## Sheet write contract

mode: named_header_mapping
required_readback: job_key, status, last_stage
blank_policy: write_explicit_blank
never_omit: apply_url_confidence

1. Read the actual header row of the tab you are writing.
2. Build a field-name to column mapping from those headers.
3. Write fields by header name, not by remembered position.
4. If a value is empty, still write an explicit blank in that named column.
5. Do not shorten a row and shift later fields left.
6. After an important queue write, read back job_key, status, and last_stage.
7. If those three fields do not match what you meant, repair the row before the next job.

Control tab writes are key upserts.
Locate the row by the key cell. Never choose a row because it looks empty on screen.
If the target key is missing, append a new row. If the visible row has a different key, abort.
Commit the edit. Then reread key, owner_run_id, notes.
A cell that looked correct is not proof the write persisted. The reread is the proof.
github_write_canary must never overwrite polar_browser.
Use polar_policy.plan_control_write and polar_policy.control_write_persisted.

Omitting apply_url_confidence once shifted status and last_stage into the wrong columns.
Named writes are the fix. Prose that says remember column I is not the fix.

## Work order

This is a one-time setup. Do not schedule it.
Open the existing Polar Jobs Google Sheet.
Preserve every current queue, writing_log, and heartbeat row.
Do not rewrite existing cells except to add missing headers.

Create a tab only when it is missing. The required tabs and exact headers are:

- queue: job_key, discovered_at, company, role, location, track, source_url, apply_url, apply_url_confidence, weight, priority_reason, lane, resume_cluster, status, last_stage, attempt_count, blocker, writing_summary, submitted_at, confirmation, updated_at, employer_requisition_id, ats_job_id
- writing_log: job_key, company, role, weight, exact_question, answer_used, evidence_note, recorded_at
- heartbeat: recorded_at, workflow, result, page_opened, notes
- run_log: run_id, workflow, workflow_version, started_at, ended_at, duration_minutes, result, lock_result, jobs_seen, jobs_attempted, submitted_regular, submitted_priority, blocked, skipped, submission_unknown, simplify_attempted, simplify_fallback_count, notes
- incident_log: incident_id, run_id, job_key, company, stage, category, time_lost_category, severity, summary, evidence, minutes_lost, resolved_in_run, repeat_key, durable_candidate, recorded_at
- control: key, owner_run_id, workflow, acquired_at, expires_at, notes
- learning_reports: report_date, recorded_at, workflow_version, body_markdown, publish_status, github_url, notes

If queue already has rows, keep them.
If queue is missing employer_requisition_id or ats_job_id, append those headers at the far right.
Do not insert a column in the middle of existing queue data.
If apply_url_confidence is missing from the live header, stop and tell Junyi. Do not guess positions.

Seed one control row with key polar_browser and empty owner_run_id.
Do not invent old run_log or incident_log history.

Verify by reading each header row and comparing it to the lists above.
Write run_log result SUCCESS with notes sheet_migration_ok when verification passes.
