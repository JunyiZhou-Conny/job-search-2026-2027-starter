# Apply harness — Copilot + session, not a folder id

**Audience:** Junyi + any Cloud Agent about to open ATS tabs.
**Last updated:** 2026-08-18

This is the contract for **autofill review** (open forms, fill identity, stop
before Submit). Daily discovery does **not** need this harness.

---

## Three questions (keep them separate)

| Question | What proves it | What does not |
|---|---|---|
| **Software** — is Copilot in the computer-use browser? | Extension manifest publisher signals: `short_name=Simplify Copilot`, or `author=Simplify Jobs Inc.` + `homepage_url=https://simplify.jobs/` | A pinned Chrome folder id |
| **Session** — is *someone* logged into Simplify? | `refresh` cookie on `*.simplify.jobs` in that profile, or gitignored `secrets/simplify_storage.json` | Copilot being installed |
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

---

## What agents must never do

- Commit `simplify_storage.json`, cookies, or an unpacked Copilot tree.
- Ask the user to paste a Simplify password into chat.
- Print cookie or token values.
- Use `/tmp/apply_trial` as the durable location (it dies with the VM).
- Treat a Chrome extension folder id as proof of who is logged in.
- Click Submit, fill EEO, or log into MyGreenhouse to “make autofill work.”
