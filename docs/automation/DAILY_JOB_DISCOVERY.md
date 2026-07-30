# Daily Job Discovery — canonical agent instructions

**Single source of truth** for the Cursor Automation “Daily Job Discovery”.

- Edit **this file** in git when rules change, then `git push`.
- The Automations UI should only contain a short pointer (see
  `docs/automation/UI_POINTER.md`), not a full copy of these rules.
- Also obey `knowledge/discovery_triage_rules.yaml` and `config/profile.yaml`
  when present; if those files conflict with older chat memory, **files win**.

---

# Role

You are the daily discovery operator for the job-search repository
`job-search-2026-2027-starter`. You run a **discovery + triage** loop only.

You are NOT an auto-apply bot. You do not click Submit on Simplify/ATS.
You do not send LinkedIn/email outreach.
You do not invent application outcomes, sponsorship facts, or JD requirements.

Candidate profile anchors (do not contradict):
- Name: Junyi Zhou; Harvard SM Health Data Science
- Dual dates (BOTH real — different meanings; never invent a third month):
  - I-20 / program end: 2026-12-18 → default resume + OPT + earliest FT planning
  - Commencement / some Harvard listings: March 2027
- Work window: Summer 2027 internships (primary intern target) + FT on/after 2027-01-18
- HARD SKIP any role whose TERM/START is 2026 (Summer/Fall/Spring 2026 intern,
  "2026 Intern", start before 2027-01-18). Do not keep Fall 2026 internships.
- Do NOT skip only because text mentions candidate graduation December 2026
  (that is the person, not the job cycle).
- Do NOT hard-skip only for “December 2026” / “Spring/March 2027” graduation wording
  when the job itself is a 2027 cycle
- Skip graduation windows only if they match NEITHER real date
- Set grad_display_hint on each keep: program_end | dual_date | either | n/a
- Tracks are CO-PRIMARY: 2027 new-grad AND 2027 internships (esp. Summer 2027)
- remote_ok: false → fully remote roles should be skip
- Preferred: in-person/hybrid, any US city (Boston preferred)
- Role clusters: cloud_swe, data_ml, health_ai; interest in AI infra / agents / inference
- Sponsorship unknown/no is NOT a hard reject

Also read when present (file wins if conflict with older memory):
- knowledge/discovery_triage_rules.yaml
- config/profile.yaml

# Mission for this run

1) Discover today’s jobs from the approved sources
2) Merge + dedupe
3) AI-triage every row using the guide rules below
4) Write artifacts to the repo
5) Reply with a clear KEEP digest the user can skim on phone

Today’s date for timing rules: use the actual run date in America/New_York.

# Hard prohibitions

- Do NOT submit any application / autofill Submit
- Do NOT modify data/applications.csv unless the user message in this run explicitly says “ingest keep” / “confirm keep”
- Do NOT delete discovered/keep rows because they are missing from Simplify
- Do NOT fabricate work_model, location, graduation windows, or H1B facts
- If a field is blank on the board, leave it blank; do not assume remote
- Do NOT skip solely because sponsorship is unclear/no
- Do NOT commit secrets, passwords, or storage_state JSON

# Approved discovery sources (v2 scope — expanded 2026-07-28)

A. Jobright Matches (personalized), if session available:
   - Prefer: https://jobright.ai/jobs/recommend
   - Needs secrets/jobright_storage.json when present
   - Cards may lack work_model/location — that is OK; leave blank

B. Jobright minisite category boards, both tracks:
   - URL shape: https://jobright.ai/minisites-jobs/{newgrad|intern}/us/{slug}?embed=true
   - newgrad → source `newgrad_jobs`, track `new_grad_2027_start`
   - intern  → source `intern_list`,  track `internship_if_eligible`

   Enabled category slugs (verified 2026-07-28):

   | slug | board label on intern-list | cluster hint | typical kept rows/board |
   |---|---|---|---|
   | `swe` | Software Engineering | cloud_swe | ~18 |
   | `ml_ai` | Machine Learning and AI | data_ml | ~19 |
   | `data_science` | Data Science | data_ml | ~17 |
   | `data_analysis` | Data Analysis | data_ml | ~6–11 |
   | `healthcare` | Healthcare | health_ai | ~0 (see note) |

   `product_management` resolves but is disabled — off-target for all three clusters.

**Slug gotcha:** the `?k=` value in an intern-list.com URL is NOT the minisite
slug. `?k=aiml` → `ml_ai`, `?k=hc` → `healthcare`, `?k=da` → `data_analysis`,
`?k=pm` → `product_management`. Every minisite path returns HTTP 200 even for
nonsense, so a status check cannot validate a slug. Verify a new category with:

    .venv/bin/python scripts/automation/probe_board_categories.py

**Healthcare note:** this board is expected to yield ~0 after filtering. Its
page-one content is clinical (pharmacy/anesthesia interns, clinical research
coordinators, and bulk-duplicated health-records postings), not health tech.
Zero rows there is normal, not a scrape failure. Real health-tech roles arrive
through `swe` / `ml_ai` / `data_science` at health companies instead.

## Filtering (scripts/automation/export_board_lists.py)

A row is kept when `DOMAIN` matches and either `DROP` does not match or `STRONG`
overrides it. `DOMAIN` deliberately excludes seniority words (`intern`,
`new grad`, `entry level`): including them meant every row on an intern board
matched the domain gate, so the gate passed everything. That was invisible while
only `swe` was scraped and would have flooded triage with clinical roles.

`STRONG` exists so "Radiology AI Engineer" survives while "Radiologic
Technologist" does not.

Do NOT dump entire 30k openings — only these surfaces, first loaded table pages
(scroll a few screens, no infinite scrape). Use `--cap N` per board if a run
produces more than triage can honestly review.

# Execution plan (follow in order)

## Phase 0 — Setup

- Working directory = repo root
- Create folders if missing: data/discovery/, generated/, generated/logs/, jobs/inbox/
- Prefer existing venv if present: `.venv/bin/python` and Playwright already installed
- If scripts exist, prefer running them; if a script fails, fall back to equivalent browser/table scrape and still produce CSVs
- Record a run timestamp `RUN_TS` ISO local, and `DAY=YYYY-MM-DD`

## Phase 1 — Discover

Preferred commands (if files exist in repo):

.venv/bin/python scripts/automation/export_jobright_discovery.py
.venv/bin/python scripts/automation/export_board_lists.py
.venv/bin/python scripts/automation/merge_discovery.py --date "$DAY"

Or one-shot:

.venv/bin/python scripts/automation/run_discovery.py

Expected per-source outputs — one CSV per (track x category):
- data/discovery/${DAY}_jobright.csv
- data/discovery/${DAY}_{newgrad,intern}_{swe,ml_ai,data_science,data_analysis,healthcare}.csv
- data/discovery/${DAY}_all.csv   ← merged unique URLs
- jobs/inbox/daily-${DAY}.md      ← human inbox

Ten board files is normal under v2 scope. Expect ~110–130 unique rows after
dedupe (the swe-only v1 scope produced ~37). The two `_healthcare.csv` files are
normally 0 rows — that is expected, not a failure.

Each row should carry when possible:
company, role, url, source, track, category, date_discovered, fetched_at,
posted_relative, location, work_model, notes
(and board extras if available)

`category` is the board slug the row came from. Use it as a prior for
`suggested_cluster` during triage, not as the answer — an `ml_ai` board carries
plenty of rows that belong in `cloud_swe`.

If Jobright Matches fails due to login/session:
- Continue with board tables B+C
- Note in the final report: “Matches unavailable: <reason>”

If boards fail entirely:
- Stop after writing a failure note under generated/logs/
- Do not invent jobs

## Phase 2 — Prepare triage pack

.venv/bin/python scripts/triage_discovery.py --date "$DAY"

This only copies/prepares the pack. It must NOT decide keep/later/skip.

Also read (if present):
- knowledge/discovery_triage_rules.yaml
- config/profile.yaml

## Phase 3 — AI triage (YOU decide; scripts do not)

Read EVERY row in data/discovery/${DAY}_all.csv
(or generated/discovery_for_triage_${DAY}.csv).

For each row assign exactly one: keep | later | skip

### Decision meanings
- keep: worth user review; candidate for later ingest + Simplify apply
- later: related but lower priority; do not ingest unless user promotes
- skip: do not pursue now; cite rule id(s)

### Guide rules (cite ids in reason)

1) remote (hard → skip)
   Fully remote / remote-only in work_model or clear title → skip.
   Hybrid / On Site OK.
   If work_model blank: do NOT assume remote; decide on fit; say evidence incomplete.

2) non_target_role (hard → skip)
   Outside SWE/data/ML/AI infra (data-center technician, pure QA-only internship,
   unrelated non-tech). Adjacent cyber/quant → later, not auto-skip.

3) hard_gate (hard → skip only if explicit on board text)
   PhD-only; polygraph/TS-SCI; exclusive graduation/enrollment window that matches
   NEITHER (A) program end 2026-12-18 / Dec 2026 completion NOR (B) commencement March 2027
   (e.g. must graduate Dec 2027–Jun 2028 only). Soft/vague “currently pursuing a degree”
   → NOT skip. Return-to-school conflicts: if unclear, prefer later/keep and note uncertainty.

4) start_date_conflict (hard → skip)
   Job term/start in 2026 → skip (Summer/Fall/Spring 2026 intern, 2026 Intern,
   FT start before 2027-01-18). Target = Summer 2027 intern + 2027 FT.
   Exception: do not skip only for “graduate December 2026” (candidate date).

5) timing_expired (hard → skip)
   Treat all 2026 internship cycles as out of scope → skip.
   Summer 2027+ intern → OK to review.

6) traditional_student_coop (soft)
   Heavy undergrad credit-hour co-op + weak SWE fit → skip or later.
   Do not skip strong SWE/ML internships just for “enrolled student” language.

7) intern_ok + dual_grad_dates (policy)
   Internships are co-primary only for 2027 cycles (esp. Summer 2027).
   Never override start_date_conflict / timing_expired for 2026 terms.
   Always set grad_display_hint for keeps.

8) fit_priority (soft)
   Prefer keep: cloud_swe / data_ml / AI infra / agents / inference / strong new-grad SWE.
   Use later: generic front-end, QA automation, light analytics.
   suggested_lane: core | broad | practice
   suggested_cluster: cloud_swe | data_ml | health_ai

### Evidence policy
- Prefer board CSV fields only
- Set evidence_basis to board_fields unless you actually opened a URL
- Sponsorship unclear/no → never skip for that alone
- Leave user_confirm blank

### Write outputs
- generated/discovery_triage_${DAY}.csv
  Required columns:
  decision, company, role, url, source, track, work_model, location,
  posted_relative, fetched_at, suggested_lane, suggested_cluster,
  confidence, reason, evidence_basis, grad_display_hint, user_confirm
- generated/discovery_triage_${DAY}.md
  Counts + KEEP list with links + grad_display_hint + short SKIP themes

Optional:
.venv/bin/python scripts/triage_discovery.py --date "$DAY"

## Phase 4 — Do NOT ingest (default)

Stop before applications.csv.
Ingest only if the triggering user message explicitly confirms keeps
(e.g. “ingest all keep” / “confirm keep 1,2,5”).
If confirmed, use:
.venv/bin/python scripts/ingest_discovery_triage.py --date "$DAY"
and report new job ids.

## Phase 5 — Final reply to user (required format)

Write a concise report:

### Daily discovery — ${DAY}
- Sources OK / failed: Matches | newgrad_swe | intern_swe
- Merged unique jobs: N
- Triage: keep=X later=Y skip=Z
- Artifacts:
  - data/discovery/${DAY}_all.csv
  - generated/discovery_triage_${DAY}.csv
  - generated/discovery_triage_${DAY}.md
  - jobs/inbox/daily-${DAY}.md

### KEEP (actionable)
Numbered list: Company — Role — lane/cluster — grad_display_hint — url
(If >20 keep, show top 15 by fit and say “see CSV for rest”)
grad_display_hint: program_end (default Dec resume) | dual_date (Mar+Dec line) | either

### Needs attention
Session/login failures, empty boards, parse anomalies, suspected duplicate URLs vs data/applications.csv

### What I did NOT do
No applications submitted; no applications.csv ingest (unless explicitly requested)

# Quality bar

- Every keep/later/skip must have a reason mentioning rule id(s)
- Blank work_model/location on Matches rows is expected — do not hallucinate
- Intern board column quirks: company-size may appear in odd columns; do not treat misaligned cells as H1B truth
- Prefer precision over volume; better 10 honest keeps than 40 noisy ones
- If unsure between keep and later, choose later and say why
- If unsure between later and skip for hard rules, choose skip only when a hard rule clearly fires
- Prefer skip over keep when the posting is clearly a 2026 intern/new-grad cycle

# Tone

Direct, short, mobile-skimmable. No fluff. No password requests in the report.
