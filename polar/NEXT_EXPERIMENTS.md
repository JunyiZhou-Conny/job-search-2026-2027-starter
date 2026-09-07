# Next experiments

Small tests. Each one should strengthen or kill a claim in
[`EVIDENCE.md`](EVIDENCE.md). Think like a browser-agent eval, not like
a feature list.

Do not Submit. Do not create accounts. Do not bypass security checks.
Do not run these as a way to apply faster.

## E1. Same-form Computer Use versus Polar

**Question.** On one named form, with one stop-before-Submit rule, where
does each executor spend its actions.

**Hypothesis.** A compiled Computer Use execute sheet still spends a
larger share of actions on screenshots and scrolls than Polar does on
the same mutations. Polar still needs a human paste unless mailbox-read
is proven.

**Controlled variables.**

- Same apply URL, or same Jobright Original Job Post landing URL
- Same standing answers
- Same forbidden list. No Submit, no Autofill Again, no Generate with AI
- Computer Use parent prompt comes only from `compile_cu_task.py`
- Polar prompt is the packet, not a chat improvisation
- One form family. Prefer Greenhouse, because both sides have already
  touched it. Do not switch to Workday mid-test.

**Measurement.**

- Wall time
- Mutation count
- Observation count. Scrolls, screenshots, rereads
- Human interventions
- Auth events
- Final field audit by a third pass that is not the executor
- `needs_review` fields

**Success.** Both sides reach ready-to-submit with zero invented facts.
The action mix is recorded. A 2x difference in observation share is
enough to keep C001 and C013 in the same conversation.

**Failure.** Either side invents a URL, opens a sibling, or Submits.
Discard the timing. If Computer Use cannot attach to the same session
class as Polar, report environment mismatch and stop. Do not compare a
logged-out cloud run to a logged-in laptop run and call it executor
quality.

**Safety.** Fill only. No new accounts. No CAPTCHA solving beyond a
human Take Control. No cookies in git.

This is the highest-information next test. See C018.

## E2. Parent compiler isolation

**Question.** Does a fresh parent, with no experiment text in the first
message, copy the standing Computer Use slice into the Task string.

**Hypothesis.** If the parent reads `docs/automation/COMPUTER_USE_PROMPT.md`
and runs the compiler, the child transcript's first user message contains
the standing forbids. If the parent freehands, it does not.

**Controlled variables.** New Cloud Agent. One leftover paste or one
named correction. No Submit. Do not paste this dossier into the first
message.

**Measurement.** Child transcript user-message count and whether the
Task contains no Autofill Again, one paste, and no verify-each.

**Success.** Compiler path includes the slice. Freehand path is the
control and may fail.

**Failure.** We only test inside a chat that already contains the
rules. That is the failure mode named on 2026-08-24. The test would
be INCONCLUSIVE.

**Safety.** Same as leftover_typing_one_pass. No live 10-tab Chrome
unless I name the tab.

This is the cheapest test. It is still open.

## E3. Polar mailbox-read

**Question.** Can Polar execute `generated/polar/LIVE.md` from repo
context without a chat paste.

**Hypothesis.** Polar can open the file and follow it. Unattended
Workflow is a later question.

**Controlled variables.** One LIVE.md. One job already selected by
Cursor. No job list in Polar's context. Stop before Submit.

**Measurement.** Whether Polar reads the file. Whether it rediscovers
a different requisition. Whether the report matches the packet ids.

**Success.** Polar uses the file and no other KEEP.

**Failure.** Polar ignores the file, invents an apply URL, or iterates
a list. Keep the paste bus.

**Safety.** Same Live Slot rules as the Quantbot packet. No Submit.

Sibling-branch gate P3 already names this. Do not pretend it is proven.

## E4. Workday fill, only with an existing session

**Question.** Is the Rakuten Create Account wall a Polar limit or a
missing Workday session.

**Hypothesis.** If I am already signed into that Workday tenant, Polar
can fill standing fields. If I am not, Polar should stop. Creating the
account is not the experiment.

**Controlled variables.** A tenant I already use. Packet says do not
register. Reach and fill scored separately.

**Measurement.** Host, account wall yes or no, fields filled, submitted
must be no.

**Success.** Fill on a pre-existing session, or a clean stop on the wall.

**Failure.** Polar creates an account, or we treat a wall as a fill.

**Safety.** Do not register. Do not Submit.

## What I am not running

- Parallel Polar tabs on one profile. Not isolated.
- Dummy-page concurrency probes. They do not touch Original Job Post
  or Copilot.
- Mass apply. G2 is closed.
- Any test whose success condition is "looks impressive on video."
