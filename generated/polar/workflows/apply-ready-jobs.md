# apply-ready-jobs

workflow: apply-ready-jobs
workflow_version: 2026-09-10.pref-reconcile+77699f609893
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

## Preferences reconcile

After POLAR_RUNTIME is open, reconcile /home/polar/PREFERENCES.md against section P preference_resolutions.
Those rows come from main. An open Cursor PR is not canonical.
Match candidate_id only. Do not compare wording.
Remove a pending id whose main outcome is DROP_ONE_OFF, DROP_REDUNDANT, PROMOTE, STALE.
Move KEEP_LOCAL out of pending into Local-only facts as a keep_local line.
Keep NEEDS_MORE_EVIDENCE, OWNER_DECISION pending, and keep any id with no main row.
Keep LOCAL_PRIVATE values. Do not emit keep_local ids in Preferences Delta.
Allocate a new pref_YYYYMMDD_NNN from pending ids, keep_local ids, and section P resolution ids.
Use max(used numbers for that date) + 1. Never fill gaps. Never reuse an id.
If there are no pending ids or no new main rows, write nothing.
The rewrite is idempotent. Do not create a preferences-cleanup workflow.

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
github_write_canary and env_simplify_copilot must never overwrite polar_browser.
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
result is SUCCESS, PARTIAL, FAILED, SKIPPED_LOCKED, NO_WORK, OWNER_ACTION_REQUIRED.

Write an incident_log row when something material happens.
Use one category from this list:
UI_ONE_OFF, LOCAL_PRIVATE_FACT, MISSING_DOCUMENT, MISSING_FACT, FACT_POLICY, TRIAGE, QUEUE_STATE, DEDUP, WRITING, AUTH, PERFORMANCE, ENVIRONMENT, NO_ACTION.
If minutes were lost, also set time_lost_category from:
AUTH, ACCOUNT_CREATION, SIMPLIFY, MISSING_FACT, MISSING_DOCUMENT, WRITING, DROPDOWN_UI, DUPLICATE, SUBMIT_VERIFY, OTHER.
repeat_key groups recurrences. Examples: simplify_onboarding, queue_schema_shift, degree_level_gate_missed_at_discovery.
Degree-level hard gates that discovery missed use that one repeat_key. Do not invent phd_only_missed_at_discovery variants.
incident_id is INC-YYYYMMDD-NNN on today's America/New_York date, three digits.
The sequence is monotonic. Read existing values for that date. The next id is one more than the highest number.
If 001 and 003 exist, write 004. Do not fill gaps. Never reuse one. Do not write INC-YYYYMMDD-01.
01 and 001 count as the same number.
A missing birth date or OPT-months answer is MISSING_FACT, not MISSING_DOCUMENT.
For authorization widgets, record auth_outcome as answered, optional_left_blank, ambiguous_required_blocked, hard_eligibility_skip, or disclosure_prevented.
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

role: required_precondition
proof: employer_page_copilot_ui
not_proof: simplify.jobs login, simplify.jobs API
max_attempts_per_application: 1
silent_manual_fallback: false
missing_action: owner_action_required
consume_job: false
control_key: env_simplify_copilot
states: PRESENT, MISSING, UNKNOWN

Simplify Copilot is required before substantial application fill.
Proof is the Copilot sidebar or Autofill This Page, Start Application, or Create Account & Autofill on the employer ATS page.
A healthy simplify.jobs session is not proof.
If Copilot is PRESENT, click Autofill This Page or Start Application once. Never Run Autofill Again. Never Generate with AI.
Then read the visible widgets and correct standing answers.
If Copilot is MISSING or UNKNOWN, do not fall back to traditional clicking.
This is an ENVIRONMENT blocker, not a job qualification failure.
Restore the probe job to its prior READY_REGULAR or READY_PRIORITY status.
Do not bump attempt_count for the miss. Do not mark the job BLOCKED.
Upsert control key env_simplify_copilot by key cell. Never write it into the polar_browser row.
notes use state=PRESENT|MISSING|UNKNOWN; evidence=short page proof. No secrets.
If a human is in this conversation, ask them once to install Simplify Copilot and recheck after they say it is installed.
Do not hold polar_browser while waiting through later hours.
On a scheduled unattended run, do not wait.
Write incident category ENVIRONMENT, time_lost_category SIMPLIFY, repeat_key simplify_copilot_missing.
job_key on that incident may name the probe page. The queue row stays READY.
Write run_log result OWNER_ACTION_REQUIRED. simplify_fallback_count stays 0.
Release the polar_browser lease. Exit the apply run. Do not start the next READY job.
The next apply-ready-jobs run rechecks Copilot on an employer page. Last MISSING is not a skip-check cache.
When Copilot is PRESENT, overwrite env_simplify_copilot to state=PRESENT and continue.

## Memory ownership

canonical: github
local_inbox: /home/polar/PREFERENCES.md
local_inbox_is_not_strategy: true
precedence: owner_instruction > canonical_github > local_private > learning_candidate
preference_classes: CANONICAL_GITHUB, LOCAL_PRIVATE, LEARNING_CANDIDATE, REDUNDANT, EPHEMERAL, SECRET_OR_CREDENTIAL, STALE, ONE_OFF

GitHub owns durable behavior, policy, and safe facts.
PREFERENCES.md is a thin local inbox. It is not a second strategy database.
Do not copy POLAR_RUNTIME or form strategy into PREFERENCES.
An old PREFERENCES strategy line must not override newer GitHub behavior.
LOCAL_PRIVATE values may stay local. SECRET_OR_CREDENTIAL must not be promoted.
If a local learning candidate conflicts with GitHub strategy, follow GitHub and report the conflict.
Export assigns or preserves pref_YYYYMMDD_NNN ids. Reconcile only after a resolution row is on main.

## Apply-time hard eligibility

Immediately after the employer JD is readable, before login, account creation, or form fill,
skip PhD-only and undergraduate-only gates.
Skip phrases include phd only, phd students only, phd candidates only, doctoral students only,
must be pursuing a phd, must be enrolled in a phd, undergraduate students only,
undergraduates only, and must be an undergraduate.
Do not skip PhD preferred, PhD and Master's, or a sentence that says the role is not PhD only.
Do not skip a line that only says the student must be enrolled in a degree.
Master's study is not PhD and is not undergraduate-only.
If the posting matches a skip phrase, status SKIP. Do not authenticate. Do not fill.
Incident repeat_key is degree_level_gate_missed_at_discovery. Category TRIAGE.
Also skip a 2026 role or start, employment start before 2027-01-18,
a non-US work location, or an incompatible TS-SCI or polygraph requirement.
If the page is an HTTP 404, says page not found, no longer open, no longer accepting,
or that this job or requisition has been removed or closed, SKIP.
A job id that contains the digits 404 is not a closed page. Barriers removed is not a closed page.
Close the tab. Do not open a sibling requisition.
Sponsorship unknown, unavailable, or generally not offered is not a skip.
F-1 or OPT mentioned on a board is not a skip.
An exclusive graduation window remains a note, not a skip.
Do not change graduation-window policy.
Do not move Original Job Post resolution into hourly discovery.

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
1. Remember the current READY_REGULAR or READY_PRIORITY status and attempt_count.
   Set status IN_PROGRESS and bump attempt_count. Write updated_at now. Read back job_key, status, last_stage.
2. Open apply_url when confidence is exact or strong. Otherwise open source_url and use Original Job Post.
3. Confirm company and title match the queue row. If they do not match, BLOCKED or SKIP.
4. If the posting is closed or 404, SKIP. Do not pick a sibling from the employer's current openings.
5. Read the full employer JD now. Run the apply-time hard eligibility check before login or form work.
6. Capture employer identity and run requisition dedupe. Then continue only if the job is still eligible.
7. Copilot preflight on this employer ATS page before substantial fill.
   If Copilot is MISSING or UNKNOWN, restore the remembered READY status and attempt_count.
   Persist env_simplify_copilot. Write OWNER_ACTION_REQUIRED. Release the lease. Exit the run.
8. Authenticate with ordinary browser flows when asked. Account creation is normal work.
9. Attach the resume_cluster from the row. If Copilot is PRESENT, Autofill once. Then read the visible widgets.
10. Fill standing answers from section A. Correct a resume-parser Harvard email on a normal contact field.
   Authorization and identity widgets use polar_policy.auth_form_action.
   Classify the exact question. Answer only that semantic. Do not copy one fact into another field.
   If the field is optional, leave it blank. Do not volunteer F-1, OPT, EAD, citizenship, or sponsorship.
   Required future-sponsorship widget: Yes. Required H-1B-named widget: No.
   Required citizenship: China. Required visa type: F-1. Required eligible-to-begin: Yes.
   Required authorized-for-any-employer: Yes. Required EAD: No. Required OPT approval: No. Required OPT eligibility: Yes.
   Required currently-authorized or sponsorship-to-begin: leave the field and mark BLOCKED on this job only when that fact is unknown.
   If the form names F-1, J-1, or M-1 and clearly says answer Yes or answer No, follow that polarity.
   If it says select Yes or No, or uses not or never with Yes, leave the field and mark BLOCKED on this job only.
   Country-only lists and work-authorization-without-sponsorship wording: blank if optional, BLOCKED if required.
   After autofill, correct invented citizenship, copied sponsorship answers, unasked F-1, or extra explanation.
   Do not mention immigration in Why-us, motivation, cover letters, or other free response unless the prompt asked.
   A blocked authorization field must not stop the rest of the batch.
11. Write free-response answers from sections F and I. Prompt-faithful. Evidence-grounded.
12. For every nontrivial free-response question, append one writing_log row with the exact question, the exact answer used, and a short evidence note.
13. Regular row. Validate, Submit once, verify. SUBMITTED or SUBMISSION_UNKNOWN. Do not click Submit a second time.
14. Prioritized row. Deeper JD and company-specific reasoning. Same evidence-bank ceiling. writing_log is mandatory for every meaningful custom question.
    Apply polar_policy.priority_submit_permitted before Submit.
    If any meaningful custom question is unanswered in writing_log, do not Submit. Mark BLOCKED.
    A logged question with a blank answer or a blank evidence_note is a Submit blocker.
    If writing_log is complete and final validation passes, Submit once and verify.
    REVIEW_READY is only for a missing owner fact or an explicit hold. It is not the default for prioritized rows.
15. If this environment cannot complete a required job-specific step after a normal attempt, status BLOCKED. Continue.
    Missing Copilot is not this case. Missing Copilot already stopped the run.
16. Update the Sheet after every meaningful stage with named writes. Refresh the lease checkpoint notes.

ATS family is only a note.
Do not implement CAPTCHA bypass, fingerprint spoofing, or anti-abuse evasion.
Update the same run_id run_log row, including submitted_regular, submitted_priority, simplify_attempted, and simplify_fallback_count.
Release the lock.
