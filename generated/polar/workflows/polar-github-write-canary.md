# polar-github-write-canary

workflow: polar-github-write-canary
workflow_version: 2026-09-10.pref-reconcile+853be3086a51
status: manual_canary
enabled: false
needs_browser_lock: false
schedule: manual America/New_York
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

## Work order

status: manual_canary
Do not schedule this Workflow.
Do not mutate production policy, YAML, or Polar runtime files.

Create one harmless GitHub Issue in JunyiZhou-Conny/job-search-2026-2027-starter.
Title: [Polar Canary] github-write-proof
Body: Polar created this issue to prove it can write a sanitized GitHub artifact. No secrets.
Labels are optional. Do not mention jobs, emails, or documents.

If the Issue is created, upsert control key github_write_canary with notes success and the Issue URL.
Locate that row by key. Never write into the polar_browser row.
Commit the edit. Reread key and notes. GitHub issue existence is a second signal, not a substitute for the reread.
Write run_log result SUCCESS.
If GitHub refuses the write, upsert the same github_write_canary key with notes failure and a short reason.
Write run_log result FAILED.
Either way, stop. Do not retry in a loop.
