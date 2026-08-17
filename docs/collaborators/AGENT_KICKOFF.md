# Paste this into a Cursor Cloud Agent (or local Agent)

Use this on **your private fork**, after GitHub + Cursor are connected. Do not run the
write-reset on the upstream template repo.

Copy everything below the line.

---

You are setting up a **personal copy** of the job-search toolkit in this repository.

## Read first, in this order

1. `docs/collaborators/SETUP.md` — follow it as the runbook. Do not improvise a different workflow.
2. `docs/FRIENDS_CANVAS.md` — shared vs personal files.
3. `docs/CONTRIBUTING.md` — what may go upstream.
4. `AGENTS.md` and `docs/BOUNDARIES.md` — truth, eligibility, no auto-submit.

## Mode

Ask the human which mode they want if they have not already said:

- **Mode A — personal job search (default):** fork, replace identity, own Simplify, own Cloud Agents / Automation.
- **Mode B — engine contributor only:** do not wipe ledgers; do not replace identity; only improve scripts/docs.
- **Mode C — help operate someone else's search:** do **not** log into their Simplify; do **not** write their applications; help on engine/docs only.

If they said they want to use this system for their own applications, that is Mode A.

## Hard rules

- Never invent skills, dates, metrics, sponsorship facts, graduation dates, or application outcomes.
- If a fact is missing, ask the human or write `unknown`. Do not guess.
- Do not submit applications, send LinkedIn/email, or claim an action was completed unless the human confirms.
- Do not paste or commit passwords, cookies, 2FA codes, passport/SEVIS/SSN/EAD scans, or session JSON.
- Do not keep Junyi Zhou’s identity, applications, contacts, or resume as if they were the collaborator’s.
- Do not open a PR into upstream that contains the collaborator’s profile, resumes, evidence bank, or ledger.
- Sponsorship unknown/no is not hard ineligibility.

## Execute Mode A in this order

### Phase 0 — prove the checkout

1. Run `git remote -v` and `git status`.
2. If `origin` is `JunyiZhou-Conny/job-search-2026-2027-starter`, **stop**. Tell the human to fork, clone the fork, add `upstream`, and reopen the agent on the fork.
3. Confirm `docs/collaborators/SETUP.md` exists.

### Phase 1 — reset identity (only on a personal fork)

```bash
python3 scripts/init_personal_copy.py
python3 scripts/init_personal_copy.py --i-am-on-a-personal-fork --write
```

If the script refuses because origin is upstream, stop. Do not `--write` on the template repo.

### Phase 2 — facts interview (required before filling files)

Ask the human the questions in `docs/collaborators/SETUP.md` §6. Wait for answers. Do not fill `REPLACE_ME` with invented values.

### Phase 3 — write identity files from confirmed facts only

Fill:

- `config/profile.yaml`
- `knowledge/work_authorization.yaml`
- `knowledge/evidence_bank.yaml` (sparse is fine; empty + honest is better than a fake full bank)
- `knowledge/discovery_triage_rules.yaml` → `profile_anchors` only
- `docs/automation/DAILY_JOB_DISCOVERY.md` → candidate profile block only (fork-local; never PR this rewrite upstream)
- `data/outreach_templates.csv` placeholders (`{school_short}`, `{grad_short}`, `{topic_self}`)

Leave shared engine files alone (`scripts/`, `knowledge/careers_boards.yaml`, triage *guide_rules*).

### Phase 4 — resumes

If the human provides a resume (`.tex`, `.pdf`, or bullet list):

- Put the source of truth in `resumes/base/`
- Do not copy Junyi’s bullets
- Register versions in `data/resume_versions.csv` only for files that exist
- Compile only if `latexmk` is available; otherwise say so

If they have no resume yet, leave `resumes/` as a TODO in `generated/collaborator_setup_status.md`.

### Phase 5 — verify

```bash
python3 scripts/init_personal_copy.py --check
python3 scripts/validate_data.py
```

`--check` may still fail on `docs/eligibility.md` / `DAILY_JOB_DISCOVERY.md` until those identity blocks are rewritten. Fix or list them. Do not “fix” by deleting shared policy text that is not identity-specific.

Update `generated/collaborator_setup_status.md` with what is done vs blocked.

### Phase 6 — human-only Cursor + Simplify (you cannot click their dashboards)

Stop and give them the exact click-path checklist from SETUP.md §8–§10:

- Simplify account + Copilot + profile filled from **their** evidence bank
- Cursor → Integrations → GitHub, with **this fork** selected
- Cloud Agents → Environments → attach **this fork**
- Secrets in the Cloud Agents dashboard or local `secrets/.env` (they type secrets; you never ask them to paste passwords into chat)
- Automations → private Daily Job Discovery on **this fork**, instructions from `docs/automation/UI_POINTER.md`

### Phase 7 — first smoke test (no submit)

If a triage CSV already exists (even an upstream example day):

```bash
python3 scripts/resolve_apply_url.py --date YYYY-MM-DD --write-csv
python3 scripts/serve_apply_queue.py --date YYYY-MM-DD
```

Tell them to open `http://127.0.0.1:8765/`. Do not tick Applied unless they applied. Do not click Submit on any ATS.

## Final reply format

1. Mode used
2. What you changed (paths)
3. What is still `unknown` / blocked on the human
4. Exact next action for the human (one concrete step)
5. Reminder: their Daily Discovery automation must read **their** `config/profile.yaml`, not Junyi’s dates
