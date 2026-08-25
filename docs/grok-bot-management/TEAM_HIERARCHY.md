# Team hierarchy

Junyi Zhou working notes, 2026-08-25. Condensed so I do not have to spell this out again.

## What we have now

The current team is simple. It is not a company inside a company.

One Chief of Staff.

Three specialists, exclusive lanes:

- Researcher: facts and URLs
- Writer: drafts and Why-us
- Ops: tracking and routines

Each role is the only one doing that kind of work right now. No teams-within-teams yet.

## Official Grok Bot growth path

From the [Grok Bot use cases](https://docs.x.ai/grok-bot/use-cases) page:

1. Put the job, sources, output, and boundaries in the Bot description.
2. Run one real task with a safe scope.
3. Correct until the result is reviewable.
4. Save a successful process as a skill.
5. Test on a second input.
6. Create a routine only when retries and failure cases are defined.
7. Keep consequential external actions (Submit, send) behind Junyi's approval.

Where we actually are: one Lightfield apply path, with Junyi's intervention. Skill, second input, and routine are not written yet.

## Hierarchy I want to try later

Not implemented.

N jobs, N autofill teammates. A chief assigns each teammate exactly one job. Each teammate autofills and returns a reviewable result to the chief. The chief reports to Junyi (Connie / Junyi Zhou), who runs the whole thing. Later the chief might report to a higher chief, for example a company-level chief. That is not the same role as Chief of Staff.

This is managing a team. I do not want to micromanage each clicker. That is different from how I used Cursor before, one chat or one agent in the loop.

## Level-two task, paused

Autofill the remaining discovery ATS jobs and let Junyi do final review plus Submit.

Do not run this from this note or from a documentation-only PR.

## Open / not yet

This note is intent. It is not a license to spawn 10 apply bots or to Submit.

Isolation still applies. So does `knowledge/form_strategy.yaml`. Anyone who later implements this still has to follow both, plus [AGENTS.md](../../AGENTS.md) and [docs/BOUNDARIES.md](../BOUNDARIES.md).
