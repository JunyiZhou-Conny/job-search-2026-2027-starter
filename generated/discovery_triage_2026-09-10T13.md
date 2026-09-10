# Discovery triage — 2026-09-10T13

- Input rows: 212
- KEEP: 37
- LATER: 95
- SKIP: 80
- Evidence basis: board fields on all 212 rows.
- KEEP with resolved apply_url: 17
- KEEP still on Jobright only: 20

## KEEP (top 15 by fit; see CSV for the rest)

1. [NVIDIA — NVIDIA 2027 Internships: Deep Learning](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Deep-Learning_JR2023497-1) — core / data_ml — grad_display_hint: program_end — apply: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Deep-Learning_JR2023497-1
2. [Tesla — Internship, Machine Learning Engineer, Factory Software (Winter/Spring 2027)](https://jobright.ai/jobs/info/6aa1d337dbc0e60e37e13dce) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
3. [Capital One — Current Master's, AI Engineering Internship Program - Summer 2027](https://jobright.ai/jobs/info/6aa0177cea127c3794694e3a) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [S&P Global — Machine Learning Engineer - Summer Intern 2027](https://jobright.ai/jobs/info/6aa17ab43272060a8e3eff0c) — core / data_ml — grad_display_hint: program_end — apply: unresolved
5. [Amazon — Software Development Engineer I, ML Infra Services, Annapurna Labs](https://jobright.ai/jobs/info/6a4557fb0dd56c76cc2f31f9) — core / data_ml — grad_display_hint: program_end — apply: unresolved
6. [Notion — Software Engineer, Early Career (AI)](https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28
7. [Merck — 2027 Future Talent Program - AI/ML Computational Toxicology - Intern](https://jobright.ai/jobs/info/6a9f5b0d2c964816f65efe64) — core / health_ai — grad_display_hint: program_end — apply: unresolved
8. [Merck — 2027 Future Talent Program – Modeling & Informatics - Intern](https://jobright.ai/jobs/info/6aa189402f936e4a53dac32b) — core / health_ai — grad_display_hint: program_end — apply: unresolved
9. [Shield AI — Summer 2027 - Software Engineer Intern](https://jobs.lever.co/shieldai/8c850c75-081d-4d09-bebf-096379a93010) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.lever.co/shieldai/8c850c75-081d-4d09-bebf-096379a93010
10. [DV Trading LLC — AI Engineer Intern - Summer 2027](https://job-boards.greenhouse.io/dvtrading/jobs/4732429005) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/dvtrading/jobs/4732429005
11. [Delta Air Lines — Graduate Intern, Innovation - AI Engineering (Spring 2027)](https://jobright.ai/jobs/info/6a90e1bf8ffa38557e6cf351) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
12. [Activision Blizzard — Activision 2027 Summer Internships - Software Engineering](https://jobright.ai/jobs/info/6aa1e2fd0ffb3d4fea6b7a52) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
13. [The Aerospace Corporation — 2027 Machine Learning Engineering Graduate Intern](https://jobright.ai/jobs/info/6aa1e791500b01124c77f96f) — core / data_ml — grad_display_hint: program_end — apply: unresolved
14. [Verizon — Verizon Consumer Group: AI/ML Engineering Summer 2027 Internship](https://jobright.ai/jobs/info/6aa1a348ef23570cae2454a4) — core / data_ml — grad_display_hint: program_end — apply: unresolved
15. [Oscar Health — Data Scientist I](https://job-boards.greenhouse.io/oscar/jobs/7592274) — core / health_ai — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/oscar/jobs/7592274

Remaining KEEP rows: 22 (ICD Portal Summer 2027 AI Software Engineering / C++ Distributed Systems Developer / Data Platform / Java Software Engineering; IBM Associate Data Scientist 2027 - AI & Data Analytics and Data Scientist & AI ELH - RTP 2027; Northrop Grumman 2027 Associate Software Engineer / Software Engineer - Roy UT; Crowe Machine Learning Software Engineer 1; Booz Allen Hamilton Data Scientist Washington DC and Fort Meade — apply unresolved; Anyscale Software Engineer (Ray Core); Clera Forward Deployed Engineer (two SF cards) / Founding AI Engineer / Founding Agentic Engineer / Founding Engineer (AI/ML) / Founding Full Stack Engineer / ML Infrastructure Engineer / Software Engineer, AI & Data Systems; OpenAI Physical Design Engineer, Forward Deployed Engineering and Software Engineer, Host Assurance; Perplexity Member of Technical Staff (General Software Engineer, Infrastructure)). See `generated/discovery_triage_2026-09-10T13.csv`.

## Short SKIP themes

- Fully remote: 29 rows (`remote`).
- Non-US work location: 42 rows (`non_us_location`).
- Explicit 2026 job cycles: 2 rows (`start_date_conflict` / `timing_expired`: Merck 2026 Future Talent co-op; Postman AI Engineer Internship Summer 2026).
- Explicit incompatible hard gates: 2 rows (Amazon Robotics postdoc; Beth Israel postdoctoral fellow). Exclusive graduation/enrollment windows that are not PhD-only or polygraph stay notes, not skips (Amex Masters 2027 AI Engineer exclusive Dec 2027–June 2028 window → later under v6; Navy Federal “December 2027 or later” → later).
- Clearly non-target roles: 5 rows (`non_target_role`: Jane Street Campus Recruiter; Personal Programa De Referidos; Amazon Security and Loss Prevention Specialist; Clera Talent AI Operator; onsemi Summer 2027 Non-Engineering Internships). Volga German Language Data Evaluator was skipped on `remote` first.

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 12 filtered). Not personalized Matches.
- All 10 Jobright boards returned (boards_ok=10, 130 kept before merge). newgrad_swe 16; intern_swe 20; intern_ml_ai 17 (populated; no empty-board flake); intern_healthcare 2; newgrad_healthcare 0 (expected ~0). Intern healthcare is Merck 2026 co-op (skip) plus Merck 2027 Modeling & Informatics intern (keep).
- Newgrad `data_analysis`: remote A Helping Hand / A Full Renovation `Data Analyst` cluster plus other remote junior-analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1825 seen, 75 kept (Clera agency 58). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- American Express Masters 2027 AI Engineer was a `hard_gate` skip on 2026-09-08T22 for an exclusive Dec 2027–June 2028 graduation window. Under v6 that window is a non-blocking note; this run marks it `later`, not skip.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows (resolver collapsed both SF FDE cards onto Berlin `98ceb57b`, Founding AI onto already-applied `3dc0a0f6`, Founding Full Stack onto `9cd39527`). Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Activision / Capital One / Delta / ICD Portal / Merck / S&P / Tesla / Aerospace / Verizon / Amazon Annapurna / Crowe / IBM / Northrop KEEP rows have no verified unique careers-board match — left unresolved (wrong link worse than none).
- Oscar Health Greenhouse `oscar` Data Scientist I remains unique `7592274` (normalized off the hioscar career-page gh_jid).
- DV Trading Greenhouse `dvtrading` AI Engineer Intern Summer 2027 Chicago `4732429005` (not a New York twin).
- Shield AI Lever `shieldai` Summer 2027 SWE intern `8c850c75` (San Diego + DC/Dallas/Seattle).
- NVIDIA Workday `nvidia.wd5` / `NVIDIAExternalCareerSite` 2027 Deep Learning intern Santa Clara `JR2023497-1`.
- Notion Early Career (AI) Ashby `85947779-6b87-466a-98bc-30a640448c28` (SF).
- OpenAI FDE London / Madrid and Clera non-US FDE — `non_us_location` (hard skip wins over `fde`).
- OpenAI Physical Design Engineer, Forward Deployed Engineering (SF) kept on `fde`; physical-design flavor is a note. Do not invent FDE experience.
- Perplexity MTS Infrastructure form still has `external_artifact` — nonstandard hold; do not Submit.
- Evening KEEP that did not reappear (board rotation, not a scrape failure): Formlabs AI Software Intern Winter/Spring 2027; TikTok ML intern 2027 Search ranking; TikTok LIVE DS intern 2027; Nuclear Company Spring/Summer 2027 DS intern; CACI SWE intern Summer 2027; Zipline Enterprise Systems SWE intern Spring 2027.
- Morning KEEP that did not reappear: Advanced Space 2027 ML intern; Allen Control CV/ML and SWE intern 2027; Gallup DS intern; IBM Data Science and AI Intern RTP 2027 / Agent Engineer family; IMC ML Research intern Chicago; Meijer DS intern 2027; MISO 2027 DS intern; Notion Winter 2027 DS intern; Plexus Fall 2027 SWE intern; Home Depot 2027 DS intern; Workato AI intern; Kustomer Early Career Full Stack; Lila ML I/II; Mayo Associate AI/ML.
