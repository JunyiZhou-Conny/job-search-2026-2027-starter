# What to paste into Cursor Automations UI (stable)

Paste **only** the block below into **Agent Instructions**.
Do not paste the full discovery rules into the UI again.

When rules change: edit `docs/automation/DAILY_JOB_DISCOVERY.md` (and
`knowledge/discovery_triage_rules.yaml` / `config/profile.yaml`), commit, push.
The UI pointer below should almost never need edits.

```text
Follow the canonical instructions in this repo — do not improvise a different workflow.

1. Read and obey ALL of:
   - docs/automation/DAILY_JOB_DISCOVERY.md
   - knowledge/discovery_triage_rules.yaml
   - config/profile.yaml
2. If anything in chat memory or an older pasted prompt conflicts with those files, the FILES win.
3. Execute the discovery + triage loop described in DAILY_JOB_DISCOVERY.md end-to-end for this run.
4. Write the required artifacts and reply in the Phase 5 report format from that file.
5. Do not submit applications, do not send outreach, and do not ingest into data/applications.csv unless the user explicitly confirms keeps in this run.
```

## Weekday apply review (separate Automation)

Do **not** mix this with daily discovery. Paste only if Junyi has created a
second Automation whose job is autofill review. Canonical file:
`docs/automation/WEEKDAY_APPLY_AUTOMATION.md`.

```text
Follow the canonical instructions in this repo — do not improvise a different workflow.

1. Read and obey ALL of:
   - docs/automation/WEEKDAY_APPLY_AUTOMATION.md
   - docs/automation/APPLY_HARNESS.md
   - config/profile.yaml
2. Run python3 scripts/automation/check_apply_harness.py first. Exit 1 → stop.
3. Open only rows Junyi already queued for autofill review. Chrome + Copilot only.
4. Never click Submit. Never use Greenhouse MyGreenhouse. Never invent essays. Never click Simplify Generate with AI.
5. Write free responses from knowledge/evidence_bank.yaml + knowledge/written_response_bank.yaml. Save drafts in docs/apply/written_answers/. Salary = page minimum else 90000. If how-heard is empty, click LinkedIn on the same Chrome.
6. If Copilot filled EEO, or work-auth/sponsorship looks wrong for an F-1 profile, block Submit and write the review row.
7. If anything in chat memory conflicts with those files, the FILES win.
```
