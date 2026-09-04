# AI triage pack — 2026-09-03

- Rows: **134**
- Input CSV: `generated/discovery_for_triage_2026-09-03.csv`
- Rules: `knowledge/discovery_triage_rules.yaml`
- Profile: `config/profile.yaml`

## Agent task

1. Read the rules YAML (guide_rules) — do not invent new hard gates.
2. Read every row of the input CSV (board fields only unless ambiguous).
3. Write:
   - `generated/discovery_triage_2026-09-03.csv`
   - `generated/discovery_triage_2026-09-03.md`
4. Leave `user_confirm` empty. Do not edit `data/applications.csv`.

In Cursor: run `/triage-discovery` or ask the agent to triage this pack.
