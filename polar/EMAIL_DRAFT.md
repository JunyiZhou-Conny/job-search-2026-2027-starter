# Email draft

**Do not send.** This is a draft for `hiring@polarbrowser.com`. I will
send it myself if I send it at all.

To: hiring@polarbrowser.com
Subject: I measured Computer Use observation loops on real ATS forms

Since late July I have been trying to automate my own 2026–2027 job
search. Discovery, triage, standing answers, ATS URL resolution,
browser fill, review, submit policy, ledger. I ran that loop on real
Ashby, Greenhouse, and Jobright pages, and I reached Workday account
walls without filling them.

Three things from that work.

1. I counted a Computer Use child doing 195 actions, including 129
   scrolls, to get 12 type or key events on one Greenhouse form. Three
   passes, about 74 minutes. The parent had asked it to verify every
   widget and screenshot the whole page. I turned those prompts into
   lint fixtures. `compile_cu_task.py lint` fails those strings when
   a parent runs it. Cursor will still spawn computerUse if the parent
   freehands.
2. I pulled four computerUse transcripts and checked what the child
   actually receives. One user message. No parent chat. No AGENTS.md.
   1147 to 2395 characters. A short clicker prompt is a handoff bug,
   not a model that "forgot the rules."
3. I then split the repo. Cursor keeps selection and facts. The
   browser that can see my logged-in Jobright and Simplify sessions
   runs on my machine. Polar took a packet, followed Original Job
   Post, filled a Greenhouse intern form, and stopped before Submit.
   Polar reported about 6 minutes. That is a different form and a
   different instrument from the Twitch count. It is not a bakeoff.

Polar is first named in this repo on 4 September, after those
Computer Use measurements. I cannot prove the hour I first opened
Frontier Problems. The cloud-agents paragraph, the self-improving
harness, and agent-to-agent communication are the same seams.

Dossier, with sources and "does not prove" lines:

https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter/tree/cursor/polar-browser-application-cad3/polar

Junyi Zhou
Boston, MA
