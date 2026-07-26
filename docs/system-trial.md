# System trial (30–60 min)

Goal: prove the loop works. **Not** a full application blitz.

```text
Discover → triage → autofill (review) → submit only if you want →
Simplify tracker → CSV → local import → enrich → dashboard
```

## Before you start (5 min)

- [ ] Chrome has **Simplify Copilot** installed and logged in
- [ ] Simplify profile has: name, email, phone, LinkedIn, GitHub, education, work auth answers ready
- [ ] PDFs already compiled locally (re-run if you edit `.tex`):

```bash
./scripts/compile_resume.sh
```

  - Default upload: `resumes/data_ml/2026-07-20_data-ml_v1.1.pdf`
  - SWE/cloud titles: `resumes/cloud_swe/2026-07-20_cloud-swe_v1.1.pdf`
- [ ] Optional: Jobright open for discovery only (do not treat as ledger)

### Work-auth cheat sheet (confirm against your own facts)

After OPT EAD is valid for full-time work (planned ~2027-01-18):

- Authorized to work in the US? → usually **Yes**
- Need sponsorship now or in future? → **Yes** (do not lie to bypass ATS)

If a form mixes OPT/EAD/H-1B wording, screenshot the question and paste into local `auth_qa_notes` later.

---

## Block 1 — Discovery (10 min)

Find **3 roles total** (including Optiver if still open):

| # | Track | What to look for |
|---|---|---|
| 1 | Already queued | Optiver Graduate Software Engineer (2027 Start) — already in repo as `J20260720-001` |
| 2 | New grad 2027 | Big tech / fast startup / AI-ish SWE or ML new-grad, in-person OK, start ≥ Jan 2027 or Summer 2027 |
| 3 | Either new-grad or internship | Only if graduation eligibility is explicit for Dec 2026 grads |

Hard skip: fully remote; US citizen only; clearance; internship that requires return-to-school after you graduate.

Write down for each: company, role, **company career URL** (not only aggregator).

---

## Block 2 — Triage (5 min)

For each role, decide in ≤30 seconds:

| Field | Options |
|---|---|
| `pursuit_lane` | `core` / `broad` / `practice` |
| resume | `data_ml` (default) or `cloud_swe` |
| apply today? | yes / later |

Trial tip: make **at least one** `broad` so you test low-effort path.

---

## Block 3 — Apply loop (15–25 min)

For each “apply today” role:

1. Open **company** apply page
2. Simplify autofill
3. Upload the cluster PDF you chose
4. **Stop and read** work-auth questions before submit
5. Submit **only if you genuinely want this application counted**
   - If you only want to test autofill: fill, screenshot, **do not submit**, still log locally as `researching` or `ready_to_apply`
6. Confirm it appears in Simplify Tracker if submitted

---

## Block 4 — Sync to local repo (10 min)

### If Simplify lets you export CSV

1. Export tracker → save as:

```text
data/imports/simplify/2026-07-20.csv
```

2. Run:

```bash
cd /Users/conny/Desktop/job-search-2026-2027-starter
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/2026-07-20.csv
```

### If export is awkward / missing

Manually add each role (submitted or seriously triaged):

```bash
python3 scripts/jobsearch.py add-job \
  --company "COMPANY" \
  --role "ROLE" \
  --url "COMPANY_URL" \
  --source "Jobright|LinkedIn|Company site" \
  --cluster data_ml \
  --employment-type new_grad \
  --eligibility likely \
  --sponsorship unclear \
  --pursuit-lane core \
  --priority B \
  --next-action "Record resume version after apply" \
  --next-action-date "2026-07-21"
```

Then for each applied job id:

```bash
python3 scripts/jobsearch.py update-job JOB_ID \
  --status applied \
  --date-applied 2026-07-20 \
  --resume-version 2026-07-20_data-ml_v1.0 \
  --pursuit-lane core \
  --auth-work-authorized yes \
  --auth-needs-sponsorship yes \
  --next-action "Watch for OA / recruiter email" \
  --next-action-date 2026-07-27 \
  --log-note "Trial apply via Simplify"
```

Optiver (already exists):

```bash
python3 scripts/jobsearch.py update-job J20260720-001 \
  --status applied \
  --date-applied 2026-07-20 \
  --resume-version 2026-07-20_cloud-swe_v1.0 \
  --pursuit-lane core \
  --auth-work-authorized yes \
  --auth-needs-sponsorship yes \
  --next-action "Watch for OA / recruiter email" \
  --next-action-date 2026-07-27 \
  --log-note "Trial apply via Simplify"
```

Only run the Optiver `applied` update **after you actually submitted**.

---

## Block 5 — Verify (3 min)

```bash
python3 scripts/jobsearch.py dashboard
```

Open `generated/dashboard.md` and check:

- [ ] Applied count matches what you submitted
- [ ] Each applied row has `resume_version`
- [ ] Each active row has `next_action` + date
- [ ] Practice share is fine (trial can be 0%)

---

## Success criteria for this trial

Pass if **all** are true:

1. Autofill saved you clear time vs typing
2. At least 1 role is in local CSV with correct status
3. You know which resume file was used
4. Dashboard is readable without confusion
5. You did **not** need Jobright as a second source of truth

## After trial — tell Cursor

Paste back:

- How many submitted vs dry-run only
- Whether Simplify CSV export worked (yes/no + column names if yes)
- Friction points (auth questions, resume upload, tracker missing a job)
- Whether you want tomorrow’s target to be 5 or 10 applies
