# Collaborator setup — agent-executable runbook

**Audience:** a friend or future collaborator, and **their** Cursor agent.  
**Last updated:** 2026-08-17  
**Upstream template:** `JunyiZhou-Conny/job-search-2026-2027-starter`

This is the long setup guide. If you are a human, read §1–§4 once, then give
[`AGENT_KICKOFF.md`](./AGENT_KICKOFF.md) to your Cursor agent (Cloud or local).
In Cursor you can also run **`/collaborator-setup`**.

Related docs (do not duplicate them here):

| Doc | Use when |
|---|---|
| [`docs/FRIENDS_CANVAS.md`](../FRIENDS_CANVAS.md) | What is shared vs personal; current progress |
| [`docs/CONTRIBUTING.md`](../CONTRIBUTING.md) | What belongs in an upstream PR |
| [`docs/platforms.md`](../platforms.md) | Simplify vs this repo vs Jobright |
| [`docs/BOUNDARIES.md`](../BOUNDARIES.md) | Labels, skills-in-files, automations, secrets |
| [`docs/automation/UI_POINTER.md`](../automation/UI_POINTER.md) | Exact text to paste into a Cursor Automation |
| [`docs/automation/DAILY_JOB_DISCOVERY.md`](../automation/DAILY_JOB_DISCOVERY.md) | What the daily automation actually does |
| [`docs/eligibility.md`](../eligibility.md) | Hard eligibility ≠ sponsorship (rewrite dates on a fork) |

---

## 1. What you are setting up

This repository is a **strategy and memory layer** around Simplify. It is not a
second job board and not a multi-user ATS.

```text
Overnight:  Cursor Automation scrapes intern + new-grad boards → triage CSV
Your hour:  Apply Queue → employer ATS → Simplify autofill → YOU click Submit
Weekly:     Simplify CSV export → import-simplify → dashboard
```

Three layers stay separate:

| Layer | Tool | Owns |
|---|---|---|
| Discovery | Jobright boards / LinkedIn / Handshake / career pages | “What roles exist?” |
| Execution + base ledger | **Your** Simplify account | Company, role, URL, date applied, base status |
| Strategy | **Your fork** of this repo | Resume version, pursuit lane, sponsorship signal, auth Q&A, networking, next action |

**Rule of thumb:** collaborate on the *engine* (scripts, docs, board maps). Keep
*identity and applications* personal.

One shared `data/applications.csv` does **not** scale to multiple people. One
Cloud Agent must **not** submit from one shared Simplify login for several people.

---

## 2. Choose a mode (do this first)

### Mode A — personal job search (default)

You want the same pipeline for **your** applications.

- Private **fork**
- Your Simplify, filled with **your** facts
- Your Cursor Pro (or higher) + your Cloud Agents + your Automation
- Your `config/profile.yaml`, evidence bank, resumes, ledger

### Mode B — engine contributor only

You want to fix scripts, the apply queue, resolver coverage, or docs.

- Fork or branch is fine
- **Do not** run the identity reset
- **Do not** replace Junyi’s profile with yours on a PR back to upstream
- Open small PRs into upstream (`scripts/`, `docs/`, shared `knowledge/careers_boards.yaml`, tests)

### Mode C — help operate someone else’s search

You are helping Junyi (or another owner) run *their* search.

- You may review PRs, watch a Cloud Agent **if you are on the same Cursor Team**, and improve the engine
- You must **not** log into their Simplify
- You must **not** write their `data/applications.csv` as if you were them
- You must **not** click Submit on their applications unless they are present and ask you to

If the human has not chosen, the agent asks. “Set this up so I can apply to jobs”
is Mode A.

---

## 3. Can we work as a team? (Cursor Pro vs Teams)

**Yes, as a Git team. Not as one shared Cursor + Simplify account.**

Two people on **Cursor Pro** can both run Cloud Agents on the same GitHub repo
(or on two forks). They share work with branches and pull requests. Pro includes
Cloud Agents and Automations.

Two standalone Pro accounts **cannot**:

- Open each other’s Cloud Agent run (chat, diffs, Take Control)
- Share Automations, secrets, or saved environments as Cursor objects
- Share editor chat transcripts

Those in-product sharing features require a **Cursor Team**
([team setup](https://cursor.com/docs/account/teams/setup.md)). Teams is a
separate paid plan. Joining a team **cancels** an individual Pro subscription,
and one Cursor account can only belong to one team.

**Recommendation for this toolkit:** stay on two Pro accounts. Share via GitHub.
Create a Cursor Team only if you keep needing to sit inside the same live agent.

Official starting points:

- Cloud Agents: [cursor.com/agents](https://cursor.com/agents)
- Environments: [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents)
- Automations: [cursor.com/automations](https://cursor.com/automations)
- GitHub integration: [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations)
- Docs: [Cloud Agents](https://cursor.com/docs/cloud-agent.md), [Setup](https://cursor.com/docs/cloud-agent/setup.md), [Automations](https://cursor.com/docs/cloud-agent/automations.md)

---

## 4. Hard rules (human and agent)

1. **Never invent.** Skills, dates, metrics, sponsorship, graduation, referrals, and
   application outcomes are either confirmed, `unknown`, or omitted.
2. **Never submit or send** without the applicant’s explicit confirmation.
3. **Never commit secrets.** No passwords, cookies, `storage_state` JSON, 2FA codes,
   passport / SEVIS / SSN / EAD / visa scans, or ATS passwords.
4. **Sponsorship unknown/no is not a hard reject.** Do not mark a role `ineligible`
   for sponsorship reasons alone. See `docs/eligibility.md`.
5. **`label_source=manual` is not auto-overwritten.**
6. **Files beat chat memory.** Profile, evidence bank, and triage rules in git are
   the source of truth.
7. **Do not copy the template owner’s identity.** The files on `main` belong to
   Junyi Zhou until a personal fork replaces them.
8. **Daily Discovery on a fork must use that fork’s `config/profile.yaml`.** If you
   leave Junyi’s dates in place, the automation will triage for Junyi.

---

## 5. Human-only prerequisites (an agent cannot finish these)

Do these in a browser, signed in as **yourself**. The agent should list them and
wait. It must not ask you to paste passwords into chat.

### 5.1 Accounts

- [ ] GitHub account
- [ ] Cursor account on a **paid** plan (Pro is enough; Hobby cannot run Cloud Agents)
- [ ] Simplify account at [simplify.jobs](https://simplify.jobs) — **yours**, not a shared login
- [ ] Chrome or Chromium with the **Simplify Copilot** extension, logged into your Simplify

Optional later: Jobright account (personalized Matches). Public intern / new-grad
boards work without it.

### 5.2 GitHub: private fork (Mode A)

1. Open `https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter`
2. **Fork** → create a **private** fork (recommended; the template contains a real
   person’s ledger and resume)
3. Clone **your fork**:

```bash
git clone git@github.com:<YOU>/job-search-2026-2027-starter.git
cd job-search-2026-2027-starter
git remote add upstream git@github.com:JunyiZhou-Conny/job-search-2026-2027-starter.git
git remote -v
```

`origin` must be **your** GitHub user/org. `upstream` is the template.

If you only have collaborator access on the original repo and no fork, **do not**
run the identity reset. You would wipe the owner’s ledger. Use Mode B or C, or
fork first.

### 5.3 Cursor ↔ GitHub

1. Open [cursor.com/dashboard/integrations](https://cursor.com/dashboard/integrations)
2. Connect GitHub with **your** GitHub user
3. Grant the Cursor GitHub App access to **the fork** (Selected repositories is fine)
4. You need **read-write** on that repo. Cloud Agents cannot push without it.

Cloud Agents only reach repositories the triggering user can already reach. Cursor
does not widen GitHub access.

### 5.4 Open the fork in Cursor

Either:

- **Local:** `File → Open Folder` on the clone, then Agent chat or `/collaborator-setup`
- **Cloud:** [cursor.com/agents](https://cursor.com/agents) → New agent → repository =
  **your fork** → branch `main` (or a setup branch) → paste [`AGENT_KICKOFF.md`](./AGENT_KICKOFF.md)

Spend limit: the first Cloud Agent run asks you to set one. Usage is billed against
your Pro (and overage) pool.

---

## 6. Facts interview (required before any identity file is written)

The agent asks. The human answers. The agent writes `unknown` when the human does
not know. **Do not infer from Junyi’s files.**

### Identity

1. Legal name, preferred name
2. Email, phone, city
3. LinkedIn URL, GitHub URL
4. School, degree
5. Program-end / I-20 / “graduation” date (the date that means “requirements complete”)
6. Commencement / ceremony date, if it is a **different real date**. If you only have
   one date, say so — do not invent a second one
7. Earliest date you can start full-time work
8. Internship target (for example Summer 2027) or “internships not in scope”

### Work authorization (non-sensitive only)

9. Current status (US citizen, LPR, F-1, other — as you are willing to store in git)
10. After graduation, what work auth do you expect (none needed, OPT, STEM OPT, other)?
11. Will you need **employer sponsorship in the future** (typically H-1B)? Yes / no / unknown
12. Any hard location or remote rule? This template defaults to **no fully remote**

Do **not** put passport numbers, SEVIS IDs, SSN, EAD images, or visa scans in the repo.

### Search shape

13. Role clusters you actually want: `cloud_swe` / `data_ml` / `health_ai` / other
14. Preferred cities
15. Hours per weekday you will really spend
16. Whether you already have a resume (paste, attach, or “not yet”)

### Evidence

17. For each job or project you want on a resume: title, org, dates, 2–5 bullets you
    can defend in an interview, and any **measured** result you can point to
18. Skills you want tagged in Simplify — only ones you can talk about

The agent may read a resume or public GitHub repo the human points at. It may **not**
upgrade “I used X once” into a strong verified skill, and it may not invent metrics.

---

## 7. Agent phases (Mode A)

### Phase 0 — prove the checkout

```bash
git remote -v
git status
git branch --show-current
```

Stop if `origin` is `JunyiZhou-Conny/job-search-2026-2027-starter`.

### Phase 1 — reset the template owner’s identity

Dry-run first (prints the plan, writes nothing):

```bash
python3 scripts/init_personal_copy.py
```

Then apply, only on a personal fork:

```bash
python3 scripts/init_personal_copy.py --i-am-on-a-personal-fork --write
```

What this does:

- Copies blank templates over `config/profile.yaml`, `knowledge/work_authorization.yaml`,
  `knowledge/evidence_bank.yaml`, `data/outreach_templates.csv`
- Resets personal ledgers to **header-only**:
  `applications.csv`, `activity_log.csv`, `job_decisions.csv`, `contacts.csv`,
  `networking.csv`, `networking_interactions.csv`, `networking_experiments.csv`,
  `resume_versions.csv`
- Writes `generated/collaborator_setup_status.md`
- Copies the previous files to `data/backups/personal-reset-<timestamp>/` (gitignored)

What this does **not** do:

- It will not run if `origin` is the upstream template
- It does not delete `scripts/`, shared board maps, or historical `generated/discovery_triage_*.csv`
  (those CSVs are useful examples; they are not your ledger)
- It does not delete `resumes/base/JZ_resume.tex` — you replace that in Phase 4
- It does not rewrite `docs/automation/DAILY_JOB_DISCOVERY.md` or
  `knowledge/discovery_triage_rules.yaml` `profile_anchors` (the agent does that after the interview)

### Phase 2 — fill identity files

Replace every `REPLACE_ME` / `unknown` you now know. Leave the rest `unknown`.

| File | What “done” looks like |
|---|---|
| `config/profile.yaml` | Your name, links, dates, tracks, remote rule |
| `knowledge/work_authorization.yaml` | Non-sensitive auth answers only |
| `knowledge/evidence_bank.yaml` | Your projects/skills; `verified` + `resume_eligible` only when true |
| `knowledge/discovery_triage_rules.yaml` | `profile_anchors` match **your** dates and remote rule. Leave `guide_rules` shared |
| `docs/automation/DAILY_JOB_DISCOVERY.md` | Candidate block matches your profile. **Fork-local only — do not PR this rewrite** |
| `data/outreach_templates.csv` | `{school_short}`, `{grad_short}`, `{topic_self}` are yours |

`docs/eligibility.md` and some `.cursor/rules/*.mdc` files still mention the
template owner’s dates. On a personal fork, either rewrite the date examples to
yours or treat those files as *policy examples* and make `config/profile.yaml`
win. Do not send those identity rewrites upstream.

### Phase 3 — resumes

Preferred layout (same as the template):

```text
resumes/base/<your>_resume.tex     ← source of truth
resumes/cloud_swe/                 ← generated cluster
resumes/data_ml/
resumes/health_ai/
data/resume_versions.csv           ← registry of versions that actually exist
```

```bash
python3 scripts/build_clusters.py           # after base exists and clusters are configured
./scripts/compile_resume.sh                 # needs latexmk / TeX Live
```

If you do not have TeX yet, keep a PDF the human already uses and record that
filename in `data/resume_versions.csv`. Do not register Junyi’s `JZ_resume` as yours.

Quality rules (also in `.cursor/rules/20-resume-tailoring.mdc`):

- No invented tools, ownership, scale, or metrics
- Cluster = same facts, different order / emphasis
- Edit base, then regenerate clusters — do not hand-edit generated cluster `.tex`

### Phase 4 — local secrets (optional until you automate a browser)

```bash
cp secrets/.env.example secrets/.env
```

Put `SIMPLIFY_EMAIL` in `.env` **on disk**. Prefer a saved session over storing a
password if 2FA is on (`scripts/automation/save_simplify_session.py`).

For Cloud Agents, add the same keys in the **Cloud Agents → Secrets** tab for
**your** environment. Secrets are not copied from anyone else’s Cursor account.
Never commit `.env` or `secrets/simplify_storage.json`.

### Phase 5 — verify

```bash
python3 scripts/init_personal_copy.py --check
python3 scripts/validate_data.py
```

`--check` fails if these still contain template-owner strings: `Junyi Zhou`,
`JunyiZhou-Conny`, the template LinkedIn slug, or the template phone number.

Update checkboxes in `generated/collaborator_setup_status.md`.

---

## 8. Simplify setup (your account, your facts)

Simplify is the **application ledger of record**. Autofill is only as good as the
profile.

### 8.1 Create and log in

1. Create an account at [simplify.jobs](https://simplify.jobs) with **your** email
2. Install **Simplify Copilot** in Chrome / Chromium
3. Confirm the extension is logged into the same account

### 8.2 Fill the profile (human in the loop)

Minimum:

- Name, email, phone, LinkedIn, GitHub
- Education (real school, degree, dates)
- Work / project history that matches the evidence bank
- Skills as individual tags (paste in batches)
- Work-authorization answers that are **true for you**

The agent may generate a paste-ready markdown file from **your**
`knowledge/evidence_bank.yaml` + resume, similar in *shape* to
`generated/simplify_profile_2026-07-30.md`. It must **not** reuse that file’s
content — that file is Junyi’s identity.

If a skill is not in your evidence bank, do not add it to Simplify “to look complete.”

### 8.3 How this repo talks to Simplify

One-way only:

```text
You apply (Simplify autofill + you click Submit)
  → Simplify tracker
  → you export CSV
  → data/imports/simplify/YYYY-MM-DD.csv
  → python3 scripts/jobsearch.py import-simplify --file ...
```

In Cursor, dropping a CSV is `/sync-simplify`.

Expected columns (aliases are OK): Company, Title, URL, Status, Date Applied, Location, Notes.

Never build a bidirectional sync. Missing from Simplify ≠ delete local keeps.

---

## 9. Cursor Cloud Agents (Pro)

### 9.1 Environment

1. Open [Cloud Agents → Environments](https://cursor.com/dashboard/cloud-agents#environments)
2. Connect the **fork** (not only the upstream template, unless you are Mode B/C)
3. Let the setup agent install what it can, or add a repo
   `.cursor/environment.json` later so both of you get the same install
4. This repo does not currently ship a committed `environment.json`. Python 3 +
   the scripts in `scripts/` are enough for the apply queue and validators.
   Playwright is only needed for browser automation (`requirements-automation.txt`)

Environment resolution order (official):

1. `.cursor/environment.json` in the repo
2. Your personal saved environment
3. A team saved environment (Teams only)

Each Cloud Agent is an isolated VM. It cannot see another agent’s disk.

### 9.2 Secrets

In the environment Secrets tab (or local `secrets/.env`):

| Key | Purpose |
|---|---|
| `SIMPLIFY_EMAIL` | Your login email |
| `SIMPLIFY_PASSWORD` | Avoid if 2FA; prefer a session file you create locally |
| `SIMPLIFY_TRACKER_URL` | Usually `https://simplify.jobs/dashboard` |
| `JOBRIGHT_URL` | Optional Matches page |

Do not paste these values into the agent chat. Tell the agent “secrets are in the
dashboard” and move on.

### 9.3 What a Cloud Agent is allowed to do here

Allowed: discover, triage, resolve apply URLs, draft resumes from the evidence
bank, open ATS pages, **autofill and stop**, write local CSVs, open PRs on your fork.

Forbidden unless you say so in that same run: click Submit, send outreach, ingest
keeps into `applications.csv`, overwrite `label_source=manual`.

Computer use (a real browser on the VM) is how the autofill trials work. Captchas,
email verification, and “Sign up to apply” walls still need a human.

---

## 10. Daily Job Discovery automation (your fork)

`.cursor/rules` and `.cursor/commands` are **not** timers. The overnight run is a
**Cursor Automation**.

1. Open [cursor.com/automations](https://cursor.com/automations)
2. Create an automation (name it e.g. `Daily Job Discovery`)
3. Trigger: weekday cron in `America/New_York` (pick a morning you will actually review)
4. Repository: **your fork**, branch `main` (committed files only — uncommitted work is invisible)
5. Permission: **Private** (Pro). Team Visible / Team Owned need a Cursor Team
6. Agent instructions: paste **only** the block in
   [`docs/automation/UI_POINTER.md`](../automation/UI_POINTER.md)
7. Enable tools you want (PR creation is on by default; that is how the template
   owner’s runs land triage on `main`)
8. Save and activate

The automation will read `docs/automation/DAILY_JOB_DISCOVERY.md`,
`knowledge/discovery_triage_rules.yaml`, and `config/profile.yaml`. If those still
describe Junyi, the keeps will be Junyi’s keeps.

Your Pro automation is **not** the same object as anyone else’s. Recreate it on
your account. Usage bills to you.

After a run you should see:

- `data/discovery/YYYY-MM-DD_all.csv`
- `generated/discovery_triage_YYYY-MM-DD.csv`
- `generated/discovery_triage_YYYY-MM-DD.md`
- `jobs/inbox/daily-YYYY-MM-DD.md`

It must **not** ingest into `applications.csv` unless that run’s user message
explicitly says to.

---

## 11. First smoke test (do not submit)

You can practice the apply queue on an existing triage day while you wait for
your own automation (those CSVs are discovery, not Junyi’s private tracker):

```bash
# pick a date that exists under generated/discovery_triage_YYYY-MM-DD.csv
python3 scripts/resolve_apply_url.py --date 2026-08-16 --write-csv
python3 scripts/serve_apply_queue.py --date 2026-08-16
```

Open **`http://127.0.0.1:8765/`**, not the static HTML file.

| Button | Writes | Does not |
|---|---|---|
| Open | Browser to `apply_url` if resolved, else discovery URL | Submit |
| Applied | `data/applications.csv` (`status=applied`) | Talk to the employer |
| Pass | `data/job_decisions.csv` + `status=passed` | Talk to the employer |

Jobright “Apply” is often a signup wall. The resolver adds employer Greenhouse /
Ashby / Workday links when it can (`knowledge/careers_boards.yaml`). Weak matches
leave `apply_url` blank on purpose.

When you really apply: Simplify autofill → you review essays / EEO / work auth →
**you** click Submit → tick Applied in the queue → later `/sync-simplify`.

---

## 12. Daily loop after setup

**Overnight.** Automation writes today’s triage pack.

**Your hour.**

```bash
python3 scripts/serve_apply_queue.py --date $(date +%F)
```

**Weekly.**

```bash
# after you drop a Simplify export at data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python3 scripts/dedupe_applications.py
python3 scripts/validate_data.py
python3 scripts/refresh_resume_stats.py
python3 scripts/jobsearch.py dashboard
```

Useful Cursor commands on a configured copy: `/apply-queue`, `/triage-discovery`,
`/sync-simplify`, `/label-job`, `/validate-data`, `/weekly-review`, `/tailor-resume`.

---

## 13. Staying in sync with the template (and helping)

```bash
git fetch upstream
git merge upstream/main    # or rebase
```

Expect merge noise in `config/profile.yaml` and `data/applications.csv` if you
personalized them. **Keep yours.** Take engine changes from `scripts/`, `docs/`,
`static/`, `knowledge/careers_boards.yaml`, `knowledge/discovery_triage_rules.yaml`
*guide_rules*.

To help everyone else:

1. Branch on your fork
2. Change only shared engine / docs / tests
3. Open a PR into `JunyiZhou-Conny/job-search-2026-2027-starter`
4. Never include your profile, resumes, evidence bank, ledger, or secrets

Good first PRs: one verified employer in `knowledge/careers_boards.yaml`, an apply
queue bug, a doc fix, a Workday mapping with a 200-proof URL.

Issue title convention: `friend-help: …`

---

## 14. File map

### Must become yours (Mode A)

| Path | Why |
|---|---|
| `config/profile.yaml` | Agents read this first for name, dates, tracks |
| `knowledge/work_authorization.yaml` | Non-sensitive auth |
| `knowledge/evidence_bank.yaml` | Only verified + resume_eligible skills go on new bullets |
| `knowledge/discovery_triage_rules.yaml` → `profile_anchors` | Otherwise daily triage uses the template owner’s dates |
| `docs/automation/DAILY_JOB_DISCOVERY.md` candidate block | Same; fork-local |
| `resumes/` + `data/resume_versions.csv` | What you actually upload |
| `data/applications.csv` and the other ledgers | Your tracker |
| `data/outreach_templates.csv` | Must not say you are someone else |

### Must not be committed

| Path | Why |
|---|---|
| `secrets/.env`, `secrets/*storage*.json` | Logins |
| `data/backups/` | Reset copies; gitignored |
| ID images, EAD scans, passport / SEVIS | Data-safety rule |

### Shared engine (improve via upstream PR)

| Path | Why |
|---|---|
| `scripts/` | CLI, queue, resolver, discovery |
| `static/apply_queue/`, `templates/apply_queue/` | Queue UI |
| `knowledge/careers_boards.yaml` | Employer ATS map |
| `knowledge/company_lists.yaml` | Shared company classes |
| `knowledge/discovery_triage_rules.yaml` → `guide_rules` | Shared keep/later/skip policy |
| `docs/` except identity rewrites | Policy and how-tos |
| `.cursor/rules/`, `.cursor/commands/` | Agent behavior |
| `tests/` | Guardrails |

---

## 15. Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `init_personal_copy.py` refuses to write | `origin` is the upstream template | Fork, clone the fork, add `upstream` |
| `--check` still fails | Candidate block / eligibility / `JZ_resume.tex` still named Junyi | Rewrite or replace those files on the fork |
| Daily keeps look like Junyi’s constraints | `profile.yaml` or `profile_anchors` not updated | Fix files, commit, push; automation sees only `main` |
| Automation did nothing new | Ran against stale `main`, or no environment | Confirm repo + branch; check the automation run log |
| Cloud Agent cannot push | GitHub App missing the fork, or no write access | Integrations → Selected repos → include the fork |
| Cannot open a friend’s agent URL | Two Pro accounts, not a Cursor Team | Review the PR on GitHub instead, or create a Team |
| Jobright Apply is a signup wall | Expected | Run `resolve_apply_url.py`; apply on the employer ATS |
| Agent asks for your password | Agent is off-script | Refuse; put secrets in `.env` or the dashboard |
| `validate_data.py` fails after reset | Empty ledger is OK; leftover Junyi rows are not | Confirm applications.csv is header-only before you apply |
| latexmk missing | Cloud / laptop has no TeX | Skip compile; use an existing PDF; say so in status |
| Friend and you edited the same ledger | You are not on separate forks | Stop; split into forks; do not merge application rows |

---

## 16. Done checklist

Setup is done when **all** of these are true:

- [ ] `origin` is the collaborator’s fork; `upstream` is the template
- [ ] `config/profile.yaml` has the collaborator’s name and dates (no `REPLACE_ME` for name)
- [ ] `python3 scripts/init_personal_copy.py --check` is clean **or** the only hits are
      documented shared-doc examples the collaborator chose to leave
- [ ] `python3 scripts/validate_data.py` exits 0
- [ ] Simplify Copilot is installed and the profile matches the evidence bank
- [ ] Cursor GitHub integration includes the fork
- [ ] A Cloud Agent environment exists for the fork
- [ ] A **private** Daily Job Discovery automation points at the fork and uses
      `docs/automation/UI_POINTER.md`
- [ ] The human has opened the apply queue once and understands Applied ≠ Submit
- [ ] `generated/collaborator_setup_status.md` reflects reality

One concrete next action after that: run discovery for today **or** serve the
newest triage date and review five keeps without submitting.

---

## 17. Agent implementation notes

- Prefer `scripts/init_personal_copy.py` over hand-deleting CSV rows.
- When filling YAML, keep comments that explain dual dates / unknown.
- Do not “helpfully” copy Junyi’s projects into an empty evidence bank.
- Do not open an upstream PR as part of setup.
- If the human is Mode B, skip Phases 1–4 and point them at `docs/CONTRIBUTING.md`.
- If asked to set up Cursor Teams, explain the Pro-cancellation tradeoff and stop
  unless they still want it; you cannot create a Team from inside the repo.
- Calendar generation stays dry-run unless they pass `--write`.
- After any material ledger change, append `data/activity_log.csv` rather than
  rewriting history — but a personal-copy reset is a deliberate wipe, backed up
  under `data/backups/`.
