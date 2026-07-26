#!/usr/bin/env python3
"""Export Jobright discovery cards → data/discovery/YYYY-MM-DD_jobright.csv

Exp B: discovery only. No apply / no submit.

Strategy:
1) Reuse secrets/jobright_storage.json if present (personalized matches)
2) Else scrape public homepage feed
3) Keyword-filter toward new-grad / SWE / ML / data / cloud (configurable)
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "secrets"
ENV_PATH = SECRETS / ".env"
STATE = SECRETS / "jobright_storage.json"
OUT_DIR = ROOT / "data" / "discovery"

DEFAULT_KEEP = re.compile(
    r"(software|swe|engineer|developer|data|machine\s*learning|ml\b|ai\b|cloud|"
    r"platform|backend|frontend|full[\s-]?stack|infra|security|research|"
    r"new\s*grad|university|graduate|intern|entry[\s-]?level)",
    re.I,
)
DEFAULT_DROP = re.compile(
    r"(sales|marketing|account\s*executive|recruiter|hr\b|human\s*resources|"
    r"customer\s*success|cashier|nurse|driver|warehouse)",
    re.I,
)


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


def parse_card_text(text: str) -> tuple[str, str]:
    """Parse homepage or recommend-card text → company, role."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    if not lines:
        return "", ""

    # Recommend feed: ...\nRole\nCompany\n/\nSoftware · ...
    if "/" in lines:
        idx = lines.index("/")
        company = lines[idx - 1] if idx >= 1 else ""
        role = lines[idx - 2] if idx >= 2 else ""
        return company, role

    # Score-only side cards
    if any(k in (text or "") for k in ("GOOD MATCH", "STRONG MATCH")) and "Why This Job" not in (text or ""):
        return "", ""

    # Homepage feed: 'Company · just now\nRole Title'
    head = lines[0]
    company = re.split(r"\s*[·•|]\s*", head)[0].strip()
    role = lines[1] if len(lines) > 1 else ""
    if re.search(r"\bago\b", company, re.I) and len(lines) >= 3:
        role = lines[1]
        company = lines[2]
    return company, role


def scrape_job_cards(page) -> list[dict]:
    by_url: dict[str, dict] = {}
    for a in page.query_selector_all("a[href*='/jobs/info/']"):
        href = a.get_attribute("href") or ""
        if not href:
            continue
        if href.startswith("/"):
            href = "https://jobright.ai" + href
        parsed = urlparse(href)
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        text = (a.inner_text() or "").strip()
        company, role = parse_card_text(text)
        if not company or not role:
            continue
        prev = by_url.get(url)
        if prev and prev.get("company") and re.search(r"\bago\b", company, re.I):
            continue
        by_url[url] = {
            "company": company,
            "role": role,
            "url": url,
            "source": "jobright_matches",
            "track": "",
            "date_discovered": date.today().isoformat(),
            "fetched_at": "",  # filled in main()
            "notes": "jobright_matches_scrape",
        }
    return list(by_url.values())


def filter_rows(rows: list[dict]) -> list[dict]:
    keep = DEFAULT_KEEP
    drop = DEFAULT_DROP
    out = []
    for r in rows:
        blob = f"{r.get('company','')} {r.get('role','')}"
        if drop.search(blob) and not keep.search(blob):
            continue
        if not keep.search(blob):
            continue
        out.append(r)
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "company",
        "role",
        "url",
        "source",
        "track",
        "date_discovered",
        "fetched_at",
        "notes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> int:
    load_env()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install: pip install -r requirements-automation.txt", file=sys.stderr)
        return 1

    fetched_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    default_start = (
        "https://jobright.ai/jobs/recommend"
        if STATE.exists()
        else "https://jobright.ai/"
    )
    start = os.environ.get("JOBRIGHT_URL", default_start)
    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() in {"1", "true", "yes"}
    out_path = OUT_DIR / f"{date.today().isoformat()}_jobright.csv"
    print(f"fetched_at={fetched_at}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        if STATE.exists():
            context = browser.new_context(storage_state=str(STATE))
            print(f"Using session {STATE}")
        else:
            context = browser.new_context()
            print("No jobright_storage.json — public feed only")
        page = context.new_page()

        urls = [start]
        if STATE.exists():
            for u in [
                "https://jobright.ai/jobs/recommend",
                "https://jobright.ai/jobs",
            ]:
                if u not in urls:
                    urls.append(u)

        all_rows: list[dict] = []
        for url in urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(4000)
                for _ in range(8):
                    page.mouse.wheel(0, 3200)
                    page.wait_for_timeout(700)
                chunk = scrape_job_cards(page)
                print(f"{url} → {page.url}: {len(chunk)} cards")
                all_rows.extend(chunk)
            except Exception as e:
                print(f"skip {url}: {type(e).__name__}: {e}")

        # dedupe by url
        by_url: dict[str, dict] = {}
        for r in all_rows:
            by_url[r["url"]] = r
        rows = filter_rows(list(by_url.values()))
        for r in rows:
            r["fetched_at"] = fetched_at
        if not rows:
            shot = OUT_DIR / f"{date.today().isoformat()}_jobright_debug.png"
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(shot), full_page=True)
            print(f"0 filtered rows. Screenshot → {shot}", file=sys.stderr)
            browser.close()
            return 3

        write_csv(rows, out_path)
        print(f"Wrote {len(rows)} filtered rows → {out_path}")
        try:
            if STATE.exists():
                context.storage_state(path=str(STATE))
        except Exception:
            pass
        browser.close()

    print("Next: review CSV, then paste keepers into jobs/inbox/ or label_job.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
