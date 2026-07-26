#!/usr/bin/env python3
"""Open Chrome, let YOU log into Simplify once, save storage state for later scripts.

Usage:
  python3 scripts/automation/save_simplify_session.py

Then daily export can reuse secrets/simplify_storage.json without typing password in chat.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "secrets"
STATE = SECRETS / "simplify_storage.json"
LOGIN_MARKERS = ("/auth/login", "/login")
MAX_WAIT_SEC = 10 * 60  # 10 minutes


def _looks_logged_in(url: str) -> bool:
    u = (url or "").lower()
    if not u.startswith("http"):
        return False
    if "simplify.jobs" not in u:
        return False
    return not any(m in u for m in LOGIN_MARKERS)


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Install first:\n  pip install -r requirements-automation.txt\n  playwright install chromium",
            file=sys.stderr,
        )
        return 1

    SECRETS.mkdir(parents=True, exist_ok=True)
    print("Chrome will open.")
    print("1) Log into Simplify (email/password; complete 2FA if any)")
    print("2) Open Job Tracker / Applied so you can see your applications")
    print("3) Stay on that page — this script auto-saves when it detects login")
    print(f"   (timeout {MAX_WAIT_SEC // 60} min)\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://simplify.jobs/auth/login", wait_until="domcontentloaded")

        deadline = time.time() + MAX_WAIT_SEC
        last_url = ""
        while time.time() < deadline:
            try:
                url = page.url
            except Exception:
                print("Browser closed before session was saved.", file=sys.stderr)
                return 2
            if url != last_url:
                print(f"  current URL: {url}")
                last_url = url
            if _looks_logged_in(url):
                # Give the app a moment to finish setting cookies
                page.wait_for_timeout(1500)
                context.storage_state(path=str(STATE))
                final_url = page.url
                browser.close()
                print(f"\nSaved session → {STATE}")
                print(f"Logged-in URL → {final_url}")
                print("Paste that URL into secrets/.env as SIMPLIFY_TRACKER_URL if it is your tracker.")
                print("Next: python3 scripts/automation/export_simplify_tracker.py")
                return 0
            page.wait_for_timeout(2000)

        try:
            browser.close()
        except Exception:
            pass
        print("Timed out waiting for login. Re-run and finish login in the Chrome window.", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
