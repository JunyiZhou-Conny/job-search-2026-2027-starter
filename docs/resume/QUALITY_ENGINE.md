# About the Resume Quality Engine

This document explains why the engine exists, what it may change, and what it must not touch.
It is an explanation, not a tutorial.

The user of this work is Junyi, who already has a working apply system and needs the strongest truthful one-page resume for a specific job.
The next engineer who owns this code inherits one package (`scripts/rqe/`), a derived wording catalog, and a CLI that writes audit files under `generated/resume_quality/`.
Polar, the evidence bank schema, and `resumes/base/JZ_resume.tex` stay owned elsewhere.

## Definition of done

The v0 predicate is falsifiable.

1. Three fixtures exist, each taken from a job already stored in this repo. One SWE, one ML/AI, one data role.
2. For each fixture the CLI writes `resume.tex`, `requirement_map.yaml`, `claim_map.yaml`, `strategy.md`, `rejected_claims.md`, `arena_report.md`, `validation_report.md`, and `interview_defense.md`.
3. The generated `.tex` is a submit-ready variant. It must pass the existing one-page compile gate when `latexmk` is installed. The master resume under `resumes/base/` is not that gate.
4. Pairwise arena compares a historical one-page benchmark, when one exists, to the engine candidate. Each preference cites one JD requirement id and one claim id. There is no ATS-style 0-100 score.
5. At least one fixture changes selection, order, or wording relative to that benchmark, using only verified claims.
6. A planted unsupported metric or forbidden technology fails validation.
7. The engine does not restore `scripts/build_clusters.py`. It does not rewrite historical `data/resume_versions.csv` ids. It does not treat the 2-page master as a Polar attach.

## Architecture answers

**What is the atomic unit?**
A claim. A claim is one interview-defensible sentence backed by named fields on one project in `knowledge/evidence_bank.yaml`. The old cluster unit was a whole `\resumeSubheading` block copied from the master. That is too coarse for SWE versus data framing.

**Where do facts live?**
Only in `knowledge/evidence_bank.yaml`. `resumes/base/JZ_resume.tex` is the current master inventory and the heading and education source. It is not a second fact store.

**Where may wording live?**
`knowledge/resume_claim_catalog.yaml` is a derived catalog. It may rephrase a bank-backed fact. The loader rejects any number that is absent from that project's measured fields. Planned and forbidden lines still come from `not_yet_built` and `do_not` on the bank.

**How does a job become a resume?**

```
JD fixture
    → requirement map
    → claim matches
    → four competing strategies
    → evidence-auditor veto
    → pairwise arena
    → one-page resume.tex under generated/resume_quality/<slug>/
```

Application automation does not call this package.
`/tailor-resume` does.

**What is deterministic, and what is model judgment?**
v0 is deterministic. Extraction, matching, strategy templates, validation, render, and arena counts have no model call. Tests stay reproducible. Richer JD reading and free-prose bullets stay behind a closed flag.

**How is claim drift prevented?**
New bullets come from catalog wording or from a synthesized bank sentence. Every number in a new bullet must appear in the selected claims or the project's measured fields. Global forbidden tokens fail the run. Historical submitted version files are never edited. A benchmark run does not append `data/resume_versions.csv`.

**What replaced cluster generation?**
Another agent removed the mechanical cluster tree on purpose. This engine does not bring it back. Historical `2026-08-24_*_v1.3.tex` files are copied under `tests/fixtures/resume_quality/baselines/` so arena has a one-page opponent. Missing baselines are allowed. A missing production one-pager is an acceptable transitional state.

**Why not put claims on the bank?**
A second agent owns the bank schema and the master TeX. Authoring `claims:` on `evidence_bank.yaml` would collide with that work. Synthesis plus a small catalog is the minimum derived layer.

**Why not learn from outcomes?**
`data/resume_versions.csv` already has parent, hypothesis, and funnel counts. Sample sizes are still too small. Record later. Do not claim a model.

## What stays exactly as it is

- `knowledge/evidence_bank.yaml` remains the only factual source of truth. This PR does not redesign its schema.
- `resumes/base/JZ_resume.tex` remains the two-page master. The engine reads headings, education, and skill lines. It does not rewrite the file.
- `scripts/compile_resume.sh` remains the compile gate. Paths under `resumes/base/` stay on the master page limit. Generated variants use the one-page limit.
- Historical rows in `data/resume_versions.csv` stay historically accurate.
- Polar, discovery, apply-queue, and form-strategy files stay out of this pipeline.
- Planned work (`not_yet_built`, `do_not`, `resume_eligible: false`) must not become completed work.
- The 2-page master is not a Polar production fallback.

## Smallest MVP that can prove the idea

The proof is one comparison. For three real fixtures, does claim-level selection and family wording beat a historical one-pager on a pairwise arena that an evidence auditor can veto, while the validator rejects a planted lie?

If the engine only reprints the master, the idea has not been proven.
If it changes emphasis using bank facts and still compiles to one page, the architecture holds.

## Files this v0 adds or changes

- `docs/resume/QUALITY_ENGINE.md` (this file)
- `docs/state/resume_quality_engine.tsv`
- `knowledge/resume_philosophy.yaml`
- `knowledge/resume_claim_catalog.yaml`
- `scripts/rqe/` and `scripts/resume_quality.py`
- `tests/test_resume_quality.py`
- `tests/fixtures/resume_quality/`
- `.cursor/commands/tailor-resume.md` and `prompts/tailor-resume.md`

## Tests that make the prototype trustworthy

Behavior tests, not mock-call tests.

- A bullet that adds `40% latency` fails because that number is not in the bank.
- A bullet that names Kubernetes or Pinecone fails.
- A planned S-Seg-RLVR result written as completed fails.
- A catalog row that invents a metric fails to load.
- The same JD, bank, philosophy, and catalog hash produce the same `resume.tex`.
- Matcher labels a named Python plus ETL requirement as `strong_direct` against `compleg_uk_nz` and labels CUDA kernel authorship as `unsupported`.
- Default CLI does not rewrite `data/resume_versions.csv`.
- A project missing from the master TeX still renders a heading from bank title, org, role, and dates.
