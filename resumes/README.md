# Resume architecture

You maintain **one evidence bank** and **three cluster resumes**. Pick a cluster by job title — not by inventing a new resume each time.

## Which file to use

| Cluster | File (current) | Use when the job looks like… |
|---|---|---|
| `cloud_swe` | `cloud_swe/2026-08-24_cloud-swe_v1.3` | Software Engineer, Backend, Platform, Cloud, Infrastructure, general new-grad SWE |
| `data_ml` | `data_ml/2026-08-24_data-ml_v1.3` | ML Engineer, Applied AI, AI Engineer, Data Scientist/Engineer, LLM/RAG roles |
| `health_ai` | `health_ai/2026-08-24_health-ai_v1.3` | Healthcare AI, clinical data, digital health, life-science ML — when domain is an asset. Leads with S-Seg-RLVR. |

**Quality rule:** cluster = base bullets + reorder only. Do not dilute specificity.

## Clusters are generated, not hand-edited

As of `v1.3`, cluster resumes are built from `base/JZ_resume.tex` by a script. Edit base, then
regenerate — do not edit a cluster `.tex` directly, or the next build will overwrite it.

```bash
python3 scripts/build_clusters.py           # all three clusters
python3 scripts/build_clusters.py data_ml   # one cluster
python3 scripts/build_clusters.py --list     # show parsed entry ids
```

Entry selection, section grouping, and skills-line ordering per cluster live in the `CLUSTERS`
dict at the top of `scripts/build_clusters.py`. Base is a two-page superset; each cluster selects
four entries and lands on one page.

**Why:** `v1.1` and earlier drifted. Pinecone and Kubernetes were removed from base on 2026-07-27
after neither could be substantiated, but both survived in every hand-maintained cluster file.
Generating from one source prevents that class of error.

## Deleted versions (2026-07-27)

The `2026-07-20` `v1.0` and `v1.1` cluster files were deleted. They contained claims since found
unsupportable (Pinecone, Kubernetes) and a stale end date on the airway chatbot ("Present" — it
actually ended August 2025), so keeping uploadable PDFs around was a live risk.

`data/applications.csv` still references `2026-07-20_data-ml_v1.1` (8 rows),
`2026-07-20_cloud-swe_v1.1` (8 rows), and `2026-07-23_google-swe-intern_v1.0` (1 row). Those
version strings are deliberately left intact — they record what was actually submitted. To see the
exact document behind one of them:

```bash
git checkout 65f4928 -- resumes/data_ml/2026-07-20_data-ml_v1.1.pdf
```

**If any of those 17 applications reaches a screen:** be ready for a Pinecone or Kubernetes
question, and correct the airway chatbot dates if they come up.

## Job-specific resumes

`cloud_swe/2026-07-23_google-swe-intern_*` predate the 2026-07-27 rewrite and are missing six
entries plus the corrected skills block. Their airway dates were fixed in place, but regenerate
from base rather than reusing them for a new application.

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

### Page-count gate

The compile script fails if a resume exceeds its page limit — **1 page for clusters, 2 for
`base/`** (the deliberate superset). A cluster resume that spills onto a second page still
compiles and still looks fine locally, so without this check it gets uploaded as a "one-pager".
This is the failure mode that tailoring edits cause most often.

```bash
./scripts/compile_resume.sh                  # exits 1 on overflow, naming the file
./scripts/compile_resume.sh --allow-overflow # intentional longer PDF
RESUME_MAX_PAGES=2 ./scripts/compile_resume.sh
```

If a cluster overflows, trim bullets in `base/JZ_resume.tex` and regenerate — do not edit the
cluster `.tex` to make it fit, because the next build overwrites it.
