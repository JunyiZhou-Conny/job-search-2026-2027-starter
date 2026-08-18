# /check-apply-harness

Before opening ATS tabs for Simplify autofill:

```bash
python3 scripts/automation/check_apply_harness.py
```

- Exit 0: Copilot is in the computer-use browser. Autofill, then **stop before Submit**.
- Exit 1: Do not fake autofill. Read `docs/automation/APPLY_HARNESS.md` and tell the human which piece is missing (branded Chrome, no extension, session).

Never treat Greenhouse “Autofill my application” as Simplify. Never paste passwords into chat.
