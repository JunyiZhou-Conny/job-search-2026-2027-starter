# Evidence selection. `swe_v1`

Selector of record. This file. Not `scripts/rqe/plan.py` `fallback_order`.

Philosophy. `.cursor/skills/swe-philosophy/SKILL.md`.
Bank. `knowledge/evidence_bank.yaml`.

Internal slate under test. Job Search OS, Compleg, mixhvg-py.

`max_projects: 4` is a ceiling, not a quota.

## Projects considered

| id | title | interview_depth | resume_eligible |
|---|---|---|---|
| job_search_os | Job Search OS. Human-supervised browser automation | strong | true |
| compleg_uk_nz | Computational Legislative Studies | strong | true historically |
| mixhvg_py | mixhvg-py | strong | true |
| autoresearch_cellot | Closed-Loop Cluster Autoresearch | strong | true |
| alphafold_pipeline | AlphaFold protein-nucleic acid pipeline | moderate | implicit |
| airway_chatbot | Airway Management Simulation Chatbot | strong | true |
| cellot_wyss | speciesOT | strong | true |
| sseg_rlvr | S-Seg-RLVR | weak | method-only |
| transformer_reimpl | Transformer reimplementation | strong | course |
| vlm_textvqa_lora | TextVQA LoRA | strong | course |
| cv_* | course CV | strong | course |

## Strongest family signals per project

- `job_search_os`. Software ownership. Policy compile. Submit gates. Tests that refuse leaked secrets. Recovery. `target_role_relevance.swe` names policy engines, tests, compilers, ledger integrity.
- `compleg_uk_nz`. ETL. Relational schema. Cloudflare 403 recovery. AWS EC2 and S3. Measured table counts from committed CSVs. Earliest cluster batch work in the bank.
- `mixhvg_py`. AnnData API. Rank ensemble. pytest harness. Pinned upstream defects. `target_role_relevance.swe` names cross-language port, API design, pinned defects, test suite.
- `autoresearch_cellot`. Automation and checkpoint or resume. Strong SWE-adjacent signals. Overlaps `ai_infra_v1` as the lead experiment loop.
- `alphafold_pipeline`. HPC inference CLI. `interview_depth: moderate`. Thinner than Compleg on interfaces and recovery.
- `airway_chatbot`. Full-stack deploy. Clinical product. `swe.de_emphasize` includes `clinical`.
- `cellot_wyss`. CLI and spec system. Science-first on this family. Philosophy says speciesOT may appear only if it pays an interface or correctness signal, not biology.
- `sseg_rlvr`. Capstone stubs. `interview_depth: weak`.
- Course ML projects. Model bakeoffs. No software-ownership story.

## Redundant signals

- Job Search OS and AutoResearch both pay automation with a gate. Keep one. AutoResearch already leads `ai_infra_v1`.
- mixhvg-py and speciesOT share HVG and single-cell biology. On SWE, mixhvg pays API and tests. speciesOT would repeat biology without adding a new SWE job.
- Airway and Job Search OS both mention agents in bank titles. Airway is a clinical product. Philosophy drops clinical.

## Evidence strength

- Job Search OS architecture and gates are `VERIFIED_IMPLEMENTED`. Live test counts and applied-row counts are `resume_ok: false`.
- Compleg row counts are measured from committed CSVs on 2026-07-29. The bank notes the user once asked for invented numbers and was declined.
- mixhvg-py Spearman 1.0000 and Jaccard 0.980 are `VERIFIED_MEASURED` and `resume_ok: true`. 68 pytest tests are `USER_REPORTED` on 2026-09-10.
- AutoResearch 338 / 318 / 79.3 h is `USER_REPORTED` and `resume_ok: true`. Public CSV is header-only.

## Interview defensibility

Copied from the bank. Job Search OS, Compleg, mixhvg-py, AutoResearch are `strong`. AlphaFold is `moderate`. S-Seg-RLVR is `weak`.

## Selected

1. `job_search_os`. Pays for ownership, compile, gates, secret-refusing tests, and recovery. Recruiter-facing title stays `Human-Supervised Browser Automation System`. First bullet names job applications. Framing is software, not agent systems.
2. `mixhvg_py`. Pays for a public API and a fidelity harness. Unique on this page. Recruiter-facing title is `mixhvg-py: AnnData API and Fidelity Tests`.
3. `compleg_uk_nz`. Pays for ETL, schema, anti-bot recovery, and AWS staging. Unique on the production stack. No other family carries Compleg.

## Rejected

- `autoresearch_cellot`. Strong. Lost because it is the lead of `ai_infra_v1`. Candidate B tested it in place of mixhvg. It made SWE look like a reorder of AI Infra.
- `airway_chatbot`. Clinical product. `de_emphasize: clinical`. Full-stack deploy is real and belongs on Health AI.
- `cellot_wyss`. Strong CLI. Biology would crowd the SWE scan. mixhvg already pays the scientific-software API.
- `alphafold_pipeline`. Real HPC CLI. Thinner than Compleg. Would add a fourth heading without a new philosophy signal.
- `sseg_rlvr`. Planned training.
- Course ML projects. Wrong family.
- Splitting CellOT / scGen / speciesOT into three projects. Bank `do_not_claim` forbids it.

## Why scarce space

Three slots. Each selected project buys a philosophy signal the others do not. Job Search OS is the owned system. mixhvg is the library API. Compleg is the data pipeline with AWS and recovery.

## Fourth-project decision

Four headings were not rendered. Compleg already fills Research. Adding AutoResearch would stack two automation stories and copy AI Infra. Adding AlphaFold would add a thin HPC line. Stay at three.
