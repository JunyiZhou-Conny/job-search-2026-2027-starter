# /record-application

After user confirms they submitted:

```bash
python3 scripts/jobsearch.py update-job JOB_ID \
  --status applied \
  --date-applied YYYY-MM-DD \
  --resume-version 2026-07-20_data-ml_v1.1 \
  --auth-work-authorized yes \
  --auth-needs-sponsorship yes \
  --next-action "Watch for OA / recruiter email" \
  --next-action-date YYYY-MM-DD \
  --log-note "User confirmed submission"
```

Set `label_source` remains manual for user-chosen lane if already set.
