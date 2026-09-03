# Twitch, Software Engineer I, Commerce Engineering. Review packet 2026-09-03

Prioritized lane. Greenhouse gate G1 (fill plus human review). The agent stops before Submit. Junyi decides.

## 1. Company

Twitch is a live streaming service and an Amazon subsidiary (Amazon bought it in 2014; the JD's pay text says "Your Amazon package" and lists an Amazon employee discount). Communities form around gaming, entertainment, music, sports, and cooking. The JD calls it the world's biggest live streaming service; read that as marketing.

## 2. Role

Commerce Engineering sits under the Community org and owns Subscriptions, Gifting, Bits, Hype Train, and Turbo. Greenhouse lists the department as Community Growth. Job ID TW9135.

| JD field | What it says |
|---|---|
| You will | Build interactive viewer support experiences; architect scalable applications for millions of concurrent users; collaborate across teams; turn customer feedback into features. |
| You have | Verbal and written communication; a track record of consumer facing products; modern languages and frameworks; algorithms, data structures, schema design; Bachelor's in CS or equivalent experience. |
| Bonus | Mobile development; Golang, TypeScript/React; AWS ECS, DynamoDB, Lambda, SQS, Step Functions; passion for gaming or streaming. |
| Location | On site, Seattle, WA or San Francisco, CA. The Greenhouse office field says Seattle. |
| Pay | Base $110,500 to $160,000 (Seattle); $127,100 to $185,000 (San Francisco). Sign on and RSUs on top. |
| Unknown | Start date, whether a January 2027 start is accepted, years of experience, team inside Commerce, interview loop. First published 2026-03-25, updated 2026-09-01, so it may be evergreen. |

## 3. Why prioritized

The signal is list membership. Twitch is on `knowledge/company_lists.yaml` `startup_or_scaleup`; parent Amazon is on `big_tech`. `knowledge/application_priority.yaml` `subfields` maps those to `startup` and `prestige`, and `do_not_conflate` says a company_lists class is a sort hint, not a confirmed weight. Twitch is not in `confirmed_prioritized`. `docs/state/decisions.tsv` (tick-0903T13) routed it here as a suggestion.

My judgment. The startup label is wrong; a 2014 Amazon subsidiary is not early or scaling. Prestige via Amazon is the only real signal. On merit this row is regular. There is no free response to write and no JD specific resume edit the bank supports. It reaches Junyi anyway because the broad sponsorship question is stop the line. The label stays a suggestion, and I lean regular.

## 4. Why Junyi fits

- Consumer facing product track record: `airway_chatbot` (knowledge/evidence_bank.yaml). React frontend, Flask REST API, Auth0, MongoDB, deployed on AWS Elastic Beanstalk and CloudFront, Agile team of 6 with a clinician feedback loop. Users are residents and clinicians, not a mass consumer audience.
- Modern languages and frameworks, plus the TypeScript/React bonus: skills `python` (strong), `javascript` (working, React authorship confirmed 2026-07-29), `sql` (working), `docker` (working). All `verified: true`.
- Schema design, algorithms, data structures: `compleg_uk_nz` designed a relational schema up front (ER diagram, 10 normalized member tables, 57,000+ measured records); `transformer_reimpl` rebuilt the Transformer from scratch, 9.38 BLEU validated against nn.Transformer.
- AWS bonus: skill `aws` (working, verified) covers Elastic Beanstalk and CloudFront; `compleg_uk_nz` adds EC2 and S3 via boto3; config/profile.yaml `certifications` lists AWS Cloud Practitioner, AI Practitioner, and ML Associate.
- Robust systems under failure: `autoresearch_cellot` ran 338 SLURM experiments with checkpoint/resume, idempotent run steps, and a spend ceiling with fallback. Cluster scheduling, not consumer traffic.

Gaps: no Golang; no mobile; no millions of concurrent users evidence; ECS, DynamoDB, SQS, Step Functions are not in the bank; degree is B.S. Applied Mathematics and Statistics plus SM Health Data Science, not CS (knowledge/written_response_bank.yaml `do_not`: do not upgrade Emory to a CS degree); Twitch familiarity unknown.

## 5. Resume selected

Cluster `cloud_swe`, default `2026-08-24_cloud-swe_v1.3` (knowledge/target_roles.yaml `role_clusters.cloud_swe.default_resume`). File `resumes/cloud_swe/2026-08-24_cloud-swe_v1.3.tex` exists. No v1.3 PDF is in the repo; run `./scripts/compile_resume.sh cloud_swe` before upload (resumes/README.md: do not upload the .tex).

Tailoring is not justified beyond v1.3 as is. It already carries React, Flask, Auth0, MongoDB, AWS, Docker, and JavaScript on the Languages line. The one evidence backed edit (evidence_bank.yaml `tailoring_policy.encouraged`) would swap the AlphaFold entry for `compleg_uk_nz` schema and ETL bullets to answer "schema design" directly. That is a v1.4 with its own data/resume_versions.csv row, not this packet. Skip unless Junyi wants it.

## 6. Form answers

20 required questions (19 listed plus a Location field), 4 optional, one voluntary EEO item, optional education. Source keys are in `knowledge/form_strategy.yaml` unless another file is named.

| # | Question | Proposed answer | Source or reason |
|---|---|---|---|
| 1-4 | First name, last name, email, phone | Junyi Zhou; profile values | config/profile.yaml `legal_name`, `email`, `phone` (Copilot fills identity) |
| loc | Location | Boston, MA | config/profile.yaml `location` |
| 5 | Resume/CV | cloud-swe v1.3 PDF, compiled first | knowledge/target_roles.yaml `role_clusters.cloud_swe.default_resume` |
| 6 | Cover letter (optional) | leave empty | `later_not_this_run.cover_letter`; no Twitch letter in the bank |
| 7 | LinkedIn (optional) | https://www.linkedin.com/in/junyi-zhou-270208247 | config/profile.yaml `linkedin` |
| 8 | Website (optional) | https://connyzhou.com | `always.personal_website` |
| 9 | Are you familiar with Twitch? | leave_for_junyi | personal usage fact with no source; `leave_for_junyi` examples |
| 10 | Currently a Twitch employee? | No | `always.employed_by_this_company_before` (reason: first intern / first job) |
| 11 | Open to relocation? Pick a city. | Seattle, WA | `always.open_to_relocating` Yes; `always.location_interest_pick_one`. Seattle is the posting office. Flip to San Francisco, CA if preferred; row 22 follows. |
| 12 | Current Amazon or subsidiary employee? | No | `always.employed_by_this_company_before` reason |
| 13 | Previously applied to Amazon or subsidiary? | No (confirm) | data/applications.csv J20260720-011 is Amazon, status saved, never applied; the 2026-09-03 Simplify export has no Amazon row. History before 2026-07-20 is not in the repo. |
| 14 | Previously employed by Amazon or subsidiary? | No | `always.employed_by_this_company_before` |
| 15 | Non compete or restrictive agreement? | No (confirm) | inferred from `always.employed_by_this_company_before` reason (no prior employer); no standing key |
| 16 | Legally eligible to begin employment immediately? | leave_for_junyi | wording is "immediately"; knowledge/work_authorization.yaml `earliest_full_time_start` is 2027-01-18. Closest rule `authorized_for_any_employer` Yes covers "authorized", not "immediately". |
| 17 | Need now or in the future any immigration support or sponsorship from Amazon? | leave_for_junyi | knowledge/work_authorization.yaml `form_strategy.visa_sponsorship` is pending_owner_confirmation; `never_lie_to_bypass_ats: true`; open owner decision in docs/policy/SUBMIT_ROLLOUT.md. The widget text names F-1 CPT letters and STEM OPT plans. |
| 18 | Held H-1B in the preceding 6 years? | No | knowledge/work_authorization.yaml `current_status` F-1; `form_strategy.h1b_named_question_only` No |
| 19 | Country of citizenship | leave_for_junyi | not stated in config/profile.yaml or knowledge/work_authorization.yaml; `clicker_cheap_cuts.do_not_invent` lists citizenship |
| 20 | Permanent resident elsewhere since last citizenship? | leave_for_junyi | no source; F-1 is temporary and the question excludes it, so the answer rests on facts outside the repo |
| 21 | Export control country (citizenship or LPR, whichever is latest) | leave_for_junyi | same as 19. `us_person_export_control` says he is not a U.S. Person, so United States is not the answer. |
| 22 | Expected base pay (optional) | 110500 | `always.salary_or_expected_compensation.if_page_lists_a_range` says type the listed minimum. Seattle minimum $110,500; San Francisco minimum $127,100 if row 11 flips. |
| 23 | Consider for future Twitch opportunities? | leave_for_junyi (suggest Yes) | no standing rule; talent pool consent only |
| EEO | Voluntary disability self identification (optional) | No, I do not have a disability and have not had one in the past | `always.disability_status` |
| edu | Education block (optional) | Harvard, SM Health Data Science, 2026-12-18; Emory, B.S. Applied Mathematics and Statistics, 2025-05; discipline Data Science, then Computer Science | `always.graduation_date_on_forms`; `always.education_discipline_or_field_of_study`; config/profile.yaml `education_history` |

No free response question on this form. No cover letter.

## 7. Referral consideration

`data/contacts.csv` and `data/networking.csv` are header only. No Twitch or Amazon contact exists. Do not hold the row for a referral (knowledge/application_priority.yaml `referral_risk` rule). Recommendation. Submit does not wait on one. A perspective ask to a Twitch Commerce engineer is optional later, draft only, never sent from this repo.

## 8. Uncertain

- Broad sponsorship answer (q17): owner decision open since 2026-09-03.
- Citizenship, permanent residence, export control country (q19, q20, q21): not in the repo.
- Begin immediately (q16): earliest full time start is 2027-01-18; the JD gives no start date.
- Whether this posting accepts a January 2027 new grad start: the JD is silent.
- Twitch familiarity (q9) and future opportunities consent (q23): Junyi only.
- Any Amazon application before 2026-07-20 (q13) and any non compete (q15): confirm.
- v1.3 PDF is not compiled in the repo.
- Prioritized weight is a company_lists suggestion, not confirmed.

## 9. Readiness

ready_for_junyi_review. Greenhouse is at G1 (config/submit_gates.yaml; docs/policy/SUBMIT_ROLLOUT.md), so fill plus human review is open and `generated/apply_runs/2026-09-03T13/twitch-swe-i.preflight.json` passed with no duplicate. Every required question has a sourced answer or leave_for_junyi; 7 are leave_for_junyi (q9, q16, q17, q19, q20, q21, q23). q17 is stop the line until Junyi decides, and prioritized rows never Submit without him.

## 10. Link

https://job-boards.greenhouse.io/twitch/jobs/8459320002

Files consulted: config/profile.yaml, config/submit_gates.yaml, knowledge/evidence_bank.yaml, knowledge/work_authorization.yaml, knowledge/form_strategy.yaml, knowledge/application_priority.yaml, knowledge/company_lists.yaml, knowledge/target_roles.yaml, knowledge/written_response_bank.yaml, docs/apply/PRIORITY.md, docs/apply/written_answers/README.md, docs/policy/SUBMIT_ROLLOUT.md, docs/state/decisions.tsv, data/contacts.csv, data/networking.csv, data/applications.csv, data/resume_versions.csv, data/imports/simplify/2026-09-03_simplify_download.csv, resumes/README.md, resumes/cloud_swe/2026-08-24_cloud-swe_v1.3.tex, generated/apply_runs/2026-09-03T13/twitch-swe-i.preflight.json, Greenhouse API job 8459320002 with questions (fetched 2026-09-03).
