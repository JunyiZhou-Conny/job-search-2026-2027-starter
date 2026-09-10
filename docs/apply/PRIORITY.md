# Regular vs prioritized applications

Junyi 2026-08-23, after the Lila review. This is a **filter**, not a
second Simplify tracker. Canonical machine file:
`knowledge/application_priority.yaml`.

It is **not** `pursuit_lane` (core / broad / practice) and **not** the
letter `priority` (A / B / C / D).

## Two chunks

| Weight | What changes |
|---|---|
| `regular` | Mass autofill. Approved base or Simplify resume. Free response answers the prompt and stops. |
| `prioritized` | More judgment. JD-tuned resume from the evidence bank only. Why-us actually answers the prompt. Full form prep, mandatory writing_log, then Polar Local may Submit (`docs/policy/SUBMIT_ROLLOUT.md`). Daily digest is post-submit oversight. Do not wait for a referral / insider page. Coffee-chat drafts only, never sent without confirm. |

## Subfields under prioritized

Use a signal only when it is strong. Do not mark a generic analyst or
data role prioritized only because the title contains data.

1. **GTC 2026.** Company is on NVIDIA GTC 2026 sponsors/exhibitors.
   List already in the repo: `knowledge/market_signals/gtc2026_sponsors_exhibitors.md`
   (435 names, from https://www.nvidia.com/gtc/sponsors/).
   Lila Sciences is an **Exhibitor**. Baseten is **Gold** (suggestion only).
2. **Startup.** Vibrant / engaging / can be pushy. `company_lists.yaml`
   `startup_or_scaleup` is a hint, not a confirmation.
3. **Prestige.** Top big tech, biomedical, or research institute Junyi
   values. `big_tech` / `biotech` lists are hints.
4. **Fortune 500 or major.** A major company Junyi values, not every
   large employer.
5. **Biotech / health AI.** Real product fit, not generic hospital admin.
6. **Biostat / data-science / bio.** Unusually strong personal fit to
   the science. Not every data title.
7. **Personal fit.** Rare. Owner judgment.
8. **FDE.** Forward Deployed / Forward-Deployed AI. Palantir-coined
   last-mile role. See `knowledge/role_families.yaml`. Junyi 2026-08-24:
   mark these; they are suitable. Charta is the type example.

Polar may assign READY_PRIORITY when a strong configured signal is present. Junyi does not confirm every priority label before the queue can move. Priority controls execution effort, writing depth, and post-submit writing audit. It is not permission to invent company facts.

Strong signals. Assign READY_PRIORITY: fde title, gtc_2026 company on the NVIDIA GTC 2026 list, confirmed_prioritized YAML match, clear fortune_500_or_major, clear biotech_health_ai.

Weak signals. Stay READY_REGULAR unless clearly justified: startup or prestige hints, personal_fit, generic data or analyst titles.

READY_PRIORITY no longer waits behind a permanent READY_REGULAR backlog. Polar Local may Submit after writing_log is complete.

## Confirmed so far

- **Lila Sciences — Software Engineer I, Instrument Software** —
  prioritized (`gtc_2026` + Junyi emphasis). Referral hold retired
  2026-08-24; review packet before Submit since 2026-09-03.
- **Charta Health — Forward Deployed AI Engineer** — prioritized
  (`fde` + startup + biomedical AI). Why-us v2 accepted. Junyi
  submitted from his own computer 2026-08-24. Cloud Chrome Submit
  was blocked as possible spam and did not land.

## Referral / insider page

Some shops have an insider / referral apply page. A public apply first
can block a later referred apply on some Ashby configs, and is
company-specific on Greenhouse.

Junyi 2026-08-24: those pages are rare. The employer pool is closer to
FIFO, so waiting to verify a referral costs more than it saves. **Do
not hold the review packet** for that check. If a named person later has a
real insider URL, record it. Do not rewind a landed public apply.

Do not send LinkedIn, email, or 1point3acres messages without confirm.

## 1point3acres (一亩三分地)

| URL | What it is |
|---|---|
| https://www.1point3acres.com | Home |
| https://jobs.1point3acres.com/ | Job多多 — companies, 面经, 内推 index |
| https://www.1point3acres.com/bbs/forum-28-1.html | 找工求职 |
| https://www.1point3acres.com/bbs/forum-198-1.html | 海外职位内推 (posts auto-close at 90 days) |

Access from this Cloud Agent VM (2026-08-23): HTTP **403** Cloudflare
challenge on home, Job多多, and the 内推 board. WebFetch timed out.
Public index pages are visible via web search. Full 内推 threads are
noisy and often login-gated. Useful as a **human-reviewed** lead source
for prioritized companies. Not a verified referral. Not an auto-apply
channel.

## What we did not change yet

How a prioritized apply *feels* different beyond tailored resume and
better Why-us is still open. Outreach templates and a ledger column
for `application_weight` wait for Junyi. Public-Submit hold is retired.