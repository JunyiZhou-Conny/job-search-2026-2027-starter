---
name: health-ai-philosophy
description: Role-evaluation policy for an early-career Health AI / Computational Biology resume. Use during Resume Stack BUILD for family health_ai. Not candidate evidence. Not application-time ROUTE or Polar.
---

# Health AI role philosophy

Read this before selecting evidence or writing bullets for `health_ai_v1`.

This file is a hiring policy. `knowledge/evidence_bank.yaml` is the only fact source.

## What the page must prove

A technical recruiter should see, in about 15 seconds, someone who applies ML to clinical or biological questions. A real clinical system if one exists. A translational biology result if one exists. No invented trial outcomes.

A domain specialist should see responsible claims. Incomplete capstone work stays labeled incomplete.

## Signals that earn space

Prefer complementary coverage across the page.

- Clinical or biological relevance the bank records.
- Translational ML. Species translation, not drug-effect composition.
- Single-cell biology when it is the project, not a keyword.
- Healthcare AI product context that is real. Airway is the clinical system.
- Scientifically valid evaluation. Held-out species, fidelity vs R, leaderboard.
- Biomedical research engineering. Hubs, ports, pipelines.
- Domain-aware interpretation. Chest X-ray orientation. Ortholog vs HVG flip.
- Responsible claims around unfinished research.

## Signals that do not earn space on this family

- Job Search OS. Wrong domain.
- AutoResearch as a cluster-ops lead. Use speciesOT for the biology.
- Planned GRPO metrics, downloaded pathology datasets, MICCAI acceptance.
- Claiming scGen, CellOT, and speciesOT as three projects.
- Keyword stuffing. No Kubernetes.

## Authority classes

- Authoritative. Harvard MCS one-page. Fact-based.
- Strong heuristic. Cut work that does not support the argument.
- Local hypothesis to test. Airway, speciesOT, mixhvg-py. Pneumonia CXR is the medical-imaging alternate. S-Seg-RLVR is allowed only as a method-and-repo line. AlphaFold is the thin protein-pipeline alternate.

## Hard writing rules

- One page.
- Do not upgrade Airway verbs. The bank does not say architected or led.
- Do not claim S-Seg-RLVR trained a policy or measured Dice.
- Do not claim drug-effect composition on speciesOT.
- HIPAA-conscious is allowed. It is in `airway_chatbot.measurable_results`.
- Provenance limits stay in `interview_defense.md`.
- Recruiter-facing prose stays plain.

## Out of scope

Do not parse a JD. Do not call Polar. Do not edit `knowledge/evidence_bank.yaml` or `resumes/base/JZ_resume.tex`.
