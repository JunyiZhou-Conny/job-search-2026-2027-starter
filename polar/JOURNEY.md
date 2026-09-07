# Journey

This is the technical chronology. Prefer attempt, failure, experiment,
result, then the change that landed in git.

Dates come from filenames, experiment bodies, or `git log --follow`.
Polar first appears in this repository on 2026-09-04. I do not treat
earlier work as Polar-inspired.

## 2026-07-26 to 2026-07-27. Local session export

**Attempt.** Pull Simplify without retyping every application.

**Observation.** Passwords and 2FA cannot live in git. The first local
path is a saved Chrome session on my Mac, then a CSV export.

**Change.** `docs/archive/local-browser-automation.md` and the discovery
pipeline. Auto-click Submit across ATS families is explicitly not in
scope.

**Kind.** repository-verified setup notes. Not a Polar experiment.

## 2026-07-31. First live apply trial

**Question.** How far can an agent get on a real form before a human is
needed.

**Method.** Ten resolved employer URLs. Headed Chromium plus unpacked
Simplify Copilot. Stop before Submit.

**Result.** 10 of 10 autofilled. Median 44 percent of visible fields, with
a stated caveat that Greenhouse custom widgets under-count. All 55 keeps
on `main` pointed at Jobright URLs. The signup wall was reproduced on the
first two keeps tried. Only 27 percent of 55 keeps resolved to a public
board API (`exact`).

**Change.** `scripts/resolve_apply_url.py` is born the same day. Autofill
is treated as the identity pass, not the whole application.

Source. [`docs/experiments/2026-07-31_apply_trial.md`](../docs/experiments/2026-07-31_apply_trial.md)

## 2026-08-18. Ten tabs, no Copilot

**Attempt.** Resume the July trial so a human can watch autofill.

**Failure.** The new Cloud Agent disk has no Copilot. Greenhouse's visible
Autofill control is MyGreenhouse, not Simplify.

**Change.** The apply harness becomes a first-class contract.
`docs/automation/APPLY_HARNESS.md` later states the three questions
separately. Software, session, identity.

Source. [`docs/experiments/2026-08-18_ten_tab_review.md`](../docs/experiments/2026-08-18_ten_tab_review.md)

Polar's Frontier Problems post is also dated 2026-08-18. That is a
calendar collision. This experiment file does not mention Polar.

## 2026-08-21. Snapshot the harness

**Question.** Can Copilot and the Simplify cookie survive a new pod.

**Result.** `ready: true` on the source disk and on two boots from its
snapshot. Cloud disks do not carry the harness unless someone
snapshotted them after a human login.

Source. [`docs/experiments/2026-08-21_harness_snapshot_clone.md`](../docs/experiments/2026-08-21_harness_snapshot_clone.md)

## 2026-08-22. Copilot on the same ten employers

**Result.** With the harness present, Copilot filled name, email, phone,
LinkedIn, and resume on the live tabs. Etched citizenship was a misfill.
Other work-authorization widgets were unverified or later reversed.
Essays stay empty. Nothing is submitted.

Source. [`docs/experiments/2026-08-22_ten_tab_copilot_review.md`](../docs/experiments/2026-08-22_ten_tab_copilot_review.md)

## 2026-08-23. Second ten-tab pass

**Result.** Copilot again fills identity. The standing sponsorship rule
that day was Yes. Computer-use flipped Copilot's No to Yes on four
broad widgets. Junyi reversed that standing answer to No on
2026-09-03. Copilot's No matches the current form answer. Relativity's
ITAR widget came back as U.S. Person and was corrected. Run Autofill
Again on a later pass wiped parent-set dropdowns.

**Change.** `do_not_run_autofill_again` in
[`knowledge/form_strategy.yaml`](../knowledge/form_strategy.yaml).
Country-named sponsorship is split from the US widget.

Source. [`docs/experiments/2026-08-23_ten_tab_round_two.md`](../docs/experiments/2026-08-23_ten_tab_round_two.md)

## 2026-08-24. Four findings in one day

### Charta spam wall

Cloud Chrome Submit on Charta returns "flagged as possible spam." The
click does not create an application. I then submit from my laptop.
Variables are not isolated. Home versus datacenter IP is not proven.

### Nested cloud child cannot click

A `Task environment=cloud` child boots the same personal environment.
`check_apply_harness.py` is ready. The tool catalog has no `computerUse`.
Outcome `not_run`.

### Isolation Submit on a dashboard agent

A fresh dashboard Cloud Agent, one Anyscale Ashby tab, Autofill once,
Submit once. Ashby success banner plus Simplify overlay. Three more
short Ashby forms later the same day also show success banners. These
are identity-only practice-lane forms. No Ashby application id is in
git. This is not a license for mass apply.

Sources.

- [`docs/experiments/2026-08-24_ashby_submit_isolation.md`](../docs/experiments/2026-08-24_ashby_submit_isolation.md)
- [`docs/experiments/2026-08-24_ashby_three_trivial_submits.md`](../docs/experiments/2026-08-24_ashby_three_trivial_submits.md)

### Context isolation

**Question.** Do computerUse children inherit the parent chat, `AGENTS.md`,
or `knowledge/*`.

**Result.** Four isolation Submit children. Each stored transcript is one
user message. No `system` role in the stored file. No `AGENTS.md`. Prompt
lengths 1147 to 2395 characters. That is the stored file, not a dump of
runtime context. The unpublished computer-use prompt is not in it.

**Change.** `computer_use_context_isolation` and
`leftover_typing_one_pass` in form strategy. The parent must compile the
clicker prompt. The file change itself cannot inject rules into the next
child.

Source. [`docs/experiments/2026-08-24_computer_use_context_isolation.md`](../docs/experiments/2026-08-24_computer_use_context_isolation.md)

The parent-compiler test named in that file was never run. See
[`NEXT_EXPERIMENTS.md`](NEXT_EXPERIMENTS.md).

## 2026-09-03. Twitch cost and the compiler

**Attempt.** Fill and review a Twitch Greenhouse form with Computer Use.
Do not Submit.

**Measurement.** Counted from fetched transcripts by
`/tmp/analyze_cu_transcripts.py`.

| Pass | Wall | CU calls | Scroll | Type/key |
|---|---|---|---|---|
| G1 fill | 23.3 min | 70 | 32 | 8 |
| Correction | 31.5 min | 82 | 56 | 4 |
| Read-only | 18.9 min | 43 | 41 | 0 |

Three passes. About 74 minutes, 195 Computer Use actions, 129 scrolls,
12 type or key actions. The correction pass needed a handful of
mutations and spent most of its time rereading.

**Cause recorded in the experiment.** The hidden computer-use prompt may
favor frequent observation. The parent Task strings invited the loops.

**Change.** `scripts/compile_cu_task.py` compiles an action sheet and
lints Task strings. The Twitch prompts are fixtures that must fail lint.
[`docs/automation/COMPUTER_USE_PROMPT.md`](../docs/automation/COMPUTER_USE_PROMPT.md)
states the contract. Parent is the brain. Computer Use is the hands.
One mode per spawn.

Same-day reality map
([`docs/state/REALITY_MAP.md`](../docs/state/REALITY_MAP.md)) records
that the isolation "finding" is a transcript observation, that Ashby
automation is not solved, and that Computer Use is now a compiled
sheet.

## 2026-09-03. Compiled Anyscale G1, still no Submit

**Attempt.** Use the new compiler on a regular Ashby role. Software
Engineer (Ray Data). Different posting from the 24 August Ray Core
Submit.

**Measurement.** Worker createdAt/updatedAt and tool-message counts.
Not the Twitch action taxonomy.

| Pass | Wall | Tool messages |
|---|---|---|
| Identity + Autofill once | 3.4 min | 23 |
| Corrections | 5.7 min | 74 |

**Result.** Form prepared. Parent checked screenshots in
`generated/apply_runs/2026-09-03T15/expected_vs_observed.md`. Submit
not clicked. G2 stays closed.

**What this does not prove.** That the compiler made Computer Use
cheap. Different ATS, different count method, no verify pass. The
file only contrasts the numbers.

Source. [`docs/experiments/2026-09-03_anyscale_g1_unit.md`](../docs/experiments/2026-09-03_anyscale_g1_unit.md)

## 2026-09-04. Polar enters the repo

**Change.** [`docs/automation/POLAR.md`](../docs/automation/POLAR.md)
names Polar as a local execution plane. Cursor keeps discovery, triage,
priority, standing answers, and the ledger. Polar runs an already-named
job on my machine. GitHub is the handoff. Polar must not become a second
KEEP list.

Owner-observed the same day, in that file. Polar runs locally, logged
in. Polar accepted instructions and repository context. Workflow exists
as a product concept. `POLAR.md` also says one Polar fill was not
flagged like some cloud submits. This dossier does not keep that
comparison. Quantbot stopped before Submit, so it has no submit-time
spam result. The unnamed fill and Quantbot count as one event until a
second job is named. The Tallgrass Original Job Post packet was written
and not run (`docs/state/decisions.tsv`).

## 2026-09-04. Quantbot Polar fill, off this branch

Copied onto this branch from `ed40f98` on
`origin/cursor/polar-first-pilot-5afa` so the result is auditable here.

**Method.** Cursor selected a KEEP. I pasted a bounded markdown packet
into Polar. Polar reported opening Jobright, clicking Original Job Post
only, using Simplify Autofill once, applying listed corrections, and
stopping before Submit.

**Polar report.** Greenhouse embed URL. About 6 minutes. `submitted=no`.
No CAPTCHA. One work-authorization widget was mapped to sponsorship No
and marked `needs_review`. That widget was not the standing sponsorship
question. The pilot cites `visa_sponsorship.do_not_auto_map`, which is
not a key in `form_strategy.yaml`. This is a partial fill.

**What Polar reported.** It consumed a Cursor-selected Jobright row and
reached an employer form on my machine. Cursor did not watch the
browser. This does not prove Workflow, ledger write-back, or every ATS
family.

Source. [`docs/experiments/2026-09-04_polar_first_pilot.md`](../docs/experiments/2026-09-04_polar_first_pilot.md)

## 2026-09-04. Rakuten reach, off this branch

Copied onto this branch from `b49d073` on
`origin/cursor/polar-scale-stage-5afa`.

**Polar report.** Original Job Post reached
`rakuten.wd1.myworkdayjobs.com`. Polar clicked Apply once, then Workday
Autofill with Resume, then hit Create Account / Sign In. No form
fields were reachable. Simplify Create Account and Autofill was not
clicked. About 4 minutes. `submitted=no`.

**Change on that branch.** Reach and fill become different cells on an
ATS matrix. A Live Slot is one markdown packet, not a Polar-owned job
list.

Sources.

- [`docs/experiments/2026-09-04_polar_second_pilot.md`](../docs/experiments/2026-09-04_polar_second_pilot.md)
- [`docs/experiments/polar_ats_matrix.md`](../docs/experiments/polar_ats_matrix.md)

## What the sequence actually converged to

1. Discovery and knowledge stay in git.
2. Autofill is an identity bootstrap, not the product.
3. Computer Use is a compiled, mode-bounded child. It does not inherit
   the rulebook.
4. Cloud and laptop do not share cookies. Jobright Original Job Post
   appeared in the tested logged-in local session. Daily cloud discovery
   lacked those cookies. A later snapshotted cloud session still ran
   short Ashby Submits.
5. Polar is the local execution plane. Cursor still picks the job.
6. Submit stays behind `docs/policy/SUBMIT_ROLLOUT.md`. G2 is closed.

That is an architecture that failed into place. It is not a polished
platform I designed on day one.
