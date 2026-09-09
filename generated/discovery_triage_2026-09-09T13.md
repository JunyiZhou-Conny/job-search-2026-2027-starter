# Discovery triage — 2026-09-09T13

- Input rows: 233
- KEEP: 40
- LATER: 115
- SKIP: 78
- Evidence basis: board fields on all 233 rows.
- KEEP with resolved apply_url: 27
- KEEP still on Jobright only: 13

## KEEP (top 15 by fit; see CSV for the rest)

1. [Advanced Space — 2027 Machine Learning Summer Internship](https://job-boards.greenhouse.io/advancedspace/jobs/4324875009) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/advancedspace/jobs/4324875009
2. [Allen Control Systems — Computer Vision/Machine Learning Intern, 2027](https://jobs.ashbyhq.com/allen-control-systems/a7831fef-7125-4c03-b828-5f0472989037) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/allen-control-systems/a7831fef-7125-4c03-b828-5f0472989037
3. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
4. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application
5. [Gallup — Data Science Intern — Summer 2027](https://job-boards.greenhouse.io/gallup/jobs/4395491009) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/gallup/jobs/4395491009
6. [IMC Trading — Machine Learning Research Intern - Summer 2027 - Chicago](https://job-boards.eu.greenhouse.io/imc/jobs/4907430101) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.eu.greenhouse.io/imc/jobs/4907430101
7. [Notion — Data Science Intern (Winter 2027)](https://jobs.ashbyhq.com/notion/a67d6f2b-7c13-41d0-b36b-b2f662c9873e) — core / data_ml — grad_display_hint: dual_date — apply: https://jobs.ashbyhq.com/notion/a67d6f2b-7c13-41d0-b36b-b2f662c9873e
8. [The Nuclear Company — Spring 2027 Data Science Intern](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383218008) — core / data_ml — grad_display_hint: dual_date — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383218008
9. [The Nuclear Company — Summer 2027 Data Science Intern](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383244008) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383244008
10. [IBM — Data Science and AI Intern - RTP 2027](https://jobright.ai/jobs/info/6a9e282e27c94c3d5a1cb5cf) — core / data_ml — grad_display_hint: program_end — apply: unresolved
11. [Midcontinent Independent System Operator (MISO) — 2027 Summer Intern - Data Science](https://jobright.ai/jobs/info/6a9ff2165b2d5633ef3bbc71) — core / data_ml — grad_display_hint: program_end — apply: unresolved
12. [Plexus Corp. — Intern - Software Engineer (Fall 2027)](https://jobright.ai/jobs/info/6a97409d455eaf6a08c1bc2c) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
13. [The Home Depot — 2027 Summer Internship - Data Science & Analytics](https://jobright.ai/jobs/info/6a9710c7f5337b2cf731fcf0) — core / data_ml — grad_display_hint: program_end — apply: unresolved
14. [Meijer — Data Science Intern - Summer 2027](https://jobright.ai/jobs/info/6aa03f50a2266b538d22f21a) — broad / data_ml — grad_display_hint: program_end — apply: unresolved
15. [Kustomer — Software Engineer, Full Stack (Early Career)](https://jobs.ashbyhq.com/kustomer/4037272a-7fd3-4040-906b-47fde875a817) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/kustomer/4037272a-7fd3-4040-906b-47fde875a817

Remaining KEEP rows: 25 (Allen Control SWE intern 2027; IBM 2027 DS/EL/agent family; Workato AI intern; Anyscale Ray Core; US-site Clera founding/ML/FDE-adjacent agency rows; OpenAI Host Assurance; Perplexity infra MTS; Booz Allen DS; Lila ML I/II; Mayo Associate AI/ML; Notion Early Career AI; Oscar DS I). See `generated/discovery_triage_2026-09-09T13.csv`.

## Short SKIP themes

- Fully remote: 31 rows (`remote`).
- Non-US work location: 38 rows (`non_us_location`).
- Explicit 2026 job cycles: 1 row (`start_date_conflict` / `timing_expired`: Hoffman Construction Data Analyst Intern School Year 2026-27).
- Explicit incompatible hard gates: 2 rows (Mayo Clinic / Mayo Clinic Healthcare London Bioinformatics Intern — PhD in progress). Exclusive graduation/enrollment windows that are not PhD-only or polygraph stay notes, not skips.
- Clearly non-target roles: 6 rows (`non_target_role`: IPG Software Product Manager; Clera founder’s associate; SWBC/SWIVEL Quality Engineering Intern; Welo speech/voice language-analyst cards). Volga German Language Data Evaluator was skipped on `remote` first.

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 9 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 159 kept before merge).
- Intern `ml_ai`: 21 rows. Intern healthcare: 5 rows (BCBS reimbursement later; Boston Children’s clinical informatics later; Boston Scientific R&D later; Mayo PhD skip; Stryker R&D later). Newgrad healthcare: 1 row (Arthrex Engineer I Service Development later). Healthcare volume above the usual ~0 after DOMAIN/STRONG is board content, not a scrape failure.
- Newgrad `data_analysis`: 20 remote A Full Renovation LLC Data Analyst cards — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1790 seen, 74 kept (Clera agency 55). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Advanced Space 2027 ML intern already applied (Greenhouse `4324875009`); Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- 65 URLs and 7 additional fingerprints also appeared on a 2026-09-08 triage with identical company/role/work_model/location, so those decisions were reused after hard-rule checks. Hard remote / non-US / 2026 / PhD / non-target skips were applied first. Other rows are new this morning (board rotation vs last evening).
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows (resolver collapsed two SF FDE cards onto `2dbfc235`, Founding AI onto already-applied `3dc0a0f6`, Founding Engineer Intern onto `d3c69268`, Founding Full Stack onto `9cd39527`). Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Allen Control Jobright title `Software Engineering Inten, 2027` matched Greenhouse FT `Software Engineer` `4534368008`. Replaced with verified Ashby `allen-control-systems` `ed5c58a7` (`Software Engineering Intern, 2027`, Austin). CV/ML intern `a7831fef` title-exact.
- IBM / MISO / Meijer / Plexus / Home Depot / Mayo KEEP rows have no verified unique careers-board match — left unresolved (wrong link worse than none).
- IMC Trading Greenhouse slug `imc` re-verified: `4907430101` is Machine Learning Research Intern Summer 2027, location Chicago US (board host is eu.greenhouse).
- Notion Early Career (AI) Ashby `85947779` re-verified SF. Winter 2027 DS intern is `a67d6f2b`.
- Oscar Health Greenhouse `oscar` re-verified. Data Scientist I is unique `7592274`.
- Nuclear Company Greenhouse `thenuclearcompany` Spring DS intern `5383218008` / Summer `5383244008` (not the AI Applied Research ids).
- Added verified boards: Allen Control Systems Ashby `allen-control-systems`; Kustomer Ashby `kustomer`; IMC Trading Greenhouse `imc`.
- OpenAI FDE London / Madrid — `non_us_location` (hard skip wins over `fde`).
- Perplexity MTS Infrastructure form still has `external_artifact` — nonstandard hold; do not Submit.
- Previous-evening KEEP that did not reappear (board rotation, not a scrape failure): Formlabs AI Software Intern Winter/Spring 2027; Gallup AI/ML and SWE intern; IBM Back End Developer Intern 2027 RTP; TikTok 2027 DS intern family; Datadog SWE intern.

