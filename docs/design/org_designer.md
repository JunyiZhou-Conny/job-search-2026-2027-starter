# Org designer

Junyi designs the Grok Bot company on a page. He never fills
`ORG_CHART_BLANK.md`. The page does not hire anyone.

## Problem

The blank chart asked Junyi to replace every `_` by hand. Graph, seat
blocks, and roster were the same facts written three times. Nothing
read a filled copy. The live Chief paste still says: assign one
existing teammate, do not hire the paper cell unless Junyi says hire.

He wants a tree he can drag, named bots, roles, then a brief a Chief
of Staff or architect can spawn from.

## Usage

```bash
python3 scripts/serve_org_designer.py
# open http://127.0.0.1:8766/
# Junyi's 2026-08-26 sketch:
# open http://127.0.0.1:8766/?template=junyi-architect-lanes
```

The server listens on all interfaces (`0.0.0.0:8766`) so a Cloud Agent
can forward the port. `127.0.0.1` in laptop Chrome is the laptop, not
the VM. On a Cloud Agent, open the agent's Desktop and use the browser
there.

On the page: set company and project, or start from a paper template
(roles land as unnamed vacancies, not invented bot names). Add a bot
under a parent. Drag a row onto another row to change who they listen
to. Fill does / does not. Save writes the charter. Export writes the
standup brief only when the chart is complete. The brief still says
do not create Bots until Junyi authorizes that revision.

A test calls `OrgDesigner.at(tmp).save(...)`. A CoS opens
`docs/grok-bot-management/ORG_SPAWN_BRIEF.md`. Nobody opens
`GROK_BOT_HANDOFF.md` for this job.

## Shape

Canonical file: `docs/grok-bot-management/ORG_CHART.json`.

Derived: `ORG_CHART.md` (same sections as the blank, no `_`) and
`ORG_SPAWN_BRIEF.md` (paste). Direct reports, ASCII graph, roster,
and headcount are compiled from `listens_to`. Teams are labels, not
a second tree.

Public Python surface: `OrgDesigner.read`, `review`, `save`. Hidden:
validation, cycle checks, template vacancies, renderers, file replace.

Owner is a human type with no parent. Seats have internal ids so a
rename does not rewrite the tree. Bot names must be unique and
non-empty before a seat can be saved. Templates become `VacantRole`
slips. Save refuses leftover vacancies.

`listens_to` is stored. It is not inferred from team nesting. An
on-call Writer can report to the Ashby cook and still sit in Copy.

`hire_allowed` is always false. Writers accept chart/brief paths
only. The live Ashby paste is never opened for write.

Sibling server on port 8766. Vanilla HTML/CSS/JS. Shipped apply-queue
tokens (paper, teal accent, hairlines). Not a route on the apply
queue.

## Synthesis decision

Arena dropouts: charter-tree canvas (candidate 1) and wizard
(candidate 4) wrote nothing.

Base: candidate 3 usage (indented reporting tree, drag to reparent,
sibling server, branded paths, do-not-hire brief).

Grafted from candidate 2:

- `OrgDesigner` read / review / save instead of a wide mutation API
- JSON charter as the only editable record
- `VacantRole` so templates do not invent bot names
- Pilot / later / on-call staffing
- Revision as digest of canonical bytes

Rejected: team boxes as the primary spatial model (user asked for a
people tree; team-inferred reporting fights on-call Writer).
Rejected: markdown as the working source (`parse(render(x)) == x` is
a grammar to maintain forever, and the blank already drifted from
apply-cell). Rejected: seeding bot names from role titles.

## Tradeoffs accepted

- We accept a new JSON file in exchange for one fact store that
  cannot drift from its own graph and roster.
- We accept an outline, not a 2D poster, so we never store x/y.
- We accept last-write-wins plus a revision check, not a merge, for
  one-human design sessions.
- We accept that Save can persist a named seat with empty does, and
  that Export is the completeness gate.

## Alternatives considered

- **Markdown as source of truth.** Smaller public object for git
  readers. Larger parser, and the blank's three copies stay a trap.
- **Nested department boxes with inferred reporting.** Hides
  `listens_to` until it is wrong (Writer on-call). Extra override
  language on every exception.
- **Wizard only, no tree.** Hides layout. Exposes a form. Junyi
  asked to drag a company.

## Next implementation step

Implement `compile_draft` and the reparent / unnamed / vacancy /
brief tests, then the page.
