# polar-scheduler-heartbeat

workflow: polar-scheduler-heartbeat
workflow_version: 2026-09-08.learning-loop+d99af025ea26
status: production
enabled: true
needs_browser_lock: false
schedule: 5 * * * * America/New_York
runtime_url: https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md
COMPILED ARTIFACT. Not canonical.

## Work order

Mode: saved Workflow on the named local profile.
This workflow does not take the polar_browser lock.

Open https://example.com
Confirm the page title contains Example Domain.
Open the Polar Jobs Google Sheet tab heartbeat.
Append one named row:
- recorded_at: now, America/New_York
- workflow: polar-scheduler-heartbeat
- result: success
- page_opened: https://example.com
- notes: screen lock unknown to you. Write only what you can observe.

If you cannot open the page or the Sheet, append result failure and a short note.
Also write one run_log row with lock_result NOT_REQUIRED.
Never apply. Never open Jobright. Never include secrets.
