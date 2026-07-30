# Handoff prompt — Simplify profile cleanup (2026-07-30)

Copy everything below the line into a fresh agent session.

---

I need you to clean up my Simplify profile using a browser.

**Profile URL:** https://simplify.jobs/profile/11784d34-a1d0-4cec-b258-a4efb11116eb

**All the exact content you need is already written.** Read this file first and follow it
literally — do not compose new wording:

`/Users/conny/Desktop/job-search-2026-2027-starter/generated/simplify_profile_2026-07-30.md`

It has paste-ready skill blocks, full work-experience entries (title / company / location /
dates / description), and a table of skills to delete with the reason for each.

**Hard rule: invent nothing.** Use only content from that file. It was derived from
`resumes/base/JZ_resume.tex` and `knowledge/evidence_bank.yaml`, which are the sources of
truth for this repo. Never add a skill, tool, metric, employer, title, or date that is not in
those files. If something seems missing, ask me — do not fill the gap yourself.

## Step 0 — prove you have a working browser before you touch anything

Do this first and report the result to me. Do not start the tasks, and do not open the profile
URL, until it passes.

1. Check that browser tools are actually registered in your session — search the available MCP
   tools for `browser` and confirm you can see `browser_navigate` and `browser_snapshot` from
   `cursor-ide-browser`. Do not assume they are there because this prompt mentions them; as of
   2026-07-30 that server was **not** registered in a fresh session.
2. If they are missing, stop and tell me to run `Cmd+Shift+P` → **Developer: Reload Window**.
   Wait for me to confirm the reload, then re-check. If they are still missing after one
   reload, go to the Playwright/CDP fallback below rather than retrying the reload.
3. Once the tools exist, navigate to the profile URL and take one snapshot to prove the browser
   is live and I am signed in. If the snapshot shows a login wall, tell me and wait — I sign in
   myself.
4. Say explicitly which path you are on ("MCP browser" or "Playwright over CDP") before the
   first edit, so I know what I am watching.

Re-check your browser tools if any call fails mid-run — the server dropped out mid-session last
time, and the recovery is the same reload.

## Tasks, in order

1. **Delete** the work-experience entry **"Cloud Architect — Harvard Medical School
   (Aug 2025 – Present)"**. I have confirmed it is fabricated. It claims Go, Redis,
   Kubernetes/EKS, and an OAuth2/JWT identity gateway integrated with hospital SSO — none of
   which I have done.

2. **Add** the real version in its place: **Entry 5** in the file — Full-Stack Engineer &
   Scrum Master, Emory Pediatric Hospital, Atlanta GA, Jan 2024 – Aug 2025 (ended, not
   "Present"). Stack is Python/Flask, React, MongoDB, Auth0, Docker on AWS Elastic Beanstalk
   and CloudFront.

3. **Replace** the "Graduate Researcher — Harvard University" description with **Entry 1**'s
   text. The current one is garbled mid-sentence ("Engineered a customdirectly within VAE
   latent spaces") and claims **diffusion models** and **GENOT**, neither of which I
   implemented. Do not reinstate either term.

4. **Delete these skill tags** — none appear anywhere in my resume or evidence bank:
   Kubernetes, Go, Redis, Node.js, Spring, Jenkins, GitHub Actions, Grafana, Prometheus,
   Bedrock, DynamoDB, EBS, EMR, Tableau, A/B testing frameworks.

5. **Add every skill** from the eight blocks in section 1 of the file. PyTorch, RAG, LoRA,
   fine-tuning, vector search, OpenAI API, SLURM, and HPC are all missing today and matter
   most — they are my strongest verified skills and the highest-value keywords for the roles
   I want (AI/ML, agents, AI infrastructure). Some terms may not exist in Simplify's
   taxonomy; add them as custom entries where possible and tell me which ones failed.

6. **Set the GitHub URL** to `https://github.com/JunyiZhou-Conny` — the field is currently
   blank even though several of my strongest entries are public repos.

## Browser setup — read this before step 0, it cost an hour last time

- Cursor's built-in browser MCP server is `cursor-ide-browser` (tools: `browser_navigate`,
  `browser_snapshot`, `browser_click`, `browser_fill`, `browser_type`, `browser_tabs`, etc.).
  It was absent from a fresh session on 2026-07-30 and **disappeared mid-session** the time
  before that. Reloading the window re-registers MCP servers.
- The Cursor browser appears as a **"Browser" editor tab**, not a side panel. It is easy to
  miss behind other tabs.
- That browser has **its own session**, separate from my normal Chrome. I have to sign in
  there myself. Never ask for, type, or store my password.
- **Fallback if the MCP browser stays broken:** Playwright is installed in
  `/Users/conny/Desktop/job-search-2026-2027-starter/.venv` and Chrome is at
  `/Applications/Google Chrome.app`. Launch Chrome with `--remote-debugging-port=9222` and
  connect over CDP with Playwright's `connect_over_cdp`. I will sign in once in that window,
  then you drive it.

## Working style

- **Confirm with me before deleting anything** — re-adding is manual if I change my mind.
- **Show me the Graduate Researcher text before saving it.**
- Verify each change with a snapshot before moving to the next; Simplify is a React app and
  saves do not always take on the first click.
- Adding ~120 skill tags is one interaction each. If it turns out slower than pasting by
  hand, say so and I will do that part myself.
