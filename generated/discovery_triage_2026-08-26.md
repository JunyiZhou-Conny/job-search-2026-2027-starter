# Discovery triage — 2026-08-26

- Input rows: 122
- KEEP: 22
- LATER: 46
- SKIP: 54
- Evidence basis: board fields only; no posting URLs opened
- KEEP with resolved apply_url: 3
- KEEP still on Jobright only: 19

## KEEP

1. [Grainger — GTG Intern - Data Science Job Details | Grainger Businesses](https://jobright.ai/jobs/info/6a8bcbb625fc4e7ae3db6502) — core / data_ml — grad_display_hint: either
2. [IBM — 2027 Software Engineering Intern – Agentic AI & Workflow Automation](https://jobright.ai/jobs/info/6a8e7c83eb0ee5374a47d452) — core / data_ml — grad_display_hint: program_end
3. [ONE Gas — Summer 2027 Data Science Intern](https://jobright.ai/jobs/info/6a8604f174e02153f1459e3d) — core / data_ml — grad_display_hint: program_end
4. [Old Mission — Software Engineer – 2027 Internship Program (June Start)](https://jobright.ai/jobs/info/6a57c970a791c6211bf00ff5) — core / cloud_swe — grad_display_hint: program_end
5. [Procter & Gamble — Data Scientist (Master's Degree) Internship](https://jobright.ai/jobs/info/6a8ca1de2f736c304f2a6ece) — core / data_ml — grad_display_hint: program_end
6. [TikTok — AI Infra Engineer Intern (Recommendation & LLM) - 2027 Summer](https://jobright.ai/jobs/info/6a8e595beb0ee5374a47d0af) — core / cloud_swe — grad_display_hint: program_end
7. [Booz Allen Hamilton — Software Engineer](https://jobright.ai/jobs/info/6a7f56fc19ce4e6e9d937036) — broad / cloud_swe — grad_display_hint: program_end
8. [Booz Allen Hamilton — Software Engineer](https://jobright.ai/jobs/info/6a887e6fe8b6601d12906ff1) — broad / cloud_swe — grad_display_hint: program_end
9. [Booz Allen Hamilton — Software Engineer](https://jobright.ai/jobs/info/6a8da619581f2d7bfdfe80ee) — broad / cloud_swe — grad_display_hint: program_end
10. [Booz Allen Hamilton — Software Engineer](https://jobright.ai/jobs/info/6a8dd74d25fc4e7ae3dbe1c8) — broad / cloud_swe — grad_display_hint: program_end
11. [CVS Health — Data Science Analyst](https://jobright.ai/jobs/info/6a893ff14afae74a0834e6dd) — core / health_ai — grad_display_hint: program_end — apply: https://cvshealth.wd1.myworkdayjobs.com/CVS_Health_Careers/job/NY---New-York/Data-Analyst_R0993501-1
12. [Cognizant — AI Engineer](https://jobright.ai/jobs/info/6a8dc9aecc0cf27068525449) — core / data_ml — grad_display_hint: program_end
13. [Cognizant — AI Engineer](https://jobright.ai/jobs/info/6a4d84bf3122a76a8fd55e2c) — core / data_ml — grad_display_hint: program_end
14. [D-Wave — Software Engineer I](https://jobright.ai/jobs/info/6a8de429d34f700f87fd6aab) — core / cloud_swe — grad_display_hint: program_end
15. [Flatiron Health — Applied AI Data Scientist - Product AI Team](https://jobright.ai/jobs/info/6a55508b4119652ff3864eaf) — core / health_ai — grad_display_hint: program_end — apply: https://flatiron.com/careers/open-positions/job?gh_jid=8010590
16. [Formation Bio — Data Scientist, Portfolio Optimization](https://jobright.ai/jobs/info/6a13788f69bd827926af83ff) — core / health_ai — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/formationbio/jobs/7757667
17. [Leidos — Junior Software Engineer – AI/ML Applications](https://jobright.ai/jobs/info/6a8da715581f2d7bfdfe813b) — core / data_ml — grad_display_hint: program_end
18. [Quest Diagnostics — Data Scientist](https://jobright.ai/jobs/info/6a8cb59a1d96e6541c8c29ba) — core / health_ai — grad_display_hint: program_end
19. [Salesforce — Software Engineer, AI Applications](https://jobright.ai/jobs/info/6a8ddd1a25fc4e7ae3dbe3e1) — core / data_ml — grad_display_hint: program_end
20. [Uber — Software Engineer I](https://jobright.ai/jobs/info/6a7ccdc3dc3dff2d1c0c9280) — core / cloud_swe — grad_display_hint: program_end
21. [Uber — Software Engineer I](https://jobright.ai/jobs/info/6a83a88e1081a745e97108b3) — core / cloud_swe — grad_display_hint: program_end
22. [World Wide Technology — Data Scientist](https://jobright.ai/jobs/info/6a8ddab347679c68bf5e5238) — core / data_ml — grad_display_hint: program_end

## Short SKIP themes

- Explicit incompatible hard gates: 24 rows (PhD-only, exclusive graduation windows, UIUC-only, high-school, Top Secret).
- Fully remote: 16 rows (`remote`); sponsorship columns were not used as the reason.
- Explicit 2026 job cycles: 3 rows (`start_date_conflict` / `timing_expired`).
- Clearly non-target roles: 19 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json` in this checkout; personalized Jobright Matches were not scraped.
- Intern healthcare board: 0 rows (expected clinical-filter outcome).
- Intern `ml_ai` returned 18 rows in the 10-board session (no empty-board flake).
- Newgrad `swe` board: 17 rows (near the ~18 typical).
- Newgrad `data_analysis` board: 9 rows — still includes the travel/marketing remote-analyst cluster, not a scrape failure.
- Newgrad healthcare: 4 rows (Cambia EDI remote; NYU Langone research data associate; Omnicell field service; Terrestrial RA) — filtered in triage, not a scrape failure.
- Intern `swe` board: 14 rows, a bit below the ~18 typical; other boards were populated so this is recorded as volume, not a failed scrape.
- Several same-company/title rows have distinct Jobright URLs and were retained separately (BNY, Honeywell, Mayo, NobleReach, Hanover, Vanguard, Booz Allen, Cognizant, IDA, NORC, Uber, Welo).
- Intern-board `h1b_signal` cells are company-size values and were not treated as sponsorship truth.
- Zero URL overlap with `data/applications.csv`.
