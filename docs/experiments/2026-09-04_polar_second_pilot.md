# Polar second fill packet, 2026-09-04

Architecture stays in `docs/automation/POLAR.md`. Scale rules stay in
`docs/automation/POLAR_SCALE.md`. This file is experiment 2.

Quantbot is experiment 1. Do not re-run it.

Do not run this packet in Cursor Computer Use. Do not Submit.

## Why Rakuten was selected

Source is the `origin/automation/discovery` KEEP file
`generated/discovery_triage_2026-09-04T22.csv`.

It is the remaining Jobright-only `core` and `cloud_swe` KEEP Junyi
would reasonably pursue after the rejects below. It is a full-time
Platform Engineer role in San Mateo, not an intern cycle.

| Field | Value |
|---|---|
| `packet_id` | `P-20260904-002` |
| Company | Rakuten Rewards |
| Role | Platform Engineer |
| Lane and cluster | `core` and `cloud_swe` |
| Location | San Mateo, CA, on site |
| Track | full-time, earliest start 2027-01-18 |
| Weight | regular |
| `discovery_url` | `https://jobright.ai/jobs/info/6a99ffb990a313642c653fe3` |
| `apply_url` | empty |
| `apply_url_confidence` | `none` |
| Resume cluster | `cloud_swe` v1.3 |
| Polar prompt | `generated/polar/LIVE.md` |

`Ledger.precheck` on that Jobright URL, company, and role returned
`duplicate=False` and no matches. Polar is not run from this turn.

Expected ATS family is Workday. That status is ASSUMED from other
public Rakuten Rewards engineering listings. The resolver returned
none for this title. Polar must use Original Job Post. Do not write
a Workday URL into the Polar prompt.

`config/submit_gates.yaml` keeps Workday at G0. Polar stops before
Submit. If an account wall appears, Polar stops and reports. It does
not register.

Jobscroller text uses forward-deployed language. Polar must not
invent FDE or customer-on-site experience.

## Rejected alternatives

| Row | Why not |
|---|---|
| Quantbot | Experiment 1 |
| Skild AI Simulation Engineer | Public board is Greenhouse |
| Anyscale Ray Core | Ledger duplicate. Exact Ashby URL |
| Clera, all listings | `knowledge/ashby_orgs.yaml` `kind=agency` |
| Northwood Ashby intern | Export-control and defense class the first Polar screen skipped |
| Booz Allen Workday | Same defense skip. Also not Jobright-only |
| NY Life 2027 AI and Data Science intern | Public posting forbids OPT and CPT |
| Spectrum 2027 Data Science intern | Requires a rising bachelor's senior graduating Dec 2027 to May 2028 |
| Delta Intern, Innovation AI Engineering Spring 2027 | Avature, but the Jobright title is the undergraduate listing. Do not open the graduate sibling |
| Manulife Summer Intern 2027 AI | Public Boston text asks for a current undergraduate plus cover letter and transcript. Jobright location is blank |
| Bain AI Engineering Intern Summer 2027 | Jobright says NY or SF. Public Bain AI intern listings found are non-US offices |
| Constellation Associate SWE AI | Resolver weak-matched the wrong Ashby board. Energy careers mention nuclear-site access |
| Adobe, Apple, Waymo, TikTok, SpaceX, IBM, and Cisco | `big_tech` hint list used in the first Polar screen |
| CGI and Capgemini | Staffing or consulting mills from the first Polar screen |

There is no legitimate Jobright-only Ashby KEEP in this pool.

## Pass and fail

Reach and fill are separate results.

Reach. Polar left Jobright, landed on the same company and Platform
Engineer role, and the host is not jobright.ai.

Fill. Reach holds, the host is not Greenhouse, standing fields are
filled or listed as unresolved, no facts were invented, and Submit
was not clicked.

Account wall. Reach may still hold if the host is the employer ATS
and the posting matches. That can open P1 as reach. Fill fails. It
does not count as a fill toward a multi-job gate.

If Original Job Post lands on Greenhouse, Stage 2 fails. Record the
host. Do not open P1. Do not open a sibling.

Invented apply URL, sibling job, or Submit freezes the Polar ladder.

## Polar prompt

The paste-ready prompt is `generated/polar/LIVE.md`. Do not paste
this experiment note into Polar.
