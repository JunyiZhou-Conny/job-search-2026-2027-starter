# daily-job-summary

workflow: daily-job-summary
workflow_version: 2026-09-08.learning-loop+422dece0d58a
status: production
enabled: true
needs_browser_lock: false
schedule: 30 21 * * * America/New_York
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

## Work order

Never apply. Never click Submit.
Do not open employer forms unless you need to verify a SUBMISSION_UNKNOWN row already in the digest.

Read today's rows from queue, writing_log, heartbeat, run_log, and incident_log.
Email Junyi one digest for America/New_York today.

The first visible section must be:

PRIORITY APPLICATIONS SUBMITTED TODAY

For each prioritized SUBMITTED row today, include company, role, confirmation,
every meaningful custom question, the exact submitted answer, and the short evidence note.
This is post-submit owner oversight. Do not hide creative answers.

Then include:
- other SUBMITTED rows, with company, role, and confirmation
- REVIEW_READY rows that still need an owner fact
- SUBMISSION_UNKNOWN rows that need owner eyes
- BLOCKED rows and the blocker text
- SKIP or closed rows
- new account or auth friction, without secrets
- writing used, as a short list plus the most important examples
- heartbeat success or failure if a heartbeat row exists today
- SKIPPED_LOCKED runs, if any

Subject line: Polar daily job summary YYYY-MM-DD.
If the Sheet is unreachable, say that in the email and stop.
Write the run_log row.
