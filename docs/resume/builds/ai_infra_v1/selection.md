# Evidence selection. `ai_infra_v1`

Selector of record. This file. Not `scripts/rqe/plan.py` `fallback_order`.

Philosophy. `.cursor/skills/ai-infra-philosophy/SKILL.md`.
Bank. `knowledge/evidence_bank.yaml`.

Internal slate under test. AutoResearch, Job Search OS, speciesOT, mixhvg-py.

`max_projects: 4` is a ceiling, not a quota.

## Projects considered

| id | title | interview_depth | resume_eligible |
|---|---|---|---|
| autoresearch_cellot | Closed-Loop Cluster Autoresearch for scGen vs CellOT | strong | true |
| job_search_os | Job Search OS. Human-supervised agentic browser automation | strong | true |
| cellot_wyss | speciesOT | strong | true |
| mixhvg_py | mixhvg-py | strong | true |
| alphafold_pipeline | AlphaFold Protein-Nucleic Acid Interaction Prediction | moderate | implicit |
| airway_chatbot | Airway Management Simulation Chatbot | (not labeled strong for infra) | true historically |
| compleg_uk_nz | Computational Legislative Studies | (etl) | true historically |
| sseg_rlvr | S-Seg-RLVR | weak | true as method-only |
| vlm_textvqa_lora | TextVQA LoRA | course / eval | true |
| transformer_reimpl | Transformer reimplementation | course | true |
| cv_* | course CV | course | true |

## Strongest family signals per project

- `autoresearch_cellot`. Closed-loop SLURM search. Validation-policy gate. Checkpointed agenda. Optional LLM planner with cost ceiling. Idempotent runner. Bank `notes` call this the strongest `ml_systems_ai_infrastructure` match. `target_role_relevance.ai_infra` names those signals.
- `job_search_os`. Human-supervised browser automation. Compiled runtime. HITL Submit gates. Durable GitHub vs Sheet vs Simplify split. `target_role_relevance.ai_infra` names those signals. This is the agent-systems project. AutoResearch is not.
- `cellot_wyss`. Hub CLI. 15 YAML specs. SLURM chains that never auto-submit. 43 GB atlas constraint. Decoded-space evaluation. `target_role_relevance.ai_infra` names hub, specs, SLURM chains, artifact-backed inference.
- `mixhvg_py`. Cross-language API. Rank ensemble. Measured fidelity vs R. Pinned upstream defects. `target_role_relevance.ai_infra` says secondary unless the posting wants scientific-software engineering.
- `alphafold_pipeline`. GPU parallel inference. HPC. CLI for non-ML users. Thin bank record. `interview_depth: moderate`.
- `airway_chatbot`. Production RAG agent and AWS. Clinical product. Philosophy `de_emphasize: clinical`.
- `compleg_uk_nz`. ETL and scrapers. Data/SWE, not infra.
- `sseg_rlvr`. Capstone stubs. `not_yet_built` includes GRPO and datasets. `interview_depth: weak`.

## Redundant signals

- AutoResearch and speciesOT both sit on FASRC Cannon and SLURM. They stay together because they argue different jobs. Search loop and policy versus no-auto-submit hub and decoded-space eval.
- mixhvg-py is an HVG dependency of speciesOT. Biology overlap is high. Its unique paid signal is a validation harness. speciesOT `testing_validation` says current main has no `tests/` directory.
- Airway and Job Search OS both mention agents. Airway is clinical product RAG. Job Search OS is HITL browser automation. Keep one. Philosophy drops clinical.

## Evidence strength

- AutoResearch 338 / 318 / 79.3 h is `USER_REPORTED` and `resume_ok: true`. Public `experiments.csv` is header-only. Architecture is `VERIFIED_IMPLEMENTED` on the public clone.
- Job Search OS architecture and gates are `VERIFIED_IMPLEMENTED`. Live test counts and applied-row counts are `resume_ok: false`.
- speciesOT hub, specs, 43 GB constraint, sidecars are `VERIFIED_*`. A-D R^2 ranges are `VERIFIED_MEASURED` and `resume_ok: true` as a rat-in-train prior, not Tabula OOD. 180+ models are `resume_ok: false`.
- mixhvg-py Spearman 1.0000 and Jaccard 0.980 are `VERIFIED_MEASURED` and `resume_ok: true`.

## Interview defensibility

Copied from the bank. AutoResearch, Job Search OS, speciesOT, mixhvg-py are `strong`. AlphaFold is `moderate`. S-Seg-RLVR is `weak`.

## Selected

1. `autoresearch_cellot`. Pays for experimentation infrastructure, reliability, and policy gates. Unique on the page.
2. `job_search_os`. Pays for agent orchestration with human gates. Recruiter-facing title is `Human-Supervised Browser Automation System`. Domain stays job applications in the first bullet. AutoResearch must not carry the agent signal.
3. `cellot_wyss`. Pays for evaluation infrastructure and a no-auto-submit experiment hub. Different job from AutoResearch despite shared cluster.

## Rejected

- `mixhvg_py`. See the fourth-project decision below. Strong evidence. Wrong use of scarce space on this page.
- `airway_chatbot`. Clinical product. `de_emphasize: clinical`. Agent signal already paid by Job Search OS.
- `alphafold_pipeline`. HPC inference is real and thinner than the three selected. Would repeat SLURM without adding eval or agent depth.
- `compleg_uk_nz`. ETL. Wrong family.
- `sseg_rlvr`. Planned training. Health-AI method line. Weak defensibility for a production infra page.
- `vlm_textvqa_lora`, `transformer_reimpl`, `cv_*`. Course or model-bakeoff. No infra ownership.
- Splitting CellOT / scGen / speciesOT into three projects. Bank `do_not_claim` forbids it.

## Why scarce space

Three slots. Each selected project buys a philosophy signal the others do not. The hypothesis slate was tested, not obeyed.

## Fourth-project decision. mixhvg-py

Rendered both layouts after the prose cleanup.

With mixhvg. Four headings. Engineering has three stacked projects. The validation-harness bullets are true and dense. They repeat single-cell / HVG biology already carried by speciesOT. The page loses whitespace and the first two engineering stories wrap harder.

Without mixhvg. Education, skills, two engineering systems, one research-infra project. Hierarchy is clearer. The three AI-infra stories are readable in 15 seconds. The page stays exactly one page with room to breathe.

Choice. Drop `mixhvg_py` from `ai_infra_v1`.

Not a quality veto. mixhvg remains `resume_eligible` and `interview_depth: strong`. It is a candidate for a later Health-AI or scientific-software page. Do not absorb it into speciesOT. Bank `notes` forbid that.

AlphaFold was the thin HPC alternate. It would add a fourth heading without paying a new philosophy signal. Not used as a replacement.
