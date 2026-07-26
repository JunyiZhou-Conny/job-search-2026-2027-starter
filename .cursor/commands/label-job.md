# /label-job

Given a job id and/or JD text:

1. Run `python3 scripts/label_job.py --job-id ... --jd-text "..."` (or `--jd-file`).
2. Present suggestions with confidence and reasons.
3. Ask user to confirm before `--apply`.
4. Never overwrite `label_source=manual` unless user requests force override.
5. Remind: sponsorship alone ≠ ineligible.
