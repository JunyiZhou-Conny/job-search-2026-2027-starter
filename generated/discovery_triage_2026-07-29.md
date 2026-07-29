# Discovery triage — 2026-07-29

- Merged unique URLs: **57**
- Decisions: **keep=19, later=25, skip=13**
- Sources: Jobright public feed 13; newgrad_swe 22; intern_swe 22
- Personalized Matches session unavailable because `jobright_storage.json` was absent; the exporter used the public feed.

## KEEP

Top 15 by fit (see CSV for all 19):

1. [Apple — Machine Learning Engineer - AI Evaluation & LLM Systems](https://jobright.ai/jobs/info/6a6a630b8693c23e7fb7a6af) — core/data_ml — program_end
2. [Tilde Research — ML Engineer (Internship and Full-time)](https://jobright.ai/jobs/info/6a5782a8f7517b519ad5aa75) — core/data_ml — either
3. [Tilde Research — Kernel Engineer (Internship and Full-time)](https://jobright.ai/jobs/info/6a55b69105c65f7c8f4c65a2) — core/data_ml — either
4. [Amazon — Network Development Engineer, ML Nework Engineering](https://jobright.ai/jobs/info/6a6a5e1a48355b3f12bf0912) — core/cloud_swe — program_end
5. [Amazon — System Development Engineer, Keya](https://jobright.ai/jobs/info/6a6a5e14c63ba56308f52cb5) — core/cloud_swe — program_end
6. [Cisco — Software Engineer Backend/Platform Systems I](https://jobright.ai/jobs/info/6a6a76d148355b3f12bf120a) — core/cloud_swe — program_end
7. [Amperesand — DevOps Engineer](https://jobright.ai/jobs/info/6a6a63a416c69119640fe0d2) — core/cloud_swe — program_end
8. [Black Kite — AI Automation Specialist](https://jobright.ai/jobs/info/6a3eddd3ce7cce40b34222c7) — core/data_ml — program_end
9. [DigiCert — Associate Backend Engineer](https://jobright.ai/jobs/info/6a6a629e19d76667a2abf50a) — core/cloud_swe — program_end
10. [SpaceX — Software Engineer, Telemetry (Starlink)](https://jobright.ai/jobs/info/6a6a2f38c63ba56308f51c76) — core/cloud_swe — program_end
11. [Booz Allen Hamilton — Data Engineer](https://jobright.ai/jobs/info/6a68957bc1787161d1444fca) — broad/data_ml — program_end
12. [Booz Allen Hamilton — Software Engineer, Junior](https://jobright.ai/jobs/info/6a6a24c00b42f866b6196f55) — core/cloud_swe — program_end
13. [Allergan Aesthetics — Associate Software Engineer I](https://jobright.ai/jobs/info/6a6a646048355b3f12bf0b66) — broad/health_ai — program_end
14. [Framatome North America — Early Career Software Engineer](https://jobright.ai/jobs/info/6a6a120816c69119640fc275) — broad/cloud_swe — program_end
15. [Tactical Engineering and Analysis — Software Developer, Entry to Junior](https://jobright.ai/jobs/info/6a6a62280b42f866b6198609) — broad/cloud_swe — program_end

## SKIP themes

- `start_date_conflict` / `timing_expired`: explicit Fall 2026 internships (3)
- `remote`: fully remote internship (1)
- `non_target_role`: product lead, talent acquisition, data-center technician, IT asset, and microscopy roles (6)
- `hard_gate`: incompatible degree/status or duration requirements (3)

## Attention

- Several internship rows omit the term; these were generally placed in `later` rather than assumed to be Summer 2027.
- Suspected duplicate posting pairs have distinct URLs: Tilde Kernel Engineer, Amazon ML Network Engineering, Black Kite AI Automation Specialist, and Metrea Cyber Engineer.
- Huawei's board location (`Markham, CA, United States`) appears anomalous and needs verification.
- `user_confirm` remains blank. Nothing was ingested into `data/applications.csv`.
