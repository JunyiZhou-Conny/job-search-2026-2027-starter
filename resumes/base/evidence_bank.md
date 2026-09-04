# Master evidence bank

Source of truth for cluster resumes. Do not invent beyond what is listed here.
Last reviewed: 2026-08-24 from `resumes/base/JZ_resume.tex`.

## Target ambition (user-stated)

- Prefer big tech or fast-iterating startups
- Want depth in AI agents, context management, applied ML systems — not “pure biotech company” as the only path
- Domain of past projects may be clinical/biology; transferable systems work should lead

## Positioning principle

```text
Domain (clinical / biology) = context of the problem
Systems work (agents, RAG, full-stack, cloud, transformers, HPC) = what you sell
```

You do **not** need to erase Health Data Science. You need to stop leading with biology as the identity.

## Open fact checks (resolve before heavy applying)

| Item | Conflict | Action needed |
|---|---|---|
| Graduation | Dual real dates: I-20 program end **2026-12-18**; commencement **2027-03** | RESOLVED 2026-07-29 — resume now carries both: date column reads Aug 2025 – Mar 2027, with a bullet stating completion December 2026 and availability January 2027. Single-field ATS forms still answer December 2026. |
| Demo credentials | Resume footnote includes a live test password | Remove from all public resumes; share privately if needed |
| Internship auth | CPT availability still `unknown` in profile | Confirm before pursuing pre-grad internships |

## Evidence inventory (interview-defensible)

### A. Agentic / LLM systems (strongest bridge to ambition)

**Airway Management Simulation Chatbot** — Full-Stack Engineer, Scrum Master | Emory Pediatric Hospital | Jan 2024 -- Present

| Capability signal | Evidence on resume |
|---|---|
| Agentic LLM pipeline | Architected clinical agentic LLM pipeline |
| RAG | RAG system + OpenAI models; reduce hallucinations |
| Context management | Prompt engineering + context window management for dynamic scenario generation |
| Full-stack product | Python/Flask, React, MongoDB, AWS; real-time analytics |
| Privacy / production constraints | HIPAA-compliant platform framing |
| Leadership | Agile team of 6; code reviews; clinician feedback loop |
| Deployed artifact | CloudFront demo URL (do not publish passwords) |

**Use in:** `cloud_swe` (lead), `data_ml` (lead), `health_ai` (lead with clinical framing OK)

### B. Core ML / foundations (big-tech interview credibility)

**Transformer reimplementation** — Emory CS | Oct 2024 -- Jan 2025

- Built Transformer in PyTorch from scratch (MHA, positional encodings, LayerNorm)
- Hyperparameter tuning; 9.38 BLEU on EN→DE
- Validated against `nn.Transformer`
- Public GitHub

**Use in:** all clusters; especially `data_ml` and SWE/ML roles

### C2. Pathology RL capstone (bootstrap — no training results yet)

**S-Seg-RLVR** — Graduate Researcher | Harvard Health Data Science capstone (mentor Alexander Chowdhury) | Aug 2026 -- Present

- Method: instance count, separation, and topology as GRPO rewards instead of only Dice/IoU
- Real today: proposal, 30-paper library, roadmap, typed reward interfaces
- Not real yet: GRPO training, datasets, metrics, MICCAI acceptance
- Public GitHub. LinkedIn paste: `knowledge/linkedin_sseg_rlvr_draft.md`
- Use in: `health_ai` lead. Do not put fake numbers on any cluster.

### C. ML systems / research scale (secondary for non-bio roles)

**Wyss / Mooney & Alvarez-Melis** — Optimal Transport, VAEs, diffusion, CellOT, scRNA-seq | Feb 2026 -- Present

- Custom PyTorch CellOT; generative models; large dataset pipelines
- For non-bio roles: emphasize model implementation, latent-space modeling, evaluation — not “drug translation” as the headline

**AlphaFold pipeline** — Bou-Nader Lab | Feb 2025 -- Aug 2025

- HPC parallel scheduling, GPU inference, CLI tools, documentation for non-ML users
- For non-bio roles: emphasize pipeline engineering / tooling / HPC

### D. Education & skills

- Emory: Applied Math & Stats + Computer Informatics minor; DS, ML, NLP, DB coursework; GPA 3.925
- Harvard: SM Health Data Science; Deep Learning, Healthcare ML coursework
- Languages: Python, C++, Java, SQL, R, JavaScript
- ML: PyTorch, TensorFlow, Keras, sklearn, XGBoost/LightGBM, HF Transformers
- Data/infra: MySQL, PostgreSQL, MongoDB, MongoDB Atlas Vector Search, Hadoop, Spark
- Tools: Git, Docker, Jupyter, SLURM/HPC
- **Removed 2026-07-27:** Pinecone (never used — the RAG store is MongoDB Atlas Vector Search) and
  Kubernetes (never used — the chatbot runs on Elastic Beanstalk with Docker). See
  `knowledge/evidence_bank.yaml` for the full claim guidance.
- Cloud: AWS (SageMaker, Lambda, EC2, S3, Redshift), Snowflake, BigQuery
- Certs: AWS Cloud Practitioner, AWS AI Practitioner, AWS ML Associate

## Cluster narrative map

| Cluster | Lead with | Demote / shorten | Best for |
|---|---|---|---|
| `cloud_swe` | Chatbot (agent/RAG/full-stack/AWS), Transformer, cloud/certs, AlphaFold-as-HPC | Long biology framing on Wyss | SWE, backend, platform, infra, general new-grad |
| `data_ml` | Chatbot + Transformer + Wyss (models) + vector DB/Spark | Pure wet-lab adjacent wording | MLE, applied AI, data eng/analytics |
| `health_ai` | Same projects, clinical/bio problem statements OK | None required | Healthcare AI, clinical data, life-science tech |

## What not to do

- Do not invent FAANG internships, production traffic metrics, or agent frameworks you did not use
- Do not claim “big tech” experience you do not have — claim **transferable systems depth**
- Do not hide the degree; put systems bullets and skills above domain storytelling
- Do not answer sponsorship/auth questions inaccurately to “fit” a JD
