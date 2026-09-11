# Narrative and strategy. `ml_ai_v1`

## Internal thesis

ML engineer who trains, compares, and evaluates models. A split that can fail. An ablation. An external score.

Do not print that sentence on the resume.

## Section order

One section. Machine Learning Projects. speciesOT, TextVQA, pneumonia.

`knowledge/resume_philosophy.yaml` lists Machine Learning Projects then Research Experience. Candidate A used that split and buried speciesOT under two course headings. The graft puts the lab comparison first in one ML section so a 15-second scan sees the identity.

## Recruiter-facing rules

Provenance limits stay in `interview_defense.md`.

Do not tell the hub or 43 GB story. That page is `ai_infra_v1`.

Prefer raw accuracies. Do not write nearly 3x.

## Per project

### cellot_wyss

Role. Lead ML story. Named comparison and a held-out split.

Unique signal. ICNN-OT vs scGen. $R^2$ drop when the source species is held out. Gene-space ranking flips.

Page space. Shared autoencoder. 0.85--0.90 vs 0.65--0.67. 6619 orthologs vs 1000 HVGs.

Deliberately omitted. Hub CLI. SLURM chains that never auto-submit. 43 GB atlas I/O. Decoded-space ranking as the headline. Drug-effect composition. 180+ models. Tabula atlas OOD. DatasetHandle and FrozenAE. Those limits stay in defense notes.

Allowed verbs. Graduate Researcher. Compared.

Likely follow-ups. Tabula-OOD question. Answer is LPS / rat-in-train prior. See `interview_defense.md`.

### vlm_textvqa_lora

Role. Trained PEFT and a prompt ablation.

Unique signal. Zero-shot vs prompt vs LoRA with raw accuracies.

Page space. 0.078 / 0.106 / 0.213. Rank ablation over 4, 8, 16. One A100.

Deliberately omitted. 2.62M params. 0.07 percent. Nearly 3x. +36 percent relative.

Allowed verbs. Sole author. Fine-tuned. Ablated.

Label. Harvard AI in Medicine. Course project.

### cv_pneumonia

Role. Generalization debug against an external leaderboard.

Unique signal. 14-point val-to-leaderboard gap. Freeze vs full fine-tune beat architecture choice. Domain-aware augmentation.

Page space. 0.959 public score. 85 percent to about 96 percent. DenseNet-121 95.6 percent. ResNet-50 93.8 percent. No vertical flips. 15-degree rotation cap.

Deliberately omitted. Full architecture table (ConvNeXt, EfficientNet, ensemble). Dropout 0.3 and Mixup alpha 0.2 stack as a laundry list.

Allowed verbs. Sole author. Reached. Diagnosing. Lifted.

Label. Harvard BST-261 Kaggle competition.

## Skills line

PyTorch. LoRA / PEFT. BLIP-2. DenseNet-121. scanpy. AnnData. Hugging Face. Held-out evaluation. Kaggle leaderboard.

Drop. Job Search OS tools. Flask. React. Kubernetes. Cluster-ops vocabulary.

## Catalog

Bank sentences only. Do not upgrade course projects into internships.
