# Traba — Software Engineer (AI Agents)

Speech-to-text said “Trava.” The Ashby tab is **Traba**.

| Field | Value |
|---|---|
| Date | 2026-08-23 |
| Ledger id | `J20260723-016` |
| ATS | Ashby |
| Apply URL | https://jobs.ashbyhq.com/traba/e1761ab2-21f1-46d6-8c69-9b4a73d9430f |
| Location on page | New York City, NY · full time · in person |
| Compensation on page | **$140K – $200K** · equity 0.04% – 0.12% |
| Application limits | Candidates may not apply more than once in any 100-day span. May not re-apply to the same or any role within 100 days if not presented with an offer. |
| `form_status` | `typed_on_form` (Ashby tab on this VM, 2026-08-23). **Not submitted.** |
| `submitted` | no |
| Identity Copilot filled | name, email, LinkedIn, `Junyi_Zhou_resume.pdf` |
| Copilot need-review | 6 (salary, sponsorship, NYC/in-person, Why Traba, week structure, how-heard) |

Do not Submit this test. The 100-day lock is real.

---

## Salary expectations

**Rule used:** page listed a range → type the **minimum**.

**Draft / form value:** `140000`

If this page had printed no number, the default would have been `90000`
(`knowledge/form_strategy.yaml`).

---

## Will you now or in the future require Traba's Sponsorship to work within the United States?

Broad sponsorship question (not H-1B-named). Standing fact:
`future_sponsorship_required: true` in `config/profile.yaml`.

**Draft / form value:**

```text
Yes. I will need employer sponsorship after F-1 OPT.
```

---

## Are you in NYC or willing to move to NYC and work with us in-person 5x a week?

Standing rule: relocate → **Yes**.

**Draft / form value:**

```text
Yes. I am in Boston now and I will move to New York for this role and work in person five days a week.
```

---

## Why Traba?

Cursor-written from `knowledge/evidence_bank.yaml` +
`knowledge/written_response_bank.yaml`. No invented employers or metrics.
Do not click Simplify Generate with AI.

**Draft:**

```text
I want to build agents that take repetitive operational work off people's plates. That is what this posting describes, and it is the problem I keep choosing in my own work.

I am a Harvard SM student in Health Data Science (program end 2026-12-18; commencement March 2027) after an Emory B.S. in Applied Mathematics and Statistics. At Emory Pediatric Hospital I built an airway-management simulation chatbot — Flask, React, Auth0, MongoDB Atlas Vector Search, RAG on OpenAI — so clinicians could practice without burning scarce bedside time. On FASRC Cannon I built a closed-loop experiment runner (338 counted runs, 79.3 hours of wall-clock compute). The live planner so far has been the rule reasoner; I also built an optional LLM planner with a cost ceiling that has not been used on a real run.

I like working with agents for the steps nobody loves, and I like working with people in the same room. I will move to NYC for this. I am not claiming supply-chain domain experience I do not have. I am claiming I want to spend the next years automating the boring parts of real operations so people can keep the work that has meaning.
```

---

## How would you usually structure your week to get your best results?

Prompt on the form (verbatim sense): Traba is early / Series A; they like
peers who do whatever it takes; in-person; most weekday evenings and some
weekends; how would you structure your week.

Junyi: show education and self-motivation; evenings/weekends when the goal
is real; ask questions; in-person over online; agents for dumb/redundant
work; meaning has to have a purpose. Be mindful this is a student / first
intern, not someone already living startup hours as a job.

**Draft:**

```text
I structure a week around one clear goal, not around looking busy. Class and lab at Harvard are the fixed spine. The hardest maker work goes in the first long block I can protect, usually late afternoon into evening, because that is when I finish things instead of circling them.

If the goal is real and I find it rewarding, I will use evenings and some weekend hours. I have done that on the Cannon experiment loop and on course projects rather than leaving them half-done. I ask questions early, and I prefer to ask them in person. I learn faster from a person at a whiteboard than from a long thread.

I like working alongside people in the room, and I like handing the leftover — scrape, watch, retry, the dumb redundant steps — to agents. The point is not hours for their own sake. The point is to automate the boring parts so the rest of the week, and the rest of other people's weeks, can go to work that has a purpose.
```

---

## How did you find out about Traba?

Copilot left every checkbox empty. Computer-use on this VM ticked
**LinkedIn Job Board** (closest LinkedIn option). Other boxes untouched.
That is the standing how-heard rule.

---

## First-test-run notes (do not treat as Submit)

- Simplify Copilot filled identity/resume and stopped. It did not write
  salary, sponsorship, relocate, Why Traba, or the week essay.
- Copilot did not tick how-heard. Cursor/computer-use must click that
  every time on the same Chrome.
- Ashby shows “Generate with AI” on the written fields. Do not click it.
- Page compensation is $140K–$200K, so salary is 140000, not the 90k
  no-information default.
- 100-day reapply lock: a mistaken Submit costs a third of a year.
- 2026-08-23 later the same day: computer-use typed the drafts above
  onto the Ashby tab. Salary `140000`, sponsorship Yes, relocate Yes,
  Why Traba, week structure, LinkedIn Job Board. Submit still unclicked.
  Ashby/Simplify showed “Refine with AI” on the week box; not clicked.
