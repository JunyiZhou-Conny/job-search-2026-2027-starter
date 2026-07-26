# macOS automation (launchd)

Scripts generate files only — never send applications or messages.

## Cadence (discovery timestamps)

Job boards post all day. Ideal “fetch the second HR posts” is far-fetched for v1.
Practical experiment:

| When | What | Why |
|---|---|---|
| **~08:30** | `run_discovery.py` + `daily_job_search.py` | Morning shortlist + Simplify sync |
| **~16:00** | `run_discovery.py` only | Catch afternoon / late postings |
| Later | shorter intervals / webhooks | Only after dual-fetch proves value |

Every discovery row stores `fetched_at` (local ISO time) so you can see **when** the pull happened vs `posted_relative` (“2 hours ago”) from the board.

## Manual

```bash
cd /Users/conny/Desktop/job-search-2026-2027-starter
source .venv/bin/activate

# Discovery (Jobright matches + intern/newgrad minisites → merge)
python3 scripts/automation/run_discovery.py

# Ledger / plans (Simplify import, labels, daily plan)
python3 scripts/daily_job_search.py
```

## launchd example — morning + afternoon discovery

Create `~/Library/LaunchAgents/com.user.jobsearch.discovery.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.user.jobsearch.discovery</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/conny/Desktop/job-search-2026-2027-starter/.venv/bin/python3</string>
    <string>/Users/conny/Desktop/job-search-2026-2027-starter/scripts/automation/run_discovery.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>30</integer></dict>
    <dict><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/conny/Desktop/job-search-2026-2027-starter</string>
  <key>StandardOutPath</key>
  <string>/Users/conny/Desktop/job-search-2026-2027-starter/generated/logs/launchd_discovery.out</string>
  <key>StandardErrorPath</key>
  <string>/Users/conny/Desktop/job-search-2026-2027-starter/generated/logs/launchd_discovery.err</string>
</dict>
</plist>
```

Morning ledger job (optional second plist) can still call `daily_job_search.py` at 08:35.

```bash
launchctl load ~/Library/LaunchAgents/com.user.jobsearch.discovery.plist
```

ICS writing remains opt-in (`--write-calendar`).
