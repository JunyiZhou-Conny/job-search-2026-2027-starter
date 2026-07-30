#!/usr/bin/env python3
"""Probe which Jobright minisite category slugs actually return job tables.

The minisites are a single-page app: every path returns HTTP 200, including
nonsense ones, so status codes cannot tell you whether a category exists.
This renders each candidate and counts real table rows instead.

    .venv/bin/python scripts/automation/probe_board_categories.py
    .venv/bin/python scripts/automation/probe_board_categories.py --track intern

Read-only. Writes nothing; prints a table so you can decide what to add to
DEFAULT_BOARDS in export_board_lists.py.
"""

from __future__ import annotations

import argparse
import sys

# The site's ?k= param is NOT the minisite slug. Confirmed mappings, read off
# the iframe src that intern-list.com builds for each category:
#   ?k=swe  -> swe            ?k=aiml -> ml_ai
#   ?k=hc   -> healthcare     ?k=da   -> data_analysis
#   ?k=pm   -> product_management
# Entries below marked "guess" are unconfirmed slug spellings; the row count
# tells you whether they resolve.
CANDIDATES = [
    ("swe", "Software Engineering (confirmed)"),
    ("ml_ai", "Machine Learning and AI (confirmed)"),
    ("data_analysis", "Data Analysis (confirmed)"),
    ("healthcare", "Healthcare (confirmed)"),
    ("product_management", "Product Management (confirmed)"),
    ("cybersecurity", "Cybersecurity (guess)"),
    ("engineering", "Engineering and Development (guess)"),
    ("data_science", "Data Science (guess)"),
    ("information_technology", "IT (guess)"),
    ("zzzznotreal", "CONTROL — must be 0"),
]

URL = "https://jobright.ai/minisites-jobs/{track}/us/{slug}?embed=true"


def probe(page, track: str, slug: str) -> tuple[int, int]:
    """Return (row_count, job_link_count) for one category page."""
    page.goto(URL.format(track=track, slug=slug), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    for _ in range(3):
        page.mouse.wheel(0, 2800)
        page.wait_for_timeout(400)
    rows = [
        tr
        for tr in page.query_selector_all("tr")
        if len(tr.query_selector_all("td")) >= 7
    ]
    links = page.query_selector_all("a[href*='/jobs/info/']")
    return len(rows), len(links)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=["intern", "newgrad", "both"], default="both")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install: pip install -r requirements-automation.txt", file=sys.stderr)
        return 1

    tracks = ["intern", "newgrad"] if args.track == "both" else [args.track]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        page = browser.new_page()
        for track in tracks:
            print(f"\n=== {track} ===")
            print(f"  {'slug':<14} {'rows':>5} {'links':>6}   label")
            for slug, label in CANDIDATES:
                try:
                    rows, links = probe(page, track, slug)
                except Exception as e:
                    print(f"  {slug:<14} {'ERR':>5} {'':>6}   {type(e).__name__}: {e}")
                    continue
                print(f"  {slug:<14} {rows:>5} {links:>6}   {label}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
