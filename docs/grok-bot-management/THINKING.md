# How to think about Grok Bot orgs

You are one person running a job search. You do not run Cursor's PR volume.

These notes are explanation. They do not spawn Bots. They do not Submit.

## What is verified

[SOURCES.md](SOURCES.md) is the quote ledger. A sentence is hers only when that file already has it.

Verified from retrieved pages:

- Her X thread on managing agents
- Her pstack README and guide
- Her LinkedIn posts on pstack and the Grok Bot outer loop
- Official xAI Grok Bot docs
- This repo's Junyi notes

Inferred, not proven:

- How a live apply cell would behave on a new Ashby URL
- Whether Auditor can catch leftovers without you steering clicks
- Whether Ashby N ever pays off

Unknown, and left unknown:

- Full @poteto tweet history. X.com returned a JavaScript shell. nitter.net was offline. Twitter syndication returned 429.
- Maven workshop audio. The public page lists chapter titles only. There is no workshop transcript in this repo.
- Numeric trust bands. The numbers 1, 1-5, 5-10, and 10-20 are unverified recollection. The workshop has a chapter titled "The Agent Trust Curve." Treat the band numbers as recollection unless you later paste a timestamped quote.
- The phrase "almost 800 by the 12th." Not found in retrieved posts.

`https://t.co/zWiTOPKXPr` resolves to the official pstack guide. It is not the Maven video.

The 10-20 line is a 0xCodez clip. This folder did not recover that sentence on @poteto.

> right now I'm running 10-20 GrokBot agents that automate 90% of my routine

Keep that clip labeled secondary.

`scripts/research/fetch_agent_sources.py` fetches the public pages. [SOURCES.md](SOURCES.md) is the compiled ledger. Re-run the script if you want a newer corpus. Do not invent tweets to fill the holes.

This folder began as a capture of your 2026-08-25 team thinking. Commits `761508d`, `2517fed`, and `f271d77`. PRs #73 and #75. GitHub Issues were not searchable from this environment.

## What she actually argues

Managing agents is like managing people.

> As a former engineering manager, I quickly realized that managing agents felt
> similar to building a human engineering team.

Go deep first.

> i'm increasingly convinced that the value of orchestrating many agents in
> parallel comes from going deep, not broad.

> if you want to go fast, go deep first.

Verification is the bottleneck.

> The bottleneck with agents is verification. Agents can write a large amount
> of code quickly. Making sure it’s all correct is exceedingly difficult. When
> you can get there, true agent parallelism, like in a dark factory for
> software, might be possible.

Naive parallelization writes slop faster.

> Naive parallelization just makes them write slop faster.

> Trying to parallelize agents you don't trust yet is a huge waste of tokens
> and introduces more slop into your codebase.

Trust one agent end-to-end, including verification, before you multiply.

> Unless you can trust an agent to own a problem end-to-end, including
> verification, you cannot automate your processes.

> pstack gives you fearless parallelism. when you can go deep on one agent and
> trust it to write good, verifiable code, you can truly parallelize with
> confidence.

Grok Bot farms the outer loop. pstack, called `/lauren-mode` inside Cursor, is the factory.

> I built pstack (https://lnkd.in/gSgTn6cX), my personal set of skills for
> rigorous engineering and verification. Inside of our codebase I call it
> /lauren-mode, but it's called /poteto-mode in pstack.

> I use Grok Bot routines to farm context for me: bug reports on Slack, user
> complaints on X, generating new feature ideas. Grok Bot feeds my "outer
> loop", where I think about what to point my factory at next.

Her retrieved "chief of staff" line is a token-cost tip. A long-lived main bot. Not a 10 to 20 agent org chart.

> my number 1 tip for controlling your grok @bot usage is to avoid scheduled
> routines that run too frequently. for example, a 15 min routine runs almost
> 100 times a day, and every run consumes tokens. hourly or a few times a day
> is usually good enough. the length of the chat with your bot can also make
> routines much more expensive. for recurring ones, try giving that to a
> fresh bot, while you continue your chat with your main bots (like a chief
> of staff). give this post to your bot and ask them to help!

Official product copy has two Chief pictures. Launch posts sell a manager of specialists.

> People inside SpaceXAI often run multiple Bots in parallel, with one to
> manage the others. A chief of staff sits on top, with a specialist for each
> lane: inbox management, expenses, recruiting, bug fixes, or operations.

The use-cases page sells a digest Bot. That desk is inbox, expenses, recruiting, bugs, and ops, or a morning brief. It is not an ATS clicker farm. Do not treat the @DannyLimanseta Chief tweet on TwiScan as hers.

## Skill versus routine

Official FAQ.

> A skill describes how to perform a task. A routine assigns a workflow to
> one Bot and tells it when to run—on a schedule or, where supported, after an
> event.

> Test the skill on a real one-time task before turning it into a routine.

A skill is how. A routine is when. Do not schedule Autofill. Do not schedule Submit.

## Extra Bots are not vaults

> Every Bot on your account uses one persistent cloud computer. They share
> its files, browser sessions, and logins so they can hand work off.

> The computer is assigned per user, not per Bot. Do not use separate Bots as
> a security boundary.

[SHARED_COMPUTER.md](SHARED_COMPUTER.md) is the local restatement. More Bots do not isolate Simplify, Ashby, or Workday logins. They share one desktop.

## The shop you have, and the apply cell

[TEAM_HIERARCHY.md](TEAM_HIERARCHY.md) is the shop of four. Chief of Staff, Researcher, Writer, Ops. Four Bots plus you.

That shop is honest about its failure. The Chief of Staff cooks. Specialists idle. You stay in the loop on every click.

[APPLY_CORP_STRUCTURE.md](APPLY_CORP_STRUCTURE.md) is the first apply trial when you say go. Chief of Staff, Triage, one Ashby mind, Auditor, Ops. Writer on call. Five Bots plus you. Still no Submit from notes.

Git never recorded a choice between those two notes. `TEAM_HIERARCHY.md` still says "what we have now." The apply cell calls that shop too naive for auto-apply. Both sit in the folder. PRs #73 and #75 have no review thread and no linked issue. `job-search-hybrid` is this pass's recommendation, not a recorded pick of yours.

That cell maps her depth-first rule onto ATS work. One cook on one Ashby job. Auditor reads the form. You keep the gates.

The recommended picture in [ORG_TEMPLATES.md](ORG_TEMPLATES.md) is `job-search-hybrid`. Same pilot roster as the apply cell. Cursor `/poteto-mode` stays the thinking layer in this repo. Grok Bots do durable computer-use jobs.

## Why twenty apply clickers fail first

Submit is irreversible. An approval does not undo a sent application.

> An approval controls the proposed action. It does not reverse work already
> completed.

Form leftovers are invented-fact risk. A Copilot review flag on an empty field is a gap. It is not a license to invent GPA, citizenship, or a project URL.

Workday is unmapped. This repo has seen a CVS account-creation wall. It has not mapped a full multi-page Workday apply. Extra page-count detail stays unknown until one study job.

Shared logins. Extra Bots sit on the same computer. They are not vaults.

Hiring twenty clickers first also fails her own test. You cannot trust those Bots end-to-end, including verification. They would write slop faster.

The 10-20 clip is secondary. Do not staff `clip-crew` first.

## Recommended path

Keep the gates. You own Submit, send, 2FA, and new ATS accounts.

Keep [APPLY_CORP_STRUCTURE.md](APPLY_CORP_STRUCTURE.md) as the first apply trial. Notes only until you say go.

Use pstack in this Cursor repo for thinking and verification.

Add one Grok Bot Chief of Staff as the one conversation. The Chief assigns. Autofill stays off. Submit stays off. The paste that points that Bot at this folder is [GROK_BOT_HANDOFF.md](GROK_BOT_HANDOFF.md).

Scale Ashby N only after Auditor works without you steering clicks.

Do not spawn twenty Bots from this note.

## Principles that shaped these notes

- Never Block on the Human. Wrote templates instead of asking which org.
- Prove It Works. Quotes only from retrieved pages.
- Build the Lever. `scripts/research/fetch_agent_sources.py`
- Laziness Protocol. Do not spawn 20 Bots.
- Experience First. Your job is applications and gates, not 1000 PRs.
- Model the Domain. OrgTemplate registry.
- Exhaust the Design Space. Several templates, not one.
- Redesign from First Principles. Poteto's depth-first rule as if it had been day one.
- Guard the Context Window. Corpus in SOURCES.md, not a tweet dump.
