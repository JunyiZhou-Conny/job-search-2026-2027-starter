# Grok Bot management

Notes on how Junyi wants to run Grok Bots against this job-search repo.

This folder does not change [AGENTS.md](../../AGENTS.md) or
[docs/BOUNDARIES.md](../BOUNDARIES.md). Submit only when Junyi names
the URL.

Copy Settings **Description** boxes from git. Do not keep a private
frozen paste in chat. If the CEO Description starts with
`You are Junyi Zhou's Architect`, that is the wrong file.

## Where Settings Descriptions live

| Bot | Copy the Description from | What it is |
| --- | --- | --- |
| Architect | [ARCHITECT.md](ARCHITECT.md) — block through `END PASTE` | Outside every company. Spawns Bots. Not apply. |
| CEO of Auto Application | [BOT_DESCRIPTIONS.md](BOT_DESCRIPTIONS.md) — **Now: CEO of Auto Application** | Assign + review. Does not Autofill. Does not spawn. |
| Ashby Autofiller | [BOT_DESCRIPTIONS.md](BOT_DESCRIPTIONS.md) — **Now: Ashby Autofiller** | One Ashby job. Pulls `form_strategy.yaml`. Checks Copilot on **this** window, then Autofill once. |

Standing answers and clicker mechanics are **not** in those
Descriptions. They live in [`knowledge/form_strategy.yaml`](../../knowledge/form_strategy.yaml)
and [`knowledge/work_authorization.yaml`](../../knowledge/work_authorization.yaml).
The Autofiller reads those files each job.

The one-turn chat you send the CEO (not Settings) is
[GROK_BOT_HANDOFF.md](GROK_BOT_HANDOFF.md). If the CEO is frozen,
use [ALIGNMENT.md](ALIGNMENT.md) plus that live block.

Later apply seats (Chief of apply, Writer, Workday, unknown portal)
are also in [BOT_DESCRIPTIONS.md](BOT_DESCRIPTIONS.md) under
**Later pastes**. Do not create them unless Junyi names the seat.

## Other notes in this folder

- [SHARED_COMPUTER.md](SHARED_COMPUTER.md) — one computer, many screens
- [APPLY_CORP_STRUCTURE.md](APPLY_CORP_STRUCTURE.md) — first apply org chart
- [TEAM_HIERARCHY.md](TEAM_HIERARCHY.md) — four-person shop (paper)
- [SOURCES.md](SOURCES.md) — quote ledger
- [THINKING.md](THINKING.md) — explanation
- [ORG_TEMPLATES.md](ORG_TEMPLATES.md) — org-record registry (paper)
- [ORG_CHART_BLANK.md](ORG_CHART_BLANK.md) — empty chart for Junyi to fill
