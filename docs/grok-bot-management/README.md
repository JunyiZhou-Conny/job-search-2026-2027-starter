# Grok Bot management

Notes on how Junyi wants to run Grok Bots against this job-search repo.

This folder does not change [AGENTS.md](../../AGENTS.md) or
[docs/BOUNDARIES.md](../BOUNDARIES.md). Submit only when Junyi names
the URL.

If the Chief is frozen, you are on the old research-only paste. Use
[ALIGNMENT.md](ALIGNMENT.md) and the live block in
[GROK_BOT_HANDOFF.md](GROK_BOT_HANDOFF.md).

- [GROK_BOT_HANDOFF.md](GROK_BOT_HANDOFF.md) — **live** Chief paste (assign + Ashby fill)
- [ALIGNMENT.md](ALIGNMENT.md) — why the Chief did nothing, and the fix
- [TEAM_HIERARCHY.md](TEAM_HIERARCHY.md) — four-person shop (paper)
- [SHARED_COMPUTER.md](SHARED_COMPUTER.md) — shared-computer fact
- [APPLY_CORP_STRUCTURE.md](APPLY_CORP_STRUCTURE.md) — first apply org chart
- [SOURCES.md](SOURCES.md) — quote ledger
- [THINKING.md](THINKING.md) — explanation
- [ORG_TEMPLATES.md](ORG_TEMPLATES.md) — org-record registry (paper)
- [ORG_CHART_BLANK.md](ORG_CHART_BLANK.md) — empty paper seed; do not fill by hand
- [JUNYI_SKETCH_2026-08-26.md](JUNYI_SKETCH_2026-08-26.md) — Architect / chiefs / Ashby × 10 sketch (paper)
- Visual designer: `python3 scripts/serve_org_designer.py` then open `http://127.0.0.1:8766/`
  (Start from **Architect lanes (Junyi sketch)** to load that page)
- After Save the designer writes `ORG_CHART.json` (source of truth) and generated `ORG_CHART.md`
- After Export it writes `ORG_SPAWN_BRIEF.md` for a CoS or architect. That file is not a hire.
