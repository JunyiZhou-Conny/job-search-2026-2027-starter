# Evidence selection. `health_ai_v1`

Selector of record. This file. Not `scripts/rqe/plan.py` `fallback_order`.

Philosophy. `.cursor/skills/health-ai-philosophy/SKILL.md`.
Bank. `knowledge/evidence_bank.yaml`.

Internal slate under test. Airway, speciesOT, mixhvg-py.

`max_projects: 4` is a ceiling, not a quota.

## Projects considered

| id | title | interview_depth | resume_eligible |
|---|---|---|---|
| airway_chatbot | Airway Management Simulation Chatbot | strong | true |
| cellot_wyss | speciesOT | strong | true |
| mixhvg_py | mixhvg-py | strong | true |
| cv_pneumonia | Pneumonia Detection from Chest Radiographs | strong | true |
| sseg_rlvr | S-Seg-RLVR | weak | method-only |
| alphafold_pipeline | AlphaFold pipeline | moderate | implicit |
| autoresearch_cellot | Closed-Loop Cluster Autoresearch | strong | true |
| job_search_os | Job Search OS | strong | true |
| vlm_textvqa_lora | TextVQA LoRA | strong | course |
| transformer_reimpl | Transformer reimplementation | strong | course |

## Strongest family signals per project

- `airway_chatbot`. Real clinical system. Flask, React, Auth0, MongoDB, AWS. HIPAA-conscious. Clinician feedback. `target_role_relevance` is implicit in the clinical product. This is the only healthcare product in the bank.
- `cellot_wyss`. Cross-species single-cell translation. OT. Atlas-scale scRNA-seq. `target_role_relevance.health_ai` names those signals.
- `mixhvg_py`. HVG selection. AnnData. scran and Seurat ecosystem. `target_role_relevance.health_ai` names those signals. Zhao et al. own the method.
- `cv_pneumonia`. Medical imaging. External leaderboard. Course Kaggle, not a clinical deployment.
- `sseg_rlvr`. Named Health Data Science capstone. Method and repo only. `not_yet_built` includes GRPO, datasets, Dice. `interview_depth: weak`.
- `alphafold_pipeline`. Protein structure inference. Thin bank record.
- `autoresearch_cellot`. Cluster loop around the same biology. Philosophy says do not lead Health AI with cluster ops.
- `job_search_os`. Wrong domain. Bank `health_ai` says do not lead with this.

## Redundant signals

- speciesOT and mixhvg share HVG and single-cell biology. They stay together because they argue different jobs. speciesOT is translational comparison. mixhvg is the scientific-software method port.
- speciesOT and AutoResearch share the scGen vs CellOT question. AutoResearch is the loop. Keep speciesOT.
- pneumonia and Airway both say healthcare. Airway is a deployed clinical trainer. pneumonia is a course radiograph classifier. Keep Airway. pneumonia already sits on `ml_ai_v1`.

## Evidence strength

- Airway deploy and stack are in `software_engineering_evidence`. Bank does not say architected or led. Dates end August 2025. Public repo last commit is 2024-12-11, so the final months are not visible publicly.
- speciesOT A-D ranges are `resume_ok: true` as a paired held-out-species evaluation. Drug-effect composition is `not_yet_built`.
- mixhvg fidelity numbers are `resume_ok: true`.
- S-Seg has no measurable results.

## Interview defensibility

Airway, speciesOT, mixhvg, pneumonia are `strong`. AlphaFold is `moderate`. S-Seg-RLVR is `weak`.

## Selected

1. `airway_chatbot`. Pays for a real clinical product. Verbs stay Built and Worked. Do not import master Architected or Led.
2. `cellot_wyss`. Pays for translational biology. Framing is mouse-to-human translation and a domain reading of the gene-space flip. Not hub CLI.
3. `mixhvg_py`. Pays for scientifically valid HVG software. Unique Health AI complement to speciesOT. Do not absorb it into speciesOT. Bank `notes` forbid that.

## Rejected

- `cv_pneumonia`. Strong medical-imaging alternate. Candidate B used it instead of mixhvg. It would duplicate `ml_ai_v1` and drop the only HVG method port.
- `sseg_rlvr`. Eligible as a method-and-repo line. Lost because `interview_depth: weak` and `not_yet_built` includes every result an interviewer would ask for. A one-line stub would spend a heading on unfinished work.
- `alphafold_pipeline`. Thin protein pipeline. Weaker than mixhvg on validation.
- `autoresearch_cellot`. Cluster-ops lead. Wrong job for this page.
- `job_search_os`. Wrong domain.
- Course VLM and transformer. No biological or clinical relevance.
- Claiming scGen, CellOT, and speciesOT as three projects. Forbidden.

## Why scarce space

Three slots. Airway is the clinical system. speciesOT is translational ML. mixhvg is biomedical research engineering. That is the Health AI argument.

## Fourth-project decision

S-Seg as a fourth heading would advertise unfinished GRPO. pneumonia as a fourth heading would crowd the page and copy ML/AI. Stay at three.
