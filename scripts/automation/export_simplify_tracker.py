#!/usr/bin/env python3
"""Export Simplify tracker rows to data/imports/simplify/YYYY-MM-DD.csv

Strategy (in order):
1) Reuse secrets/simplify_storage.json session if present
2) Else email/password from secrets/.env (fragile if 2FA)
3) Prefer clicking an Export/CSV control if found
4) Else scrape visible table/cards into CSV

This is an experiment probe — UI changes will break selectors; we log failures.
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "secrets"
ENV_PATH = SECRETS / ".env"
STATE = SECRETS / "simplify_storage.json"
OUT_DIR = ROOT / "data" / "imports" / "simplify"


def load_env() -> None:
    if not ENV_PATH.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_PATH)
    except ImportError:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def write_csv(rows: list[dict], path: Path) -> None:
    fields = ["Company", "Title", "URL", "Status", "Date Applied", "Location", "Notes"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def scrape_rows(page) -> list[dict]:
    """Best-effort scrape; Simplify DOM varies — capture what we can."""
    rows: list[dict] = []

    # Try HTML tables first
    tables = page.query_selector_all("table")
    for table in tables:
        trs = table.query_selector_all("tr")
        if len(trs) < 2:
            continue
        headers = [c.inner_text().strip().lower() for c in trs[0].query_selector_all("th,td")]
        for tr in trs[1:]:
            cells = [c.inner_text().strip() for c in tr.query_selector_all("td")]
            if not cells:
                continue
            data = {headers[i] if i < len(headers) else f"c{i}": cells[i] for i in range(len(cells))}
            link = tr.query_selector("a[href]")
            url = link.get_attribute("href") if link else ""
            rows.append({
                "Company": data.get("company") or data.get("employer") or cells[0],
                "Title": data.get("title") or data.get("role") or data.get("job") or (cells[1] if len(cells) > 1 else ""),
                "URL": url or "",
                "Status": data.get("status") or data.get("stage") or "",
                "Date Applied": data.get("date applied") or data.get("applied") or "",
                "Location": data.get("location") or "",
                "Notes": "",
            })
        if rows:
            return rows

    # Fallback: collect anchors that look like job links
    for a in page.query_selector_all("a[href]"):
        href = a.get_attribute("href") or ""
        text = (a.inner_text() or "").strip()
        if not text or len(text) < 3:
            continue
        if not re.search(r"job|greenhouse|lever|ashby|workday|boards", href, re.I):
            continue
        rows.append({
            "Company": "",
            "Title": text.split("\n")[0][:200],
            "URL": href,
            "Status": "applied",
            "Date Applied": "",
            "Location": "",
            "Notes": "scraped_link_fallback",
        })
    return rows


def dismiss_overlays(page) -> None:
    """Cookie banners (and similar) block Playwright clicks on Simplify."""
    for sel in [
        "button:has-text('Accept all')",
        "button:has-text('Accept')",
        "button:has-text('Allow all')",
        "button:has-text('Allow')",
        "button:has-text('Got it')",
        "[data-testid='cookie-banner-root'] button",
    ]:
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        try:
            loc.first.click(timeout=2000)
            page.wait_for_timeout(300)
            return
        except Exception:
            pass
    try:
        page.evaluate(
            """() => {
              const el = document.querySelector('[data-testid="cookie-banner-root"]');
              if (el) el.remove();
            }"""
        )
    except Exception:
        pass


def password_login(page, email: str, password: str) -> None:
    dismiss_overlays(page)
    for sel in ["input[type='email']", "input[name='email']", "#email"]:
        if page.locator(sel).count():
            page.fill(sel, email)
            break
    page.fill("input[type='password']", password)
    dismiss_overlays(page)
    submitted = False
    for sel in ["button[type='submit']", "button:has-text('Sign in')", "button:has-text('Log in')"]:
        if page.locator(sel).count():
            try:
                page.locator(sel).first.click(timeout=5000, force=True)
                submitted = True
                break
            except Exception:
                continue
    if not submitted:
        page.press("input[type='password']", "Enter")
    page.wait_for_timeout(5000)


def try_click_export(page) -> Path | None:
    """If an export button triggers a download, save it."""
    candidates = [
        "text=Export",
        "text=Export CSV",
        "text=Download CSV",
        "text=Download",
        "[aria-label*=Export i]",
        "button:has-text('CSV')",
    ]
    for sel in candidates:
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        try:
            with page.expect_download(timeout=8000) as di:
                loc.first.click()
            download = di.value
            out = OUT_DIR / f"{date.today().isoformat()}_simplify_download.csv"
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            download.save_as(str(out))
            return out
        except Exception:
            continue
    return None


def main() -> int:
    load_env()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install:\n  pip install -r requirements-automation.txt\n  playwright install chromium", file=sys.stderr)
        return 1

    tracker = os.environ.get("SIMPLIFY_TRACKER_URL", "https://simplify.jobs/jobs/applied")
    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() in {"1", "true", "yes"}
    email = os.environ.get("SIMPLIFY_EMAIL", "")
    password = os.environ.get("SIMPLIFY_PASSWORD", "")

    out_path = OUT_DIR / f"{date.today().isoformat()}.csv"
    print(f"Tracker URL: {tracker}")
    print(f"Session file exists: {STATE.exists()}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        if STATE.exists():
            context = browser.new_context(storage_state=str(STATE), accept_downloads=True)
        else:
            context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto(tracker, wait_until="domcontentloaded", timeout=60000)
        dismiss_overlays(page)

        # If redirected to login and we have credentials
        if "login" in page.url.lower() or page.locator("input[type='password']").count() > 0:
            if not email or not password:
                print(
                    "Not logged in. Run save_simplify_session.py OR set SIMPLIFY_EMAIL/PASSWORD in secrets/.env",
                    file=sys.stderr,
                )
                browser.close()
                return 2
            print("Attempting password login…")
            if "login" not in page.url.lower():
                page.goto("https://simplify.jobs/auth/login", wait_until="domcontentloaded")
            password_login(page, email, password)
            page.goto(tracker, wait_until="domcontentloaded")
            dismiss_overlays(page)
            if "login" in page.url.lower():
                print(
                    "Password login failed (still on login page). "
                    "Prefer: python3 scripts/automation/save_simplify_session.py",
                    file=sys.stderr,
                )
                shot = OUT_DIR / f"{date.today().isoformat()}_simplify_login_failed.png"
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot), full_page=True)
                print(f"Screenshot → {shot}", file=sys.stderr)
                browser.close()
                return 2

        page.wait_for_timeout(2000)
        downloaded = try_click_export(page)
        if downloaded:
            print(f"Downloaded export → {downloaded}")
            # normalize copy to dated path
            text = downloaded.read_text(encoding="utf-8", errors="replace")
            out_path.write_text(text, encoding="utf-8")
            print(f"Copied → {out_path}")
        else:
            print("No export button download detected; scraping visible rows…")
            rows = scrape_rows(page)
            if not rows:
                # save screenshot for debugging
                shot = OUT_DIR / f"{date.today().isoformat()}_simplify_debug.png"
                OUT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot), full_page=True)
                print(f"Scraped 0 rows. Screenshot → {shot}", file=sys.stderr)
                print("Open the screenshot and tell me what you see (login wall? different layout?).", file=sys.stderr)
                browser.close()
                return 3
            write_csv(rows, out_path)
            print(f"Scraped {len(rows)} rows → {out_path}")

        # refresh storage state if logged in
        try:
            context.storage_state(path=str(STATE))
        except Exception:
            pass
        browser.close()

    print("Next:\n  python3 scripts/daily_job_search.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
