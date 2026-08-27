# Job Search 2026–2027 Operating System

Strategy and memory layer on top of Simplify and discovery tools. Simplify is the
application ledger of record; this repo holds *why* — resume version, pursuit lane,
sponsorship signal, work-authorization answers, networking, and next actions.

**Target:** Summer 2027 internships and 2027 new-grad roles. Earliest full-time start
`2027-01-18` (I-20 program end `2026-12-18`, commencement March 2027). No fully remote roles.

## Sharing with friends

Early shared toolkit (scripts + discovery + apply queue). Personal ledgers stay in forks.

→ **Set up your own copy (you or your Cursor agent):** [`docs/collaborators/SETUP.md`](docs/collaborators/SETUP.md)  
→ Kickoff prompt to paste into a Cloud Agent: [`docs/collaborators/AGENT_KICKOFF.md`](docs/collaborators/AGENT_KICKOFF.md)  
→ In Cursor: `/collaborator-setup`  
→ Progress / architecture: [`docs/FRIENDS_CANVAS.md`](docs/FRIENDS_CANVAS.md)  
→ Upstream PR rules: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md)

## The one-hour daily loop

**Overnight — automatic.** The "Daily Job Discovery" Cursor Automation scrapes the intern
and new-grad boards, triages every row, and writes `generated/discovery_triage_YYYY-MM-DD.{csv,md}`
plus `jobs/inbox/daily-YYYY-MM-DD.md`. Rules live in `docs/automation/DAILY_JOB_DISCOVERY.md` —
edit that file and push; the Automations UI only holds the pointer in `docs/automation/UI_POINTER.md`.

**Your hour — the apply queue.**

```bash
python3 scripts/serve_apply_queue.py --date $(date +%F)
# then open http://127.0.0.1:8765/
```

Open a role → read the JD → apply via Simplify → tick **Applied**, or click **Pass**.
Both write to the repo immediately:

| Action | Writes |
|---|---|
| Applied | `status=applied` + `date_applied` + `resume_version` (creates the row if the role was triage-only) |
| Pass | `data/job_decisions.csv` + `status=passed`, and the role stops reappearing |

Filters: GTC 2026 sponsor · Boston/MA · Bay Area/SF · big tech / biotech / startup · queue freshness.

Open the served URL, not the static HTML file — the file version can only hold decisions in
browser storage, which then need `scripts/sync_queue_decisions.py`.

**Org designer.** Design the Grok Bot company as a tree. Does not hire Bots.

```bash
python3 scripts/serve_org_designer.py
# then open http://127.0.0.1:8766/
```

**Weekly.** Drop a Simplify export in `data/imports/simplify/YYYY-MM-DD.csv`, then reconcile:

```bash
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/dedupe_applications.py
python3 scripts/validate_data.py
python3 scripts/refresh_resume_stats.py     # which resume version actually converts
python3 scripts/jobsearch.py dashboard
```

## Layout

| Path | Holds |
|---|---|
| `config/profile.yaml` | Canonical profile, dual graduation dates, tracks, lanes |
| `knowledge/` | Evidence bank, triage rules, company classes, market signals |
| `data/applications.csv` | The ledger |
| `data/job_decisions.csv` | Passed roles (URL archive, prevents resurfacing) |
| `generated/` | Machine output — triage packs, apply queue, dashboards |
| `resumes/` | Base + cluster resumes; registry in `data/resume_versions.csv` |
| `docs/` | Current policy; `docs/archive/` is history, not current state |
| `docs/collaborators/` | Friend / future-collaborator setup runbook + identity templates |

## Non-negotiables

- Nothing is submitted or sent without explicit confirmation.
- Sponsorship `unclear` / `no` is never hard ineligibility — route via `pursuit_lane`.
- Never invent statuses, dates, metrics, referrals, or JD requirements.
- `label_source=manual` is not auto-overwritten.
- No passwords, ID documents, or session files in git (`secrets/` is ignored).

## Resumes

- Baseline: `resumes/base/JZ_resume.tex`
- Clusters: `cloud_swe` / `data_ml` / `health_ai`
- Default resume line is **December 2026 program completion**; use the dual-date line
  (March 2027 commencement + December 2026 completion) only when a posting demands
  Spring 2027 wording. See `docs/eligibility.md`.

## Cursor commands

`.cursor/commands/` — `apply-queue`, `triage-discovery`, `sync-simplify`, `label-job`,
`validate-data`, `weekly-review`, `tailor-resume`, `audit-system`.
