# Polar ATS sweep batch

Cursor selected these jobs. Polar does not discover, rank, or pick a
replacement. Paste one packet at a time. If a packet hits an auth wall,
report it and open the next packet. Do not Submit. Do not run these in
Cursor Computer Use.

Source KEEP files are on `origin/automation/discovery`.
Trusted `apply_url` is used only when resolver confidence is `exact`
or `strong`. A public index is not an apply URL.

## Execution order

1. `P-20260906-001` Solidigm. SmartRecruiters. Trusted apply URL.
2. `P-20260906-002` Citadel. Custom careers expected. Jobright Original Job Post.

## Selected

| packet_id | Company | Role | Expected family | Path | File |
|---|---|---|---|---|---|
| P-20260906-001 | Solidigm | 2027 Graduate Software, Firmware & AI Engineering Internships - US | SmartRecruiters | trusted apply_url | `solidigm.md` |
| P-20260906-002 | Citadel | Sector Data Scientist – 2027 Intern (US) | custom employer form | Jobright Original Job Post | `citadel.md` |

## One-line reason

| packet_id | Why this job |
|---|---|
| P-20260906-001 | Current KEEP, live posting, Master's intern on software and applied ML, trusted SmartRecruiters URL, not applied. |
| P-20260906-002 | Current KEEP, 2027 intern in New York, public careers page is a custom employer form, Jobright-only so Polar must use Original Job Post. |

## No current candidate

| Family | Status | Why |
|---|---|---|
| Ashby | `no_current_candidate` | WHOOP SWE I is live Ashby but the posting is an immediate hire and tells Fall 2026 grads to use a different New Grad requisition. Fab2 is export-controlled fab infra. Anyscale is a ledger duplicate. Clera is an agency. OpenAI Host Assurance and Perplexity MTS are too senior. |
| Lever | `no_current_candidate` | No Lever KEEP in 2026-09-04 through 2026-09-06 triage. Hive Lever is already a saved ledger row. |
| iCIMS | `no_current_candidate` | No iCIMS KEEP in those triage files. |

Greenhouse and Workday are not in this batch. Quantbot already filled Greenhouse. Rakuten already reached Workday.

## Auth expectations before Polar runs

| ATS | Reach | Auth needed | Existing Polar session | Fill tested |
|---|---|---|---|---|
| Greenhouse | proven (Quantbot) | no account wall on that job | not required | proven |
| Workday | proven (Rakuten) | account wall on that job | not prepared | not tested |
| Oracle Cloud | proven (Tallgrass land) | unknown | not prepared | not tested |
| SmartRecruiters | pending this batch | unknown until Polar reports | none | not tested |
| custom (Citadel) | pending this batch | unknown until Polar reports | none | not tested |
| Ashby | not tested | unknown | none | not tested |
| Lever | not tested | unknown | none | not tested |
| iCIMS | not tested | unknown | none | not tested |

If a form asks for a new account, stop. Do not register. Do not invent credentials.

## Polar results

| packet_id | Reach | Fill | Auth wall | submitted | P1 |
|---|---|---|---|---|---|
| P-20260906-001 | yes | full | no | no | opened |
| P-20260906-002 | yes | partial | no | no | already open |

A 3 to 5 job serial Polar batch is now permitted. G2 stays closed.
Agents must not Submit. Build the renderer before the next
hand-copied standing-answer block.
