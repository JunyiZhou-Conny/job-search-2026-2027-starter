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

## Polar production maintenance (separate Automation)

Do **not** mix this with daily discovery or weekday apply. Create it only
after `docs/automation/POLAR_PRODUCTION_MAINTENANCE.md` is on `main`.

UI fields (match Daily Job Discovery, except the schedule and this
pointer):

| Field | Value |
|---|---|
| Name | `Polar Production Maintenance` |
| Trigger | Scheduled. Custom cron `0 23 * * *`. Timezone **America/New_York** (same control the 09:00 / 18:00 discovery Automations already use). |
| Repository | `JunyiZhou-Conny/job-search-2026-2027-starter` |
| Branch | `main` |
| Permission | **Private** |
| Pull request creation | **On** (default). This Automation must open a PR. Do not reuse the discovery “turn PR creation off” setting. |
| Computer use | Leave default. The instruction file forbids using it for Polar or Cursor Web. |
| Memories | Leave on. The agent writes `last_processed_report_date`. |
| MCP | Same GitHub connection already used by Daily Job Discovery. No Google Sheets MCP. |

If the UI cron is UTC-only (no timezone dropdown), do **not** paste
`0 23 * * *`. Use `0 3 * * *` while America/New_York is on EDT. After
the 2026-11-01 fallback to EST, change that UTC cron to `0 4 * * *`.
Prefer the timezone dropdown if it exists — discovery already fires at
09:02 / 18:03 ET, so that control is the proven one.

Agent Instructions — paste **only** this block, then the optional CSV
line:

```text
Follow the canonical instructions in this repo — do not improvise a different workflow.

1. Read and obey docs/automation/POLAR_PRODUCTION_MAINTENANCE.md.
2. If anything in chat memory or an older pasted prompt conflicts with that file, the FILE wins.
3. You were started by this Cursor Automation. Polar did not launch you. ChatGPT is not a gate.
4. Process the latest Polar production packet that is not already claimed. Implement at most one durable lesson that does not need a personal-fact answer. Write preference_resolutions.yaml. Compile Polar runtime if you change compiler sources. Open one PR titled [Polar maintenance] YYYY-MM-DD. STOP BEFORE MERGE.
5. If a [Polar maintenance] PR is already open, or the packet is missing, exit NO_WORK. Do not open an empty PR.
6. Do not submit applications, send outreach, merge, or enable other workflows.
```

Optional last line (needed on `sheet_only` nights; do **not** commit this
URL to git — the repo is public):

```text
POLAR_JOBS_LEARNING_CSV: <paste the public learning_reports gviz CSV URL Junyi already uses for Polar Jobs>
```

