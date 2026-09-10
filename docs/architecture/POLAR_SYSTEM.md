# Polar job-search system map

This page is the companion to the current Polar production maps. The diagrams are the primary artifact. This text answers the questions the nodes cannot hold.

Policy revision on the `main` this map was drawn from is `2026-09-10.worker-pool`. Measured from `knowledge/polar_operator.yaml` and `generated/polar/workflows/WORKFLOW_MANIFEST.md`.

Canonical behavior lives in YAML, `scripts/polar_policy.py`, and the compilers. Polar reads compiled English from raw `main`. Generated files are not independently canonical.

## How to read this map / 怎么看这张图

Start with [`polar-system-map.mmd`](polar-system-map.mmd) or the poster at [`rendered/polar-system-map.svg`](rendered/polar-system-map.svg). Read the six bands from control plane through discovery, workers, ATS, persist, and the workflow inventory.

English names on a node are the real symbols. `READY_PRIORITY`, `claim_run_id`, `apply-ready-jobs`. Chinese on the same node is meaning, why, or recovery. One diagram. Not two translations.

Use the zoom-ins when the master node is too short:

- [`polar-apply-worker.mmd`](polar-apply-worker.mmd) for one worker from trust bootstrap to Submit.
- [`polar-state-concurrency.mmd`](polar-state-concurrency.mmd) for status, claims, and the same requisition.
- [`polar-learning-loop.mmd`](polar-learning-loop.mmd) for what is automatic today versus what still needs a human.

Dashed gray is historical or disabled. Red is a genuine human gate. Green cylinders are Sheet runtime. Yellow diamonds are decisions Polar must make from live data.

`docs/state/REALITY_MAP.md` is 2026-09-03 archaeology. Do not use it as the current Polar map.

## Major components

GitHub is durable canonical memory. Policy, evidence, resume metadata, compilers, and generated Polar English live there.

Polar Local is the production browser operator on Junyi's Mac. Each saved Workflow stores only a trust-delegation bootstrap. That bootstrap loads two owner-designated raw `main` URLs. A URL inside those files does not expand the allowlist.

Cursor is the engineer. It changes YAML and `polar_policy`, compiles generated files, opens a PR, and stops before merge. Cursor Cloud discovery is shadow and fallback. Cloud Computer Use is a second Submit plane with ATS-family gates. Do not mix the two planes.

The Google Sheet is shared operational state. It is the checkpoint. It is not a second `applications.csv`.

`/home/polar/PREFERENCES.md` is a thin local inbox. It may hold LOCAL_PRIVATE values and pending `pref_YYYYMMDD_NNN` candidates. It is not a second strategy database. An old PREFERENCES strategy line must not override newer GitHub behavior.

Simplify Copilot is a required apply precondition. Proof is Copilot UI on the employer ATS page. A healthy `simplify.jobs` login is not proof.

## Workflow responsibilities

Scheduled production workflows, all with `needs_browser_lock: false`:

| Workflow | ET cron | What it owns |
|---|---|---|
| `discover-jobs-hourly` | `0 * * * *` | Jobright cards into `queue`. Triage. READY labels. Never apply. |
| `apply-ready-jobs` | `20 * * * *` | One worker. Claim, fill, Submit, recover. Per-run budget 3. |
| `polar-scheduler-heartbeat` | `5 * * * *` | Harmless page plus one `heartbeat` row. Locked-screen proof. |
| `daily-job-summary` | `30 21 * * *` | One email digest. First section is prioritized SUBMITTED rows. |
| `production-learning-daily` | `0 22 * * *` | Sanitized learning report. Does not change GitHub policy. |

Manual or disabled workflows. Drawn dashed on the master map.

| Workflow | Status | What it owns |
|---|---|---|
| `polar-sheet-migration` | `manual_once` | Only schema mutator for `claim_run_id` and required tabs. |
| `polar-github-write-canary` | `manual_canary` | One harmless GitHub Issue. Sets `control.github_write_canary`. |
| `chatgpt-production-review` | `disabled_until_proven` | Optional later classifier. Not a required hop. |
| `cursor-production-maintenance` | `disabled_until_proven` | Designed Cursor handoff. Never merge. |

Independent Polar Workflows may overlap. Each may keep its own browser surface. A crashed apply worker must not freeze heartbeat, discovery, or learning.

## State meanings

| Status | Meaning |
|---|---|
| `NEW` | Seen and written. Not yet READY. |
| `READY_REGULAR` | Keep, regular weight, eligible to execute. |
| `READY_PRIORITY` | Keep, prioritized weight, eligible to execute with deeper writing. |
| `IN_PROGRESS` | This run owns the row via `claim_run_id`. Other jobs may also be IN_PROGRESS. |
| `REVIEW_READY` | Form is complete but Polar stopped for a missing owner fact or an explicit hold. Not the default for prioritized rows. |
| `SUBMITTED` | Submit clicked and verification succeeded. |
| `SUBMISSION_UNKNOWN` | Submit may have happened. Verify before any retry. Never blindly resubmit. |
| `BLOCKED` | This job cannot finish a required job-specific step. The worker continues. Missing Copilot is not BLOCKED. |
| `SKIP` | Hard skip, closed posting, owner skip, or duplicate requisition. |

`last_stage` is a coarse checkpoint on the same queue row. It is not a second status machine. Values are `discovered`, `source_resolved`, `application_open`, `authenticated`, `form_filled`, `reviewed`, `submit_clicked`, `confirmation_seen`.

Discovery must not overwrite execution fields on `IN_PROGRESS`, `SUBMITTED`, `SUBMISSION_UNKNOWN`, `REVIEW_READY`, or `BLOCKED`. The helper is `polar_policy.discover_may_overwrite_execution_fields`.

## Concurrency model

There is no production `polar_browser` mutex. That control key is historical. Do not acquire it. Do not write `SKIPPED_LOCKED` because that row looks held.

Each `apply-ready-jobs` invocation is one worker. Its new-work budget is `max_new_jobs = 3`. One of those three slots is reserved for `READY_PRIORITY` when such a row exists. There is no shared daily regular submission pool. Another overlapping apply run has its own budget.

Ownership is `queue.claim_run_id` on one `job_key`. The worker claims one job close to execution, processes it, then calls `select_next_apply_job` again. A lost claim does not consume the budget.

Google Sheet writes are last-write plus readback. The Sheet is not compare-and-swap. Two workers may attempt Job X. Only the run whose readback still shows its `claim_run_id` proceeds. The loser notes `already_claimed` and selects the next job.

Before Submit the owner rereads `claim_run_id` (`submit_claim_still_held`) and reruns `requisition_submit_blocked`. A later sibling claim can flip the canonical winner. That is why the Submit-time reread exists.

The same employer requisition has one logical survivor. `pick_canonical_requisition_row` ranks `SUBMITTED`, then `SUBMISSION_UNKNOWN`, then live `IN_PROGRESS`, then earlier `discovered_at`, then `job_key`. `requisition_submit_blocked` ignores `SKIP` and abandoned `IN_PROGRESS`. The non-canonical worker marks its row `SKIP` with blocker `duplicate employer requisition`. Both workers must not back off.

Abandoned claims are locally recoverable. Empty `claim_run_id` on `IN_PROGRESS` is abandoned. A claim older than 180 minutes with a parseable `updated_at` is abandoned. A claim whose owner `run_log.result` is not `PARTIAL` is abandoned. Unreadable `updated_at` is not abandoned. A live claim owned by another `run_id` must not be stolen.

## READY_REGULAR vs READY_PRIORITY

`application_weight` is orthogonal to `pursuit_lane` (`core` / `broad` / `practice`).

`READY_REGULAR` is fast truthful autonomous execution. Prefer the Simplify resume already attached. Autofill once. Correct visible widgets. Short prompt-faithful free response. Submit when final validation passes.

`READY_PRIORITY` is the same truth ceiling plus more work. Deeper JD and company-specific reasoning. Resume tailoring only from `knowledge/evidence_bank.yaml` facts that are `verified` and `resume_eligible`. Every meaningful custom question must have a complete `writing_log` row before Submit. Polar Local may auto-submit when `polar_policy.priority_submit_permitted` is true. Junyi does not confirm every priority label before the queue can move. Daily digest gives post-submit oversight.

Strong signals that may set `READY_PRIORITY` without waiting. `fde` title. `gtc_2026`. `confirmed_prioritized`. Clear `fortune_500_or_major`. Clear `biotech_health_ai`. Weak hints stay `READY_REGULAR`.

Cursor Cloud prioritized rows still stop for a review packet. That is the other Submit plane. Do not draw Polar Local as waiting for that packet.

## Simplify environment model

Role is `required_precondition`. Proof is `employer_page_copilot_ui`. Not proof is `simplify.jobs` login or API.

States are `PRESENT`, `MISSING`, `UNKNOWN`. Last state lives on `control.env_simplify_copilot` as telemetry. It is not a skip-check cache. The next apply run rechecks Copilot on an employer page.

If Copilot is PRESENT, click Autofill This Page or Start Application once. Never Run Autofill Again. Never Generate with AI. Then read the visible widgets.

If Copilot is MISSING or UNKNOWN, do not fall back to traditional clicking. Restore the probe job to its prior READY status. Clear `claim_run_id`. Do not mark the job `BLOCKED`. Write incident `ENVIRONMENT` / `simplify_copilot_missing`. Exit the apply run with `OWNER_ACTION_REQUIRED`. The job stays valid. The environment is unhealthy.

## Recovery model

Recovery order is `SUBMISSION_UNKNOWN`, then abandoned or self-owned `IN_PROGRESS`, then `READY_PRIORITY`, then `READY_REGULAR`.

Crash before ATS. The row may already be `IN_PROGRESS`. The next worker recovers it if the claim is abandoned or self-owned. Otherwise it leaves that job and takes another.

Crash during form fill. Resume from `last_stage`. Do not restart an earlier finished job.

Crash after Submit click and before confirmation. Persist `SUBMISSION_UNKNOWN` when possible. The next run verifies first. It must not click Submit again.

Crash after confirmation and before persistence. The next run still verifies. Then it writes `SUBMITTED`.

`SUBMISSION_UNKNOWN` is the verify-before-retry invariant. Daily summary also surfaces those rows for owner eyes.

## State ownership table

| Store | Owns | Does not own |
|---|---|---|
| GitHub `main` | Policy, evidence, compilers, generated Polar English, HistoricalGuard keys | Hourly checkpoints, passwords, street address |
| Polar bootstrap | Exact two-file load set for that Workflow | Strategy text, Sheet schema |
| `PREFERENCES.md` | Local-only facts, pending learning ids | Canonical behavior after a GitHub conflict |
| Google Sheet `queue` | Job lifecycle, `claim_run_id`, `last_stage` | Durable policy |
| Sheet `writing_log` | Exact custom question, answer, evidence note | Resume files |
| Sheet `run_log` | One upserted row per invocation | A second applications ledger |
| Sheet `incident_log` | Material events, `repeat_key`, `durable_candidate` | Secrets |
| Sheet `heartbeat` | Locked-screen scheduler proof | Job ownership |
| Sheet `control` | Historical `polar_browser`, `github_write_canary`, `env_simplify_copilot` | A production browser lock |
| Sheet `learning_reports` | Sanitized daily Markdown | Unredacted PREFERENCES |
| Cursor | PRs, tests, Cloud shadow discovery | Autonomous merge, Polar cookies |
| ChatGPT | Nothing on the critical path today | Production policy |

## Self-improvement loop

Real Polar production writes Sheet telemetry and may add PREFERENCES candidates.

`production-learning-daily` reads today's `run_log`, `incident_log`, `writing_log`, and `queue`. It groups by `repeat_key`. It writes one sanitized report. It rewrites PREFERENCES to four sections. Emitting the report does not resolve a candidate.

If `github_write_canary` is `success`, the same body may become a GitHub Issue. Otherwise the report stays `sheet_only`. Do not invent a GitHub write path.

`chatgpt-production-review` is compiled and disabled. Do not treat ChatGPT as a required hop.

A human or a later Cursor session reads the sanitized evidence. It classifies bug, policy gap, recurring UX failure, one-off, environment, or no-action. It inspects current `main`. It generalizes a fix. It runs tests. It opens a PR. It stops.

Human merge is the only gate that changes Polar's next-load behavior. After merge, the same bootstrap loads updated raw `main` files. Production behavior changes on the next invocation.

`cursor-production-maintenance` describes that Cursor handoff. It is disabled until proven. It still says STOP BEFORE MERGE.

## Human intervention boundaries

Genuine human gates on current `main`:

- Install or restore Simplify Copilot when the employer page has no Copilot UI.
- Run `polar-sheet-migration` once when `claim_run_id` is missing or duplicated.
- Provide a genuinely missing private fact or document. Birth date, OPT months, a required transcript that is not in the local registry.
- Merge a Cursor PR. An open PR is not canonical.
- Run `polar-github-write-canary` once if you want Issues instead of Sheet-only learning.
- Name a ChatGPT conversation only if you later enable that optional bridge.
- Cursor Cloud prioritized review packets. Polar Local does not wait for those.

Ordinary browser work is Polar work. Account creation, email OTP on the Mac, multi-page forms, and Why-Be answers from the evidence bank are autonomous once the gates above are clear.

## What is automatic today vs what still needs a human

Automatic today, once Copilot is present and the Sheet schema is ready:

- Hourly discovery, triage, READY labeling.
- Hourly apply for regular and prioritized Polar Local rows, including Submit.
- Heartbeat, daily email, sanitized learning report.
- Preference reconcile against resolution rows that are already on `main`.

Still needs a human:

- First-time Sheet header migration.
- Copilot install or repair.
- Missing private facts.
- Merge.
- Optional ChatGPT and Cursor-maintenance Workflows.
- Cloud G2 Submit. That gate stays closed.

## Source-of-truth references

Compiler relationship. `knowledge/polar_operator.yaml` plus the other YAML listed in `POLAR_RUNTIME` plus `scripts/polar_policy.py` feed `scripts/build_polar_runtime.py` and `scripts/polar_workflows.py`. Those writers emit `generated/polar/runtime/POLAR_RUNTIME.md` and `generated/polar/workflows/*.md`. Polar follows the compiled English. Engineers change the YAML and helpers, then recompile.

Read these when a node is in doubt:

- `knowledge/polar_operator.yaml` for schedules, statuses, columns, Copilot, memory, and `work_claim`.
- `scripts/polar_policy.py` for `attempt_claim_job`, `select_next_apply_job`, `claim_is_abandoned`, `pick_canonical_requisition_row`, `priority_submit_permitted`, and Copilot restore.
- `docs/policy/SUBMIT_ROLLOUT.md` for the two Submit planes.
- `docs/automation/POLAR.md` for the Polar essay.
- `docs/automation/POLAR_QUEUE.md` for Sheet columns.
- `docs/automation/POLAR_WORKFLOWS.md` for the bootstrap paste.
- `knowledge/application_priority.yaml` and `knowledge/discovery_triage_rules.yaml` for READY labeling.
- `knowledge/form_strategy.yaml` and `knowledge/evidence_bank.yaml` for form truth.
- `tests/test_polar_concurrency.py` and `tests/test_polar_copilot_memory.py` for the claim and Copilot contracts.

## Validation traces

These traces are how to walk the master map. The checker in `scripts/validate_polar_system_map.py` requires the named nodes to exist.

1. Ordinary job. Jobright → `discover-jobs-hourly` → KEEP → `READY_REGULAR` → `apply-ready-jobs` → claim → employer page → Copilot PRESENT → Autofill → Submit once → `SUBMITTED`.
2. Prioritized job. Same path through `READY_PRIORITY`, then extra JD work and `writing_log`, then `priority_submit_permitted`, then Submit.
3. Two concurrent workers. Worker A Job X and Worker B Job Y at the same time. No `polar_browser` acquire.
4. Two workers on Job X. Write, readback, only current `claim_run_id` proceeds.
5. Same requisition. `pick_canonical_requisition_row` keeps one survivor.
6. Copilot MISSING. Restore READY, clear claim, `env_simplify_copilot`, `OWNER_ACTION_REQUIRED`, job still valid.
7. Crash before Submit. Recover abandoned or self-owned `IN_PROGRESS` from `last_stage`.
8. Crash after Submit click. `SUBMISSION_UNKNOWN`, verify before retry.
9. `SUBMISSION_UNKNOWN` recovery. Inspect first. Never blindly resubmit.
10. Learning. Telemetry → `production-learning-daily` → report → optional Issue → Cursor PR → human merge → next Polar load.
11. Schema. Missing `claim_run_id` exits apply. Only `polar-sheet-migration` appends the column.
12. Disabled workflows stay dashed. ChatGPT is not on the happy path.

## Repository contradictions

These are real disagreements found while drawing. The map follows the compiler and `polar_policy`, not the stale line.

1. `docs/state/REALITY_MAP.md` still describes `main` at `28bd317` on 2026-09-03. It is archaeology. The current Polar map is this folder.
2. `docs/apply/PRIORITY.md` still says Lila waits for a review packet since 2026-09-03. Polar Local policy since `prioritized_auto_submit: true` is Submit after `writing_log`. Cursor Cloud still uses a review packet.
3. `knowledge/application_priority.yaml` Lila `hold_reason` still names that 2026-09-03 packet rule. That row is historical company notes. It does not override `polar_operator.yaml` canary or `SUBMIT_ROLLOUT.md`.
4. `AGENTS.md` still says the broad future-sponsorship widget is No, dated 2026-09-03. Compiled `apply-ready-jobs` and `knowledge/form_strategy.yaml` dated 2026-09-10 say a required future-sponsorship widget is Yes. Polar execution follows the compiled workflow and `form_strategy.yaml`.
5. `docs/automation/POLAR.md` still has a root loop line "submit or prepare for review". Polar Local prioritized rows no longer default to review. `REVIEW_READY` is only a missing owner fact or an explicit hold.
6. `docs/automation/POLAR.md` still says do not build "parallel browser workers". That forbids a custom worker-fleet product. It does not forbid overlapping Polar Saved Workflows. Current production allows those overlaps.

None of these block using this folder as the canonical mental model for Polar Local on current `main`. They do mean you should not treat `REALITY_MAP.md` or the 2026-09-03 AGENTS sponsorship sentence as Polar execution policy.

## Visual structure

The master poster is six columns, left to right.

Column 1 is ownership. Who may change behavior. Who only holds runtime.

Column 2 is discovery. Sources into READY.

Column 3 is workers. Trust, schema, claim, concurrent jobs. The obsolete mutex is drawn as historical.

Column 4 is the employer page. Eligibility, requisition, Copilot, fill, priority extra work, Submit recheck.

Column 5 is persist and learning. Statuses, telemetry, sanitized export, human merge, next load.

Column 6 is every Polar workflow. Scheduled boxes are solid. Manual and disabled boxes are dashed.

Zoom-ins repeat the same names so a classmate can jump without learning a second vocabulary. The SVG is the Zoom artifact. A 1600-pixel thumbnail will look empty.
