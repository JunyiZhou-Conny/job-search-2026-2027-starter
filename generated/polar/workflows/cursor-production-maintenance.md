# cursor-production-maintenance

workflow: cursor-production-maintenance
workflow_version: 2026-09-09.direct-maintenance+a9b5017bc09e
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

## Browser lease

needs_browser_lock: false
This workflow does not take the polar_browser lock.
If apply-ready-jobs or discover-jobs-hourly holds the lock, continue anyway.

## Maintenance contract

chatgpt_required: false
chatgpt_role: optional_independent_review
cursor_reads_report_directly: true
classify_with: polar_policy.classify_maintenance_item
report_title_pattern: [Polar Production] YYYY-MM-DD
recommended_cron_et: 35 22 * * *
dispositions: FIX, OBSERVE, LOCAL_ONLY, NO_ACTION, FIXED_ALREADY
performance_priority: correctness_integrity, duplicate_submit_risk, repeated_blockers, repeated_time_sinks, cosmetic_one_off
Do not schedule this Workflow yet.
Do not invent a Polar Production report.
If the report is still sheet_only and Junyi did not supply the body, write run_log result NO_WORK and stop.
ChatGPT review is optional. Do not wait for chatgpt-production-review.
Absence of a ChatGPT review must never block this workflow.

## Input

Preferred input after github_write_canary is success:
GitHub Issue titled [Polar Production] YYYY-MM-DD.
Read the full sanitized body.
If useful, follow evidence pointers into current policy, workflow_version, compiled workflows, tests, and the decision trail.
Do not reread the whole repository without a reason.

## Work order

1. Record the workflow_version values named in the report.
2. Read the report once.
3. Group incidents by repeat_key or mechanism, not by company.
4. Classify each group with polar_policy.classify_maintenance_item.
   Disposition is one of: FIX, OBSERVE, LOCAL_ONLY, NO_ACTION, FIXED_ALREADY.
5. Verify each FIX candidate against current main.
   If main already fixes it, mark FIXED_ALREADY. Do not patch it again.
6. Interrogate only when a claim is ambiguous or may be misleading.
   Interrogate when: A report claim is ambiguous or may be misleading. Challenge the premise before any code change.
7. Arena only when at least two credible fixes have meaningful tradeoffs.
   Arena when: At least two credible fixes have meaningful tradeoffs. Do not run it for an obvious one-path fix.
8. Architect only when the lesson needs a new durable shape or plane boundary.
   Architect when: The lesson needs a new durable data shape, state machine, compiler contract, or GitHub/Sheet/local-private boundary.
9. Implement the smallest durable fix. Prefer a general invariant, fallback, or data-shape fix.
   Do not add an employer-specific rule unless the platform has a stable unique requirement.
10. Add or update tests that reproduce the actual failure mode.
11. Regenerate POLAR_RUNTIME and generated Polar workflow files when their inputs changed.
12. Run the focused tests, then the Polar suite if production behavior can change.
13. Open ONE maintenance PR.
14. STOP BEFORE MERGE.

## What not to change

LOCAL_ONLY facts stay out of public GitHub. Encode the semantic source, never the value.
Do not write street address, password, OTP, cookie, session token, or private mailbox values.
UI_ONE_OFF without high-risk correctness is OBSERVE.
A single strange writing prompt is OBSERVE. Repeated writing failure may be FIX.
NO_ACTION is a successful result when evidence is thin.

## Performance

Rank time sinks in this order: correctness_integrity, duplicate_submit_risk, repeated_blockers, repeated_time_sinks, cosmetic_one_off.
Use time_lost_category, minutes_lost, repeat_key, and workflow_version.
Prefer subtraction. Do not weaken factual or Submit verification.
Do not ask Polar to count every click.

## PR body

The PR must name:
- Production evidence
- Diagnosis
- Durable lesson
- What was deliberately not changed
- Expected next-day effect
- Verification
- Old workflow_version and new workflow_version

## Next-day verification

A green test suite is not the end of the loop.
The next Polar Production report must answer:
- Did the repeat_key recur?
- Did minutes_lost fall?
- Did the blocker disappear?
- Did a new regression appear?
- Was the new workflow_version actually used?
If the fix failed, reopen the hypothesis. Do not stack a workaround.

No autonomous merge.
Do not run gh pr merge.
Do not click Merge pull request.
Do not enable auto-merge.
