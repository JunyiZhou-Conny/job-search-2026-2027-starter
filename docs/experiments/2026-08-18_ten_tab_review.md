# Live 10-tab autofill review — 2026-08-18

Resume of the 2026-07-31 trial so a human can watch the Cloud Agent browser
and mark what autofill got right vs wrong.

**Stop rule:** never click Submit. Never answer EEO. Never create accounts.
This is review-only.

## Tab list (resolved live 2026-08-18)

Same 10 employers as the July 31 trial. Two titles changed because the old
requisitions are gone or no longer exact-match.

| # | Company | ATS | Role on the tab | Apply URL | Notes vs July 31 |
|---|---|---|---|---|---|
| 1 | OpenAI | Ashby | Performance Modeling Engineer | https://jobs.ashbyhq.com/openai/19fc3e36-3bf3-4a7c-b65f-498d89220436 | Same family; new Ashby id |
| 2 | Etched | Ashby | Inference Intern | https://jobs.ashbyhq.com/etched/6f23713f-5409-45b7-aae8-adb8710cdbc3 | Same |
| 3 | Bild AI | Ashby | AI/SWE Intern | https://jobs.ashbyhq.com/bild-ai/b333f0f7-0ca6-4509-8697-9303396b5364 | Same |
| 4 | Traba | Ashby | Software Engineer (AI Agents) | https://jobs.ashbyhq.com/traba/e1761ab2-21f1-46d6-8c69-9b4a73d9430f | Same |
| 5 | Neuralink | Greenhouse | Machine Learning Engineer Intern | https://boards.greenhouse.io/neuralink/jobs/6594261003?gh_jid=6594261003 | Same |
| 6 | Gemini | Greenhouse | Design Developer | https://boards.greenhouse.io/embed/job_app?for=gemini&token=7951195&gh_jid=7951195 | Title drifted; still this employer’s board |
| 7 | Nirmata | Greenhouse | AI Software Engineer Intern | https://job-boards.greenhouse.io/nirmata/jobs/4606513008 | Same |
| 8 | Apptronik | Greenhouse | Robotics Software Intern – Real-Time Controls | https://boards.greenhouse.io/apptronik/jobs/5985132004?gh_jid=5985132004 | Old “ML Systems intern” is gone |
| 9 | Together AI | Greenhouse | Research Intern, Model Shaping (Fall 2026) | https://job-boards.greenhouse.io/togetherai/jobs/5157661007 | 2026-cycle intern — **do not submit**; form-only |
| 10 | SpaceX | Greenhouse | New Graduate Engineer, Software | https://boards.greenhouse.io/spacex/jobs/8493079002?gh_jid=8493079002 | Same |

Together #9 is a **2026 intern cycle**. It is open only to inspect autofill. Do not apply.

## Live session notes (same Cloud Agent, 2026-08-18)

Tabs 1–10 are open in the VM browser. Forms are visible. **Nothing submitted.**

What is already correct:

- Each tab is the intended employer + role from the table (Apptronik and Together titles are the live replacements).
- Ashby tabs 1–4 are on the `/application` form, not the Jobright signup wall.
- Greenhouse tabs 5–10 show the embedded apply form after Apply.
- EEO untouched. Submit unclicked.

What is not done yet / blocked in this environment:

- This Cloud Agent browser does **not** have the unpacked Simplify Copilot session used on 2026-07-31.
- Ashby: no Simplify panel, so identity fields are still empty.
- Greenhouse: the visible **Autofill my application** control is Greenhouse’s own MyGreenhouse login (`my.greenhouse.io`), not Simplify. Clicking it asks for a security code. Do not complete that login from chat.
- To judge fill quality the way the July 31 trial did, Take Control and run **your** Simplify Copilot (already logged in) on these same tabs.

Until then, monitor requisition match and form structure, not filled-vs-empty identity fields.

## What to mark on each tab

For each tab, check:

| Check | Correct if… | Common failure |
|---|---|---|
| Right requisition | Title/company match the table | Resolver pointed at a sibling job |
| Identity block | Name, email, phone, LinkedIn match `config/profile.yaml` | Empty or leftover someone else’s session |
| School | Harvard / Health Data Science / Dec 2026 (or dual-date) | Wrong school widget; empty custom dropdown |
| Résumé | A real Junyi PDF, not a blank upload | Missing file; wrong cluster |
| Essays | Left blank for a human | Agent-invented answers |
| EEO | Untouched | Agent selected gender/race/veteran/disability |
| Submit | Still unclicked | — |

July 31 floor scores (autofill only; Greenhouse under-counts custom widgets):

| Company | July 31 coverage |
|---|---|
| OpenAI | 88% |
| Etched | 80% |
| Bild AI | 75% |
| Traba | 74% |
| Neuralink | 48% (essays left empty — correct) |
| Gemini | 40% |
| Nirmata | 36% |
| Apptronik | 25% |
| Together AI | 16% |
| SpaceX | 12% (widgets filled more than the counter saw) |

## How to watch

Open this Cloud Agent run and use **Take Control** on the VM browser.
Tabs stay open. Nothing is submitted from this run unless you say so in a
later message.
