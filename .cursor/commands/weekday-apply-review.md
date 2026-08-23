# /weekday-apply-review

Read `docs/automation/WEEKDAY_APPLY_AUTOMATION.md` and
`docs/automation/APPLY_HARNESS.md`. Then:

```bash
python3 scripts/automation/check_apply_harness.py
```

- Exit 0: open only queued apply URLs in Chrome. Copilot once per form.
  Screenshot. **Stop before Submit.**
- Exit 1: stop. Do not fake-fill.

Never treat Greenhouse “Autofill my application” as Simplify.
If Copilot filled EEO or work-auth looks wrong for F-1, block Submit and
write the review row. Do not invent essays.
