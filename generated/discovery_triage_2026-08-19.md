# Discovery triage — 2026-08-19

- Input rows: 117
- KEEP: 18
- LATER: 47
- SKIP: 52
- Evidence basis: board fields only; no posting URLs opened
- KEEP apply URLs resolved exact/strong: 3; still Jobright-only: 15

## KEEP

1. [ByteDance — Agent Evaluation & Evolution Machine Learning Engineer Intern (AML-Ark-US) - 2027 Summer](https://jobright.ai/jobs/info/6a7ae06667a1ad0bc53d4845) — core / data_ml — grad_display_hint: dual_date
2. [IBM — Intern Data Scientist 2027 – AI & Data Analytics](https://jobright.ai/jobs/info/6a7fcd50927c79391ad0d13b) — core / data_ml — grad_display_hint: dual_date
3. [IBM — Intern Data Scientist 2027 – AI & Data Analytics](https://jobright.ai/jobs/info/6a7fcd6ab56bea5779c0f599) — core / data_ml — grad_display_hint: dual_date
4. [TikTok — Data Science Intern (TikTok Integrity and Safety) - 2027 Summer](https://jobright.ai/jobs/info/6a71a42202d93145bf89023b) — core / data_ml — grad_display_hint: dual_date
5. [TikTok — Data Science Intern (TikTok LIVE) - 2027 Summer](https://jobright.ai/jobs/info/6a71a40d02d93145bf890236) — core / data_ml — grad_display_hint: dual_date
6. [TikTok — Data Science Intern (TikTok Product) - 2027 Summer](https://jobright.ai/jobs/info/6a7284f8ee751e0c793493e5) — core / data_ml — grad_display_hint: dual_date
7. [TikTok — Data Scientist Intern (VOD Data) - 2027 Summer](https://jobright.ai/jobs/info/6a72f51b6ffeee418e5b7eac) — core / data_ml — grad_display_hint: dual_date
8. [AlphaLife Sciences — AI Software Engineer](https://jobright.ai/jobs/info/6a453a674f64ba41dcb4c9fe) — core / health_ai — grad_display_hint: dual_date
9. [Booz Allen Hamilton — Data Engineer](https://jobright.ai/jobs/info/6a7f8005ad9ff00c26baeab5) — broad / data_ml — grad_display_hint: dual_date
10. [Booz Allen Hamilton — Data Scientist](https://jobright.ai/jobs/info/6a66b1920c8e2b4f36dd5a8b) — broad / data_ml — grad_display_hint: dual_date
11. [Booz Allen Hamilton — Data Scientist](https://jobright.ai/jobs/info/6a2376936624e500cad0bbfc) — broad / data_ml — grad_display_hint: dual_date
12. [ByteDance — Machine Learning Engineer, AML - Engine (Multiple Positions)](https://jobright.ai/jobs/info/6a85503b2f4f0014cae2461f) — core / data_ml — grad_display_hint: dual_date
13. [Capgemini — Junior AI Engineer Job Details | Capgemini](https://jobright.ai/jobs/info/6a848f93e12474455273b1b5) — core / data_ml — grad_display_hint: dual_date
14. [Hayden AI — Associate Data Scientist](https://jobright.ai/jobs/info/6a574774367e61670f5aedc1) — core / data_ml — grad_display_hint: dual_date
15. [Radian — Data Scientist I, MIRS (Hybrid - at least 3 days in NYC office)](https://jobright.ai/jobs/info/6a8316793eeac101cfa9d536) — core / data_ml — grad_display_hint: dual_date
16. [Relativity Space — AI Software Engineer](https://jobright.ai/jobs/info/6a84b3a42f4f0014cae2241b) — core / data_ml — grad_display_hint: dual_date
17. [SpaceX — AI Engineer, Platform Infrastructure, Special Programs](https://jobright.ai/jobs/info/6a85863674e02153f145754a) — core / cloud_swe — grad_display_hint: dual_date
18. [Uber — Data Scientist I, Tech](https://jobright.ai/jobs/info/6a7e2319e2030208f2767d92) — core / data_ml — grad_display_hint: dual_date

## Short SKIP themes

- Explicit 2026 job cycles: 23 rows (`start_date_conflict` / `timing_expired`).
- Fully remote: 13 rows (`remote`); sponsorship columns were not used as the reason.
- Incompatible hard gates: 20 rows (`hard_gate`), including PhD-only, exclusive bachelor's enrollment, Dec 2027–2028 graduation windows, remaining-term Master's join rules, and a US-citizen/PR-only listing.
- Clearly non-target roles: 7 rows (`non_target_role` / campus biomedical or clinical-ops data), excluding rows already counted under 2026/remote.

## Anomalies

- intern_ml_ai first scrape returned 0 rows; a second scrape of that board alone produced 19 rows and was merged in.
- Healthcare boards were nonzero (intern 3, newgrad 4) and were triaged on board evidence rather than treated as parse failures.
- Several same-company/title rows have distinct Jobright URLs and were retained as separate records (Amazon 2026 internships, IBM, Booz Allen, Magnera, BCG X, Tennant, USC).
- Intern-board `h1b_signal` cells often hold company size; those values were not treated as H1B truth.
- LATER count is 47; strong-fit internships without an explicit 2027 term were not promoted to KEEP.
