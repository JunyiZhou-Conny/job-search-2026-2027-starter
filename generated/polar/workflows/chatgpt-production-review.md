# chatgpt-production-review

workflow: chatgpt-production-review
workflow_version: 2026-09-09.direct-maintenance+d82cbcaa3180
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
chatgpt_required: false
chatgpt_role: optional_independent_review
Do not schedule this Workflow.
Run it only when Junyi explicitly wants an independent second opinion.
Absence of this review must never block cursor-production-maintenance.

## Designed work order

1. Open today's sanitized Polar Production report if it exists.
2. Open the owner-designated ChatGPT conversation only if Polar Preferences already record it.
3. If that conversation is missing, write run_log result NO_WORK with notes chatgpt_optional_skipped.
   Then stop. Do not treat this as a Cursor blocker.
4. Ask ChatGPT to classify each incident using the existing Sheet categories.
5. Ask for durable-candidate lessons, observe items, local-only items, and no-action items.
6. Persist that review as a comment only if github_write_canary is success.
7. Never paste secrets into ChatGPT. Use the already sanitized report.
