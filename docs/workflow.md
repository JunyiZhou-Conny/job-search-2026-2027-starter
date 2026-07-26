# End-to-end workflow

## 1. Discover

Use Jobright / LinkedIn / Handshake / career pages. Capture the company URL when convenient; otherwise apply first via Simplify and import later.

## 2. Hard eligibility gate

Check only hard constraints: citizenship, clearance, graduation/return-to-school, start-date vs authorization timing, unacceptable location/work model, and whether the role can reasonably fit your background.

See `docs/eligibility.md`. Sponsorship wording is **not** this gate.

## 3. Assign pursuit lane + priority

- Lane: `core` / `broad` / `practice` (effort model)
- Priority: A / B / C (urgency / strategic value)

Example: strong SWE fit + "no sponsorship" → often `broad` + B, not `ineligible`.

## 4. Apply (execution layer)

Prefer company career page + Simplify Autofill. Answer work-auth questions truthfully. Confirm submission before status `applied`.

## 5. Local enrichment (same day or end of day)

Record or import:

- resume version
- pursuit lane
- sponsorship signal
- auth answers / verbatim Q&A if ambiguous
- next action

```bash
python scripts/jobsearch.py import-simplify --file data/imports/simplify/YYYY-MM-DD.csv
python scripts/jobsearch.py dashboard
```

## 6. Networking lane

For **core / A** roles: identify 1–3 relevant people. First ask is perspective, not referral.

## 7. Follow through

Invest deep prep when OA/interview arrives—especially for broad/practice lanes that were low-effort at apply time.

## 8. Learn weekly

Compare OA/interview rates by lane, sponsorship signal, source, and resume version. Keep practice lane near 15–25% of applied volume unless data says otherwise.
