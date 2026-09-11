# Semantic review. `health_ai_v1`

Heuristic `arena()` was not used as recruiter judgment.

Two structurally different candidates were written and fact-checked before this review.

## Candidates

**A. Clinical system plus translational software.** Airway, speciesOT, mixhvg-py.

**B. Clinical system plus imaging.** Airway, speciesOT, pneumonia. Replaces mixhvg with the chest X-ray Kaggle.

A third sketch, Airway plus speciesOT plus S-Seg method-only, was drafted and rejected before Arena. S-Seg has `interview_depth: weak` and no usable results. It did not enter.

## Evidence auditor

Airway verbs stay Built and Worked. No Architected. No Led. No Kubernetes.

speciesOT does not claim drug composition or Tabula OOD.

mixhvg credits Zhao et al. and does not claim mv_ct match.

pneumonia in candidate B is factually clean and already used on `ml_ai_v1`.

## Technical recruiter

Candidate A. Clinical product first. Then mouse-to-human translation. Then an HVG method. The page says Health AI in 15 seconds.

Candidate B. Also readable. The third heading is a course radiograph classifier. It looks like ML/AI's pneumonia block pasted under a clinical header.

Preference. A.

## Domain specialist

Is the biology responsible?

Candidate A. speciesOT is species translation. mixhvg is a validated HVG port. Together they cover translational ML and biomedical software. The gene-space flip is framed as a biological convenience check, not a leaderboard brag.

Candidate B. pneumonia is honest medical imaging and not a clinical trial. It does not add single-cell biology.

S-Seg as a heading would force a specialist to open a repo full of `NotImplementedError`.

Preference. A.

## Skeptical technical interviewer

Airway "Scrum Master" plus "team of 6" can be heard as Led. The page does not say Led. Be ready to describe the team role without upgrading it.

speciesOT gene-space sentence is an interpretation of a measured flip, not a new metric. Allowed.

mixhvg "used by speciesOT specs" is in the bank notes. Do not say other production users.

Candidate B's pneumonia 0.959 is fine and redundant with `ml_ai_v1`.

Preference. A.

## Disagreements

The recruiter liked pneumonia's 0.959 more than mixhvg's Jaccard. The domain specialist did not. Graft decision. Keep mixhvg. Do not add a pneumonia bullet under speciesOT.

No S-Seg one-liner. A heading with no result wastes the scan.

## Pairwise question

Would a health-AI or computational-biology reader see why this PDF exists next to `ml_ai_v1`?

Yes. Airway is only here. mixhvg's job here is HVG biology, not a SWE test harness. speciesOT is framed as translation, not as a hub.
