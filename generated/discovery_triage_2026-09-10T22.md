# Discovery triage — 2026-09-10T22

- Input rows: 216
- KEEP: 39
- LATER: 101
- SKIP: 76
- Evidence basis: board fields on all 216 rows.
- KEEP with resolved apply_url: 23
- KEEP still on Jobright only: 16
- Decision reuse: 107 URL-stable rows from 2026-09-10T13 / 2026-09-09; 109 new rows decided this run.

## KEEP (top 15 by fit; see CSV for the rest)

1. [IBM — Associate Data Scientist 2027 - AI & Data Analytics](https://jobright.ai/jobs/info/6a9e23d7a7ba386c5d670e00) — core / data_ml — grad_display_hint: program_end — apply: unresolved
2. [Adobe — 2027 Intern - Machine Learning Engineer](https://jobright.ai/jobs/info/6a960b44c8763a3a87ffe1bd) — core / data_ml — grad_display_hint: program_end — apply: unresolved
3. [Capital One — Current Master's, AI Engineering Internship Program - Summer 2027](https://jobright.ai/jobs/info/6aa0177cea127c3794694e3a) — core / data_ml — grad_display_hint: program_end — apply: unresolved
4. [NVIDIA — NVIDIA 2027 Internships: Autonomous Vehicles and Robotics](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Autonomous-Vehicles-and-Robotics_JR2023496) — core / data_ml — grad_display_hint: program_end — apply: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Autonomous-Vehicles-and-Robotics_JR2023496
5. [NVIDIA — NVIDIA 2027 Internships: Deep Learning](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Deep-Learning_JR2023497-1) — core / data_ml — grad_display_hint: program_end — apply: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Deep-Learning_JR2023497-1
6. [Notion — Data Science Intern (Winter 2027)](https://jobs.ashbyhq.com/notion/a67d6f2b-7c13-41d0-b36b-b2f662c9873e) — core / data_ml — grad_display_hint: dual_date — apply: https://jobs.ashbyhq.com/notion/a67d6f2b-7c13-41d0-b36b-b2f662c9873e
7. [Tesla — Internship, Machine Learning Engineer, Factory Software (Winter/Spring 2027)](https://jobright.ai/jobs/info/6aa1d337dbc0e60e37e13dce) — core / data_ml — grad_display_hint: dual_date — apply: unresolved
8. [AV — Summer 2027 Software Engineering Intern](https://jobright.ai/jobs/info/6a970054246d697dcee029ca) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
9. [Adobe — 2027 Intern - Software Engineer](https://jobright.ai/jobs/info/6a99bd37ad752e2ad55018ea) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
10. [Amazon — Software Development Engineer Intern/Co-Op, ROBOTICS - 2027](https://jobright.ai/jobs/info/6a9a2881551435518ebf3188) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
11. [Figma — Software Engineer Intern (Winter 2027)](https://boards.greenhouse.io/figma/jobs/6131089004?gh_jid=6131089004) — core / cloud_swe — grad_display_hint: program_end — apply: https://boards.greenhouse.io/figma/jobs/6131089004?gh_jid=6131089004
12. [Google — Software Engineering Intern, BS, Summer 2027](https://jobright.ai/jobs/info/6a95ac6ec8763a3a87ffb3ee) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
13. [NVIDIA — NVIDIA 2027 Internships: Software Engineering](https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Software-Engineering_JR2023495) — core / cloud_swe — grad_display_hint: program_end — apply: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/NVIDIA-2027-Internships--Software-Engineering_JR2023495
14. [Stripe — Software Engineer, Intern](https://jobright.ai/jobs/info/6a95fec94c22023a07937674) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved
15. [TikTok — Software Engineer Intern (Recommendation Architecture, Feeds Infrastructure) - 2027 Summer](https://jobright.ai/jobs/info/6a86674974e02153f145bc5a) — core / cloud_swe — grad_display_hint: program_end — apply: unresolved

Remaining KEEP rows: 24 (TikTok Software Engineer Intern (Recommendation Architecture, Feeds Infrastructure) - 2027 Summer [unresolved]; TikTok Software Engineer Intern (Recommendation Infra, Performance Efficiency) - 2027 Summer [unresolved]; Clera Forward Deployed Engineer; Clera Forward Deployed Engineer; OpenAI Physical Design Engineer, Forward Deployed Engineering; Booz Allen Hamilton AI Engineer, Junior; Booz Allen Hamilton Data Scientist, Junior [unresolved]; IBM Associate Software Engineer [unresolved]; Notion Software Engineer, Early Career; Notion Software Engineer, Early Career (AI); Booz Allen Hamilton Data Scientist [unresolved]; Booz Allen Hamilton Data Scientist [unresolved]; Clera Founding AI Engineer; Clera Founding Agentic Engineer; Clera Founding Engineer (AI/ML); Clera ML Infrastructure Engineer; Clera Research Engineer / Research Scientist, Robotics and Physical AI; Clera Software Engineer, AI & Data Systems; Perplexity Member of Technical Staff (Applied AI Engineer, Agent Capabilities); SpaceX Software Engineer, Inference (AI Data Engineering); Clera Founding Full Stack Engineer; OpenAI Software Engineer, Host Assurance; Perplexity Member of Technical Staff (General Software Engineer, Infrastructure); SpaceX Software Engineer, Telemetry (Starlink)). See `generated/discovery_triage_2026-09-10T22.csv`.

## Short SKIP themes

- Fully remote: 13 rows (`remote`).
- Non-US work location: 41 rows (`non_us_location`).
- Explicit 2026 job cycles: 2 rows (`start_date_conflict` / `timing_expired`: NVIDIA Dynamo Fall 2026 intern; TikTok Shop DS intern 2026 Start). Reused 2026 skips from the morning file stay skip.
- Explicit incompatible hard gates: 10 rows (ByteDance / NVIDIA / TikTok USDS / Meta PhD-only intern titles; Novartis postdoctoral fellows). Exclusive graduation/enrollment windows that are not PhD-only or polygraph stay notes, not skips (Amex campus 2027; Navy Federal “December 2027 or later” → later).
- Clearly non-target roles: 10 rows (`non_target_role`: Gusto Head of Sales; ServiceNow Principal PM; Sarah Cannon Data Coordinator; WTW File Analyst; SpaceXAI Human Data BizOps; USAA Audit Data Analyst; OpenAI Mechanical Engineer; Clera Talent AI Operator / Founder's Associate).

## Anomalies

- Matches unavailable: no `secrets/jobright_storage.json`; `export_jobright_discovery.py` fell back to the public homepage (20 cards → 15 filtered). Not personalized Matches.
- All 10 Jobright boards returned (boards_ok=10, 128 kept before merge). newgrad_swe 19; intern_swe 17; intern_ml_ai 18; intern_healthcare 0 (expected ~0); newgrad_healthcare 1 (Sarah Cannon Data Coordinator — `non_target_role` leak, not a scrape failure).
- Newgrad `data_analysis`: remote A Helping Hand / junior-analyst listings — `remote` skip; not a scrape failure.
- Intern-board `h1b_signal` cells can be company-size values and were not treated as sponsorship truth.
- Ashby sweep: 20 orgs, 0 failed, 1832 seen, 88 kept (Clera agency 69). `g2_candidate` is a form fact, not a triage decision.
- Zero discovery-URL overlap with `data/applications.csv`. Company+role overlap: Google SWE Intern BS Summer 2027 already on the ledger as J20260723-006 under a different Jobright URL; Clera Founding AI Engineer already applied (`3dc0a0f6`) vs this run’s SF agency card `e668f8ff`.
- Title-guess resolve attached Clera FDE NYC+SF onto Berlin `98ceb57b`, Founding AI onto already-applied `3dc0a0f6`, Founding Full Stack onto `9cd39527`. Restored sweep applyUrls. Do not add Clera to `careers_boards.yaml`.
- Stripe Greenhouse `stripe` title `Software Engineer, Intern` is location-split (London 8130867 / Singapore 8130883 / Bengaluru 8031833). Card lists SF/Seattle/NY — left unresolved. Do not add Stripe.
- Booz Allen generic FT `Data Scientist` still many Workday reqs — left unresolved (McLean `R0229815-1` vs Jobright Washington DC / Fort Meade). Junior DS San Antonio title-only attached San Diego `R0243527-1` — left unresolved. Junior AI Engineer San Antonio remains unique `R0247417`.
- SpaceX Telemetry (Starlink) is location-split (Hawthorne `8631930002` / Redmond `8656526002`). Card is Hawthorne — kept the Hawthorne URL. Inference (AI Data Engineering) Palo Alto is unique `8717350002`.
- Figma Greenhouse `figma` Winter 2027 SWE intern is unique `6131089004` (SF+NY). Added to `careers_boards.yaml`.
- NVIDIA Workday 2027 intern titles unique: AV/Robotics `JR2023496`, Deep Learning `JR2023497-1`, SWE `JR2023495` (Santa Clara).
- Notion Ashby Winter 2027 DS intern `a67d6f2b`, Early Career `297b4ece`, Early Career (AI) `85947779` (all SF unique).
- AV / Adobe / Amazon / Capital One / Google / Tesla / TikTok / IBM KEEP rows have no verified unique careers-board match — left unresolved (wrong link worse than none).
- Perplexity MTS Infrastructure and new MTS Agent Capabilities forms have `external_artifact` — nonstandard hold; do not Submit.
- OpenAI Physical Design Engineer, Forward Deployed Engineering (SF) kept on `fde`; physical-design flavor is a note. Do not invent FDE experience.
- OpenAI FDE London / Madrid and Clera non-US FDE — `non_us_location` (hard skip wins over `fde`).
- Morning KEEP that did not reappear (board rotation, not a scrape failure): Activision 2027 SWE intern; DV Trading AI intern; Delta Spring 2027 AI intern; ICD Portal Summer 2027 family; Merck 2027 Future Talent AI/ML + Modeling; S&P ML intern 2027; Shield AI SWE intern; Aerospace ML graduate intern; Verizon AI/ML intern; Anyscale Ray Core; Amazon Annapurna SDE I; Crowe ML SWE 1; IBM DS & AI ELH RTP 2027; Northrop Roy UT; Oscar Health Data Scientist I.
