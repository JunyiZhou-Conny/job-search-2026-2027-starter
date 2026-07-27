# /audit-system

Audit the repo against how it is actually used, not against an old plan.

1. Read `README.md`, `docs/workflow.md`, `docs/BOUNDARIES.md`, `docs/automation/DAILY_JOB_DISCOVERY.md`.
2. Check reality, not intent:
   - Which scripts produced output recently (`generated/`, `data/`) and which are stale?
   - Which `data/applications.csv` columns are still never populated?
   - Where is the funnel stuck (counts by `status`)?
3. Report completed vs unused vs contradictory (docs that disagree with `config/profile.yaml`,
   `knowledge/discovery_triage_rules.yaml`, or `docs/status-definitions.md`).
4. Propose the next smallest increment. Prefer deleting unused parts over adding new ones.
   Do not rewrite the system.

Historical snapshots live in `docs/archive/` — treat them as history, not current state.
