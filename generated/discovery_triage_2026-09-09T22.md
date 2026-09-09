# Discovery triage — 2026-09-09T22

- Input rows: 206
- KEEP: 25
- LATER: 104
- SKIP: 77
- Evidence basis: board fields on all 206 rows.
- KEEP with resolved apply_url: 18
- KEEP still on Jobright only: 7

## KEEP (top 15 by fit; see CSV for the rest)

1. [Formlabs — AI Software Intern (Winter/Spring 2027)](https://careers.formlabs.com/job/8174874/apply/?gh_jid=8174874) — core / data_ml — grad_display_hint: dual_date — apply: https://careers.formlabs.com/job/8174874/apply/?gh_jid=8174874
2. [TikTok — Machine Learning Engineer Intern (TikTok-Data-Search-Basic Ranking) - 2027 Summer](https://jobright.ai/jobs/info/6a70072cf5953013637f7042) — core / data_ml — grad_display_hint: program_end — apply: unresolved
3. [TikTok — Data Science Intern (TikTok LIVE) - 2027 Summer](https://jobright.ai/jobs/info/6a71a40d02d93145bf890236) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [The Nuclear Company — Spring 2027 Data Science Intern](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383218008) — core / data_ml — grad_display_hint: dual_date — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383218008
5. [The Nuclear Company — Summer 2027 Data Science Intern](https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383244008) — core / data_ml — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/thenuclearcompany/jobs/5383244008
6. [CACI International Inc — Software Engineering Intern – Summer 2027](https://jobright.ai/jobs/info/6aa1770a500b01124c77cc6f) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
7. [Zipline — Enterprise Systems Software Engineer Intern (Spring 2027)](https://jobright.ai/jobs/info/6a84a90d2f4f0014cae22047) — core / cloud_swe — grad_display_hint: dual_date — apply: unresolved
8. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/2d24aa21-569f-4d72-8fd4-fbffcc7effd8/application
9. [Clera — Forward Deployed Engineer](https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/53d8d4e8-9bf7-4c9b-8120-c3f89b9050ab/application
10. [Clera — Founding Engineer - ML Research](https://jobs.ashbyhq.com/clera/c2df35aa-7b7f-4193-a1fa-352d1a66ce57/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/c2df35aa-7b7f-4193-a1fa-352d1a66ce57/application
11. [Clera — ML Infrastructure Engineer](https://jobs.ashbyhq.com/clera/cd0ca0f3-727b-43da-a2b8-a51dc13d7269/application) — core / data_ml — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/clera/cd0ca0f3-727b-43da-a2b8-a51dc13d7269
12. [Oscar Health — Data Scientist I](https://job-boards.greenhouse.io/oscar/jobs/7592274) — core / health_ai — grad_display_hint: program_end — apply: https://job-boards.greenhouse.io/oscar/jobs/7592274
13. [IBM — Data Scientist & AI ELH - RTP 2027](https://jobright.ai/jobs/info/6aa0599e500b01124c778721) — core / data_ml — grad_display_hint: program_end — apply: unresolved
14. [Anyscale — Software Engineer (Ray Core)](https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/anyscale/81809616-ef2f-44f8-bcee-d1e17749f45d/application
15. [OpenAI — Software Engineer, Host Assurance](https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1/application) — core / cloud_swe — grad_display_hint: program_end — apply: https://jobs.ashbyhq.com/openai/0b9e565a-ae5f-40fc-8350-b59f71f76df1

Remaining KEEP rows: 10 (Clera Founding AI / Agentic / AI-ML / Machine Learning / Full Stack / SWE AI & Data Systems; OpenAI Physical Design FDE; Perplexity infra MTS; Booz Allen DS Washington DC and Fort Meade — apply unresolved). See `generated/discovery_triage_2026-09-09T22.csv`.

## Short SKIP themes

- Fully remote: 20 rows (`remote`).
- Non-US work location: 34 rows (`non_us_location`).
- Explicit 2026 job cycles: 10 rows (`start_date_conflict` / `timing_expired`: Amazon 2026 Applied Science / Fall intern family, Amazon SDE 2026, ByteDance 2026 ML intern, Medpace Clinical Data Spring 2026, Merck 2026 Future Talent co-op).
- Explicit incompatible hard gates: 9 rows (Boeing PhD intern; ByteDance / TikTok / Toyota PhD intern; Mayo Bioinformatics Intern PhD in progress; Amazon postdoc; Truveta ML postdoc; Google Data Analytics Apprenticeship excludes current Bachelor's/Master's/PhD). Exclusive graduation/enrollment windows that are not PhD-only or polygraph stay notes, not skips (Navy Federal "December 2027 or later" → later).
- Clearly non-target roles: 4 rows (`non_target_role`: Holy Family Quality And Data Manager; Amazon IT Support Engineer I; Amazon Security and Loss Prevention Specialist; Welo Dutch speech/voice analyst). Welo English Maps Trainer cards were skipped on `remote` first.

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 10 filtered). Not personalized Matches.
- All 10 Jobright boards returned (boards_ok=10, 137 kept before merge). newgrad_swe 19; intern_swe 20; intern_ml_ai 20; intern_healthcare 7; newgrad_healthcare 0 (expected ~0). Intern healthcare volume above the usual ~0 after DOMAIN/STRONG is board content, not a scrape failure (BCBS reimbursement later; Boston Children’s clinical informatics later; Boston Scientific R&D later; Mayo PhD skip; Stryker R&D later; Medpace 2026 skip; Merck 2026 skip).
- Newgrad `data_analysis`: 6 remote A Helping Hand Renovation LLC Data Analyst cards plus other remote junior-analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1809 seen, 68 kept (Clera agency 49). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Anyscale Software Engineer (Ray Core) already applied under a different Ashby id (`73a973b1`); Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- 93 URLs overlapped a prior triage with identical company/role/work_model/location (86 from 2026-09-09T13; also 2026-09-08T22 Formlabs keep, 2026-09-04 TikTok LIVE DS keep, plus older skip/later). Those decisions were reused after hard-rule checks. Hard remote / non-US / 2026 / PhD / non-target skips were applied first. Two UST HealthProof Junior Full Stack fingerprint-keeps from 2026-09-07T22 were demoted to later to match the newer 2026-09-08T22 later on the same title.
- Title-guess resolve attached Anyscale Bengaluru `Software Engineer, Ray Core` (`8b29c5e5`) instead of SF `Software Engineer (Ray Core)` (`81809616`). Restored ashby_sweep applyUrl.
- Clera agency: restored sweep applyUrls on ashby_sweep KEEP rows (resolver collapsed the second SF FDE onto `2d24aa21`, Founding AI onto already-applied `3dc0a0f6`, Founding Full Stack onto `9cd39527`). Do not add Clera to `careers_boards.yaml`.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade).
- CACI / TikTok / Zipline / IBM KEEP rows have no verified unique careers-board match — left unresolved (wrong link worse than none).
- Oscar Health Greenhouse `oscar` Data Scientist I remains unique `7592274` (normalized off the hioscar career-page gh_jid).
- Nuclear Company Greenhouse `thenuclearcompany` Spring DS intern `5383218008` / Summer `5383244008` (not the AI Applied Research ids).
- Formlabs Greenhouse `formlabs` AI Software Intern Winter/Spring 2027 remains unique `8174874`.
- No new `careers_boards.yaml` entries this evening.
- OpenAI FDE London / Madrid and Clera non-US FDE — `non_us_location` (hard skip wins over `fde`).
- OpenAI Physical Design Engineer, Forward Deployed Engineering (SF) kept on `fde`; physical-design flavor is a note. Do not invent FDE experience.
- Perplexity MTS Infrastructure form still has `external_artifact` — nonstandard hold; do not Submit.
- Morning KEEP that did not reappear (board rotation, not a scrape failure): Advanced Space 2027 ML intern; Allen Control CV/ML and SWE intern 2027; Gallup DS intern; IBM Data Science and AI Intern RTP 2027 / Agent Engineer intern+FT / Associate DS 2027; IMC ML Research intern Chicago; Meijer DS intern 2027; MISO 2027 DS intern; Notion Winter 2027 DS intern and Early Career AI; Plexus Fall 2027 SWE intern; Home Depot 2027 DS intern; Workato AI intern; Kustomer Early Career Full Stack; Lila ML I/II; Mayo Associate AI/ML; Clera Founding Engineer Intern and Robotics Research.
