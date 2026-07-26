# /sync-simplify

One-way ledger sync when the user drops a Simplify export (any path).

## Trigger

Do this whenever the user:
- attaches / pastes a path to a Simplify CSV (e.g. `/Users/…/Downloads/Simplify_Tracked_Jobs_YYYY-MM-DD.csv`), or
- says “导入 Simplify / sync simplify / 我下载了 tracker”, or
- runs this command.

Do **not** wait for them to manually copy into the repo first — you copy it.

## Steps

1. **Copy** the file into the repo (preserve original name date if present):
   ```bash
   cp "<user-path>" data/imports/simplify/YYYY-MM-DD.csv
   ```
   Use the export date from the filename when possible; else today.
2. **Import** (one-way; preserves local strategy fields):
   ```bash
   python3 scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
   ```
3. **Dedupe / validate / dashboard**:
   ```bash
   python3 scripts/dedupe_applications.py
   python3 scripts/validate_data.py
   python3 scripts/jobsearch.py dashboard
   ```
4. **Reconcile mismatches (robustness)** — import matches by URL then company+role; Simplify often uses dashboard URLs or typos:
   - If a new `applied` row looks like a duplicate of an existing triage/keep row (same company + similar role, different URL) → **merge**: set the canonical local id to `applied` + `date_applied`, close/mark the Simplify-created duplicate, preserve `pursuit_lane` / `resume_version`.
   - Local `discovered` keep rows **not** in the export → leave as-is (user simply has not applied yet). Never delete them because they are missing from Simplify.
   - Brand-new companies in Simplify (e.g. Uber) → keep the new row; fill missing lane/cluster/resume with sensible defaults and `needs_review` if unsure.
5. **Report** to user: created / updated / merged duplicates / still-unapplied keep count / applied rows missing `resume_version`.

## Never

- Bidirectional sync back into Simplify
- Auto-submit applications
- Overwrite `pursuit_lane`, `resume_version`, auth, sponsorship, referral on import
- Invent statuses not in the CSV
