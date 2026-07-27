# Daily discovery triage — 2026-07-27

## Summary

- Sources: Jobright Matches unavailable (no saved session); `newgrad_swe` OK (19); `intern_swe` OK (22)
- Merged unique URLs: **41**
- Decisions: **keep 9 · later 16 · skip 16**
- Evidence: board fields only; no job detail URLs opened
- Run timestamp: `2026-07-27T09:00:23-04:00` (automation trigger converted to America/New_York)

## KEEP

1. [Justworks — Software Engineer](https://jobright.ai/jobs/info/69b4223d569738374138bd15) — broad / cloud_swe — `program_end`
2. [KRM22 — Junior AWS & IT Engineer](https://jobright.ai/jobs/info/6a673594872eb74f9ead859f) — core / cloud_swe — `program_end`
3. [MatX — Software Engineer - Kernels](https://jobright.ai/jobs/info/6a4242e61cc9cc2b12feb45d) — core / data_ml — `program_end`
4. [North Carolina Department of Agriculture and Consumer Services — ITPA11 - Data Warehouse Developer](https://jobright.ai/jobs/info/6a674160872eb74f9ead8724) — broad / data_ml — `program_end`
5. [Science and Technology Corporation (STC) — Software Development Engineer](https://jobright.ai/jobs/info/6a672d5a2bf1fb2b719244b3) — broad / cloud_swe — `program_end`
6. [Scout AI — Junior Firmware Engineer](https://jobright.ai/jobs/info/6a52114b8ef95364ead8cb0a) — core / cloud_swe — `program_end`
7. [UST — Associate Data Engineer (Early Career Talent)](https://jobright.ai/jobs/info/6a44a21b57ffc22029407b57) — core / data_ml — `program_end`
8. [UST — Jr Fullstack Engineer](https://jobright.ai/jobs/info/6a6658c287cef057612cfdf6) — broad / cloud_swe — `program_end`
9. [UST — Junior Full Stack Developer](https://jobright.ai/jobs/info/6a4c65016189f64e437f1e80) — broad / cloud_swe — `program_end`

## Skip themes

- Explicit 2026 internship terms (`start_date_conflict`, `timing_expired`): 5
- Explicit PhD, undergraduate-only, citizenship, or clearance gates (`hard_gate`): 10
- Fully remote roles (`remote`): 3
- General IT/support work outside target clusters (`non_target_role`): 2
- Some rows fire more than one theme.

## Needs attention

- Personalized Matches were not run because `secrets/jobright_storage.json` is absent.
- Internship rows without an explicit 2027 term were placed in `later`, even when fit was strong; verify timing before promotion.
- The board exporter exposed a known intern-table column quirk: company size appears under `h1b_signal` and requirements text under `is_new_grad_signal`. Those values were not treated as H1B facts.
- Suspected cross-URL duplicates: NSA C2DP and several UST Associate Data Engineer / junior full-stack listings.
- Parse anomaly: the North Carolina Department of Agriculture row lists Lansing, Michigan; verify employer and location before applying.
- No URLs overlap the current `data/applications.csv` ledger.
- The VM clock lagged the trusted automation trigger date. Files and timestamps use the trigger's `2026-07-27` America/New_York run date.

No applications were submitted, and `data/applications.csv` was not modified.
