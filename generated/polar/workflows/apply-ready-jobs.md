# apply-ready-jobs

workflow: apply-ready-jobs
workflow_version: 2026-09-08.learning-loop+6f04552065d9
status: production
enabled: true
needs_browser_lock: true
schedule: 20 * * * * America/New_York
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

At start, read the control row whose key is polar_browser.
If another non-expired production workflow owns it, write run_log result SKIPPED_LOCKED and exit.
If the lock is free or expired, acquire it with this run_id, this workflow, acquired_at now, and expires_at now plus 180 minutes.
If this long run is still active and remaining time is under 60 minutes, refresh expires_at to now plus 180 minutes.
Release the lock on normal completion by clearing owner_run_id.
A crashed run must not lock the browser forever. Treat an expired expires_at as free.

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

## Local identities and documents

street_address_source: local Polar or private profile. Never copy the street value into git or the Sheet.
Normal ATS email, account email, preferred contact, and password-reset email use the local APPLICATION mailbox.
If a field asks for school email, university email, or institutional email, use the local academic mailbox.
A resume parser that pastes Harvard email into a normal contact field is wrong. Correct it before Submit.
Do not create a second employer account only to change email.
Do not write mailbox values or passwords into the Sheet.

Approved documents:
- emory_official_transcript: path `Emory_Official_Transcript.pdf` (available). Use when the form asks for that document class.
- harvard_unofficial_transcript: path `Harvard_unofficial_transcript.pdf` (available). Use when the form asks for that document class.
Do not attach a transcript when the job asks for a different school or a diploma.
If a required transcript is missing locally and in the registry, mark BLOCKED with category MISSING_DOCUMENT.
Never paste transcript contents into logs.

## Priority contract

max_new_jobs: 3
reserved_priority_slots: 1
shared_pool: true
reservation_is_from_pool: true
prioritized_auto_submit: true
writing_log_required_before_priority_submit: true
priority_submit_gate: polar_policy.priority_submit_permitted
max_regular_submissions_per_local_day: 10

Recovery first. Inspect every SUBMISSION_UNKNOWN row. Verify. Never blindly resubmit.
Then resume the oldest IN_PROGRESS row from last_stage.
If READY_PRIORITY exists, reserve 1 new-execution slot for one priority job.
Use remaining new-execution slots for READY_REGULAR.
If no READY_PRIORITY exists, regular may use every configured new-execution slot.
Do not let a READY_REGULAR backlog starve READY_PRIORITY.

## Simplify contract

role: optional_accelerator
max_attempts_per_application: 1
fallback: polar_runtime_plus_local_profile

Try Simplify once when it is already available and useful.
If onboarding, missing injection, a broken session, or repeat navigation appears, stop using it on that job.
Fall back to POLAR_RUNTIME, the approved resume or document registry, and the local Polar profile.
Do not spend the run repairing Simplify.
If Simplify materially slowed the run, write a PERFORMANCE incident with repeat_key simplify_onboarding or simplify_not_injected.

## Apply-time hard eligibility

Before major fill, read the full employer posting.
Re-apply the existing hard rules from POLAR_RUNTIME section C.
Skip when the fuller JD shows a 2026 role or start, employment start before 2027-01-18,
a non-US work location, PhD-only, or an incompatible TS-SCI or polygraph requirement.
Sponsorship unknown or no is not a skip.
An exclusive graduation window remains a note, not a skip.
Do not change graduation-window policy.

## Employer requisition dedupe

After Original Job Post or the employer application is resolved, capture the most stable identity:
employer_requisition_id, canonical employer apply_url, and ats_job_id.
Write those named fields. Keep apply_url_confidence.
Compare against the Sheet and section K.
If another row already points at the same employer requisition, keep one canonical row.
Mark siblings SKIP with blocker duplicate employer requisition and the canonical job_key.
Do not submit the same employer requisition twice.
Do not create a second ledger.

## Work order

Never click Jobright APPLY WITH AUTOFILL.
Never invent facts. If a required fact is missing, leave the widget and mark BLOCKED.
A blocked job must not stall the batch.

For each selected job:
1. Set status IN_PROGRESS and bump attempt_count. Write updated_at now. Read back job_key, status, last_stage.
2. Open apply_url when confidence is exact or strong. Otherwise open source_url and use Original Job Post.
3. Confirm company and title match the queue row. If they do not match, BLOCKED or SKIP.
4. Capture employer identity and run requisition dedupe before extensive fill.
5. Re-check hard eligibility on the full posting before extensive fill.
6. Authenticate with ordinary browser flows when asked. Account creation is normal work.
7. Prefer the Simplify resume already attached. If the widget is empty, upload the compiled base resume. Use Simplify at most once. Then read the visible widgets.
8. Fill standing answers from section A. Correct a resume-parser Harvard email on a normal contact field.
9. Write free-response answers from sections F and I. Prompt-faithful. Evidence-grounded.
10. For every nontrivial free-response question, append one writing_log row with the exact question, the exact answer used, and a short evidence note.
11. Regular row. Validate, Submit once, verify. SUBMITTED or SUBMISSION_UNKNOWN. Do not click Submit a second time.
12. Prioritized row. Deeper JD and company-specific reasoning. Same evidence-bank ceiling. writing_log is mandatory for every meaningful custom question.
    Apply polar_policy.priority_submit_permitted before Submit.
    If any meaningful custom question is unanswered in writing_log, do not Submit. Mark BLOCKED.
    A logged question with a blank answer or a blank evidence_note is a Submit blocker.
    If writing_log is complete and final validation passes, Submit once and verify.
    REVIEW_READY is only for a missing owner fact or an explicit hold. It is not the default for prioritized rows.
13. If this environment cannot complete a required step after a normal attempt, status BLOCKED. Continue.
14. Update the Sheet after every meaningful stage with named writes.

ATS family is only a note.
Do not implement CAPTCHA bypass, fingerprint spoofing, or anti-abuse evasion.
Write the run_log row, including submitted_regular, submitted_priority, simplify_attempted, and simplify_fallback_count.
Release the lock.
