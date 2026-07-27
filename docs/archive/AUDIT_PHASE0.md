# Phase 0 Audit — 2026-07-20

## 1. Current directory structure (material)

```text
.cursor/rules/          # 6 rules (00,10,20,30,40,50) — no .cursor/commands/
config/profile.yaml
data/
  applications.csv      # 1 job (Optiver)
  networking.csv        # contacts+interactions combined; empty rows
  activity_log.csv
  imports/simplify/
docs/                   # workflow, platforms, eligibility, trial, status
generated/              # dashboard, weekly-review
prompts/                # analyze-jd, tailor, coffee-chat, weekly
resumes/
  base/                 # JZ_resume + evidence_bank.md
  cloud_swe|data_ml|health_ai/  # v1.0 (weak) + v1.1 (current)
scripts/
  jobsearch.py          # add/update/import-simplify/dashboard/weekly
  compile_resume.sh
templates/
```

**Missing vs target:** `knowledge/`, `tests/`, `.cursor/commands/`, `resumes/clusters|job_specific|archive/`, `data/contacts.csv`, `data/resume_versions.csv`, analytics/daily/calendar/outreach generators, schema migration tooling.

## 2. Completed / partial / missing

| Area | Status | Notes |
|---|---|---|
| Profile basics | Partial | `config/profile.yaml` exists; not split into knowledge/* |
| Evidence bank | Partial | Markdown only (`resumes/base/evidence_bank.md`); no YAML skill IDs |
| Applications ledger | Partial | Core fields + lane/auth; missing stage dates, tailoring, label meta, scoring |
| Simplify one-way import | Done (MVP) | URL / company+role match; preserves strategy fields |
| Sponsorship ≠ hard gate | Done | Rules + docs |
| Pursuit lanes | Done | core/broad/practice |
| Resume clusters | Partial | v1.1 good quality; no `resume_versions.csv`; path ≠ `resumes/clusters/` |
| Networking | Partial | One CSV mixes contact+outreach; no queue engine |
| Daily plan / outreach queue | Missing | |
| Calendar ICS / Google | Missing | |
| Analytics / experiments | Partial | Dashboard counts only; no funnel.csv / time cost |
| Validate / dedupe | Missing | Import has light match only |
| Cursor commands | Missing | Prompts exist under `prompts/` |
| Tests | Missing | |
| Automation docs | Missing | |

## 3. Naming / schema conflicts (migration risks)

| Current | Target | Strategy |
|---|---|---|
| `id` | `job_id` | Keep `id` as primary; add `job_id` alias column = same value |
| `posting_url` | `job_url` | Keep `posting_url`; add `job_url` mirror on migrate/import |
| `date_found` | `date_discovered` | Keep both; sync on write |
| `status` | `application_status` | Keep `status`; add alias column |
| `eligibility` values verified/likely/unclear/ineligible | `hard_eligibility` eligible/uncertain/ineligible | Map + new column; do not drop old |
| `sponsorship_signal` verified/likely/unclear/no | supportive/historically_possible/unclear/unlikely/explicit_no | Map + allow both during transition |
| Status set includes `researching`, `ready_to_apply` | `saved`, `preparing`, … | Accept union of both enums |
| `networking.csv` all-in-one | `contacts.csv` + `networking.csv` interactions | Split: migrate contacts out; keep interaction rows |
| `resumes/cloud_swe/` | `resumes/clusters/cloud_swe/` | **Do not move** existing files; document canonical paths; optional symlink later |
| Rules `00-50` | Rules `01-10` named modules | Add new modules; keep old until commands rely on new ones |

## 4. Data safety

- 1 application row (Optiver) — must survive migration.
- Resume PDFs/tex must not be deleted.
- No secrets currently in git except historical resume footnote password (removed from tex; base PDF regenerated without password).
- `.gitignore` needs expansion for tokens/credentials.

## 5. Implementation plan (incremental)

1. **Phase 1 — Data foundation:** backup → migrate applications (additive) → knowledge YAMLs → validate + dedupe + tests  
2. **Phase 2 — Labeling + resume versions:** label engine (suggest/confidence/manual lock) + `resume_versions.csv`  
3. **Phase 3 — Networking:** contacts split + outreach queue + templates  
4. **Phase 4 — Daily ops:** daily plan + analytics + wire into `daily_job_search.py`  
5. **Phase 5 — Calendar + schedule docs:** ICS dry-run + launchd/cron docs  
6. **Phase 6 — deferred:** Google Calendar OAuth, Cursor CLI/Background Agents  

**Constraint:** no auto-send email/LinkedIn/apply/calendar write without confirmation.
