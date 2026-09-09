# production-learning-daily

workflow: production-learning-daily
workflow_version: 2026-09-09.direct-maintenance+90bba3a3438b
status: production
enabled: true
needs_browser_lock: false
schedule: 0 22 * * * America/New_York
runtime_url: https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md
COMPILED ARTIFACT. Not canonical.

## Open these files

1. This file. Follow it.
2. https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md

Read both fully before clicking employer pages.
Do not browse the rest of GitHub.

## Secrets ban

Never write passwords, cookies, OTP codes, 2FA secrets, session tokens,
street address values, or transcript contents into the Sheet, email, git, or a report.
Phone and email values stay in the local Polar profile.

## Browser lease

needs_browser_lock: false
This workflow does not take the polar_browser lock.
If apply-ready-jobs or discover-jobs-hourly holds the lock, continue anyway.

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

Omitting apply_url_confidence once shifted status and last_stage into the wrong columns.
Named writes are the fix. Prose that says remember column I is not the fix.

## Run telemetry

One workflow invocation writes one run_log row.
Copy workflow_version from this file into that row.
Record started_at when you acquire work. Record ended_at before you exit.
duration_minutes is coarse. Use whole minutes.
result is SUCCESS, PARTIAL, FAILED, SKIPPED_LOCKED, or NO_WORK.

Write an incident_log row when something material happens.
Use one category from this list:
UI_ONE_OFF, LOCAL_PRIVATE_FACT, MISSING_DOCUMENT, FACT_POLICY, TRIAGE, QUEUE_STATE, DEDUP, WRITING, AUTH, PERFORMANCE, NO_ACTION.
If minutes were lost, also set time_lost_category from:
AUTH, ACCOUNT_CREATION, SIMPLIFY, MISSING_FACT, MISSING_DOCUMENT, WRITING, DROPDOWN_UI, DUPLICATE, SUBMIT_VERIFY, OTHER.
repeat_key groups recurrences. Examples: simplify_onboarding, queue_schema_shift.
durable_candidate is yes only when a repo policy or compiler change would prevent a repeat.
Evidence must be enough for an engineer. No secrets.

## Work order

This workflow does not change GitHub policy.
It does not apply. It does not click Submit.

Read today's America/New_York rows from run_log, incident_log, writing_log, and queue.
Group incidents by repeat_key.
Write one sanitized Markdown report that covers:
- repeated incidents
- one-off UI issues
- local-only facts
- missing documents
- candidate durable policy lessons
- triage problems
- queue or state bugs
- dedupe problems
- writing observations
- performance bottlenecks, using time_lost_category and minutes_lost

Sanitize before you persist. The report must never contain street address, private application email,
phone, OTP, password, cookie, session token, transcript contents, or private auth material.
Replace those with redaction tokens if they appear in source rows.

Write the report into the learning_reports tab with publish_status sheet_only.
If control key github_write_canary is success, you may also publish the same sanitized body
as a GitHub Issue titled [Polar Production] YYYY-MM-DD. Otherwise keep it in the Sheet.
Cursor reads that report directly. Do not wait for ChatGPT.
Do not invent a GitHub write path that has not been proven.
Write the run_log row.
