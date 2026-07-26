# /ingest-job

Given JD text (or company + role + URL):

1. Extract company, role, location, employment type, requirements.
2. Run `python3 scripts/label_job.py --role "..." --company "..." --jd-text "..."`.
3. Show suggested labels with confidence + evidence.
4. Ask user to confirm before:
   ```bash
   python3 scripts/jobsearch.py add-job ...
   python3 scripts/label_job.py --job-id ... --jd-text "..." --apply
   ```
5. Never mark ineligible for sponsorship alone.
