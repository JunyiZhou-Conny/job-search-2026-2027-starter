# Cloud Agent prompt — finish Simplify profile cleanup (2026-07-30)

Paste everything below the line into a **Cloud** agent session
(Cursor Desktop → agent mode dropdown → Cloud, or Agents Window → `/in-cloud`).

Do **not** use the local Browser tab / `cursor-ide-browser` instructions from the older
handoff file. You are on a remote VM with computer use; drive the desktop browser there.

---

I need you to finish cleaning up my Simplify profile on a Cloud Agent VM.

**Profile URL:** https://simplify.jobs/profile/11784d34-a1d0-4cec-b258-a4efb11116eb

**Paste-ready source of truth (follow literally — invent nothing):**
`generated/simplify_profile_2026-07-30.md`

It was derived from `resumes/base/JZ_resume.tex` and `knowledge/evidence_bank.yaml`.
Never add a skill, tool, metric, employer, title, or date that is not in those files.
If something seems missing, ask me — do not fill the gap yourself.

## Auth — do this before any edits

1. Open the profile URL in the VM browser.
2. If you hit a login wall:
   - Prefer asking me to **Take Control** of the remote desktop and sign in myself
     (safest). Never print or echo passwords into chat.
   - If secrets `SIMPLIFY_EMAIL` and `SIMPLIFY_PASSWORD` are present as environment
     variables, you may use them only to fill the email/password form — never quote
     their values back to me. If login is Google/SSO/magic-link instead, stop and ask
     me to take control.
3. Confirm with a screenshot that the signed-in profile shows **Junyi Zhou** before
   the first edit.

## Already done on the live profile (do NOT redo)

A prior local session already completed and saved these. Verify they are still true;
do not delete or recreate them unless verification shows they reverted.

| Item | Expected live state |
|---|---|
| Cloud Architect — Harvard Medical School | **Gone** (deleted; was fabricated) |
| Research Software Engineer — Emory | **Gone** (deleted; Bou-Nader work under invented title + fabricated K8s/Redis) |
| Full-Stack Engineer, Scrum Master — Emory University | Present: **Jan 2024 – Aug 2025**, **Part-Time**, Entry 5 description (Airway chatbot; company kept as Emory University, not Pediatric Hospital) |
| Graduate Researcher — Harvard | Present: **Part-Time**, Entry 1 description (Cross-Species Drug Translation…); no diffusion models, no GENOT |
| Data Analyst — Emory | Present: **Part-Time**, Entry 3 description (AlphaFold Bou-Nader) |

There may be a **half-filled Add Experience draft** for the FASRC entry left open from
the interrupted local session. Cancel/discard it if present, then add Entry 2 cleanly.

## Remaining tasks, in order

Simplify's Experience Type dropdown only has: Internship / Full-Time / Part-Time /
Contract. Use **Part-Time** wherever the paste-ready file says Research / Part-Time /
Project.

1. **Add Entry 2** — Independent Project — ML Systems Engineer  
   Company: Harvard University (FASRC Cannon detail belongs in the description)  
   Location: Boston, MA  
   Type: Part-Time  
   Dates: Jun 2026 – Present (check "I currently work here")  
   Description: Entry 2 block from the paste-ready file

2. **Add Entry 4** — Research Assistant  
   Company: Emory University  
   Location: Atlanta, GA  
   Type: Part-Time  
   Dates: Dec 2023 – May 2024  
   Description: Entry 4 block (Carrubba & Estrada / Comput-Leg)

3. **Update Machine Learning Researcher** (Entry 6)  
   Type → Part-Time  
   Replace description with Entry 6 text from the file  
   Dates should stay Oct 2024 – Jan 2025

4. **Fix Harvard education**  
   Degree/field → **Health Data Science** (not bare "Data Science")  
   **Clear the GPA field** (repo has no Harvard GPA on record; the "4" is unsupported)

5. **Set GitHub URL** to `https://github.com/JunyiZhou-Conny`

6. **Delete these skill tags** (confirm none are resume/evidence-bank backed):  
   Kubernetes, Go, Redis, Node.js, Spring, Jenkins, GitHub Actions, Grafana,
   Prometheus, Bedrock, DynamoDB, EBS, EMR, Tableau, A/B testing frameworks,
   **OAuth2, JWT** (keep Auth0)

   Keep SageMaker AI, Lambda, HIPAA, HIPAA compliance unless I say otherwise.

7. **Add every skill** from the eight blocks in section 1 of
   `generated/simplify_profile_2026-07-30.md`. Highest-value missing ones: PyTorch,
   RAG, LoRA, fine-tuning, vector search, OpenAI API, SLURM, HPC. Report which
   custom tags Simplify rejected.

## Working style

- Snapshot/screenshot after each material save — Simplify's React UI sometimes
  fails to persist on the first click.
- Confirm with me before any **new** deletion not listed above.
- If skill-tag entry is slower than hand-pasting (~120 tags), stop after a few and
  say so — I will paste the skill blocks myself.
- Do not invent wording. Copy from the paste-ready file.
- Do not submit applications or send outreach.

## When finished

Reply with a short checklist: what you verified as already done, what you changed,
which skill tags failed to add, and one screenshot of the final Work Experience
section plus the Portfolio & Skills section.
