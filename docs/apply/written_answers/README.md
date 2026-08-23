# Written-answer archive

This is the interview-recall file for **free-response answers** we drafted
on ATS forms (why this company, how I structure a week, meaning / purpose,
and similar).

It is not a second Simplify tracker. A file here does **not** mean the
application was submitted.

## Where things live

| Place | What it holds |
|---|---|
| This folder | One markdown file per company + role + date. The exact questions and the exact drafts. |
| `knowledge/written_response_bank.yaml` | Reusable ideology Junyi confirmed (automate the boring, in-person, hours for a real goal). |
| `knowledge/form_strategy.yaml` | Always-rules: relocate Yes, salary = JD minimum else 90k, how-heard = LinkedIn. |
| `knowledge/evidence_bank.yaml` | Metrics and projects. Do not invent new ones in an essay. |
| `data/applications.csv` `auth_qa_notes` | Verbatim Q&A **after** a real apply. |

## How an agent should use this

1. After Copilot, write every short/long free response by **answering
   the prompt**. Ideology is for week / meaning / culture questions only.
   Do not paste education + three projects into Why-us. Never click
   Simplify **Generate with AI**. Prioritized companies:
   `knowledge/application_priority.yaml`.
2. Save the draft here **before** or as you type it on the form.
3. Set `form_status` to `drafted` or `typed_on_form`. Set `submitted` only
   when Junyi names that row and confirms Submit.
4. If the company later emails, open this file. Do not reconstruct from
   chat memory.

## Naming

```text
docs/apply/written_answers/YYYY-MM-DD_<company-slug>-<role-slug>.md
```

Example: `2026-08-23_traba-swe-ai-agents.md`
