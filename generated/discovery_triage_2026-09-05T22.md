# Discovery triage — 2026-09-05T22

- Input rows: 234
- KEEP: 51
- LATER: 91
- SKIP: 92
- Evidence basis: board fields only; no posting URLs opened
- KEEP with resolved apply_url: 22
- KEEP still on Jobright only: 29

## KEEP (top 15 by fit; see CSV for the rest)

1. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
2. [Axon — AI Scientist I](https://job-boards.greenhouse.io/axon/jobs/7746492003) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/axon/jobs/7746492003
3. [Fab2 — Infrastructure Software Engineering Intern - Summer](https://jobs.ashbyhq.com/fab2/53f3fe23-9d2d-4eef-bd28-968d011f86c7) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/fab2/53f3fe23-9d2d-4eef-bd28-968d011f86c7
4. [Neuralink — Machine Learning Engineer Intern](https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003
5. [OpenAI — Software Engineer, Host Assurance](https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1
6. [Perplexity — Member of Technical Staff (Software Engineer, Infrastructure)](https://jobs.ashbyhq.com/perplexity/76c9b39f-aecc-4247-b5f5-ebcd02dff7c3) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/perplexity/76c9b39f-aecc-4247-b5f5-ebcd02dff7c3
7. [Quantifind — Associate Data Scientist](https://www.quantifind.com/open-positions/?gh_jid=7589899) — core / data_ml — grad_display_hint: program_end — apply: https://www.quantifind.com/open-positions/?gh_jid=7589899
8. [Schonfeld — 2027 Data Science Intern](https://job-boards.greenhouse.io/schonfeld/jobs/8171692) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/schonfeld/jobs/8171692
9. [SpaceX — Data Scientist (Starlink)](https://boards.greenhouse.io/spacex/jobs/8783265002?gh_jid=8783265002) — core / data_ml — grad_display_hint: program_end — apply: https://boards.greenhouse.io/spacex/jobs/8783265002?gh_jid=8783265002
10. [The Nuclear Company — Spring 2027 AI Applied Research Internship](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5391888008) — core / data_ml — grad_display_hint: dual_date — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5391888008
11. [The Nuclear Company — Summer 2027 AI Applied Research Internship](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5391923008) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5391923008
12. [Booz Allen Hamilton — AI Engineer, Junior](https://bah.wd1.myworkdayjobs.com/BAH_Jobs/job/San-Antonio-TX/AI-Engineer--Junior_R0247417) — broad / data_ml — grad_display_hint: program_end — apply: https://bah.wd1.myworkdayjobs.com/BAH_Jobs/job/San-Antonio-TX/AI-Engineer--Junior_R0247417
13. [Citadel — Sector Data Scientist – 2027 Intern (US)](https://jobright.ai/jobs/info/6a7a308fbb6ca93ae561a556) — core / data_ml — grad_display_hint: program_end — unresolved
14. [Rippling — Machine Learning Software Engineer Intern - Winter 2027](https://jobright.ai/jobs/info/6a55f31cf7517b519ad5221c) — core / data_ml — grad_display_hint: program_end — unresolved
15. [IBM — Intern Data Scientist 2027 – AI & Data Analytics](https://jobright.ai/jobs/info/6a9c33aca7ba386c5d66e143) — core / data_ml — grad_display_hint: program_end — unresolved

Remaining KEEP rows: 36 (Clera agency US-site rows, additional 2027 interns, and broad-lane new-grad). See `generated/discovery_triage_2026-09-05T22.csv`.

## Short SKIP themes

- Fully remote: 23 rows (`remote`).
- Non-US work location: 47 rows (`non_us_location`).
- Explicit 2026 job cycles: 7 rows (`start_date_conflict` / `timing_expired`).
- Explicit incompatible hard gates: 5 rows (PhD-only / clearance / poly).
- Clearly non-target roles: 10 rows (`non_target_role`).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 12 filtered). Not personalized Matches.
- All 10 Jobright boards returned rows (boards_ok=10, 137 kept before merge).
- Newgrad healthcare: 1 row (Freudenberg Medical Product Development Engineer I) — skipped `non_target_role`.
- Intern healthcare: 3 rows (Medpace Fall 2026 clinical data / Neuralink biomedical / Oak Ridge medical-evac) — triaged on board text.
- Newgrad `data_analysis`: includes 9 remote A Full Renovation `Data Analyst` twins — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1851 seen, 97 kept (Clera agency 74). `g2_candidate` is a form fact, not a triage decision.
- Zero URL overlap with `data/applications.csv`.
- 135 URLs also appeared on the 2026-09-05T13 triage; board fields were identical so those decisions were reused. 99 URLs are new this evening.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows. Jobright Clera KEEP rows left unresolved. Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved. Junior AI Engineer San Antonio title is unique.
- Neuralink Greenhouse has one ML intern req (`6594261003`, South San Francisco). Fremont Jobright card left unresolved.
- Added verified boards this run: Axon (Greenhouse `axon`), The Nuclear Company (Greenhouse `thenuclearcompany`; slug guess `nuclear` 404s), Fab2 (Ashby `fab2`).
