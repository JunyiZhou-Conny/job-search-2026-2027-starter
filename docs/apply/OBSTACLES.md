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
