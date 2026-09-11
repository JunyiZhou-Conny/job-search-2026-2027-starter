# Interview defense. `ai_infra_v1`

These boundaries used to leak onto the resume as disclaimers. They stay here and in the evidence bank.

## autoresearch_cellot

Expect. How many runs are in the public repo?
Answer. Public `results/experiments.csv` is header-only. 338 / 318 / 79.3 h is the 2026-07-29 Cannon count, `USER_REPORTED`, `resume_ok: true`. Walk `autoresearch.py`, `proposer.py`, `director.py`, `policy.validate()`, `cluster.yaml`.

Expect. Did an LLM direct the search?
Answer. No. Default reasoner is RuleReasoner. `AR_REASONER=rule`. The LLM client exists, with token and cost accounting and a spend ceiling that falls back to the rule planner. It has not been exercised on recorded runs. Do not let the resume's "optional LLM planner infrastructure" sentence become "an LLM ran the experiments."

Expect. Did you reduce cost 200-500x?
Answer. No. That figure is FASRC GPU vs CPU fairshare policy. CPU default is a design choice in `cluster.yaml` comments.

Expect. Is this an agent?
Answer. No. Call it closed-loop or self-directed. Bank `control_logic` forbids agentic / LLM-agent wording.

Expect. What is `serial_requeue` / `cache/last.pt`?
Answer. SLURM requeue plus resume from the last checkpoint. The resume says "resumed preempted jobs from the last checkpoint." The path names are implementation details.

## job_search_os

Expect. Does this system apply for you by itself?
Answer. No. Polar Local may Submit after listed identity and writing gates. Cloud G2/G3 stay closed. Prioritized Polar rows need `writing_log`. The system does not send messages or apply on its own. The resume states the positive form: Submit is allowed only after those checks.

Expect. Why is the title not Job Search OS?
Answer. Recruiter-facing title leads with the capability. The project is still this repo. The first bullet names job applications. Do not claim a different product domain.

Expect. How many applications did it submit?
Answer. Do not answer with `data/applications.csv` applied counts. Those are ledger statuses, `resume_ok: false`.

Expect. Why is Computer Use not the production operator?
Answer. Polar Local on the Mac is. Computer Use is hands-only on a compiled action sheet. The resume says "browser steps follow a compiled action sheet rather than rediscovering the form."

Expect. What are G2 and G3?
Answer. Cloud Submit ladder stages. Both closed as of 2026-09-08. Keep them off the resume.

## cellot_wyss

Expect. Are the R^2 numbers Tabula atlas OOD?
Answer. No. They are the Mac Stage 1 LPS / rat-in-train prior living in the AutoResearch public insights. Resume ranges 0.85-0.90 and 0.65-0.67. The resume calls this a paired held-out-species evaluation. Do not imply Tabula atlas OOD.

Expect. Did you ship DatasetHandle and FrozenAE?
Answer. Not on current `origin/main` `109bf12`. PRs 8-10 are open. Do not claim them.

Expect. 180+ trained models?
Answer. Hub docs say that. It is not live-countable without the gitignored results tree. `resume_ok: false`.

Expect. Is this drug translation?
Answer. Species translation is shipped. Treatment composition is not implemented.

Expect. What are decoded-frame metrics?
Answer. Gap-closed and R^2 computed after AE decode, not in the raw gene frame. The resume says "decoded-space gap-closed."

## mixhvg_py

Not on this page. Keep the answers if an interviewer opens the GitHub org and asks.

Expect. Did you invent mixhvg?
Answer. No. Zhao et al. 2024. This is a validated Python port with an AnnData API.

Expect. Is every method bit-exact?
Answer. seuratv3 / seuratv1 match at reported precision. scran_pos is seed-dependent. mv_ct and mv_nc do not match and are excluded.

Expect. Is it used in production?
Answer. speciesOT specs set `hvg_method: mixhvg`. Do not claim other production users.
