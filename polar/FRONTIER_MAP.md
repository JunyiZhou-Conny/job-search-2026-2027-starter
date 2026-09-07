# Frontier map

Polar problem, then the problem I hit, then the file, then what I
learned. I only keep rows I can defend. Polar's full list is larger
than this table.

Public Polar text is from
[Frontier Problems](https://polarbrowser.com/blog/frontier-problems)
(18 August 2026) and
[Introducing Polar](https://polarbrowser.com/blog/introducing-polar)
(29 July 2026). Those dates are Polar's. Repo dates are git and
experiment filenames.

I do not claim I independently discovered Polar's research agenda.
Frontier Problems was published on 18 August 2026. Polar first appears
in this repo on 4 September 2026. July work predates the post.
Isolation and Twitch are after the post and before the git mention.
C017 is why I do not argue a private reading history.

The eight named Frontier Problems are the `<h2>` headings on that
post. Cloud agents and computer-use agents sit under Future products.

## Named Frontier Problems I can defend

### Self-improving agent harness

**Polar (public).** Polar takes millions of actions a week. Manually
reading trajectories to invent harness changes is slow. Can an agent
triage rollouts, propose changes, and take feedback.

**What I hit.** Twitch Computer Use spent most of its budget observing.
The parent Task strings invited that. I did not "prompt better" in
chat. I compiled the bad strings into fixtures and made lint fail.

The same pattern shows up earlier as YAML. Leftover verify loops, Run
Autofill Again, Generate with AI, and nested-Task-without-computerUse
each became a named rule after a dated incident.

**Evidence.** `docs/experiments/2026-09-03_twitch_cu_cost.md`.
`tests/test_compile_cu_task.py`.
`docs/automation/COMPUTER_USE_TOKEN_SINKS.md`.
`knowledge/form_strategy.yaml` `computer_use_context_isolation` and
`leftover_typing_one_pass`.

**What I learned.** A trajectory is only useful if the next parent
cannot repeat the failed instruction. I encoded one incident as lint
fixtures. A human still writes the rule. That is not Polar's
self-improving harness. Polar wants an agent that proposes the next
change. I do not have that.

**Unanswered.** I do not have an agent that proposes the next lint
rule from a transcript without me.

**How I might contribute.** Trajectory triage that emits a failing
fixture, not a paragraph of advice.

### Agent-human interface and agent-to-agent communication

**Polar (public).** ChatGPT and Claude were not built for delegating 10
hours of browser work. Users hand off 10,000+ LLM calls across hundreds
of subagents. Polar also asks how to orchestrate organizations of
agents and keep communication smooth across layers.

**What I hit.**

- The stored computerUse transcript contained one user message and no
  copied rule files. Runtime context still includes pixels, the Task
  string, and Cursor's unpublished computer-use prompt.
- A short Task is a parent compiler failure.
- Nested `Task environment=cloud` is a different process class. It can
  have the disk and still lack the clicker tool.

**Evidence.** Isolation experiment. Ashby isolation `not_run`.

**Later, Polar-aware.** After 4 September, Polar receives a pasted
markdown packet. Polar reading `generated/polar/LIVE.md` from git is
unproven. Polar writing git is unproven. I am the paste bus.

**What I learned.** The interface problem is not only human-to-agent.
It is parent-to-child. A stored transcript with one user message is
not the same as proving the child received nothing else at runtime.

**Unanswered.** The isolation file's own follow-up test, a fresh parent
that copies standing rules without me restating them, was never run.

**How I might contribute.** Handoff formats that are complete enough
for a child and small enough that the child does not start a discovery
loop.

## Future products Polar named

These two bullets are not among the eight named Frontier Problems.
They are expansion-product ideas under `Future products`.

### Cloud agents

**Polar (public).** Cloud browser agents sound attractive. 2FA, SSO, and
passkeys are increasingly device-bound. Many sites ban datacenter IPs.
Tasks need seamless authentication, so for now agents must run on user
devices for long-running work. Polar then says there are workarounds,
and that as a Chromium fork they want Polar running in a cloud computer
after nailing the AI browser.

**What I hit, and when.**

- 2026-07-31, before the post. Daily discovery runs in a fresh cloud
  checkout and does not see `secrets/jobright_storage.json`. All 55
  keeps pointed at Jobright URLs. The signup wall was reproduced on
  the first two keeps tried.
- 2026-07-30, before the post. Signing into Simplify on a new browser
  hit reCAPTCHA and cost about half an hour of agent time.
- 2026-08-21 to 2026-08-24, after the post. Copilot vanishes on a new
  Cloud Agent unless a personal environment was snapshotted after a
  human login. One crowded cloud Ashby session was flagged as possible
  spam. A later one-tab dashboard agent on short forms was not. IP
  class was not isolated.

**Evidence.** July 31 trial F1 and F4. Apply harness. Ashby isolation.
`docs/automation/POLAR.md` environments section. See C012 and C022.

**What I learned.** Cloud is a good control plane. Logged-in apply
failed on the daily cloud sessions that lacked Jobright cookies and,
unless snapshotted, Copilot. A later authenticated cloud snapshot kept
Copilot and recorded four short Ashby Submits. The constraint is session
and provisioning, not locality as a law. The missing object is a
browser that already has the needed cookies, not another prompt.

**Unanswered.** Whether the Charta spam wall was datacenter IP, session
reputation, retry count, Why-us length, or something else.

**How I might contribute.** Eval and harness work that treats
device-bound auth as a first-class constraint, not a footnote.

### Computer-use agents

**Polar (public).** Computer-use agents are not highly parallelizable on
one machine yet. Polar began with browser use. Extending to computer
use is a later step.

**What I hit.** I used Cursor `computerUse` as the cloud clicker. It is
not Cursor's public Browser built-in. It screenshots often. The
Computer Use contract says it cannot read a textarea DOM value. Asking
it to prove a paste with Ctrl+F is how leftover-typing burned tokens.
Twitch widgets reverted after they looked correct. See C020.

**Evidence.** Isolation experiment. Computer Use contract. Twitch
education widget note in `COMPUTER_USE_PROMPT.md`.

**What I learned.** A vision-first clicker is the wrong tool for
"prove the string is in the box." It may still be the right tool for
one named mutation. Polar's Chromium-fork bet is a different tool
surface. I should not wrap Polar inside a `computerUse` Task.

**Unanswered.** I have no Polar-internal tool inventory. I only have
product prose and one Polar-reported Greenhouse partial fill.

## Medium correspondences. Do not over-read

### Browser agent evals

Polar asks how to eval work that is not verifiable and not undoable,
on logged-in user data.

This repo already treats Submit as a one-way door and writes
experiments as pass or fail with an explicit "does not prove" line.
That is eval hygiene on a personal ATS, not a Polar benchmark.

I have no synthetic ATS, no comparable-site farm, and no RL loop.

### Extremely long-running browser agents

Polar talks about days-to-months runs and organizations of agents.

My longest measured Computer Use cluster is about 74 minutes across
three passes on one form. I have not run a 10-hour apply agent.
REALITY_MAP records 68 short discovery runs over 39 days on an older
main that wrote artifacts and never submitted. That count is a
2026-09-03 snapshot. See C023. Do not pair it with Polar's 6-minute
Quantbot report. That contrast is informal. See C018.

The correspondence is orchestration and stop rules, not duration.

## Weak or no match. Left unmatched on purpose

| Polar problem | Why I am not claiming it |
|---|---|
| Automating the company | This is a personal job-search repo, not a company operating system. |
| Compounding memory graphs | `knowledge/` and `config/profile.yaml` are durable facts. They are not a learned graph from tabs. |
| The blank slate problem | I already speak in Task strings and YAML. I am not Polar's non-coder user. |
| Owning the model layer | No training data pipeline, no model mix of my own. |
| Next browser action prediction (Future products) | Not attempted. |
| API / RPA successor (Future products) | `resolve_apply_url.py` talks to public board APIs. That is URL resolution, not an RPA agent. |

## Chronology rule used in this map

Frontier Problems published 2026-08-18. Polar first named in git
2026-09-04. Those are different cutoffs.

| Work | First dated in repo | Vs 18 Aug post | Polar in git |
|---|---|---|---|
| Local Simplify session notes | 2026-07-26 | before | no |
| Apply trial, resolver | 2026-07-31 | before | no |
| Ten-tab / harness / Copilot / Autofill Again | 2026-08-18 to 2026-08-23 | on or after | no |
| Isolation, spam wall, leftover typing | 2026-08-24 | after | no |
| Twitch cost, compiler | 2026-09-03 | after | no |
| Polar execution-plane essay | 2026-09-04 | after | yes |
| Quantbot and Rakuten Polar packets | 2026-09-04 | after | yes |

Anything dated 2026-09-04 or later is Polar-aware. Work dated after
18 August and before 4 September is not Polar-aware in git. It is
also not independent discovery. C017 is unknown.
