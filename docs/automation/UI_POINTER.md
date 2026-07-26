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
