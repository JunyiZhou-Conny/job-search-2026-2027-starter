# Schema migration notes

## 2026-07-20 additive migration

1. Automatic backup to `data/backups/` before writes.
2. Run:

```bash
python3 scripts/migrate_schema.py --dry-run
python3 scripts/migrate_schema.py
```

3. Changes:
   - `applications.csv` expanded with aliases (`job_id`, `job_url`, `hard_eligibility`, stage dates, label fields, etc.).
   - Legacy values mapped: eligibility→hard_eligibility; sponsorship verified/likely/no→supportive/historically_possible/explicit_no.
   - `contacts.csv` created; `networking_interactions.csv` created; legacy `networking.csv` retained.
   - `resume_versions.csv` seeded for v1.1 cluster resumes + base.

4. Resume files were **not** moved from `resumes/cloud_swe|data_ml|health_ai/` (avoid breaking paths). Target `resumes/clusters/` is optional later via symlink.
