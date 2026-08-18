# /check-apply-harness

Before opening ATS tabs for Simplify autofill:

```bash
python3 scripts/automation/check_apply_harness.py
```

- Exit 0: Copilot (publisher signals) + a Simplify session are in the computer-use browser. Autofill, then **stop before Submit**.
- Exit 1: Do not fake autofill. Read `docs/automation/APPLY_HARNESS.md` and tell the human which piece is missing (Copilot vs session vs wrong profile).

A Chrome folder id is the extension package, not the person. `identity_match` is separate and usually `unknown`. Confirm the dashboard name against `config/profile.yaml`.

Never treat Greenhouse “Autofill my application” as Simplify. Never paste passwords into chat. Never print cookie values.
