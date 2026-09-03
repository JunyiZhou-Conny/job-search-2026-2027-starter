# Experiment: first G2 candidate screen (2026-09-03)

Question. Is there a fresh Ashby keep from the last six discovery runs
that qualifies for a limited autonomous regular Submit under
`docs/policy/SUBMIT_ROLLOUT.md` G2, and do the negative gates fire
correctly on the ones that do not?

Method. Read every `discovery_triage_*.csv` from runs 08-28 through
09-02 (12 runs), filter `decision=keep` with an Ashby `apply_url`,
fetch each form from Ashby's public GraphQL (`ApiJobPosting`,
`applicationForm.sections.fieldEntries`), and run
`scripts/apply_ledger.py precheck`.

## Ashby keeps found

| Company | Role | Fresh (Jobright) | Form facts | Gate verdict |
|---|---|---|---|---|
| KAYAK | Associate Software Engineer (Cambridge, MA) | "2 hours ago" on 09-02, but Ashby `publishedAt` 2026-07-20 | required broad sponsorship boolean with "unable to offer work sponsorship (including OPT)"; front-end React role | blocked, broad sponsorship question (open owner decision) and OPT exclusion. Not a G2 row. |
| DatologyAI | SWE Intern, Infrastructure (Winter 2027) | 09-01 | GraphQL returns null | posting closed. Recorded with `close-posting`. |
| Bland | Machine Learning Intern | 08-28, 08-29 | required LongText "Why are you a fit for this role?" | needs the writer path; not a minimal G2 row. |
| Northwood | SWE Intern (Summer 2027) | 08-29 | ITAR U.S. Person select, required project LongText, broad sponsorship select, 5 days on site Torrance | blocked, export compliance plus broad sponsorship plus essay. |
| Clera | Founding AI Engineer | 08-29 | Name, Email, Resume, LinkedIn, one work-authorization boolean. Shortest form seen. | Simplify tracker shows an application dated 08-25 to this company and title (browser probe). Duplicate once the tracker export lands in `data/imports/simplify/`. |
| Notion | SWE Intern (Summer 2027), Data Science Intern (Winter 2027) | 08-28 to 08-30 | Written answers drafted 08-23 in round two | prestige, prioritized. Review packet lane, never G2. |
| MeshyAI | Infrastructure Intern | 08-28 | already `J20260824-002` | `precheck` exit 3, duplicate by URL against `applications.csv` and `apply_attempts.csv`. Negative case verified. |

## Result

No qualifying G2 row in this window, and the Ashby G2 gate itself stays closed in `config/submit_gates.yaml` until the first wanted regular role completes the protocol. Four negative gates fired as
designed on real data: closed posting, duplicate against the repo,
duplicate against Simplify (pending the export), and broad-sponsorship
block. Two rows route to other lanes: Bland to the writer path, Notion
to the prioritized packet.

## What this changes

- `precheck` now reads the newest Simplify export, because the repo
  ledger alone would have let the Clera duplicate through.
- The G2 candidate filter needs the form facts before the browser opens.
  Ashby's GraphQL gives them for free; `scripts/ashby_form.py` will hold
  that probe.
- Freshness from Jobright's "posted N hours ago" is repost time, not
  first publication. Ashby `publishedAt` is the truth for Ashby rows.
