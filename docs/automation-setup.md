# Hands-off sync setup (local browser automation)

You want Cursor/scripts to pull Simplify data without manual CSV clicks.  
Passwords stay in `secrets/.env` on **your Mac** (gitignored). Do not commit them.

## What I need from you

Reply with these facts (password → only into `secrets/.env`, not necessarily in chat):

1. **Simplify account email**
2. **2FA on?** yes/no (if yes, use session-save method)
3. After login, what URL shows your tracker? (paste from browser bar if you can)
4. Do you also want **Jobright** discovery automation next? yes/no
5. Chrome already installed? (you have `/Applications/Google Chrome.app`)

Optional: create `secrets/.env` yourself:

```bash
cp secrets/.env.example secrets/.env
# edit secrets/.env — set SIMPLIFY_EMAIL and SIMPLIFY_PASSWORD
```

## Install (one time)

```bash
cd /Users/conny/Desktop/job-search-2026-2027-starter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-automation.txt
playwright install chromium
```

(Already created on this machine if `.venv` exists — just `source .venv/bin/activate`.)

## Preferred path (handles 2FA): save session once

```bash
source .venv/bin/activate
python scripts/automation/save_simplify_session.py
# log in in the Chrome window, open tracker, press ENTER in terminal
```

## Daily export → local repo

```bash
source .venv/bin/activate
python scripts/automation/export_simplify_tracker.py
python scripts/daily_job_search.py
```

## Scope of this first automation

| Done in this phase | Not yet |
|---|---|
| Open Simplify with saved session | Jobright full crawl |
| Try Export CSV / scrape tracker | Auto-click Submit on every ATS |
| Write `data/imports/simplify/YYYY-MM-DD.csv` | Unattended Core applications |

Auto-apply across Greenhouse/Workday is the next experiment **after** export works for 3 days.
