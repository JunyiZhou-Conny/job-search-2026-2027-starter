# Polar as the local production operator

This file is the only full Polar essay. Other docs may point here. They must not retell it.

Operator config is `knowledge/polar_operator.yaml`.
The file Polar opens every hour is `generated/polar/runtime/POLAR_RUNTIME.md`.
Queue columns and statuses are `docs/automation/POLAR_QUEUE.md`.
Paste-ready Workflow text is `docs/automation/POLAR_WORKFLOWS.md`.
The 48-hour Cloud comparison is `docs/automation/POLAR_SHADOW.md`.
Pilot packets and the ATS matrix stay under `docs/experiments/` and `generated/polar/`.

The 2026-09-04 Live Slot design in `docs/automation/POLAR_SCALE.md` is the pilot lineage. It is not the production shape.

```text
GitHub
canonical memory, configuration, policy, evidence, audit
        |
        +----------------------+----------------------+
        |                                             |
        v                                             v
Cursor / Cloud                                  Polar / Local
engineer, maintainer                            authenticated production
fallback discovery                              hourly discovery
reconciliation                                  Jobright source_url
                                                form execution
                                                lane-aware submit
                                                result reporting
```

## Owner decision

The product goal is no longer one Cursor discovery pass, one pasted job, and one Polar experiment.

The production loop is hourly authenticated local discovery, a durable queue, local Polar execution, resumable state, automatic Submit on regular and prioritized jobs, a daily digest, and a sanitized production-learning report. Polar conversation windows are disposable. Learning lives in Sheet telemetry and the compiled GitHub artifacts.

ATS family is diagnostic metadata only. It is not the root abstraction.

The root loop is:

```text
READY job
  -> reach the original employer application
  -> authenticate if needed
  -> fill
  -> answer
  -> validate
  -> submit or prepare for review
  -> verify
  -> persist state
```

## Evidence kinds

Treat each claim as one of these. Do not upgrade a lower kind.

- **Owner-observed.** Junyi's live Polar, Jobright, and Mac use.
- **Public product docs.** Polar's own site and press. Cited when used.
- **Architectural inference.** A boundary we chose so GitHub stays one memory system.

## Roles

GitHub is canonical memory. Policy, evidence, resume metadata, and audit live here. Polar reads one compiled file from a stable raw URL. Polar writes runtime checkpoints to the Google Sheet, not a second git ledger.

Cursor and Cloud remain the engineer. They maintain this repo, compile `POLAR_RUNTIME`, reconcile the Sheet into `data/applications.csv` when a result is verified, and keep Cloud discovery running as shadow and fallback. Cloud Computer Use stays available on a Cloud Agent VM. See `docs/automation/DAILY_JOB_DISCOVERY.md` and `docs/automation/COMPUTER_USE_PROMPT.md`.

Polar is the local production operator. It runs on Junyi's Mac with the real browser profile. It does hourly Jobright discovery. apply-ready-jobs resolves Original Job Post on demand. Polar also does ordinary account creation and auth, writing, Submit according to lane, and result reporting.

Junyi is willing to leave the Mac powered on and online. Polar Workflows can use a named profile, save reusable instructions, attach files, and run on a schedule, including an hourly schedule at a selected minute.

Polar's own introduction says it "clicks, types, and navigates the web the way you would, logged in as you" ([Introducing Polar](https://polarbrowser.com/blog/introducing-polar)). Polar describes itself as a Chromium fork ([A New Interface for Composer](https://polarbrowser.com/blog/new-interface)). TechCrunch reports that users can schedule workflows and save prompts ([29 July 2026](https://techcrunch.com/2026/07/29/perplexity-employee-who-worked-on-comet-launches-an-ai-browser-aimed-at-knowledge-work/)).

## What Polar must not do

Polar must not become a second job-search truth system.

- Own `data/applications.csv` or mint ledger ids.
- Click Jobright **APPLY WITH AUTOFILL**.
- Copy the whole repository into the Workflow prompt.
- Store passwords, cookies, OTP codes, or 2FA secrets in git, the Sheet, or mail.
- Invent metrics, projects, employers, referrals, clearance, or technologies outside the evidence bank.
- Auto-submit a prioritized row when `writing_log` is incomplete.
- Disable Cloud discovery on day one.
- Organize execution as ATS-family worker classes.
- Build a database, Redis, a web service, parallel browser workers, or a custom scheduler.

## One compiled runtime

Polar should not reread ten YAML files every hour.

`scripts/build_polar_runtime.py` compiles canonical repo state into `generated/polar/runtime/POLAR_RUNTIME.md` and `generated/polar/workflows/`. Those files are COMPILED, not canonical. After `main` has them, a saved Polar Workflow opens one stable raw URL:

`https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/<workflow>.md`

That file then opens `POLAR_RUNTIME.md` from the same `main` raw tree.

Until `main` has the files, use the same path on the production branch.

The compiler must stay the only writer of those files. Tests refuse passwords, cookies, OTP assignments, leaked phone or email, missing policy sections, and contradictory identity facts.

## URL rules

These two fields are not interchangeable.

| Field | Meaning |
|---|---|
| `source_url` | Where Polar found the row. Often `https://jobright.ai/jobs/info/...`. |
| `apply_url` | Employer application URL when Polar trusts it. |

If `apply_url` is present and `apply_url_confidence` is `exact` or `strong`, Polar opens that URL. Do not open Jobright first.

discover-jobs-hourly does not open Original Job Post. It keeps the Jobright `source_url`.

If `apply_url` is empty and `source_url` is a Jobright job page, apply-ready-jobs opens that page in the local logged-in session and clicks **Original Job Post** only. Follow one redirect if the click needs it. Keep the result only when the final host is not `jobright.ai`.

Junyi observed that logged-in Jobright shows **Original Job Post**. For Tallgrass Intern-AI and Data Solutions, that link was `https://epix.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/4239?jr_id=6a9b267b90a313642c658c5f`.

`scripts/resolve_apply_url.py` still helps cloud runs that have no Jobright session. Polar does not need it when Original Job Post works.

If Original Job Post cannot be resolved, keep the Jobright URL. Application execution must still be able to resolve it later. The resolver is an optimization, not a prerequisite.

Do not resolve Original Job Post for obvious SKIP rows.

## Durable state

Do not rely on a Polar tab.

The Google Sheet is the operational store. GitHub is not the hourly checkpoint.

Sheet writes use the live header row and named fields. Polar must not omit `apply_url_confidence` and shift later columns. After an important queue write, read back `job_key`, `status`, and `last_stage`.

`discover-jobs-hourly` and `apply-ready-jobs` take a 180 minute `polar_browser` lease in the `control` tab so a long apply run does not overlap the next hourly Workflow.

Recovery must survive Mac shutdown, Wi-Fi loss, browser restart, Workflow interruption, and the laptop leaving the desk.

See `docs/automation/POLAR_QUEUE.md` for columns, statuses, and the recovery order.

`last_stage` is a coarse checkpoint. Status is the state machine. Do not add more statuses without an owner decision.

## Regular versus prioritized

`application_weight` stays. It is production policy, not a pilot leftover.

Regular work is fast and truthful. Prefer the Simplify resume already attached. If the widget is empty, upload the compiled base `JZ_resume` PDF. Use Simplify once when it helps. Correct visible fields. Complete ordinary account creation. Write short prompt-faithful answers. Validate. Submit once. Verify. Persist.

Prioritized work gets more care. Signals include startup or scale-up Junyi values, Fortune 500 or major companies, NVIDIA GTC, prestige, biotech or health AI, strong biostatistics or bio data-science fit, FDE, and unusually strong personal fit. Do not mark a generic analyst or data role prioritized only because the title contains "data".

For prioritized rows, research the JD, write a better Why-us from the evidence bank only, tailor the resume only when justified, finish the form, log every meaningful custom question and the exact answer used, then Submit when final validation passes. The daily digest highlights those rows for post-submit oversight. `REVIEW_READY` is only for a missing owner fact or an explicit hold.

## Writing observation

`writing_observation_mode` is true in `knowledge/polar_operator.yaml`.

For every nontrivial free-response question, write a `writing_log` row with company, role, exact question, answer used, and a short evidence note. Regular answers may still submit when the facts support them. Prioritized answers must be logged before Submit.

The point is 10 to 20 real examples Junyi can use to improve the writing policy.

## Authentication and blockers

A required new application account is normal execution.

Attempt ordinary user-facing completion for account creation, a browser-generated strong password, saved credentials, forgot-password, email verification, email OTP, SMS on the Mac, ordinary consent, multi-page forms, unknown widgets, and required writing.

Use only normal browser flows for security or anti-abuse challenges. Do not implement CAPTCHA-bypass services, fingerprint spoofing, or anti-abuse evasion.

Escalate to `BLOCKED` only after this local environment cannot complete a required step. Persist the blocker. Continue to the next READY job.

## Two Submit planes

`docs/policy/SUBMIT_ROLLOUT.md` now separates `cursor_cloud` gates from `polar_local` gates.

Cloud Computer Use still uses ATS-family gates in `config/submit_gates.yaml`. Those gates stay because that is the evidence we have for cloud Chrome. G2 stays closed there.

Polar Local uses capability and policy checks. A regular job may be submitted once when the duplicate check passes, company and title match, the correct resume is attached, identity is correct, required facts are resolved, no unsupported claim was invented, writing is evidence-grounded, weight is regular, final review passes, one Submit is used, and the result is verified or marked `SUBMISSION_UNKNOWN`.

Initial canary caps live in `knowledge/polar_operator.yaml` and `config/submit_gates.yaml` `polar_local`:

- 3 new jobs per `apply-ready-jobs` run (shared pool; priority reservation is taken from it)
- 10 regular submissions per local calendar day in America/New_York

Junyi can raise those caps after production evidence is good.

## Workflows

Do not merge these into one giant Workflow. Saved Polar Workflows store only the thin bootstrap in `docs/automation/POLAR_WORKFLOWS.md`.

| Workflow | Eastern Time | Polar mode |
|---|---|---|
| `discover-jobs-hourly` | minute 00 every hour | Saved Workflow on the named local profile. Discovery and queue only. Takes the browser lease. |
| `apply-ready-jobs` | minute 20 every hour | Saved Workflow on the same profile. Execution with the run cap. Takes the browser lease. |
| `daily-job-summary` | 21:30 daily | Saved Workflow. Queue read and one email. No application clicks. No browser lease. |
| `production-learning-daily` | 22:00 daily | Saved Workflow. Sanitized learning report. No application clicks. No browser lease. |

`polar-github-write-canary`, `chatgpt-production-review`, and `cursor-production-maintenance` exist as compiled instructions. They stay manual until the write path is proven. Phase 3 stops before merge.

## Cloud discovery stays as shadow

Do not disable the existing Cursor Automation on day one.

For the first 48 hours after Polar hourly discovery is actually running:

- Polar hourly discovery is the production candidate.
- Cloud morning and evening discovery is shadow and fallback.

Compare jobs found by both, jobs only Cloud found, jobs only Polar found, duplicate rate, latency, false KEEP or SKIP, and employer URL resolution.

The checklist is `docs/automation/POLAR_SHADOW.md`.

Keep Cloud as fallback, reduce it, or retire it only after that evidence exists.

## Locked-screen scheduler test

Before overnight autonomous Submit, run `polar-scheduler-heartbeat`.

The Workflow opens a harmless page and writes one `heartbeat` row while Polar is backgrounded, the screen is locked, and the Mac stays powered and online.

Do not assume sleep or lock behavior. Record the result before raising overnight Submit confidence.

## Environments

`cursor_cloud` and `polar_local` do not share cookies.

Cursor Cloud Agents and the daily discovery Automation run in a fresh checkout. They do not see Junyi's laptop sessions. `secrets/jobright_storage.json` is gitignored and has been absent from every recent cloud discovery pack.

Polar sees the local browser. That is why Original Job Post and ordinary auth are available there.

Polar's May 2026 product note says Polar is macOS only for now ([A New Interface for Composer](https://polarbrowser.com/blog/new-interface)). Do not assume a Windows Polar exists.

Cloud Computer Use still uses `scripts/compile_cu_task.py` on cloud Chrome. Do not wrap Polar inside a `computerUse` Task.

## Proven versus unproven

| Claim | Kind | Status |
|---|---|---|
| Polar runs locally, logged in as Junyi | owner-observed | Proven 2026-09-04 |
| Polar can start from a Jobright URL, use Original Job Post, and reach employer applications | owner-observed | Proven across several jobs |
| Polar filled one real application in the first pilot | owner-observed | Proven 2026-09-04 |
| Polar filled Quantbot Greenhouse and stopped before Submit | Polar report, 2026-09-04 | Proven. About 6 minutes. No CAPTCHA. |
| Polar reached Rakuten Rewards Workday | Polar report P-20260904-002 | Proven land. Create Account wall. submitted=no. |
| Polar filled Solidigm SmartRecruiters and stopped before Submit | Polar report P-20260906-001 | Proven. Guest Easy Apply. About 6 minutes. submitted=no. P1 open. |
| Polar reached Citadel custom careers | Polar report P-20260906-002 | Proven land. Fill partial. Two Yes/No prompts have no approved answer. |
| Polar completed a real Grainger / SAP SuccessFactors application after an earlier auth experiment | owner-observed, 2026-09-08 | Proven only as that high-level success. No detailed report is in this repo. Do not invent steps. |
| Workflow exists and can use a named profile, saved instructions, attachments, and an hourly schedule | owner-observed. Public press agrees. | Proven as a product capability |
| Junyi will leave the Mac powered and online | owner-observed | Stated 2026-09-08 |
| Polar Workflow can consume `POLAR_RUNTIME` from a raw GitHub URL unattended | inference | Unproven |
| Polar Workflow writes the Google Sheet while the screen is locked | inference | Unproven until the heartbeat test |
| Polar hourly discovery matches Cloud discovery quality | inference | Unproven until the 48-hour shadow |
| Every Original Job Post is an employer ATS | inference | Unproven |
| Polar can write `apply_attempts.csv` without a human | inference | Unproven |
| Daily Cursor Automations can use Polar sessions | inference | False unless someone runs Polar locally |

## Pilot history

Do not delete the Quantbot, Rakuten, Solidigm, Citadel, or P1 evidence.

The first land-only packet was Tallgrass. The first fill-and-stop was Quantbot Greenhouse. Experiment 2 was Rakuten Rewards. The ATS sweep results are `generated/polar/results/P-20260906-001.md` and `generated/polar/results/P-20260906-002.md`. Ledger ids already minted on that lineage stay. Do not mint a second Quantbot id.

`generated/polar/LIVE.md` remains a mailbox for a single pasted job. Production no longer depends on that mailbox.

G2 stays closed on the Cursor Cloud plane.
