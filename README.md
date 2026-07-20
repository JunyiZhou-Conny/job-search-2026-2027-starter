# Job Search 2026–2027

A local, version-controlled operating system for a U.S. tech job search.

## Start here

1. Edit `config/profile.yaml`.
2. Put your current LaTeX resume sources under `resumes/`.
3. Run:

```bash
python scripts/jobsearch.py add-job --company "Example" --role "Software Engineer, New Grad" --url "https://example.com/job" --source "LinkedIn" --cluster cloud_swe --employment-type new_grad --eligibility likely --priority A
python scripts/jobsearch.py dashboard
```

4. Open `generated/dashboard.md` in Cursor.
5. Follow `docs/first-7-days.md` and `docs/workflow.md`.

## System design

- `data/applications.csv` is the source of truth for applications.
- `data/networking.csv` is the source of truth for people and outreach.
- `data/activity_log.csv` preserves a chronological history.
- `jobs/` contains deeper dossiers only for high-priority roles.
- `resumes/` contains a small number of role-cluster resumes, not one full fork per posting.
- `generated/dashboard.md` is regenerated from the CSV files.
- `.cursor/rules/` keeps Cursor's behavior consistent.

## Daily cadence

- Discover and triage roles.
- Apply to eligible high-fit roles quickly.
- Attach networking to live roles.
- Update next actions before ending the session.

## Weekly cadence

```bash
python scripts/jobsearch.py weekly
python scripts/jobsearch.py dashboard
```

Review funnel conversion, stale applications, upcoming follow-ups, resume performance, and interview preparation gaps.
