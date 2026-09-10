# Hard eligibility vs sponsorship

These are **not** the same field and must not be collapsed.

## `eligibility` = hard gate only

Use `ineligible` only when at least one of these is true and verified from the posting or application:

- U.S. citizenship required
- Active security clearance required
- Internship requires return-to-school / a graduation window that matches **neither** real date: I-20 program end **2026-12-18** (December 2026 completion) **nor** commencement / school listing **March 2027**
- Start date conflicts with available work authorization timing (planned earliest FT **2027-01-18** from program end + OPT; confirm with HIO)
- Location / work model is actually unacceptable (including a clear
  non-US work city/country such as Belgrade; `non_us_location`)
- Role cannot be reasonably connected to your background (Health Data Science + target clusters)

Export compliance / ITAR / U.S. Person on a rocket or defense form is
**not** this list. Keep those jobs in discovery. Do not filter them
out. Care is low. No need to submit. See
`knowledge/form_strategy.yaml` `us_person_export_control`.

Values: `verified` | `likely` | `unclear` | `ineligible`

## `sponsorship_signal` = probability, not eligibility

Values: `verified` | `likely` | `unclear` | `no`

- `no` or `unclear` does **not** make a role `ineligible`
- Prefer routing via `pursuit_lane` instead of discarding

## `pursuit_lane`

| Lane | When | Effort |
|---|---|---|
| `core` | Strong fit; sponsor verified/likely/unclear but company plausibly sponsors | Tailor, network, dossier if A |
| `broad` | Strong tech fit; sponsor `no` or weak; still may yield OA/interview | Approved base resume. 1–2 bullets max |
| `practice` | Low conversion expected; used for interview reps | Cap at ~15–25% of applied volume |

## `application_weight` (separate filter)

`regular` vs `prioritized` (GTC 2026 / startup / prestige). Not the letter
`priority` field. See `knowledge/application_priority.yaml` and
`docs/apply/PRIORITY.md`. Prioritized on Polar Local: full form prep,
mandatory writing_log, then Submit. Cursor Cloud still uses a review
packet. The referral hold was retired 2026-08-24. Confirm the weight
before writing it onto a ledger row.

apply-ready-jobs re-reads the full employer posting before major fill
and applies these same hard rules. A fuller JD can reveal a skip that
discovery missed. Sponsorship unknown or no is still not a skip.
Graduation-window policy is unchanged.

## Dual graduation dates (both real)

| Date | Meaning | Use for |
|---|---|---|
| **2026-12-18** | I-20 / SEVIS program end | OPT, earliest FT, default resume, most “graduation / program end” forms |
| **2027-03** | Commencement / some Harvard listings | JD/forms that explicitly want Spring 2027 / March graduation |

Default resume: December 2026 program completion. Dual-date resume line when the posting needs March/Spring wording — still mention December program completion. Do not present only March as if program end were March.

## Work-authorization answers

Exact question → one matching fact. Do not copy one answer onto a
neighboring field. Do not volunteer F-1, OPT, EAD, citizenship, or
sponsorship on a field that did not ask.

| Exact question | Fact | Required | Optional |
|---|---|---|---|
| Will you now or in the future require visa sponsorship? | `future_sponsorship_required` | **Yes** | leave blank |
| Do you require sponsorship to begin employment? | `sponsorship_required_to_begin` | unknown → BLOCK that job | leave blank |
| Will you require H-1B sponsorship? | `h1b_sponsorship_required` | **No** | leave blank |
| Are you a U.S. citizen? / country of citizenship | `citizenship_country` | **China** | leave blank |
| What is your visa / status? | `current_status` | **F-1** | leave blank |
| Are you currently authorized to work in the U.S.? | `current_us_work_authorization` | unknown → BLOCK that job | leave blank |
| Are you authorized to work in the U.S.? (no currently/now) | `legally_eligible_to_begin_immediately` | **Yes** | leave blank |
| Authorized to work for any employer? | `authorized_for_any_employer` | **Yes** | leave blank |
| Do you have an EAD? | `opt_ead_in_possession` | **No** | leave blank |
| Has OPT been approved? | `opt_approved` | **No** | leave blank |
| Will you be eligible for OPT? | `opt_eligible_expected` | **Yes** | leave blank |
| Will you require work authorization (no sponsorship words)? | none | BLOCK that job | leave blank |

If one required widget conflates two of those semantics, leave that
field, mark only that job BLOCKED, and continue the batch. Save the
verbatim question in `auth_qa_notes`.
