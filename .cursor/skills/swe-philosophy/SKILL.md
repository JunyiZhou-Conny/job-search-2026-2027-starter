---
name: swe-philosophy
description: Role-evaluation policy for an early-career SWE / Backend / Infrastructure resume. Use during Resume Stack BUILD for family swe. Not candidate evidence. Not application-time ROUTE or Polar.
---

# SWE role philosophy

Read this before selecting evidence or writing bullets for `swe_v1`.

This file is a hiring policy. `knowledge/evidence_bank.yaml` is the only fact source.

## What the page must prove

A technical recruiter should see, in about 15 seconds, an engineer who owns software other people can run. Interfaces. Schemas. Recovery. Tests. Automation that stays gated.

A senior engineer should see implementation and operational judgment, not a list of model names.

## Signals that earn space

Prefer complementary coverage across the page.

- Software ownership. A system the candidate built and can walk.
- Architecture that shows module boundaries or plane splits.
- APIs, CLIs, or schemas other people consume.
- Reliability and recovery. Restart, resume, anti-bot, handoff.
- Automation with an explicit gate.
- Testing and numerical or schema correctness.
- Deployment or cloud work the bank actually records.
- Maintainability. Handoff notes, pinned defects, policy as code.

## Signals that do not earn space on this family

- Clinical product story. Airway belongs on Health AI. `swe.de_emphasize` includes `clinical`.
- Course-project model bakeoffs.
- Science-only speciesOT claims. If speciesOT appears, it must pay an interface or correctness signal, not biology.
- Planned GRPO results.
- Keyword stuffing. No Kubernetes.

## Authority classes

- Authoritative. Harvard MCS one-page. Fact-based. AI may edit but must not author.
- Strong heuristic. A resume is an argument, not a lab notebook.
- Local hypothesis to test. Job Search OS, Compleg, mixhvg-py. Compleg pays ETL and schema. mixhvg pays an API and a test harness. AutoResearch is the automation alternate and overlaps `ai_infra`.

## Hard writing rules

- One page.
- Do not upgrade verbs. Bank `airway_chatbot` does not say architected or led. Do not import those master verbs onto this family either.
- Do not write agentic for AutoResearch.
- Provenance limits stay in `interview_defense.md`.
- Recruiter-facing prose stays plain.

## Out of scope

Do not parse a JD. Do not call Polar. Do not edit `knowledge/evidence_bank.yaml` or `resumes/base/JZ_resume.tex`.
