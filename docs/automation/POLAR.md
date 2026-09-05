# Polar as a local execution plane

This file is the only full Polar essay. Other docs may point here. They must not retell it.

Status is architecture only. This repo has no Polar runtime, SDK, or scheduler.

Polar is a second execution environment, not a second job-search system.

```text
                 GitHub repository
             canonical state / handoff
                       |
           +-----------+-----------+
           |                       |
           v                       v
     Cursor / Cloud            Polar / Local
     control plane             execution plane

     what to apply to          how to execute
     discovery, triage         logged-in browser
     dedupe, priority          Original Job Post
     queue, facts, ledger      employer ATS
```

Cursor answers what we apply to. Polar answers how an already-approved browser task runs on Junyi's machine.

## Evidence kinds

Treat each claim as one of these. Do not upgrade a lower kind.

- **Owner-observed (2026-09-04).** Junyi's live Polar and Jobright use.
- **Public product docs.** Polar's own site and press. Cited when used.
- **Architectural inference.** A boundary we chose so the repo stays one system.

## Roles

Cursor is the control plane. It owns discovery, merge, dedupe, triage, KEEP or SKIP, lanes, the resolver, the apply queue, form strategy, Submit policy, and ledger writes. Cloud Computer Use stays available for clicks on a Cloud Agent VM. See `docs/automation/DAILY_JOB_DISCOVERY.md` and `docs/automation/COMPUTER_USE_PROMPT.md`.

Polar is the execution plane. It does local agentic browser work after GitHub already named the job. It opens the right URL. When the handoff is still a Jobright discovery link, it follows **Original Job Post**. It fills or prepares the employer form only when the handoff says so. It stops at `stop_rule`.

GitHub is the handoff and the durable state. Polar must not invent a parallel KEEP list. Cursor later reconciles Polar's result into `data/applications.csv` and `data/apply_attempts.csv`. Until that write path exists, Junyi or a later Cursor turn copies the result by hand.

Junyi observed that Polar runs on Junyi's computer in a real local browser, already logged into services that matter for applications. Polar accepted instructions and GitHub repository context. Polar has **Workflow**. Workflows can be saved and scheduled.

Polar's own introduction says it "clicks, types, and navigates the web the way you would, logged in as you" ([Introducing Polar](https://polarbrowser.com/blog/introducing-polar)). Polar describes itself as a Chromium fork ([A New Interface for Composer](https://polarbrowser.com/blog/new-interface)). TechCrunch reports that users can schedule workflows and save prompts ([29 July 2026](https://techcrunch.com/2026/07/29/perplexity-employee-who-worked-on-comet-launches-an-ai-browser-aimed-at-knowledge-work/)).

GitHub stays in the middle so Polar cannot become a second source of truth. That is our boundary, not a Polar product claim.

## What Polar must not do

- Redo discovery, ranking, dedupe, or priority.
- Own `data/applications.csv` or become a second ledger.
- Treat Jobright as the final application URL.
- Click **APPLY WITH AUTOFILL**. That is Jobright's apply product, not the employer ATS.
- Submit unless `docs/policy/SUBMIT_ROLLOUT.md` has an open gate and the handoff allows Submit.
- Receive passwords, 2FA codes, or cookies in git or in a Cursor chat.

## URL rules

These two fields are not interchangeable.

| Field | Meaning |
|---|---|
| `discovery_url` | Where we found the row. Often `https://jobright.ai/jobs/info/...`. |
| `apply_url` | Employer or source application URL when we trust it. |

If `apply_url` is present and `apply_url_confidence` is `exact` or `strong`, Polar opens that URL. Do not open Jobright first.

If `apply_url` is empty and `discovery_url` is a Jobright job page, Polar opens that page in the local logged-in session and clicks **Original Job Post** only. Follow one redirect if the click needs it. Keep the result only when the final host is not `jobright.ai`.

Junyi observed that logged-in Jobright shows **Original Job Post**. For Tallgrass Intern-AI and Data Solutions, that link was `https://epix.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/4239?jr_id=6a9b267b90a313642c658c5f`.

This path complements `scripts/resolve_apply_url.py`. It does not delete the resolver. Public ATS APIs still help cloud runs that have no Jobright session.

`apply_url_confidence` of `weak` or `none` is not a license to invent a board URL. On Polar, prefer Original Job Post. Otherwise leave `apply_url` blank.

## Environments

`cursor_cloud` and `polar_local` do not share cookies.

Cursor Cloud Agents and the daily discovery Automation run in a fresh checkout. They do not see Junyi's laptop sessions. `secrets/jobright_storage.json` is gitignored and has been absent from every recent cloud discovery pack.

Polar sees the local browser. That is why Original Job Post is available there and not on the daily discovery VM.

Polar's May 2026 product note says Polar is macOS only for now ([A New Interface for Composer](https://polarbrowser.com/blog/new-interface)). Do not assume a Windows Polar exists.

Cloud Computer Use still uses `scripts/compile_cu_task.py` on cloud Chrome. Polar does not load that compiler. Do not wrap Polar inside a `computerUse` Task.

## Handoff shape

No API in this change. A later Cursor turn may write one markdown packet Polar can paste. Minimum fields:

- `company`
- `role`
- `discovery_url`
- `apply_url` (may be empty)
- `apply_url_confidence` (`exact`, `strong`, `weak`, `none`, or blank)
- `stop_rule`
- pointers to `knowledge/form_strategy.yaml`, `knowledge/work_authorization.yaml`, and `docs/policy/SUBMIT_ROLLOUT.md`

The first experiment uses this default `stop_rule`. Reach the source posting. Fill only if the packet says to fill. Do not Submit.

## Result shape

Polar returns these observations. Cursor or Junyi later writes durable state. Do not add ledger columns until a result exists.

- `opened_url`
- `original_job_post_url` (if that path was used)
- `apply_url_used`
- `filled` (`yes`, `no`, or `partial`)
- `submitted` (`no` unless authorized)
- `notes`

Junyi filled a real application with Polar. That test was not flagged the way some cloud-browser submits were. That is one test. It is not a general claim that Polar is invisible to ATS spam filters.

## Proven versus unproven

| Claim | Kind | Status |
|---|---|---|
| Polar runs locally, logged in as Junyi | owner-observed | Proven 2026-09-04 |
| Polar filled one real application | owner-observed | Proven 2026-09-04 |
| That one test was not flagged like some cloud submits | owner-observed | Proven for that test only |
| Workflow exists and can be saved or scheduled | owner-observed. Public press agrees. | Proven as a product concept |
| Polar can take repo context | owner-observed | Proven |
| Jobright Original Job Post reaches the Tallgrass Oracle Cloud URL | owner-observed | Proven for that job |
| Polar Workflow can consume this repo's queue unattended | inference | Unproven |
| Every Original Job Post is an employer ATS | inference | Unproven. The link may be LinkedIn or a tracker. |
| Polar can write `apply_attempts.csv` without a human | inference | Unproven |
| Daily Cursor Automations can use Polar sessions | inference | False unless someone runs Polar locally |

## First experiment packet

Do not run this packet in a Cursor Cloud Agent turn. The next Cursor turn may turn it into a Polar prompt.

This job is owner-named. It is not a row in `data/applications.csv` in the 2026-09-04 checkout. The packet is still the GitHub handoff. Polar must not scrape a replacement job.

| Field | Value |
|---|---|
| `company` | Tallgrass |
| `role` | Intern-AI and Data Solutions |
| `discovery_url` | `https://jobright.ai/jobs/info/6a9b267b90a313642c658c5f` |
| `apply_url` | empty |
| `apply_url_confidence` | blank |
| Expected Original Job Post | `https://epix.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/4239?jr_id=6a9b267b90a313642c658c5f` |
| `stop_rule` | Open Jobright while logged in. Click **Original Job Post** only. Confirm host `epix.fa.us2.oraclecloud.com` and job `4239`. Do not click **APPLY WITH AUTOFILL**. Do not fill. Do not Submit. |
| Weight | Regular. Not a G2 Ashby protocol unit. |

Pass condition. Polar left Jobright and landed on the source posting. Cursor did not rediscover the job. Polar returns `opened_url`, `original_job_post_url`, `apply_url_used`, `filled=no`, `submitted=no`, and a short note.
