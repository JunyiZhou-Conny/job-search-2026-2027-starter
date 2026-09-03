# Reality map, 2026-09-03

Evidence-backed reconstruction of this repository before any redesign.
Written by the coordinator agent that took ownership on 2026-09-03.
Every claim carries a pointer. `VERIFIED` means read or run. `INFERRED`
means a conclusion from verified facts. `UNKNOWN` means the repo cannot
answer it. Full archaeology reports were produced read-only from four
subagents and are summarized here; their rerunnable levers are noted.

Decision trail for this takeover lives in `docs/state/decisions.tsv`.

## 1. Current `main`

`main` is `28bd317` (PR #60, 2026-08-23). 79 commits since 2026-07-20.
55 tests pass. `validate_data.py` exits 0 with 7 errors (applied rows
missing `resume_version`) and 8 warnings. VERIFIED.

What `main` owns today.

| Subsystem | Files | State |
|---|---|---|
| Discovery scrape and merge | `scripts/automation/{export_board_lists,export_jobright_discovery,merge_discovery,run_discovery}.py` | Working. Runs headless without credentials except Jobright Matches. |
| Triage | `docs/automation/DAILY_JOB_DISCOVERY.md`, `knowledge/discovery_triage_rules.yaml`, `scripts/triage_discovery.py` | Working. The agent decides keep/later/skip per row; scripts only pack. |
| Apply URL resolution | `scripts/resolve_apply_url.py`, `knowledge/careers_boards.yaml` | Working. Coverage 8 to 53 percent of keeps per run, capped by ATS families with public APIs. |
| Apply queue web app | `scripts/{generate_apply_queue,serve_apply_queue,queue_writeback}.py` | Built, tested, never used. Zero `status_change` events in the log. |
| Application ledger | `data/applications.csv` (34 rows), `data/job_decisions.csv` (1 row), `data/activity_log.csv` (38 rows), `scripts/js_lib.py` | Working schema. Stale since 2026-07-26 except two 08-23 rows. |
| Simplify import | `scripts/jobsearch.py import-simplify`, `data/imports/simplify/` | Works. Last export 2026-07-26. |
| Resume variants | `resumes/{base,cloud_swe,data_ml,health_ai}`, `data/resume_versions.csv` | Files exist at v1.2. Registry points at deleted v1.1 files. |
| Knowledge | `config/profile.yaml`, `knowledge/*.yaml` | Only 4 of 11 files are read by code. The rest are prose for the model. |
| Apply harness check | `scripts/automation/check_apply_harness.py` | Working. Exits 0 on the personal environment, 1 elsewhere. |
| Collaborator fork tooling, friends showcase | `scripts/init_personal_copy.py`, `docs/collaborators/`, `docs/FRIENDS_CANVAS.md` | Working, unrelated to applying. |
| Calendar, daily plan, analytics, networking | `scripts/generate_*.py`, `data/{contacts,networking*}.csv` | No data behind them since 2026-07-26. |

Source. `/tmp/archaeology/01_main_inventory.md` and its lever `inventory.py`.

## 2. Important historical branches

101 remote branches. Two unmerged stacks carry all post-08-23 work.

Stack A, the apply and Ashby lineage. `main` > #61 `ten-tab-round-two` >
#62 `priority-why-us-and-referrals` > #65 `ashby-submit-isolation` >
#66 `ashby-three-trivial-submits` > #67 `fifo-over-referral-hold` >
#68 `form-rules-notion-perplexity` > #69 `computer-use-context-isolation`.
Tip `c9cada8`, 31 commits, 44 files, +2601 lines. All PRs open. VERIFIED
by `gh pr view` base fields and merge-base containment.

Stack B, the Grok bot management lineage. `main` > #73
`grok-bot-management-docs` > #75 `grok-shared-computer` (with #76, #82,
#84 merged into it, not into `main`) > #86 `autofiller-git-loop` >
`ashby-page-session-restore`. Side branches hold an org chart designer
web tool (#79 and three follow-ups) and #77. Tip 17 commits, 17 files,
+2359 lines, documentation plus three prose-checking scripts.

Independent small branches. #74 `form-strategy-aug25` (GPA, personal
website, discipline, any-employer answer), #83
`form-strategy-clicker-cheap-cuts` (disability_status No, clicker cuts),
#64 `pathology-rlvr-experience` (evidence bank entry, v1.3 resumes),
#70 `add-verifier-subagent` (`.cursor/agents/verifier.md`), #51 closed
(superseded by merged #50).

Discovery output. 68 `discovery-triage-loop-*` branches from two
enabled Cursor Automations (13:0x UTC and 22:0x UTC). 21 merged, 26
closed, 19 open and individually mergeable but pairwise conflicting on
`knowledge/careers_boards.yaml`. Nothing merged since 2026-08-23.

## 3. Currently working components

- Discovery scrape, merge, and triage. 68 runs over 39 days, no day
  missed, 85 to 93 percent of rows under one day old by
  `posted_relative`. VERIFIED by `/tmp/archaeology/analyze_discovery.py`.
- Apply URL resolver. All five sampled keep URLs in the latest run are
  employer ATS pages (Greenhouse, Workday). VERIFIED by `curl -sI`.
- Apply harness on the personal environment
  `41a15b57-8916-11f1-b532-320a589b8025`. Branded Chrome, Simplify
  Copilot `pbanhockgagggenencehbnadejlgchfc`, live Simplify session as
  Junyi Zhou. VERIFIED 2026-09-03 by `check_apply_harness.py` and a
  browser probe (`/opt/cursor/artifacts/probe/*.png`).
- Ledger schema and validators. `js_lib.py`, `validate_data.py`, 55
  tests.
- Copilot identity autofill on Ashby and Greenhouse. 07-31 trial median
  44 percent of fields, identity and resume reliable on 9 of 10 tabs on
  08-22. VERIFIED from experiment docs.
- One-tab Ashby Cloud Submit. 4 of 4 landed on 2026-08-24 (see section 5).

## 4. Abandoned or dormant components

- Apply queue web app. Built 07-31, never wrote to `main`. INFERRED from
  zero `status_change` events.
- Weekday apply Automation. Design only, never enabled
  (`WEEKDAY_APPLY_AUTOMATION.md:3` on Stack A).
- Networking, contacts, outreach, calendar, daily plan, analytics.
  Header-only CSVs and 2026-07-26 artifacts.
- Grok bot organization. Prose only. No ledger row, screenshot, or log
  shows a Grok bot ran. The one recorded event is a report-and-stop
  failure (`docs/grok-bot-management/ALIGNMENT.md:16-18` on Stack B).
- Org chart designer tool. Runs, 17 tests, tangent.
- Jobright Matches personalized feed. Needs `secrets/jobright_storage.json`,
  absent in every cloud run.
- `jobs/inbox/README.md` describes a JD drop workflow that has no files.

## 5. Actual successful experiments

| Date | Experiment | Result | Evidence |
|---|---|---|---|
| 07-31 | Apply trial, 10 postings, Chromium plus unpacked Copilot | 10 of 10 autofilled, median 44 percent fields; resolver born | `docs/experiments/2026-07-31_apply_trial.md` |
| 08-21 | Harness snapshot clone | `ready: true` on three boots, Copilot and cookie survive | `docs/experiments/2026-08-21_harness_snapshot_clone.md` |
| 08-22 | Ten-tab Copilot review | Identity on 9 of 10; found EEO and work-auth misfills; stop-the-line table | `docs/experiments/2026-08-22_ten_tab_copilot_review.md` |
| 08-24 | Anyscale isolation Submit, dashboard agent, one tab, Autofill once, Submit once | Ashby success banner plus Simplify overlay | Stack A `docs/experiments/2026-08-24_ashby_submit_isolation.md:189-200` |
| 08-24 | Three trivial Ashby Submits (Meshy, Midjourney, cfo.ai), one tab each | 3 of 3 success banners; ledger J20260824-002/003/004 | Stack A `docs/experiments/2026-08-24_ashby_three_trivial_submits.md:60-64` |

Caveat on every success. The evidence is a page banner plus a Simplify
overlay. No Ashby application id or archived confirmation email exists in
git. Simplify's tracker shows these rows as Applied (browser probe
2026-09-03). Post-submit review by the employer is UNKNOWN.

## 6. Actual failed experiments

| Date | Experiment | Failure | Evidence |
|---|---|---|---|
| 08-18 | Ten-tab review on a fresh Cloud Agent | No Copilot on the VM; Greenhouse "Autofill" was MyGreenhouse | `docs/experiments/2026-08-18_ten_tab_review.md:40-45` |
| 08-23 | Ten-tab round two | Four sponsorship widgets flipped wrong way; Run Autofill Again wiped corrections; typed Why-us drafts later rejected as project dumps | Stack A `docs/experiments/2026-08-23_ten_tab_round_two.md:76-110` |
| 08-24 | Charta Cloud Chrome Submit from the round-two parent session (many tabs, retries, long Why-us) | "flagged as possible spam", nothing landed. Junyi then submitted from his laptop. No confirmation captured. No ledger row. | Stack A `docs/apply/OBSTACLES.md:281-285`, `data/activity_log.csv:60-61` |
| 08-24 | Anyscale run 1 as a nested `Task environment=cloud` child | `not_run`. Child had the harness but no `computerUse` tool. | Stack A isolation doc lines 104-141 |
| 08-25 | Grok bot chief given a research-only paste | Wrote a report and stopped. Obedience, not a bug. | Stack B `ALIGNMENT.md:16-18` |

Never run. Charta re-test from a fresh pod. A long-form Ashby Cloud
Submit. Any Greenhouse, Lever, or Workday Submit from Cloud. The
parent-compiler test for computer-use context
(`2026-08-24_computer_use_context_isolation.md:28-45`).

## 7. Contradictions between policies

1. Submit. `AGENTS.md:13` and every layer say never Submit without
   explicit confirmation. Four Cloud Submits were authorized by chat and
   landed on 08-24, recorded only on Stack A. The current owner brief
   wants autonomous Submit for regular roles once proven and human
   review for high-value roles. The old blanket ban is superseded as
   policy, not as a fact about the ledger.
2. Prioritized rows. Stack A says prioritized means public Submit when
   ready, FIFO over referral hold (`docs/apply/PRIORITY.md:11-15,47-52`).
   The owner brief says prioritized means human review before Submit.
   The FIFO argument survives for regular rows only.
3. Referral hold. Created 22aaf12, retired e90c733, yet
   `docs/eligibility.md:42-43`, `.cursor/rules/06-networking.mdc:23-24`,
   and `docs/apply/OBSTACLES.md:235-237` on Stack A still say hold.
4. Sponsorship widget. Main's `work_authorization.yaml:45-47` answers the
   broad question Yes and `eligibility.md:50` forbids answering No to
   bypass ATS. Stack A flips the standing answer to "No, I do not need
   sponsorship" (`form_strategy.yaml:26-44`) and sets
   `never_lie_to_bypass_ats: false`, while the fact
   `future_sponsorship_required: true` stays in both files. This is a
   fact-versus-form-answer conflict and needs the owner's word.
5. Applied means confirmed. `docs/workflow.md:22` says confirm before
   `applied`; `.cursor/rules/12-application-records.mdc:41` lets an apply
   queue click write `applied`.
6. Status enums are defined four ways (`status-definitions.md`, rule 12,
   `js_lib.py`, data) and `js_lib` accepts both old and new sets.
7. Resume default. `profile.yaml:26` says dual-date resume is default;
   `profile.yaml:115`, `README.md:82-84`, `eligibility.md:40` say
   December 2026 is default.

## 8. Contradictions between the owner's memory and repository evidence

- "Cloud agents cannot submit Ashby" is not supported. One rejection
  (Charta, parent session, many tabs, retries) versus four acceptances
  (one tab, new pod, one click, four tenants). No variable was isolated
  and Charta was never re-tested.
- "Ashby automation is solved" is not supported either. Every success is
  a short identity-only form. No long-form, no free response, no
  Greenhouse or Workday Submit has ever been attempted from Cloud.
- The only application the owner actually wanted from that session,
  Charta, has no `applications.csv` row and no captured confirmation.
- Simplify's tracker holds five applications dated 2026-08-25 (AppLovin,
  Tensortrent, Cilera, Kodiak Robotics, Advanced Space) that no branch
  records. The two memories have drifted since 08-24. VERIFIED by probe.
- The 07-31 trial's blocking finding (keeps are unactionable without an
  employer URL) is still true. The resolve step ran on 4 of 24 triage
  days on `main`.
- The computer-use context isolation "finding" is a transcript
  observation, not a run experiment. It is consistent with Cursor docs.
- Copilot and the repo are two memory systems and have already
  disagreed on the form. Copilot autofilled "Harvard University" as
  current company on Anyscale; the repo says student, leave empty.

## 9. Architecture boundaries that look healthy

- Discovery never writes the ledger. Scrapers, merge, and triage produce
  `generated/` artifacts; ingest is a gated separate step. The boundary
  held for 39 days.
- The harness checker fails closed and never prints secrets.
- Queue write path is one module with an undo journal and tests.
- Fork tooling refuses to run on upstream.
- Rules in git, prompts point at them (`UI_POINTER.md` pattern). The Grok
  stack independently arrived at the same mechanism plus "leftovers
  return as proposed rules, human confirms".
- One tab, Autofill once, targeted corrections, Submit once, no retry.
  This protocol produced the only four verified Submits.

## 10. Architecture boundaries that repeatedly caused friction

- Application state has three writers (queue, Simplify import, CLI) and
  two homes (`applications.csv.status` and `job_decisions.csv`), with
  Simplify declared ledger of record but never reconciled by code.
- Knowledge is prose copied by hand into rules, commands, automation
  docs, README, and `AGENTS.md`. The same fact appears in up to five
  places and has already diverged (sections 7.4, 7.7). Nothing lints it.
- `form_strategy.yaml` grew 22 blocks on Stack A of which four are
  experiment logs or agent-mechanics retrospectives, and nine
  `autofill_obstacles.yaml` gap rows only point back at it.
- Day-keyed discovery filenames make the two daily runs destructive to
  each other, and `careers_boards.yaml` is re-appended every run.
- PR-per-run delivery for discovery depends on a weekly human batch
  merge that stopped on 08-23.
- Nested `Task environment=cloud` children have no `computerUse`; only a
  dashboard-launched agent can click. Any apply orchestration must run
  the clicker as a `computerUse` subagent of a first-class agent and
  compile the standing rules into the Task string.
- The harness is Junyi's live session on a snapshotted environment.
  `identity_match` is never verified by code. Safe under a no-Submit
  gate, dangerous once Submit is autonomous, so identity must be checked
  at run start.
- Verification stops at the banner. No independent channel (email,
  application id) is wired. Outlook MCP is present but `needsAuth`.

## 11. Smallest high-value next experiment

Consolidate first, then prove one real unit.

1. Land the durable knowledge, experiment history, and ledger rows from
   Stack A onto `main` with the four ledger corrections the archaeology
   found, and retire stale hold and blanket-ban text. This PR.
2. Fix discovery delivery (run-stamped artifacts, sorted
   `careers_boards.yaml`, single delivery branch). Separate PR, in
   flight.
3. Encode the application lifecycle as one state machine with an
   idempotency key and a verification record, and record the four 08-24
   Submits under it.
4. Run one real regular-lane Ashby application end to end from a fresh
   discovery keep: resolve URL, check identity, one tab, Autofill once,
   corrections from repo knowledge, validator screenshot, Submit once,
   verify banner plus Simplify tracker, write the ledger, rerun and show
   no duplicate. This extends the proven envelope (4 of 4 trivial forms)
   to a wanted role under the same protocol. Long-form, Greenhouse, and
   prioritized rows stay behind human review until this unit is green.

Rollout ladder (policy, supersedes the blanket ban).

| Gate | Condition to open | Current |
|---|---|---|
| Fill only | harness ready | open |
| Fill plus human review | identity check at run start, stop-the-line table | open |
| Limited autonomous regular Submit | Ashby, one tab, no required free response or answer from the approved bank, sponsorship question absent or H-1B-named, cap 3 per run, banner plus a durable second signal, ledger row before next job | closed until unit 4 is verified (`config/submit_gates.yaml`) |
| Broader regular automation | 10 consecutive verified regular Submits with zero wrong-fact incidents, one independent channel (email or application id) wired | closed |
| Prioritized rows | human review packet before Submit, always | policy |
