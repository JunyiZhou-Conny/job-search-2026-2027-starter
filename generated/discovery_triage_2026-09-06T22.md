# Discovery triage — 2026-09-06T22

- Input rows: 223
- KEEP: 54
- LATER: 90
- SKIP: 79
- Evidence basis: board fields only; no posting URLs opened
- KEEP with resolved apply_url: 20
- KEEP still on Jobright only: 34

## KEEP (top 15 by fit; see CSV for the rest)

1. [Schonfeld — 2027 Data Science Intern](https://job-boards.greenhouse.io/schonfeld/jobs/8171692) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/schonfeld/jobs/8171692
2. [Citadel — Sector Data Scientist – 2027 Intern (US)](https://jobright.ai/jobs/info/6a7a308fbb6ca93ae561a556) — core / data_ml — grad_display_hint: program_end — apply: unresolved
3. [Naval Nuclear Laboratory (FMP) — Data Science Internship Summer 2027](https://jobright.ai/jobs/info/6a9bfc25a7ba386c5d66dd39) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [PepsiCo — 2027 Summer Intern: Technology Data & Analytics, Data Engineer & Data Science](https://jobright.ai/jobs/info/6a9860a483fc633357631306) — core / data_ml — grad_display_hint: program_end — apply: unresolved
5. [The Walt Disney Company — Commercial Data Science Intern, Spring 2027](https://jobright.ai/jobs/info/6a9b58829c24314c35f98fe8) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
6. [TikTok — (General Hire) Machine Learning Engineer Intern (TikTok-Recommendation) - 2027 Summer](https://jobright.ai/jobs/info/6a6ffdbdcd3bac13d370951e) — core / data_ml — grad_display_hint: program_end — apply: unresolved
7. [TikTok — Data Scientist Intern (VOD Data) - 2027 Summer](https://jobright.ai/jobs/info/6a72f51b6ffeee418e5b7eac) — core / data_ml — grad_display_hint: program_end — apply: unresolved
8. [TikTok — Recommendation Architecture AI/ML Infrastructure Engineer Intern (Data-Arch-TikTok Live) - 2027 Summer](https://jobright.ai/jobs/info/6a75b46f7b3417772ade4eee) — core / data_ml — grad_display_hint: program_end — apply: unresolved
9. [CoreWeave — Software Engineer, Inference AI/ML](https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006) — core / data_ml — grad_display_hint: program_end — apply: https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006
10. [Axon — AI Scientist I](https://job-boards.greenhouse.io/axon/jobs/7746492003) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/axon/jobs/7746492003
11. [Qualcomm — Machine Learning Engineer - College Graduate](https://jobright.ai/jobs/info/6a0fa3f580bf0430c76357ef) — core / data_ml — grad_display_hint: program_end — apply: unresolved
12. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
13. [moss — Spring ’27 Intern – ML / Perception / Robotics](https://jobright.ai/jobs/info/6a9dc8eba7ba386c5d670593) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
14. [XTX Markets — AI Research Internship - XTY Labs](https://jobright.ai/jobs/info/6a52e8768ef95364ead90566) — core / data_ml — grad_display_hint: program_end — apply: unresolved
15. [SpaceX — ML Engineer, Surrogate Modeling (Vehicle Engineering)](https://boards.greenhouse.io/spacex/jobs/8559035002?gh_jid=8559035002) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/spacex/jobs/8559035002?gh_jid=8559035002

Remaining KEEP rows: 39 (Clera agency US-site rows, additional 2027 TikTok interns, SpaceX Starlink, and broad-lane new-grad). See `generated/discovery_triage_2026-09-06T22.csv`.

## Short SKIP themes

- Fully remote: 14 rows (`remote`).
- Non-US work location: 40 rows (`non_us_location`).
- Explicit 2026 job cycles: 11 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 10 rows (PhD-only / poly / undergrad-only window).
- Clearly non-target roles: 8 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 13 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 131 kept before merge).
- Newgrad healthcare: 0 rows (expected empty clinical board).
- Intern healthcare: 2 rows (Neuralink Neuroengineer Intern Fremont / South San Francisco) — skipped `non_target_role`.
- Newgrad `data_analysis`: Helping Hand / Torentify remote analyst listings — `remote` skip; not a scrape failure.
- Intern `ml_ai`: 20 rows (populated; not the empty-board flake).
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1817 seen, 90 kept (Clera agency 67). `g2_candidate` is a form fact, not a triage decision.
- Zero URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`).
- 150 URLs also appeared on the 2026-09-06T13 triage with identical board fields, so those decisions were reused. 3 more URLs reused from 2026-09-05T22. 70 URLs are new this evening.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Jobright Clera KEEP rows left unresolved. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- IMC Greenhouse `imc` has two exact `Graduate Software Engineer` reqs (Chicago `4818790101` / Aarhus `4917773101`). Matches card location is blank — left unresolved.
- SpaceX Greenhouse has multiple `Software Engineer (Starlink)` reqs (Redmond `8525359002` / `8584271002` / `8569790002` and Hawthorne `8706510002`). All four Jobright cards left unresolved.
- Ashby slug `moss` is a different European company, not the SF robotics intern. Left unresolved.
- Added verified boards this run: CoreWeave → greenhouse `coreweave` (Inference AI/ML `4609928006`); Inversion → greenhouse `inversionspace` (slug guess `inversion` 404s; Autonomy Engineer I Arc Vehicle `4705511005`); Pipe17 → greenhouse `pipe17` (Junior Software Engineer Seattle `4717950005`).
- Previous-morning KEEP that did not reappear on this evening's boards (not a scrape failure): Neuralink infra intern, Rippling Winter 2027 ML intern, several TikTok 2027 ML/research interns, WHOOP Software Engineer I (Backend), Giga SWE I/II, CyberProof / UST HealthProof Data CoE twins (new URLs for some of those titles appeared and were marked later).
