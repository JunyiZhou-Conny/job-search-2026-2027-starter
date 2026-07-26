#!/usr/bin/env python3
"""Scrape Jobright minisite boards that power intern-list / newgrad-jobs.

These sites embed tables like:
  https://jobright.ai/minisites-jobs/newgrad/us/swe?embed=true
  https://jobright.ai/minisites-jobs/intern/us/swe?embed=true

Exp B: discovery only. Writes per-source CSVs under data/discovery/.
Each row includes fetched_at (ISO timestamp of this scrape run).
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse

ROOT = Path(__file__).resolve().parents[2]
SECRETS = ROOT / "secrets"
ENV_PATH = SECRETS / ".env"
OUT_DIR = ROOT / "data" / "discovery"

# Balanced default: ~50% new-grad SWE, ~50% intern SWE (profile track_balance).
DEFAULT_BOARDS = [
    {
        "source": "newgrad_jobs",
        "track": "new_grad_2027_start",
        "list_url": "https://jobright.ai/minisites-jobs/newgrad/us/swe?embed=true",
        "out_suffix": "newgrad_swe",
    },
    {
        "source": "intern_list",
        "track": "internship_if_eligible",
        "list_url": "https://jobright.ai/minisites-jobs/intern/us/swe?embed=true",
        "out_suffix": "intern_swe",
    },
]

KEEP = re.compile(
    r"(software|swe|engineer|developer|data|machine\s*learning|ml\b|ai\b|cloud|"
    r"platform|backend|frontend|full[\s-]?stack|infra|security|quant|"
    r"new\s*grad|graduate|intern|entry[\s-]?level)",
    re.I,
)
DROP = re.compile(
    r"(sales\b|marketing|account\s*executive|recruiter|\bhr\b|human\s*resources|"
    r"customer\s*success|cashier|nurse|driver|warehouse|soc\s*analyst)",
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


def canon_url(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def scrape_minisite_table(page, list_url: str, source: str, track: str, fetched_at: str) -> list[dict]:
    page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    for _ in range(6):
        page.mouse.wheel(0, 2800)
        page.wait_for_timeout(400)

    rows_out: list[dict] = []
    trs = page.query_selector_all("tr")
    for tr in trs:
        cells = [c.inner_text().strip() for c in tr.query_selector_all("td")]
        if len(cells) < 7:
            continue
        # Expected: idx, title, date, apply, work_model, location, company, ...
        role = cells[1] if len(cells) > 1 else ""
        posted_rel = cells[2] if len(cells) > 2 else ""
        work_model = cells[4] if len(cells) > 4 else ""
        location = cells[5] if len(cells) > 5 else ""
        company = cells[6] if len(cells) > 6 else ""
        h1b = ""
        is_new_grad = ""
        # newgrad tables append H1b / Is New Grad near the end
        if len(cells) >= 12:
            h1b = cells[-2]
            is_new_grad = cells[-1]

        link = tr.query_selector("a[href*='/jobs/info/']")
        href = link.get_attribute("href") if link else ""
        if not href or not company or not role:
            continue
        if href.startswith("/"):
            href = "https://jobright.ai" + href
        url = canon_url(href)

        blob = f"{company} {role}"
        if DROP.search(blob) and not KEEP.search(blob):
            continue
        if not KEEP.search(blob):
            continue

        rows_out.append(
            {
                "company": company,
                "role": role,
                "url": url,
                "source": source,
                "track": track,
                "date_discovered": fetched_at[:10],
                "fetched_at": fetched_at,
                "posted_relative": posted_rel,
                "location": location,
                "work_model": work_model,
                "h1b_signal": h1b,
                "is_new_grad_signal": is_new_grad,
                "list_url": list_url.split("?")[0],
                "notes": f"minisite_scrape;posted={posted_rel}",
            }
        )
    return rows_out


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "company",
        "role",
        "url",
        "source",
        "track",
        "date_discovered",
        "fetched_at",
        "posted_relative",
        "location",
        "work_model",
        "h1b_signal",
        "is_new_grad_signal",
        "list_url",
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

    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() in {"1", "true", "yes"}
    fetched_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    day = fetched_at[:10]

    print(f"fetched_at={fetched_at}")
    print(f"boards={len(DEFAULT_BOARDS)} (balanced intern/newgrad)")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        page = browser.new_page()
        totals = []
        for board in DEFAULT_BOARDS:
            try:
                rows = scrape_minisite_table(
                    page,
                    board["list_url"],
                    board["source"],
                    board["track"],
                    fetched_at,
                )
            except Exception as e:
                print(f"FAIL {board['source']}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            out = OUT_DIR / f"{day}_{board['out_suffix']}.csv"
            write_csv(rows, out)
            print(f"{board['source']} → {len(rows)} rows → {out}")
            totals.append(len(rows))
        browser.close()

    if not totals:
        return 3
    print(f"done total_rows={sum(totals)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
