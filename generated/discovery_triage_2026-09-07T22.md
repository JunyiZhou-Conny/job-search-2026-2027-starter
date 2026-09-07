# Discovery triage — 2026-09-07T22

- Input rows: 210
- KEEP: 44
- LATER: 106
- SKIP: 60
- Evidence basis: board fields on 208 rows; Jobright/public JD skim on 2 American Express Masters 2027 SWE intern cards (hard_gate window).
- KEEP with resolved apply_url: 17
- KEEP still on Jobright only: 27

## KEEP (top 15 by fit; see CSV for the rest)

1. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
2. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application
3. [Neuralink — Machine Learning Engineer Intern](https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003
4. [Neuralink — Machine Learning Engineer Intern](https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003
5. [NXP Semiconductors — Embedded Machine Learning & Radar Processing Intern - Summer 2027](https://jobright.ai/jobs/info/6a9e670668f82b4036739e40) — core / data_ml — grad_display_hint: program_end — apply: unresolved
6. [Neuralink — Machine Learning Engineer Intern](https://jobright.ai/jobs/info/6a038dc98ecfd93cd9c0f6f5) — core / data_ml — grad_display_hint: program_end — apply: unresolved
7. [Notion — Software Engineer, Early Career (AI)](https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/notion/85947779-6b87-466a-98bc-30a640448c28
8. [Clera — Founding Engineer - Machine Learning](https://jobs.ashbyhq.com/clera/90d61dff-38b6-4a3d-891d-e8c8029df845/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/90d61dff-38b6-4a3d-891d-e8c8029df845/application
9. [Clera — Founding Engineer Intern](https://jobs.ashbyhq.com/clera/88d809ef-3c2e-44fb-a16b-6aec14960c46/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/88d809ef-3c2e-44fb-a16b-6aec14960c46/application
10. [CoreWeave — Software Engineer, Inference AI/ML](https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006) — core / data_ml — grad_display_hint: program_end — apply: https://coreweave.com/careers/job?4609928006&board=coreweave&gh_jid=4609928006
11. [IBM — Associate Data Scientist 2027 - AI & Data Analytics](https://jobright.ai/jobs/info/6a9e23d7a7ba386c5d670e00) — core / data_ml — grad_display_hint: program_end — apply: unresolved
12. [IBM — Data Science and AI Intern - RTP 2027](https://jobright.ai/jobs/info/6a9e282e27c94c3d5a1cb5cf) — core / data_ml — grad_display_hint: program_end — apply: unresolved
13. [IBM — Data Scientist & AI ELH - RTP 2027](https://jobright.ai/jobs/info/6a9e28bbdacf777321a90a57) — core / data_ml — grad_display_hint: program_end — apply: unresolved
14. [IBM — Data Scientist Intern - Poughkeepsie, NY - 2027](https://jobright.ai/jobs/info/6a9e2848a7ba386c5d670e59) — core / data_ml — grad_display_hint: program_end — apply: unresolved
15. [IBM — Data and AI Intern 2027](https://jobright.ai/jobs/info/6a9e267c75edfa11b471067f) — core / data_ml — grad_display_hint: program_end — apply: unresolved

Remaining KEEP rows: 29 (second Clera FDE, other US-site Clera agency rows, additional 2027 IBM DS interns, Neuralink Fremont ML intern unresolved, Sage 2027 SWE interns, TikTok 2027 DE/DS interns, CyberProof / UST HealthProof junior full-stack, Booz Allen / CACI / Citadel / Fanatics / SPA DS, IBM entry-level SWE, Perplexity infra MTS, OpenAI Host Assurance). See `generated/discovery_triage_2026-09-07T22.csv`.

## Short SKIP themes

- Fully remote: 13 rows (`remote`).
- Non-US work location: 32 rows (`non_us_location`).
- Explicit 2026 job cycles: 5 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 13 rows (PhD-only / remaining-term / grad-window / Fall 2027 enrollment / Amex Masters Dec 2027–Jun 2028).
- Clearly non-target roles: 3 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 8 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 136 kept before merge).
- Newgrad healthcare: 1 row (Thermo Fisher Field Service Engineer, remote) — DOMAIN/STRONG let `engineer` through; skipped `remote` + `non_target_role`. Not a scrape failure. Intern healthcare: 0 rows (expected empty clinical board).
- Newgrad `data_analysis`: Helping Hand remote analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1781 seen, 69 kept (Clera agency 50). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`); Neuralink Machine Learning Engineer Intern already saved under Greenhouse `6594261003` (this run’s South San Francisco KEEP resolves to that same req).
- 149 URLs also appeared on a prior triage with identical company/role/work_model/location (148 from 2026-09-07T13, 1 from 2026-09-06T22), so those decisions were reused. 61 URLs are new this evening.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- Neuralink Greenhouse `Machine Learning Engineer Intern` `6594261003` is South San Francisco only. Fremont Jobright card left unresolved (location twin). Two South San Francisco Jobright cards share that req.
- IBM / NXP / TikTok / Citadel / Fanatics / Qualcomm-absent / CACI / SPA / Sage / CyberProof / UST HealthProof KEEP rows have no verified careers-board match — left unresolved (wrong link worse than none).
- American Express 2027 Masters SWE intern (Charlotte + New York): public JD requires graduation December 2027–June 2028 — `hard_gate` (same gate as this morning’s Amex Masters AI Engineer card).
- Dropbox Summer 2027 SWE intern is Remote — `remote` skip.
- Allied HOA Partners SWE/DS internship titled Fall 2026 — `start_date_conflict` / `timing_expired`.
- Previous-morning KEEP that did not reappear (not a scrape failure): IBM AI Foundations Research Internship 2027, Qualcomm ML Engineer College Graduate, Medpace Junior SWE (Booz Allen Fort Meade and CACI Bethesda DS returned under new Jobright URLs and were kept).
