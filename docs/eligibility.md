# Hard eligibility vs sponsorship

These are **not** the same field and must not be collapsed.

## `eligibility` = hard gate only

Use `ineligible` only when at least one of these is true and verified from the posting or application:

- U.S. citizenship required
- Active security clearance required
- Internship requires return-to-school after the internship, and you graduate December 2026
- Start date conflicts with available work authorization timing
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

## Work-authorization answers (typical for post-grad OPT)

Do not invent answers. After OPT EAD is in hand for full-time work:

- "Are you authorized to work in the United States?" → usually **Yes** (with valid EAD)
- "Will you now or in the future require sponsorship?" → usually **Yes** if future H-1B/employer sponsorship is needed

Never answer the second question **No** to bypass ATS. If the form conflates OPT/EAD/H-1B, save the **verbatim question and submitted answer** in `auth_qa_notes` and confirm with HIO when needed.
