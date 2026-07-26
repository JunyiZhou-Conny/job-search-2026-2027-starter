# Analyze and Tailor for a High-Interest Adjacent Role

You are analyzing a job that may not fit cleanly into the candidate’s existing resume clusters but may represent an important recurring career direction.

The candidate currently maintains these primary resume clusters:

1. Cloud / Software Engineering
2. Data / Machine Learning
3. Healthcare / Bio-AI

The candidate is also strongly interested in emerging roles involving:

* AI infrastructure
* ML systems
* model inference
* model serving
* distributed training or inference
* AI agents and agent infrastructure
* GPU or accelerator workloads
* high-performance computing
* cloud AI infrastructure
* developer tooling for AI systems

Do not assume that this job is an isolated exception. Determine whether it is part of a recurring role family that should eventually become a new resume cluster.

The job description will be provided below or attached to this command.

---

## Primary Objective

Produce an evidence-backed strategy for applying to this role without fabricating skills or mechanically copying every keyword from the job description.

The analysis must answer:

1. What kind of role is this?
2. How important is it to the candidate?
3. How well does the candidate currently match?
4. Which existing experiences are directly relevant?
5. Which experiences are adjacent but transferable?
6. Which requirements are genuinely missing?
7. Should the candidate apply now?
8. How much resume customization is justified?
9. Should this role contribute toward a new recurring resume cluster?
10. What networking and skill-building actions should follow?

---

## Required Repository Context

Before analyzing the job, inspect the repository and read all relevant available files, including:

```text
config/profile.yaml
knowledge/evidence_bank.yaml
knowledge/target_roles.yaml
knowledge/work_authorization.yaml
resumes/base/
resumes/clusters/
data/applications.csv
data/resume_versions.csv
data/role_patterns.csv
.cursor/rules/
AGENTS.md
```

Also inspect relevant project documentation, source code summaries, READMEs, and prior resume bullets when available.

Do not rely only on the current resume. The resume may omit relevant experience that exists elsewhere in the repository.

Do not assume a skill is real merely because it appears in a Skills section. Verify it against the evidence bank, project files, coursework, certifications, or other documented work.

---

## Truth and Evidence Rules

Never fabricate or exaggerate:

* technologies
* responsibilities
* project scope
* performance results
* team size
* deployment scale
* system architecture
* metrics
* employment dates
* degree dates
* work authorization
* publications
* production usage

For every job requirement, classify the candidate’s evidence as:

```text
PROVEN
ADJACENT
MISSING
UNCERTAIN
```

Definitions:

### PROVEN

The candidate has direct, documented evidence and could reasonably discuss the experience in an interview.

### ADJACENT

The candidate has transferable experience, but not the exact technology, system, scale, or environment described in the job.

Examples:

* Running AlphaFold workloads on GPU HPC nodes is adjacent to inference infrastructure.
* Implementing a Transformer in PyTorch is adjacent to production Transformer serving.
* Using Spark is adjacent to distributed systems but is not evidence of consensus protocol expertise.
* Building an agentic RAG application is adjacent to agent infrastructure but is not automatically evidence of distributed agent runtime design.

### MISSING

There is no documented evidence of the skill or responsibility.

### UNCERTAIN

The repository suggests possible experience, but the evidence is incomplete. Add it to a factual clarification list rather than assuming it is true.

Never convert ADJACENT evidence into PROVEN evidence merely to improve keyword coverage.

---

## Phase 1: Parse the Job Description

Extract and normalize:

```text
company
role_title
location
employment_type
internship_term
degree_requirements
graduation_requirements
required_languages
required_frameworks
required_systems_knowledge
preferred_skills
primary_responsibilities
technical_domain
work_authorization_language
sponsorship_language
posting_date
application_deadline
```

Separate requirements into:

```text
critical
important
preferred
decorative
```

“Decorative” means language that describes an ideal candidate but is unlikely to be a true screening requirement.

Identify the role family using one primary and up to two secondary labels:

```text
ai_infrastructure
ml_systems
inference_systems
model_serving
distributed_systems
gpu_accelerator
compiler_systems
cloud_infrastructure
backend_platform
agent_infrastructure
applied_ml
bio_ai
data_engineering
general_swe
other
```

---

## Phase 2: Determine Strategic Importance

Calculate these dimensions separately:

```text
interest_score: 0–100
technical_fit_score: 0–100
evidence_coverage_score: 0–100
career_direction_score: 0–100
application_urgency_score: 0–100
```

Do not combine personal interest and current technical fit into one number.

A job may be:

```text
high interest + stretch fit
```

That is a valid and important category.

Classify:

```text
fit_band:
  strong
  competitive
  stretch
  remote

pursuit_lane:
  core
  broad
  practice
```

Definitions:

### Core

The candidate cares deeply about the opportunity and should invest meaningful effort.

A Core role may still be a stretch role.

### Broad

The opportunity is relevant enough to apply to, but does not justify extensive customization or networking.

### Practice

The role is unlikely to convert into a final job but may provide OA or interview practice. Limit time investment.

Do not downgrade a role from Core solely because the candidate lacks some exact qualifications.

Do not use sponsorship uncertainty as the primary determinant of pursuit lane.

---

## Phase 3: Build the Evidence Map

Create:

```text
jobs/<company-role-slug>/evidence_map.md
```

Use this structure:

| JD requirement | Importance | Candidate evidence | Evidence source | Classification | Interview depth | Resume usable | Notes |
| -------------- | ---------: | ------------------ | --------------- | -------------- | --------------- | ------------- | ----- |

For each requirement, identify:

* exact matching evidence
* transferable evidence
* missing evidence
* evidence that needs user confirmation

Also summarize:

```text
Top five strongest matches
Top five most important gaps
Misleading keywords that must not be added
Experiences currently hidden by the generic resume
```

---

## Phase 4: Decide the Tailoring Level

Choose exactly one:

```text
cluster_default
cluster_light
job_specific
job_specific_plus_build
```

### cluster_default

Use an existing cluster resume with no meaningful change.

Appropriate when the role is routine and the existing resume already presents the right evidence.

### cluster_light

Use an existing cluster resume but:

* reorder a few bullets
* adjust the summary of one or two projects
* reorder Skills
* change no more than approximately 15–20% of the content

### job_specific

Create a dedicated version because:

* the role is high interest
* relevant evidence exists but is buried
* project ordering needs to change substantially
* the job combines multiple existing clusters
* the terminology and technical emphasis differ materially from existing resumes

### job_specific_plus_build

Create a dedicated version and recommend a proof-building project because:

* the candidate is highly interested
* meaningful adjacent evidence exists
* important technical gaps remain
* similar roles are expected to recur
* a small project could create genuine evidence for future applications and interviews

Do not delay the application solely because a proof project is not yet complete.

---

## Phase 5: Select the Parent Resume

Determine the closest parent resume.

Possible outputs:

```text
cloud_swe_vX.Y
data_ml_vX.Y
health_ai_vX.Y
hybrid of two existing clusters
new role-specific document from the base resume
```

Explain why the selected parent is closest.

A job-specific resume must preserve a parent version and change log.

Suggested version format:

```text
<company>_<role_family>_v1.0
```

Example:

```text
etched_inference_systems_v1.0
```

---

## Phase 6: Create the Job-Specific Resume Strategy

Create:

```text
jobs/<company-role-slug>/resume_strategy.md
```

Include:

### Recommended section order

Determine which experiences should appear first.

The ordering must reflect relevance to the target role, not chronology or the ordering in the base resume.

### Projects to retain

Explain why each retained project supports the JD.

### Projects to shorten

Identify projects that remain useful but should receive fewer bullets.

### Projects to remove

Remove projects only when space is needed and the project contributes little to the role.

### Skills ordering

Put the most relevant verified skills first.

Do not add unsupported technologies.

### Bullet transformation plan

For every proposed bullet change, record:

```text
original bullet
proposed bullet
evidence source
JD concept supported
classification: proven or adjacent
risk of overstatement
```

The goal is not to hit every keyword.

The goal is to make the strongest truthful evidence visible in the first 10–20 seconds of review.

---

## Phase 7: Generate the Resume

Create:

```text
resumes/job_specific/<company-role-slug>_v1.tex
```

Also create:

```text
resumes/job_specific/<company-role-slug>_v1_change_log.md
```

Requirements:

* one page unless the repository explicitly allows otherwise
* ATS-readable
* truthful
* no fabricated skills
* no exposed passwords or credentials
* no test-account passwords
* no unsupported performance metrics
* accurate degree title
* accurate graduation date
* accurate employment and research dates
* consistent punctuation
* consistent tense
* relevant GitHub or portfolio links only
* no unnecessary footnotes
* compile successfully

Compile the LaTeX resume and validate the resulting PDF.

If the resume exceeds one page:

1. remove low-value bullets
2. shorten less relevant projects
3. reduce redundant skills
4. do not reduce readability solely to force one page

---

## Phase 8: Evaluate Skill Gaps

Create:

```text
jobs/<company-role-slug>/gap_analysis.md
```

Divide gaps into:

```text
resume_gap
evidence_gap
knowledge_gap
experience_gap
eligibility_gap
```

Definitions:

### Resume gap

The candidate has the experience, but it is not visible in the current resume.

### Evidence gap

The candidate may know the skill, but there is no project, code, metric, or documented use proving it.

### Knowledge gap

The candidate has not yet learned the concept deeply enough.

### Experience gap

The candidate lacks practical use in a realistic project or environment.

### Eligibility gap

The role has a concrete graduation, enrollment, citizenship, clearance, location, or timing condition.

For each gap, recommend one of:

```text
clarify
rewrite existing evidence
build small proof project
complete targeted study
accept as a gap and apply anyway
do not apply
```

Do not recommend building a large project for every missing keyword.

Focus on gaps that recur across multiple high-interest jobs.

---

## Phase 9: Detect Emerging Resume Clusters

Maintain:

```text
data/role_patterns.csv
```

Suggested fields:

```text
pattern_id
role_family
date_first_seen
date_last_seen
jobs_seen
jobs_applied
average_interest_score
average_fit_score
recurring_required_skills
existing_cluster_coverage
new_cluster_recommended
notes
```

After analyzing the job, update the role-family pattern.

Recommend creating a new permanent cluster only when at least one of the following is true:

1. At least five high-interest jobs belong to the same role family.
2. The candidate expects this role family to be a major application target.
3. Existing clusters repeatedly require more than approximately 25–30% restructuring.
4. The same project ordering, skills emphasis, and narrative recur across multiple jobs.
5. The role family has a distinct interview preparation track.

Potential new cluster:

```text
ml_systems_ai_infrastructure
```

Do not create a new cluster automatically after one job.

Output:

```text
cluster_status:
  isolated_case
  emerging_pattern
  cluster_recommended
```

---

## Phase 10: Proof-Building Sprint

If `tailoring_mode` is `job_specific_plus_build`, create:

```text
jobs/<company-role-slug>/proof_sprint.md
```

The proof sprint should:

* be realistically completable
* address a recurring gap
* produce code or measurable output
* be relevant to multiple future roles
* include tests
* include documentation
* include performance or correctness evaluation where appropriate
* not be added to the resume until implemented

For AI infrastructure and inference roles, possible themes include:

* Transformer inference benchmarking
* prefill versus decode latency
* batching and throughput
* KV-cache behavior
* PyTorch Profiler
* `torch.compile`
* vLLM or SGLang after actual implementation
* distributed inference fundamentals
* GPU memory profiling
* model quantization
* serving API design
* fault handling and reproducibility
* comparison of inference backends

Do not prescribe every technology. Select the smallest project that addresses the most recurring gap.

---

## Phase 11: Networking Plan

Create:

```text
jobs/<company-role-slug>/outreach_plan.md
```

Recommend search targets, not invented people.

Prioritize:

1. Harvard alumni at the company
2. Emory alumni at the company
3. engineers in the exact role family
4. current or former interns
5. early-career recruiters
6. hiring managers
7. people with a similar career transition

Generate:

* LinkedIn search queries
* Google search queries
* suggested target titles
* a short connection message
* a follow-up after acceptance
* a request for a 15-minute informational conversation
* a later referral request only after meaningful interaction

Each outreach message must reference a real overlap:

* shared school
* related project
* relevant technical area
* specific company work
* similar transition

Do not generate generic praise.

Do not automatically send any message.

---

## Phase 12: Application Recommendation

Produce one recommendation:

```text
apply_now
apply_after_quick_clarification
apply_after_light_resume_update
do_not_apply
```

Default toward applying when:

* interest is high
* hard eligibility is not clearly violated
* at least some relevant or transferable evidence exists
* the posting encourages candidates who do not meet every requirement

Do not require a perfect match.

Do not wait for a long proof-building sprint before applying.

Also recommend:

```text
application_effort_minutes
recommended_resume_version
networking_priority
proof_sprint_priority
interview_preparation_priority
```

---

## Phase 13: Review Queue

Any uncertain factual claims must be added to:

```text
generated/review_queue.csv
```

Examples:

* actual depth of C++ experience
* actual Linux usage
* whether profiling tools were used
* whether distributed execution was implemented
* whether a project had production users
* whether a stated metric is verified
* internship enrollment eligibility
* graduation-date conflicts

Do not block the entire analysis for minor uncertainty.

Use the strongest safe wording and visibly flag facts requiring confirmation.

---

## Phase 14: Final Output

At the end, produce:

```text
1. Role classification
2. Strategic importance
3. Fit assessment
4. Proven evidence
5. Adjacent evidence
6. Missing evidence
7. Hard eligibility review
8. Recommended pursuit lane
9. Recommended tailoring mode
10. Recommended parent resume
11. Resume changes completed
12. Skills requiring confirmation
13. Application recommendation
14. Networking plan
15. Proof sprint recommendation
16. Emerging cluster status
17. Files created or modified
18. LaTeX compilation result
19. Manual review items
20. Exact next actions
```

The exact next actions should be ordered and concrete.

Example:

```text
1. Confirm graduation and internship eligibility.
2. Review three flagged C++ and Linux claims.
3. Approve the job-specific resume.
4. Submit the application.
5. Find three relevant employees or alumni.
6. Send two personalized outreach messages.
7. Begin the selected proof sprint.
8. Add this role to the emerging AI infrastructure pattern.
```

---

## Human-Control Rules

The system may automatically:

* parse the JD
* propose labels
* analyze evidence
* generate files
* rewrite evidence-backed resume bullets
* compile LaTeX
* generate networking targets
* generate outreach drafts
* update an unconfirmed review queue
* recommend a new cluster

The system must not automatically:

* invent qualifications
* overwrite a manually approved label
* submit an application
* answer work-authorization questions without review
* send outreach
* request a referral
* create calendar events without approval
* add an unfinished proof project to the resume
* create a permanent new cluster after only one occurrence

When confidence is below 0.80, explicitly mark the conclusion as requiring review.

When confidence is at least 0.90 and the conclusion does not involve eligibility, immigration, or unsupported experience, the system may write the proposed label while preserving the evidence and confidence fields.

---

## Job Description

Analyze the job description supplied with this command. If the job description is stored in a file, use that file as the source of truth.

Begin by auditing the relevant repository context and then execute all applicable phases above.

### How to use

1. Save the JD under `jobs/inbox/<company-role>.md` (or paste it in chat).
2. Run `/analyze-adjacent-role`.
3. Say: `Analyze jobs/inbox/<company-role>.md using the adjacent-role workflow.`

Keep these dimensions separate:

```text
Interest: high
Fit: stretch
Pursuit lane: core
Tailoring: job-specific
Evidence: partially adjacent
Application decision: apply now
```

That prevents rejecting an exciting stretch role, or rewriting the resume as if every JD skill is already proven.
