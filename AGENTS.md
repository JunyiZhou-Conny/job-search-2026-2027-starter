# Project Instructions

This repository is a job-search operating system, not a general notes folder.

## Core behavior

- Treat `data/applications.csv`, `data/networking.csv`, and `data/activity_log.csv` as structured records.
- Never invent application status, recruiter responses, sponsorship facts, graduation eligibility, dates, metrics, or referral outcomes.
- Distinguish verified facts from inference and unknowns.
- Preserve existing IDs and append history rather than rewriting it.
- Every active record should have one concrete `next_action` and, where useful, a `next_action_date`.
- Prefer a few role-cluster resumes plus targeted bullet edits over creating a completely new resume for every job.
- Do not submit an application, send a message, or claim an action was completed unless the user explicitly confirms it.
