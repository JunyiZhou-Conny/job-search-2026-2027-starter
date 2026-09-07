# Evidence index

Every significant claim I am willing to show Polar. Types are closed.

- `directly_measured` means a count or timing from a named artifact.
- `owner_observed` means I reported a live Polar or laptop fact.
- `repository_verified` means the file or commit exists as described.
- `public_polar` means Polar's own site or post.
- `architectural_inference` means a boundary we chose.
- `hypothesis` means a plausible cause that is not isolated.
- `unknown` means the repo cannot answer it.

Do not upgrade a lower type. A Polar engineer should be able to open
the source and see the same sentence I used.

Polar fill packets from sibling branches are copied onto this branch
so a reviewer does not need those remotes. Original commits remain
`ed40f98` and `b49d073`.

## Claim list

### C001. Twitch three-pass Computer Use cost

- claim: Three Computer Use passes on one Twitch Greenhouse form took about 74 minutes, 195 CU actions, 129 scrolls, and 12 type or key actions.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-09-03_twitch_cu_cost.md
- date: 2026-09-03
- confidence: high
- does_not_prove: That every Computer Use form costs this much. That the unpublished computer-use system prompt is the sole cause. That Polar is faster on the same form. The counter script was `/tmp/analyze_cu_transcripts.py` and is not in git. Re-count needs the original transcripts.

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

### C004. computerUse children start clean

- claim: Four isolation Submit children each had one user message, 1147 to 2395 characters, no AGENTS.md or knowledge files in the stored transcript.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-08-24_computer_use_context_isolation.md
  - knowledge/form_strategy.yaml
- date: 2026-08-24
- confidence: high
- does_not_prove: The contents of Cursor's unpublished computerUse system prompt. The file says not to ask a child to dump it. It also does not prove a later parent will copy standing rules without being told. The four child transcripts are not stored in git. The table is the surviving measurement.

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

- claim: 10 of 10 resolved postings autofilled, median 44 percent of visible fields, nothing submitted, and all 55 keeps on main pointed at Jobright pages that could not be applied on without an account. 15 of 55 keeps resolved exact on a public board.
- evidence_type: directly_measured
- sources:
  - docs/experiments/2026-07-31_apply_trial.md
- date: 2026-07-31
- confidence: high
- does_not_prove: Current keep-list coverage. The 27 percent figure is that day's 55 keeps. Greenhouse coverage is a floor because custom widgets often lack a DOM value.

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
- does_not_prove: Polar's internal roadmap priority. Blog order is not a hiring rubric.

### C012. Polar names device-bound auth and datacenter IPs

- claim: Polar's Frontier Problems cloud-agents section says 2FA/SSO/passkeys are increasingly device-bound, many sites ban datacenter IPs, and for now agents must run on user devices to do long-running tasks.
- evidence_type: public_polar
- sources:
  - https://polarbrowser.com/blog/frontier-problems
- date: 2026-08-18
- confidence: high
- does_not_prove: That Polar has solved those constraints. Polar presents them as open problems.

### C013. Polar Quantbot fill report

- claim: On 2026-09-04 Polar reported using Jobright Original Job Post, landing on a Quantbot Greenhouse embed, running Simplify Autofill once, applying listed corrections, remaining unsubmitted, and taking about 6 minutes.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-09-04_polar_first_pilot.md
- date: 2026-09-04
- confidence: medium
- does_not_prove: Independent observation. Cursor did not watch the browser. The writeup says the facts are Polar's report. It does not prove Polar bypasses ATS bot detection. It does not prove Workflow or any other ATS family. One work-authorization widget was mapped to sponsorship No and marked needs_review.

### C014. Polar Rakuten Workday reach

- claim: Polar reported leaving Jobright, landing on rakuten.wd1.myworkdayjobs.com for Platform Engineer in San Mateo, then stopping on Create Account / Sign In after about 4 minutes, submitted=no.
- evidence_type: owner_observed
- sources:
  - docs/experiments/2026-09-04_polar_second_pilot.md
  - docs/experiments/polar_ats_matrix.md
- date: 2026-09-05
- confidence: medium
- does_not_prove: A Workday fill. The matrix records reach, not fill. It does not prove Polar can register or should register.

### C015. Polar is a second execution environment, not a second system

- claim: This repo treats Polar as local browser execution after Cursor has already named the job. Polar must not redo discovery or own the ledger.
- evidence_type: architectural_inference
- sources:
  - docs/automation/POLAR.md
  - docs/platforms.md
- date: 2026-09-04
- confidence: high
- does_not_prove: That Polar the product agrees with this boundary. POLAR.md says the boundary is ours.

### C016. One Polar fill was not flagged like some cloud submits

- claim: I filled a real application with Polar and that test was not flagged the way some cloud-browser submits were.
- evidence_type: owner_observed
- sources:
  - docs/automation/POLAR.md
- date: 2026-09-04
- confidence: low
- does_not_prove: That Polar evades ATS spam filters. POLAR.md already forbids that upgrade. The flagged cloud case and the Polar case are not a controlled pair.

### C017. Exact hour I first read Frontier Problems

- claim: Unknown.
- evidence_type: unknown
- sources:
  - docs/automation/POLAR.md
- date: unknown
- confidence: low
- does_not_prove: Anything about motive. Use C010 for the git chronology instead.

### C018. Fair Computer Use versus Polar comparison

- claim: This repository does not contain a same-form, same-stop-rule, dual-instrumented comparison of cloud Computer Use and Polar.
- evidence_type: repository_verified
- sources:
  - polar/DEMO.md
  - polar/NEXT_EXPERIMENTS.md
- date: 2026-09-07
- confidence: high
- does_not_prove: That Polar is faster or more accurate. Any 6-minute versus 74-minute contrast in conversation is informal.

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
