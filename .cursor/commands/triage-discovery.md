# /triage-discovery

AI-layer triage of today's discovery CSV. **No hardcoded skip regex in Python.**

## Steps

1. Ensure merged discovery exists (`data/discovery/YYYY-MM-DD_all.csv`). If missing, run `python3 scripts/automation/run_discovery.py`.
2. Run `python3 scripts/triage_discovery.py` (optional `--date`) to refresh the review pack.
3. Read:
   - `knowledge/discovery_triage_rules.yaml` (guide rules)
   - `config/profile.yaml`
   - `generated/discovery_for_triage_YYYY-MM-DD.csv` (or the `_all.csv`)
4. For **every** row, decide `keep` | `later` | `skip` using the guide rules:
   - `remote` (hard)
   - `non_target_role` (hard)
   - `hard_gate` (hard; soft on vague intern grad windows — internships OK)
   - `timing_expired` (hard)
   - `traditional_student_coop` (soft)
   - `intern_ok` / `fit_priority` (policy)
5. Write `generated/discovery_triage_YYYY-MM-DD.csv` with required columns from the rules file, including `evidence_basis` and blank `user_confirm`.
6. Write a short `generated/discovery_triage_YYYY-MM-DD.md` with counts + KEEP list.
7. Stop. Do **not** ingest into `applications.csv` until the user confirms.

## Honesty

- Prefer board CSV fields; do not fabricate JD requirements.
- If `work_model` is empty, do not invent remote.
- Sponsorship unknown/no is not skip.
