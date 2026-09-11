---
name: ai-infra-philosophy
description: Role-evaluation policy for an early-career AI Infrastructure / Agent Systems resume. Use during Resume Stack BUILD for family ai_infra. Not candidate evidence. Not application-time ROUTE or Polar.
---

# AI Infra role philosophy

Read this before selecting evidence or writing bullets for `ai_infra_v1`.

This file is a hiring policy. `knowledge/evidence_bank.yaml` is the only fact source.

## What the page must prove

A technical recruiter should see, in about 15 seconds, an engineer who builds the machinery around models. Experiment loops. Agent runtimes with human gates. Evaluation that refuses a convenient metric. Cluster jobs that resume after preemption.

A senior AI-infra engineer should see ownership of those systems, not generic model use.

## Signals that earn space

Prefer complementary coverage across the page.

- Experimentation infrastructure. Search loops, validation gates, idempotent runners.
- Agent or tool orchestration with an explicit human or policy gate.
- Reliability. Checkpoint, resume, preemption, fallback.
- Observability you can point at. Logs, ledgers, tests, compiled runtimes.
- Distributed or HPC execution the candidate actually ran.
- Evaluation infrastructure. Decoded metrics, fidelity checks, honest floors.
- API or workflow design that other people can run.
- Production-minded limits. Cost ceilings, no auto-submit, spend caps.

## Signals that do not earn space on this family

- Clinical product story. Airway stays off this page unless a later family needs it.
- Course-project model bakeoffs.
- Planned GRPO / untrained S-Seg-RLVR results.
- Science-only CellOT claims that duplicate AutoResearch or speciesOT.
- Keyword stuffing. No Kubernetes. No invented ATS score.

`knowledge/resume_philosophy.yaml` `ai_infra.de_emphasize` includes `clinical`. Obey it.

## Authority classes

Treat sources as labeled. Do not flatten them.

- Authoritative. Harvard MCS one-page, fact-based, tailor to valued skills, AI may edit but must not author. See `knowledge/resume_philosophy.yaml` `guidance`.
- Strong heuristic. A resume is an argument, not a lab notebook. Cut work that does not support the argument.
- Borrowed public idea. Groundedness gate before export. Keep the idea. Drop ATS 0-100 scores and required keyword percentages.
- Local hypothesis. Testable in the selection report. The current slate to test is AutoResearch, Job Search OS, speciesOT, mixhvg-py. Complementary coverage beats four overlapping keyword hits.

## Hard writing rules

- One page for this production variant.
- Not every bullet needs a number. A true architecture sentence can beat a weak count.
- Do not write "agent" or "LLM directed" for AutoResearch. Bank `control_logic` forbids it.
- Do not upgrade verbs. `built` stays `built` unless the bank says architected or led.
- Do not put provenance disclaimers on the resume when the same limit lives in the bank.
- Recruiter-facing prose stays plain. No em dashes. No "spearheaded". No "cutting-edge".

## Out of scope

Do not parse a JD. Do not call Polar. Do not edit `knowledge/evidence_bank.yaml` or `resumes/base/JZ_resume.tex`.
