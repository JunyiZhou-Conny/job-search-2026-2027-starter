# Experiment: does a computerUse child inherit the rulebook?

Date: 2026-08-24
Question from Junyi: clicker prompts look short. Does the child see
the parent chat, `AGENTS.md`, or `knowledge/*`?

## Already measured (this Cloud Agent run)

Four isolation Submit children. Each transcript: one user message,
no `system` role in the stored file, no `AGENTS.md` / `knowledge/*`.

| Child | Prompt chars |
| --- | ---: |
| Anyscale `bc-e6b93672` | 2395 |
| Meshy `bc-c2329ec6` | 1240 |
| Midjourney `bc-b1661bf4` | 1147 |
| Runway `bc-f13355c8` | 1244 |

Cursor: [Subagents](https://cursor.com/docs/subagents.md) — clean
context. Cloud reserved name `computerUse` is not the public Browser
built-in.

Writing `COMPUTER_USE_PROMPT.md` / `form_strategy.yaml` does **not**
inject those files into the next clicker. It only helps if a later
**parent** reads them and copies the standing slice into the Task
string.

## What the file change can test (parent compiler)

Do **not** run this on Junyi's live 10-tab Chrome unless he names
the tab. Do **not** Submit.

1. New Cloud Agent (fresh chat). Do not paste this experiment into
   the first message.
2. Ask only: leftover-type an already-accepted draft on one named
   tab, then stop.
3. Inspect the `computerUse` Task prompt the parent wrote.
4. Pass only if the prompt includes the standing slice (no Autofill
   Again, one paste, no Ctrl+F / verify, no Submit) without Junyi
   restating those rules in chat.
5. Fetch the child transcript. Confirm the first user message is
   that Task string and nothing from the parent chat.

This chat cannot be that test. The parent here already has the
rules in conversation.

## What it cannot test

Cursor's unpublished `computerUse` system prompt. Do not ask a
child to dump it. Official docs do not publish it.
