# Linux automation (cron)

```bash
crontab -e
```

```cron
30 8 * * 1-5 cd /path/to/job-search-2026-2027-starter && /usr/bin/python3 scripts/daily_job_search.py >> generated/logs/cron.log 2>&1
```

Generates plans/dashboards only; no outbound messaging.
