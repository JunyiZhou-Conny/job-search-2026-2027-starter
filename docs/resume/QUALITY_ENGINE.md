# About the Resume Stack

This document explains the product boundary. It is an explanation, not a tutorial.

Junyi needs Polar to attach a truthful one-page resume in ordinary apply time. He does not need a new resume compiled from a job description on every row.

The next engineer inherits the `#121` substrate (`scripts/rqe/`, claim types, validator, one-page gate) and must not treat `resume_quality.py run --jd` as the default apply path.

`#120` owns `knowledge/evidence_bank.yaml` and `resumes/base/JZ_resume.tex`. This stack consumes those files. It does not redesign them.

## The intended path

```
canonical evidence bank
        │
        ▼
  two-page master resume          inventory only. Not Polar's attach.
        │
        ▼
  Resume Stack BUILD              rare. Four frozen family one-pagers.
        │
        ▼
  lightweight ROUTE               job metadata → family → variant id
        │
        ▼
  Polar attachment
```

VIP tailoring is off that line.

```
high-priority JD
        │
        ▼
  vip-tailor --jd <jd>            exceptional only. Not Polar's default.
```

Normal applications must not generate resumes dynamically.

Application-time behavior is:

```
job / discovery metadata
        → role-family classification
        → existing resume variant id
        → Polar attachment
```

## Production families

BUILD produces four frozen one-pagers.

1. `swe` — SWE, backend, infrastructure
2. `ml_ai` — ML and applied AI
3. `ai_infra` — AI infrastructure and agent systems
4. `health_ai` — Health AI and computational biology

`data` is not a v0 production family. A data-scientist or ETL posting routes to the closer of `swe` or `ml_ai`. Compleg can sit on the SWE variant. TextVQA-style evaluation can sit on the ML variant. A fifth family needs evidence that those two miss a real apply lane, not a leftover cluster name.

## Desired commands

These names are the contract. They are not all wired yet.

```
python3 scripts/resume_quality.py build --family swe
python3 scripts/resume_quality.py build --family ml_ai
python3 scripts/resume_quality.py build --family ai_infra
python3 scripts/resume_quality.py build --family health_ai

python3 scripts/resume_quality.py route --job <metadata>

python3 scripts/resume_quality.py vip-tailor --jd <jd>
```

`resume_quality.py run --jd` is the current VIP stand-in. Polar must not call it.

`/tailor-resume` is VIP-only. Regular and most prioritized rows use ROUTE.

## What Polar may attach

1. The Simplify resume already on the profile, when that widget is filled.
2. After BUILD exists, the routed frozen family PDF.
3. After a human accepts a VIP run, that one registered variant.

The two-page master is inventory. It is not the production attach. Landed `main` marks an empty resume widget `REVIEW_READY` / `missing_production_resume` and does not upload `resumes/base/JZ_resume.pdf`. This stack will replace that gap with a routed family variant once BUILD writes one. This PR does not edit Polar runtime.

A missing production one-pager is an acceptable transitional state. Do not invent a cluster tree to fill the gap. Do not restore `scripts/build_clusters.py`.

## Skills versus deterministic code

### Skills and model judgment

These decide what the page argues. They belong in project-local Resume Stack skills or policy packs, not as silent Python score boosts.

- Evidence selection (which projects, which claims)
- Role philosophy (SWE versus ML versus AI-infra versus Health AI)
- Narrative
- Bullet framing
- Page-space tradeoffs
- Recruiter scanability
- Technical depth
- Skeptical-interviewer review
- Pairwise judgment between two already-valid candidates

`knowledge/resume_philosophy.yaml` is the v0 policy pack. Promote it into skills later. Do not hard-code a second copy of those rules in `plan.py`.

### Deterministic code

These gates stay in Python and must remain reproducible.

- Evidence loading from `knowledge/evidence_bank.yaml`
- Claim provenance
- Forbidden and planned claims
- Dates, names, and identity consistency
- One-page compile gate for submit-ready variants
- PDF page validation
- Reproducibility (same inputs, same `resume.tex`)
- Resume version registry writes only when a human opts in
- Routing contract (metadata → family → variant id)

A beautiful resume that fails validation is invalid.

## How `#121` maps onto BUILD / ROUTE / VIP

| Current piece | Command | Fate |
|---|---|---|
| `scripts/rqe/models.py` (`Claim`, `Bank`, `ValidationReport`) | all | Keep. This is the domain shape. |
| `scripts/rqe/load.py` | BUILD, VIP | Keep as the bank loader. Tighten catalog provenance before BUILD ships. |
| `scripts/rqe/render.py` | BUILD, VIP | Keep. Reads master headings. Does not edit the master. |
| `scripts/rqe/judge.py` `validate_tex` / `validate_pdf_pages` | BUILD, VIP | Keep. Hard veto. |
| `scripts/rqe/judge.py` `arena` | BUILD, VIP | Keep the code. Call it a heuristic ranker. Do not present metric count, signal count, or defensibility count as recruiter or hiring-manager judgment. Real pairwise review is a skill. |
| `scripts/rqe/jd.py` | VIP only | Keep. Polar and ROUTE do not parse a JD body. |
| `scripts/rqe/plan.py` `match_job` | VIP, later BUILD | Keep token overlap as a helper. It is not the selector of record. |
| `scripts/rqe/plan.py` `fallback_order` score boosts | none | Remove before BUILD. A family may publish an inspectable default slate in a policy pack. Project choice must be justified by bank signals, not a silent prior. |
| `scripts/rqe/cli.py` `run` / `benchmark` | VIP | Rename to `vip-tailor`. Keep the audit pack. |
| `scripts/resume_quality.py` | entry | Keep. Add `build` and `route` later. Do not make `run` the apply default. |
| `knowledge/resume_philosophy.yaml` | BUILD, ROUTE | Keep as the v0 pack. Add `ai_infra`. Mark `data` as `routes_to` only. |
| `knowledge/resume_claim_catalog.yaml` | BUILD, VIP | Reduce to a display layer. See provenance below. |
| `tests/fixtures/resume_quality/baselines/` | BUILD | Keep as historical one-page opponents. |
| `tests/fixtures/resume_quality/jds/` | VIP, ROUTE | Keep. Citadel is a ROUTE fixture (data → swe or ml_ai), not a reason to BUILD a data variant. |
| `tests/test_resume_quality.py` | all | Keep validator and provenance tests. VIP pipeline tests stay optional-path tests. |
| `/tailor-resume` | VIP | Relabel. Do not tell Polar to run it. |
| `data/resume_versions.csv` mutation | none | Still forbidden unless a human registers a frozen or VIP file. |
| `scripts/build_clusters.py` | none | Do not restore. |

## Catalog provenance

Numeric grounding is not enough. A line can keep every number from the bank and still overclaim ownership, architecture, impact, responsibility, or a technology.

Until a semantic gate exists, the catalog is a display alias file.

A catalog row may stand only when all of these hold.

1. Every number appears as a whole token in the cited bank fields (already enforced).
2. Every technology token appears in that project's `technologies` or cited evidence fields.
3. Ownership and architecture verbs (`architected`, `led`, `deployed`, `sole author`) appear in the cited bank fields or are dropped.
4. The row points at bank field names. It does not add a fact.

If a paraphrase fails those checks, BUILD and VIP must use the synthesized bank sentence instead. They must not keep the stronger wording.

Do not add `claims:` to `evidence_bank.yaml`. `#120` owns that schema.

## Arena

`arena()` counts coverage, metric tokens, signal density, and stored defensibility labels. That is a reproducible heuristic. It is useful as a BUILD or VIP sort key after the auditor veto.

It is not recruiter judgment. It is not hiring-manager judgment. It is not a skeptical interview. Those reviews are skills that read the same claim ids and the JD or family pack, then write a preference with a reason a human can reject.

The evidence-auditor veto stays deterministic and hard. A factually invalid candidate cannot win.

## Git stacking

`#121` started on `main`. `#120` started on `#117`. `#117` deletes the cluster tree and is currently dirty against `main`. Targeting `main` made `#121` look like it owned a one-page product on top of the old cluster checkout.

`#117` and `#120` have landed on `main`. This branch rebases onto that `main`.

```
main  (#117 folder reset + #120 bank/master)
  └── #121  this branch
        Resume Stack substrate. No bank or master rewrite.
```

This PR must not overwrite `knowledge/evidence_bank.yaml` or `resumes/base/JZ_resume.tex`. If a rebase conflict appears there, take latest `main`.

## What this correction changes now

- This document.
- Command and rule wording so VIP is optional and ROUTE is the apply path.
- Policy-pack keys for `ai_infra` and for `data` as a router alias.
- Git base of `#121` onto landed `main`.

## First BUILD

`ai_infra_v1` is the first frozen family one-pager.

- Path. `resumes/families/ai_infra/ai_infra_v1.tex`
- Skills. `.cursor/skills/resume-stack-build/` and the four Resume Stack skills
- Gate. `python3 scripts/resume_quality.py build --family ai_infra --compile`
- Artifacts. `docs/resume/builds/ai_infra_v1/`
- Page. Three projects after the cleanup pass. mixhvg-py was tested and dropped. See `docs/resume/builds/ai_infra_v1/selection.md`.
- Contact. Source TeX keeps a sanitized email. Application PDF is `python3 scripts/export_resume.py --family ai_infra`.

`swe`, `ml_ai`, and `health_ai` are not built. `route` is not implemented. Polar is unchanged.

`plan.py` `fallback_order` is still in the VIP matcher. BUILD does not call it. The selector of record for `ai_infra_v1` is `docs/resume/builds/ai_infra_v1/selection.md`.

## Later BUILD predicate

A reviewer can run `build --family swe` (and the other three), see why each included project earned its slot from bank signals, see the auditor veto on a planted lie, and see a one-page PDF. Polar then receives a variant id from `route`. `vip-tailor` is unused on a regular row.
