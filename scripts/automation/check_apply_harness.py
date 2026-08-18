#!/usr/bin/env python3
"""Report whether this machine can run Simplify autofill the way the July 31 trial did.

Exit 0 only when the computer-use browser is not branded Chrome-without-extensions
AND Simplify Copilot is installed in the profile that computer-use will attach to.

Session cookies are reported but do not fail the check — a logged-out Copilot
is still a real harness; a missing extension is not.

Usage:
  python3 scripts/automation/check_apply_harness.py
  python3 scripts/automation/check_apply_harness.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SIMPLIFY_EXTENSION_ID = "cdcddpbdpgfipkmobdipjfheopledajg"
BRANDED_CHROME = Path("/opt/google/chrome/chrome")
DEFAULT_CHROME_PROFILE = Path.home() / ".config" / "google-chrome"
DEFAULT_CHROMIUM_PROFILE = Path.home() / ".config" / "chromium"
HARNESS_PROFILE = Path.home() / ".config" / "simplify-harness"
PLAYWRIGHT_GLOB = Path.home() / ".cache" / "ms-playwright"


def _first_playwright_chromium() -> Path | None:
    if not PLAYWRIGHT_GLOB.exists():
        return None
    matches = sorted(PLAYWRIGHT_GLOB.glob("chromium-*/chrome-linux64/chrome"))
    return matches[-1] if matches else None


def _extension_installed(profile: Path, ext_id: str) -> bool:
    ext_dir = profile / "Default" / "Extensions" / ext_id
    if ext_dir.is_dir():
        return True
    # Some profiles store unpacked extensions under Extensions/<id>/<version>
    alt = profile / "Extensions" / ext_id
    return alt.is_dir()


def _list_extension_ids(profile: Path) -> list[str]:
    ids: list[str] = []
    for base in (profile / "Default" / "Extensions", profile / "Extensions"):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and not child.name.startswith("Temp"):
                ids.append(child.name)
    return ids


def inspect(home: Path | None = None) -> dict[str, Any]:
    home = home or Path.home()
    chrome_profile = home / ".config" / "google-chrome"
    chromium_profile = home / ".config" / "chromium"
    harness_profile = home / ".config" / "simplify-harness"
    playwright = None
    cache = home / ".cache" / "ms-playwright"
    if cache.exists():
        matches = sorted(cache.glob("chromium-*/chrome-linux64/chrome"))
        playwright = str(matches[-1]) if matches else None

    branded = Path("/opt/google/chrome/chrome").exists()
    chrome_exts = _list_extension_ids(chrome_profile)
    simplify_in_chrome = _extension_installed(chrome_profile, SIMPLIFY_EXTENSION_ID)
    simplify_in_chromium = _extension_installed(chromium_profile, SIMPLIFY_EXTENSION_ID)
    simplify_in_harness = _extension_installed(harness_profile, SIMPLIFY_EXTENSION_ID)

    session_paths = [
        ROOT / "secrets" / "simplify_storage.json",
        Path("/tmp/apply_trial/simplify_storage.json"),
    ]
    session = next((str(p) for p in session_paths if p.exists()), None)
    legacy_tmp = Path("/tmp/apply_trial").is_dir()

    computer_use_browser = os.environ.get("CHROME_EXECUTABLE_PATH") or (
        "/opt/google/chrome/chrome" if branded else playwright
    )
    using_branded = computer_use_browser == "/opt/google/chrome/chrome" or (
        computer_use_browser or ""
    ).endswith("/opt/google/chrome/chrome")

    simplify_visible_to_computer_use = False
    if using_branded:
        simplify_visible_to_computer_use = simplify_in_chrome
    else:
        simplify_visible_to_computer_use = (
            simplify_in_harness or simplify_in_chromium or simplify_in_chrome
        )

    ready = bool(simplify_visible_to_computer_use) and not (
        using_branded and not simplify_in_chrome
    )
    # Branded Chrome without the Store-installed extension cannot load unpacked
    # Copilot via --load-extension (Chrome ignores the flag).
    if using_branded and not simplify_in_chrome:
        ready = False

    blockers: list[str] = []
    if using_branded and not simplify_in_chrome:
        blockers.append(
            "computer-use is branded Google Chrome and Simplify Copilot is not "
            "in ~/.config/google-chrome; Chrome also ignores --load-extension"
        )
    if not simplify_visible_to_computer_use:
        blockers.append(
            f"Simplify extension {SIMPLIFY_EXTENSION_ID} not found in the "
            "computer-use profile"
        )
    if playwright is None and not branded:
        blockers.append("Playwright Chromium is not installed")
    if legacy_tmp:
        blockers.append(
            "/tmp/apply_trial exists on this VM only — it will not survive the next agent"
        )

    return {
        "ready": ready,
        "simplify_extension_id": SIMPLIFY_EXTENSION_ID,
        "branded_chrome_present": branded,
        "playwright_chromium": playwright,
        "computer_use_browser": computer_use_browser,
        "using_branded_chrome": using_branded,
        "profiles": {
            "google-chrome": {
                "path": str(chrome_profile),
                "exists": chrome_profile.is_dir(),
                "extension_ids": chrome_exts,
                "simplify_installed": simplify_in_chrome,
            },
            "chromium": {
                "path": str(chromium_profile),
                "exists": chromium_profile.is_dir(),
                "simplify_installed": simplify_in_chromium,
            },
            "simplify-harness": {
                "path": str(harness_profile),
                "exists": harness_profile.is_dir(),
                "simplify_installed": simplify_in_harness,
            },
        },
        "session_storage_state": session,
        "legacy_tmp_harness": legacy_tmp,
        "blockers": blockers,
        "next_step": (
            "Harness ready. Open ATS tabs, autofill, do not Submit."
            if ready
            else "See docs/automation/APPLY_HARNESS.md — Take Control on Chromium, "
            "install Copilot, log into Simplify, then snapshot this personal environment."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = inspect()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("Apply harness check")
        print(f"  ready: {report['ready']}")
        print(f"  computer-use browser: {report['computer_use_browser']}")
        print(f"  branded Chrome: {report['using_branded_chrome']}")
        print(f"  playwright chromium: {report['playwright_chromium']}")
        chrome = report["profiles"]["google-chrome"]
        print(
            f"  chrome profile extensions: {chrome['extension_ids'] or '(none)'}"
        )
        print(f"  simplify in chrome profile: {chrome['simplify_installed']}")
        print(f"  session storage_state: {report['session_storage_state'] or '(none)'}")
        if report["blockers"]:
            print("  blockers:")
            for b in report["blockers"]:
                print(f"    - {b}")
        print(f"  next: {report['next_step']}")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
