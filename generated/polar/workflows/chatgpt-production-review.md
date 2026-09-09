# chatgpt-production-review

workflow: chatgpt-production-review
workflow_version: 2026-09-08.learning-loop+1689f8dc545a
status: disabled_until_proven
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

## Status

status: disabled_until_proven
Do not schedule this Workflow.
Do not run it until github_write_canary is success and Junyi names the ChatGPT conversation.

## Designed work order

1. Open today's sanitized Polar Production GitHub artifact.
2. Open the owner-designated ChatGPT conversation only if Polar Preferences already record it.
3. If that conversation is missing, stop and write run_log result FAILED with notes chatgpt_context_missing.
4. Ask ChatGPT to classify each incident into one-off, local-only, missing document, durable policy, triage, queue/state, dedupe, writing, performance, or no action.
5. Ask for P0 durable fixes, P1 durable fixes, local-only actions, no-action items, and ONE Cursor-ready implementation prompt.
6. Persist that review back to the same GitHub artifact as a comment only if the canary write path is proven.
7. Never paste secrets into ChatGPT. Use the already sanitized report.
