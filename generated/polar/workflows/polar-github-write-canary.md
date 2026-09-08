# polar-github-write-canary

workflow: polar-github-write-canary
workflow_version: 2026-09-08.learning-loop+ddc670202ceb
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

## Work order

status: manual_canary
Do not schedule this Workflow.
Do not mutate production policy, YAML, or Polar runtime files.

Create one harmless GitHub Issue in JunyiZhou-Conny/job-search-2026-2027-starter.
Title: [Polar Canary] github-write-proof
Body: Polar created this issue to prove it can write a sanitized GitHub artifact. No secrets.
Labels are optional. Do not mention jobs, emails, or documents.

If the Issue is created, write control key github_write_canary with notes success and the Issue URL.
Write run_log result SUCCESS.
If GitHub refuses the write, write control key github_write_canary with notes failure and a short reason.
Write run_log result FAILED.
Either way, stop. Do not retry in a loop.
