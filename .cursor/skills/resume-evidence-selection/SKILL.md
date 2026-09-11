---
name: resume-evidence-selection
description: Inspectable project selection for Resume Stack BUILD. Use after ai-infra-philosophy and before narrative framing. Input is the evidence bank plus a family philosophy. Output is a selection report. Never use plan.py fallback_order as the selector.
---

# Evidence selection

## Input

- `knowledge/evidence_bank.yaml`
- The family philosophy skill (`ai-infra-philosophy` for this BUILD)
- `knowledge/resume_philosophy.yaml` lead signals and `max_projects`

## Output

Write `docs/resume/builds/<variant>/selection.md` with every heading below.

1. Projects considered
2. Strongest family signals per project
3. Redundant signals
4. Evidence strength
5. Interview defensibility from the bank field, not a new score
6. Selected
7. Rejected
8. Why each selected project deserves one-page space

Cite project ids. Quote or closely paraphrase bank fields. Mark `USER_REPORTED` vs `VERIFIED_*`.

## Selector of record

The report is the selector. `scripts/rqe/plan.py` `fallback_order` is not.

A silent prior that boosts Compleg or Airway is a defect. If those projects win, the report must say why from bank signals.

## Complementary coverage

Maximize distinct philosophy signals across the slate.

Two Cannon/SLURM projects may both ship only if they argue different jobs. Example. AutoResearch owns the search loop and policy gate. speciesOT owns the no-auto-submit hub and decoded-metric eval.

Drop a project that only repeats a signal already paid for.

## Strength and defensibility

- `resume_eligible: false` or empty usable evidence. Reject.
- `interview_depth: weak` plus `not_yet_built` results. Reject for a production one-pager.
- `resume_ok: false` numbers. Keep in the report. Do not put them on the page.
- `do_not` and `do_not_claim`. Those statements are bans, not bullets.

## Hypothesis, not order

For `ai_infra`, test this slate rather than obeying it.

- `autoresearch_cellot`
- `job_search_os`
- `cellot_wyss` (speciesOT)
- `mixhvg_py`

If mixhvg only adds biology already carried by speciesOT, replace it or drop it. AlphaFold is the thin HPC-inference alternate. Airway is the clinical-agent alternate and fails `de_emphasize: clinical` unless the report overturns that with a bank reason.

## Fences

Do not invent metrics, employers, or planned-as-done work. Do not restore `scripts/build_clusters.py`.
