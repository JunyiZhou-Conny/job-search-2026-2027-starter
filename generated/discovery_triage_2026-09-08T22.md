# Discovery triage — 2026-09-08T22

- Input rows: 222
- KEEP: 43
- LATER: 105
- SKIP: 74
- Evidence basis: board fields on all 222 rows.
- KEEP with resolved apply_url: 21
- KEEP still on Jobright only: 22

## KEEP (top 15 by fit; see CSV for the rest)

1. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
2. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application
3. [Formlabs — AI Software Intern (Winter/Spring 2027)](https://careers.formlabs.com/job/8174874/apply/?gh_jid=8174874) — core / data_ml — grad_display_hint: dual_date — apply: https://careers.formlabs.com/job/8174874/apply/?gh_jid=8174874
4. [Gallup — AI/ML Research Intern — Summer 2027](https://job-boards.greenhouse.io/gallup/jobs/4395921009) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/gallup/jobs/4395921009
5. [Gallup — Data Science Intern — Summer 2027](https://job-boards.greenhouse.io/gallup/jobs/4395491009) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/gallup/jobs/4395491009
6. [Gallup — Software Engineer Intern — Summer 2027](https://job-boards.greenhouse.io/gallup/jobs/4395897009) — core / cloud_swe — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/gallup/jobs/4395897009
7. [Advanced Space — 2027 Machine Learning Summer Internship](https://job-boards.greenhouse.io/advancedspace/jobs/4324875009) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/advancedspace/jobs/4324875009
8. [IBM — Back End Developer Intern 2027 - RTP](https://jobright.ai/jobs/info/6aa05930dbc0e60e37e0d120) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
9. [Midcontinent Independent System Operator (MISO) — 2027 Summer Intern - Data Science](https://jobright.ai/jobs/info/6a9ff2165b2d5633ef3bbc71) — core / data_ml — grad_display_hint: program_end — apply: unresolved
10. [TikTok — Data Science Intern (TikTok Integrity and Safety) - 2027 Summer](https://jobright.ai/jobs/info/6a71a42202d93145bf89023b) — core / data_ml — grad_display_hint: program_end — apply: unresolved
11. [TikTok — Data Science Intern (TikTok Product) - 2027 Summer](https://jobright.ai/jobs/info/6a7284f8ee751e0c793493e5) — core / data_ml — grad_display_hint: program_end — apply: unresolved
12. [TikTok — Data Scientist Intern (VOD Data) - 2027 Summer](https://jobright.ai/jobs/info/6a72f51b6ffeee418e5b7eac) — core / data_ml — grad_display_hint: program_end — apply: unresolved
13. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
14. [OpenAI — Software Engineer, Host Assurance](https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1/application
15. [Perplexity — Member of Technical Staff (Software Engineer, Infrastructure)](https://jobs.ashbyhq.com/perplexity/76c9b39f-aecc-4247-b5f5-ebcd02dff7c3/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/perplexity/76c9b39f-aecc-4247-b5f5-ebcd02dff7c3/application

Remaining KEEP rows: 28 (US-site Clera founding/ML/FDE-adjacent agency rows; Datadog SWE intern unresolved; IBM 2027 DS/EL/agent family; Lila Sciences ML I/II; Mayo Associate AI/ML; Oscar Health DS I; Workato AI intern; Booz Allen / CACI / Citadel DS; Zebra SWE I). See `generated/discovery_triage_2026-09-08T22.csv`.

## Short SKIP themes

- Fully remote: 18 rows (`remote`).
- Non-US work location: 39 rows (`non_us_location`).
- Explicit 2026 job cycles: 4 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 4 rows (3 American Express Campus Graduate Masters 2027 AI Engineer cards — prior-run confirmed Dec 2027–June 2028 window; 1 TikTok 2027 PhD intern). Exclusive graduation/enrollment windows that are not that Masters gate stay notes, not skips.
- Clearly non-target roles: 9 rows (`non_target_role`: leave specialist, website intern, field-engineer apprentice, mainframe apprenticeship, clinical research assistant, data debriefer, quality data specialist, Clera founder’s associate).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 11 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 153 kept before merge).
- Intern `ml_ai`: 19 rows. Intern healthcare: 4 rows (GE field-engineer apprentice skip; Medpace informatics later; ORISE CDC fellowship later). Newgrad healthcare: 6 rows (3 Goldbelt remote analyst skips; Englewood CRA skip; Medtronic R&D I later; Oscar DS I keep). Higher healthcare volume than the usual ~0 after DOMAIN/STRONG is board content, not a scrape failure.
- Newgrad `data_analysis`: Goldbelt remote analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1769 seen, 71 kept (Clera agency 50). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Advanced Space 2027 ML intern already applied (Greenhouse `4324875009`); Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- 47 URLs also appeared on a prior triage with identical company/role/work_model/location, so those decisions were reused after hard-rule checks. Hard remote / non-US / 2026 / PhD / non-target skips were applied first. Other rows are new this evening (board rotation vs this morning).
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Datadog `Software Engineering Intern` title-only attached Paris `8114186`. US Boston/NY Summer is `8052118` and Winter is `8052095` — two US reqs, left unresolved.
- Oscar Health Greenhouse `oscar` re-verified (288 jobs). Data Scientist I is unique NY `7592274`. LA/Tempe Oscar cards on the board are Data Scientist II.
- IBM / TikTok / MISO / Mayo / CACI / Citadel / Zebra KEEP rows have no verified unique careers-board match — left unresolved (wrong link worse than none).
- American Express Campus Graduate Masters Summer Internship 2027 AI Engineer (NY / Phoenix / Sunrise): prior-run confirmed exclusive graduation December 2027–June 2028 — `hard_gate`. Undergraduate 2027 AI Engineer cards are later (`traditional_student_coop`).
- NVIDIA Research Scientist Physical AI PhD New College Grad 2026 — `start_date_conflict` + `hard_gate`.
- OpenAI FDE London / Madrid — `non_us_location` (hard skip wins over `fde`).
- Previous-morning KEEP that did not reappear (board rotation, not a scrape failure): MISO 2027 SWE intern, ByteDance 2027 intern/grad family, Manheim 2027 DS intern, Merck Nonclinical DS intern, Neuralink Implant SWE intern, TikTok 2027 Search SWE / Monetization DE / Local-Service ML interns, Clera Founding Engineer - ML Research + ML Infrastructure, Booz Allen Junior AI Engineer, CoreWeave Inference AI/ML, Fanatics DS I, SPA Junior/Journeyman DS.
