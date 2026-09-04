# Polar first fill pilot, 2026-09-04

Architecture stays in `docs/automation/POLAR.md`. This file is the first
fill packet. It does not change ownership. Cursor selected the job. Polar
executes it on Junyi's machine. Do not run this packet in Cursor Computer
Use.

## Why this job

Source is `origin/automation/discovery` triage
`generated/discovery_triage_2026-09-04T22.csv` (fetched
2026-09-04T22:03:29Z). Decision is `keep`. Lane is `core`. Cluster is
`data_ml`. Weight is `regular`.

| Field | Value |
|---|---|
| Company | Quantbot Technologies LP |
| Role | Machine Learning Research Engineer Internship - 2027 [New York] |
| `discovery_url` | `https://jobright.ai/jobs/info/6a9b1602fe45b8490f606c9f` |
| `apply_url` | empty |
| `apply_url_confidence` | `none` |
| Location | New York, NY, on site |
| Track | `internship_if_eligible` |

`scripts/apply_ledger.py` `precheck` on the Jobright URL returned
`duplicate=False` and no matches in `data/applications.csv`,
`data/job_decisions.csv`, `data/apply_attempts.csv`, or the newest
Simplify export. Quantbot does not appear in those tables.

It is not FDE. It is not in `knowledge/application_priority.yaml`
`confirmed_prioritized`. It is not an agency board. It is not a 2026
intern cycle. Title is not Senior. Work model is on site.

Other 2026-09-04T22 KEEP rows were worse for this pilot. Anyscale Ray
Core is a blocking ledger duplicate. Clera is an agency board. Apple,
Waymo, TikTok, Adobe, and SpaceX sit on the `big_tech` hint list. Booz
Allen, General Dynamics, Naval Nuclear, Northwood, and SpaceX are
export-control or defense. CGI, Capgemini, and similar firms are
staffing or consulting mills. Scale AI, Kodiak, Schonfeld, and
Quantifind already have an `exact` `apply_url`, so they would skip
Original Job Post.

Public web indexes list Greenhouse `gh_jid=4340833009` for this title.
That is not a resolver `exact` or `strong` write. Polar must not open
that URL unless Original Job Post takes it there.

## Submit policy

`config/submit_gates.yaml` has `greenhouse: G1` and `other: G0`. G2 is
closed for every ATS family. This regular row is not authorized for
autonomous Submit. Polar fills and validates, then stops immediately
before Submit.

## What this experiment tests

```text
GitHub-selected KEEP
→ Polar opens the Jobright discovery URL
→ Original Job Post only
→ employer or source application
→ Simplify once if present
→ canonical corrections
→ ready, not submitted
```

It does not test Workflow scheduling, ledger write-back, or bulk
throughput.

## If it succeeds

Polar can consume a Cursor-selected Jobright row, leave Jobright, reach
the intended Quantbot intern posting, fill standing answers without
inventing facts, and stop before Submit.

## If it fails

Name the break. Typical breaks are Original Job Post missing, a
LinkedIn-only or closed destination, a different requisition, an
account wall, a required essay with no approved draft, or a bad
autofill that Polar cannot correct from the packet.

## What would justify the next stage

- 1 → 3–5 jobs. Two clean Jobright-to-source fills on different ATS
  hosts, each with `submitted=no` and no invented facts. One of those
  two may be this Quantbot run.
- 3–5 → scheduled Polar Workflow. Five fills with the same stop
  discipline, zero wrong-fact incidents, and a human still reconciling
  results into the ledger. Do not schedule from a single lucky run.

## Polar prompt

Copy the block below into Polar. Do not add P-Stack. Do not open extra
jobs.

````text
You are Polar on Junyi Zhou's already-logged-in local browser. This is one bounded apply task. Cursor already selected the job. Do not search Jobright, LinkedIn, or the employer's board for another requisition.

JOB
- Company: Quantbot Technologies LP
- Role: Machine Learning Research Engineer Internship - 2027 [New York]
- Location: New York, NY, on site
- Track: Summer 2027 internship, about June to August, 10 weeks
- Weight: regular
- Lane: core
- Resume cluster: data_ml. Prefer the Simplify resume that matches 2026-08-24_data-ml_v1.3. Do not create a new resume. Do not upload a file from disk unless Simplify has no resume attached.
- Starting URL: https://jobright.ai/jobs/info/6a9b1602fe45b8490f606c9f
- apply_url: none. Do not invent one.

JOBRIGHT
1. Open the starting URL while logged into Jobright.
2. Confirm the page is Quantbot Technologies and Machine Learning Research Engineer Internship 2027 in New York.
3. Click Original Job Post only.
4. Do not click APPLY WITH AUTOFILL. That is Jobright's product, not the employer ATS.
5. Follow one redirect if Original Job Post needs it.
6. Continue only if the destination is the same company and the same intern role, and the host is not jobright.ai.
7. Stop and report if the destination is a different role, a closed or 404 page, LinkedIn only, a generic careers home with no this requisition, or any other unusable page. Do not open Quantitative Researcher, Quantitative Developer, or any sibling.

EMPLOYER APPLICATION
8. Use the existing logged-in session. Do not create a Greenhouse, Workday, or MyGreenhouse account. If an account wall appears, stop and report.
9. If Simplify Copilot is available, run Autofill once. Never Run Autofill Again. Never click Generate with AI.
10. Look at the visible form, not the Copilot sidebar. Correct mismatches using ONLY the answers below.
11. Click required privacy / I agree squares.
12. Leave cover letter empty.
13. If a required free-response or Why-us box has no approved text below, leave it empty, list it as unresolved, and do not invent an essay.
14. Stop immediately before Submit. Do not click Submit, Apply, or Finish application.

IDENTITY AND STANDING ANSWERS
Use Simplify for phone and email. Do not invent a different name, phone, or email.
- Legal name: Junyi Zhou
- Preferred name: Junyi
- Location: Boston, MA
- LinkedIn: https://www.linkedin.com/in/junyi-zhou-270208247
- GitHub: https://github.com/JunyiZhou-Conny
- Website: https://connyzhou.com
- School now: Harvard T.H. Chan School of Public Health, SM in Health Data Science
- Program end / graduation date widget: 2026-12-18
- Year-only graduation widget: 2027
- Commencement if they ask for ceremony: March 2027
- Undergrad: Emory University, B.S. Applied Mathematics and Statistics, minor Computer Informatics, end May 2025, GPA 3.925
- Harvard / current / single GPA box: 4.0
- Do not invent SAT, ACT, or another GPA
- Earliest full-time start: 2027-01-18
- This intern start: Summer 2027. If they want a date and the posting names June to August, use June 2027 or 2027-06-01
- Open to relocate: Yes
- Work on site / committed office schedule: Yes
- Location picker: pick one US option that unblocks the form. Prefer New York if listed
- Employed by this company before: No
- Prior internship or co-op in general: Yes
- Prior internship at Quantbot: No
- Number of prior internships: 2
- Years of relevant experience: 2
- How did you hear: LinkedIn. Prefer LinkedIn Job Board if that option exists
- Applying via automated script or spoofing: No
- Authorized to work in the US for any employer: Yes
- Need visa sponsorship now or in the future: No. Also accept "No, I do not need sponsorship" or None
- Current visa type if asked: F-1
- Citizenship / nationality / export-control country: China
- Permanent resident elsewhere since citizenship: No
- Eligible to begin employment immediately: Yes
- U.S. Person / ITAR / EAR: I am not a U.S. Person
- Disability: No / I do not have a disability
- Other EEO (gender, Hispanic/Latino, race, veteran): keep whatever Simplify Copilot filled. Do not change those four if they already match Male, No, Asian, not a protected veteran
- Education discipline: prefer Data Science, then Computer Science, then Mathematics. Not Other if those exist
- Salary if the page shows a range: type the listed minimum only. Public indexes have listed 180000 to 200000. If that range is on the page, type 180000. If the page has no number, type 90000. Do not invent a higher number
- Engineering interest if asked: backend, then platform, then cloud, then infrastructure, then ML, then AI

DO NOT INVENT
GPA beyond 4.0 / 3.925. Citizenship other than China. Sponsorship Yes. A project URL. Finance-domain experience. Quantbot employment. FDE or customer-on-site work. CellOT, VLM, CV, or the Emory airway project name. A cover letter. A Why-us or project essay. A sibling job.

STOP
Ready means the intended Quantbot intern application is open, standing fields are filled or listed as unresolved, and Submit has not been clicked.

REPORT (plain text, this shape only)
- company
- role
- starting URL
- Original Job Post used: yes/no
- final application URL / host
- posting matched intended role: yes/no
- Simplify used: yes/no
- corrections Polar made
- unresolved required fields
- ready to submit: yes/no
- submitted: yes/no
- if stopped, exact reason
- any CAPTCHA / authentication / anti-abuse issue
- approximate elapsed time if you have it

One or two final screenshots are enough if easy. Do not hunt for a pretty crop.
````
