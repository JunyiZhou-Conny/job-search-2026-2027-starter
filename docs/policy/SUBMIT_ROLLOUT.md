# Submit policy and rollout ladder

Owner intent as of 2026-09-03. This file is the single source for when an
agent may click Submit. Every other file that mentions Submit points here.
The older blanket rule "never Submit without explicit confirmation" was a
stage of experimentation, not a permanent product requirement. It is
retired as policy. Facts about Junyi are unchanged by this file.

## Two lanes

| Weight | Who submits | What the agent does |
|---|---|---|
| `regular` | the agent, once the gate for the ATS family is open | cluster resume, truthful concise answers, fill, validate, Submit once, verify, record |
| `prioritized` | Junyi, after a review packet | deeper research, tailored resume from the evidence bank, real Why-us, referral check, full form prep, stop before Submit, compact packet |

`prioritized` is decided by `knowledge/application_priority.yaml`. The
FIFO argument (do not wait for a rare insider page) applies to regular
rows. For prioritized rows the agent does more work before Junyi sees
it, and Junyi clicks or says "submit it".

## Ladder

Gates open per ATS family. They open on evidence, never on time. The
machine-readable copy is `config/submit_gates.yaml`;
`scripts/apply_ledger.py preflight` refuses any attempt above the open
gate, and the two files must agree.

| Gate | Condition to open | Ashby | Greenhouse | Lever | Workday |
|---|---|---|---|---|---|
| G0 fill only | `check_apply_harness.py` ready | open | open | open | closed (account wall) |
| G1 fill plus human review | identity check at run start, stop-the-line table applied | open | open | untested | closed |
| G2 limited autonomous regular Submit | one tab, Autofill once, corrections from repo knowledge, no required free response or answer from the approved bank, sponsorship question absent or H-1B-named, cap 3 per run, banner plus a durable second signal, ledger row written before the next job, rerun shows no duplicate | closed. 4 of 4 controlled Submits on 2026-08-24 were practice-lane, identity-only forms with a banner and a Simplify overlay. Opens after one wanted regular role completes the full protocol below with durable evidence and a blocked rerun. | closed | closed | closed |
| G3 broader regular automation | 10 consecutive verified regular Submits with zero wrong-fact incidents, one independent channel (confirmation email or application id) wired, scheduled run proven idempotent twice | closed | closed | closed | closed |
| prioritized rows | human review packet before Submit, always | policy | policy | policy | policy |

## Stop-the-line (applies at every gate)

Block Submit and record the reason when any of these hold.

- Copilot filled EEO (gender, race, veteran). `disability_status` is the
  one EEO field with a standing answer (No).
- Work authorization widget shows US citizen or green card.
- A sponsorship question is broad ("now or in the future") and the
  owner's confirmation in section "Open owner decisions" is still open.
- A required free response has no approved answer in
  `knowledge/written_response_bank.yaml` or
  `docs/apply/written_answers/`.
- The posting is closed, 404, or "no longer open". Close the tab, write
  `decision=closed`, never pick a sibling.
- Company or title on the page differs from the row.
- Non-US work location.
- An external artifact (exercise URL, portfolio piece) is required and
  not in the profile.
- `application_weight = prioritized`.

## Protocol for a G2 Submit

1. `check_apply_harness.py` ready and the Simplify dashboard shows
   Junyi Zhou, with the dashboard screenshot saved under
   `generated/apply_runs/<run_id>/`.
2. `scripts/apply_ledger.py preflight ... --out generated/apply_runs/<run_id>/<slug>.preflight.json`
   must print `verdict: pass`. It checks the gate table, the duplicate
   set (`applications.csv`, `job_decisions.csv`, `apply_attempts.csv`,
   newest Simplify export), weight, harness and identity flags, the
   per-run cap, and for Ashby the live form (open, no required essay,
   no broad sponsorship or export-control question, no external
   artifact). `start` refuses without that file.
3. One Chrome tab. Copilot Autofill once. Never Run Autofill Again after
   corrections. Never Generate with AI.
4. Corrections only from `config/profile.yaml`,
   `knowledge/form_strategy.yaml`, `knowledge/work_authorization.yaml`.
5. One screenshot of the filled form. Validator reads it against the
   stop-the-line list.
6. Submit once. One screenshot of the result. No retry on a spam wall.
7. Verify: Ashby success banner text, then export the Simplify tracker
   (Export CSV in the tracker toolbar) into `data/imports/simplify/` and
   confirm the row is there. Email or an ATS application id also count.
8. Ledger: `apply_ledger.py finish --outcome submitted_verified` with the
   banner text and the export path. The command refuses a second signal
   that is not a file under `data/` or an application id, and refuses to
   finish an attempt twice. Screenshots go under
   `generated/apply_runs/<run_id>/`.

## Open owner decisions

- Broad sponsorship question. The 08-24 recorded answer "No, I do not
  need sponsorship" contradicts the fact `future_sponsorship_required:
  true`, and the recording is agent prose. On 2026-09-03 the standing
  answer in `knowledge/form_strategy.yaml` and
  `knowledge/work_authorization.yaml` was set back to `leave_for_junyi`
  and `never_lie_to_bypass_ats` back to `true`. Junyi decides, in
  writing, one answer per exact question wording. Until then agents
  skip Submit on forms that ask it broadly and answer No only when the
  question names H-1B.
- Outlook MCP authentication for confirmation-email verification.

## History

Blanket ban text existed in `AGENTS.md`, `.cursor/rules/00-core-system.mdc`,
`knowledge/form_strategy.yaml`, `.cursor/rules/13-computer-use-fire-and-forget.mdc`,
`docs/automation/WEEKDAY_APPLY_AUTOMATION.md`, and
`docs/apply/written_answers/README.md`. See `docs/state/REALITY_MAP.md`
section 7 for the contradictions that motivated this file.

## Where attempts are recorded

`data/apply_attempts.csv` holds one row per Submit attempt with outcome and
evidence (`scripts/apply_ledger.py`). `data/applications.csv` stays the
current-state ledger and is updated from the attempt outcome. Rows are
append-only; a finished attempt cannot be rewritten. Outcomes:
`submitted_verified` needs the banner text plus a durable second signal
(a tracker export or email file under `data/`, or an ATS application id);
`submitted_unverified` is a banner alone; `submit_failed`, `blocked`,
`review_packet`, `posting_closed`, `not_run`. The four 2026-08-24
`submitted_verified` rows are bound to the 2026-09-03 Simplify export,
which lists each of them as APPLIED on 08-24.
