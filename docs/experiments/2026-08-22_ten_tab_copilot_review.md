# Live 10-tab Copilot review — 2026-08-22

Same 10 employers as `docs/experiments/2026-08-18_ten_tab_review.md`.
Chrome + Simplify Copilot on this Cloud Agent. **Nothing submitted.**

Harness on this VM (updated checker): `ready: true`. Copilot id
`pbanhockgagggenencehbnadejlgchfc`. Session cookie present.

Stop rules held: no Submit, no accounts, no MyGreenhouse login, no
invented essays typed by the agent.

## Session identity

Copilot used Junyi Zhou, Harvard HSPH email, phone +1 404-663-5601,
LinkedIn `junyi-zhou-270208247`, resume `Junyi_Zhou_resume.pdf`. That
matches `config/profile.yaml`. The checker still reports
`identity_match: unknown` (it does not decrypt cookies). Glance the
Simplify dashboard if you want a second confirmation.

A tab titled “Thank you for applying” is Copilot’s local tutorial page
(`chrome-extension://…/tutorial/submitted.html`), not an employer
confirmation.

## Results (autofill only)

| # | Company | Requisition | Identity / résumé | Essays | EEO | Work auth / sponsorship | Submit |
|---|---|---|---|---|---|---|---|
| 1 | OpenAI | match | name, email, phone, Boston, resume | left for review | **filled** (gender, race, veteran, disability) | Copilot marked work auth completed (not re-read on the still) | unclicked |
| 2 | Etched | match | name, email, phone, resume | left empty | none visible | **wrong: US Citizen or Permanent Resident selected** | unclicked |
| 3 | Bild AI | match | name, email, resume (phone digit not confirmed on a still) | left for review | none visible | computer-use said Copilot completed sponsorship — **unverified** | unclicked |
| 4 | Traba | match | name, email, LinkedIn, resume | empty (correct) | none visible | left in need-review (correct) | unclicked |
| 5 | Neuralink | match | first/last, email, phone, Harvard + Emory, resume | 10 fields need review (ability examples, season, start) | none visible on the still | not visible on the identity still | unclicked |
| 6 | Gemini | match | LinkedIn exact, education Master’s, resume | none | none on form | **Work authorization Yes; Visa sponsorship No** | unclicked |
| 7 | Nirmata | match | name, email, phone, LinkedIn, resume | none | **filled** (male, not Hispanic, Asian, not veteran; disability section opened) | **H-1B sponsorship No** | unclicked |
| 8 | Apptronik | match | name, email, phone, Boston, LinkedIn, resume | none | computer-use reported Copilot filled gender/veteran/disability | citizenship / ITAR left in need-review (correct) | unclicked |
| 9 | Together AI | **posting closed** | n/a | n/a | n/a | n/a | n/a |
| 10 | SpaceX | match | computer-use reported identity + resume | 13 need review (GPA, tests, clearance, citizenship) | veteran dropdown filled (“not a protected veteran”); disability listed need-review | citizenship listed need-review | unclicked |

Together Fall 2026 URL now shows “The job you are looking for is no longer open.”
No replacement was opened.

## What Copilot gets right

- Attaches to branded Chrome on this snapshot.
- Hits the intended employer + title when the URL is still live (9/10).
- Fills name, email, phone, LinkedIn, and uploads `Junyi_Zhou_resume.pdf`.
- Leaves most essays / “why us” / salary / source-of-hire empty.
- Does not click Submit.
- Greenhouse “Autofill my application” (MyGreenhouse) was not used.

## What Copilot gets wrong (evidence)

1. **EEO** — OpenAI, Nirmata, and SpaceX (veteran). A later Automation must
   **refuse Submit** when EEO is touched, even if Copilot filled them.
2. **Work authorization** — Etched selected US citizen / permanent resident.
   Profile is F-1; future sponsorship is needed. Hard-fact miss.
3. **Sponsorship “No”** — Gemini visa sponsorship and Nirmata H-1B were set
   to No. That may be wrong for “now or in the future.” Human review before
   any real apply.
4. **Education widgets (Etched)** — college, major, and GPA all received the
   same blob: `08/2025 - 03/2027 Studied Health Data Science at Harvard
   University Master`. Expected graduation date stayed empty.
5. **Closed requisitions** — resolver URLs go stale (Together). The apply
   loop must re-resolve or skip, not submit a sibling job.

## Artifacts

- `/opt/cursor/artifacts/tab01_openai_after_copilot.webp`
- `/opt/cursor/artifacts/tab02_etched_education_misfill.webp`
- `/opt/cursor/artifacts/tab02_etched_work_auth_misfill.webp`
- `/opt/cursor/artifacts/tab04_traba_after_copilot.webp`
- `/opt/cursor/artifacts/tab05_neuralink_after_copilot.webp`
- `/opt/cursor/artifacts/tab06_gemini_sponsorship_no.webp`
- `/opt/cursor/artifacts/tab07_nirmata_h1b_no.webp`
- `/opt/cursor/artifacts/tab07_nirmata_eeo.webp`
- `/opt/cursor/artifacts/tab08_apptronik_after_copilot.webp`
- `/opt/cursor/artifacts/tab09_together_closed.webp`
- `/opt/cursor/artifacts/tab10_spacex_eeo.webp`

## Next

See `docs/automation/WEEKDAY_APPLY_AUTOMATION.md`. Do not build a Playwright
fallback until a later decision. Do not Submit from this review.
