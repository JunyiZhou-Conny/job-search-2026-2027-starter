# Polar second fill packet, 2026-09-04

Architecture stays in `docs/automation/POLAR.md`. Scale rules stay in
`docs/automation/POLAR_SCALE.md`. This file is experiment 2.

Quantbot is experiment 1. Do not re-run it.

Do not run this packet in Cursor Computer Use.

## Why this job

Source is `origin/automation/discovery` triage
`generated/discovery_triage_2026-09-04T22.csv`. Decision is `keep`.
Lane is `core`. Cluster is `cloud_swe`. Weight is `regular`.

| Field | Value |
|---|---|
| Company | Rakuten Rewards |
| Role | Platform Engineer |
| `discovery_url` | `https://jobright.ai/jobs/info/6a99ffb990a313642c653fe3` |
| `apply_url` | empty |
| `apply_url_confidence` | `none` |
| Location | San Mateo, CA, on site |
| Track | full-time, earliest start 2027-01-18 |
| Resume | `cloud_swe` v1.3 |

`scripts/apply_ledger.py precheck` on that Jobright URL returned
`duplicate=false` and no matches.

It is not in `knowledge/application_priority.yaml`
`confirmed_prioritized`. The title is Platform Engineer, not Forward
Deployed Engineer. It is not an agency board. It is not a 2026 intern
cycle. Title is not Senior.

Expected ATS family is Workday. That is ASSUMED from other Rakuten
Rewards engineering listings on `rakuten.wd1.myworkdayjobs.com`.
`scripts/resolve_apply_url.py` returned `none` for this title. Polar
must use Original Job Post. Do not write a Workday URL into the packet.

`config/submit_gates.yaml` has `workday: G0`. G2 is closed for every
ATS family. Polar fills if it can, then stops before Submit. If an
account wall appears, Polar stops and reports. It does not register.

## Rejected rows from the same KEEP pool

| Row | Why not |
|---|---|
| Quantbot | Experiment 1 |
| Skild AI Simulation Engineer | Public board is Greenhouse |
| Anyscale Ray Core | Ledger duplicate. Exact Ashby URL |
| Clera (all) | `knowledge/ashby_orgs.yaml` `kind=agency` |
| Northwood Ashby intern | Export-control / defense class the first Polar screen skipped |
| Booz Allen Workday | Same defense skip |
| NY Life 2027 AI & Data Science intern | Public posting forbids OPT/CPT |
| Spectrum 2027 Data Science intern | Requires a rising bachelor's senior graduating Dec 2027 to May 2028 |
| Delta Intern, Innovation AI Engineering Spring 2027 | Avature, but the Jobright title is the undergraduate listing. Do not open the graduate sibling |
| Manulife Summer Intern 2027 AI | Public Boston text asks for a current undergraduate plus cover letter and transcript. Jobright location is blank |
| Bain AI Engineering Intern Summer 2027 | Jobright says NY/SF. Public Bain AI intern listings found are non-US offices |
| Constellation Associate SWE AI | Resolver weak-matched the wrong Ashby board. Energy careers mention nuclear-site access |
| Adobe / Apple / Waymo / TikTok / IBM / Cisco | `big_tech` hint list used in the first Polar screen |
| CGI / Capgemini | Staffing or consulting mills from the first Polar screen |

There is no legitimate Jobright-only Ashby KEEP in this pool.

## What this experiment tests

```text
GitHub Live Slot
→ Polar opens the Jobright discovery URL
→ Original Job Post only
→ non-Greenhouse host if the assumption holds
→ Simplify once if the form is reachable
→ stop before Submit
```

It does not test Workflow, parallel workers, or Polar ledger write-back.

## Pass and fail

Reach pass. Polar left Jobright, landed on the same company and
Platform Engineer role, host is not `jobright.ai` and not Greenhouse,
submitted=no.

Fill pass. Reach pass, plus standing fields filled or listed as
unresolved, no invented facts.

Account wall. Reach may still pass if the host is the employer ATS.
Fill fails. That does not open the 3 to 5 fill gate.

Greenhouse again. Record the cell. Do not open P1. Do not open a
sibling. Clear the slot on a later turn.

Invented apply URL, sibling job, or Submit. Stop the Polar ladder.

## Polar prompt

Paste `generated/polar/LIVE.md`. Do not add P-Stack. Do not open extra
jobs.
