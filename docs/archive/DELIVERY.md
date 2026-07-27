# Delivery summary — OS expansion

See also `docs/AUDIT_PHASE0.md`.

## What you can run now

```bash
python3 scripts/migrate_schema.py
python3 scripts/validate_data.py
python3 scripts/dedupe_applications.py
python3 scripts/label_job.py --role "Software Engineer" --jd-text "..." 
python3 scripts/generate_outreach_queue.py
python3 scripts/generate_daily_plan.py
python3 scripts/generate_analytics.py
python3 scripts/generate_calendar.py          # dry-run
python3 scripts/generate_calendar.py --write  # write ICS
python3 scripts/daily_job_search.py
python3 scripts/jobsearch.py dashboard
python3 -m unittest tests/test_core.py
```

## Automated vs still manual

| Automated (local files) | Still manual |
|---|---|
| Schema migrate / validate / dedupe proposals | Submit applications |
| Simplify CSV import (owned fields only) | Send LinkedIn/email |
| Label *suggestions* | Approve/apply labels |
| Daily plan + outreach queue drafts | Actually send outreach |
| Analytics + dashboard | Interpret with sample-size rules |
| ICS dry-run / optional write | Google Calendar OAuth (Phase 6) |

## Not done yet (Phase 6 / polish)

- Full Google Calendar provider + OAuth
- Cursor Background Agent API automation
- Exhaustive `.cursor/commands/*` set (core ones added)
- Physical move to `resumes/clusters/` (deferred; files preserved in place)
