# Platform layers (do not sync bidirectionally)

## Layer 1 — Discovery

Jobright, LinkedIn, Handshake, 1point3acres, company career pages, new-grad lists.

Question answered: *What roles exist right now?*

## Layer 2 — Application execution + base ledger

Simplify Autofill / Tracker (and company ATS). Jobright Autofill only if needed.

Question answered: *What did I apply to, when, and what stage is it in?*

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
