# UI direction — Intelligent Career Journal

**Status: reference only. Not implemented.** Filed 2026-07-27 while the apply queue is in
daily use. Do not start a visual refactor mid-application-cycle; revisit once the resume is
settled and there is a week of real usage data.

## Core premise

Not a job board. A **daily-published personal career intelligence journal** — an
AI-curated opportunity archive and application desk.

A job board optimizes for cramming in listings, filters, and ads. This system's value is:
*something watched the market overnight, judged what mattered, and tells me what to do next.*
Closer to an editorial publication, a private researcher's desk, and an archive than to a
SaaS dashboard.

Target blend: **60% editorial publishing** (Anthropic-like warmth and curation),
**25% restraint and hierarchy** (Apple — one focus per screen), **15% humanist precision**
(OpenAI — order with a little life in it).

## Principles

1. **Conclusion first, list second.** Don't re-filter 200 roles daily. Open with
   "8 opportunities worth your attention today," then the list.
2. **Every recommendation is explained.** Not `92% match` — the `+`/`−` evidence behind it.
3. **One primary action per role**, changing with state: Review → Prepare → Apply → Follow up → Archive.
4. **AI as editor, not chatbot.** Marginal notes, confidence, an "Editor's note" on an odd
   posting — no floating assistant bubble, no robot avatar.
5. **Retro feeling comes from typography, language, structure**, and very light texture —
   never a yellow filter or fake stains.

## Visual system

```css
--color-paper:   #F3F0E8;
--color-surface: #FAF8F3;
--color-ink:     #171714;
--color-muted:   #67645E;
--color-line:    #D7D1C5;
--color-accent:  #B64A35;  /* single accent, used sparingly */
--color-success: #5E735D;
--color-warning: #B88946;
--color-danger:  #A33D32;
```

Type: editorial headings in Instrument Serif / Newsreader / EB Garamond; UI and body in
Geist / Inter; **mono only** for dates, IDs, scores, sources, timestamps.

Layout (desktop): three columns at roughly **15% / 60% / 25%** — date archive, today's
opportunities, application desk. The centre column is always the subject; the side columns
must not compete for attention.

Borders and rules carry the structure. Shadows only for true overlays (menus, dialogs).
Radii stay restrained: 4–8px on inputs, 0–12px on panels — not 20–32px everywhere.

## Roles are article entries, not floating cards

The failure mode of AI-generated frontends is that everything becomes a rounded rectangle,
so the page reads as a pile of plastic boxes. Use editorial entries separated by hairlines:

```text
────────────────────────────────────────────────────────────
03                                                 MATCH 91

Research Analyst — AI & Economic Policy
Company · Washington, DC

A concise summary of the role.

WHY IT MATCHES
+ Quantitative analysis experience
+ AI research background
− Consumer product experience missing

Posted 6 hours ago · Hybrid · Apply by Aug 12

[Review]        Save   Archive
────────────────────────────────────────────────────────────
```

Hierarchy comes from size, leading, rules, whitespace, numbering, and colour — not from
fifteen shadow variants.

## Vocabulary

Editorial names, with plain names available as subtitles so usability never suffers:

| Plain | Journal |
|---|---|
| Dashboard | Today's Edition |
| Job feed | Opportunity Desk |
| Saved | Shortlist |
| Applications | Application Ledger |
| Resume manager | Document Cabinet |
| AI recommendation | Editor's Pick |
| Archived | Filed Away |
| Rejected by me | Passed |
| Alerts | Watchlist |
| Analytics | Field Notes |

Note: `Passed` already exists as a real status in `docs/status-definitions.md`, and
`Application Ledger` matches how `data/applications.csv` is described — the vocabulary is
partly implemented already.

## Allowed / not allowed

Allowed: very light paper grain, faint print texture, annotation-style rules, numbering and
edition marks, a subtle stamp on save, underline-on-hover, content settling in line by line.

Not allowed: yellow-aged filters, heavy noise, fake stains, page-flip 3D, skeuomorphic
buttons, heavy glassmorphism, large shadows, everything-a-card, rainbow gradients,
blue-violet "AI glow", decorative 3D orbs or particle fields.

## Constraints when this is implemented

Visual layer only: no backend, API, schema, routing, or data-flow changes; no feature
removal; keep component props and events. Establish design tokens first
(typography, spacing, colour, border, button, status, layout), then convert page by page.
Keep full keyboard access, focus states, responsive layout, and `prefers-reduced-motion`.
The page must remain usable with no animation, texture, or web fonts loaded.

## Applying this to what exists today

The current apply queue already follows some of this: warm paper palette, serif display type,
single calm column, hairline separators instead of card stacks. The realistic gap list:

1. **Extract the template.** The page is generated from f-strings inside
   `scripts/generate_apply_queue.py` (~900 lines). A newline inside a `prompt()` string once
   broke every filter silently. Move HTML/CSS/JS into `templates/` and a real `.js` file
   before any restyling.
2. **Rename the freshness tiers.** `A/B/C/D` reads as a grade. Use
   Today / Backlog / Verify level / Older.
3. **Add the editorial lede.** Replace the stat line with one sentence, and demote counts.
4. **Explain the judgement.** The triage reason already exists per row — show it as
   "Why it matches" instead of hiding it in the CSV.
5. **One primary action per row**, driven by status, with Pass and Save secondary.
