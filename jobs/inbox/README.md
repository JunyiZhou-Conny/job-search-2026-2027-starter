# Job inbox

Drop JD text here before running `/analyze-adjacent-role`:

```text
jobs/inbox/<company-role>.md
```

Example:

```text
jobs/inbox/etched-inference-engineer.md
```

Then in Cursor:

```text
/analyze-adjacent-role
Analyze jobs/inbox/etched-inference-engineer.md using the adjacent-role workflow.
```

Analyses and job-specific artifacts are written under `jobs/<company-role-slug>/`.
Job-specific resumes go under `resumes/job_specific/`.
