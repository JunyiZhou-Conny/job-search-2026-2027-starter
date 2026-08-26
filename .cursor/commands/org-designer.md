# /org-designer

Open the visual Grok Bot org designer. Junyi designs the tree. The page does not hire Bots.

```bash
python3 scripts/serve_org_designer.py
```

Then open `http://127.0.0.1:8766/` — not the apply queue on :8765.

## What the page writes

| Action | Writes |
|---|---|
| Save charter | `docs/grok-bot-management/ORG_CHART.json` (source of truth) and generated `ORG_CHART.md` |
| Export brief | `docs/grok-bot-management/ORG_SPAWN_BRIEF.md` when the chart is complete, and copies the paste |

It does not write `GROK_BOT_HANDOFF.md` or `ORG_CHART_BLANK.md`. It does not Submit.

## Tests

```bash
python3 tests/test_org_designer.py
```
