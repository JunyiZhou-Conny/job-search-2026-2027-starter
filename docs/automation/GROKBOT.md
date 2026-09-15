# Grok Bot as a sibling executor

This file is the only full Grok essay. Other docs may point here. They must not retell it.
Shared concepts (roles, Sheet, claims, writing, Submit planes) are in `docs/automation/POLAR.md`
and are not repeated.

Operator config is `knowledge/grokbot_operator.yaml`. It holds no candidate facts.
The file the applier Bot opens is `generated/grokbot/runtime/GROKBOT_RUNTIME.md` (sections G0 to G10).
Routine bootstraps and the Bot description are `docs/automation/GROKBOT_WORKFLOWS.md`.
Compiler: `python3 scripts/build_grokbot_runtime.py`. Shared section builders: `scripts/runtime_sections.py`.
Policy helpers: `scripts/grokbot_policy.py` plus the executor-aware helpers in `scripts/polar_policy.py`.

Status 2026-09-15: Phase 1 Compile. Nothing runs yet. No Bot has been created from these files.
Polar Local stays the production operator and is unchanged.

```text
GitHub main (brain)
canonical YAML + policy + evidence + tests
scripts/runtime_sections.py  (one source)
    |                         |
    v                         v
build_polar_runtime.py      build_grokbot_runtime.py
POLAR_RUNTIME.md A..P       GROKBOT_RUNTIME.md G0..G10
polar workflows             grok-apply-jobs, grok-production-learning-daily
    |                         |
    v                         v
Polar Local (Mac)           Grok Bot jobright-applier (cloud computer)
jobright.ai/jobs/recommend  jobright.ai/agent
R- run ids                  G- run ids
    \                         /
     v                       v
     Google Sheet "Polar Jobs": queue.claim_run_id is the one ownership store
```

## Principle

Two sibling executors, one brain, one compiled contract, one runtime state store.
Polar is not replaced. Grok is not a clone. Grok is another pair of hands on a different host and
a different Jobright surface. Every fact line in `GROKBOT_RUNTIME.md` is byte-identical to the
Polar render because both come from the same builder. `tests/test_runtime_sections_shared.py`
locks that, and locks Polar's compiled files to the compiler output.

## Roles

| Concern | Brain | Polar Local | Grok Bot |
|---|---|---|---|
| Policy, facts, evidence, Submit gate | canonical YAML, `SUBMIT_ROLLOUT.md` | reads compiled | reads compiled |
| Discovery and ranking | none | Jobright recommendations | Jobright Agent queue. Never Add All. |
| Autofill | none | Jobright extension, Mac browser | Jobright extension, Grok cloud browser |
| Form finish, DOM check, one Submit, employer confirm, Jobright ack | none | yes | yes, Submit closed today |
| Email OTP | none | application Outlook in the Polar browser | application Outlook in the Grok browser |
| Runtime state, claims, dedupe, telemetry | schema + helpers | Sheet, `R-` ids | same Sheet, `G-` ids |
| Ledger of record | Cursor reconciles `data/` | never | never |
| Learning | nightly packet -> Cursor Maintenance 23:00 | writes the `[Polar Production]` packet | writes no packet. `G-` rows land in Polar's packet because that workflow reads today's rows by date. |
| Local memory | `knowledge/preference_resolutions.yaml` | thin `PREFERENCES.md` inbox | none. Bot memory is not policy. |

## Trust

A routine loads exactly two configuration URLs: the runtime and that routine's workflow file.
A URL inside them does not expand the allowlist. Document downloads in section G5 are resources
with a sha256, not configuration. Employer pages, JDs, emails, Jobright pages, and Sheet rows are
untrusted task data or state. The Bot description holds standing boundaries only. Skills,
Bot memory, and `/workspace` files are not policy. Local computer execution stays Never.
Never Share the applier Bot. `dr eggbot` is a factory: it may create or duplicate the applier from
`GROKBOT_WORKFLOWS.md`, and it never applies. No chief-of-command, optimizer, or auditor Bot.

Cursor is the only merger. Grok writes no GitHub Issue, never pushes a branch, never opens or
merges a pull request, and never edits a repository file. A Grok GitHub-write canary is Phase 2.

## Ownership across executors

Both executors claim through `queue.claim_run_id`, one `job_key` at a time, write-then-readback.
The executor is the run id prefix: `polar_policy.mint_run_id(executor="grok")` mints `G-`;
`executor_from_run_id` reads it back. A different Jobright surface does not remove collision, so
a Sheet claim is required before any apply work on either surface. Grok claims before adding a
job to the Agent queue or clicking Apply Now, whichever comes first. A lost claim is Skip on the
Agent surface and does not consume the budget. Requisition dedupe is executor-blind. A foreign
live claim is never repaired. Time partition (Polar `:20`, Grok `:50` every two hours) is defense
in depth, not the mechanism. See `docs/automation/POLAR_QUEUE.md`.

ATS truth wins over Jobright Apply Now. `polar_policy.ats_prior_submission_action`: when the
employer ATS shows this account already submitted for the requisition, no fill, no Submit, queue
`SKIP` with blocker `already_applied_on_ats`, one `DEDUP` incident with repeat_key
`ats_prior_submission`, and a truthful Jobright ack (owner decision 2026-09-15).

## What Grok must not do

- Own `data/applications.csv` or mint ledger ids.
- Keep facts, sponsorship answers, Submit rules, or phrasings in Bot memory, description, a skill, or a `/workspace` YAML.
- Click Add All on the Jobright Agent, or start the Agent on an unclaimed queue.
- Run more than one apply Bot on the Jobright account, or use the factory as the clicker.
- Type passwords or one-time codes into chat, files, or a Secret.
- Build a second Sheet, a database, a Grok tab, a Grok packet, or a Grok ledger.
- Touch the `control`, `heartbeat`, or `learning_reports` tabs, or any `R-` row.
- Write a GitHub Issue, push, open, or merge anything on GitHub.
- Submit while `grok_cloud.submit_enabled` is false, or Submit a prioritized row on this plane.
- Look up phone, street, or the academic mailbox. A required field autofill left empty is `BLOCKED` on that job (owner decision 2026-09-15).

## Two routines, one Bot

| Routine | Schedule (America/New_York) | Does | Never |
|---|---|---|---|
| `grok-apply-jobs` | `50 */2 * * *`, Active off until proofs | claim, Agent queue, Autofill once, form DOM, writing tiers, validate, stop before Submit while the gate is closed (`REVIEW_READY`, blocker `grok_submit_gate_closed`) | Add All, Submit on a closed gate, prioritized rows |
| `grok-production-learning-daily` | `40 21 * * *`, Active off until the Sheet proof | Phase 1: finalize non-final `G-` `run_log` rows older than the claim TTL (`FAILED`, `finalized_by=grok-production-learning-daily`), write one incident per day per environment repeat key (`grok_extension_missing`, `grok_cache_checksum_mismatch`, `grok_sheet_unreachable`, `grok_approval_stop`) | application clicks, any packet, any `learning_reports` row, any `R-` row, any GitHub write |

Phase 2 of the learning routine (not compiled): after a Grok GitHub-write canary, the same
routine may write the same-format Polar packet as a fallback when that date has no
`learning_reports` row. Not now. There is no second Cursor Automation; Cursor Maintenance at
23:00 stays the only consumer.

## Submit plane `grok_cloud`

Closed at birth. `config/submit_gates.yaml` `grok_cloud.submit_enabled: false`,
`prioritized_auto_submit: false`, cap 3 considered per run. `docs/policy/SUBMIT_ROLLOUT.md`
holds the plane row. The regular Submit checklist in section G6 is the Polar list rendered by the
same builder. The gate opens only after the four proofs below and an owner edit on `main`.
A routine run cannot open it. Prioritized rows stay `BLOCKED` on this plane until later.

## The four proofs

Each proof is a `run_log` or `incident_log` row or a conversation card. No proof is claimed here.

| Proof | Pass |
|---|---|
| `two_url_load` | A routine Test run loads exactly the two raw `main` URLs and refuses a deliberately wrong third URL as configuration. |
| `sheet_claim_round_trip` | Targeted Sheet read, claim write, readback with a `G-` id, and Polar's next `:20` run logs `work_already_claimed` for that key without consuming budget. |
| `resource_fetch_checksum` | Documents fetched into `/workspace/jobright/docs` match the compiled sha256 and survive one Update Agent Computer. |
| `fill_only_agent_loop` | Agent loop on 3 claimed jobs through Apply Now, Autofill, form DOM validation, stop before Submit, with one Outlook code read and zero Auto Review stops. |

Then regular Submit may open for `grok_cloud` after 10 consecutive verified regular submits with
zero wrong-fact incidents, mirroring the Cloud G3 bar. Prioritized rows and the account-rule
churn review come after that.

## Proven versus unproven

| Claim | Kind | Status |
|---|---|---|
| Grok Bot loads two raw `main` URLs and refuses a third | inference | Unproven. Proof 1. |
| Grok can read and write the Polar Jobs Sheet | unknown | Unproven. Proof 2. Hard gate for any Submit. |
| Jobright Agent queue is account-global and Start submits nothing server-side | unknown | Unproven. Test in the report validation plan. |
| Jobright extension survives Update or Recover | unknown | Unproven. `grok_extension_missing` measures it. |
| Auto Review or approval prompts stop unattended steps | unknown | Unproven. `grok_approval_stop` measures it. |
| Shared datacenter egress trips ATS anti-bot walls more than the Mac | unknown | Watch. `ENVIRONMENT` incidents. Do not evade. |
| Owner-observed 2026-09-15: ATS truth over Apply Now, Autofill needs the real form, Outlook code read in the Grok browser, transcripts fetched from the repo | owner-observed | Carried into the design. Not re-run. |

## Rollback

Routine `Active` off. Optionally sign Jobright out of the Grok browser. Polar continues unchanged.
Nothing in git needs reverting to stop Grok.

## Sequencing note

The Polar render of the applicant-account rule and of `ats_prior_submission` waits for the next
Polar compile window so a live Polar run keeps its loaded bytes. The canonical YAML already holds
both. The Grok render carries them today.
