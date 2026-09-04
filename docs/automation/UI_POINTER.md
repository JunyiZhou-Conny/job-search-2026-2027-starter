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
4. Stamp every artifact with the UTC run stamp RUN=YYYY-MM-DDTHH from Phase 0. Never reuse a day-keyed name.
5. Deliver per the "Delivery" section of that file: commit on the automation/discovery branch after running scripts/automation/normalize_careers_boards.py, merge the branch tip, push. Do not open a PR against main.
6. Write the required artifacts and reply in the Phase 5 report format from that file.
7. Do not submit applications, do not send outreach, and do not ingest into data/applications.csv unless the user explicitly confirms keeps in this run.
```

Both Automations ("Daily Job Discovery Morning" at 09:00 and "Daily Job
Discovery Evening" at 18:00 America/New_York) share this block. They commit
to one branch, `automation/discovery`, so their output accumulates instead of
producing one PR per run. If a run still opens a `cursor/*` PR against
`main`, turn off PR creation in that Automation's settings; the branch is the
delivery path.

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
