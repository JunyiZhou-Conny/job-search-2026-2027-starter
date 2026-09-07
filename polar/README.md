# Polar Browser application dossier

This branch is an evidence packet, not a second job tracker. It reconstructs
what this repository actually did while I tried to automate my own 2026–2027
job search, then maps those findings to Polar's Frontier Problems.

I have not emailed Polar. I have not submitted an application. This file is
the landing page. The rest of `polar/` is the audit trail.

## Who I am

I am Junyi Zhou. I am an SM student in Health Data Science at Harvard T.H.
Chan, previously Applied Mathematics and Statistics at Emory. I am in Boston
on F-1 status and I am looking at Summer 2027 internships and 2027 new-grad
roles.

The relevant fact for Polar is not the degree line. Since late July I have
been building a control plane and two incomplete browser executors in
public git, then instrumenting
why the browser half kept failing or getting expensive.

## Why Polar maps onto this repo

Git does not show Polar in the apply or Computer Use writeups before
4 September 2026. That is the chronology I can defend. I am not
claiming a private reading history.

From late July through 3 September 2026 this repo records a sequence of
browser-agent failures. Jobright pages that cannot be applied on. Cloud
sessions that lose Simplify Copilot. A Computer Use child that does not
inherit the parent rulebook. Parent prompts that spend most of their budget
scrolling and verifying. One Ashby spam wall on a crowded cloud Chrome
session. Nested `Task environment=cloud` children that have no `computerUse`
tool at all.

Polar first appears in this repository on 4 September 2026, in
[`docs/automation/POLAR.md`](../docs/automation/POLAR.md). Polar's
[Frontier Problems](https://polarbrowser.com/blog/frontier-problems) post is
dated 18 August 2026. I cannot prove the exact hour I first read that post.
I can prove that the Computer Use cost, isolation, and compiler work is
dated before Polar is mentioned in git.

The overlap is specific. Polar writes that cloud browser agents look
attractive until 2FA and datacenter IPs get in the way, and that agents
need to run on the user's device for long logged-in work. That is the
split this repo already had to make.

## What I have been building

A control plane in git, plus two execution environments that do not share
cookies.

```text
discovery / scrape
  → triage and dedupe
  → profile knowledge
  → resume cluster
  → ATS URL resolution
  → browser fill
  → review
  → submit policy
  → ledger
```

Cursor and this repo decide what to apply to. Cloud Computer Use can click
on a snapshotted VM. Polar can click on my already-logged-in Mac. Simplify
holds the public apply ledger. Git holds strategy, standing answers, and
the handoff packet.

Polar is not a second job-search product in this design. It is the local
execution plane. See [`ARCHITECTURE.md`](ARCHITECTURE.md).

## The two or three strongest things

These are the stories I can defend after checking the original files.
They are not the most flattering sentences.

1. **I measured an observation-loop tax, then encoded it.** On 3 September
   2026 three Computer Use passes on one Twitch Greenhouse form took about
   74 minutes and 195 actions, including 129 scrolls and 12 type or key
   actions. The parent Task strings had asked for whole-form screenshots,
   verify-each-field, and report-every-widget. I compiled those strings
   into fixtures. `scripts/compile_cu_task.py lint` rejects them now.
   The same day, a compiled Ashby G1 unit on a different form ran in
   3.4 plus 5.7 minutes. That is not a controlled before-and-after.
2. **I showed that a computerUse child starts clean.** Four isolation
   clickers on 24 August 2026 each received one user message (1147 to 2395
   characters) and no `AGENTS.md`, no `knowledge/*`, and no parent chat.
   Writing a better rule file does not change the next clicker unless a
   parent copies the standing slice into the Task string. That is a handoff
   problem, not a "the model forgot the rules" problem.
3. **I split control-plane reasoning from local browser execution.** Cloud
   discovery cannot see my Jobright session. A public ATS resolver covers
   only a slice of keeps. Nested cloud children can boot the harness disk
   and still lack `computerUse`. Polar, on my machine, used Jobright
   Original Job Post, reached Greenhouse, filled standing fields, and
   stopped before Submit in about 6 minutes on one Quantbot intern form.
   That Polar result is a Polar report I pasted back, not a second observer
   watching the browser.

I am not claiming the 6-minute Polar fill and the 74-minute Twitch Computer
Use pass are a controlled comparison. Different forms, different days,
different measurement methods. [`DEMO.md`](DEMO.md) says what a fair test
would require.

## Frontier Problems I hit before Polar is in this repo

A few correspondences are unusually tight. I did not force the rest.

| Polar problem | What I hit | Evidence |
|---|---|---|
| Cloud agents, device-bound auth, datacenter IPs | Jobright Original Job Post only exists in a local logged-in session. Cloud Copilot vanishes without a snapshot. One crowded cloud Ashby session was flagged as possible spam. | [`FRONTIER_MAP.md`](FRONTIER_MAP.md) |
| Self-improving agent harness | Failures became YAML, then a compiler and tests, instead of another long prompt. | `scripts/compile_cu_task.py`, `knowledge/form_strategy.yaml` |
| Agent-human interface, agent-to-agent communication | Parent understands the form. Child sees pixels and one Task string. | isolation experiment, 2026-08-24 |

I do not have a match for owning the model layer, next-browser-action
prediction, or Polar's blank-slate consumer problem.

## What to inspect

Start here, then follow links. Do not treat this folder as a rewrite of
the operating system.

- [`JOURNEY.md`](JOURNEY.md) is the chronology.
- [`FRONTIER_MAP.md`](FRONTIER_MAP.md) is Polar problem to repo evidence.
- [`EVIDENCE.md`](EVIDENCE.md) is the claim index. Every important number
  lives there with a type and a "does not prove" line.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) is the split that actually emerged.
- [`DEMO.md`](DEMO.md) is a small demo I could record later.
- [`NEXT_EXPERIMENTS.md`](NEXT_EXPERIMENTS.md) is the eval I would run next.
- [`EMAIL_DRAFT.md`](EMAIL_DRAFT.md) is unsent.

Canonical files I did not duplicate:

- [`docs/automation/POLAR.md`](../docs/automation/POLAR.md)
- [`docs/automation/COMPUTER_USE_PROMPT.md`](../docs/automation/COMPUTER_USE_PROMPT.md)
- [`docs/experiments/2026-09-03_twitch_cu_cost.md`](../docs/experiments/2026-09-03_twitch_cu_cost.md)
- [`docs/experiments/2026-08-24_computer_use_context_isolation.md`](../docs/experiments/2026-08-24_computer_use_context_isolation.md)

## What I would want to explore with Polar

I want to work on the harness and eval side of browser agents, not on a
generic "I like AI browsers" pitch.

The live questions I already have are Polar-shaped. How do you stop a
parent from spending the action budget on verification theater. How do
you hand a child just enough context. How do you keep durable state in
git while the browser stays on the user's device. How do you write evals
for forms you cannot undo.

If that is useful, the email draft is ready. It stays unsent until I send
it myself.
