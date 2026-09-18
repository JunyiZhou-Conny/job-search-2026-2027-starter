# auto-apply-50

Work the job board's application queue until **the run's target number of submissions has
been reached**, and record every attempt in the ledger sheet.

Read `profile.md` first. Every personal fact on every form comes from there — this file
contains the *procedure*, never the data.

## Run parameters

- **Target:** the `applications target per run` from `profile.md`, counted **per run**. Each
  run starts its own count at zero.
- **Submission mode:** whatever `profile.md` says. If it says prepare-and-stop, fill
  everything and stop before the final submit; do not submit.
- **Ledger:** the sheet URL in `profile.md`, tab `Sheet1`, columns
  `run_id | timestamp_et | company | role | job_url | ats | outcome | cumulative_applied | blocker_or_note | evidence`
- `outcome` ∈ `SUBMITTED` · `SUBMISSION_UNKNOWN` · `BLOCKED` · `SKIPPED`. Only `SUBMITTED`
  counts. **Never write `SUBMITTED` without the literal confirmation text or URL in
  `evidence`.**

## STEP 0 — Precondition: the application mailbox must be signed in

**Before touching a single job**, open the application email inbox from `profile.md` and
confirm it loads signed in.

This is not bookkeeping. ATS platforms email one-time verification codes mid-application.
Without a live session, the application dead-ends *after* an employer account has been
created — the worst failure state, because a clean retry is no longer possible.

If it does not load — especially if it redirects into a passkey prompt, which waits on an OS
security dialog that cannot be answered from here — **stop and ask the owner to sign in.**
Do not start applying. Leave the tab open for the whole run; codes get read from it.

## STEP 1 — Set up the run

1. Mint a `run_id`, e.g. `R-YYYYMMDD-HHMM`.
2. Read the **entire** ledger tab and collect every `job_url` already marked `SUBMITTED`.
   Scan all rows — they are not reliably in chronological order. That set is the
   do-not-reapply list.

### Stop conditions

Stop at the first of these and report:

- The run's target number of `SUBMITTED` rows is reached.
- The queue is empty **and** a request for more matches returns nothing new. The queue
  emptying around 40 jobs is normal and is *not* a stop condition — refill per STEP 3.
- **Eight consecutive jobs end `BLOCKED` or `SKIPPED` with no submission.** Something
  systemic is wrong — a changed UI, a dead login, bad profile state. Stop and report rather
  than grinding through the queue.
- Nine hours elapsed. Stop, report, leave the queue mid-flight for the next run.

Budget ~2.5 min for a simple one-page form and up to ~15 min for Workday or SuccessFactors
with account creation. **~7 min average**, so a 50-application target is roughly a six-hour
run. Report the real number achieved. Never inflate the count, and never mark an unconfirmed
application `SUBMITTED` to hit a number.

## STEP 2 — Read the queue's state

The top status bar is the control surface:

- `● Standby — "N Jobs Added. Awaiting Application Start."` with a **Start** button
- `● Executing — "N Jobs Remaining."` with a **Pause** button

The list icon opens the queue panel with **Active(n)** / **Completed(n)** tabs. Treat
`Completed` as a cross-check only — **the ledger sheet is the source of truth**, and the two
will disagree.

## STEP 3 — Fill the queue, and expect to refill it

**The queue caps at 40 jobs at a time.** (The in-app assistant may claim 50; it's wrong.)
Any target above 40 needs a mid-run refill.

Add jobs via the composer or a "show me more matches" control, then click **Add** on the
cards that appear. Fill to 40, press **Start**.

When Active empties, you are not done — request more matches, add at least
`target - submitted_so_far` more (allow slack for jobs that won't submit cleanly), press
**Start** again.

## Autonomous execution mode

After **Start**, the board's own agent may drive an entire job by itself — generate resume →
confirm → fill form → submit — **without opening a visible browser tab**, then post a
"submitted" line in its chat feed and mark the job Applied in its own tracker.

Decide which posture you want and write it in `profile.md`:

- **Accept it** (the reference setup's choice): let it finish, don't pause it, and log the row
  `SUBMITTED` with the agent's submission line plus its tracker entry as `evidence`. The
  tradeoff is real — there is no employer-side confirmation to capture, and no opportunity to
  run the correction checklist on that application.
- **Require supervision:** don't press Start. Work every job through the manual route in
  STEP 4, where you see each form before it submits.

Either way, whenever the board **hands control back** — `Action Required`,
`Confirm Resume To Proceed`, `Apply Now ↗` — STEP 4 and the correction checklist apply in
full.

## STEP 4 — The per-job loop

Each job card walks fixed stages: generate resume → confirm resume → fill out application
form (**Action Required**) → submit application.

**Per job:**

1. **Default is apply. Do not judge fit.** The board's matching model picked these. Never
   skip over match %, seniority, domain, or location, and don't read the full job description
   hunting for reasons to opt out. Deliberation is the cost this system exists to remove.
2. **Only two reasons to skip:**
   - The `job_url` is already `SUBMITTED` in the ledger. Never apply twice.
   - The posting states a hard bar that voids the application regardless of how it's filled —
     citizenship or active clearance required, or enrollment at one named school. Log
     `SKIPPED` with the reason; move on immediately.
3. **Confirm the generated resume before it goes anywhere.** It is the single most common
   source of false claims. Check specifically:
   - Every **number** traces to real evidence in `profile.md`
   - The **skills line** contains nothing you didn't list — a generated resume has been caught
     silently adding a programming language the candidate had never used
   - Any **cover letter** is skipped when optional. Generated ones invent metrics freely.
4. Click **Apply Now ↗** (or, manual route: queue panel → a "Not Started" job → **Original
   Job Post** in the detail pane). The employer ATS opens in a new tab with the autofill
   sidebar injected. **The board sometimes opens 2–3 duplicate tabs** — close the extras.
5. Work the form. The sidebar mirrors the page's own advance button and shows an
   `x/y required fields filled` meter. **Don't trust its green checkmarks** — read the actual
   page. Per-ATS notes are in `DEPENDENCIES.md`.
6. **Run the pre-submit correction checklist below. Do not skip it.**
7. Submit. Capture the literal confirmation text or URL as `evidence`. Anything ambiguous —
   a duplicate-profile screen, "we already have your profile" — is `SUBMISSION_UNKNOWN`, not
   `SUBMITTED`.
8. **Return to the queue tab and click `I've Applied.`** The queue does not advance on its
   own; skipping this stalls the whole run. For a blocked job, click **Skip** instead.
9. **Append the ledger row immediately**, before starting the next job. Write with an explicit
   range update to the next empty row — the Sheets *append* operation auto-detects where your
   table ends and can overwrite an existing row mid-table. Re-read after writing to confirm.
10. If a "some jobs have expired" banner appears, click **Remove & Continue**.

## Pre-submit correction checklist

**This table is the heart of the system.** Autofill is fast and wrong in specific, repeating
ways. Verify each line against the actual rendered form before every submit. Every entry
below is here because it really happened.

| Field | Correct value / action |
|---|---|
| Email | The application mailbox from `profile.md` — never a personal address |
| Legal name | Exactly as written in `profile.md`. Autofill has submitted **"Mr. `<Name>` Sr."** — strip invented titles and suffixes. |
| Phone / address / LinkedIn | From `profile.md` |
| **Resume attached** | Confirm the **filename on the employer's own form.** Upload widgets that offer no file picker will grab whatever the profile's default is, which may be an unapproved multi-page master. |
| Currently authorized to work | The stated answer in `profile.md`. **Never infer this.** |
| Future sponsorship required | The stated answer in `profile.md`. A **separate** question from the one above, and autofill gets both wrong in both directions. |
| Graduation / program timing | From `profile.md`. Graduation-term pickers default to the wrong term — one defaulted to "Summer 2027" for a December 2026 completion. |
| GPA | The single correct value. Autofill has **concatenated two schools' GPAs into one field**, and produced the floating-point artifact `4.000000000000001`. |
| Salary expectation | From `profile.md` unless the posting implies otherwise |
| "How did you hear about us?" | **Never claim a referral that doesn't exist.** Default `LinkedIn`; if the list is populated but has no neutral option, pick any option rather than stalling. (A genuinely *empty* required dropdown is a hard block — see below.) |
| Required transcript upload | Upload the transcript from `profile.md`. Common on campus and quant-finance postings. |
| Work-experience `Company` fields | **Never blank** — Workday rejects it outright. Solo/personal work is `Self-Employed`. |
| Skill tags the ATS auto-suggests | **Delete wrong ones.** Workday's taxonomy expands short names into unrelated products — "R" became "SAP R", "MCP" became "Unisys MCP". |
| Language proficiency | Workday wants an explicit overall level; autofill leaves it blank and validation fails. |
| **Every autofilled free-text answer** | **Read all of it. Autofill invents biography.** One wrote *"I am a Computer Science student"* for a candidate in a different field entirely — a false degree claim on a legal form. Rewrite in the owner's real terms from `profile.md`. |
| Voluntary EEO / veteran / disability | From `profile.md` |
| Fields autofill skipped entirely | Scan for required-but-empty before submitting. Ashby's "name pronunciation" is silently skipped and fails validation on submit. |

### Hard stops — log `BLOCKED`, never fabricate

- **Any field whose answer isn't in `profile.md`** and can't be derived truthfully from it.
  Date of birth is the usual one.
- **A required dropdown whose option list is genuinely empty.** Some tenants ship a required
  field containing only a placeholder, so the form can never validate. Clicking, keyboard
  navigation, and a reload all fail — don't burn attempts on it.
- **An employer account whose verification code never arrives.**
- **A required document that doesn't exist** in `profile.md`.

If the owner's stated work-authorization answer ever conflicts with direct evidence of their
actual status, **do not override their instruction** — note it in `blocker_or_note` and raise
it in the run summary. It's a legal attestation and it's theirs to make.

## STEP 5 — Report

A short chat summary: submissions this run against target, blockers grouped by type, real
average minutes per application, and a link to the ledger.

**Also report every correction you made.** That list is what feeds the daily audit workflow,
and it's how this checklist grows.
