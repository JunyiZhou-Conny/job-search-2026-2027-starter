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

## What is still Junyi’s click

`propose-environment-json` was sent with that `buildId`. **Save** in
the Cloud Agents environment dashboard is required before ordinary
new agents and Automations boot this image by default.

Until Save, default boot can still be the earlier empty Chrome image
(`bld-20260819-88dc0b61-ac73-482f-88db-1e40295d0834`).

Environment:
https://cursor.com/dashboard/cloud-agents/environments/e/41a15b57-8916-11f1-b532-320a589b8025

## What this does *not* prove

- Dashboard name is Junyi (`identity_match` stayed `unknown` on the
  clone because that checkout had no `config/profile.yaml`; glance the
  Simplify dashboard once).
- Default boot *without* pinning the draft build id (needs Save first).
- Autofill quality on real ATS tabs.
- Unattended Submit. Policy remains: stop before Submit unless Junyi
  explicitly changes it.

## After Save

Start one **normal** new agent (no build-id override). Run the 073b
checker. `ready: true` means later weekday apply Automations can use
this harness. `ready: false` means default boot is still the empty
image.

Daily **discovery** Automations do not need this harness.
