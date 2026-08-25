# Apply project — first corporate structure (brain jar)

Junyi 2026-08-25. Thinking only. Not a runbook to spawn Bots or Submit.

This note turns Junyi's hierarchy complaint into a roster we can
reason about before spending tokens. Reality still has to test it.
Tokens are limited, so the first live test must be small.

## What Junyi is saying

The CoS + Researcher / Writer / Ops roster is too naive for
auto-apply. The Chief of Staff is cooking (doing the work) instead of
judging. Junyi is still the supervisor on every click. That wastes the
point of many Grok Bots working at once.

Different ATS pages need different clicker minds. Ashby is short and
mostly handled **before Submit**. Workday and Jobright walls are
another class: accounts, email codes, many pages. Semi-supervised
either way (standing rules + the mind reasons on leftovers), but the
rule packs are not the same.

Inside one Grok Bot teammate: the **mind** writes a sticky note; the
**hand** is another agent that only clicks. Time-to-click and length
of the hand's thought chain are metrics, not vibes.

We should design top-down, then let a cheap trial punch holes in it.
We should not buy unlimited trial-and-error.

## Facts this note must not blur

- The **10-tab** Copilot work was review-only. No Submit there.
- Cloud **did** Submit four short Ashby forms (Anyscale + three
  trivials) as named isolation tests. That is not a 10-tab Submit
  license. Charta Cloud Submit hit a spam wall and did not land.
- Ashby-before-Submit is **good enough to be satisfied**, not
  "finished." Leftovers, EEO, Autofill Again, and Submit-time walls
  still exist. See `knowledge/form_strategy.yaml` on later branches.
- Workday: we have seen a **CVS account-creation wall**. We have not
  mapped a full multi-page Workday apply. Per-company profile + email
  verify is Junyi's working model; treat extra page-count detail as
  **unknown until one study job**.
- Jobright "Apply" is often a signup wall, not the employer ATS
  (2026-07-31 trial).

## Why the current three-worker shop fails

| Role now | What it should do | What happens |
| --- | --- | --- |
| Chief of Staff | Assign, accept/reject, escalate to Junyi | Does the apply path |
| Researcher | Facts and URLs | Idle or unused |
| Writer | Why-us drafts | Idle unless Junyi asks |
| Ops | Tracking and routines | Idle |
| Junyi | Submit, 2FA, account create | Supervises every click |

A head chef does not plate every dish. Parallel Bots only pay off if
**specialists cook** and **Junyi only touches gates**.

## Design rules for this prototype

1. **CoS does not click ATS and does not write Why-us.**
2. **One job, one cooking teammate.** No two minds on the same tab.
3. **Lane by ATS**, not by "researcher vs writer." Ashby playbook ≠
   Workday playbook.
4. **Semi-supervised:** standing rules go on the sticky note; the mind
   reasons only on uncatalogued leftovers. Do not invent GPA,
   citizenship, or project URLs.
5. **Hand is internal.** Do not hire a second named Bot just to be
   "the clicker" unless a trial proves the mind/hand split needs a
   visible teammate. xAI: each Bot already has a hand.
6. **Shared computer** ([SHARED_COMPUTER.md](SHARED_COMPUTER.md)):
   parallel screens, same logins. Do not use extra Bots as vaults.
7. **Expensive lanes stay at 0 or 1** until a playbook exists.
   Workday is not N-way parallel.
8. **Junyi-only gates:** Submit, send, Workday email/2FA, new ATS
   accounts, MyGreenhouse login.
9. **Auditor, not Junyi, is the first reviewer.** Junyi sees a
   one-page exception list.

## Org chart (pilot)

```text
                         Junyi
                     (gates only)
                           |
                    Chief of Staff
                     (does not cook)
                    /      |      \
              Triage    Auditor    Ops
           (classify)  (accept /   (time,
                        send back)  tokens)
                           |
                    cooking lane
                           |
              +------------+------------+
              |            |            |
           Ashby      Greenhouse     Workday
          (1 mind)    (0 until       (0 until
                       needed)        one study)
              |
           Writer
        (on-call only)
```

Jobright is **not** a cooking lane. Triage resolves to an employer
ATS or marks skip. Nobody "applies on Jobright."

## Teams and headcount

Human (not a Bot): **Junyi × 1**

| Team | Members | Count (pilot) | Count (later, only if pilot works) | Role |
| --- | --- | --- | --- | --- |
| Office of the Chief | Chief of Staff | 1 | 1 (or 1 per company-level chief later) | Pick the next named job. Assign **one** cooking teammate. Read Auditor + Ops. Accept, send back, or escalate. Never Autofill, never paste Why-us, never Submit. |
| Intake | Triage | 1 | 1 | Open the URL. Label ATS: Ashby / Greenhouse / Workday / Jobright wall / other / closed. Output: lane + skip reason. Does not fill the form. |
| Ashby cell | Ashby specialist (mind) | 1 | N (one job each) | Compile the Ashby sticky note from `form_strategy.yaml`. Autofill once. Correct leftovers. Stop before Submit. Hand clicks; mind does not resume to verify a paste. |
| Greenhouse cell | Greenhouse specialist | 0 | 1, then N | Same as Ashby, plus: never MyGreenhouse login. EEO filled → cannot unattended-Submit. |
| Workday cell | Workday specialist | 0 | 1 study mind, never N until playbook | One named study job, **no account create**. Map pages and widgets. Write rules. Stop. Email verify is Junyi. |
| Copy | Writer | 0 standing | 1 on-call | Why-us / leftover essay only when CoS assigns a draft. File goes in `docs/apply/written_answers/`. A file is not a Submit. |
| Quality | Auditor | 1 | 1 | Compare **visible form** to standing rules. Score leftovers. Block if EEO touched, sponsorship wrong, invented facts, or Autofill Again. Does not click. |
| Finance | Ops | 1 | 1 | Per job: wall-clock, hand thought-chain length, Autofill vs leftover vs dead clicks. Stop the lane if a job exceeds a budget Junyi set. No apply clicks. |

**Pilot live roster = 5 Bots + Junyi.**  
CoS, Triage, Ashby × 1, Auditor, Ops.  
Researcher-as-a-standing-role is dropped. URL facts are Triage.
Writer is summoned, not seated.

**Do not staff Workday or N Ashby clickers in the first trial.**

## What each person does on one job

1. CoS names one URL (or takes a keep Junyi already marked).
2. Triage returns `ats=ashby` or skip.
3. If skip (Jobright wall, Workday account, closed, non-US): stop.
   Ops logs why. No hand.
4. If Ashby: Ashby mind gets the job + the standing slice only
   (sponsorship No, no Autofill Again, no Generate with AI, relocate
   Yes, current company empty, …).
5. Hand runs. Mind records time + thought-chain length for Ops.
6. Auditor reads screenshots / the form, not the mind's story.
7. CoS: accept (ready for Junyi) or send back **once** with a
   specific defect. Second fail → escalate.
8. Junyi: Submit or not. Nobody else.

## Why this is better than CoS + 3 generalists

- Cooking is ATS-shaped. A Writer does not help a Workday wall.
- Supervision moves from Junyi-on-every-click to Auditor-on-every-job
  and Junyi-on-gates.
- Token spend is visible (Ops) and capped on the expensive lane.
- Parallelism is **N Ashby minds on N jobs**, not 10 minds on one
  Workday.
- Matches xAI's path: one safe task (one Ashby job, stop before
  Submit) before skills or routines.

## Cheap trial (when Junyi says go) — still no Submit

One Ashby URL already in the 10-tab or isolation set. CoS may only
assign. Ashby mind may only fill. Auditor must catch at least one
known leftover class (sponsorship widget or current company). Ops
must return time + thought-chain length.

Pass: Junyi never had to steer a click. Fail: CoS cooked, or Junyi
had to babysit the hand.

Workday study is a **later** one-job, no-account, no-Submit pass.

## Open / not yet

This is a first prototype of a corporate structure. It is not
permission to spawn the roster. Isolation and `form_strategy.yaml`
still apply.
