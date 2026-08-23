# Weekday apply Automation — design (stop before Submit)

**Status:** design only. Not enabled. Not authorized to Submit.
**Audience:** Junyi + the Cloud Agent that will run this Automation.
**Depends on:** personal environment with Chrome + Copilot already on disk
(`docs/experiments/2026-08-21_harness_snapshot_clone.md`). Daily discovery
does **not** use this harness.

---

## What this Automation is

A weekday Cloud Agent that:

1. Boots the **saved personal environment** (default, no pinned build id).
2. Fails closed if the harness checker is not `ready`.
3. Takes already-resolved employer apply URLs (not Jobright signup walls).
4. Opens them in **Google Chrome** and lets **Simplify Copilot** fill.
5. Screenshots the form, writes a review row, **stops**.
6. Leaves Submit for Junyi.

It is not a second Simplify tracker. It does not send outreach. It does not invent metrics. Written answers come from the evidence bank
or go to leftovers. It does not click Greenhouse MyGreenhouse. It does
not click Simplify Generate with AI.

---

## Fail closed

Before any ATS tab:

```bash
python3 scripts/automation/check_apply_harness.py
python3 scripts/automation/check_apply_harness.py --json
```

- Exit 1 → stop. Report Copilot vs session vs wrong browser. Do not type
  identity by hand. Do not treat MyGreenhouse as Simplify.
- `ready: true` → continue. `identity_match: unknown` is expected; glance
  the dashboard when you care.

Computer-use must stay on `/opt/google/chrome/chrome` and
`~/.config/google-chrome` until a later written decision changes that.

---

## Input (from discovery, not from chat memory)

For each candidate row, require:

| Field | Rule |
|---|---|
| `apply_url` | Employer ATS (Ashby `/application` or Greenhouse job board). Re-resolve if the page says the job is closed. |
| `company` + `title` | Must still match the live page. Sibling jobs are a skip. |
| `pursuit_lane` | Honor `core` / `broad` / `practice` mix already in the repo. |
| Fall 2026 intern | Skip (same hard skip as discovery). Together 2026-08-22 was closed anyway. |

Do not open a Jobright “Sign up to apply” wall. Do not create accounts.

Source of URLs: confirmed keeps / apply-queue rows the user already marked
for autofill — not every discovery keep. Until Junyi names that queue, the
Automation idles with “no rows.”

---

## Per-tab loop

1. Open `apply_url` in Chrome.
2. Confirm company + title vs the row. Mismatch → skip, log `wrong_requisition`.
3. Trigger Copilot once (“Start Application” / “Autofill This Page”).
4. Never click employer Submit / Apply (final). Never click MyGreenhouse.
5. Apply `knowledge/form_strategy.yaml` (prior employer, relocate, H-1B-named,
   intern-in-general vs at-this-company, grad year 2027, on-site, start date,
   how-heard). Click required privacy / I-agree squares.
6. Written responses: Cursor writes from `knowledge/evidence_bank.yaml`.
   **Never** click Simplify “Generate with AI.” Do not invent metrics.
   Preference / interest questions go to the leftover pile.
   Never type salary / expected pay / compensation. Leave those for Junyi.
7. Never change EEO answers. If Copilot filled EEO, mark `eeo_touched=true`.
8. Screenshot identity, work-auth, EEO, consent boxes, and the unclicked Submit control.
9. Write one review row (below). Next URL.

---

## Stop-the-line (do not Submit even if a human is watching)

From the 2026-08-22 10-tab review
(`docs/experiments/2026-08-22_ten_tab_copilot_review.md`):

| Signal | Action |
|---|---|
| Copilot filled EEO (gender/race/veteran/disability) | `eeo_touched=true`. **Block Submit.** |
| Work auth is US citizen / green card and profile is F-1 | `work_auth_mismatch=true`. **Block Submit.** |
| Broad “now or in the future require sponsorship?” answered No | `sponsorship_needs_review=true`. **Block Submit.** Fact is still Yes. |
| Other non-H-1B sponsorship wording answered No (e.g. Gemini “Visa sponsorship”) | `sponsorship_needs_review=true`. **Block Submit.** Fact is still Yes. |
| “H-1B sponsorship?” named and answered No | Intended as of 2026-08-23. Do not block on that alone. See `knowledge/work_authorization.yaml` `form_strategy`. |
| Education widgets look like a dumped blob | `education_misfill=true`. Review, do not Submit. |
| Copilot “need review” matches empty form fields | Expected. Log the empty field names into `knowledge/autofill_obstacles.yaml` if they are new gaps. |
| Job closed / 404 / “no longer open” | **Close the tab.** Write `decision=closed` in `data/job_decisions.csv` and `posting_closed` in `data/activity_log.csv`. Do not pick a sibling from Current openings. Next URL. |
| Checker `ready: false` | Stop the run. |

Default remaining policy: **every tab is blocked from Submit** until Junyi
explicitly changes this file to allow it for a named row. The first shipped
Automation only produces review artifacts.

---

## Artifacts to write

Per run, under `generated/apply_review/YYYY-MM-DD/`:

- `review.csv` — one row per URL: company, title, apply_url, requisition_match,
  identity_ok, resume_filename, eeo_touched, work_auth_value,
  sponsorship_value, need_review_count, submit_clicked (must be false),
  blocker, screenshot paths.
- Screenshots copied into that folder (no cookies, no passwords).
- `leftovers.md` — preference / missing-evidence questions for Junyi.
- End-of-day digest draft (counts fluent vs leftover + this agent URL).
  **Do not send email** until Junyi confirms send.
- Append `data/activity_log.csv` only for “autofill reviewed, not submitted”
  when a material review happened. Do not write `status=applied`.

Do not commit Chrome profiles or `simplify_storage.json`.

---

## What this Automation is not

- Not unattended Submit. That needs a later, explicit user sentence.
- Not Simplify “Generate with AI.” Essays are written from the evidence bank
  or left for Junyi. Still not unattended Submit until he says so.
- Not daily discovery. Discovery stays `docs/automation/DAILY_JOB_DISCOVERY.md`.
- Not a shared/friends environment. The snapshot is a live Simplify login.

---

## How to turn it on (Junyi)

1. Confirm the personal environment still default-boots `ready: true`.
2. Name the input queue (which CSV / which `next_action=autofill_review`).
3. Create a Cursor Automation whose instructions are only the pointer in
   `docs/automation/UI_POINTER.md` (apply block).
4. Keep the schedule weekday-only if you want. Discovery can stay daily.
5. After each run, you Submit (or skip) in Take Control or on your laptop.

Until step 3 exists in the Cursor UI, this design is repo-only.
