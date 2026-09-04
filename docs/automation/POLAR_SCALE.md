# Polar repeatable execution

Architecture stays in `docs/automation/POLAR.md`. This file is the scale
stage after experiment 1. It does not retell Polar.

Quantbot Greenhouse is one proven Jobright-to-source fill. That is not
repeatability, multi-ATS coverage, scheduling, or Polar ledger write-back.

## The unit

The unit is one Live Slot. Cursor compiles one packet. Polar executes
that packet. GitHub stores both sides. Polar never sees a job list.

```text
Cursor selects a KEEP and writes generated/polar/LIVE.md
        ↓
Junyi pastes LIVE.md into Polar (mailbox-read is not tested)
        ↓
Polar opens the named URL, Original Job Post if needed, fills, stops
        ↓
Polar returns the report shape
        ↓
Cursor files the report and reconciles the ledger
        ↓
The slot clears
```

Polar receives resolved values. It does not read policy YAML. It does
not rediscover. Phone and email stay in Simplify.

`apply_url` is used only when confidence is `exact` or `strong`. A
public index or a HostHint is not an apply URL.

## Four families

| Family | Now? | Why |
|---|---|---|
| A. Serial Polar Workflow | Later | Workflow exists as a product concept. Unattended consumption of this repo is unproven. A workflow that iterates KEEPs makes Polar a second discovery loop. |
| B. Parallel job workers | No | One Mac, one Polar profile, one Jobright session, one Simplify Copilot. None of that is tested under two writers. |
| C. ATS-sharded workers | No | Most current KEEPs have no trusted `apply_url`. ATS is an Original Job Post output. Shards would pressure Polar to invent a board URL. |
| D. Live Slot | Yes | One markdown packet. One Polar tab. Cursor owns selection and the ledger. |

D is the now shape. A becomes transport for the same slot after Polar
can read `LIVE.md` without a paste and after three clean serial fills.
B and C stay closed until a dedicated isolation probe exists.

## Handoff

Cursor → GitHub → Polar → GitHub → Cursor.

The Polar surface is markdown. Polar already followed a pasted markdown
packet and returned a bullet report. JSON and GitHub Issues are not
that surface. Issues would become a second ledger.

Polar writing git is unproven. Experiment 2 still pastes. The file in
git is the durable mailbox so Junyi copies from the repo, not from chat.

An external ChatGPT reviewer reads this file, the ATS matrix, the
experiment notes, and `LIVE.md`. The system does not depend on that
chat being online.

## Reach versus fill

Landing on a host and filling a form are different facts.

A Workday account wall can prove Jobright Original Job Post reached
Workday. It does not prove Polar can fill Workday. It does not open
the 3 to 5 fill gate.

Do not upgrade `not_tested` to `proven` from a public career page.

## Polar parallelism

| Claim | Status |
|---|---|
| One Polar tab, one pasted packet, one Greenhouse fill, stop held | Proven (Quantbot) |
| Two Polar tabs on one profile | Not tested |
| Two Workflows on one Mac | Not tested |
| Simplify Copilot on two ATS tabs | Not tested |
| Two Original Job Post clicks in one Jobright session | Not tested |
| Locked or sleeping Mac, Polar backgrounded | Not tested |
| Polar Workflow consumes this repo unattended | Unproven |

Smallest isolation experiment, not run now. Two Polar tabs on dummy
pages, same profile, a few minutes, written collision report. Not two
KEEP applies.

## Gates

| Gate | Evidence | Failure that blocks | Newly allowed | Still prohibited |
|---|---|---|---|---|
| P0 Polar fill exists | Quantbot Greenhouse, submitted=no | none | One more Polar packet | Submit, Workflow, parallel |
| P1 Non-Greenhouse OJP | Jobright-only KEEP, host is not Greenhouse and not jobright.ai, posting matched, submitted=no | Invented apply URL, sibling job, Submit | Record that ATS family as reached. A fill on that host is a separate cell | Submit, Workflow, parallel |
| P2 Packet repeatability | Second packet from the same standing-answer render, no YAML homework for Polar | Standing answers drift | A small renderer | Workflow |
| P3 Mailbox-read | Polar executes `LIVE.md` from repo context with no chat paste | Polar ignores the file or rediscovers | Junyi clicks Run | Polar git-write, scheduled Workflow |
| P4 One-slot Workflow | P1 plus P2 plus P3, three clean serial fills, zero invented facts, human still reconciles | Workflow iterates a KEEP list or Submits | A scheduled Workflow whose body is "do LIVE.md" | Parallel, Submit |
| P5 Concurrency probe | Dummy-page collision report | Cookie or Copilot cross-fill | Maybe two slots on one profile | Production parallel KEEP applies |

G2 and Submit stay in `docs/policy/SUBMIT_ROLLOUT.md`. Polar success
does not open them.

The 1 / non-GH / 3 to 5 / Workflow / parallel ladder mixes volume with
transport. Three Greenhouse fills would not prove Workday. A scheduled
Workflow before mailbox-read would still use Junyi as the bus.

## This turn

Implemented. The Live Slot file, the ATS matrix, the Rakuten packet,
and a lint on `LIVE.md`.

Not implemented. A Python compiler, PolarSlot, Workflow, parallel
workers, ledger write before Polar reports, G2, Submit.

## Next packet

`docs/experiments/2026-09-04_polar_second_pilot.md`
and `generated/polar/LIVE.md`.
