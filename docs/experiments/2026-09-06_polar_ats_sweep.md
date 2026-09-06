# Polar ATS sweep, 2026-09-06

Architecture stays in `docs/automation/POLAR.md`. Scale rules stay in
`docs/automation/POLAR_SCALE.md`. This file is the third Polar
experiment set. Quantbot is experiment 1. Rakuten is experiment 2.
Do not re-run either.

Do not run these packets in Cursor Computer Use. Do not Submit.

## Lineage

`cursor/polar-ats-sweep-5afa` merges first-pilot Quantbot ledger
state with scale-stage Rakuten reach. Quantbot ids stay
`J20260904-001` and `A20260904-001`. Rakuten stays result
`P-20260904-002` with no ledger start.

## What changed in the objective

Routing is no longer the question. A trusted `apply_url` with
confidence `exact` or `strong` is used directly. Jobright-only rows
still use Original Job Post. Polar still does not invent an ATS URL
and does not open a sibling requisition.

## Selected packets

See `generated/polar/ats_sweep/manifest.md`.

| packet_id | Company | Why |
|---|---|---|
| P-20260906-001 | Solidigm | Live 2027 graduate internship KEEP. Trusted SmartRecruiters URL. |
| P-20260906-002 | Citadel | Live 2027 intern KEEP. Jobright-only. Public careers page is a custom form. |

Precheck on the Solidigm SmartRecruiters URL, the Solidigm Jobright
URL, and the Citadel Jobright URL returned `duplicate=false`.

## Rejects that did not fill an ATS slot

| Company | Family | Why not selected |
|---|---|---|
| WHOOP SWE I (Backend) | Ashby | Live, Boston, exact URL. The posting is an immediate hire and tells Fall 2026 grads to use a New Grad requisition. Opening that sibling would be substitution. |
| Fab2 infra intern | Ashby | Export-controlled semiconductor fab intern. Care is low. Not a volume path. |
| Anyscale Ray Core | Ashby | Ledger duplicate. |
| Clera | Ashby | Agency board. |
| OpenAI Host Assurance | Ashby | Too senior for a regular first Polar screen. |
| Perplexity MTS Infra | Ashby | Too senior. |
| Hive MLE | Lever | Already a saved ledger row. Not in the current KEEP pool. |
| Rippling ML SWE intern Winter 2027 | Rippling ATS | Posting requires enrollment during the January to April 2027 intern term. Program end is 2026-12-18. |
| Credence AI SWE | Workable | Federal-contractor pattern. Not used to fill an ATS slot. |
| PepsiCo 2027 DS intern | Workday expected | Workday reach is already proven. Fill waits on an owner session. |
| Disney Spring 2027 DS intern | likely Workday | Unrestricted work-authorization wording plus another Workday. |

## Families with no current candidate

Ashby. Lever. iCIMS.

## Workday later

Do not re-run Rakuten. Do not create a Workday account in this
experiment. Later path is one owner login in Polar, session kept,
then a real Workday packet tests fill.

## What evidence will count

| Result | Meaning |
|---|---|
| reach | Polar left the starting URL, posting matched, host is not jobright.ai. Account wall still counts as reach. |
| partial fill | Form fields were reachable. Some standing answers were entered. Required fields remain unresolved or an auth wall stopped later pages. |
| clean fill | Intended requisition is open. Standing fields are filled or listed unresolved. Approved written answers were used where those boxes existed. Submit was not clicked. |

A public career page does not count. Cursor Computer Use does not count.

## What unlocks the next batch

One clean non-Greenhouse Polar fill from this sweep opens a 3 to 5
job serial Polar batch. P1 stays a fill gate, not a reach gate.
