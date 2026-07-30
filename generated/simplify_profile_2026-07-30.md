# Simplify profile — paste-ready long form (2026-07-30)

Source of truth: `resumes/base/JZ_resume.tex` + `knowledge/evidence_bank.yaml`.
Every item below is traceable to one of those two files. Nothing here is invented.

The one-page cluster PDF stays the human artifact. This file is the machine artifact:
the Simplify profile feeds Copilot autofill, which populates the structured candidate
profile that recruiters actually search.

---

## 1. SKILLS — paste this block

Simplify takes skills as individual tags. Paste in batches; it will tokenize on commas.

### Languages and core

```
Python, SQL, JavaScript, R, Java, C/C++, HTML/CSS, Bash, Git, Linux/Unix
```

### ML and deep learning

```
PyTorch, TensorFlow, Keras, scikit-learn, XGBoost, LightGBM, NumPy, Pandas,
Machine Learning, Deep Learning, Neural Networks, Transformers,
Hugging Face Transformers, Transfer Learning, Fine-tuning,
Parameter-Efficient Fine-Tuning (PEFT), LoRA, Model Evaluation,
Hyperparameter Tuning, Ablation Studies, Data Augmentation, Statistical Modeling
```

### LLM and applied AI

```
Large Language Models (LLM), Retrieval-Augmented Generation (RAG),
Agentic LLM Pipelines, Prompt Engineering, OpenAI API, Anthropic Claude API,
Embeddings, Vector Search, MongoDB Atlas Vector Search, Context Window Management,
LLM Evaluation, Token and Cost Accounting, Multi-turn Dialogue Systems,
BLIP-2, InstructBLIP, Vision-Language Models
```

### Computer vision

```
Computer Vision, Convolutional Neural Networks (CNN), Vision Transformers (ViT),
ResNet, DenseNet, EfficientNet, ConvNeXt, U-Net, DeepLabV3+,
Image Classification, Semantic Segmentation, Medical Imaging, Mixup
```

### Backend, frontend, and DevOps

```
Flask, REST APIs, RESTful API Development, React.js, Auth0, Docker,
Backend Development, Full-Stack Development, API Design, Authentication,
DevOps, Agile, Scrum, Code Review, Team Coordination
```

### Data and compute

```
PostgreSQL, MySQL, MongoDB, Spark, Hadoop, ETL, Data Pipelines, Web Scraping,
Selenium, Relational Schema Design, Data Analysis, Jupyter, conda,
SLURM, HPC, High-Performance Computing, GPU Computing, Multi-GPU Training,
Distributed Job Scheduling, Job Arrays, Checkpointing, Batch Processing
```

### Cloud

```
AWS, Amazon EC2, Amazon S3, AWS Elastic Beanstalk, AWS CloudFront, boto3,
Snowflake, BigQuery, Cloud Deployment
```

### Scientific and domain

```
Health Data Science, Computational Biology, Bioinformatics, scRNA-seq,
Single-Cell Genomics, scanpy, Optimal Transport, Variational Autoencoders (VAE),
Generative AI, AlphaFold, Protein Structure Prediction, Clinical AI
```

### Certifications

```
AWS Certified Cloud Practitioner, AWS Certified AI Practitioner,
AWS Certified Machine Learning Associate
```

---

## 2. SKILLS TO REMOVE from the current profile

None of these appear in `resumes/base/JZ_resume.tex` or `knowledge/evidence_bank.yaml`.

| Skill | Why remove |
|---|---|
| **Kubernetes** | Bank records `verified: false, level: none`. You confirmed 2026-07-26 that the airway chatbot uses Elastic Beanstalk + Docker, not Kubernetes. Removed from the resume for this reason. |
| **Go** | No project, coursework, or bank entry. |
| **Redis** | No project, coursework, or bank entry. |
| **Node.js** | Your JS is the React frontend. No Node backend anywhere. |
| **Spring** | Java is coursework-only; no Spring work exists. |
| **Jenkins**, **GitHub Actions** | No CI/CD pipeline in any project or repo. |
| **Grafana**, **Prometheus** | No observability stack in any project. |
| **Bedrock**, **DynamoDB**, **EBS**, **EMR** | AWS services never used; certifications cover concepts, not hands-on work. |
| **Tableau** | No evidence. Your plotting is matplotlib. |
| **A/B testing frameworks** | No experiment-on-users work. (Your ablation work is offline model evaluation — already listed above under its real name.) |

### Judgment calls — keep only if you can defend them in a screen

| Skill | Status |
|---|---|
| **OAuth2**, **JWT** | Auth0 is real and implements both under the hood, but you configured Auth0 rather than building an identity gateway. Safe framing: keep "Auth0", drop the raw protocol tags. |
| **SageMaker AI**, **Lambda** | On your resume's Cloud line but not evidenced in the bank. Keep only if certification study is enough for you to answer questions. |
| **HIPAA**, **HIPAA compliance** | The airway platform is described as "HIPAA-conscious", not certified-compliant. Already un-hearted in your profile; consider dropping. |
| **Anthropic Claude API** | `llm_client.py` implements the Anthropic path, but verification on 2026-07-29 found no usage ledger — the call has never actually run. Defensible as "integrated the API"; do not claim production use. OpenAI API is unambiguous (airway chatbot). |

---

## 3. WORK EXPERIENCE — paste-ready blocks

Simplify fields: Position Title / Company / Location / Experience Type / Start / End / Description.

**Fix first:** the current "Cloud Architect — Harvard Medical School, Aug 2025 – Present" entry
does not correspond to anything in your resume or evidence bank. Entry 5 below is the real
version of that work.

---

### Entry 1

- **Position Title:** Graduate Researcher
- **Company:** Harvard University (Wyss Institute — Mooney Lab & Alvarez-Melis Lab)
- **Location:** Boston, MA
- **Experience Type:** Research / Part-Time (you are a full-time student)
- **Dates:** Feb 2026 – Present

**Description:**

```
Cross-Species Drug Translation using Optimal Transport and Generative AI.

- Built Optimal Transport models (VAEs, unbalanced OT) predicting animal-to-human trial
  translation from scRNA-seq atlases, with scanpy pipelines automating cell-type labeling
  and dataset integration.
- Ported a 2018 CPU-only TensorFlow reference implementation to PyTorch, reimplementing the
  Input Convex Neural Networks behind the optimal-transport dual and enabling GPU training
  on Harvard's FASRC Cannon cluster.
- Benchmarked CellOT against scGen on cross-species perturbation prediction, measuring
  0.85-0.90 R^2 with the source species in training versus 0.65-0.67 on the held-out-species
  split.
- Established through paired single-factor ablations that gene-space choice reverses with
  split - 6,619 orthologs wins in-distribution while 1,000 HVGs wins on every
  out-of-distribution metric - ruling out a split-independent default.
```

> Do not reinstate "diffusion models" or "GENOT": the bank records diffusion as planned but
> never implemented, and GENOT has no evidence entry.

---

### Entry 2

- **Position Title:** Independent Project — ML Systems Engineer
- **Company:** Harvard FASRC Cannon Cluster (independent)
- **Location:** Boston, MA
- **Experience Type:** Project
- **Dates:** Jun 2026 – Present

**Description:**

```
Autonomous Ablation-Search Agent for Cluster-Scale ML Experimentation.
github.com/JunyiZhou-Conny/scgen-cellot-autoresearch

- Built a self-directed experiment harness (submit -> watch -> reflect -> decide ->
  synthesize) that plans, launches, and triages SLURM ablation studies unattended -
  338 runs, 318 clean and 20 with handled errors, over 79 hours of compute.
- Split the planner from the execution substrate and checkpointed each agenda to disk, so
  the cluster keeps running the last plan while the planner is offline; an adaptive
  one-delta proposer clears a validation gate before every submit.
- Designed a fairshare-aware scheduler routing small-MLP training to CPU partitions, where
  GPU carries 200-500x the fairshare cost, and made runs preemption-tolerant on
  serial_requeue via checkpoint/resume and capped job arrays.
- Wired an optional LLM planner behind that interface with per-call token and cost
  accounting and a spend ceiling that degrades to the deterministic planner on breach or
  API failure.
```

---

### Entry 3

- **Position Title:** Data Analyst
- **Company:** Emory University — Bou-Nader Lab, Dept. of Biochemistry
- **Location:** Atlanta, GA
- **Experience Type:** Research / Part-Time
- **Dates:** Feb 2025 – Aug 2025

**Description:**

```
AlphaFold Protein-Nucleic Acid Interaction Prediction.
github.com/JunyiZhou-Conny/AlphaFold-Bou-Nader-Lab

- Engineered a pipeline integrating AlphaFold-Multimer and AlphaFold3 to predict
  protein-nucleic acid interactions from MSA data.
- Automated high-throughput inference across GPU nodes with SLURM parallel scheduling,
  tuning batch size to raise GPU utilization on shared HPC clusters.
- Built Python tooling (PyMOL, ChimeraX) ranking structures by pLDDT and PAE score, shipped
  as a documented CLI so non-technical researchers could run inference and triage results
  independently.
```

---

### Entry 4

- **Position Title:** Research Assistant
- **Company:** Emory University (Carrubba & Estrada)
- **Location:** Atlanta, GA
- **Experience Type:** Research / Part-Time
- **Dates:** Dec 2023 – May 2024

**Description:**

```
Computational Legislative Studies: UK & New Zealand Parliamentary Data.
github.com/JunyiZhou-Conny/Comput-Leg-UK-NZ

- Built Python scrapers and ETL pipelines over UK Parliament open data, normalizing bills,
  members, divisions, and Hansard proceedings into a relational schema covering 22,606
  member-level division votes, 4,791 MPs, 4,108 bills, and 3,875 constituencies.
- Diagnosed Cloudflare bot mitigation (403 challenge responses) and restored collection
  using TLS-impersonating requests (curl_cffi) and Selenium against an otherwise blocked
  source.
- Ran long scrapes as batch jobs on Emory's QTM cluster with isolated conda environments,
  staging data through AWS S3/EC2 and documenting the pipeline for a UK-to-New-Zealand
  handoff.
```

---

### Entry 5 — replaces the "Cloud Architect / Harvard Medical School" entry

- **Position Title:** Full-Stack Engineer, Scrum Master
- **Company:** Emory Pediatric Hospital
- **Location:** Atlanta, GA
- **Experience Type:** Part-Time / Project
- **Dates:** Jan 2024 – Aug 2025 (ended; not "Present")

**Description:**

```
Airway Management Simulation Chatbot. Live demo: d3g1qw60hz7yw7.cloudfront.net

- Architected a clinical agentic LLM pipeline pairing RAG retrieval over MongoDB Atlas
  Vector Search with prompt engineering and context-window management to generate
  multi-turn training scenarios from OpenAI models.
- Built a HIPAA-conscious full-stack platform (Python/Flask REST API, React, MongoDB,
  Auth0) deployed on AWS Elastic Beanstalk and CloudFront, tracking resident performance
  metrics.
- Led an Agile team of 6, running code reviews and folding clinician feedback into
  successive releases.
```

---

### Entry 6

- **Position Title:** Machine Learning Researcher
- **Company:** Emory University — Dept. of Computer Science
- **Location:** Atlanta, GA
- **Experience Type:** Research / Project
- **Dates:** Oct 2024 – Jan 2025

**Description:**

```
Reimplementation of Transformer Architecture.
github.com/JunyiZhou-Conny/Reimplementation-of-Transformer

- Implemented a Transformer in PyTorch from scratch - Multi-Head Self-Attention, Positional
  Encodings, Layer Normalization - validating architectural correctness against
  nn.Transformer.
- Tuned hyperparameters and the Cross-Entropy objective to reach a 9.38 BLEU score on
  English-to-German translation.
```

---

## 4. PROJECTS — coursework (label as coursework; do not list as employment)

If Simplify has a Projects section, these belong there rather than in Work Experience.

**Parameter-Efficient Fine-Tuning of BLIP-2 for Visual Question Answering** — Harvard
SHBT-261, Spring 2026 — github.com/JunyiZhou-Conny/mini3

```
- Fine-tuned BLIP-2 (OPT-2.7B) on TextVQA using LoRA, lifting accuracy from 0.078 zero-shot
  to 0.213 - nearly 3x - while training 2.62M parameters (0.07% of the model) in 8 minutes
  on a single A100.
- Isolated the contribution of prompt engineering across four templates, showing
  OCR-augmented prompting alone raised zero-shot accuracy to 0.106 before any weight updates.
- Ablated LoRA rank over r in {4, 8, 16} and automated the pipeline end to end, generating
  every reported figure and LaTeX table directly from result JSONs for reproducibility.
```

**Image Classification Benchmark: Classical ML, CNNs, and Vision Transformers** — Harvard
SHBT-261, Spring 2026

```
- Benchmarked ViT-B/16, ResNet-18, and a HOG + Random Forest baseline on Caltech-101
  (8,677 images, 101 classes), reaching 0.972 top-1 and 0.998 top-5 with ViT against 0.507
  for the classical pipeline.
- Quantified the cost of that gain: ViT beat fine-tuned ResNet-18 by 1.8 points at roughly
  9x the training time, making the accuracy-per-GPU-hour tradeoff explicit.
- Established through ablations that light augmentation and SGD outperform heavy
  regularization and adaptive optimizers when fine-tuning on small datasets.
```

**Semantic Segmentation Benchmark: U-Net, ViT, and DeepLabV3+** — Harvard SHBT-261,
Spring 2026 — github.com/JunyiZhou-Conny/mini2

```
- Benchmarked DeepLabV3+, U-Net, and a frozen ViT-Tiny encoder on Pascal VOC 2007
  (21 classes), reaching 0.640 mIoU and 0.928 pixel accuracy with COCO-pretrained
  DeepLabV3+.
- Diagnosed mode collapse in U-Net under data scarcity - 209 training images yielded
  predictions for only 4 of 21 classes - isolating pretraining rather than architecture as
  the dominant factor.
- Reached 0.304 mIoU in 105 s by training only an 814K-parameter decoder head on a frozen
  encoder, establishing a compute-efficient middle ground.
```

**Pneumonia Detection from Chest Radiographs** — Harvard BST-261 Kaggle competition,
Spring 2026

```
- Diagnosed a 14-point generalization gap on a Kaggle chest-radiograph benchmark - 99%
  validation against 85% leaderboard - and traced it to memorization of a 4,700-image
  training set.
- Closed the gap to 96% with domain-aware augmentation (Mixup alpha = 0.2,
  RandomResizedCrop, RandomErasing, affine jitter), excluding vertical flips that would
  render chest radiographs anatomically implausible.
- Found that freezing DenseNet-121's early layers outweighed architecture choice, beating
  ResNet-50, ConvNeXt-Tiny, EfficientNet-B0, and a three-model ensemble to reach a 0.959
  public score.
```

---

## 5. PORTFOLIO & LINKS — currently empty, fill these

Your GitHub URL field is blank while four of your strongest entries link to repos.

- **GitHub URL:** `https://github.com/JunyiZhou-Conny`
- **LinkedIn URL:** already set
- **Portfolio URL:** pending — this is the personal-site project

---

## 6. EDUCATION

- Harvard T.H. Chan School of Public Health — S.M. Health Data Science — Aug 2025 – Mar 2027
  (program requirements complete December 2026; commencement March 2027; available for
  full-time start January 2027)
- Emory University, College of Arts and Sciences — B.S. Applied Mathematics and Statistics,
  Minor in Computer Informatics — Aug 2021 – May 2025 — GPA 3.925
