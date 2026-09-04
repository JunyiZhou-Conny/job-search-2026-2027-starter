# Twitch Computer Use cost (2026-09-03)

Regression artifact. Do not reopen citizenship, sponsorship, EEO, or
Submit. The form stays unsubmitted.

Source: parent Task strings plus `computer_use` tool results in

- [Twitch G1 fill](https://cursor.com/agents/bc-e715751f-389e-525d-9490-3c957d675f5e)
- [Correction](https://cursor.com/agents/bc-9e01d095-049c-52e7-a2a5-e5c8aa3a6c20)
- [Read-only education/consent](https://cursor.com/agents/bc-5d024fa7-518e-5d53-a6b4-8111c422c457)

Counted by `/tmp/analyze_cu_transcripts.py` against the fetched
transcripts. Re-run that script on the same JSON for the same numbers.

| Pass | Wall | CU calls | Scroll | Click | Type/key | Screenshot | Parent prompt |
|---|---|---|---|---|---|---|---|
| G1 fill | 23.3 min | 70 | 32 | 20 | 8 | 5 | Fill-and-review. Screenshot the whole form. Report every question. |
| Correction | 31.5 min | 82 | 56 | 21 | 4 | 1 | Verify each widget after setting. Report every widget, including untouched ones. Six named shots. |
| Read-only | 18.9 min | 43 | 41 | 0 | 0 | 2 | Only scroll. Two facts that sit far apart. |

Three passes: about 74 minutes, 195 CU actions, 129 scrolls, 12 type/key
actions. The correction pass needed a handful of mutations and spent most
of its time rereading. The verify pass never clicked.

## What persisted

From the review packet, not a new live audit:

- Citizenship China, PR elsewhere No, export-control country China
- Sponsorship No, eligible immediately Yes
- Prior Amazon No, non-compete No, future opportunities Yes
- EEO values Junyi confirmed, left as Copilot set them
- Familiar with Twitch left blank on purpose
- Harvard discipline and end date reverted to Other / March 2027

## Cause

The hidden computer-use prompt may favor frequent observation. The
parent Task strings invited the loops: verify-each, report-every,
whole-form evidence, and one screenshot spanning distant facts.

Those strings fail `python3 scripts/compile_cu_task.py lint` today.
The replacement is an action sheet compiled in page order
(`docs/automation/COMPUTER_USE_PROMPT.md`).
