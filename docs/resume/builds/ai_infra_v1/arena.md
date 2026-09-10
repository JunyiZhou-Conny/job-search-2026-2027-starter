# Semantic review. `ai_infra_v1`

Heuristic `arena()` was not used as recruiter judgment.

Opponent. `tests/fixtures/resume_quality/baselines/2026-08-24_cloud-swe_v1.3.tex`.
Master. Inventory only.

## Evidence auditor

`python3 scripts/resume_quality.py build --family ai_infra --compile` must stay clean.

First pass compiled to 1 page. `validate` had no hard failures.

## Recruiter

Preference. `ai_infra_v1` over the 2026-08-24 cloud-swe baseline.

Why. The first engineering title is a closed-loop cluster system, not an "Ablation-Search Agent". Job Search OS is readable in two sentences. Hierarchy is Education, Skills, Engineering, Research.

Change after this pass. Shortened the skills line so "Computer Use action sheets" does not wrap. Tightened the mixhvg fidelity bullet so the Jaccard and median facts stay and the mean-overshoot story is one clause.

Cite. `autoresearch_cellot.title` suggested resume title. `job_search_os.architecture`.

## Senior AI infrastructure engineer

Preference. `ai_infra_v1`.

Why. The page shows a validation-gated proposer, a checkpointed agenda, a fairshare design choice, an unused LLM fallback, a compiled agent runtime with HITL gates, a no-auto-submit hub, and a fidelity test against R. That is systems work. The baseline spends the second engineering slot on a clinical chatbot and the research slot on a drug-translation story the current bank forbids.

Cite. `autoresearch_cellot.software_engineering_evidence`. `cellot_wyss.architecture` hub never auto-submits. `job_search_os.software_engineering_evidence` Submit gates.

## Skeptical technical interviewer

Disagreement with the recruiter. The 338 / 79.3 h line will be the first hard question because the public CSV is empty. Keep the counts. They are `resume_ok: true`. Put the provenance in `interview_defense.md`, not on the page.

Verb check. "designed recovery" matches `job_search_os.strongest_accomplishments`. "Engineered atlas-scale I/O" matches the master and bank "Engineered atlas-scale handling". No built→architected upgrades.

Cite. `autoresearch_cellot.measurable_results` resume_note. `autoresearch_cellot.do_not_claim` LLM directed. `cellot_wyss.do_not_claim` 180+ models.

## Pairwise question

Would a reasonable AI-infrastructure recruiter or engineer learn a clearer and stronger truthful story from this page than from the old cloud-swe cluster or from the two-page master?

Yes. The cluster page is louder and less true. The master is an inventory. This page is a four-project argument.

## Changes made after review

1. Dropped Computer Use from the skills line. It remains in the Job Search OS bullet.
2. Shortened mixhvg validation to Spearman, Jaccard, and the median correction.
3. Dropped R/scran/Seurat dotted versions and the 495 count. The number gate only sees tokens on usable claims. 4.3.3 and 495 are in bank prose that did not become usable claims.
4. Wrote 6619 without a LaTeX thousands group so strip_tex does not split it into 6 and 619.
