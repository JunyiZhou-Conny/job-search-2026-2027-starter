# Daily discovery triage — 2026-07-26

## Summary

- Sources: Jobright Matches unavailable (no saved session); `newgrad_swe` OK (19); `intern_swe` OK (22)
- Merged unique URLs: **41**
- Decisions: **keep 18 · later 11 · skip 12**
- Evidence: board fields only; no job detail URLs opened
- Run timestamp: `2026-07-26T13:45:16-04:00` (automation trigger converted to America/New_York)

## KEEP

1. [ByteDance — Backend Development Engineer Intern (Infrastructure Platform Delivery), Fall 2026](https://jobright.ai/jobs/info/6a661c9a8d53603449609311) — core / cloud_swe — `program_end`
2. [Copart — Software Engineering Intern](https://jobright.ai/jobs/info/6a5fa5abf68dd368023e7b43) — broad / cloud_swe — `program_end`
3. [Gemini — Software Engineering Intern (Fall 2026)](https://jobright.ai/jobs/info/6a40816416b14939532835d3) — broad / cloud_swe — `program_end`
4. [MaxLinear — AI Intern](https://jobright.ai/jobs/info/6a457e880dd56c76cc2f3a03) — core / data_ml — `either`
5. [Neuralink — Firmware Engineer Intern, Robotics and Surgery Engineering](https://jobright.ai/jobs/info/6a3e325f78237a036d5e388a) — broad / health_ai — `either`
6. [Neuralink — Machine Learning Engineer Intern (Fremont)](https://jobright.ai/jobs/info/6a038dc98ecfd93cd9c0f6f5) — core / health_ai — `either`
7. [Neuralink — Machine Learning Engineer Intern (South San Francisco)](https://jobright.ai/jobs/info/6a51c40f8d7d3e6cf1cc296d) — core / health_ai — `either`
8. [PlusAI — Machine Learning Engineer Intern, Scenario Generation](https://jobright.ai/jobs/info/6a1b0dcb547e292ae139bf19) — core / data_ml — `either`
9. [Plymouth Rock Assurance — Data Engineer Intern/Co-op](https://jobright.ai/jobs/info/6a5de48895356634d79e2862) — core / data_ml — `either`
10. [Together AI — Systems Research Engineer Intern, GPU Programming (Fall 2026)](https://jobright.ai/jobs/info/6a512355bf63b66c79979464) — core / data_ml — `program_end`
11. [AEG — Software Engineer, CH-AXS](https://jobright.ai/jobs/info/6a2c4bddd3ec94183f4bc303) — broad / cloud_swe — `program_end`
12. [FieldAI — Embedded Systems Engineer, Federal](https://jobright.ai/jobs/info/6a1377d112f8b43cf398f13c) — core / cloud_swe — `program_end`
13. [Neuralink — Embedded Software Engineer, Implant Embedded Systems](https://jobright.ai/jobs/info/6a0f500d83d714428981e885) — core / health_ai — `program_end`
14. [OpenAI — Performance Modeling Engineer ~2](https://jobright.ai/jobs/info/6a5c5a3363a8f619507cd483) — core / data_ml — `program_end`
15. [Qualcomm — GPU Software Engineer (San Diego)](https://jobright.ai/jobs/info/6a50aae62e2ceb72963b4a5c) — core / cloud_swe — `program_end`
16. [Qualcomm — GPU Software Engineer (Boxborough, MA)](https://jobright.ai/jobs/info/6a50ab79d5d2a327b664cfef) — core / cloud_swe — `program_end`
17. [UST HealthProof — Data Engineer](https://jobright.ai/jobs/info/6a6620615c7e2d715ebb2f83) — broad / health_ai — `program_end`
18. [WD — Software Development Engineer (Firmware)](https://jobright.ai/jobs/info/6a4e82649469c0662034ba37) — broad / cloud_swe — `program_end`

## Skip themes

- Fully remote (`remote`): 5
- Non-target QA, IT support, coordinator, or technician work (`non_target_role`): 4
- Explicit citizenship/clearance/PhD or start-date gate (`hard_gate`): 3
- Some rows fire more than one theme.

## Needs attention

- Personalized Matches were not run because `secrets/jobright_storage.json` is absent.
- The board exporter exposed a known intern-table column quirk: company size appears under `h1b_signal` and requirements text under `is_new_grad_signal`. Those values were not treated as H1B facts.
- Suspected cross-URL duplicates: Copart Software Engineering Intern; FieldAI Embedded Systems Engineer-Federal; Neuralink Machine Learning Engineer Intern. One overlapping URL variant in each group was moved to `later` where appropriate.
- The VM clock lagged the trusted automation trigger date. Files and timestamps use the trigger's `2026-07-26` America/New_York run date.

No applications were submitted, and `data/applications.csv` was not modified.
