# Experiment: three more Ashby Cloud Submits (trivial / non-pursuit)

Date: 2026-08-24
Authorized by: Junyi, after the Anyscale isolation thank-you email.
Question: does Cloud Chrome Submit still land if we do **three more**
short Ashby forms, **one tab at a time**, on jobs we would not otherwise
pursue?

This is **not** the weekday apply Automation. That design still stops
before Submit (`docs/automation/WEEKDAY_APPLY_AUTOMATION.md`). These
are named isolation repeats using the same tools as Anyscale:
`check_apply_harness.py` + branded Chrome + Simplify Copilot Autofill
once + `computerUse` leftover corrections + one Submit.

## Why these three

Verified live 2026-08-24 via `api.ashbyhq.com/posting-api/job-board/{slug}`
and Ashby public GraphQL `applicationForm`. Different Ashby orgs.
Not in either 10-tab set. Not Charta. Not Anyscale. Not prioritized.

Required fields are identity + resume only (optional essays left empty).
No project URL, no “currently based in SF/NYC” lie, no PhD-only, no
Fall 2026 intern.

| # | Company | Role | Why trivial / not a pursuit | Apply URL | Required fields |
|---|---|---|---|---|---|
| 1 | MeshyAI | Infrastructure Intern | Intern at the 10-tab Meshy org; never submitted. Shortest form. Not a prioritized FT SWE. | https://jobs.ashbyhq.com/meshy/c2f596a3-378c-4a57-b2cd-0bccd88866d7 | Name, Email, Resume |
| 2 | Midjourney | QA Analyst | QA is outside target clusters. Optional “amazing thing you created” left empty. | https://jobs.ashbyhq.com/midjourney/68e8eed8-ba7e-4530-bee1-4baf3d368d55 | Name, Email, Resume |
| 3 | Runway | Forward Deployed Finance Partner | Finance, not engineering. Optional Why-Runway left empty. | https://jobs.ashbyhq.com/runway/82789f66-9216-4ef3-bfeb-6cef4b416e63 | Name, Email, Resume |

Rejected for this pack (form or truth):

| Job | Why not |
|---|---|
| Replit SWE Intern Summer 2027 | Required project URL we do not have |
| Abridge SWE Intern | Fall 2026 cycle |
| Hex Fullstack / SDR | SF/NYC office or sales-essay / June ’26 grad |
| Modal ML Research Intern | Already rejected as PhD-only |
| Ramp Android intern | Android / Kotlin / App Store facts we do not have |
| Plaid Technical Support | Required Why-Plaid essay |
| Charta / Lila / Hayden / Baseten | Prioritized or 10-tab; not trivial |

## Protocol (each job, then stop)

1. `python3 scripts/automation/check_apply_harness.py` once at the start.
2. One Chrome window. Close the previous ATS tab after the screenshot.
   Do not keep three Ashby tabs open.
3. Open **only** the next URL in the table.
4. Copilot Autofill This Page **once**.
5. Correct leftovers only. Leave optional essays empty. Current company
   empty if present. Location `Boston, MA` if asked. Sponsorship **No**
   if asked. Relocate **Yes** if asked. Do not Generate with AI. Do not
   Autofill Again.
6. Screenshot filled form. Click Submit **once**. Screenshot result.
7. If pink spam wall: **stop the pack**. Do not open the next URL.
8. If thank-you: close that tab, go to the next row.

## Result

| # | Job | Opened | Autofill once | Submit once | Outcome | Page copy |
|---|---|---|---|---|---|---|
| 1 | Meshy Infrastructure Intern | pending | pending | pending | `in_progress` | |
| 2 | Midjourney QA Analyst | pending | pending | pending | `not_started` | |
| 3 | Runway FD Finance Partner | pending | pending | pending | `not_started` | |

## How to read

- **3× submitted** — Cloud Submit on short Ashby forms is repeatable on
  this VM class. Still not a license for a 10-tab Submit pass or for
  prioritized public Submit.
- **spam_block on N** — the Nth extra Submit tripped the wall. Stop.
  Do not retry that tab. Personal-machine path for anything that matters.
- **form_blocked / posting_closed** — that row is not a spam result.
