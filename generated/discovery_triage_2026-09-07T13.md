# Discovery triage — 2026-09-07T13

- Input rows: 230
- KEEP: 39
- LATER: 117
- SKIP: 74
- Evidence basis: board fields only; no posting URLs opened
- KEEP with resolved apply_url: 17
- KEEP still on Jobright only: 22

## KEEP (top 15 by fit; see CSV for the rest)

1. [Notion — Software Engineer, Early Career (AI)](https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28
2. [IBM — AI Foundations - Research Scientist - Research Internship - 2027](https://jobright.ai/jobs/info/6a9e22382c964816f65ebc96) — core / data_ml — grad_display_hint: program_end — apply: unresolved
3. [NXP Semiconductors — Embedded Machine Learning & Radar Processing Intern - Summer 2027](https://jobright.ai/jobs/info/6a9e670668f82b4036739e40) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [IBM — Software Engineer / Agent Engineer - EDA - Austin](https://jobright.ai/jobs/info/6a9e29b6a7ba386c5d670e64) — core / data_ml — grad_display_hint: program_end — apply: unresolved
5. [IBM — Software Engineer / Agent Engineer - EDA - Poughkeepsie](https://jobright.ai/jobs/info/6a9e29c368f82b4036738c54) — core / data_ml — grad_display_hint: program_end — apply: unresolved
6. [IBM — Data Scientist & AI ELH - RTP 2027](https://jobright.ai/jobs/info/6a9e28bbdacf777321a90a57) — core / data_ml — grad_display_hint: program_end — apply: unresolved
7. [IBM — Associate Data Scientist 2027 - AI & Data Analytics](https://jobright.ai/jobs/info/6a9e23d7a7ba386c5d670e00) — core / data_ml — grad_display_hint: program_end — apply: unresolved
8. [IBM — Data Science and AI Intern - RTP 2027](https://jobright.ai/jobs/info/6a9e282e27c94c3d5a1cb5cf) — core / data_ml — grad_display_hint: program_end — apply: unresolved
9. [Neuralink — Machine Learning Engineer Intern](https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003
10. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
11. [CoreWeave — Software Engineer, Inference AI/ML](https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006) — core / data_ml — grad_display_hint: program_end — apply: https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006
12. [SpaceX — ML Engineer, Surrogate Modeling (Vehicle Engineering)](https://boards.greenhouse.io/spacex/jobs/8559035002?gh_jid=8559035002) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/spacex/jobs/8559035002?gh_jid=8559035002
13. [Qualcomm — Machine Learning Engineer - College Graduate](https://jobright.ai/jobs/info/6a0fa3f580bf0430c76357ef) — core / data_ml — grad_display_hint: program_end — apply: unresolved
14. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
15. [IBM — Intern Data Scientist 2027 – AI & Data Analytics](https://jobright.ai/jobs/info/6a9e2d5068f82b4036738c96) — core / data_ml — grad_display_hint: program_end — apply: unresolved

Remaining KEEP rows: 24 (second Clera FDE, other US-site Clera agency rows, additional 2027 IBM DS interns, Neuralink Fremont ML intern unresolved, Citadel / Fanatics / Booz Allen / CACI / SPA DS, Medpace junior SWE, Perplexity infra MTS, OpenAI Host Assurance). See `generated/discovery_triage_2026-09-07T13.csv`.

## Short SKIP themes

- Fully remote: 14 rows (`remote`).
- Non-US work location: 40 rows (`non_us_location`).
- Explicit 2026 job cycles: 6 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 15 rows (PhD-only / remaining-term / grad-window / Fall 2027 enrollment).
- Clearly non-target roles: 5 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 11 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 140 kept before merge).
- Newgrad healthcare: 0 rows (expected empty clinical board).
- Intern healthcare: 0 rows (expected empty clinical board).
- Newgrad `data_analysis`: Helping Hand / Full Renovation remote analyst listings — `remote` skip; not a scrape failure.
- Intern `ml_ai`: 22 rows (populated; not the empty-board flake).
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1815 seen, 89 kept (Clera agency 65). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`); Neuralink Machine Learning Engineer Intern already saved under Greenhouse `6594261003` (this run’s South San Francisco KEEP resolves to that same req).
- 123 URLs also appeared on a prior triage with identical company/role/work_model/location (115 from 2026-09-06T22, 5 from 2026-09-06T13, 3 from 2026-09-05T22), so those decisions were reused. 107 URLs are new this morning.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Neuralink Greenhouse `Machine Learning Engineer Intern` `6594261003` is South San Francisco only. Fremont Jobright card left unresolved (location twin). Two South San Francisco Jobright cards share that req.
- IBM / NXP / TikTok / Citadel / Fanatics / Medpace / Qualcomm / CACI / SPA KEEP rows have no verified careers-board match — left unresolved (wrong link worse than none).
- Huawei Canada intern listed `Markham, CA, United States` is Canada — `non_us_location`.
- American Express 2027 Masters AI Engineer intern: board text requires graduation December 2027–June 2028 — `hard_gate`.
- ID.me Summer 2027 SDE intern: graduating 2028 or beyond — `hard_gate`.
- Microsoft CoreAI university intern: remaining-semester-after-internship gate — `hard_gate`.
- Xcel Energy intern cards that require current-student status as of Fall 2027 — `hard_gate`.
- Previous-evening KEEP that did not reappear (not a scrape failure): IMC Graduate SWE, Citadel 2027 intern, Naval Nuclear / PepsiCo / Schonfeld / Disney / moss / XTX 2027 DS/ML interns, several TikTok 2027 SWE/ML interns, Axon AI Scientist I, Inversion / Pipe17 juniors, SpaceX Starlink SWE/DS, DE Shaw Software Developer.
