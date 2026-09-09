# cursor-production-maintenance

workflow: cursor-production-maintenance
workflow_version: 2026-09-09.prod-learn+21b841a26ef0
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
Do not run it until the ChatGPT review path and Cursor browser handoff are proven.

## Designed work order

1. Open today's production report.
2. Read the ChatGPT production review if present.
3. Open Cursor Web or Cursor Agent only if Polar Preferences already record that target.
4. Give Cursor the generated implementation prompt.
5. Cursor must inspect current main, verify each claimed issue, change only durable lessons,
   regenerate runtime and workflow artifacts, run tests, and open a PR.
6. STOP BEFORE MERGE.

No autonomous merge.
Do not run gh pr merge.
Do not click Merge pull request.
Do not enable auto-merge.
