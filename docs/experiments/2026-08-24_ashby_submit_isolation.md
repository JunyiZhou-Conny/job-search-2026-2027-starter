# Experiment: Ashby Submit isolation (fresh Cloud VM)

Date: 2026-08-24
Authorized by: Junyi. He already submitted Charta from his own computer.
Question: does Ashby still block Cloud Chrome Submit on a **different**
Ashby org, from a **new** VM, with a short form and one tab?

## Why this is the last-step gap

Cloud Chrome Submit on Charta hit: “We couldn’t submit your application.
Your application submission was flagged as possible spam.” That click
did **not** create an application. Junyi then submitted Charta from his
laptop. If a second Cloud Submit also dies, the Cloud path is the gap
and mass apply cannot depend on it.

## What this VM is (and is not)

A sibling Cloud Agent on the same personal environment
(`41a15b57-8916-11f1-b532-320a589b8025`) is a **new pod**. It can get a
new IP. It still boots the same Copilot snapshot and the same
datacenter class.

This is **not** a home laptop, not a new residential ISP, and not a
new Simplify account.

| Isolated | Not isolated |
|---|---|
| This parent Chrome session / many open ATS tabs | Home vs datacenter IP class |
| Charta tenant / Charta Why-us length | Same email, phone, resume |
| Retry loops on the blocked tab | Simplify Copilot still installed |
| Required long essay (none on the chosen form) | Computer-use still clicks Submit |

## Target job (primary)

Pick a live Ashby posting that is **not** in either 10-tab set and
**not** Charta.

| Field | Value |
|---|---|
| Company | Anyscale |
| Role | Software Engineer (Ray Core) |
| ATS | Ashby (`anyscale`) |
| Apply URL | https://jobs.ashbyhq.com/anyscale/73a973b1-6377-4144-a6e5-610b78719882 |
| Location / mode | San Francisco, Hybrid (board API) |
| Lane | `practice` (FT SWE, not intern; Submit test, not a prioritized FDE) |
| Why this form | No required Why-us / project URL. Required: name, email, location, resume, hybrid Mon/Tue/Thu, sponsorship |

Verified 2026-08-24 via `api.ashbyhq.com/posting-api/job-board/anyscale`
and Ashby public GraphQL `applicationForm`.

### Standing answers for this form

From `knowledge/form_strategy.yaml` + `config/profile.yaml`:

- Full name / email / phone / resume: Copilot profile (do not invent)
- Current location: `Boston, MA`
- Current company: leave empty (student; do not invent an employer)
- Additional information: **leave empty** (optional; do not invent Why-us)
- LinkedIn / GitHub: Copilot or profile URLs if empty
- Twitter / Portfolio / Other: leave empty
- Hybrid Mon, Tue, Thu: **Yes**
- Open to relocate if outside SF Bay: **Yes**
- Require visa sponsorship: **No**
- Cover letter: none on this form
- Do not click Generate with AI
- Do not Run Autofill Again after corrections

### Rejected alternatives (do not use unless primary is closed)

| Job | Why not first |
|---|---|
| Replit SWE Intern Summer 2027 | Required Project URL + password. We do not have one. Inventing it would break the truth rule. |
| Abridge SWE Intern | Fall **2026** cycle. Discovery skip. |
| Hex Fullstack | “Currently based in SF or NYC” is false (Boston). Yes would be a lie. |
| Modal ML Research Intern | PhD-only. Already rejected. |
| Meshy Infrastructure Intern | Shortest form (name/email/resume), but same Ashby org as the 10-tab Meshy tab. Backup only. |
| Ramp Android intern | Required App Store / Kotlin / Android project facts we do not have. |

**Backup if Anyscale is closed:** Meshy Infrastructure Intern
https://jobs.ashbyhq.com/meshy/c2f596a3-378c-4a57-b2cd-0bccd88866d7
Name / email / resume only. Same Meshy org as the unsubmitted 10-tab
Fullstack Intern. Close the Anyscale tab. Do not open a sibling Anyscale
role.

## Parent VM (this Chrome)

Do **not** click Submit again here. Do not open the Anyscale tab here.
The isolation is the new pod.

## Child VM protocol (one pass)

1. Fresh Cloud Agent. One Chrome window. No other ATS tabs.
2. `python3 scripts/automation/check_apply_harness.py` — record ready / Copilot id.
3. Open **only** the Anyscale URL above.
4. Copilot Autofill This Page **once**.
5. Correct leftovers only: location `Boston, MA` if empty; hybrid **Yes**;
   relocate **Yes**; sponsorship **No**. Leave Additional information empty.
6. One screenshot of the filled form.
7. Click **Submit** / **Submit application** **once**.
8. One screenshot of the result (thank-you **or** pink spam wall).
9. Stop. Do not retry Submit. Do not Autofill Again.

## Result (fill after the child run)

| Field | Value |
|---|---|
| Child agent URL | TBD |
| Harness ready | TBD |
| Copilot id | TBD |
| Job actually opened | TBD |
| Autofill once | TBD |
| Submit clicked | TBD |
| Outcome | `spam_block` / `submitted` / `form_blocked` / `posting_closed` / `not_run` |
| Page copy (verbatim if error) | TBD |
| Notes | TBD |

## How to read the outcome

- **spam_block again** — Cloud Chrome Submit is the gap. Next experiments
  are not “one more tab on this VM.” They are personal-machine apply,
  Copilot paused at Submit, or a non-datacenter path. Do not keep
  retrying Cloud Submit.
- **submitted** — this parent session / Charta retries / long Why-us were
  enough to trip the wall. Cloud Submit is not proven safe for mass
  apply; it is no longer a one-sample failure.
- **form_blocked / posting_closed** — test did not reach Submit. Do not
  treat that as a spam result.
