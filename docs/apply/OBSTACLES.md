# Autofill obstacle notebook

Canonical facts and open asks: `knowledge/autofill_obstacles.yaml`.

This is the dedicated place to record **why Copilot cannot finish a form
without a human**. It is not a second application ledger. It is not
permission to Submit.

There was no single notebook before 2026-08-23. Nearby pieces:

| Place | What it holds |
|---|---|
| `config/profile.yaml` | Name, school, Emory GPA 3.925, dates |
| `knowledge/work_authorization.yaml` | F-1, OPT timing, typical auth answers |
| `auth_qa_notes` on `data/applications.csv` | Verbatim Q&A **after** a real apply |
| `docs/experiments/2026-08-22_ten_tab_copilot_review.md` | Session evidence |

When a form blocks full automation, add a `gaps` row in the YAML. Ask
Junyi later. Write the confirmed value into profile / auth / evidence
bank. Do not invent GPA, test scores, clearance, or citizenship.

## Closed posting (decisive)

If the apply URL is gone (“no longer open”, Greenhouse `?error=true`
board, 404): **close the tab**, do not pick a sibling from Current
openings, and write `decision=closed` in `data/job_decisions.csv`.
Together AI Fall 2026 (`jobs/5157661007`) is the first logged case.
This will happen often; high-volume roles close in minutes.

## Two memories: repo vs Simplify Copilot

**Copilot here means Simplify Copilot** (the Chrome extension), not Cursor
and not this Cloud Agent.

They do not share a profile.

| Memory | What it is | What it filled on SpaceX |
|---|---|---|
| Simplify Copilot | Logged-in extension on this VM | Name, school, resume, LinkedIn. Left undergrad GPA blank. |
| This repo | `config/profile.yaml` and `knowledge/` | Already has Emory GPA **3.925**. Cursor did not type it onto the form. |

A fact in git does not appear on an ATS page unless it is also in the
Simplify profile, or a later agent types a **verified** repo value on
purpose. Writing 3.925 only in YAML is not enough for unattended apply.

## What Junyi confirmed on SpaceX (2026-08-23)

New Graduate Engineer, Software. Copilot ran. Submit unclicked.

**Already good:** name, email, phone, resume, location, school, Emory
bachelor’s in mathematics, LinkedIn, how-you-heard = LinkedIn. EEO /
veteran / disability looked correct to Junyi.

**Need-review list matched the empty form (13 items).** That alignment is
the useful signal: Copilot left gaps instead of guessing SAT, GPA,
clearance, or citizenship.

**Still empty / wrong enough to block unattended Submit:**

- Undergrad GPA empty even though `3.925` is already in `config/profile.yaml`
- Graduate and doctorate GPA empty (not in the repo)
- SAT / ACT empty (Junyi has scores; not in the repo yet)
- Active security clearance empty
- SpaceX employment history empty
- Essential functions / reasonable accommodation empty
- Citizenship empty (repo knows F-1; do not pick US citizen)
- Discipline optional and “kind of not correct”

Ask-later wording lives in the YAML. Do not paste scores into chat until
Junyi is ready to put them in the bank.

## What Junyi confirmed on Apptronik (2026-08-23)

Robotics Software Intern – Real-Time Controls. Copilot ran. Submit
unclicked.

**The 3 need-review items are OK.** They are lawful / work-authorization
status, citizenship, and eligibility to contract with or receive US
government licenses. Those need more attention than name and email.
Leaving them flagged is the desired stop.

**Also noted:**

- LinkedIn filled.
- Disability filled.
- Veteran left empty (Junyi: nice — did not invent).
- Hispanic or Latino empty here, but filled on SpaceX the same day.
  EEO is not stable across forms.
- No cover letter. Expected; none was requested. Later decision.
- Website empty. Junyi may build a personal project site later. Do not
  invent a URL. GitHub is already in the profile.

## EEO inconsistency (same session)

| Field | SpaceX | Apptronik |
|---|---|---|
| Hispanic or Latino | filled (Junyi: looks correct) | empty |
| Veteran | filled | empty (Junyi: nice) |
| Disability | filled | filled |

Do not assume the next Greenhouse form will match the last one.

## What Junyi confirmed on Nirmata (2026-08-23)

AI Software Engineer Intern. Sidebar: Autofill complete, nothing in
need-review. Submit unclicked. Junyi said the rest looks perfect because
the form has no long written answers.

**H-1B field was No.** Junyi wants that on every form that asks
specifically “Will you require H-1B sponsorship?” Written as form
strategy in `knowledge/work_authorization.yaml`. The fact file still
says future employer sponsorship is expected. Broader “now or in the
future require sponsorship?” is still Yes / do not answer No.

## What Junyi confirmed on Gemini (2026-08-23)

Design Developer. Cover letter and website empty (expected; later).
H-1B No (wanted).

New always-rules (`knowledge/form_strategy.yaml`):

- “Have you been employed by this company before?” → **No**
- “Are you open to relocating?” → **Yes**
- Required privacy / I-agree squares → **click every time**, then stop.
  Simplify often skips these. Computer-use (same Chrome as Copilot)
  clicks them. Do not Submit after the click unless Junyi names that row.

## What Junyi confirmed on Neuralink (2026-08-23) — rules only, no redo

Machine Learning Engineer Intern. Copilot: 10 need review. Submit
unclicked. Do not click Simplify **Generate with AI** (paid).

New always-rules (same file):

- Short/long written answers → Cursor writes them from
  `knowledge/evidence_bank.yaml`. Quantitative, no invented metrics.
  If evidence is missing, leftover pile.
- Prior internship/co-op (no company named) → **Yes**
- Internship/co-op at **this** company or a named affiliate → **No**
- Graduation year → **2027**
- On-site / “I understand I must work on-site” → **Yes**
- Ideal start date → JD term if present, else **2027-05-18**
- How did you hear → **LinkedIn** is fine
- Interest / preference questions → leave for Junyi

Later target he described: most forms fluent, a leftover set for him,
then a digest (counts + agent Take Control link). Do not email that
digest until he confirms send.

## What Junyi confirmed on Traba (2026-08-23) — first written-answer test

Software Engineer (AI Agents), Ashby. Speech-to-text said “Trava.”
Submit unclicked. Application-limits box: 100-day reapply lock.

New always-rules / archive:

- Salary / expected pay → **JD minimum if the page lists a range**
  (this page: $140K–$200K → `140000`). If the page has no number →
  **90000**.
- Relocate / NYC 5x a week → still **Yes**.
- Why-company and week-structure essays → Cursor writes them. Archive
  every draft in `docs/apply/written_answers/`. Ideology:
  `knowledge/written_response_bank.yaml`.
- How-heard empty after Copilot → computer-use ticks **LinkedIn Job
  Board** on the same Chrome. Do not leave it.

Never click Simplify **Generate with AI**. Do not Submit this test
(100-day lock).

## Round two (2026-08-23) — new obstacles

Ten unused employers. Notes:
`docs/experiments/2026-08-23_ten_tab_round_two.md`. Nothing submitted.

**Workday account wall (CVS Health).** Data Science Analyst
`R0993501-1` stopped at account creation. Tab closed. No account
created. This is not a closed posting and not a sibling hunt.

**U.S. Person / ITAR (Relativity Space).** Copilot picked the U.S.
Person side. Profile is F-1. Computer-use set “I am not a U.S. Person.”
Standing rule in `knowledge/form_strategy.yaml`.

**Broad sponsorship No (again).** Lila, Hayden, Relativity, and Scale
all used “now or in the future” with H-1B as an example. Copilot said
No. Computer-use said Yes. H-1B-**named-only** questions stay No.

**Any-employer work auth (Hayden AI).** Copilot Yes. F-1 is not that.
Leftover. Do not silently flip it.

**Country-named sponsorship (Perplexity).** UK / Germany / Serbia, role
in Belgrade. Copilot No. Do not apply the US Yes rule. Also a pick miss:
Belgrade is outside `search.country: United States`.

**Perplexity exercise URL.** Required shared thread. Left empty. Do not
invent one. Junyi 2026-08-24: non-standard apply hold. Do not Submit.
Daily digest must list these. `knowledge/nonstandard_apply_holds.yaml`.

**Past-project dump.** Perplexity draft listed several projects. Junyi:
one story, matched to company type. Bank is empty until he writes it.
`knowledge/project_stories.yaml`.

**Hayden 90 / 182-day lock.** Do not Submit this test.

**EEO filled** on Hayden, Baseten, Relativity, Scale, Notion. Block
unattended Submit.

**Notion (Ashby) 2026-08-24.** Anchor Days / committed → Yes. Relocate
→ Yes. Location interest → pick one US option. Visa type → F-1.
Future sponsorship → No / None. Prior internships → 2. Role type →
closest fit or any that unblocks. Graduation date → 2026-12-18.
How-heard → LinkedIn or any option that unblocks.

**Scale AI sponsorship.** Computer-use had flipped the future-
sponsorship widget to Yes. Junyi 2026-08-24: that is wrong. Standing
answer is No / None. Not re-clicked from the note.

**Run Autofill Again clears corrections.** After leftover essays were
typed, a second Autofill reset Lila Yes dropdowns and flipped Baseten
sponsorship to No. Re-set. Do not click it after a human/computer-use
pass.

## Lila evening review (2026-08-23) — no re-click

Junyi reviewed the Lila tab. Nothing was re-clicked.

**Sidebar ≠ form.** Copilot said phone country, phone, and resume were
complete. They were empty. Future pass: look at the widgets. Cover
letter empty is expected.

**Why Lila was a miss.** The typed draft answered a resume prompt that
was not on the page. Cause: `written_responses.style` plus the Traba
ideology pack reused as a Why-company template. New rule: answer the
prompt, ardent / genuine / truthful, no project dump.

**Lila is prioritized.** GTC 2026 Exhibitor (already in
`knowledge/market_signals/gtc2026_sponsors_exhibitors.md`) plus Junyi
emphasis. Hold public Submit until a referral / insider page is checked.
See `knowledge/application_priority.yaml` and `docs/apply/PRIORITY.md`.

## Hayden inspect (2026-08-24) — no re-click

Junyi reviewed the Hayden AI Associate Data Scientist tab. Screen
checked only. Nothing clicked.

**Start date rule worked.** Sidebar still flags “When can you start a
new role” as the one need-review. The widget is `05/18/2027`. Copilot
did not fill it; computer-use on the same Chrome did (not Playwright).

**Years of relevant experience** is empty. Future answer: **2**.

**Visa sponsorship** widget is **Yes** (old flip). New form answer:
**No, I do not need sponsorship**. Re-read before any Submit.

**Automated script / spoofing:** sidebar says complete; neither radio
is selected. Future answer: **No**.

**Why Hayden** still formulaic. Rewrite later (company values / culture
+ Junyi’s philosophy). Cover letter empty is fine.

## Leftover typing over-click (Charta 2026-08-24)

Junyi asked to paste accepted Why Charta v2. He would Submit.

The first computer-use pass put the text in the box. The parent then
started a second pass (Ctrl+F / scroll) and a third (blank line). That
is the waste. Not a Copilot miss.

Rule: one paste, one screenshot, stop.
`knowledge/form_strategy.yaml` `leftover_typing_one_pass`.
Parent copies `docs/automation/COMPUTER_USE_PROMPT.md`. Do not ask the
clicker to Ctrl+F or prove a cropped textarea.

Other computer-use token sinks (nested Task with no clicker, vision
full-apply stills, parent screenshot audits, huge screen recordings)
are listed under `computer_use_token_sinks` in
`knowledge/form_strategy.yaml`. The Why-us loop has a fix. A DOM fill
does not.

## Ashby submit blocked as possible spam (Charta 2026-08-24)

Junyi hit Ashby’s candidate-facing page: “We couldn’t submit your
application… flagged as possible spam,” with VPN / pause extensions /
other browser / switch networks.

That is a **submit-time block**. The application did not land. It is
not a Why-us word limit.

Two different Ashby layers (do not collapse them):

1. **Recruiter fraud detection** (Ashby, 2025-09-16 product): scans
   device, IP, email, phone after a successful submit. Ashby’s blog
   says it should not add candidate friction.
   https://www.ashbyhq.com/blog/all/ashby-launches-the-first-ats-integrated-fraud-detection-system
2. **This pink error** is a bot/spam wall on Submit. Same wording
   reported by other applicants (e.g. Norton community). Triggers
   include VPN/proxy, privacy extensions, odd IP reputation.

This Cloud Chrome is a bad Submit path: datacenter IP, Simplify
Copilot, computer-use clicks, many ATS tabs.

Do: wait, Submit from Junyi’s own machine, pause Copilot, no VPN,
prefer home or mobile data. Do not keep retrying on the already
blocked VM. Do not invent a bypass.

2026-08-24: Junyi submitted Charta from his laptop after the Cloud
block. Isolation test (new pod, different Ashby org, one Submit):
`docs/experiments/2026-08-24_ashby_submit_isolation.md`.

First nested child: harness ready, no computer-use, `not_run`.
Dashboard agent `bc-b6ea9703-f8db-491d-98ab-52b490155db1`: Autofill
once, Submit once on Anyscale Software Engineer (Ray Core). Ashby
thank-you: “Success. Your application was successfully submitted.”
No pink spam wall. Outcome `submitted`. Cloud Submit is no longer a
one-sample failure. Still do not mass-Submit from Cloud Chrome. Do
not retry Charta on the blocked parent session.
