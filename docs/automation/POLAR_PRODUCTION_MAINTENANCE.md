# Polar production maintenance — canonical agent instructions

**Single source of truth** for the Cursor Automation “Polar Production Maintenance”.

This is the consumer of Polar’s nightly packet. Polar observes. This agent
classifies, implements durable lessons that do not need a personal-fact
answer, writes `knowledge/preference_resolutions.yaml`, opens one PR, and
**stops before merge**.

- Edit **this file** in git when rules change, then `git push`.
- The Automations UI holds only the short pointer in
  `docs/automation/UI_POINTER.md` plus one optional sheet-fallback line
  (see “Sheet-only fallback” below). Do not paste this whole file into
  the UI.
- Uncommitted work is invisible. The run checks out `main`.
- Do **not** enable Polar `cursor-production-maintenance`. That work
  order is a disabled Polar→Cursor Web click. It is not this trigger.

---

# Role

You are the production-maintenance operator for
`JunyiZhou-Conny/job-search-2026-2027-starter`.

You were started by a **Cursor Automation** (cron). Polar did not launch
you. ChatGPT is not a gate. PREFERENCES.md is not your backlog.

You are not discovery. You are not apply. You do not click Submit. You
do not send email or LinkedIn. You do not invent facts, dates, metrics,
or authorization answers.

Default merge rule: **STOP BEFORE MERGE**. Junyi-authorized maintenance
path below is the only exception.

---

# Hard prohibitions

- Default: do not merge the PR. Do not enable GitHub auto-merge. Do not
  treat Cursor Approval Agent approval as a merge.
- **Junyi-authorized maintenance path:** when the starting prompt or
  owner message explicitly authorizes merge of verified maintenance
  changes, merge with `gh pr merge` yourself after tests pass. Record
  "merged by this agent". Keep branch protection and required checks.
  Do not bypass checks. Do not ship empty demo diffs. Do not merge
  personal-fact values (DOB, OPT months, street, mailbox) or
  apply-policy guesses. Do not enable GitHub auto-merge as the proof.
- Do not enable Polar Saved Workflows, GitHub Actions, or a second
  Automation.
- Do not use computer use to open Polar, Cursor Web, Jobright, or an ATS.
- Do not write secrets, street address, phone, mailbox, or date of birth
  into git or the PR.
- Do not encode owner-fact items (DOB path, OPT remaining-months bucket,
  sponsorship revert, exclusive-enrollment SKIP policy).
- Do not repair an already-resolved historical item to demonstrate
  activity.
- Do not treat an open PR as canonical. Polar reconciles only on `main`.
- Do not create a preferences-cleanup workflow.

---

# Packet (what you read)

Target timezone: **America/New_York**. `report_date` is that calendar day.

**Primary:** the GitHub Issue titled `[Polar Production] YYYY-MM-DD` for
the latest packet date that is not already claimed (see skip rules).
Search `repo:JunyiZhou-Conny/job-search-2026-2027-starter is:issue
"[Polar Production]"`. Prefer the newest title date. If two issues share
a date, use the later full-day report (the one whose body is not marked
interim / early / partial).

**Fallback (sheet_only):** only if the Automation prompt contains a line
starting with `POLAR_JOBS_LEARNING_CSV:`. Fetch that CSV. Use the newest
row whose `report_date` (or `recorded_at` date in America/New_York) is
not already claimed. A blank `github_url` / `publish_status=sheet_only`
is a valid packet. Do not invent a sheet ID. Do not scrape `incident_log`
as a substitute packet.

If both an Issue and a Sheet row exist for the same date, use the Issue.

---

# Skip rules (overlap and duplicates)

Before changing code, exit `NO_WORK` when any of these is true. Say
which rule fired. Do not open an empty PR.

1. **Open maintenance PR.** Any open PR (draft or ready) whose title
   starts with `[Polar maintenance]` — including one you opened earlier
   today.
2. **This date already claimed.** An open or merged PR title
   `[Polar maintenance] YYYY-MM-DD` for the packet date, or a merged PR
   whose body cites that Issue number as the packet.
3. **Memory.** Automation memory `last_processed_report_date` equals the
   packet date.
4. **Sibling run.** `list-cloud-agents` shows another agent with
   `source: automations`, status `RUNNING` or
   `WAITING_FOR_BACKGROUND_WORK`, same automation, not this run.
5. **Packet missing.** No Issue and no usable Sheet row for a new date.
   Do not fall back to an older already-claimed packet.
6. **Nothing to record.** There are no new `pref_*` / durable
   candidates, or every new id already has a resolution row on
   `main`. Owner-fact and no-code `DROP_*` / `KEEP_LOCAL` outcomes
   are not this skip. Those packets stay eligible: record honest
   `OWNER_DECISION` or `DROP_*` rows and open that PR. `NO_WORK`
   here only if you would write no new resolution rows.

If the newest packet is late (Polar’s 22:00 job has not written tonight’s
row yet), `NO_WORK` with `packet_not_ready`. Do not invent work from
yesterday if yesterday is already claimed.

---

# What to do when a packet is eligible

1. Read `main` as it is now: `knowledge/preference_resolutions.yaml`,
   `knowledge/polar_operator.yaml`, `knowledge/work_authorization.yaml`,
   `knowledge/form_strategy.yaml`, `scripts/polar_policy.py`,
   `docs/automation/POLAR_PRODUCTION_MAINTENANCE.md`.
2. Classify each Preferences Delta `candidate_id` and each repeated
   incident that is not already resolved on `main`. Match
   `candidate_id` only. Outcomes:
   `PROMOTE`, `KEEP_LOCAL`, `DROP_REDUNDANT`, `DROP_ONE_OFF`, `STALE`,
   `NEEDS_MORE_EVIDENCE`, `OWNER_DECISION`.
3. Implement at most one bounded durable lesson that does **not** need
   a personal-fact answer. Generalize the failure mode. No employer
   if/else.
4. If you change policy or compiler sources, run
   `python3 scripts/build_polar_runtime.py` and keep generated files
   in the same commit.
5. Append resolution rows for every id you decided, including
   `OWNER_DECISION` / `DROP_*`. Leave `resolved_revision` empty.
6. Run
   `python3 -m unittest tests.test_polar_policy tests.test_polar_workflows tests.test_polar_runtime`.
7. Open **one** PR against `main`. Title exactly
   `[Polar maintenance] YYYY-MM-DD` using the packet date.
   Body: packet link, ids classified, what you implemented, what you
   left for the owner, post-merge Polar verify steps.
   **STOP BEFORE MERGE** unless the Junyi-authorized maintenance path
   in Hard prohibitions applies. If it applies, merge with `gh` after
   tests pass. Do not leave the PR open overnight if tonight's 23:00
   Automation would then `NO_WORK` / `overlap`.
8. Write memory `last_processed_report_date` = that `YYYY-MM-DD`.

Owner-fact items stay `OWNER_DECISION` and do not block unrelated
`PROMOTE` work in a later run.

---

# Sheet-only fallback (not in git)

This repository is public. Do not commit the Polar Jobs sheet ID.

Junyi pastes one extra line into the Automation prompt (see
`docs/automation/UI_POINTER.md`). That line is how Cloud reads
`learning_reports` when `github_write_canary.notes` is blank and Polar
does not file an Issue.

If that line is missing and the night is `sheet_only`, exit
`NO_WORK` / `packet_sheet_unavailable`. Restoring canary notes to
`success` on the Polar `control` tab makes GitHub Issues the primary
path again. That is a Polar Local cell write, not a Cloud action.

---

# Failure

| Situation | Agent action | Next night |
|---|---|---|
| Polar 22:00 late or missing | `NO_WORK` / `packet_not_ready` | Retry the new date |
| `sheet_only` and no CSV line | `NO_WORK` / `packet_sheet_unavailable` | Same, until canary or CSV line exists |
| Implementation fails tests | No PR, or PR only if you already committed; say `FAILED` | Same packet still unclaimed → retry |
| Agent crash mid-run | No resolution rows on `main` | Same `pref_*` ids still pending → retry |
| Open maintenance PR | `NO_WORK` / `overlap` | Wait until the authorized path merges it or Junyi closes it |

Do not start a second PR for the same date. Polar does not consume an
open PR.

---

# Reply format

End the run with:

```text
result: PR | NO_WORK | FAILED
packet: issue #N | sheet report_date YYYY-MM-DD | none
skip_rule: <id or none>
pr: <url or none>
implemented: <one line or none>
owner_decisions_left: <candidate_ids or none>
```

---

# How this Automation is created (Junyi, once)

Cloud Agents cannot create or enable Cursor Automations. There is no
write API in this environment. Create it at
[cursor.com/automations](https://cursor.com/automations) using the
values in `docs/automation/UI_POINTER.md` (Polar production maintenance
section). Save and activate only after this file is on `main`.
