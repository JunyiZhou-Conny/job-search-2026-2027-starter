# Platform layers (do not sync bidirectionally)

## Layer 1 — Discovery

Jobright, LinkedIn, Handshake, 1point3acres, company career pages, new-grad lists.

Question answered: *What roles exist right now?*

## Layer 2 — Application execution + base ledger

Simplify Autofill and Tracker, plus the company ATS.
Polar must not use Jobright **APPLY WITH AUTOFILL** as the path to the employer ATS.

Question answered: *What did I apply to, when, and what stage is it in?*

Two execution environments share this layer. They do not share cookies.

- **Cursor cloud.** Computer Use on a Cloud Agent VM. Needs the apply harness. See `docs/automation/APPLY_HARNESS.md` and `docs/automation/COMPUTER_USE_PROMPT.md`.
- **Polar local.** Polar is Junyi's agentic browser on Junyi's computer. It uses logged-in Jobright, Original Job Post, and the employer ATS. See `docs/automation/POLAR.md`.

Cursor still decides what to apply to. Polar or cloud Computer Use executes a named job. GitHub holds the handoff. Polar does not scrape or triage a second job list.

## Layer 3 — Local Cursor strategy system

This repository.

Question answered: *Why apply, which resume, what auth answers, who was contacted, what did we learn, what is next?*

Owned here only:

- `resume_version`
- `pursuit_lane`
- `sponsorship_signal`
- `eligibility` (hard gate)
- `auth_work_authorized` / `auth_needs_sponsorship` / `auth_qa_notes`
- referral + networking
- interview notes / dossiers
- `next_action`

## One-way nightly import

```text
Discovery platforms → Apply via Simplify → Export CSV → Cursor import
```

```bash
# Save export as:
# data/imports/simplify/YYYY-MM-DD.csv

python scripts/jobsearch.py import-simplify \
  --file data/imports/simplify/2026-07-20.csv

python scripts/jobsearch.py dashboard
```

Importer matches by URL first, then `company + role`. It updates base status / applied date / URL and **preserves** local strategy fields.

Expected CSV columns (aliases accepted): `Company`, `Title`/`Job Title`, `URL`/`Link`, `Status`, `Date Applied`, `Location`, `Notes`.
