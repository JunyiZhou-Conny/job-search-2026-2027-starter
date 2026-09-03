# Computer Use contract (parent compiler)

**Audience:** the parent Cloud Agent about to spawn `computerUse`.
**Decided:** 2026-08-24 leftover paste after Charta; generalized 2026-09-03
after Twitch burned ~74 minutes on three visual passes.

The clicker starts with a clean Task context. It does not inherit this
chat, `AGENTS.md`, `.cursor/rules`, or `knowledge/*`. Cursor's unpublished
computer-use system prompt is fixed infrastructure. We do not replace it.
We bound the job so conservative observation cannot become a 15–30 minute
exploration.

```text
Parent            Action sheet         computerUse          Parent / verifier
understands  -->  final actions   -->  bounded UI      -->  expected vs observed
resolves facts    page order           no rediscovery       delta only
```

The parent is the brain. Computer Use is the hands. Verification is a
separate responsibility. A child saying "✓" is not proof.

## Before you spawn a clicker

You must already know:

- target tab and URL
- whether Simplify already ran
- exact fields that need mutation, with resolved answers
- fields that must stay untouched
- page order of the mutations
- Submit permission (`docs/policy/SUBMIT_ROLLOUT.md`)
- the evidence you actually need
- any fact that still blocks execution

If you do not know those, inspect first (structured state, DOM, existing
screenshots). Do not spawn an EXECUTE worker to rediscover the form.

Then:

```bash
python3 scripts/compile_cu_task.py compile path/to/sheet.yaml
```

Lint any hand-written Task string the same way:

```bash
python3 scripts/compile_cu_task.py lint path/to/task.txt
```

A Task that fails lint is not sent. The Twitch fill, correction, and
read-only prompts are the regression fixtures
(`tests/fixtures/computer_use/twitch_*.txt`).

## Modes

Use one mode per spawn. Do not combine them.

| Mode | Does | Does not |
|---|---|---|
| `execute` | Named mutations in page order, then stop | Rediscover, audit untouched fields, verify after each click |
| `verify` | Read named final-state facts | Click, type, compose one viewport of distant facts |
| `repair` | Named mismatches only, one alternate commit each | Repeat the same interaction, touch other fields |
| `submit` | One Submit click when the gate is open | Retry, Autofill Again, a second Submit |

Leftover Why-us paste is `execute` with one `commit: paste` mutation.
That is still one spawn, one paste, one screenshot, stop.

## Page order and evidence

Walk the form top → middle → bottom → stop. Reuse a page map from an
earlier worker in this run. Do not make every child rediscover it.

Evidence proves state. It does not need a pretty screenshot. Distant
facts get two shots. Once a fact is readable, stop hunting for a
viewport that shows both.

Safety-critical fields (identity, citizenship, sponsorship, export
control, work authorization, resume, consequential EEO) still need a
stable read after the page settles. Batch that read. Do not screenshot
after every click.

## Bounded retry and searchable dropdowns

For a field that does not persist:

1. Use the widget's normal commit.
2. Observe the settled value once.
3. Try one materially different commit.
4. Mark the field unresolved and return to the parent.

Highlighting a searchable-dropdown option is not a commit. Click the
option, then Tab off the widget. If it reverts, try Enter as the one
alternate, or the reverse. Do not encode "always press Enter."

Twitch Harvard education (Greenhouse): discipline and end date showed
the intended values, then reverted to Other / March 2027. Semantic
answers stay in `form_strategy.yaml` (Data Science; degree end date is
program completion December 2026 unless the widget text means
commencement). Widget persistence is a separate obstacle
(`greenhouse_education_widget_reverts_edits`).

## What the clicker can see

- pixels, mouse, keyboard, the same Chrome on this VM
- whatever you put in the Task string
- Cursor's unpublished computer-use prompt

It cannot read a textarea DOM value. Asking it to prove a paste with
Ctrl+F is how Charta burned tokens.

## Forbidden in every Task

Submit unless mode is `submit` and `submit_permitted` is true under
`docs/policy/SUBMIT_ROLLOUT.md`. Autofill Again. Generate with AI.
Reload after a filled form. Ctrl+F / phrase hunts. Screen recording
unless Junyi asked. A field-by-field audit of untouched widgets.

## Leftover paste (still valid)

`tests/fixtures/computer_use/leftover_paste.yaml` compiles to the
one-paste Task. You may still copy this by hand if the compiler is
unavailable:

```text
MODE EXECUTE. You are hands only. Do not rediscover the form.
Same Chrome. Do not Submit. Do not Run Autofill Again. Do not click
Generate with AI. Do not change any other field.

1. Open the tab: <COMPANY> — <ROLE>
   URL contains: <URL_SUBSTRING>
2. Click the box: <FIELD LABEL>
3. Ctrl+A. Paste the text between the markers once. Do not type it
   key by key. If an autosuggest dropdown opens, click the textarea
   once and paste anyway. Do not press Escape in a loop.
4. Click once outside the box.
5. One screenshot of the page. Stop.

A cropped textarea is normal. Do not start a second pass.

-----BEGIN TEXT-----
<ACCEPTED DRAFT, EXACT>
-----END TEXT-----
```

## If the first pass fails

- Tab not found, or the named mutation never happened → one retry with
  the same compiled Task. Still no verify-each steps.
- A field reverted after one alternate commit → unresolved. Parent
  records the obstacle. Do not Autofill Again.
- Dropdown / find-in-page noise → ignore. Not a retry reason.
