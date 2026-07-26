# /daily-plan

Run the local daily operating loop and summarize results for the user.

1. Run `python3 scripts/daily_job_search.py` (calendar dry-run).
2. Open and summarize:
   - `generated/daily/YYYY-MM-DD.md`
   - `generated/outreach/YYYY-MM-DD.md`
   - `generated/review_queue.csv` (errors only)
3. List what the user must manually approve (applications, outreach sends).
4. Do not send messages or submit applications.
