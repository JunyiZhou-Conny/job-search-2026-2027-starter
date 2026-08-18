# Apply harness — why Simplify vanishes, and how later Cloud Agents keep it

**Audience:** Junyi + any Cloud Agent about to open ATS tabs.  
**Last updated:** 2026-08-18

This is the contract for **autofill review** (open forms, fill identity, stop
before Submit). Daily discovery does **not** need this harness.

---

## What we just witnessed (2026-08-18)

Opening 10 real ATS tabs on a new Cloud Agent showed the real failure mode:

| Layer | What happened | Why |
|---|---|---|
| Discovery → employer URL | Worked | `resolve_apply_url.py` |
| Form visible | Worked | Ashby `/application`, Greenhouse Apply |
| Simplify Copilot on the page | **Missing** | New VM, branded Chrome, no snapshot of the July 31 harness |
| Greenhouse “Autofill my application” | Wrong product | MyGreenhouse login, not Simplify |
| Identity fields filled | Did not happen | No Copilot + no Simplify session |

The July 31 trial only had autofill because **that** VM had a local harness
under `/tmp/apply_trial/` (unpacked extension + injected cookies). That directory
is not in git, and Cloud Agent disks do not carry over. A later agent starts
clean. That is expected, not a regression in the ATS pages.

---

## What “the harness” actually is

Three pieces. Missing any one of them looks like “Simplify is gone.”

| Piece | Must live where | Must not live where |
|---|---|---|
| **Chromium** that still honors `--load-extension` | Environment snapshot / `install` | Branded `/opt/google/chrome/chrome` (it silently ignores the flag) |
| **Simplify Copilot** installed in **that** browser’s profile | Same snapshot (or a gitignored unpacked dir you load once) | The repo, a friends’ shared environment |
| **Logged-in Simplify session** | Personal snapshot **or** `secrets/simplify_storage.json` / Cursor secret | Git, chat, PRs, collaborator forks |

Computer-use on this repo today attaches to **Google Chrome**. Even if Playwright
Chromium has the extension, the 10-tab window will not see it unless
`chromeExecutablePath` (and the profile) point at the harness browser.

---

## Recommended setup (personal environment only)

Do this **once**, then every *new* Cloud Agent that boots from that environment
build/snapshot already has the harness. This running agent will not gain it
after the fact.

### 1. Bake tools (safe to share, no login)

In the Cloud Agent environment
([environment dashboard](https://cursor.com/dashboard/cloud-agents/environments/e/41a15b57-8916-11f1-b532-320a589b8025)):

- `install` (idempotent):

```bash
python3 -m pip install -r requirements-automation.txt
python3 -m playwright install chromium
```

- Set **computer-use Chrome path** to Playwright’s Chromium, not Google Chrome.
  After install it is typically:

```text
/home/ubuntu/.cache/ms-playwright/chromium-*/chrome-linux64/chrome
```

  Confirm with `python3 scripts/automation/check_apply_harness.py`.
  Cursor field: `chromeExecutablePath` in the environment (dashboard or
  `.cursor/environment.json`).

Do **not** commit Simplify’s `.crx` or a logged-in profile.

### 2. Human once — Take Control on a throwaway agent

On Chromium (the path above), not Google Chrome:

1. Open `chrome://extensions` and confirm you are not on branded Chrome.
2. Install **Simplify Copilot** from the Chrome Web Store (or load the unpacked
   extension if Chromium will not talk to the Store).
3. Log into **your** Simplify. Complete captcha / 2FA yourself. Do not paste
   the password into chat.
4. Open one ATS page and confirm the Copilot panel exists (Ashby: “Start
   Application”; Greenhouse: “Autofill This Page”).
5. Do **not** click Submit.

### 3. Snapshot that machine

After step 2 succeeds, snapshot the environment so the next agent boots with
Chromium + Copilot + session already on disk.

- Personal environment only. A snapshot with your Simplify cookies is a
  **login**. Do not share that environment with friends or a Cursor Team
  follow-up setting.
- Friends need their **own** snapshot and their **own** Simplify login.
  See `docs/collaborators/SETUP.md`.

### 4. Every later autofill run

The agent must:

```bash
python3 scripts/automation/check_apply_harness.py
```

- Exit 0 → open ATS tabs, autofill, stop before Submit.
- Exit 1 → **stop**. Report the missing piece. Do not pretend Greenhouse’s
  MyGreenhouse button is Simplify. Do not type identity fields by hand to
  “fake” autofill.

---

## If you do not want the session inside the snapshot

Keep step 1 (Chromium + Copilot installed, logged out). Store the session as
a Cursor **runtime secret** or local `secrets/simplify_storage.json` (already
gitignored). Refresh it with:

```bash
python3 scripts/automation/save_simplify_session.py
```

(That script currently launches branded Chrome; after the harness exists,
point it at the same Chromium + profile as computer-use.)

Sessions expire. Captcha comes back if you log in from a new profile. That is
why a personal snapshot of an already-logged-in profile is less painful for
*your* later agents — and why it must stay personal.

---

## What agents must never do

- Commit `simplify_storage.json`, cookies, or an unpacked Copilot tree.
- Ask the user to paste a Simplify password into chat.
- Use `/tmp/apply_trial` as the durable location (it dies with the VM).
- Open 10-tab autofill on branded Chrome and call a missing panel a surprise.
- Click Submit, fill EEO, or log into MyGreenhouse to “make autofill work.”

---

## Check command

```bash
python3 scripts/automation/check_apply_harness.py
python3 scripts/automation/check_apply_harness.py --json
```

Ready means: Chromium (or a browser that can load extensions) + Simplify
extension id `cdcddpbdpgfipkmobdipjfheopledajg` in the computer-use profile.
Session is reported separately (present / missing / unknown).
