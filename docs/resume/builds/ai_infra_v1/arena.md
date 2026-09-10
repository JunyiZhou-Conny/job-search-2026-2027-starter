# Semantic review. `ai_infra_v1`

Heuristic `arena()` was not used as recruiter judgment.

Opponent. `tests/fixtures/resume_quality/baselines/2026-08-24_cloud-swe_v1.3.tex`.
Master. Inventory only.

Rendered two layouts after the prose cleanup. Three-project production page versus the same page with mixhvg-py restored. Both compile to one page.

## Evidence auditor

`python3 scripts/resume_quality.py build --family ai_infra --compile` is clean.

`pdfinfo` and `compile_resume.sh` both report 1 page. No hard factual failures.

Cite. `autoresearch_cellot.measurable_results` 338 / 318 / 79.3 h `resume_ok: true`. `cellot_wyss.research_evidence` A-D ranges `resume_ok: true`. `job_search_os.do_not_claim` autonomous apply.

## Recruiter

Can a technical recruiter see the AI-infra identity in 10-15 seconds?

Yes. First heading is a closed-loop cluster system with a job count and wall-clock. Second heading is human-supervised browser automation. Research is a hub plus honest eval. Skills are ordinary technologies.

Hierarchy is Education, Skills, Engineering, Research. The strongest systems signal is first.

Preference over the 2026-08-24 cloud-swe baseline stands. That page titles AutoResearch an agent and spends an engineering slot on a clinical chatbot.

Cite. `autoresearch_cellot.title`. `job_search_os.architecture`.

## Senior AI infrastructure engineer

Do I see real systems depth rather than repository-specific jargon?

Yes. The page now shows a validation-gated deterministic planner, a checkpointed agenda, optional LLM planner infrastructure with a spend ceiling and fallback, preemption resume, a compiled browser runtime with Submit checks, a no-auto-submit experiment hub, and atlas-scale I/O. Those are systems.

Gone from recruiter-facing prose. `policy.validate()`. `serial_requeue`. `cache/last.pt`. Polar runtime compiler. G2 / G3. decoded-frame metrics as a skill.

Would this person plausibly join an AI or ML infra team? Yes, as an early-career engineer who has owned experiment loops and gated automation.

Cite. `autoresearch_cellot.software_engineering_evidence`. `cellot_wyss.architecture` hub never auto-submits. `job_search_os.software_engineering_evidence` Submit gates.

## Skeptical technical interviewer

Are all strong verbs and claims defensible?

The 338 / 79.3 h line remains the first hard question because the public CSV is header-only. Keep the counts. They are `resume_ok: true`. Provenance stays in `interview_defense.md`.

"Optional LLM planner infrastructure" can be over-read as a live LLM episode. The sentence does not say an LLM directed the runs. `control_logic` and `do_not_claim` still forbid that. The unused-on-recorded-runs fact is in `interview_defense.md`.

"Designed recovery" matches `job_search_os.strongest_accomplishments`. "Engineered atlas-scale I/O" matches the bank. No built→architected upgrades.

Paired held-out-species R^2 will draw a Tabula-OOD question. Answer is LPS / rat-in-train prior. That parenthetical is no longer on the page.

Cite. `autoresearch_cellot.measurable_results` resume_note. `autoresearch_cellot.do_not_claim` LLM directed. `cellot_wyss.research_evidence` placement.

## mixhvg with-versus-without

With mixhvg. Four headings. Engineering stacks three projects. The fidelity bullets are true and dense. They repeat single-cell / HVG biology already carried by speciesOT. Whitespace collapses. The first two systems stories lose dominance.

Without mixhvg. Two engineering systems and one research-infra project. Bottom margin opens. Scan path is cleaner.

Choice. Three projects. Recorded in `selection.md`.

## Pairwise question

Would a reasonable AI-infrastructure recruiter or engineer learn a clearer and stronger truthful story from this page than from the old cloud-swe cluster or from the two-page master?

Yes. The cluster page is louder and less true. The master is an inventory. This page is a three-project argument in ordinary engineering language.

## Changes made after this review

1. Removed recruiter-facing disclaimers. Unused LLM, no auto-apply, and LPS / not-Tabula stay in `interview_defense.md`.
2. Translated repo-internal names into engineering language.
3. Retitled Job Search OS to Human-Supervised Browser Automation System. First bullet still names job applications.
4. Dropped mixhvg-py after rendering both layouts.
5. Skills line keeps languages, ML libraries, SLURM, and tests. Drops Polar compiler, `policy.validate`, and decoded-frame metrics.

No further wording change after the visual pass. The auditor is clean and the pairwise answer is yes.
