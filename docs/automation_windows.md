# Windows automation (Task Scheduler)

1. Open Task Scheduler → Create Basic Task.
2. Trigger: Daily 8:30 AM weekdays.
3. Action: Start a program
   - Program: `python`
   - Arguments: `scripts\daily_job_search.py`
   - Start in: repo root

Logs land under `generated/logs/`. No auto-send of applications or messages.
