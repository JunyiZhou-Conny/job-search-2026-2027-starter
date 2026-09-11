---
name: resume-stack-build
description: BUILD-time orchestrator for a frozen family one-pager. Use when asked to BUILD a Resume Stack family variant. Not Polar. Not ROUTE. Not vip-tailor. Not a per-JD generate.
---

# Resume Stack BUILD

Run this at BUILD time only. Application time routes to an existing variant id.

## Sequence

1. Read `docs/resume/QUALITY_ENGINE.md` for the product boundary.
2. Read the family philosophy skill. `swe-philosophy`, `ml-ai-philosophy`, `ai-infra-philosophy`, or `health-ai-philosophy`. Do not BUILD `data_v1`. `data` is a router alias.
3. Follow `.cursor/skills/resume-evidence-selection/SKILL.md`.
4. Follow `.cursor/skills/resume-narrative-framing/SKILL.md`.
5. Write TeX under `resumes/families/<family>/<variant>.tex`. Stitch identity and education from `resumes/base/JZ_resume.tex`. Do not edit the master.
6. Follow `.cursor/skills/resume-semantic-review/SKILL.md`.
7. Gate with `python3 scripts/resume_quality.py build --family <family>` and `./scripts/compile_resume.sh`.

## Python owns

Evidence load, provenance, forbidden and planned claims, one-page compile, PDF page count, registry writes only when a human registers the frozen file.

## Skills own

Philosophy, selection, narrative, framing, page-space, scanability, semantic review.

## Fences

- Do not parse a JD as the main input.
- Do not modify Polar or implement ROUTE.
- Do not modify `knowledge/evidence_bank.yaml` schema or `resumes/base/JZ_resume.tex`.
- Do not restore `scripts/build_clusters.py`.
- Do not treat `generated/` as submitted.
- `plan.py` `fallback_order` is not the selector.
