# Resume architecture

You maintain **one evidence bank** and **three cluster resumes**. Pick a cluster by job title — not by inventing a new resume each time.

## Which file to use

| Cluster | File (current) | Use when the job looks like… |
|---|---|---|
| `cloud_swe` | `cloud_swe/2026-07-20_cloud-swe_v1.1` | Software Engineer, Backend, Platform, Cloud, Infrastructure, general new-grad SWE |
| `data_ml` | `data_ml/2026-07-20_data-ml_v1.1` | ML Engineer, Applied AI, AI Engineer, Data Scientist/Engineer, LLM/RAG roles |
| `health_ai` | `health_ai/2026-07-20_health-ai_v1.1` | Healthcare AI, clinical data, digital health, life-science ML — when domain is an asset |

**Quality rule:** cluster = base bullets + reorder only. Do not dilute specificity. `v1.0` was too rewritten; prefer `v1.1`.

## Adjacent / stretch roles (AI infra, ML systems, inference)

Do **not** invent a fourth generic resume for every exciting posting.

Use Cursor command `/analyze-adjacent-role`:

1. Save JD to `jobs/inbox/<company-role>.md`
2. Run the command — it produces evidence maps, optional job-specific resume, gap analysis, outreach plan
3. Updates `data/role_patterns.csv`
4. Only recommends a permanent `ml_systems_ai_infrastructure` cluster when the pattern thresholds are met

Keep separate: **Interest** vs **Fit** vs **Pursuit lane** vs **Tailoring mode**.

### For your goals (big tech / fast startups / agents)

Default order:

1. **Most roles → `data_ml`** (AI agent, RAG, applied ML)
2. **Classic SWE / cloud / backend → `cloud_swe`**
3. **Only when the company is clearly health/life-science → `health_ai`**

Same projects in all three; only **ordering and wording emphasis** change.

## Folders

- `base/`: master source + `evidence_bank.md`
- `cloud_swe/`, `data_ml/`, `health_ai/`: stable cluster versions
- For a specific A-tier job: change 2–4 bullets max; record version in `data/applications.csv`

## Version names

Example: `2026-07-20_cloud-swe_v1.0.tex` → compile to same-name `.pdf`

After applying, log the exact **PDF basename** (or tex stem) as `resume_version`, e.g. `2026-07-20_data-ml_v1.0`.

## Compile to submit-ready PDF

Whenever a `.tex` is ready:

```bash
# all clusters
./scripts/compile_resume.sh

# one cluster
./scripts/compile_resume.sh data_ml

# one file
./scripts/compile_resume.sh resumes/data_ml/2026-07-20_data-ml_v1.0.tex
```

Upload the generated `.pdf` sitting next to the `.tex`. Do not upload the `.tex` to ATS.
