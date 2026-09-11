# About resume routing

This document explains the discovery-time resume router. It is an explanation, not a BUILD guide.

`docs/resume/QUALITY_ENGINE.md` still owns the Resume Stack product boundary. This file owns only classification.

The router answers one question from cheap job metadata: which frozen production family should this job use?

It does not write resume text. It does not call a model. It does not read a full job description. It does not run at form fill time.

## What Polar later reads

Discovery writes the decision onto the queue row. An apply worker later reads `resume_family` and `resume_variant`. It does not classify again.

```
card metadata
        → deterministic ROUTE
        → resume_family
        → approved active resume_variant, or blank
        → Polar attach
```

## Input contract

The classifier uses metadata that hourly discovery already has.

Required:

- `role`

Optional:

- `company`
- `source` or `board_category`
- `track`
- `location`
- `short_text` when the card already has it
- `legacy_cluster` when a historical label is present

Do not open Original Job Post to classify. Do not fetch the employer JD for routine routing. If the card is too thin, return `REVIEW`.

Canonical policy: `knowledge/resume_routing.yaml`.

Engine: `scripts/resume_routing.py`.

CLI: `scripts/resume_route.py`.

Do not call `scripts/resume_quality.py route`. BUILD owns that entry point.

## Production families

Family ids must match production families in `knowledge/resume_philosophy.yaml`.

- `swe` — software engineering, backend, platform, APIs, general cloud software
- `ml_ai` — machine learning, applied AI, model training and evaluation, modeling-heavy data science
- `ai_infra` — ML or AI platform, inference and training infrastructure, agent platform, MLOps when the title is infrastructure
- `health_ai` — health or biology domain plus modeling work

There is no production `data` family. Data titles route to `swe` or `ml_ai`, or stay `REVIEW`.

A health company name alone is not `health_ai`. A backend intern at a clinic stays `swe` or `REVIEW`.

An AI company name alone is not `ml_ai` or `ai_infra`. A generic software engineer there stays `swe`.

## Rule precedence

The engine is a policy table, not a model.

1. Normalize the title. Punctuation becomes a token break, so `AI/ML` and `(AI)` still match.
2. Match exclusive multiword title patterns on token boundaries. `ai` does not match inside `training`.
3. If an AI-infra exclusive pattern and a generic applied-AI pattern both hit, keep infra.
4. Add weighted family signals. Health signals score the title only, so a company named Health does not win by itself.
5. Apply the data overlay. Modeling and experimentation add `ml_ai`. Pipelines, ETL, and data engineering add `swe`. Mixed data-science plus data-engineer titles become `REVIEW`.
6. Apply the health overlay. Domain plus modeling raises `health_ai`. Domain without modeling does not.
7. A board category is a weak prior only when that family already has a score.
8. Bare `gpu` stays off `ai_infra` unless an AI or ML token is also present.
9. Compare scores. If the lead is too small, return `REVIEW`. Never default to `swe`.

## Confidence

Confidence is one of `high`, `medium`, or `review`. The router does not emit probabilities.

- `high` — an exclusive pattern for the winning family, or a lead of 5 or more
- `medium` — a family led by at least 2 points and a score of at least 3
- `review` — unresolved, mixed, or too weak

Thresholds live in `knowledge/resume_routing.yaml`.

## Unresolved jobs

`family = REVIEW` when the role is empty, scores do not lead, or a data overlay forces review.

`resume_variant` stays blank. Polar apply treats an empty variant as `missing_production_resume`. It does not attach `JZ_resume.pdf` and it does not borrow another family.

## Variant resolution

Classification and variant lookup are separate.

`resolve_variant()` reads `data/resume_versions.csv`. It accepts a row only when `cluster` equals the routed family and `active` is true, 1, or yes. It never returns `JZ_resume` or `cluster=base`.

If no approved active variant exists, the family still stands and `resume_variant` stays blank with reason `no_active_family_variant`. This PR does not activate registry rows.

## Legacy `resume_cluster`

The live Sheet column `resume_cluster` is older than this router.

Hourly discovery used to set it from Polar runtime section E, which compiles title families in `knowledge/target_roles.yaml`. Those labels are `cloud_swe`, `data_ml`, and `health_ai`. A Polar agent mapped card titles onto that list. There is no Python classifier on that path.

`scripts/label_job.py` is a different substring helper for `applications.csv`. `scripts/rqe/jd.py` parses a full JD for VIP only. Neither is this router.

Treat stored `resume_cluster` values as historical labels. They are useful as a benchmark. They are not ground truth. The first migration pass does not overwrite them.

Coarse correspondence for the benchmark:

- `cloud_swe` often maps to `swe`
- `data_ml` often maps to `ml_ai`
- `health_ai` often maps to `health_ai`

Disagreement is expected. The old taxonomy cannot represent `ai_infra`. Perfect agreement would mean the new family is unused.

## Sheet schema

`polar-sheet-migration` appends these names at the far right when they are missing:

- `resume_family`
- `route_confidence`
- `route_reason`
- `resume_variant`

Discover and apply do not append headers. `plan_route_header_migration()` is the planner. A duplicate name stops the migration. It does not delete columns.

## Discovery integration

Hourly discovery now does this after eligibility triage:

1. Write `resume_cluster` on new rows only, from the old title families.
2. Run `python3 scripts/resume_route.py --role ...` on card metadata when the local filesystem is available.
3. Write the four route fields from that JSON.

If the CLI is missing, write `REVIEW` / `review` / `router_unavailable` and leave the variant blank. If the live header lacks `resume_family`, note `missing_route_columns` and continue.

Cloud daily discovery still writes `suggested_cluster` as the legacy label. After triage, run the same CLI over the triage CSV. Do not open a posting only to classify.

## Apply boundary

Apply reads `resume_family` and `resume_variant`. It does not rerun the router. It does not upload a resume in this change set. Attachment is a later consumer.

## VIP precedence

VIP does not change the family classifier. A VIP job can still be `ai_infra`.

Later attach order is:

1. A human-approved VIP variant for that job
2. Otherwise the routed active family variant

Prioritized is not VIP. VIP needs an explicit owner decision. This router does not generate VIP resumes.

## Commands

One job:

```bash
python3 scripts/resume_route.py --role "ML Infrastructure Engineer" --company AppLovin
```

Historical triage CSV:

```bash
python3 scripts/resume_route.py --csv generated/discovery_triage_2026-09-02.csv --out /tmp/routed.csv
```

Legacy benchmark over unique discovery triage rows:

```bash
python3 scripts/resume_route.py --benchmark
```

The benchmark writes `generated/resume_routing/benchmark.json`.
