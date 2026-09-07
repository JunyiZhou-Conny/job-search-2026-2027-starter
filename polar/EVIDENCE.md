# Evidence index

Every significant claim I am willing to show Polar. Types are closed.

- `directly_measured` means a count or timing from a named artifact.
- `owner_observed` means I watched or reported a live laptop or
  cloud-agent fact.
- `executor_self_report` means Polar or another executor wrote the
  result. Cursor did not independently observe it.
- `repository_verified` means the file or commit exists as described.
- `public_polar` means Polar's own site or post.
- `architectural_inference` means a boundary we chose.
- `hypothesis` means a plausible cause that is not isolated.
- `unknown` means the repo cannot answer it.

Do not upgrade a lower type. A Polar engineer should be able to open
the source and see the same sentence I used.

Polar fill packets from sibling branches are copied onto this branch.
Original commits remain `ed40f98` and `b49d073`. The Rakuten Polar
report is `generated/polar/results/P-20260904-002.md`. Live Slot
machinery on the scale-stage branch is still not here.

## Claim list

### C001. Twitch three-pass Computer Use cost

- claim: Three Computer Use passes on one Twitch Greenhouse form took about 74 minutes, 195 CU actions, 129 scrolls, and 12 type or key actions.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-09-03_twitch_cu_cost.md
- date: 2026-09-03
- confidence: medium
- does_not_prove: That every Computer Use form costs this much. That the unpublished computer-use system prompt is the sole cause. That Polar is faster on the same form. That 195 actions were one child. The total includes a deliberately read-only 43-call pass. The counter script was `/tmp/analyze_cu_transcripts.py` and is not in git. Re-count needs the original transcripts.

### C002. Twitch parent prompts invited the loops

- claim: The G1 fill, correction, and read-only parent Task strings asked for fill-and-review, verify-each-widget, report-every-question, and scroll-only distant facts.
- evidence_type: repository_verified
- sources:
  - docs/experiments/2026-09-03_twitch_cu_cost.md
  - tests/fixtures/computer_use/twitch_g1_fill.txt
  - tests/fixtures/computer_use/twitch_correction.txt
  - tests/fixtures/computer_use/twitch_verify.txt
- date: 2026-09-03
- confidence: high
- does_not_prove: That a different parent prompt on the same day would have been cheap. The experiment did not A/B the prompt against a compiled sheet on Twitch.

### C003. Compiler rejects the Twitch prompts

- claim: `scripts/compile_cu_task.py lint` flags those Twitch fixtures, and unit tests require those hits.
- evidence_type: repository_verified
- sources:
  - scripts/compile_cu_task.py
  - tests/test_compile_cu_task.py
- date: 2026-09-03
- confidence: high
- does_not_prove: That later parents always compile. Lint only catches strings that match the regexes.

### C004. Isolation stored transcripts omit parent rule files

- claim: Four isolation Submit children each left a stored transcript with one user message, 1147 to 2395 characters, and no AGENTS.md or knowledge files in that file.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-08-24_computer_use_context_isolation.md
  - knowledge/form_strategy.yaml
- date: 2026-08-24
- confidence: high
- does_not_prove: Runtime context the child actually received. Cursor's unpublished computerUse system prompt is not in the stored file. The designed parent-compiler follow-up was never run. The four child transcripts are not stored in git. The table is the surviving measurement.

### C005. Nested cloud Task can lack computerUse

- claim: Child bc-7f8a7941 booted the personal apply environment with harness ready and computerUseSupported false, so the Anyscale isolation Submit was not_run.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-08-24_ashby_submit_isolation.md
- date: 2026-08-24
- confidence: high
- does_not_prove: That every nested cloud Task lacks computerUse forever. It proves that class of child, on that day, could not click.

### C006. One-tab Ashby Cloud Submit can succeed

- claim: A dashboard Cloud Agent submitted Anyscale Software Engineer (Ray Core) once on 2026-08-24 and the page showed an Ashby success banner plus a Simplify overlay. Three later short Ashby forms also showed success banners.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-08-24_ashby_submit_isolation.md
  - docs/experiments/2026-08-24_ashby_three_trivial_submits.md
  - docs/state/REALITY_MAP.md
- date: 2026-08-24
- confidence: medium
- does_not_prove: Mass apply safety. Long-form Ashby. Greenhouse or Workday Submit from cloud. An Ashby application id. That cloud Submit is reliable. REALITY_MAP says no application id or confirmation email is in git.

### C007. Charta cloud Submit was flagged as possible spam

- claim: Cloud Chrome Submit on Charta returned "We couldn't submit your application. Your application submission was flagged as possible spam." and did not create an application.
- evidence_type: owner_observed
- sources:
  - knowledge/form_strategy.yaml
  - docs/apply/OBSTACLES.md
  - docs/experiments/2026-08-24_ashby_submit_isolation.md
- date: 2026-08-24
- confidence: high
- does_not_prove: That Ashby blocks all datacenter IPs. The isolation doc lists many variables that were not isolated. I then submitted from my laptop. That laptop submit is not captured as a confirmation artifact in the isolation file.

### C008. July 31 autofill trial coverage and Jobright wall

- claim: 10 of 10 resolved postings autofilled, median 44 percent of visible fields, nothing submitted. All 55 keeps on main pointed at Jobright URLs. The signup wall was reproduced on the first two keeps tried. 15 of 55 keeps resolved exact on a public board.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-07-31_apply_trial.md
- date: 2026-07-31
- confidence: high
- does_not_prove: That all 55 Jobright pages were opened. Only 2 of 2 tested pages showed the signup wall. Current keep-list coverage. The 27 percent figure is that day's 55 keeps. Greenhouse coverage is a floor because custom widgets often lack a DOM value.

### C009. Run Autofill Again can wipe corrections

- claim: After computer-use corrected sponsorship or similar widgets, a later Simplify Run Autofill Again cleared Yes dropdowns and flipped Baseten sponsorship back to No.
- evidence_type: owner_observed
- sources:
  - knowledge/form_strategy.yaml
  - docs/experiments/2026-08-23_ten_tab_round_two.md
- date: 2026-08-23
- confidence: high
- does_not_prove: That Copilot is generally unsafe. It proves a second Autofill is not a safe "refresh."

### C010. Polar first appears in this repo on 2026-09-04

- claim: The first Polar execution-plane essay on this line of history is commit 678a320, dated 2026-09-04. Earlier apply and Computer Use experiment files do not mention Polar.
- evidence_type: repository_verified
- sources:
  - docs/automation/POLAR.md
- date: 2026-09-04
- confidence: high
- does_not_prove: The hour I first read Polar's blog. That date is unknown. It only proves Polar is absent from the earlier experiment writeups.

### C011. Polar Frontier Problems publication date

- claim: Polar published Frontier Problems on 18 August 2026 and asks candidates to email hiring@polarbrowser.com with the 2-3 most extraordinary things they have done.
- evidence_type: public_polar
- sources:
  - https://polarbrowser.com/blog/frontier-problems
  - https://polarbrowser.com/blog
- date: 2026-08-18
- confidence: high
- does_not_prove: Polar's internal roadmap priority. Blog order is not a hiring rubric. The checker does not fetch this URL.

### C012. Polar names device-bound auth and datacenter IPs

- claim: Polar's Frontier Problems Future products Cloud agents bullet says 2FA/SSO/passkeys are increasingly device-bound, many sites ban datacenter IPs, and for now agents must run on user devices to do long-running tasks.
- evidence_type: public_polar
- sources:
  - https://polarbrowser.com/blog/frontier-problems
- date: 2026-08-18
- confidence: high
- does_not_prove: That Polar has abandoned cloud agents. The same paragraph says there are workarounds, and that Polar wants to run in a cloud computer after nailing the AI browser. Cloud agents is not one of the eight named Frontier Problems. The checker does not fetch this URL.

### C013. Polar Quantbot fill report

- claim: On 2026-09-04 Polar reported using Jobright Original Job Post, landing on a Quantbot Greenhouse embed, running Simplify Autofill once, applying listed corrections, remaining unsubmitted, and taking about 6 minutes. Polar also reported mapping sponsorship No onto a different work-authorization widget and leaving that field needs_review.
- evidence_type: executor_self_report
- sources:
  - docs/experiments/2026-09-04_polar_first_pilot.md
- date: 2026-09-04
- confidence: medium
- does_not_prove: Independent observation. Cursor did not watch the browser. Screenshots and trajectory logs are not in git. This is a partial fill, not a proven Greenhouse fill. The pilot cites `visa_sponsorship.do_not_auto_map`, which is not a key in `knowledge/form_strategy.yaml`. It does not prove Polar bypasses ATS bot detection. It does not prove Workflow or any other ATS family.

### C014. Polar Rakuten Workday reach

- claim: Polar reported leaving Jobright, landing on rakuten.wd1.myworkdayjobs.com for Platform Engineer in San Mateo, clicking Apply once, then Workday Autofill with Resume, then hitting Create Account / Sign In. About 4 minutes. submitted=no. No form fields were reachable.
- evidence_type: executor_self_report
- sources:
  - docs/experiments/2026-09-04_polar_second_pilot.md
  - generated/polar/results/P-20260904-002.md
  - docs/experiments/polar_ats_matrix.md
- date: 2026-09-04
- confidence: medium
- does_not_prove: A Workday fill. Independent observation. Cursor did not watch the browser. The Rakuten result file is a normalized pasted report. Polar stopped after Workday's own Autofill control, not at the first Jobright click. It does not prove Polar can register or should register.

### C015. Polar is a second execution environment, not a second system

- claim: This repo treats Polar as local browser execution after Cursor has already named the job. Polar must not redo discovery or own the ledger.
- evidence_type: architectural_inference
- sources:
  - docs/automation/POLAR.md
  - docs/platforms.md
- date: 2026-09-04
- confidence: high
- does_not_prove: That Polar the product agrees with this boundary. POLAR.md says the boundary is ours.

### C016. Quantbot has no submit-time spam result

- claim: The named Polar fill (Quantbot) stopped before Submit. A fill that never hits Submit cannot be compared to Charta's submit-time Ashby spam wall.
- evidence_type: repository_verified
- sources:
  - docs/experiments/2026-09-04_polar_first_pilot.md
  - docs/automation/POLAR.md
- date: 2026-09-04
- confidence: high
- does_not_prove: That Polar evades or trips ATS spam filters. POLAR.md still contains the older one-test sentence. This dossier does not adopt it.

### C017. Exact hour I first read Frontier Problems

- claim: Unknown.
- evidence_type: unknown
- sources:
  - docs/automation/POLAR.md
- date: unknown
- confidence: low
- does_not_prove: Anything about motive. Use C010 for the git chronology instead.

### C019. Compiled Anyscale G1 wall time

- claim: On 2026-09-03 a compiled Computer Use bootstrap execute on Anyscale Ray Data took 3.4 minutes and 23 tool messages. A compiled 4-field correction execute took 5.7 minutes and 74 tool messages. Submit was not clicked.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-09-03_anyscale_g1_unit.md
- date: 2026-09-03
- confidence: medium
- does_not_prove: That the compiler caused the lower time versus Twitch. The file says the counts are not Twitch-style action taxonomy. Different ATS. No verify pass. Worker createdAt and tool-message logs are not in git. `expected_vs_observed.md` is a field audit and has no timings.

### C018. Fair Computer Use versus Polar comparison

- claim: This repository does not contain a same-form, same-stop-rule, dual-instrumented comparison of cloud Computer Use and Polar.
- evidence_type: repository_verified
- sources:
  - polar/DEMO.md
  - polar/NEXT_EXPERIMENTS.md
- date: 2026-09-07
- confidence: high
- does_not_prove: That Polar is faster or more accurate. Any 6-minute versus 74-minute contrast in conversation is informal.

### C020. computerUse cannot read a textarea DOM value

- claim: The Computer Use contract states that a computerUse child cannot read a textarea DOM value and must not prove a paste with Ctrl+F.
- evidence_type: repository_verified
- sources:
  - docs/automation/COMPUTER_USE_PROMPT.md
  - knowledge/form_strategy.yaml
- date: 2026-08-24
- confidence: high
- does_not_prove: Polar's tool surface. This is contract language from leftover-typing, not a Polar measurement.

### C021. Copilot identity fields versus work-authorization

- claim: On 2026-08-22, with the harness ready, Copilot filled name, email, phone, LinkedIn, and resume on the live employer tabs. Work-authorization, EEO, and some education widgets were wrong or unverified.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-08-22_ten_tab_copilot_review.md
- date: 2026-08-22
- confidence: medium
- does_not_prove: That identity fill is reliable on every ATS. The checker still reported identity_match unknown. Work-authorization is not in the reliable set.

### C022. Auth difference is session and provisioning, not locality

- claim: Daily cloud discovery lacked Jobright cookies. Original Job Post appeared in the tested logged-in local session. A later authenticated cloud snapshot kept Copilot and recorded four short Ashby Cloud Submits.
- evidence_type: repository_verified
- sources:
  - docs/automation/POLAR.md
  - docs/state/REALITY_MAP.md
  - docs/experiments/2026-08-21_harness_snapshot_clone.md
  - docs/experiments/2026-08-24_ashby_three_trivial_submits.md
- date: 2026-08-24
- confidence: high
- does_not_prove: That cloud can never do logged-in apply. That Original Job Post exists only on a laptop. That Polar is required for any authenticated session.

### C023. Discovery stretch on the 2026-09-03 reality map

- claim: REALITY_MAP dated 2026-09-03 records 68 discovery-triage runs over 39 days on an older main, with nothing merged since 2026-08-23.
- evidence_type: repository_verified
- sources:
  - docs/state/REALITY_MAP.md
- date: 2026-09-03
- confidence: high
- does_not_prove: A 39-day continuous browser agent. Those were short scheduled discovery runs that wrote artifacts and did not submit. The count is that snapshot, not a live metric.

## Ranking notes for the 2-3 stories

I ranked candidate stories on difficulty, originality, ownership,
evidence, depth, Polar relevance, non-obvious lesson, and whether I
can defend every sentence.

| Candidate | Keep? | Why |
|---|---|---|
| "I built an auto-apply system" | no | Generic. Hides the failures. Overstates Submit. |
| Observation-loop tax plus compiler | yes | Measured. Encoded. Polar-relevant. Defensible. |
| Context isolation plus parent compiler | yes | Directly answers agent-to-agent handoff. The follow-up test is still open, and I say so. |
| Control plane versus local Polar execution | yes | Architecture that failed into place. Polar packets are Polar-aware and labeled that way. |
| Four Ashby Cloud Submits | no as a headline | Real, but practice-lane identity forms. Easy to overclaim. Used as supporting evidence only. |
| CellOT, airway chatbot, S-Seg-RLVR | not in this packet | Real work in `knowledge/evidence_bank.yaml`. Different audience. This dossier is the browser-agent case. |

The three kept stories are one system seen at three seams. Tool budget,
context boundary, and environment. Collapsing them into one sentence
would hide the measurements.
