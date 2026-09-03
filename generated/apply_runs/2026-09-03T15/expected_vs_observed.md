# Anyscale Ray Data — expected vs observed

Parent compared screenshots to the compiled sheet. Worker checkmarks were not used as proof.

| Field | Expected | Observed | Evidence |
|---|---|---|---|
| Simplify account | Junyi Zhou | Junyi Zhou | 00_identity.png |
| Name | Junyi Zhou | Junyi Zhou | 01_after_autofill_top.png, 02_company.png |
| Email | profile email | matches `config/profile.yaml` | 01, 02 |
| Current location | Boston, MA | Boston, MA, USA | 01, 02. Left untouched. |
| Current company | empty | empty | 02_company.png. Copilot had Harvard University. |
| Hybrid Mon/Tue/Thu | Yes | Yes | 03_questions.png |
| Relocate to SF Bay | Yes | Yes | 03_questions.png |
| Visa sponsorship for this country | No | No | 03_questions.png |
| Additional information / Other | empty | empty | 03_questions.png |
| Submit | not clicked | Submit Application still visible, not clicked | 03_questions.png |

Copilot sidebar still listed hybrid and relocate under Need review after Yes was selected. Completed is not a value check.

No second Computer Use VERIFY pass. The two post-mutation screenshots were enough.

G2 preflight after start: `duplicate` (this attempt) and `gate_closed:ashby=G1<G2`. Identity is verified this run. Submit is not permitted.
