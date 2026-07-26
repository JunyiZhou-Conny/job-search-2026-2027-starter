# Hard eligibility vs sponsorship

These are **not** the same field and must not be collapsed.

## `eligibility` = hard gate only

Use `ineligible` only when at least one of these is true and verified from the posting or application:

- U.S. citizenship required
- Active security clearance required
- Internship requires return-to-school / a graduation window that matches **neither** real date: I-20 program end **2026-12-18** (December 2026 completion) **nor** commencement / school listing **March 2027**
- Start date conflicts with available work authorization timing (planned earliest FT **2027-01-18** from program end + OPT; confirm with HIO)
- Location / work model is actually unacceptable
- Role cannot be reasonably connected to your background (Health Data Science + target clusters)

Values: `verified` | `likely` | `unclear` | `ineligible`

## `sponsorship_signal` = probability, not eligibility

Values: `verified` | `likely` | `unclear` | `no`

- `no` or `unclear` does **not** make a role `ineligible`
- Prefer routing via `pursuit_lane` instead of discarding

## `pursuit_lane`

| Lane | When | Effort |
|---|---|---|
| `core` | Strong fit; sponsor verified/likely/unclear but company plausibly sponsors | Tailor, network, dossier if A |
| `broad` | Strong tech fit; sponsor `no` or weak; still may yield OA/interview | Nearest cluster resume; 1–2 bullets max |
| `practice` | Low conversion expected; used for interview reps | Cap at ~15–25% of applied volume |

## Dual graduation dates (both real)

| Date | Meaning | Use for |
|---|---|---|
| **2026-12-18** | I-20 / SEVIS program end | OPT, earliest FT, default resume, most “graduation / program end” forms |
| **2027-03** | Commencement / some Harvard listings | JD/forms that explicitly want Spring 2027 / March graduation |

Default resume: December 2026 program completion. Dual-date resume line when the posting needs March/Spring wording — still mention December program completion. Do not present only March as if program end were March.

## Work-authorization answers (typical for post-grad OPT)

Do not invent answers. After OPT EAD is in hand for full-time work:

- "Are you authorized to work in the United States?" → usually **Yes** (with valid EAD)
- "Will you now or in the future require sponsorship?" → usually **Yes** if future H-1B/employer sponsorship is needed

Never answer the second question **No** to bypass ATS. If the form conflates OPT/EAD/H-1B, save the **verbatim question and submitted answer** in `auth_qa_notes` and confirm with HIO when needed.
