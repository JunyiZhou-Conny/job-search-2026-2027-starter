# production-learning-daily

A short daily audit of the application system. Read yesterday's attempts, find anything new
that went wrong, and fold the durable lessons back into the files that actually drive
behavior. Nothing else.

This is what keeps the apply loop from decaying silently. Job sites redesign forms, autofill
invents new failure modes, an ATS adds a required field. Without this loop, quality degrades
and you don't find out until an employer does.

**Design constraint: stay small.** A handful of tool calls, a few minutes, and most days the
answer is "nothing new." Resist turning it into a reporting exercise — if there's no new
lesson, say so in one line and stop.

## What it operates on

- **The ledger:** the sheet URL in `profile.md`, tab `Sheet1`
- **The files that encode behavior:**
  - `workflows/auto-apply-50.md` — how applications get made
  - `profile.md` — the personal facts every form field comes from
- **Its own memory:** `workflows/seen.md` — defect patterns already folded in, so the same
  lesson isn't re-litigated every day. Create it on the first run if absent.

## Steps

1. **Read the ledger.** Pull the full sheet and take rows whose `timestamp_et` falls in the
   last 24 hours. If none, widen to the most recent `run_id`. If the sheet is unreachable,
   report that and stop — don't guess.

2. **Count the day.** Tally `SUBMITTED` / `SUBMISSION_UNKNOWN` / `BLOCKED` / `SKIPPED`, and
   note the highest `cumulative_applied` reached. That's the run's real throughput.

3. **Read `seen.md`** so you know what's already known.

4. **Extract candidate lessons** from every `blocker_or_note` and `evidence` cell:
   - A **blocker that repeated** across two or more rows, or has now appeared on a second
     different employer or ATS. One-off oddities are not lessons.
   - An **autofill defect** that put a wrong or invented value on a form — a bad date, a
     garbled number, a fabricated skill or claim, a blank required field.
   - An **ATS mechanic** that cost real time and would be cheap to write down — a fragile
     widget, a CAPTCHA style, an account-creation quirk.
   - A **data gap only the owner can close** — a document that doesn't exist, a fact not in
     `profile.md`. These aren't fixable by editing files; they go in the report as a direct
     ask.

   Drop anything already in `seen.md` or already written into the apply workflow or
   `profile.md`.

5. **Sanity-check the ledger while you're in there.** Flag, and fix if unambiguous:
   - a `SUBMITTED` row with an empty `evidence` cell — submissions require evidence
   - duplicate `job_url` values marked `SUBMITTED` more than once (a double application)
   - `cumulative_applied` not increasing by exactly one per `SUBMITTED` row in timestamp order

   Write with explicit range updates, never the Sheets *append* operation — append places rows
   by table auto-detection and can overwrite an existing row mid-table. Re-read to confirm.

6. **Fold the real lessons in — at most two or three per day.**
   - A *procedural* lesson (how to work a form, what to check before submitting) → edit the
     pre-submit checklist table or the relevant ATS section in `workflows/auto-apply-50.md`.
   - A *fact* about the owner or their documents → edit `profile.md`. Read it first; it may
     have changed elsewhere.
   - Append every lesson you folded in to `seen.md` with the date and a one-line summary.

   Edit in place, keep it tight, don't restructure. **Don't add a lesson you're not confident
   about** — a wrong entry in the checklist is worse than a missing one.

7. **Report in chat, briefly.** Three parts, no preamble:
   - yesterday's counts
   - what you changed, file by file (or "no new lessons — nothing changed")
   - anything only the owner can resolve, as a direct ask

## Out of scope

Don't apply to jobs. Don't restructure the workflow files. If the system needs a change
bigger than an edit to the checklist or `profile.md`, describe it in the report and let the
owner decide.
