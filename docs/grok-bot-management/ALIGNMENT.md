# Align the paper with what Junyi actually wants

2026-08-26. Docs only. This file explains a three-way mismatch.
It does not Submit. It does not hire Bots by itself.

## The mismatch

Three voices said different jobs for the Chief.

| Voice | What it told the Chief | What Junyi wanted |
| --- | --- | --- |
| This Cursor agent (`APPLY_CORP_STRUCTURE.md`) | Paper org chart. Cheap trial later. Stop before Submit. Do not spawn the roster. | A structure, then **use** it. |
| Grok Bot / PR #77 paste (`GROK_BOT_HANDOFF.md` on `cursor/sync-grok-handoff-paste-9be3`) | Research only. One report. No Autofill. No new Bots. Wait until Junyi says go. | Kick off the experiment. Assign teammates. **Fill** applications. |
| Junyi, 2026-08-26 | — | Chief assigns. Teammates cook Ashby. Workday is later. Submit is already happening on Ashby. |

The Chief that “did nothing” followed the paste. That was obedience,
not a broken Grok Bot. The paste forbade Autofill, assignment, and
group chat.

## What is true on the apply path

- **Ashby fill** is the live lane. Copilot + a clicker mind/hand is
  good enough to keep using. Not 100%. Standing rules still apply
  (`form_strategy.yaml` on later branches: sponsorship No, no
  Autofill Again, no Generate with AI).
- **Ashby Submit is in use.** This Cursor run recorded four Cloud
  isolation thank-yous (Anyscale + three trivials). Junyi says many
  more Ashby Submits have landed since. This branch’s
  `data/applications.csv` does **not** yet list that later volume.
  Do not invent a count. Do not treat “four” as the project total.
- **Workday is not that lane.** Account create, email codes, many
  pages. Skip unless Junyi names a study job and does the verify
  himself.
- **Jobright Apply** is often a signup wall. Resolve or skip. Do not
  “apply on Jobright.”

## What the Chief is allowed to do now

See the **live** block in [GROK_BOT_HANDOFF.md](GROK_BOT_HANDOFF.md).
Throw away the old “research only / wait” block from PR #77.

1. Read this folder on `cursor/grok-shared-computer-5db1`.
2. Assign **one** Ashby job to an existing teammate (do not hire the
   five-Bot paper cell unless Junyi says hire).
3. That teammate Autofills once, corrects leftovers, stops.
4. Auditor (or Chief if Auditor is not seated) checks the visible form.
5. Submit only if Junyi **names that URL** in the same turn.
6. Workday / new accounts / MyGreenhouse / send: stop.

The Chief still does not cook the form. The Chief **does** start the
turn. Waiting for a second “go” after a live paste is the old bug.

## What not to merge blindly

PR #77 synced a **stale** research-only paste. If that file is merged
on top of this one, the Chief will freeze again. Prefer this
`ALIGNMENT.md` + the live handoff on this branch.
