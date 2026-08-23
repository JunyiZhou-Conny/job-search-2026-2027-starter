# Experiment: harness snapshot + clone (2026-08-21)

Facts only. No applications submitted.

## What this tested

Whether a disk snapshot of a Cloud Agent VM that already has
**Simplify Copilot** and a **Simplify session cookie** can be turned
into an environment build, and whether a **new** VM booted from that
build still has Copilot and the session — without a second install.

## What succeeded

1. This VM (`ten-tab-autofill-review`) received Copilot + Simplify
   login via Take Control (the parent URL still pointed here).
2. `scripts/automation/check_apply_harness.py` from
   `origin/cursor/apply-harness-checker-073b` reported **`ready: true`**
   on this disk:
   - Copilot: Chrome extension `pbanhockgagggenencehbnadejlgchfc`
     (Simplify Copilot 3.0.11)
   - Session: `simplify.jobs` refresh cookie in
     `~/.config/google-chrome/Default/Cookies`
   - Computer-use browser: branded Chrome `/opt/google/chrome/chrome`
3. Snapshot:
   `snapshot-20260821-8f23abf1-d6b7-452d-88ae-778465f9a248`
4. Draft environment build:
   `bld-20260821-34982884-1cea-42cd-a0bb-156061700642`
5. A separate Cloud Agent booted **that** build id and ran the same
   checker. Result: **`ready: true` again**. Same Copilot id. Session
   cookie present. No reinstall.

The 2026-08-19 `PauseContainer` failure was infrastructure. Cookies
and the extension **did** copy on this try.

Junyi Saved the proposal in the Environment panel. Environment:
https://cursor.com/dashboard/cloud-agents/environments/e/41a15b57-8916-11f1-b532-320a589b8025

## Default boot after Save (2026-08-22)

A new Cloud Agent started from `main` with **no** build-id override.
Checker source: `origin/cursor/apply-harness-checker-073b`.

- **`ready: true`**
- Booted [`bld-20260822-be4df1ce-5add-4587-abeb-e4e06c3c9405`](https://cursor.com/dashboard/cloud-agents/builds/bld-20260822-be4df1ce-5add-4587-abeb-e4e06c3c9405)
  (`SYSTEM` / `CONFIG_CHANGE`, environment version `744792`)
- Computer-use: branded Chrome `/opt/google/chrome/chrome`
- Copilot: `pbanhockgagggenencehbnadejlgchfc`
- Session cookie present
- No reinstall, Take Control, or ATS tabs

Save made a new default image. That image still has Copilot and the
session. Ordinary later agents and apply Automations can use this
harness if they boot this environment.

## What this does *not* prove

- Dashboard name is Junyi (`identity_match` stayed `unknown` because
  the probe checkout had no `config/profile.yaml`; glance the
  Simplify dashboard once).
- Autofill quality on real ATS tabs (plan step 2).
- Unattended Submit. Policy remains: stop before Submit unless Junyi
  explicitly changes it.

Daily **discovery** Automations do not need this harness.
