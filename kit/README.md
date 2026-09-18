# Agentic Auto-Apply Kit

A fork-and-run setup for having an AI browser agent apply to software / data / ML jobs on
your behalf, all day, unsupervised — and keep an auditable log of every attempt.

This is not a script. There is nothing to `npm install`. It is a set of **instructions an
agent reads and executes in a real browser**, plus the config you fill in with your own
details. You fork this, spend about 45 minutes on setup, and then it runs on a schedule.

Built and tested by someone applying to 2027 new-grad and internship roles. The numbers in
[COSTS.md](COSTS.md) and the defect list in
[workflows/auto-apply-50.md](workflows/auto-apply-50.md) come from real runs, not estimates.

---

## What it actually does

```
Jobright AI Agent queue  ──►  employer's ATS (Workday / Greenhouse / Ashby / iCIMS / ADP …)
        │                              │
        │                              ├─ agent fills the form
        │                              ├─ agent runs a correction checklist against your real facts
        │                              └─ agent submits, captures the confirmation text
        │                              │
        └──◄── "I've Applied" ─────────┘
                    │
                    └──►  one row appended to your Google Sheet ledger
```

Three workflows, running on three different clocks:

| Workflow | Cadence | Job |
|---|---|---|
| `auto-apply-50` | 2×/day | Works the job queue and submits applications |
| `production-learning-daily` | 1×/day | Reads yesterday's log, folds new defects back into the instructions |
| `cursor-production-maintenance` | 1×/week | Preflights every dependency, writes a reflection entry to GitHub |

The second and third exist because **the first one degrades**. Job sites redesign their UI,
autofill invents new lies, an ATS adds a required field. The audit loops are what keep the
apply loop honest without you babysitting it.

## The honest pitch, and the honest warning

**What works:** you stop spending evenings on application forms. A run submits real
applications to real ATS platforms with your correct visa status, graduation timing, and
salary expectation — the fields that job-board autofill reliably gets wrong.

**What you're accepting:** this submits legally-attested forms in your name without asking
first. Read [The consent boundary](#the-consent-boundary) before you turn on a schedule.
The single most important thing in this kit is the **pre-submit correction checklist**,
because the underlying tools *will* put false claims on your application if nothing checks
them. During the trial run, autofill:

- wrote *"I am a Computer Science student"* into a free-text answer (wrong degree entirely)
- added **Go** to a technical-skills line for someone who has never written Go
- produced a GPA of `4.000000000000001`
- answered a visa-sponsorship question backwards
- left a required "Company" field blank and a required name-pronunciation field untouched

None of that is hypothetical. All five happened in eleven applications. The checklist
exists because of them.

## Results from the reference run

Eleven jobs processed in one supervised session:

| Outcome | Count |
|---|---|
| Submitted (confirmation captured) | 8 |
| Blocked (missing document, broken form) | 3 |

Roughly **2.5 minutes** for a simple single-page form, up to **15 minutes** for a Workday or
SuccessFactors application needing account creation and a CAPTCHA. Call it ~7 minutes
average. That means a 50-application target is a ~6-hour run, not a 20-minute one — plan the
schedule accordingly.

## Prerequisites at a glance

| | What | Cost |
|---|---|---|
| **Required** | An agentic browser (Polar) | $0–20/mo |
| **Required** | A job source with an apply queue (Jobright) | $0–40/mo |
| **Required** | A Google account (Sheets ledger) | $0 |
| **Required** | A dedicated application email address | $0 |
| **Required** | Your resume as a PDF, 1 page | $0 |
| Strongly recommended | Your transcript as a PDF | $0 |
| Optional | A GitHub account (reflection log) | $0 |

Full detail, versions, and what breaks without each: **[DEPENDENCIES.md](DEPENDENCIES.md)**
Full pricing with sources: **[COSTS.md](COSTS.md)** — realistic all-in is **$20–60/month**,
and there is a genuinely usable **$0 path**.

## Setup

Follow **[SETUP.md](SETUP.md)**. The short version:

1. Sign up for the two services, install the browser + the autofill extension
2. Create the Google Sheet ledger from the schema in [SETUP.md](SETUP.md)
3. Fill in `profile.example.md` with your real details → save as `profile.md`
4. Paste the handoff prompt from [SETUP.md](SETUP.md) into your agent
5. Run **one supervised session of at least 10 jobs** before you ever turn on a schedule

Step 5 is not optional padding. Ten is the minimum that surfaces the per-ATS quirks; three
tells you nothing. The reference run found four distinct new defects in eleven jobs.

## The consent boundary

Decide these three before you start, and write your answers into `profile.md`:

1. **Does it submit, or only prepare?** This kit's default is *submit automatically*. The
   safer setting is prepare-and-stop, and it costs you the unsupervised-overnight benefit.
2. **What may it never fill in?** Anything you cannot verify. Date of birth, a GPA you don't
   remember, a claimed referral, a degree you don't hold, a skill you don't have. The
   workflow's rule is: a required field you cannot answer truthfully is a **hard stop** that
   gets logged as `BLOCKED` — never a guess.
3. **Which answers are yours alone to give?** Work authorization and visa sponsorship are
   legal attestations on a federal-facing form. The agent should read your stated answer
   from config and never infer one. If your status changes, you update config — not the
   agent.

An agent submitting a form in your name is you submitting it. Fabrications become *your*
misrepresentation on an employment application, which is a real consequence and not a bug
report. Treat the checklist as the product.

## Repo layout

```
README.md                 you are here
SETUP.md                  step-by-step + the prompt to paste into your agent
DEPENDENCIES.md           every dependency, why, and what breaks without it
COSTS.md                  pricing, sources, and the $0 path
profile.example.md        your facts — copy to profile.md and fill in
workflows/
  auto-apply-50.md                   the apply loop (the substantial one)
  production-learning-daily.md       the daily audit loop
  cursor-production-maintenance.md   the weekly system check
```

The three files in `workflows/` are written to be handed to an agent verbatim. They are
generic — every personal detail lives in `profile.md`, which is gitignored so a fork never
leaks the author's information or yours.

## License and expectations

Take it, change it, don't credit anyone. No warranty of any kind: the services it drives are
third-party products that change without notice, and an application submitted wrongly is
your problem, not the kit's. Re-read [The consent boundary](#the-consent-boundary) if that
sentence made you uncomfortable — that discomfort is the correct response to automating
legal attestations, and the checklist is how you manage it.
