---
name: ml-ai-philosophy
description: Role-evaluation policy for an early-career ML / Applied AI resume. Use during Resume Stack BUILD for family ml_ai. Not candidate evidence. Not application-time ROUTE or Polar.
---

# ML and Applied AI role philosophy

Read this before selecting evidence or writing bullets for `ml_ai_v1`.

This file is a hiring policy. `knowledge/evidence_bank.yaml` is the only fact source.

## What the page must prove

A technical recruiter should see, in about 15 seconds, an engineer who trains, compares, and evaluates models. Measured generalization. Ablations. An honest metric.

A senior ML engineer should see experimental judgment, not a cluster-ops tour and not a clinical product story.

## Signals that earn space

Prefer complementary coverage across the page.

- Model training the candidate actually ran.
- Experimentation with a named comparison.
- Evaluation that can fail. Held-out splits, leaderboards, decoded floors.
- Ablations. Rank, prompt, architecture, freeze vs fine-tune.
- Generalization gaps the candidate diagnosed.
- Inference or PEFT when the bank records it.
- Reproducibility. Specs, seeds, documented setups.
- Meaningful measured results that are `resume_ok`.

## Signals that do not earn space on this family

- Job Search OS. Agent ops, not model work.
- Clinical product packaging. Airway is Health AI.
- AutoResearch as the lead if it only retells the cluster loop. That page is `ai_infra`.
- Untrained S-Seg-RLVR results.
- Keyword stuffing.

This family must not be `ai_infra_v1` with "ML" in the title.

## Authority classes

- Authoritative. Harvard MCS one-page. Fact-based.
- Strong heuristic. Cut work that does not support the argument.
- Local hypothesis to test. speciesOT, TextVQA LoRA, pneumonia CXR. AutoResearch is the experimentation-infra alternate and overlaps `ai_infra`. Transformer reimplementation is the foundations alternate.

## Hard writing rules

- One page.
- Do not upgrade verbs.
- Do not claim Tabula atlas OOD for the A-D R^2 ranges. Call them a paired held-out-species evaluation.
- Do not write "nearly 3x" unless you also keep the raw accuracies. Prefer the raw numbers.
- Provenance limits stay in `interview_defense.md`.
- Recruiter-facing prose stays plain.

## Out of scope

Do not parse a JD. Do not call Polar. Do not edit `knowledge/evidence_bank.yaml` or `resumes/base/JZ_resume.tex`.
