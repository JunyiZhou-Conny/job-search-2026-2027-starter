# Evidence selection. `ml_ai_v1`

Selector of record. This file. Not `scripts/rqe/plan.py` `fallback_order`.

Philosophy. `.cursor/skills/ml-ai-philosophy/SKILL.md`.
Bank. `knowledge/evidence_bank.yaml`.

Internal slate under test. speciesOT, TextVQA LoRA, pneumonia.

`max_projects: 4` is a ceiling, not a quota.

## Projects considered

| id | title | interview_depth | resume_eligible |
|---|---|---|---|
| cellot_wyss | speciesOT | strong | true |
| vlm_textvqa_lora | TextVQA LoRA | strong | true |
| cv_pneumonia | Pneumonia Detection from Chest Radiographs | strong | true |
| autoresearch_cellot | Closed-Loop Cluster Autoresearch | strong | true |
| transformer_reimpl | Transformer reimplementation | strong | true |
| cv_caltech101 | Caltech-101 classification | strong | course |
| cv_segmentation_voc | VOC segmentation | strong | course |
| mixhvg_py | mixhvg-py | strong | true |
| job_search_os | Job Search OS | strong | true |
| airway_chatbot | Airway chatbot | strong | true |
| sseg_rlvr | S-Seg-RLVR | weak | method-only |
| alphafold_pipeline | AlphaFold pipeline | moderate | implicit |

## Strongest family signals per project

- `cellot_wyss`. ICNN-OT vs scGen. Held-out-species $R^2$. Gene-space flip. `target_role_relevance.ml` names those signals. This is the lab comparison, not the hub story.
- `vlm_textvqa_lora`. Zero-shot 0.078, OCR prompt 0.106, LoRA r=8 0.213. Rank ablation. PEFT. Bank notes this is absent from every prior resume.
- `cv_pneumonia`. External Kaggle leaderboard 0.959. Diagnosed 14-point generalization gap. Freeze vs full fine-tune mattered more than architecture. Domain-aware augmentation.
- `autoresearch_cellot`. Experiment loop around the same models. Infrastructure, not a training result. Overlaps `ai_infra_v1`.
- `transformer_reimpl`. 9.38 BLEU. Foundations. Thinner than TextVQA on ablations and PEFT.
- `cv_caltech101` / `cv_segmentation_voc`. Real bakeoffs. Weaker generalization story than pneumonia's external leaderboard.
- `mixhvg_py`. Validation methodology. Secondary ML signal. Biology overlap with speciesOT.
- `job_search_os`. Agent ops. Philosophy says off this page.
- `airway_chatbot`. Clinical product packaging. Health AI.
- `sseg_rlvr`. Untrained GRPO. Not a results line.
- `alphafold_pipeline`. Inference, not training or comparison.

## Redundant signals

- speciesOT and AutoResearch share Cannon, SLURM, and the scGen vs CellOT question. AutoResearch pays the loop. speciesOT pays the comparison and the split. This family needs the comparison.
- pneumonia and Caltech both compare architectures. pneumonia has an external leaderboard and a diagnosed generalization failure. Keep pneumonia.
- mixhvg and speciesOT both speak HVG. speciesOT already carries the gene-space flip.

## Evidence strength

- speciesOT A-D $R^2$ ranges are `VERIFIED_MEASURED` and `resume_ok: true` as a paired held-out-species evaluation, not Tabula atlas OOD. 180+ models are `resume_ok: false`.
- TextVQA numbers are transcribed from the repo. Course project. Must stay labeled as Harvard AI in Medicine.
- pneumonia numbers are transcribed from `reflection.md`. Course Kaggle. External public score is the honest headline.
- AutoResearch job counts are `USER_REPORTED` and `resume_ok: true`.

## Interview defensibility

speciesOT, TextVQA, pneumonia, AutoResearch, transformer, Caltech, VOC are `strong`. AlphaFold is `moderate`. S-Seg-RLVR is `weak`.

## Selected

1. `cellot_wyss`. Pays for a named model comparison and a split that can fail. Framing is OT vs scGen and the gene-space flip. Not hub CLI. Not 43 GB I/O.
2. `vlm_textvqa_lora`. Pays for training, PEFT, and a prompt ablation with raw accuracies. Prefer 0.078 / 0.106 / 0.213 over "nearly 3x".
3. `cv_pneumonia`. Pays for generalization debugging against an external leaderboard. Unique on the production stack.

## Rejected

- `autoresearch_cellot`. Strong. Candidate B used it instead of pneumonia. It retells the AI Infra loop and drops the only external-leaderboard generalization story.
- `job_search_os`. Wrong family.
- `airway_chatbot`. Clinical product.
- `mixhvg_py`. Strong fidelity work. speciesOT already spends the HVG slot.
- `transformer_reimpl`. Real BLEU. Loses to TextVQA on PEFT and prompt comparison.
- `cv_caltech101`, `cv_segmentation_voc`. Real course bakeoffs. pneumonia is the stronger generalization page.
- `sseg_rlvr`. No trained results.
- `alphafold_pipeline`. Inference only.

## Why scarce space

Three slots. speciesOT is the lab comparison. TextVQA is trained PEFT. pneumonia is the generalization debug. That is ML, not AI Infra with the word ML in the title.

## Fourth-project decision

Adding AutoResearch would copy `ai_infra_v1`. Adding mixhvg would repeat HVG. Stay at three.
