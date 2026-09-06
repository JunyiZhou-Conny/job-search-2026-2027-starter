# Discovery triage — 2026-09-06T13

- Input rows: 228
- KEEP: 50
- LATER: 87
- SKIP: 91
- Evidence basis: board fields only; no posting URLs opened
- KEEP with resolved apply_url: 20
- KEEP still on Jobright only: 30

## KEEP (top 15 by fit; see CSV for the rest)

1. [Schonfeld — 2027 Data Science Intern](https://job-boards.greenhouse.io/schonfeld/jobs/8171692) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/schonfeld/jobs/8171692
2. [Citadel — Sector Data Scientist – 2027 Intern (US)](https://jobright.ai/jobs/info/6a7a308fbb6ca93ae561a556) — core / data_ml — grad_display_hint: program_end — apply: unresolved
3. [Naval Nuclear Laboratory (FMP) — Data Science Internship Summer 2027](https://jobright.ai/jobs/info/6a9bfc25a7ba386c5d66dd39) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [PepsiCo — 2027 Summer Intern: Technology Data & Analytics, Data Engineer & Data Science](https://jobright.ai/jobs/info/6a9860a483fc633357631306) — core / data_ml — grad_display_hint: program_end — apply: unresolved
5. [Rippling — Machine Learning Software Engineer Intern - Winter 2027](https://jobright.ai/jobs/info/6a55f31cf7517b519ad5221c) — core / data_ml — grad_display_hint: program_end — apply: unresolved
6. [The Walt Disney Company — Commercial Data Science Intern, Spring 2027](https://jobright.ai/jobs/info/6a9b58829c24314c35f98fe8) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
7. [TikTok — (General Hire) Machine Learning Engineer Intern (TikTok-Recommendation) - 2027 Summer](https://jobright.ai/jobs/info/6a6ffdbdcd3bac13d370951e) — core / data_ml — grad_display_hint: program_end — apply: unresolved
8. [TikTok — (General Hire) Machine Learning Engineer Intern (Trust and Safety - CV/NLP/Multimodal LLM) - 2027 Summer](https://jobright.ai/jobs/info/6a6ffdd0c56c0956e8add73f) — core / data_ml — grad_display_hint: program_end — apply: unresolved
9. [TikTok — Data Scientist Intern (VOD Data) - 2027 Summer](https://jobright.ai/jobs/info/6a72f51b6ffeee418e5b7eac) — core / data_ml — grad_display_hint: program_end — apply: unresolved
10. [TikTok — Machine Learning Engineer Intern (TikTok-Data-Search-Local Service) - 2027 Summer](https://jobright.ai/jobs/info/6a714fe9cb96192a36848660) — core / data_ml — grad_display_hint: program_end — apply: unresolved
11. [TikTok — Machine Learning Engineer Intern (TikTok-Data-Search-Recommendation) - 2027 Summer](https://jobright.ai/jobs/info/6a7348bd6a034212ea0267da) — core / data_ml — grad_display_hint: program_end — apply: unresolved
12. [TikTok — Research Engineer Intern, Agentic Systems & AI Infrastructure (TikTok-Generalized Arch) - 2027 Summer](https://jobright.ai/jobs/info/6a701a18160eda5948e8d487) — core / data_ml — grad_display_hint: program_end — apply: unresolved
13. [TikTok — Software Engineer Intern (TikTok Search Architecture) - 2027 Fall](https://jobright.ai/jobs/info/6a8667454afae74a08344c4f) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
14. [Walt Disney World — Commercial Data Science Intern, Spring 2027](https://jobright.ai/jobs/info/6a9b50fbd5ff1f3f1c39ec79) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
15. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application

Remaining KEEP rows: 35 (Clera agency US-site rows, additional 2027 interns, and broad-lane new-grad). See `generated/discovery_triage_2026-09-06T13.csv`.

## Short SKIP themes

- Fully remote: 23 rows (`remote`).
- Non-US work location: 47 rows (`non_us_location`).
- Explicit 2026 job cycles: 11 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 8 rows (PhD-only / clearance / poly).
- Clearly non-target roles: 7 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 9 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 130 kept before merge).
- Newgrad healthcare: 2 rows (DaVita remote clinical analyst; Orthofix Design Engineer) — skipped `remote` / `non_target_role`.
- Intern healthcare: 3 rows (Medpace Fall 2026 clinical data x2 / Neuralink biomedical) — triaged on board text.
- Newgrad `data_analysis`: includes 8 remote Full Renovation / Helping Hand `Data Analyst` twins — `remote` skip; not a scrape failure.
- Intern `ml_ai`: 19 rows (populated; not the empty-board flake).
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1851 seen, 98 kept (Clera agency 75). `g2_candidate` is a form fact, not a triage decision.
- Zero URL overlap with `data/applications.csv`.
- 157 URLs also appeared on the 2026-09-05T22 triage; board fields were identical so those decisions were reused. 71 URLs are new this morning.
- JPMorganChase `2027 Data & AI Program` intern titled Analyst marked `later` to match the reused Chase twin (analyst, not SWE/ML IC).
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Jobright Clera KEEP rows left unresolved. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Neuralink Greenhouse `Software Engineer Intern, Infrastructure` (`5469298003`) is South San Francisco only. Fremont Jobright card left unresolved.
- Added verified board this run: WHOOP (Ashby `whoop`; Software Engineer I (Backend) Boston OnSite `0623a9e9`).
- Previous-evening KEEP that did not reappear on today's boards (not a scrape failure): Fab2 infra intern, GE Appliances Fall 2027 co-op, IBM 2027 interns, Neuralink ML intern, The Nuclear Company 2027 AI research interns, Booz Allen Junior AI Engineer, Crowe ML SWE 1, Quantifind Assoc DS, RSM Fall 2027 AI SWE.

