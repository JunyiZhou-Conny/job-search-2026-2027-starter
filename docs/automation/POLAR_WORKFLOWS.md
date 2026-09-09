# Polar Workflow prompts

Saved Polar Workflows store a thin bootstrap only. They open a stable raw
`main` URL on every run. Do not paste a new 3,000-word prompt after a
Cursor patch.

Canonical policy lives in YAML and docs. Generated instructions live in
`generated/polar/workflows/`. Compile with
`python3 scripts/build_polar_runtime.py`.

Until `main` has the compiled files, replace `main` in the raw URL with
the production branch name.

Runtime file Polar also opens from each generated workflow:

`https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md`

Queue reference: `docs/automation/POLAR_QUEUE.md`.

| Workflow | Eastern Time | Polar mode |
|---|---|---|
| `discover-jobs-hourly` | `0 * * * *` (minute 00) | Saved Workflow. Named local profile. Discovery and Sheet writes only. |
| `apply-ready-jobs` | `20 * * * *` (minute 20) | Saved Workflow. Same profile. Execution with the configured cap. |
| `daily-job-summary` | `30 21 * * *` (21:30) | Saved Workflow. Sheet read and one email. No application clicks. |
| `production-learning-daily` | `0 22 * * *` (22:00) | Saved Workflow. Sanitized learning report. No application clicks. |
| `polar-scheduler-heartbeat` | `5 * * * *` until proven | Saved Workflow. Harmless page plus one heartbeat row. |
| `polar-github-write-canary` | manual | One-time proof. Do not schedule. |
| `chatgpt-production-review` | disabled | Optional second opinion. Never a Cursor gate. |
| `cursor-production-maintenance` | disabled | Reads Polar Production report directly. Stop before merge. |
| `polar-sheet-migration` | manual once | Add missing Sheet tabs. Preserve current rows. |

Attach no secrets. Phone and email stay in the browser profile.

## discover-jobs-hourly

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/discover-jobs-hourly.md
Read it fully.
Follow the latest instructions for this workflow (discover-jobs-hourly).
Then execute.
Do not browse the rest of GitHub.
```

## apply-ready-jobs

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/apply-ready-jobs.md
Read it fully.
Follow the latest instructions for this workflow (apply-ready-jobs).
Then execute.
Do not browse the rest of GitHub.
```

## daily-job-summary

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/daily-job-summary.md
Read it fully.
Follow the latest instructions for this workflow (daily-job-summary).
Then execute.
Do not browse the rest of GitHub.
```

## production-learning-daily

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/production-learning-daily.md
Read it fully.
Follow the latest instructions for this workflow (production-learning-daily).
Then execute.
Do not browse the rest of GitHub.
```

## polar-scheduler-heartbeat

Run this before overnight autonomous Submit. Polar should be backgrounded. The screen should be locked. The Mac stays powered and online.

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/polar-scheduler-heartbeat.md
Read it fully.
Follow the latest instructions for this workflow (polar-scheduler-heartbeat).
Then execute.
Do not browse the rest of GitHub.
```

Record the first locked-screen result in `docs/state/decisions.tsv` after a human or Polar report exists. Do not invent that result.

## polar-github-write-canary

Manual one-time proof. Do not schedule.

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/polar-github-write-canary.md
Read it fully.
Follow the latest instructions for this workflow (polar-github-write-canary).
Then execute.
Do not browse the rest of GitHub.
```

## polar-sheet-migration

Paste this once after the PR lands. It adds missing tabs and headers. It does not rewrite existing queue, writing_log, or heartbeat rows.

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/polar-sheet-migration.md
Read it fully.
Follow the latest instructions for this workflow (polar-sheet-migration).
Then execute.
Do not browse the rest of GitHub.
```

## chatgpt-production-review

Optional. Manual when Junyi wants an independent second opinion. Never required for Cursor maintenance.

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/chatgpt-production-review.md
Read it fully.
Follow the latest instructions for this workflow (chatgpt-production-review).
Then execute.
Do not browse the rest of GitHub.
```

## cursor-production-maintenance

Disabled until a real Polar Production report exists. Cursor reads that report directly. ChatGPT is not required. Stop before merge.

```text
Open https://raw.githubusercontent.com/JunyiZhou-Conny/job-search-2026-2027-starter/main/generated/polar/workflows/cursor-production-maintenance.md
Read it fully.
Follow the latest instructions for this workflow (cursor-production-maintenance).
Then execute.
Do not browse the rest of GitHub.
```
