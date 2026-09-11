---
name: resume-narrative-framing
description: Internal thesis and per-project bullet framing for Resume Stack BUILD. Use after evidence selection. Writes strategy and interview-defense notes. Does not invent facts. Does not put the thesis sentence on the resume unless selection says to.
---

# Narrative and bullet framing

## Internal thesis

Write a one-sentence thesis in `docs/resume/builds/<variant>/strategy.md`.

It is an editorial north star. Do not paste it onto the resume unless the selection report explicitly asks for a summary line.

Current `ai_infra` hypothesis. ML and AI engineer who builds experimentation, agent, and research infrastructure.

## Per selected project

For each project, record in `strategy.md`.

- Role in the story. What unique signal it pays for.
- Dimensions that get bullets.
- True evidence to omit, with the bank reason.
- Allowed ownership verbs. Copy them from the bank (`Sole author`, `Graduate Researcher`, `Implemented`). Do not promote them.
- Strongest defensible wording. Prefer a synthesized bank sentence over `knowledge/resume_claim_catalog.yaml` when ownership, architecture, technology, or impact is uncertain.
- Likely interview follow-ups. Write those in `interview_defense.md`.

## Wording bans

Do not silently change.

- built → architected
- contributed → led
- implemented → designed
- prototype → production
- automation → autonomous system
- closed-loop / self-directed → agentic / LLM agent (AutoResearch)

Catalog rows are display aliases. If a paraphrase is stronger than the cited bank fields, use the bank sentence.

## Recruiter-facing prose

- Generate bullets from bank fields, not by polishing the master or a historical cluster.
- Facts stay. Framing may change.
- Keep provenance limits in the bank and in `interview_defense.md`. Do not spend resume words on "public CSV is empty" unless the claim is otherwise indefensible.
- Avoid academic density on the first engineering project.
- Section order for `ai_infra` is Engineering Projects, then Research Experience.

## Page budget

`max_projects: 4`. `max_bullets_per_project: 3` in `knowledge/resume_philosophy.yaml`. Drop a bullet before overflowing one page.

## Fences

Do not edit the evidence bank or `resumes/base/JZ_resume.tex`. Copy contact and education from the master heading. Do not invent a second identity block.
