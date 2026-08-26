# Source notes for Grok Bot management

Reference. Quotes and links only. No org chart. No advice.

A sentence is hers only when the page is hers, or when a third party quotes her
and names the post. Clips and tutorials stay in their own section.

Fetched 2026-08-25 with `scripts/research/fetch_agent_sources.py` plus extra
public GETs into `/tmp/poteto-corpus`. X.com returned a JavaScript shell, not a
tweet archive. nitter.net was offline. Twitter syndication returned 429. This
file is not every sentence Lauren Tan has posted.

## User links

| Input | Resolved | What it is |
| --- | --- | --- |
| https://x.com/poteto | same | Profile. Bio via [api.fxtwitter.com/poteto](https://api.fxtwitter.com/poteto). Timeline not scraped. |
| https://t.co/zWiTOPKXPr | https://github.com/cursor/plugins/blob/main/pstack/docs/guide/README.md | Official pstack guide. Not the Maven video. |

## What we could not retrieve

- Full @poteto tweet history. 5,235 tweets on the profile payload. A few
  posts were recovered through TwiScan and LinkedIn.
- Maven workshop audio or transcript. [maven.com/p/e23d9c](https://maven.com/p/e23d9c)
  lists chapter titles only. Sign-up is required to watch the recording.
- The numeric trust bands (1, 1–5, 5–10, 10–20, hundreds). Those numbers are
  not in any public page retrieved this session. The workshop has a chapter
  titled "The Agent Trust Curve." Treat the band numbers as unverified
  recollection unless Junyi later pastes a timestamped quote.
- "almost 800 by the 12th." Not found in retrieved posts. Do not use it.
- GitHub Issues on this repo. `gh issue list` returned
  `Resource not accessible by integration`.

## Identity (profile payload)

From [api.fxtwitter.com/poteto](https://api.fxtwitter.com/poteto), retrieved
2026-08-25:

> Grok @Bot and Cursor at @SpaceXAI. Shipping with
> https://cursor.com/marketplace/cursor/pstack. React compiler core team, prev
> @cursor_ai @meta @netflix

GitHub [github.com/poteto](https://github.com/poteto) lists company `@cursor`
and `twitter_username: poteto`.

## Lauren Tan, primary

### How I Use Cursor (X thread)

Source: https://x.com/poteto/status/2058975157503570132
Mirror used: https://tool.lu/en_US/article/7Qz/preview

> As a former engineering manager, I quickly realized that managing agents felt
> similar to building a human engineering team.

> Agents are like new hires in a constant state of amnesia and idiocy. They
> don't remember what you tell them, and they never really learn anything new.
> But we can equip them with rules, skills, tools, and long term memory which
> can approximate that. They're capable yet stupid, and very teachable.

> Naive parallelization just makes them write slop faster.

> i'm increasingly convinced that the value of orchestrating many agents in
> parallel comes from going deep, not broad.

> The bottleneck with agents is verification. Agents can write a large amount
> of code quickly. Making sure it’s all correct is exceedingly difficult. When
> you can get there, true agent parallelism, like in a dark factory for
> software, might be possible.

> But first, we need to go deep and be rigorous. I think we get there by
> dialing up the trust.

> Unless you can trust an agent to own a problem end-to-end, including
> verification, you cannot automate your processes.

> Trying to parallelize agents you don't trust yet is a huge waste of tokens
> and introduces more slop into your codebase.

> The heart of the plugin is /poteto-mode, which is a higher order skill that
> gives agents the right playbook to follow for a given task. The goal is not
> maximal LOC, but the opposite: maximum impact with the least amount of code.

> I make extensive use of Cursor automations at Cursor. They're cloud agents
> that can be scheduled, or run in response to events like new messages in a
> Slack channel. One such example is my bot Benny.

### pstack README (her voice)

Source: https://github.com/cursor/plugins/tree/main/pstack
Mirror read: https://github.com/backnotprop/pstack

> if you want to go fast, go deep first.

> pstack gives you fearless parallelism. when you can go deep on one agent and
> trust it to write good, verifiable code, you can truly parallelize with
> confidence.

### LinkedIn, pstack launch

Source: https://www.linkedin.com/posts/laurenelizabethtan_cursor-pstack-the-skills-behind-10000-activity-7465439429042737152-ADbv

> My Cursor skills were used 10,000 times last week by our eng team. So I'm
> open sourcing them. It's a plugin called pstack

> The core is /poteto-mode: a higher-order skill that routes your agent to the
> right playbook for whatever you're working on.

The same post repeats the "amnesia and idiocy" paragraph from the X thread.

### LinkedIn, cloud agents and Grok Bot outer loop

Source: https://www.linkedin.com/posts/laurenelizabethtan_cloud-agents-and-cursor-harness-improvements-activity-7495972438262853632-bLQ5

> I shipped 1000 PRs last month and am on track to doubling that this month,
> all thanks to cloud agents. You can also launch cloud agents with Grok Bot
> btw!

> I built pstack (https://lnkd.in/gSgTn6cX), my personal set of skills for
> rigorous engineering and verification. Inside of our codebase I call it
> /lauren-mode, but it's called /poteto-mode in pstack.

> I use Grok Bot routines to farm context for me: bug reports on Slack, user
> complaints on X, generating new feature ideas. Grok Bot feeds my "outer
> loop", where I think about what to point my factory at next.

> I make heavy use of /goal, /loop, and /swarm inside of pstack to run my Full
> Autopilot playbook, which lets your agents/bots fully own, verify, and ship a
> task from start to finish.

> Everything runs on cloud agents, so my bots work 24/7 even when I'm asleep or
> my laptop is offline.

### LinkedIn, Maven teaser

Source: https://www.linkedin.com/posts/laurenelizabethtan_how-cursor-turned-ai-agents-into-better-engineers-activity-7493165544628703233-ZfM-

> Excited to share more about my journey building pstack (...), shipping 2,000
> PRs a month, and the client framework powering Grok Bot tomorrow!

### Grok Bot launch tweet

Source: https://x.com/poteto/status/2087227636590465030
Date on TwiScan: 2026-08-11 17:20

> Extremely excited to share that we just launched Grok Bot! Bots do work on
> their own computers while you're at meetings, while you're having lunch, and
> while you sleep.

> I've been using Grok Bot to manage my calendar and ship code. My team of
> bots also help me with my personal life, including finding me tickets to The
> Odyssey in IMAX 70mm, ordering me lunch everyday, and finding me dank emojis
> to upload to Slack.

> I've completely refactored it to be built on top of a new agent friendly
> framework I've been building that I'm currently codenaming "Dune" (working
> title).

> It's designed for agents, even the ones who have very little context, to
> write high quality code by default.

### Later X fragment (TwiScan profile mix)

Source: https://twiscan.com/en/x/poteto

> just took over the 4th all time spot. 6 more days to go to break the 2k PRs
> world record

The surrounding TwiScan page mixes other accounts. Treat this line as hers
only if you open the tweet from her handle.

### pstack guide (repo docs she ships)

https://github.com/cursor/plugins/blob/main/pstack/docs/guide/README.md

> pstack works best when you stop micromanaging the agent. You describe what
> you want and how you'll know it's done.

> Give the agent a goal and a way to check it, in your own words

https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md

> "It compiles" is not evidence.

> A CLI change runs the real command.
> A UI change walks the changed flow in the running app.

https://github.com/cursor/plugins/blob/main/pstack/docs/guide/07-overnight.md

> An agent you can trust to verify its own work is an agent you can leave
> alone with a hard task.

> A duration is not a finish condition. "work on this for 4 hours" gives the
> agent nothing to check

https://github.com/cursor/plugins/blob/main/pstack/docs/guide/02-poteto-mode.md

> `/poteto-mode` is the front door. You give it a goal, it matches one of
> twenty-two playbooks

> If you run several agents against one repository, they will fight over the
> working tree.

## Maven workshop (chapter titles only)

https://maven.com/p/e23d9c
Title: How Cursor Turned AI Agents Into Better Engineers
Speaker listed: Lauren Tan, Member of Technical Staff at Cursor
Length: 60 min. Date on page: Aug 12, 2026.

Chapters on the public page:

1. Introduction and Lauren Tan's Background in Engineering Management
2. The Agent Trust Curve: Moving from Micromanagement to Auto-Merging PRs
3. The Importance of Verification Skills and Feature Maps for Agents
4. Introducing PStack: Building Skills to Prevent Agent Hallucinations
5. Maintaining Agent Skills Using Evals and the Eval Playbook
6. Scaling Verification: From Local Observation to Cloud Agents
7. Refactoring Codebases and Setting Guardrails for AI Agents
8. Managing PR Sizes and Structuring Work for AI Agents
9. Implementing Strict CI Constraints and the Dune Architecture
10. Token Usage, ROI, and the Cost of Agent-Optimized Codebases
11. Empowering Product Teams with GrockBot and Final Thoughts

The page misspells Grok Bot as GrockBot in that last title.

Public blurb:

> Why AI agents behave like talented but forgetful new hires

No spoken sentence from the recording is in this repo.

## Official Grok Bot (SpaceXAI)

These are company docs. They match her product. They are not her personal
voice unless a quote is attributed to her.

### Introducing Grok Bot (2026-08-11)

https://x.ai/news/introducing-grok-bot

> People inside SpaceXAI often run multiple Bots in parallel, with one to
> manage the others. A chief of staff sits on top, with a specialist for each
> lane: inbox management, expenses, recruiting, bug fixes, or operations.
> Instead of multiple agents you have to manage, Grok Bot gives you a small
> team that can work in parallel so you’re not the middleman.

> You can also place Bots in a group chat where they can coordinate on their
> own. They pass work, assign ownership, and only pull you in for judgment
> calls.

> The best way for a Bot to learn your workflow is to ask it to follow along
> the next time you do a job.

Emma, Operations, quoted on that page:

> When I first started, I was checking in on them every 15 minutes and
> micromanaging the Bots to the point where they asked me why I kept asking so
> many questions.

### More plans (2026-08-21)

https://x.ai/news/grok-bot-more-plans

> Stand up a researcher, writer, and chief of staff. Put them in a group chat
> so they pass work between themselves, and you're not in the middle.

> only pull you in for judgment calls.

### Use cases

https://docs.x.ai/grok-bot/use-cases

The official growth path:

1. Put the job, source systems, output format, and standing boundaries in the
   Bot description.
2. Run one real task with a safe scope.
3. Correct the result until it is reviewable.
4. Save the successful process as a skill.
5. Test it on a second input.
6. Create a routine only when retries and failure cases are defined.
7. Keep consequential external actions behind approval.

Chief of Staff example on that page owns a digest. It does not click ATS
forms. Start prompt includes "Do not send messages or change meetings."

### Skill vs routine

https://docs.x.ai/grok-bot/faq

> A skill describes how to perform a task. A routine assigns a workflow to
> one Bot and tells it when to run—on a schedule or, where supported, after an
> event.

> Test the skill on a real one-time task before turning it into a routine.

### Shared computer

https://docs.x.ai/grok-bot/faq
https://docs.x.ai/grok-bot/computer-and-apps

> Every Bot on your account uses one persistent cloud computer. They share
> its files, browser sessions, and logins so they can hand work off.

> The computer is assigned per user, not per Bot. Do not use separate Bots as
> a security boundary.

> Each Bot gets its own screen on the shared computer.

### Approvals

https://docs.x.ai/grok-bot/approvals-security-and-privacy

Prefer explicit boundaries for sending, publishing, purchases, deleting,
permissions, production changes, and accepting legal terms.

> An approval controls the proposed action. It does not reverse work already
> completed.

Passwords, 2FA, CAPTCHAs, and payment confirmations use computer takeover.
Do not paste them into chat.

## Secondary. Not her words

### 0xCodez clip, 10–20 agents

https://threadnavigator.com/thread/2089676836619878567/ lists a related
0xCodez thread that quotes:

> right now I'm running 10-20 GrokBot agents that automate 90% of my routine
>
> i have a Chief of staff agent. he knows about all my other bots and manages
> everything

Junyi already noted she does not quite say it that way. This file did not
recover that sentence on @poteto. Keep it labeled as a clip.

### 0xCodez 10-step tutorial

https://threadnavigator.com/thread/2089676836619878567/

Author on that page: @0xCodez. Not @poteto.

The ten headings:

1. Install it, then meet the Chief
2. Give it a job title, not a prompt
3. Connect the tools once
4. Hand off the login, don’t paste the password
5. Show it once, don’t explain it twice
6. Turn it into a routine that runs without you
7. Hire specialists, not one generalist
8. Put them in a group chat
9. Draw the approval line
10. Review weekly, prune ruthlessly

The approval line on that page is reversibility. Draft, file, tag, summarize,
research, prepare, reconcile finish alone. Send, spend, publish, delete, and
accept terms park for the human.

### grokbot.dev CoS prompt

https://grokbot.dev/use-cases/team-in-10-minutes/

The page says it reconstructs @zodchiii. It is not official xAI and not
Poteto.

### Flavio Copes, pstack deep dive

https://flaviocopes.com/pstack/ (2026-08-21)

Useful secondary map of pstack. Paraphrase, not a primary quote.

### This repo, Junyi notes

`docs/grok-bot-management/TEAM_HIERARCHY.md`
`docs/grok-bot-management/APPLY_CORP_STRUCTURE.md`
`docs/grok-bot-management/SHARED_COMPUTER.md`

Commits `761508d`, `2517fed`, `f271d77`. PRs #73 and #75.
Thinking notes. Not a spawn license.

## Link list

Primary

- https://x.com/poteto
- https://x.com/poteto/status/2058975157503570132
- https://x.com/poteto/status/2087227636590465030
- https://cursor.com/marketplace/cursor/pstack
- https://github.com/cursor/plugins/tree/main/pstack
- https://github.com/cursor/plugins/blob/main/pstack/docs/guide/README.md
- https://maven.com/p/e23d9c
- https://www.linkedin.com/in/laurenelizabethtan
- https://www.linkedin.com/posts/laurenelizabethtan_cursor-pstack-the-skills-behind-10000-activity-7465439429042737152-ADbv
- https://www.linkedin.com/posts/laurenelizabethtan_cloud-agents-and-cursor-harness-improvements-activity-7495972438262853632-bLQ5
- https://www.linkedin.com/posts/laurenelizabethtan_how-cursor-turned-ai-agents-into-better-engineers-activity-7493165544628703233-ZfM-

Official Grok Bot

- https://x.ai/news/introducing-grok-bot
- https://x.ai/news/grok-bot-more-plans
- https://docs.x.ai/grok-bot/use-cases
- https://docs.x.ai/grok-bot/faq
- https://docs.x.ai/grok-bot/computer-and-apps
- https://docs.x.ai/grok-bot/approvals-security-and-privacy
- https://docs.x.ai/grok-bot/get-started

Secondary

- https://threadnavigator.com/thread/2089676836619878567/
- https://grokbot.dev/use-cases/team-in-10-minutes/
- https://flaviocopes.com/pstack/
- https://twiscan.com/en/x/poteto
