# profile.md

Copy this file to `profile.md` and replace every `<...>` placeholder. This is the **single
source of truth** for every field the agent puts on an application form.

`profile.md` is gitignored. Don't commit it, and don't put anything here you wouldn't want
an agent to type into a form — because it will.

---

## Identity

- **Legal name:** `<First Last>`
  Exactly as it should appear. Autofill has been observed inventing titles and suffixes
  ("Mr. Firstname Lastname Sr.") — the agent must strip anything not written here.
- **Name pronunciation (phonetic):** `<FUR-st LAST-name>` — some forms require this field
- **Application email:** `<yourname_application@outlook.com>`
  The agent uses this for every ATS account and never your personal address.
- **Phone:** `<(555) 123-4567>` — type: `<Mobile>`
- **Address:** `<123 Main Street>`, `<City>`, `<ST>` `<ZIP>`, `<Country>`
- **LinkedIn:** `<https://www.linkedin.com/in/your-handle>`
- **GitHub / portfolio:** `<optional>`

## Education

Most recent first. One block per school.

- **School:** `<University>` — `<City, ST, Country>`
  **Degree:** `<M.S.>` in `<Field>`
  **Dates:** `<08/2025>` – `<12/2026>`
  **GPA:** `<3.9>`
  **Is this your highest level of education?** `<Yes>`
  Some forms ask this per-school as a Yes/No; answer Yes only for the most advanced degree.

- **School:** `<University>` — `<City, ST, Country>`
  **Degree:** `<B.S.>` in `<Field>`
  **Dates:** `<08/2021>` – `<05/2025>`
  **GPA:** `<3.9>`
  **Is this your highest level of education?** `<No>`

**Program timing** — write this out in plain language, because forms ask it three different
ways and autofill guesses wrong:

- Requirements complete: `<December 2026>`
- Commencement / degree conferred: `<March 2027>`
- **Available to start full-time:** `<January 2027>`
- Concrete start date to use when a form demands one: `<01/04/2027>`
- Anticipated graduation season, if offered as a picker: `<Spring 2027>`

## Work experience

One block per entry. **Every entry needs a `Company` value** — Workday and others reject a
blank one. Personal or solo projects go in as `Self-Employed`, not blank.

- **Company:** `<Employer, or Self-Employed>`
  **Title:** `<Title>`
  **Dates:** `<05/2025>` – `<Present>`
  **Location:** `<City, ST>`
  **Summary:** `<2-3 factual lines. Every number here must be defensible.>`

## Skills

List **only** what you'd defend in an interview. The resume generator has been caught adding
a language the candidate had never written. The agent must not add to this list.

- **Languages:** `<Python, R, SQL>`
- **Tools / frameworks:** `<...>`
- **Spoken languages:** `<English — Proficient (C2)>` (Workday wants a proficiency level)

## Answers only you can give

These are legal attestations or personal decisions. The agent reads them here and **must
never infer them.** Update this section if your status changes.

- **Currently legally authorized to work in `<country>`:** `<Yes / No>`
- **Will you now or in the future require visa sponsorship:** `<Yes / No>`
  These are two different questions and autofill gets them wrong in both directions.
- **Current visa / status:** `<F-1 OPT / Citizen / Permanent Resident / ...>`
- **Salary expectation:** `<65000>` — used unless the posting implies otherwise
- **Willing to relocate:** `<Yes / No>`
- **Office preference, if asked:** `<No preference>`
- **Veteran status:** `<I am not a protected veteran>`
- **Disability self-identification:** `<your choice, or "Decline to self-identify">`
- **Race / ethnicity / gender (voluntary EEO):** `<your choice, or "Decline to self-identify">`
- **"How did you hear about us?"** → default `<LinkedIn>`. If the option list has no
  LinkedIn and no neutral choice, pick any option rather than stalling. Never claim an
  employee referral that doesn't exist.
- **AI interview-notetaking consent, if asked:** `<Yes / No>`

## Never fill in — hard stops

If a required field needs one of these, the agent logs `BLOCKED` and moves on. It does not
guess, and it does not approximate.

- `<Exact date of birth>` — or delete this line and add it above if you're comfortable
  storing it
- `<SSN / national ID>`
- `<Anything not written in this file>`

Add your own. The rule is: if it isn't in this file, it doesn't go on a form.

## Documents

Absolute paths the agent can read.

- **Resume (one page, approved):** `<path/to/resume.pdf>`
  Keep exactly one. If a two-page master exists anywhere the agent can see, an upload widget
  with no file picker will eventually grab it. The agent must verify the attached filename on
  the employer's own form.
- **Transcript:** `<path/to/transcript.pdf>`
- **Cover letter:** none. Skip when optional.

## System

- **Ledger sheet:** `<https://docs.google.com/spreadsheets/d/YOUR_ID/edit>` — tab `Sheet1`
- **Job source:** `<https://jobright.ai/agent>`
- **Application email inbox:** `<https://outlook.live.com/mail/0/>`
- **Applications target per run:** `<50>`
- **Submission mode:** `<submit automatically / prepare and stop for my review>`
  See the consent boundary section in README.md before choosing.
