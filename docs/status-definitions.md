# Status definitions

| Status | Meaning |
|---|---|
| discovered | Captured but not yet evaluated |
| researching | Hard eligibility, team, or role fit is being checked |
| referral_requested | A relevant person has been contacted about the live role |
| ready_to_apply | Materials and required facts are ready |
| applied | Submission confirmed by the user |
| oa | Online assessment received or underway |
| recruiter_screen | Recruiter conversation scheduled or completed |
| technical_screen | Technical interview stage |
| onsite | Final loop, virtual onsite, or equivalent |
| offer | Written or verbal offer received |
| rejected | Employer rejected the application |
| withdrawn | User withdrew |
| closed | Posting closed or no longer actionable |
| passed | User reviewed the JD and chose **not** to apply (experience gate, interest, fit, etc.). Not an employer rejection. Kept for memory so discovery will not resurface it in the apply queue. |

URL-level archive (even before a row exists in `applications.csv`) also lives in `data/job_decisions.csv` (`decision=pass`).

## Priority

- **A:** Strong fit, strategically valuable; apply fast and network (usually core).
- **B:** Reasonable fit; light tailoring.
- **C:** Lower strategic value; inexpensive apply only.

## Pursuit lane

- **core:** High conversion effort (tailor + network + follow).
- **broad:** Expand interview surface despite weak/no sponsorship signal; low pre-apply effort.
- **practice:** Intentional practice volume; cap ~15–25% of applied.

## Sponsorship signal

`verified` | `likely` | `unclear` | `no` — probability only. Never equate `no` with hard ineligibility.
