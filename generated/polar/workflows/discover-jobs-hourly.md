# discover-jobs-hourly

workflow: discover-jobs-hourly
workflow_version: 2026-09-09.prod-learn+b2681682cb94
status: production
enabled: true
needs_browser_lock: true
schedule: 0 * * * * America/New_York
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

needs_browser_lock: true
lock_key: polar_browser
ttl_minutes: 180
tab: control

At start, locate the control row by the key cell polar_browser. Do not pick a visually empty row.
If another non-expired production workflow owns it, write run_log result SKIPPED_LOCKED and exit.
If the lock is free or expired, acquire it with this run_id, this workflow, acquired_at now, and expires_at now plus 180 minutes.
Immediately upsert a run_log row for this run_id with started_at now and result PARTIAL. Notes may say acquired.
A later crash must still leave that run_log row. Update the same run_id at the end. Do not append a second row for the same run_id.
If this long run is still active and remaining time is under 60 minutes, refresh expires_at to now plus 180 minutes.
After each job stage, refresh control notes with polar_policy.lease_checkpoint_notes(job_key, last_stage).
Release the lock on normal completion by clearing owner_run_id. Keep the checkpoint until then.
A crashed run must not lock the browser forever. Treat an expired expires_at as free.
Do not weaken the lease to recover a crashed run.

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
If the target key is missing, append a new row.
If the visible row has a different key, or no key, abort. Do not write that row.
If two rows share the same key, abort.
Commit the edit. Then reread key, owner_run_id, notes.
A cell that looked correct is not proof the write persisted. The reread is the proof.
github_write_canary must never overwrite polar_browser.
After a canary write, reread polar_browser key, owner_run_id, acquired_at, and expires_at.
Those four cells must still match the values from before the canary write. Notes on that lock may change.
These English rules are what Polar follows. polar_policy helpers are the same decision table for engineers.

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
UI_ONE_OFF, LOCAL_PRIVATE_FACT, MISSING_DOCUMENT, MISSING_FACT, FACT_POLICY, TRIAGE, QUEUE_STATE, DEDUP, WRITING, AUTH, PERFORMANCE, NO_ACTION.
If minutes were lost, also set time_lost_category from:
AUTH, ACCOUNT_CREATION, SIMPLIFY, MISSING_FACT, MISSING_DOCUMENT, WRITING, DROPDOWN_UI, DUPLICATE, SUBMIT_VERIFY, OTHER.
repeat_key groups recurrences. Examples: simplify_onboarding, queue_schema_shift, degree_level_gate_missed_at_discovery.
Degree-level hard gates that discovery missed use that one repeat_key. Do not invent phd_only_missed_at_discovery variants.
incident_id is INC-YYYYMMDD-NNN on today's America/New_York date, three digits.
Read existing incident_id values first. Never reuse one. Do not write INC-YYYYMMDD-01.
If 001 and 003 exist, the next id is 002. 01 and 001 count as the same number.
A missing birth date or OPT-months answer is MISSING_FACT, not MISSING_DOCUMENT.
durable_candidate is yes only when a repo policy or compiler change would prevent a repeat.
Evidence must be enough for an engineer. No secrets.

## Work order

Never apply. Never click Submit. Never click Jobright APPLY WITH AUTOFILL.
Never invent metrics, projects, employers, referrals, citizenship, or clearance.
This run must finish quickly. Checkpoint the Sheet after every new or updated job.

1. Create run_id. Read the control lock. Exit SKIPPED_LOCKED if blocked.
2. Open Jobright while already logged in.
3. Inspect Matches at https://jobright.ai/jobs/recommend.
4. Inspect the intern and newgrad minisite boards listed in POLAR_RUNTIME section B.
5. For each unseen card, write or update one queue row using named header mapping.
6. job_key is the Jobright job id when the URL is https://jobright.ai/jobs/info/<id>.
7. Deduplicate by job_key first, then company + role + location, then section K.
8. Triage with section C. Hard skips become status SKIP.
9. If a section K key matches, do not set READY_REGULAR or READY_PRIORITY.
10. For KEEP rows that pass section K, set READY_REGULAR or READY_PRIORITY using section D.
11. Set resume_cluster from section E.
12. Keep Jobright source_url. last_stage stays discovered.
13. Leave apply_url empty unless you already have a trusted employer URL.
14. Always write apply_url_confidence. Use none when apply_url is empty.
15. Do not open Original Job Post in this Workflow.
16. Never start apply-ready-jobs work in this Workflow.

Stop when the first loaded pages of the configured boards are covered.
Do not infinite-scroll the whole internet.
Write the run_log row. Release the lock.
