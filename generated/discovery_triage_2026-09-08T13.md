# Discovery triage — 2026-09-08T13

- Input rows: 195
- KEEP: 36
- LATER: 82
- SKIP: 77
- Evidence basis: board fields on all 195 rows.
- KEEP with resolved apply_url: 15
- KEEP still on Jobright only: 21

## KEEP (top 15 by fit; see CSV for the rest)

1. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
2. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application
3. [Neuralink — Software Engineer Intern, Implant](https://boards.greenhouse.io/neuralink/jobs/6569018003?gh_jid=6569018003) — core / health_ai — grad_display_hint: program_end — apply: https://boards.greenhouse.io/neuralink/jobs/6569018003?gh_jid=6569018003
4. [ByteDance — Agent Evaluation & Evolution Machine Learning Engineer Intern (AML-Ark-US) - 2027 Summer](https://jobright.ai/jobs/info/6a886393cde3717f9e9b4ebd) — core / data_ml — grad_display_hint: program_end — apply: unresolved
5. [ByteDance — Agent Evaluation & Evolution Machine Learning Engineer Intern (AML-Ark-US) - 2027 Summer](https://jobright.ai/jobs/info/6a8863b9680f314a29d3bacb) — core / data_ml — grad_display_hint: program_end — apply: unresolved
6. [CoreWeave — Software Engineer, Inference AI/ML](https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006) — core / data_ml — grad_display_hint: program_end — apply: https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006
7. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
8. [ByteDance — Applied Machine Learning Production Engineer Graduate (AML-Production Engineer) - 2027 Start](https://jobright.ai/jobs/info/6a88639ad34f700f87fc84b2) — core / data_ml — grad_display_hint: program_end — apply: unresolved
9. [ByteDance — Software Engineer Intern (Distributed NoSQL Database Systems) - 2027 Summer](https://jobright.ai/jobs/info/6a86a196cc81eb647e9f317b) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
10. [TikTok — Machine Learning Engineer Intern (TikTok-Data-Search-Local Service) - 2027 Summer](https://jobright.ai/jobs/info/6a714fe9cb96192a36848660) — core / data_ml — grad_display_hint: program_end — apply: unresolved
11. [TikTok — Backend Software Engineer Intern (TikTok-Search) - 2027 Summer](https://jobright.ai/jobs/info/6a701a0fc56c0956e8adda58) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
12. [Merck — 2027 Future Talent Program - Nonclinical Drug Safety Data Scientist - Intern](https://jobright.ai/jobs/info/6a9f5b952c964816f65efe87) — core / health_ai — grad_display_hint: program_end — apply: unresolved
13. [Midcontinent Independent System Operator (MISO) — 2027 Summer Intern - Software Engineering](https://jobright.ai/jobs/info/6aa00725a2266b538d22dd22) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
14. [Midcontinent Independent System Operator (MISO) — 2027 Summer Intern - Data Science](https://jobright.ai/jobs/info/6a9ff2165b2d5633ef3bbc71) — core / data_ml — grad_display_hint: program_end — apply: unresolved
15. [OpenAI — Software Engineer, Host Assurance](https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1/application

Remaining KEEP rows: 21 (Manheim 2027 DS intern; additional 2027 TikTok DE/DS interns; US-site Clera founding/ML/FDE-adjacent agency rows; Perplexity infra MTS; Booz Allen junior AI + two DS cards; CACI / Citadel / Fanatics / SPA DS; IBM 2027 Associate DS Chicago). See `generated/discovery_triage_2026-09-08T13.csv`.

## Short SKIP themes

- Fully remote: 29 rows (`remote`).
- Non-US work location: 31 rows (`non_us_location`).
- Explicit 2026 job cycles: 6 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 8 rows (PhD-only titles). Exclusive graduation/enrollment windows are notes, not skips.
- Clearly non-target roles: 3 rows (`non_target_role`: recruiters, Philips field service).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 7 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 130 kept before merge).
- Intern `ml_ai`: 13 rows (populated; not the empty-board flake).
- Intern healthcare: 1 row (Gilead Computational Biologics intern) — later (no 2027 term; Fall-after-intern enrollment is a non-blocking note). Not a scrape failure.
- Newgrad healthcare: 1 row (Philips Field Service Engineer) — `non_target_role`. Not a scrape failure.
- Intern `data_analysis`: 1 row (Kite Pharma clinical data-management intern) — later.
- Newgrad `data_analysis`: Helping Hand remote analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1781 seen, 69 kept (Clera agency 50). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- 56 URLs also appeared on a prior triage with identical company/role/work_model/location, so those decisions were reused after hard-rule checks. Other repeats were re-decided because a hard rule fired first (remote / 2026 / non-US / PhD).
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade). Junior AI Engineer San Antonio Workday `R0247417` kept (title + city match).
- Neuralink Greenhouse `Software Engineer Intern, Implant` `6569018003` is Austin + South San Francisco (matches the Jobright card). Prior ML intern `6594261003` did not reappear this morning.
- ByteDance / TikTok / MISO / Merck / Manheim / IBM / CACI / Citadel / Fanatics / SPA KEEP rows have no verified careers-board match — left unresolved (wrong link worse than none).
- OpenAI Applied AI Engineer, Digital Natives is London, UK — `non_us_location`.
- SCE 2027 data-analytics intern cards require graduation December 2027 or later: non-blocking eligibility note under current `hard_gate` (remote card still skipped `remote`; on-site CA card is later).
- Previous-evening KEEP that did not reappear (not a scrape failure): IBM 2027 DS intern family (except Chicago Associate DS), NXP Summer 2027 ML intern, Neuralink ML intern, Sage 2027 SWE interns, CyberProof / UST HealthProof junior full-stack, Notion Early Career (AI), SpaceX ML Surrogate Modeling.

