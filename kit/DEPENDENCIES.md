# Dependencies

Everything this kit needs, why it needs it, and what actually breaks if you skip it.

There are no code dependencies — no runtime, no package manager, no API keys to rotate. The
dependencies are **accounts, a browser extension, and three files**. That is the whole
surface area, and it is deliberately small: the previous version of this system ran on a
Python repo with a config runtime, scheduled scripts, and a state file, and it was replaced
because the agent-plus-instructions version does the same job with roughly a tenth of the
moving parts.

---

## 1. Agentic browser — **required**

| | |
|---|---|
| Reference implementation | [Polar](https://polarbrowser.com) (macOS + web app) |
| Role | Reads the workflow files and drives every click, form fill, and submit |
| Needs | Persistent logged-in browser sessions, file storage, a scheduler, Google Sheets access |
| Without it | Nothing runs. This is the execution engine. |

Non-negotiable capabilities, because the workflows assume all four:

1. **Persistent sessions.** It must stay logged into the job board, the employer ATS accounts
   it creates, and your email across runs. An agent that starts from a cold browser cannot
   retrieve a verification code.
2. **A scheduler.** Unsupervised runs at fixed times are the entire point. Without this you
   have a chatbot you have to babysit, which is strictly worse than applying by hand.
3. **Durable file storage the agent can read and write.** The workflow instructions, your
   `profile.md`, and your transcript PDF have to survive between runs.
4. **Google Sheets read/write**, natively or via a connector, for the ledger.

Other agentic browsers (Comet, OpenAI's Operator-style agents, Browser Use) may work — the
workflow files are plain English, not Polar-specific API calls. But the four capabilities
above are the filter, and scheduling plus durable storage is where most alternatives fall
short. Verify before committing.

## 2. Job source with an apply queue — **required**

| | |
|---|---|
| Reference implementation | [Jobright](https://jobright.ai) — the `/agent` product specifically |
| Role | Supplies matched jobs, generates a per-role tailored resume, injects an autofill sidebar on the employer's own ATS page |
| Without it | The agent has no job pipeline and no autofill assist, and you are hand-writing search queries into it |

What you're actually buying: a **queue with a per-job state machine** (generate resume →
confirm → fill form → mark applied), plus a browser extension that pre-fills employer forms.
The matching quality matters less than you'd think — the workflow's stated policy is to trust
the recommendations and not second-guess fit, because deliberating over match percentages is
where a human burns the time this is supposed to save.

Known constraints you should plan around, from real use:

- The queue **caps at 40 jobs at a time.** Any target above 40 requires a mid-run refill.
  The in-app assistant claims 50; it's wrong.
- There is **no public pricing page** — you only see prices after signing up.
- The "autonomous" mode can complete a whole application without opening a visible tab. Decide
  up front whether you accept that (no employer-side confirmation to capture) or require the
  manual per-job route where you watch every submit.
- Its generated resumes **invent details.** See the defect list in the apply workflow.

Substitutable with Simplify, LazyApply, JobCopilot, or similar, but you will have to rewrite
the UI-mechanics sections of `workflows/auto-apply-50.md`, which is most of that file.

## 3. Autofill browser extension — **required, and easy to miss**

The job source's extension must be **installed and enabled in the same browser profile the
agent drives.** It injects the sidebar that fills employer forms.

Two failure modes worth knowing before you hit them:

- Extensions using the `activeTab` permission model only inject their UI after a *human*
  clicks the toolbar icon. An agent cannot perform that click. Confirm your extension
  auto-injects on page load, or you will get a silent no-op on every application.
- When the sidebar opens or closes, **the page viewport width changes** and every element
  shifts. Re-locate elements after any sidebar state change rather than reusing coordinates.

## 4. Google account + Sheets — **required**

| | |
|---|---|
| Role | The ledger. One row per application attempt. |
| Cost | $0 |
| Without it | No dedupe (you reapply to jobs), no audit trail, no throughput data, and the daily audit loop has nothing to read |

The ledger is the **source of truth**, not the job board's own tracker. It's what prevents
double applications and what the audit workflow reads to spot repeating defects. Schema is in
[SETUP.md](SETUP.md).

One operational gotcha: the Sheets API's *append* operation places rows by auto-detecting
where your table ends, and it can land a new row mid-table and **overwrite an existing one.**
This happened twice during the reference run and silently destroyed a logged row both times.
Write with an explicit range update to the next empty row, then re-read to confirm.

## 5. A dedicated application email address — **required**

| | |
|---|---|
| Role | Every ATS account, every verification code, every recruiter reply |
| Cost | $0 (Outlook, Gmail, anything) |
| Without it | Your personal inbox becomes unusable within a week |

Two hard requirements:

- **It must be signed in, in the agent's browser, before every run.** ATS platforms email
  one-time codes mid-application. A dead session strands the application *after* an account
  has been created — the worst possible failure state, because now you can't cleanly retry.
  The apply workflow has this as a blocking precondition for exactly this reason.
- **Do not put a passkey on this account.** A passkey prompt waits on an OS-level security
  dialog that an agent cannot answer, so a stale session becomes permanently unrecoverable
  mid-run. Use a password the agent's password manager can fill.

## 6. Your documents

| File | Required? | Notes |
|---|---|---|
| Resume PDF | **Yes** | **One page.** Keep exactly one approved file. A two-page master sitting in the same folder will get grabbed by an upload widget that offers no file picker — verify the attached filename on the employer's own form, every time. |
| Transcript PDF | Strongly recommended | Campus and quant-finance postings require it outright. Without it, those applications are hard-blocked. Three of eleven jobs in the reference run blocked on this before the file existed. |
| Cover letter | No | Skip when optional. Generated cover letters are the single worst offender for invented metrics. |

## 7. GitHub — **optional**

Only used by the weekly maintenance workflow, to commit a reflection entry and open a PR so
there's a change history outside the agent's own files. Drop it and keep the journal locally;
nothing else depends on it.

---

## Per-ATS notes

You don't configure these — the agent hits them. Listed so the field notes in
`workflows/auto-apply-50.md` make sense, and so you know what "it's taking 15 minutes" means.

| ATS | Domain pattern | What to expect |
|---|---|---|
| Workday | `*.myworkdayjobs.com` | Longest flow. Account creation, 7-step stepper. Its skill taxonomy invents wrong entries from short skill names — "R" became "SAP R", "MCP" became "Unisys MCP". |
| Greenhouse | `job-boards.greenhouse.io` | Simple, but campus roles require the transcript. |
| Ashby | `jobs.ashbyhq.com` | Clean. Long-answer textareas silently discard newlines. Required fields autofill skips entirely (e.g. name pronunciation), so the first submit attempt fails validation. |
| iCIMS | `*.icims.com` | Form lives in an iframe autofill **cannot reach** — every question is manual. Accounts are per-tenant despite a shared login domain. |
| ADP WorkforceNow | `workforcenow.adp.com` | Email OTP required mid-flow. Final step needs a typed full name as an e-signature. |
| SAP SuccessFactors | `*.successfactors.com` | Image-grid CAPTCHA at sign-in. Fragile dropdowns that silently revert to unset when adjacent fields change — set them last, then re-verify. |
| Paylocity | `recruiting.paylocity.com` | Multi-step, straightforward. |
| Oracle Cloud | `*.oraclecloud.com` | Clicking Submit can re-trigger the extension mid-submit. Never cancel that — let it finish, re-verify every field, resubmit. |

## Preflight checklist

Run this before any scheduled run. It's step 1 of the weekly maintenance workflow.

- [ ] Application email inbox loads, signed in, no passkey prompt
- [ ] Job board loads and shows a queue status bar
- [ ] Autofill extension enabled in the agent's browser profile
- [ ] Ledger sheet reachable, header row intact
- [ ] Resume PDF present — and it's the one-page approved file
- [ ] Transcript PDF present, non-zero size
- [ ] `profile.md` reflects your *current* visa status and graduation timing
- [ ] The apply workflow's schedule is on
