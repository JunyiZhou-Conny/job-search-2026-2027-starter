#!/usr/bin/env python3
"""Open Chrome, let YOU log into Jobright, save storage state for discovery scrapes.

Usage:
  python3 scripts/automation/save_jobright_session.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "secrets"
STATE = SECRETS / "jobright_storage.json"
LOGIN_MARKERS = ("/sign-in", "/signin", "/login", "/auth")
MAX_WAIT_SEC = 10 * 60


def _looks_logged_in(page) -> bool:
    try:
        url = (page.url or "").lower()
    except Exception:
        return False
    if "jobright.ai" not in url:
        return False
    if any(m in url for m in LOGIN_MARKERS):
        return False

    # Strong URL signals
    if any(k in url for k in ("/jobs", "/match", "/recommend", "/dashboard", "/home", "/profile", "/settings")):
        return True

    # Homepage can still be logged-in — detect nav chrome
    try:
        # Logged-out marketing nav usually has both of these
        sign_in = page.locator("text=SIGN IN").count()
        join = page.locator("text=JOIN NOW").count()
        if sign_in == 0 and join == 0:
            return True
        # Some builds use mixed case
        if page.locator("text=/sign out|log out|my profile|account/i").count() > 0:
            return True
    except Exception:
        pass
    return False


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
    print("Chrome will open on Jobright.", flush=True)
    print("1) Click SIGN IN and finish login", flush=True)
    print("2) Open Matches/Jobs if you can (homepage after login also OK)", flush=True)
    print("3) Stay there — session auto-saves", flush=True)
    print(f"   (timeout {MAX_WAIT_SEC // 60} min)\n", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://jobright.ai/", wait_until="domcontentloaded")

        deadline = time.time() + MAX_WAIT_SEC
        last_url = ""
        while time.time() < deadline:
            try:
                url = page.url
            except Exception:
                print("Browser closed before session was saved.", file=sys.stderr)
                return 2
            if url != last_url:
                print(f"  current URL: {url}", flush=True)
                last_url = url
            if _looks_logged_in(page):
                page.wait_for_timeout(1500)
                context.storage_state(path=str(STATE))
                final_url = page.url
                browser.close()
                print(f"\nSaved session → {STATE}", flush=True)
                print(f"Logged-in URL → {final_url}", flush=True)
                print("Next: python3 scripts/automation/export_jobright_discovery.py", flush=True)
                return 0
            page.wait_for_timeout(2000)

        try:
            browser.close()
        except Exception:
            pass
        print("Timed out waiting for Jobright login.", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
