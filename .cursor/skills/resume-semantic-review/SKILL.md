---
name: resume-semantic-review
description: Semantic pairwise or adversarial review for a Resume Stack BUILD candidate. Use after a one-page TeX exists. Deterministic validate_tex is the auditor veto. scripts/rqe/judge.py arena() is a heuristic ranker, not this review.
---

# Resume review

## Inputs

- Candidate TeX and compiled PDF
- `docs/resume/builds/<variant>/selection.md` and `strategy.md`
- `knowledge/evidence_bank.yaml`
- Historical one-page baseline under `tests/fixtures/resume_quality/baselines/` when one exists
- Master resume as inventory only. It is not a one-page opponent.

## Deterministic auditor first

```bash
python3 scripts/resume_quality.py validate <tex>
./scripts/compile_resume.sh <tex>
```

`validate_tex` and the one-page compile gate veto the candidate. Do not argue writing quality past a factual fail.

`scripts/rqe/judge.py` `arena()` may run as a heuristic. Do not quote its coverage or metric counts as recruiter or hiring-manager judgment.

## Semantic reviewers

Write `docs/resume/builds/<variant>/arena.md`. Each reviewer cites a project id and a bank field. No 0-100 score.

### Recruiter

Can a technical recruiter see the value in 10-15 seconds? Is hierarchy clear? Are the strongest systems signals first? What is unnecessarily academic or dense?

### Senior AI infrastructure engineer

Does the page show systems depth rather than generic AI use? Are architectural decisions, reliability, experiment infra, and ownership visible? Would this person plausibly join an AI or ML infra team?

### Skeptical technical interviewer

Which bullets invite hard follow-ups? Can each important claim survive five minutes? Is any verb stronger than the bank?

### Evidence auditor

Restate the deterministic report. A fail is a veto.

## Pairwise question

Against the historical baseline, ask only this.

Would a reasonable AI-infrastructure recruiter or engineer learn a clearer and stronger truthful story from this candidate?

If the answer is not clearly yes, iterate framing or selection. Do not invent facts to win.

## Historical baseline traps

The 2026-08-24 cloud-swe one-pager is a benchmark opponent. It is not truth. It titles AutoResearch an agent, sells speciesOT as drug translation, and uses a 2018 TF-to-PyTorch port the current bank no longer measures. Prefer the truthful page even if it looks quieter.

## After review

Record disagreements and the changes you made in `arena.md`. Re-run validate and compile. Stop when the auditor is clean, the PDF is one page, and the pairwise question is yes.
