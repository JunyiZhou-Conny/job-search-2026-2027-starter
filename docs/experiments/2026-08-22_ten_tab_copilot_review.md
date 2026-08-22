# Live 10-tab Copilot review — 2026-08-22

Same 10 employers as `docs/experiments/2026-08-18_ten_tab_review.md`.
Chrome + Simplify Copilot on this Cloud Agent. **Nothing submitted.**

Harness on this VM (073b checker): `ready: true`. Copilot id
`pbanhockgagggenencehbnadejlgchfc`. Session cookie present.

Stop rules held: no Submit, no accounts, no MyGreenhouse login, no
invented essays typed by the agent.

## Session identity (from filled forms, not guessed)

Copilot used Junyi Zhou, Harvard HSPH email, phone +1 404-663-5601,
resume `Junyi_Zhou_resume.pdf`. That matches `config/profile.yaml`.
Glance the Simplify dashboard if you want a second confirmation; the
checker still reports `identity_match: unknown`.

A tab titled “Thank you for applying” is Copilot’s local tutorial page
(`chrome-extension://…/tutorial/submitted.html`), not an employer
confirmation.

## Scores so far (autofill only)

| # | Company | Requisition | Identity | Résumé | Essays | EEO | Work auth | Submit | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenAI | match | name/email/phone/location correct | `Junyi_Zhou_resume.pdf` | left for review | **Copilot filled** gender/race/veteran/disability | Copilot marked completed (not independently re-read) | unclicked | 6 fields need review (start date, 3 days in office, arbitration, cert) |
| 2 | Etched | match | name/email/phone correct | uploaded | left empty (correct) | none visible | **wrong: US Citizen or Permanent Resident selected** | unclicked | College/Major/GPA all got the same blob: `08/2025 - 03/2027 Studied Health Data Science at Harvard University Master`. Grad date empty. 9 fields need review |
| 3 | Bild AI | match | name/email reported; phone digit not verified from a still | uploaded | left for review | none visible | computer-use reported Copilot completed sponsorship as No — **unverified** | unclicked | 2 fields need review (SF 5 days, additional info) |
| 4 | Traba | match | name/email/LinkedIn/resume completed per Copilot | uploaded | empty (correct) | none visible | left in need-review (correct) | unclicked | salary, NYC, why Traba, source left empty |
| 5–10 | Greenhouse | not run yet | | | | | | | |

## What Copilot already gets wrong (evidence)

1. **EEO on OpenAI** — Copilot selected gender, race, veteran, and
   disability. A later apply Automation must refuse Submit when EEO is
   touched, even if Copilot filled them.
2. **Work authorization on Etched** — selected US citizen / permanent
   resident. Profile is F-1; future sponsorship is needed. This is a
   hard-fact miss.
3. **Education widgets on Etched** — dumped one date/school string into
   college, major, and GPA.
4. **Job-specific and essay fields** — left for review. Correct behavior
   for this trial; do not invent answers.

## Tabs 5–10

Not started in this file yet.
