# Automation experiment — find the bottlenecks (safely)

## Goal

Learn what can actually be automated end-to-end **without** putting passwords in Cursor chat or git.

Target aspirational loop:

```text
Discover (Jobright/etc.) → triage → apply (Simplify/ATS) → export tracker → local import → daily optimize
```

## Hard safety rules

1. **Never paste account passwords, 2FA codes, or session cookies into Cursor chat.**
2. **Never commit** `.env`, cookies, `storage_state.json`, or exported personal CSVs with secrets to git.
3. Prefer **you logged-in locally** + script uses your browser profile / saved session.
4. Auto-**submit** stays opt-in and off by default. First experiments stop at: discover list, open apply URL, autofill assist, export CSV.
5. Work-auth answers must stay truthful; no “answer No to sponsorship to pass ATS.”

Secrets stay only on your machine:

```text
secrets/          # gitignored
  .env            # optional paths only, not passwords if avoidable
  simplify_storage.json   # Playwright storage state YOU create
```

---

## What Cursor can and cannot do here

| Capability | Reality |
|---|---|
| Write scripts, run them locally, parse CSVs | Yes |
| “Remember” your password and log into Simplify every morning | **No — do not give passwords to the agent** |
| Use Jobright public API | None reliable for consumers |
| Scrape Jobright while logged in | Possible technically; fragile; may violate ToS; CAPTCHA/rate limits |
| Click Submit on every ATS | Hard: Greenhouse/Workday differ; CAPTCHA; MFA; high mis-apply cost |
| Simplify CSV export | Often UI/manual; community scrapers exist; treat as brittle |

So the experiment is not “Cursor holds my password.”  
It is “we probe each link and measure failure modes.”

---

## Experiment ladder (do in order)

### Exp A — Tracker sync only (safest, do today)

**Hypothesis:** Daily value comes from Simplify → local CSV more than from crawling.

1. You manually export Simplify tracker once (or copy table → CSV).
2. Save to `data/imports/simplify/YYYY-MM-DD.csv`.
3. Run `python3 scripts/daily_job_search.py`.

**Pass if:** import + dashboard + label suggestions work with zero passwords in chat.

**Bottleneck to record:** export clicks? column names? missing URLs?

### Exp B — Discovery shortlist without auto-apply

**Hypothesis:** Getting a daily candidate list is more valuable than auto-submit.

Options (pick one):

1. **Manual 10 min:** Jobright UI → save 10–20 links into `jobs/inbox/daily-YYYY-MM-DD.md`.
2. **Browser assist (you drive):** You stay logged into Jobright; agent only helps structure the list you paste.
3. **Local Playwright later:** Script opens Jobright with **your** saved storage state; dumps titles/URLs to `data/discovery/YYYY-MM-DD.csv`. No submit.

**Pass if:** we get a CSV of `{company, role, url, source}` for one day.

**Do not** auto-apply in Exp B.

### Exp C — Apply assist (human still clicks Submit)

**Hypothesis:** Autofill + correct resume choice is enough; full Submit automation is not worth risk yet.

1. For Broad roles: open company URL + Simplify Copilot; upload cluster PDF; **you** submit.
2. Log `resume_version`, `pursuit_lane`, minutes in local CSV.
3. Measure: minutes/application, error rate on auth questions.

**Pass if:** Broad apps drop below ~10–15 min each and auth answers stay correct.

### Exp D — Product Agent (optional)

If Jobright Agent / Simplify can auto-apply **inside their product**:

1. Restrict Agent to Broad/Practice only.
2. Cap volume (e.g. 10/day).
3. Nightly: export tracker → local import → review mistakes.

**Pass if:** Agent error rate on eligibility/auth is acceptable to you.

### Exp E — Full unattended apply (defer)

Only after A–D are stable. Requires:

- explicit allowlist of companies/role patterns
- kill switch
- no Core/adjacent roles
- logged audit of every submit
- acceptance that accounts may be banned

**Not the first experiment.**

---

## Bottleneck log (fill as you go)

| Step | Result | Blocker | Severity | Workaround |
|---|---|---|---|---|
| Jobright list export | | | | |
| Jobright scrape logged-in | | | | |
| Open company ATS | | | | |
| Simplify autofill | | | | |
| Auth questions | | | | |
| Click Submit | | | | |
| Simplify CSV export | | | | |
| Local import | | | | |
| Label suggestions | | | | |

---

## Recommended first experiment this week

**Only Exp A + light Exp B (manual paste).**

Why: early applications are low-stakes enough to learn process, but **credential sharing and blind submit** are high-stakes even on “unimportant” apps (wrong auth answer, spam filters, account flags).

When Exp A works for 3 days, we add a **local** Playwright probe for Simplify export **using storage state you create**, never a password in chat.

---

## Commands for Exp A

```bash
# after you drop the CSV:
python3 scripts/daily_job_search.py
open generated/daily/$(date +%F).md
open generated/label_suggestions.csv
```
