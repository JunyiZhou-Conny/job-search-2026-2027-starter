# Live 10-tab Copilot review — round two — 2026-08-23

Second autofill test after the first 10-tab session. **Nothing submitted.**

First-round companies (do not reuse): OpenAI, Etched, Bild AI, Traba,
Neuralink, Gemini, Nirmata, Apptronik, Together AI, SpaceX.

Harness: `python3 scripts/automation/check_apply_harness.py` → `ready: true`.
Copilot id `pbanhockgagggenencehbnadejlgchfc`. Same Chrome profile.

## Tab list (resolved 2026-08-23)

Public board APIs only. No invented URLs. Skip 2026 intern cycles.

| # | Company | ATS | Role | Apply URL |
|---|---|---|---|---|
| 1 | MeshyAI | Ashby | Fullstack Engineer Intern | https://jobs.ashbyhq.com/meshy/262d74c7-8aab-474e-9fc6-8c8c48ec6572 |
| 2 | CVS Health | Workday | Data Science Analyst | https://cvshealth.wd1.myworkdayjobs.com/CVS_Health_Careers/job/NY---New-York/Data-Analyst_R0993501-1 |
| 3 | Lila Sciences | Greenhouse | Software Engineer I, Instrument Software | https://job-boards.greenhouse.io/lilasciences/jobs/4186444009 |
| 4 | Hayden AI | Ashby | Associate Data Scientist | https://jobs.ashbyhq.com/haydenai/6951fb04-478b-46f5-b918-123a69a28925 |
| 5 | Baseten | Ashby | Software Engineer - Dedicated Inference | https://jobs.ashbyhq.com/baseten/fc6e5f2e-eb2d-4a6c-8a51-8422e8662bde |
| 6 | Charta Health | Ashby | Forward Deployed AI Engineer | https://jobs.ashbyhq.com/chartahealth/3088555d-de93-4236-add1-41005bf0933b |
| 7 | Relativity Space | Greenhouse | AI Software Engineer | https://job-boards.greenhouse.io/relativity/jobs/8726261002 |
| 8 | Scale AI | Greenhouse | AI Builder Intern | https://job-boards.greenhouse.io/scaleai/jobs/4703343005 |
| 9 | Notion | Ashby | Software Engineer Intern (Summer 2027) | https://jobs.ashbyhq.com/notion/3fba1c39-c5cb-47d7-9ad2-1cec4d7e9d0c |
| 10 | Perplexity | Ashby | Internship - Search Machine Learning Engineer | https://jobs.ashbyhq.com/perplexity/9246cf02-26fd-4ae8-90c5-639c6e85e9e2 |

## Supervised rules (do not skip)

From `knowledge/form_strategy.yaml` + `knowledge/written_response_bank.yaml`:

- Do not Submit / Apply (final). Do not click Simplify Generate with AI.
- Relocate / in-person → Yes.
- H-1B-**named** → No. Broad “now or in the future require sponsorship?” → Yes.
- Salary: page minimum if listed, else 90000.
- How-heard empty → computer-use ticks LinkedIn (same Chrome).
- Written answers: Cursor writes from evidence bank; archive in
  `docs/apply/written_answers/`.
- Closed posting → close tab, `decision=closed`, do not pick a sibling.
- Privacy / I-agree squares → click, then stop.
- EEO touched → block Submit.

## Results

Live pass on this VM, 2026-08-23. First-round Chrome tabs were closed first.
Harness still `ready: true`. **Nothing submitted.** Generate with AI not clicked.
Round-two tabs left open for Take Control.

| # | Company | Requisition | Identity / résumé | Essays / leftovers | EEO | Work auth / sponsorship | Submit |
|---|---|---|---|---|---|---|---|
| 1 | MeshyAI | match (Ashby intern, Bay Area on-site) | name, email, `Junyi_Zhou_resume.pdf` | none (short form) | none visible | none visible | unclicked |
| 2 | CVS Health | Workday account-creation wall | n/a | n/a | n/a | n/a | n/a — tab closed |
| 3 | Lila Sciences | match | name, Harvard email, phone, resume | **Why Lila** empty (1 need-review). Preferred first name empty | Privacy notice filled | Copilot set sponsorship **No**; computer-use corrected to **Yes** (broad, names H-1B as example). US reside Yes. Relocate Yes | unclicked |
| 4 | Hayden AI | match | name, email, phone, LinkedIn, resume | Preferred first name empty. Why Hayden empty. First-job leftover. Start date typed **2027-05-18**. Cover letter empty | **filled** (gender, Asian, veteran) | Relocate own-expense Yes. Commute 3x Yes. **Any-employer work auth = Yes (questionable for F-1 — leftover).** Broad sponsorship **Yes** (Copilot had No; corrected) | unclicked. 90/182-day reapply lock |
| 5 | Baseten | match | name, email, phone, LinkedIn, resume | **2 leftovers:** why Baseten; developer-facing APIs/SDKs/CLI | **filled** (Asian, veteran) | Work auth + visa sponsorship marked completed by Copilot (not re-read as wrong after the pass) | unclicked |
| 6 | Charta Health | match | identity + resume filled | **5 leftovers:** onsite 5x SF/NYC; office choice; languages; customer-facing exp; Why Charta | not re-read on a still | range on page $90k–$140k | unclicked |
| 7 | Relativity Space | match | name, Boston, resume, LinkedIn | **2 leftovers:** sponsorship/export explanation; Why Relativity | **filled** (Hispanic No, Asian, veteran, disability) | Copilot set **U.S. Person** (wrong). Corrected to **I am not a U.S. Person.** Broad sponsorship (H-1B/TN-etc) Copilot **No** → **Yes**. Onsite Long Beach 5x **Yes**. Source LinkedIn | unclicked |
| 8 | Scale AI | match | name, email, phone, location, resume, LinkedIn | **1 leftover:** “If yes, please provide further explanation below” (conditional; left empty) | **filled** (gender, Hispanic, ethnicity Asian, veteran, disability) | Broad sponsorship Copilot **No** → **Yes** | unclicked |
| 9 | Notion | match (Summer 2027 intern) | name, email, phone, resume, LinkedIn | **7 need-review after Copilot:** Anchor Days; relocate NYC/SF; location interest; sponsorship **type** multi-select; role type; AI tech; Why Notion. Relocate later set **Yes** | **filled** (gender Male; veteran not protected) | Sponsorship is a **type** multi-select (H-1B / OPT / etc.), left unselected | unclicked |
| 10 | Perplexity | match, but **Belgrade** location | name, email, phone, resume, location, GitHub | **4 leftovers:** past project; why Perplexity; how you use AI; 2-year contact. Exercise **Shared URL** empty (do not invent). Generate with AI visible, not clicked | none visible | Sponsorship is **UK / Germany / Serbia** (not US). Copilot **No**. Office 3x **Yes**. I-agree clicked | unclicked |

CVS is not a closed posting. It is a **do-not-create-accounts** stop. No sibling Workday job was opened.

Perplexity Search ML intern is posted from Belgrade. That is outside `search.country: United States`. Recorded as a pick miss for this test, not as a US apply.

## What Copilot gets right (this round)

- Hits the intended employer + title when the URL is live (9/10; CVS blocked before the form).
- Fills name, Harvard email, phone, LinkedIn, GitHub (when asked), and `Junyi_Zhou_resume.pdf`.
- Leaves Why-us / essays empty instead of guessing.
- Does not click Submit.
- Hayden human-check (“select the THIRD option”) and “automated script” were filled.
- Meshy short form: Autofill complete with no need-review.

## What Copilot gets wrong (this round)

1. **Broad sponsorship → No** — Lila, Hayden, Relativity, Scale. All name H-1B as an *example* inside a “now or in the future” question. Standing rule is **Yes**. Computer-use corrected those four.
2. **U.S. Person** — Relativity Copilot picked the ITAR “U.S. Person” side. Profile is F-1. Corrected to **I am not a U.S. Person.**
3. **Authorized for any employer** — Hayden Copilot Yes. F-1 is not a blanket any-employer authorization. Do not treat that Yes as verified. Leftover for Junyi.
4. **Country-specific sponsorship** — Perplexity asks UK / Germany / Serbia, not the US. Copilot No. Do not map that onto the US Yes rule.
5. **EEO filled** — Hayden, Baseten, Relativity, Scale, Notion. Block unattended Submit.
6. **How-heard / relocate** — Notion relocate left empty until computer-use set Yes. Relativity source showed LinkedIn completed.
7. **Workday wall** — CVS asked for an account. Tab closed. No account created.

## Salary numbers on the page (do not invent a higher ask)

| Company | Page / Copilot range | If a salary field appears, type |
|---|---|---|
| MeshyAI | $40–$50 / hour | `40` (hourly minimum) |
| Lila | $108,000–$140,000 | `108000` |
| Hayden AI | $120,694–$156,920 | `120694` |
| Baseten | $165,000–$330,000 | `165000` |
| Charta Health | $90,000–$140,000 | `90000` |
| Relativity | $115,000–$173,000 | `115000` |
| Scale AI | $74,400–$93,000 | `74400` |
| Notion | $57–$61 / hour | `57` |
| Perplexity | none read on the stills | `90000` if a field appears |
| CVS | n/a | n/a |

No numeric salary widget was typed on this pass except where a start-date widget existed (Hayden `2027-05-18`).

## Written-answer archives

Drafts from `knowledge/evidence_bank.yaml` + `knowledge/written_response_bank.yaml`.
A later pass on the same Chrome **typed** the leftover Why-us / essays.
`form_status` is now `typed_on_form`. **Still not submitted.**

Do not click **Run Autofill Again** after corrections. A later Autofill
cleared Lila's Yes dropdowns back to Select… and flipped Baseten
sponsorship back to No. Both were re-set.

| File | Leftovers covered |
|---|---|
| `docs/apply/written_answers/2026-08-23_lila-swe-i-instrument.md` | Why Lila |
| `docs/apply/written_answers/2026-08-23_hayden-associate-data-scientist.md` | Why Hayden, preferred name, first job |
| `docs/apply/written_answers/2026-08-23_baseten-swe-dedicated-inference.md` | Why Baseten, APIs/SDKs/CLI |
| `docs/apply/written_answers/2026-08-23_charta-forward-deployed-ai.md` | Why Charta, onsite, leftovers |
| `docs/apply/written_answers/2026-08-23_relativity-ai-swe.md` | Why Relativity, export/sponsorship explanation |
| `docs/apply/written_answers/2026-08-23_scale-ai-builder-intern.md` | Conditional explanation leftover |
| `docs/apply/written_answers/2026-08-23_notion-swe-intern-summer-2027.md` | Why Notion, AI tech, role type |
| `docs/apply/written_answers/2026-08-23_perplexity-search-ml-intern.md` | Project, why Perplexity, AI usage; no exercise URL |

Meshy had no free-response. CVS never reached a form.

## Artifacts

- `/opt/cursor/artifacts/round_two_first_five_tabs.mp4`
- `/opt/cursor/artifacts/r2_meshy_autofill_complete.webp`
- `/opt/cursor/artifacts/r2_lila_sponsorship_yes.webp`
- `/opt/cursor/artifacts/r2_hayden_sponsorship_yes.webp`
- `/opt/cursor/artifacts/r2_baseten_eeo_two_leftovers.webp`
- `/opt/cursor/artifacts/r2_relativity_not_us_person_sponsorship_yes.webp`
- `/opt/cursor/artifacts/r2_scale_one_leftover.webp`
- `/opt/cursor/artifacts/r2_notion_seven_leftovers.webp`
- `/opt/cursor/artifacts/r2_perplexity_four_leftovers.webp`
- `/opt/cursor/artifacts/r2_lila_why_and_sponsorship_yes.webp`
- `/opt/cursor/artifacts/r2_baseten_sponsorship_yes_why_typed.webp`
- `/opt/cursor/artifacts/r2_relativity_why_typed_linkedin.webp`
- `/opt/cursor/artifacts/r2_hayden_why_typed.webp`
- `/opt/cursor/artifacts/r2_notion_ai_tech_typed.webp`

## Next

Tabs stay open for Take Control. Do not Run Autofill Again.
Do not invent a Perplexity exercise URL. Do not create a Workday account.
Leftovers that stay leftovers: Hayden any-employer; Notion sponsorship
type + role-type checkboxes; Perplexity exercise URL; Charta SF office
radio; Scale conditional explanation.

Junyi 2026-08-24: Relativity Space is export-compliance / rocket
science. Keep in mass apply. Do not filter out. No need to submit.
Why Relativity is known bad and left as is. Form fill otherwise fine.

Junyi 2026-08-24: type Charta Why-us v2 onto the Ashby tab. He will
Submit that one himself. Agent does not click Submit.
