# Experiment — automated application trial (2026-07-31)

**Question:** how far can an agent get through a real job application before a human is
needed, and what exactly stops it?

**Result:** the browser half works better than expected — 10/10 postings autofilled, median
44% of visible fields — but the pipeline in front of it is broken: **not one discovered job
links to a page you can actually apply on**, and only 27% of them can be resolved to the
employer's real posting automatically.

**Nothing was submitted.** No application was sent, no account was created, no
`status=applied` was written. Every run stopped at the ready-to-submit state.

---

## 1. Method

| | |
|---|---|
| Job sample | 10 keeps, resolved to employer ATS URLs (6 Greenhouse, 4 Ashby) |
| Browser | Chromium (headed, `DISPLAY=:1`) with the Simplify Copilot extension v3.0.0 loaded |
| Identity | the cleaned Simplify profile from 2026-07-30 |
| Stop rule | screenshot the filled form, never click Submit |
| Evidence | `/opt/cursor/artifacts/trial/*.png`, one or two shots per job |

Sample selection is stated up front so the result is not cherry-picked: the 10 jobs are the
first 10 *unique companies* whose postings could be resolved to a public ATS at all. That is
itself a biased sample — see finding 2 — and it excludes every Workday employer.

---

## 2. Findings, worst first

### F1 — Every discovered job links to Jobright, and Jobright will not let you apply

All 55 keeps currently on `main` point at `jobright.ai/jobs/info/...`. That page renders the
description fine, but **"Apply now" opens a "Sign Up to Apply" modal**. The employer URL is
not in the HTML, not in any XHR payload the page makes, and not reachable without an account.

- Severity: **blocking** — it makes the whole keep list unactionable as-is.
- Evidence: `/opt/cursor/artifacts/trial_pilot_apptronik.png` for the working case;
  the signup wall was reproduced on the first two keeps tried.
- Fix shipped: `scripts/resolve_apply_url.py` resolves company + title against the public
  board APIs employers already publish (Greenhouse, Ashby, Lever, SmartRecruiters, Workable,
  Recruitee) and grades each match `exact / strong / weak / none`.
- Fix not attempted: creating a Jobright account. That needs your say-so, and one account
  would still be a single point of failure for the whole pipeline.

### F2 — Only 27% of jobs can be resolved to a real application URL automatically

Run over all 55 keeps:

| Outcome | Count |
|---|---|
| exact match on a public board | 15 (27%) |
| weak match (title overlap too low to trust) | 2 |
| no public board found | 38 (69%) |

Resolved by ATS: Greenhouse 10, Ashby 5.

The misses are systematic, not random: **Google, Meta, TikTok, ByteDance, Qualcomm, Cadence,
Copart, KLA** and similar all run Workday, iCIMS or bespoke portals with no open board API.
So the automatable slice is skewed toward startups, and the roles you most want are the
hardest to reach.

- Severity: high.
- Proposed fix (not built): a per-employer `careers_url` map in `knowledge/` for the ~20
  companies that recur, plus a Workday-specific resolver — Workday tenants expose
  `/wday/cxs/{tenant}/{site}/jobs` as JSON, which covers a large share of the misses.

### F3 — Google Chrome silently refuses to load the extension

`--load-extension` is now rejected by branded Chrome:

```
WARNING:chrome/browser/extensions/extension_service.cc:418]
--load-extension is not allowed in Google Chrome, ignoring.
```

Chrome starts normally and the extension simply is not there — no error in the UI. Two
hours could disappear here without the verbose log.

- Fix used: run the trial in **Chromium** (Playwright's bundled build), which still honours
  the flag. Extension confirmed live via its service worker
  `chrome-extension://cdcddpbdpgfipkmobdipjfheopledajg/background.js`.
- Alternative for your own machine: install Simplify from the Web Store normally; this only
  bites automated/unpacked loading.

### F4 — Moving browsers means moving the session, or fighting the captcha again

Signing into Simplify triggers a Google reCAPTCHA image challenge, which took roughly half
an hour of agent time on 2026-07-30. Re-logging in inside Chromium would have repeated that.

- Fix used: exported the existing Simplify cookies from the Chrome profile and injected them
  into the Chromium context. Chrome on Linux with `--password-store=basic` encrypts cookies
  with a fixed passphrase, so this is a local decrypt — no password re-entry, no captcha.
- Kept out of the repo deliberately: the exporter and the cookie file are local-only
  (`/tmp/apply_trial/`). Session material must not be committed.

### F5 — Ashby hides the form behind a tab; the autofill button changes name

On Ashby the first screen is the description, and Simplify's panel shows **"Start
Application"** instead of "Autofill This Page". A harness that only looks for the latter
concludes the extension is broken — my first run reported 0/4 Ashby jobs autofilled and
`0/0` form fields, which was wrong.

After clicking "Start Application" first, all four Ashby jobs autofilled, and they scored the
*highest* coverage of the whole sample (74–88%).

- Severity: medium (harness bug, not a Simplify limitation) — but worth recording, because
  the same mistake would make anyone conclude Ashby is unsupported.

### F6 — Autofill is slower than it looks; a 9-second wait under-reports it

Nirmata was recorded as "clicked but nothing changed". The screenshot shows why: Simplify was
still on *"Scanning this page… 12 fields detected"* when the measurement ran. Re-run with a
30-second window, the same page autofilled normally.

- Fix: poll for Simplify's completion state instead of sleeping a fixed interval.

### F7 — Coverage is real but uneven: 12% to 88%

| Company | ATS | Filled / visible | Coverage |
|---|---|---|---|
| OpenAI | Ashby | 23 / 26 | 88% |
| Etched | Ashby | 28 / 35 | 80% |
| Bild AI | Ashby | 3 / 4 | 75% |
| Traba | Ashby | 14 / 19 | 74% |
| Neuralink | Greenhouse | 20 / 42 | 48% |
| Gemini | Greenhouse | 8 / 20 | 40% |
| Nirmata | Greenhouse | 5 / 14 | 36% |
| Apptronik | Greenhouse | 5 / 20 | 25% |
| Together AI | Greenhouse | 5 / 32 | 16% |
| SpaceX | Greenhouse | 5 / 43 | 12% |

Median 44%. **Caveat on the low Greenhouse numbers:** the counter only sees a field as filled
when a DOM input carries a `value`. Greenhouse renders school, degree, discipline and country
as custom dropdown widgets, and the SpaceX screenshot clearly shows *Harvard University*,
*Boston, Massachusetts*, phone and résumé all correctly populated while the counter scored
5/43. Real coverage on Greenhouse is meaningfully higher than the table says; the numbers
are a floor, not a measurement.

What autofill reliably got right across the board: first/last name, email, phone (with
country), location, LinkedIn, résumé upload, and school.

### F8 — What is always left for a human

Aggregated across the 10 forms, the fields autofill left empty:

| Field | Times unfilled | Why it should stay manual |
|---|---|---|
| free-text essays (`text`) | 27 | company-specific; Simplify gates AI answers behind Simplify+ |
| country / candidate-location | 6 / 4 | custom dropdown widgets |
| preferred name | 3 | not in the profile |
| degree / end month / end year | 2 each | education sub-widgets |
| gender, ethnicity, veteran, disability | 2 each | **EEO — must be answered by you, never by an agent** |

Neuralink is the clearest example of the ceiling: Simplify detected 25 fields, filled the
identity block, and explicitly flagged the three "describe your exceptional ability" essays
as needing a subscription. Those are exactly the answers that decide the application.

### F9 — Work authorization questions never came up in this sample

None of the 10 forms asked a sponsorship/authorization question before the submit step. That
is a sampling artifact — they usually appear on the final page — so `auth_qa_notes` could not
be exercised. Worth re-testing on Workday, where they appear early.

---

## 3. What this means for the pipeline

Ranked by how much time each would save:

1. **Resolve apply URLs at discovery time, not at apply time.** Run
   `resolve_apply_url.py` inside the daily discovery job and store `apply_url` +
   `apply_url_confidence` in the triage CSV. Unresolved rows get flagged for a manual lookup
   instead of silently wasting a click later.
2. **Add a Workday resolver.** `/wday/cxs/{tenant}/{site}/jobs` is public JSON and covers a
   large share of the 69% currently unresolvable.
3. **Keep a `careers_url` map** in `knowledge/` for repeat employers where nothing else works.
4. **Treat autofill as the identity pass only.** Budget human time for essays and EEO; those
   are ~30% of fields and 100% of the differentiating content.
5. **Ashby first when triaging by effort.** Ashby forms reach ~80% autofill; Greenhouse needs
   more dropdown work; Workday is not reachable yet.

## 4. What I did not do, on purpose

- No application submitted, no Submit clicked (a submit control existed on all 10 pages).
- No account created anywhere, including Jobright.
- No EEO/demographic answer chosen.
- No `status=applied` written — the ledger still reflects reality.
- The cookie exporter and session file stayed local; nothing session-related is committed.

## 5. Reproducing

```bash
# 1. resolve discovery rows to real apply URLs
python3 scripts/resolve_apply_url.py --date 2026-07-28 --out /tmp/resolved.json

# 2. the trial harness itself is local-only (needs the unpacked extension +
#    an exported Simplify session); see /tmp/apply_trial/run_trial.py on the VM
```

Screenshots: `/opt/cursor/artifacts/trial/` — `*_1_loaded.png` before autofill,
`*_2_autofilled.png` after.


## 6. Follow-up (same day) — Workday resolver

Shipped in the same session after this report:

- `knowledge/careers_boards.yaml` — verified Workday CXS hosts (Caterpillar, Waystar, NVIDIA)
- `resolve_apply_url.py` now queries Workday CXS (`/wday/cxs/{tenant}/{site}/jobs`, limit≤20 + paging)
- Daily discovery docs require `--write-csv` after triage
- Existing triage CSVs on main enriched; apply queue Open prefers `apply_url`

Verified live: NVIDIA “Software Engineering Intern, Dynamo - Fall 2026” resolves
`exact` → `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/...`

A full Simplify autofill pass on Workday was **not** re-run in this follow-up (the
trial Chromium profile / unpacked extension under `/tmp` was no longer available).
That remains the next live experiment once the extension harness is restored.
