# Org templates

Reference records for Grok Bot org shapes. Each template is one named record. These notes do not spawn Bots. These notes do not Submit.

Fields on every record:

- id
- name
- source_fit
- trust_band
- layers
- spawn_count_pilot
- spawn_count_later
- roles
- verification
- gates
- when_it_fits
- costs
- failure_mode

`source_fit` is one of poteto, xai, 0xcodez, junyi, or hybrid. `trust_band` is one of 1, 1-5, 5-10, 10-20, or later. Band numbers are unverified recollection. See [SOURCES.md](SOURCES.md).

## shop-of-four

**id.** shop-of-four

**name.** Shop of four

**source_fit.** junyi

**trust_band.** 1

**layers.**

1. Chief of Staff. Assigns and also cooks.
2. Researcher. Facts and URLs.
3. Writer. Drafts and Why-us.
4. Ops. Tracking and routines.

**spawn_count_pilot.** 4 Bots plus Junyi

**spawn_count_later.** 4 Bots plus Junyi until `apply-cell`

**roles.**

- Chief of Staff. Owns assignment and, in this roster, the apply path. Stop line. Never Submit.
- Researcher. Owns facts and URLs. Stop line. Never Autofill. Never Submit.
- Writer. Owns drafts and Why-us. Stop line. A draft file is not a Submit.
- Ops. Owns tracking and routines. Stop line. Never apply-click.

**verification.** Junyi reviews. Specialists are often idle.

**gates.** Junyi owns Submit, send, 2FA, and new ATS accounts.

**when_it_fits.** Current [TEAM_HIERARCHY.md](TEAM_HIERARCHY.md) roster.

**costs.** Four Bots on one shared computer. Chief of Staff still cooks.

**failure_mode.** Chief of Staff cooks. Specialists idle. Junyi stays in the loop.

## apply-cell

**id.** apply-cell

**name.** Apply cell

**source_fit.** junyi, xai

**trust_band.** 1-5

**layers.**

1. Office of the Chief. Assigns. Never Autofill. Never Submit.
2. Intake. Triage labels ATS only.
3. Cooking lane. One Ashby mind now. Greenhouse 0, then 1. Workday 0, then 1 study.
4. Quality. Auditor reads the form.
5. Copy. Writer on call.
6. Ops. Time, tokens, weekly prune list.

**spawn_count_pilot.** 5 Bots plus Junyi. Chief of Staff, Triage, one Ashby mind, Auditor, Ops.

**spawn_count_later.** N Ashby only if the pilot works. Workday stays 0, then 1 study. Never N Workday.

**roles.**

- Chief of Staff. Owns the next named job and one cook assignment. Stop line. Never Autofill. Never paste Why-us. Never Submit.
- Triage. Owns ATS label only. Stop line. Never fill the form.
- Ashby mind. Owns one Ashby sticky note, one Autofill, leftover correction. Stop line. Stop before Submit. Never invent GPA, citizenship, or project URLs.
- Auditor. Owns form review against standing rules. Stop line. Never click.
- Ops. Owns wall-clock, thought-chain length, and token budget. Stop line. Never apply-click.
- Writer. Owns a Why-us draft only when assigned. Stop line. A file in `docs/apply/written_answers/` is not a Submit.

**verification.** Auditor reads the visible form, not the cook's story. Junyi sees a one-page exception list.

**gates.** Junyi owns Submit, send, Workday email and 2FA, new ATS accounts, and MyGreenhouse login.

**when_it_fits.** First apply trial when Junyi says go. Matches [APPLY_CORP_STRUCTURE.md](APPLY_CORP_STRUCTURE.md). Still no Submit from notes.

**costs.** Five Bots on one shared computer. Writer is summoned, not seated.

**failure_mode.** Chief of Staff cooks, or Junyi steers clicks.

## official-function-desk

**id.** official-function-desk

**name.** Official function desk

**source_fit.** xai

**trust_band.** 5-10

**layers.**

1. Chief of Staff. Manages the others.
2. Inbox. Mail and messages.
3. Expenses. Spend tracking.
4. Recruiting. Candidate pipeline, not Junyi ATS Autofill.
5. Bugs. Product defects.
6. Ops. Operations.

**spawn_count_pilot.** About 6 Bots plus Junyi

**spawn_count_later.** More lanes of the same life-ops kind

**roles.**

- Chief of Staff. Owns assignment across life-ops lanes. Stop line. Never ATS Autofill. Never Submit.
- Inbox specialist. Owns inbox triage. Stop line. Never send without Junyi.
- Expenses specialist. Owns expense drafts. Stop line. Never spend without Junyi.
- Recruiting specialist. Owns recruiting admin. Stop line. Never apply on Junyi's behalf.
- Bugs specialist. Owns bug intake. Stop line. Never ship without Junyi.
- Ops specialist. Owns operations tracking. Stop line. Never Submit an application.

**verification.** Official path. One safe task, then a skill, then a routine only after retries exist. Consequential actions stay behind approval.

**gates.** Junyi owns send, spend, publish, delete, legal terms, and Submit.

**when_it_fits.** Life-ops later. Wrong first map onto ATS apply.

**costs.** About 6 Bots on one shared computer. Lanes do not match Ashby or Workday pages.

**failure_mode.** Mapped onto ATS apply as if inbox and expenses were clicker jobs.

## depth-then-factory

**id.** depth-then-factory

**name.** Depth, then factory

**source_fit.** poteto

**trust_band.** 1

**layers.**

1. Chief of Staff. One conversation. Assigns.
2. Cook. Owns one lane end-to-end, including verification on the real artifact.
3. Auditor. Reads the artifact, not the story.

**spawn_count_pilot.** 2 to 3 Bots plus Junyi. Chief of Staff, one cook, Auditor.

**spawn_count_later.** 5 to 10 cooks of one lane, only after that cook is trusted.

**roles.**

- Chief of Staff. Owns assignment. Stop line. Never cook. Never Submit.
- Cook. Owns one job through verification on the real form or the real command. Stop line. Never Submit. Never invent facts.
- Auditor. Owns artifact review. Stop line. Never click.

**verification.** The cook verifies on the real artifact. Auditor confirms. Trust comes before multiply.

**gates.** Junyi owns Submit and other irreversible actions.

**when_it_fits.** Matches go deep first, then fearless parallelism after trust.

**costs.** Slow headcount growth. Tokens spent on one trusted cook before N.

**failure_mode.** Multiply before the cook verifies.

## outer-loop-plus-factory

**id.** outer-loop-plus-factory

**name.** Outer loop plus factory

**source_fit.** poteto, hybrid

**trust_band.** 1

**layers.**

1. Grok Bot Chief of Staff farmer. Farms Slack, X, and ideas. Points the factory.
2. Cursor pstack factory. Cloud agents in this repo think and verify.

**spawn_count_pilot.** 1 Grok Bot farmer plus Cursor cloud agents on this repo. Not 20 Grok clickers.

**spawn_count_later.** Farmer plus `apply-cell`

**roles.**

- Farmer. Owns discovery complaints, closed URLs, and next-target notes. Stop line. Never Autofill. Never Submit.
- Cursor cloud agent. Owns thinking and verification in this repo. Stop line. Never Submit.
- Junyi. Owns gates.

**verification.** pstack checks the real artifact in this repo. Grok Bot does not pretend this repo is Cursor.

**gates.** Junyi owns Submit, send, and 2FA.

**when_it_fits.** A question about using Grok Bot better, without treating this repo as Cursor.

**costs.** One Grok Bot computer plus Cursor cloud agents. Farmer is not an apply clicker.

**failure_mode.** Twenty Grok clickers instead of one farmer.

## clip-crew

**id.** clip-crew

**name.** Clip crew

**source_fit.** 0xcodez

**trust_band.** 10-20

**layers.**

1. Chief of Staff. Manages the group chat.
2. Specialists. Ten to twenty named jobs in one group.

**spawn_count_pilot.** 10 to 20 Bots plus Junyi

**spawn_count_later.** 10 to 20 Bots plus Junyi, after weekly prune

**roles.**

- Chief of Staff. Owns the specialist list. Stop line. Never Submit.
- Specialists. Own one job title each. Stop line. Draft, file, tag, summarize, research, prepare, or reconcile may finish alone. Send, spend, publish, delete, and accept terms park for Junyi.
- Junyi. Owns Submit and other irreversible actions.

**verification.** Weekly review and prune. Secondary source. The 10-20 line was not recovered on @poteto.

**gates.** Junyi owns Submit. Shared computer still holds every login.

**when_it_fits.** Secondary. After a smaller template has a working Auditor.

**costs.** Shared computer, token burn, weekly prune load. Junyi still owns Submit.

**failure_mode.** Staffed first. Token burn on untrusted specialists. Shared logins. Junyi still Submits.

## job-search-hybrid

**id.** job-search-hybrid

**name.** Job-search hybrid

**source_fit.** hybrid

**trust_band.** 1-5

**layers.**

1. Human gates. Junyi. Submit, send, 2FA, new ATS accounts.
2. Office of the Chief. 1 Grok Bot Chief of Staff. Assigns. Never Autofill. Never Submit.
3. Intake. Triage. ATS label only.
4. Cooking lane. One Ashby mind now, N later. Greenhouse 0, then 1. Workday 0, then 1 study.
5. Quality. Auditor. Reads the form, not the story.
6. Copy. Writer on call.
7. Ops. Time, tokens, weekly prune list.
8. Optional outer loop. One farmer for discovery complaints and closed URLs. After `apply-cell` works.

**spawn_count_pilot.** 5 Grok Bots plus Junyi. Same as `apply-cell`.

**spawn_count_later.** 8 to 12 if Ashby N is proven. Not 20 generalists.

**roles.**

- Junyi. Owns Submit, send, 2FA, and new ATS accounts. Stop line. Never invent facts for a Bot to paste.
- Chief of Staff. Owns assignment. Stop line. Never Autofill. Never Submit.
- Triage. Owns ATS label only. Stop line. Never fill the form.
- Ashby mind. Owns one Ashby job through leftover correction. Stop line. Stop before Submit. Never invent facts.
- Auditor. Owns form review. Stop line. Never click.
- Writer. Owns assigned drafts only. Stop line. A file is not a Submit.
- Ops. Owns time, tokens, and the weekly prune list. Stop line. Never apply-click.
- Farmer. Owns discovery complaints and closed URLs after `apply-cell` works. Stop line. Never Autofill. Never Submit.

**verification.** Auditor first. Cursor `/poteto-mode` stays the thinking layer in this repo. Grok Bots do durable computer-use jobs.

**gates.** Junyi owns Submit, send, 2FA, and new ATS accounts.

**when_it_fits.** Recommended operating picture. Still thinking only.

**costs.** Five Bots on one shared computer at pilot. Cursor agents for thinking. No 20-generalist roster.

**failure_mode.** Ashby N before Auditor works without Junyi steering clicks.

## junyi-architect-lanes

**id.** junyi-architect-lanes

**name.** Architect lanes (Junyi sketch)

**source_fit.** junyi

**trust_band.** later

**layers.**

1. Human gates. Junyi. Login, email verification, free-response power, Submit, 2FA, new ATS accounts.
2. Architect. One conversation. Stands up the org from the charter. Never Autofill. Never Submit.
3. Four chiefs. One apply chief now. Three titles still blank on the page.
4. ATS desks under the apply chief. Ashby now. Workday later (one study). Unknown portal later.
5. Ashby stack. One autofiller now. Bench toward × 10 later. Email verification asks Junyi. Writer × 1, maybe 2.

**spawn_count_pilot.** 4 Bots plus Junyi. Architect, apply chief, Ashby lane, one autofiller.

**spawn_count_later.** Toward 10 Ashby cooks if the first cook is trusted. Not 10 first. Workday stays 1 study. Unknown portal unnamed.

**roles.**

- Junyi. Owns login, email codes, free-response power, Submit, 2FA, new ATS accounts. Stop line. Never invent facts for a Bot to paste.
- Architect. Owns the charter and the chiefs. Stop line. Never Autofill. Never Submit. Never hire unless Junyi authorizes the revision.
- Chief of ____ (apply). Owns ATS desks. Stop line. Never Autofill. Never Submit.
- Chief of ____ / open chiefs. Titles blank on the 2026-08-26 sketch.
- Ashby Application. Owns the Ashby lane. Stop line. Never Submit.
- Autofiller / clicker. Owns one Ashby job through leftover correction. Stop line. Stop before Submit. Never invent facts.
- Autofiller bench. Later copies of that cook. Stop line. Do not seat 10 first.
- Email verification. Parks the job and asks Junyi. Stop line. Never complete 2FA. Never Submit.
- Writer. Owns a Why-us or leftover essay when asked. Stop line. A file is not a Submit.
- Workday. One study mind later. Stop line. No account create. Never N.
- Miscellaneous / unknown portal. Label or skip. Stop line. Never apply on Jobright. Never Submit.

**verification.** Not drawn. Auditor is absent on the page. Junyi still owns gates.

**gates.** Junyi owns login, email verification, free-response power, Submit, send, 2FA, new ATS accounts, MyGreenhouse login.

**when_it_fits.** Junyi's 2026-08-26 hand sketch. See [JUNYI_SKETCH_2026-08-26.md](JUNYI_SKETCH_2026-08-26.md).

**costs.** Shared computer. × 10 Ashby clickers share one login.

**failure_mode.** Staff the × 10 bench before one cook is trusted, or let a Bot complete email verify.

## Comparison

| id | pilot count | later count | who reviews | who Submits | main failure |
| --- | --- | --- | --- | --- | --- |
| shop-of-four | 4 | 4 | Junyi | Junyi | Chief of Staff cooks. Specialists idle. |
| apply-cell | 5 | N Ashby | Auditor, then Junyi | Junyi | Chief of Staff cooks, or Junyi steers clicks. |
| official-function-desk | 6 | more life-ops lanes | Junyi on judgment calls | Junyi | Mapped onto ATS apply. |
| depth-then-factory | 2 to 3 | 5 to 10 one-lane cooks | Cook, then Auditor | Junyi | Multiply before the cook verifies. |
| outer-loop-plus-factory | 1 Grok farmer | farmer plus apply-cell | pstack in this repo | Junyi | Twenty Grok clickers instead of one farmer. |
| clip-crew | 10 to 20 | 10 to 20 | Junyi weekly | Junyi | Staffed first on a shared computer. |
| job-search-hybrid | 5 | 8 to 12 | Auditor, then Junyi | Junyi | Ashby N before Auditor works. |
| junyi-architect-lanes | 4 | toward 10 Ashby | Not drawn (no Auditor on the page) | Junyi | × 10 before one cook is trusted, or a Bot completes 2FA. |

## Role charter

Paste later. Stop lines stay in force. Never invent facts. Never Submit.

```text
Junyi
Owns Submit, send, 2FA, and new ATS accounts.
Stop line. Never invent facts for a Bot to paste.

Chief of Staff
Owns assignment of one named job to one cook.
Stop line. Never Autofill. Never Submit. Never write Why-us.

Triage
Owns ATS label only.
Stop line. Never fill the form.

Ashby mind
Owns the sticky note, one Autofill, and leftover correction.
Stop line. Stop before Submit. Never invent GPA, citizenship, or project URLs.

Auditor
Owns review of the visible form against standing rules.
Stop line. Never click. Block invented facts, wrong sponsorship, EEO edits, or Autofill Again.

Writer
Owns a Why-us or leftover essay only when assigned.
Stop line. A file in `docs/apply/written_answers/` is not a Submit.

Ops
Owns time, tokens, and the weekly prune list.
Stop line. Never apply-click.

Farmer
Owns discovery complaints and closed URLs after apply-cell works.
Stop line. Never Autofill. Never Submit.
```
