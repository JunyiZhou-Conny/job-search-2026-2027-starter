# Setup

About 45 minutes of your time, plus a ~2-hour supervised trial run you should not skip.

Do the steps in order. Step 6 is the one people want to skip and the one that saves them.

---

## 1. Accounts and installs — 15 min

1. **Create a dedicated application email.** Outlook or Gmail, something like
   `yourname_application@outlook.com`. Use a normal password — **do not add a passkey**, since
   a passkey prompt waits on an OS dialog an agent cannot answer, and a stale session then
   becomes unrecoverable mid-application.
2. **Install the agentic browser** ([Polar](https://polarbrowser.com), or your alternative —
   see [DEPENDENCIES.md](DEPENDENCIES.md#1-agentic-browser--required) for the four
   capabilities it must have).
3. **Sign up for the job source** ([Jobright](https://jobright.ai)) using the application
   email. Start on the free tier; don't pay until step 6 proves the loop works.
4. **Install its autofill browser extension in the same browser profile the agent drives.**
   Then open any job application page and confirm the sidebar appears **without you clicking
   the extension's toolbar icon.** If it only appears after a manual click, the agent will
   never be able to summon it, and you need a different extension.
5. **Sign into the application email in that browser and leave it signed in.**

## 2. Build the ledger — 5 min

New Google Sheet, name it something findable like `Auto-Apply Log`. Leave the tab as
`Sheet1`. Paste this as row 1:

```
run_id	timestamp_et	company	role	job_url	ats	outcome	cumulative_applied	blocker_or_note	evidence
```

| Column | Holds |
|---|---|
| `run_id` | One id per run, e.g. `R-20260918-0900`. Lets you measure a single run's throughput. |
| `timestamp_et` | When the attempt finished |
| `company`, `role` | As shown on the posting |
| `job_url` | **The dedupe key.** Must be filled — this is what stops you reapplying. |
| `ats` | Workday / Greenhouse / Ashby / iCIMS / ADP / SuccessFactors / … |
| `outcome` | `SUBMITTED` · `SUBMISSION_UNKNOWN` · `PREPARED` · `BLOCKED` · `SKIPPED` |
| `cumulative_applied` | Running count of this run's target outcomes (`SUBMITTED` or `PREPARED`). Resets to zero each run. |
| `blocker_or_note` | What went wrong, or what you had to correct. **This column is what the daily audit reads** — write real detail here, not "ok". |
| `evidence` | The literal confirmation text or URL. **No evidence, no `SUBMITTED`.** |

Keep the sheet's URL handy; you'll paste it into `profile.md` next.

## 3. Fill in your profile — 15 min

Copy `profile.example.md` to `profile.md` and fill in every field. This is the only file with
your personal information in it, and it's gitignored so forks never leak it.

Take the "answers only you can give" section seriously — visa status, graduation timing, and
salary expectation are the fields generic autofill gets wrong most often, and two of them are
legal attestations.

## 4. Load the workflows — 5 min

Give your agent the three files in `workflows/`, each as a scheduled workflow:

| File | Suggested schedule |
|---|---|
| `auto-apply-50.md` | 9:00 AM and 5:00 PM local |
| `production-learning-daily.md` | 10:00 PM local |
| `cursor-production-maintenance.md` | Mondays 8:00 AM local |

**Leave all three schedules off for now.** You turn them on after step 6.

In Polar this is: paste the file contents into chat, say *"save this as a scheduled workflow
called auto-apply-50, running at 9am and 5pm, but leave the schedule off for now."* Other
agents will have their own mechanism.

The scheduled copy is what the apply loop executes. The daily audit edits
`workflows/auto-apply-50.md` and then **must replace that scheduled workflow** with the
updated file. If you skip the refresh, checklist lessons never reach the next apply run.

Each workflow file references `profile.md` for personal facts, so put `profile.md` where the
agent can read it and tell the agent that path.

## 5. The handoff prompt

Paste this into your agent once everything above is done. It does the whole setup check and
the first supervised run.

```text
I'm setting up an automated job-application system from a kit I forked. The files are at
<PATH TO YOUR FORK>. Read these first, in this order:

  1. README.md            — what this system does and its consent boundaries
  2. DEPENDENCIES.md      — the preflight checklist is at the bottom
  3. profile.md           — my personal facts, the source of truth for every form field
  4. workflows/auto-apply-50.md  — the apply loop you'll be executing

Then do these three things:

STEP A — Preflight. Run every item in the DEPENDENCIES.md preflight checklist and report
pass/fail per line. Do not start applying if any line fails; tell me what's broken instead.

STEP B — One supervised run of exactly 10 jobs. Follow workflows/auto-apply-50.md exactly,
including the pre-submit correction checklist before every single submit. Two rules while
we're in trial:
  - Before you click submit on the FIRST TWO applications, stop and show me every field
    you're about to send so I can check your reading of my profile. After those two, proceed
    on your own.
  - Log every attempt to my ledger sheet as you go, one row each, never batched at the end.

STEP C — Report back with: how many submitted vs blocked, the real average minutes per
application, and every instance where autofill got something wrong and you corrected it.
That last list is the important one — it tells us what to add to the checklist before this
runs unsupervised.

Rules for the trial:
- Never fabricate. A required field you can't answer truthfully from profile.md is a hard
  stop: log it BLOCKED and move on. Do not guess a date of birth, a GPA, or a referral.
- Never mark something SUBMITTED without capturing the literal confirmation text or URL.
- Read every autofilled free-text answer before submitting. It invents biography.
```

## 6. The supervised trial run — ~2 hours, do not skip

Run at least **10 jobs** with you watching. Not 3 — three tells you nothing, because each ATS
platform fails differently and you need to see several.

What to watch for, all of which happened in the reference run:

- A **false claim** in a free-text answer (wrong degree, invented skill, fabricated metric)
- **Visa / work-authorization answers** flipped from what your profile says
- The **wrong resume file** attached — check the filename on the employer's own form
- A **garbled number** in a GPA or date field
- A **required field autofill skipped entirely**, failing validation on submit

When you find one, add it to the pre-submit checklist table in
`workflows/auto-apply-50.md` immediately. That table is the kit's actual value, and it should
grow as you learn your own stack's failure modes.

## 7. Go live

Once the trial run comes back clean:

1. Turn on `auto-apply-50`'s schedule.
2. Turn on the two audit workflows. They're what keeps the apply loop honest as sites change
   underneath it — without them, quality decays silently.
3. Upgrade to the paid tiers now that you know the loop works
   (see [COSTS.md](COSTS.md); take the job board's **quarterly** plan, never weekly).
4. Read the daily audit output for the first week. After that, weekly is enough.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Autofill sidebar never appears | Extension needs a human toolbar click (`activeTab` model) | Different extension, or fill manually |
| Agent stalls mid-application waiting for a code | Application email session died | Re-sign-in; remove any passkey from the account |
| Applications not deduping | `job_url` column blank on earlier rows | Backfill it; it's the dedupe key |
| A logged row vanished from the sheet | Sheets API append overwrote it mid-table | Write with explicit range updates, not append; re-read after each write |
| Clicks land on the wrong element | Sidebar opened/closed and shifted the viewport | Re-screenshot after any sidebar state change; don't reuse coordinates |
| Queue stops around 40 jobs | The job board's queue caps at 40 | Normal — refill and restart, per the workflow |
| Same job offered repeatedly | Board tracker and your ledger disagree | Your ledger wins. Dedupe on `job_url`, not the board's status. |
| Checklist grew but apply still makes the same mistake | Scheduled apply is a frozen paste | Daily audit must refresh the scheduled `auto-apply-50` workflow from the file |
