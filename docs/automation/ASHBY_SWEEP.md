# Ashby board sweep

A credential-free discovery source. It reads the public list endpoint of every
board in `knowledge/ashby_orgs.yaml`, keeps fresh early-career engineering
postings, probes each kept posting's application form through
`scripts/ashby_form.py`, and writes candidate rows the apply stage can act on
without waiting for Jobright to surface the posting.

```bash
python3 scripts/automation/export_ashby_boards.py --days 7
python3 scripts/automation/export_ashby_boards.py --days 3 --only kayak notion
```

Outputs, `RUN` being the UTC hour stamp `YYYY-MM-DDTHH`:

- `generated/ashby_sweep_{RUN}.csv`, one row per kept posting plus one row per
  board that failed to load (blank title, reason in `notes`).
- `generated/ashby_sweep_{RUN}.md`, a digest with `g2_candidate` rows first.

## What a row means

`publishedAt` is Ashby's first publication time, the freshness truth for Ashby
rows (`docs/experiments/2026-09-03_g2_candidate_screen.md`). The form columns
come from `ashby_form.summarize`: `required_count`, `required_essays`,
`broad_sponsorship_question`, `export_control_question`, `external_artifact`,
`g2_blockers`. They are blank when the probe failed or the posting is closed.

`g2_candidate` is true when the posting is open, `g2_blockers` is empty, the
type is FullTime or Intern, and the posting is not remote-only. It is a form
fact, not a decision. Location, the 2026 cycle year, and fit stay with triage
(`knowledge/discovery_triage_rules.yaml`), and the Submit gate stays with
`docs/policy/SUBMIT_ROLLOUT.md`.

## Filters in code

- Window: `publishedAt` within `--days`.
- Remote: excluded when `workplaceType` is `Remote`. Ashby sets `isRemote`
  for Hybrid postings too, so that flag alone would drop every hybrid role.
- Title: must match the domain pattern built from `knowledge/target_roles.yaml`
  titles plus engineering words; excluded on seniority words (Senior, Staff,
  Principal, Lead, Manager, Director, Head, Chief, Architect, PhD) and on
  `2026` in the title; clearly non-technical titles (sales, hardware,
  finance, design, and similar) drop unless a strong engineering word is
  present.

## Adding a board

Append one block to `knowledge/ashby_orgs.yaml` in slug order after confirming
`https://api.ashbyhq.com/posting-api/job-board/{slug}` returns real postings.
The test suite checks the file stays sorted and covers every slug in the
`ashby:` section of `knowledge/careers_boards.yaml`.

## Boundaries

Sequential requests with a short pause and a 20 second timeout. A board
error is one CSV row, never an aborted sweep. The script writes only under
`generated/`; it does not touch `data/`, does not ingest, and does not apply.
