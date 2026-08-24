# Apply harness — Copilot + session, not a folder id

**Audience:** Junyi + any Cloud Agent about to open ATS tabs.
**Last updated:** 2026-08-24

This is the contract for **autofill review** (open forms, fill identity, stop
before Submit). Daily discovery does **not** need this harness.

---

## Three questions (keep them separate)

| Question | What proves it | What does not |
|---|---|---|
| **Software** — is Copilot in the computer-use browser? | Extension manifest publisher signals: `short_name=Simplify Copilot`, or `author=Simplify Jobs Inc.` + `homepage_url=https://simplify.jobs/` | A pinned Chrome folder id |
| **Session** — is *someone* logged into Simplify? | `refresh` cookie on `*.simplify.jobs` in that profile | Copilot being installed; Playwright `secrets/simplify_storage.json` (export-only) |
| **Identity** — is it Junyi? | Dashboard name/email vs `config/profile.yaml` (human confirm) | The extension folder id (that is the *package*, not the person) |

`ready` is **software + session** in the profile computer-use will attach to.
`identity_match` is reported as `unknown` unless a later check can compare
account email without decrypting cookies. Do not treat a folder id as you.

Chrome Web Store and unpacked `--load-extension` installs get **different**
ids from the same product. Store ids are a hash of the publisher key and stay
stable for that listing; unpacked ids follow the load path. The checker must
not require either id.

---

## Why Copilot “vanishes” on a new Cloud Agent

The July 31 trial only had autofill because **that** VM had a local harness
(unpacked extension + injected cookies). Cloud Agent disks do not carry over.
A later agent starts clean unless this **personal** environment was snapshotted
after a human Store install + Simplify login.

Computer-use on this repo today attaches to **Google Chrome**
(`/opt/google/chrome/chrome`, profile `~/.config/google-chrome`). Install
Copilot from the Store in **that** browser. Branded Chrome ignores
`--load-extension`; a Store install is the path that works here.

---

## Human once — Take Control on a throwaway agent

1. Run `python3 scripts/automation/check_apply_harness.py`.
2. Take Control of the computer-use browser. Open `chrome://extensions` and
   the Chrome Web Store listing for **Simplify Copilot**.
3. Install Copilot. Log into **your** Simplify. Complete captcha / 2FA
   yourself. Do not paste the password into chat.
4. Confirm the dashboard shows your name. Do **not** click Submit on any ATS.
5. Re-run the checker. `ready: true` means software + session. Confirm
   identity yourself against `config/profile.yaml`.
6. Snapshot this **personal** environment so later agents boot with the
   profile already on disk. A snapshot with Simplify cookies is a **login**.
   Do not share that environment with friends. Friends need their own
   snapshot and their own Simplify login — `docs/collaborators/SETUP.md`.

---

## Every later autofill run

```bash
python3 scripts/automation/check_apply_harness.py
python3 scripts/automation/check_apply_harness.py --json
```

- Exit 0 → open ATS tabs, autofill, stop before Submit.
- Exit 1 → **stop**. Report the missing piece (Copilot vs session vs wrong
  browser profile). Do not pretend Greenhouse’s MyGreenhouse button is
  Simplify. Do not type identity fields by hand to “fake” autofill.

Proven 2026-08-22: a normal new agent (no pinned build) default-booted
`ready: true` after Junyi Saved the personal environment. Live 10-tab
quality notes: `docs/experiments/2026-08-22_ten_tab_copilot_review.md`.
If Copilot fills EEO or marks US-citizen / “no sponsorship” on an F-1
profile, do not Submit — see `docs/automation/WEEKDAY_APPLY_AUTOMATION.md`.

**Two memories:** Simplify Copilot (the Chrome extension) does not read
this repo. A value in `config/profile.yaml` (for example Emory GPA 3.925)
can stay unused on the form. See `docs/apply/OBSTACLES.md`. Do not call
Cursor “Copilot” in apply notes.

---

## Leftover typing is one paste

Junyi 2026-08-24 after Charta. If a draft is already accepted and the
ask is “type it, I will Submit”:

1. One computer-use call.
2. Find the tab. Click the box. Select all. **Paste** once.
3. One screenshot. Stop.

Do not type the essay key by key. Do not resume the clicker to Ctrl+F,
scroll the textarea, or fix a blank line. Do not start a second or
third computer-use “verify” pass. Do not start a screen recording
unless he asked for a demo. He can see the tab.

Canonical: `knowledge/form_strategy.yaml` `leftover_typing_one_pass`.
Parent must copy `docs/automation/COMPUTER_USE_PROMPT.md`. Do not invent
a verify-heavy Task prompt. You cannot edit the Computer Use built-in
system prompt. You can only send a short fire-and-forget user prompt.

---

## What agents must never do

- Commit `simplify_storage.json`, cookies, or an unpacked Copilot tree.
- Ask the user to paste a Simplify password into chat.
- Print cookie or token values.
- Use `/tmp/apply_trial` as the durable location (it dies with the VM).
- Treat a Chrome extension folder id as proof of who is logged in.
- Click Submit, fill EEO, or log into MyGreenhouse to “make autofill work.”
