#!/usr/bin/env python3
"""Scrape Jobright minisite boards that power intern-list / newgrad-jobs.

These sites embed tables like:
  https://jobright.ai/minisites-jobs/newgrad/us/swe?embed=true
  https://jobright.ai/minisites-jobs/intern/us/ml_ai?embed=true

Discovery only. Writes one CSV per (track x category) under data/discovery/.
Each row carries fetched_at (ISO timestamp of this run) and category.

    .venv/bin/python scripts/automation/export_board_lists.py
    .venv/bin/python scripts/automation/export_board_lists.py --only swe ml_ai
    .venv/bin/python scripts/automation/export_board_lists.py --track intern --cap 40

Category slugs are NOT the ?k= values used by intern-list.com. Verify new ones
with scripts/automation/probe_board_categories.py before enabling them here.
"""

from __future__ import annotations

import argparse
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

# Tracks are co-primary per config/profile.yaml (track_balance: balanced).
TRACKS = [
    {"kind": "newgrad", "source": "newgrad_jobs", "track": "new_grad_2027_start"},
    {"kind": "intern", "source": "intern_list", "track": "internship_if_eligible"},
]

# Verified 2026-07-28 with probe_board_categories.py: each returns a populated
# table on both tracks. `enabled: False` categories resolve but are off-target
# for the current role clusters -- flip to True rather than editing URLs.
BOARD_CATEGORIES = [
    {"slug": "swe", "cluster_hint": "cloud_swe", "enabled": True},
    {"slug": "ml_ai", "cluster_hint": "data_ml", "enabled": True},
    {"slug": "data_science", "cluster_hint": "data_ml", "enabled": True},
    {"slug": "data_analysis", "cluster_hint": "data_ml", "enabled": True},
    {"slug": "healthcare", "cluster_hint": "health_ai", "enabled": True},
    {"slug": "product_management", "cluster_hint": None, "enabled": False},
]

LIST_URL = "https://jobright.ai/minisites-jobs/{kind}/us/{slug}?embed=true"

# Filtering is a domain gate plus a vetoed exception list.
#
# DOMAIN must match, and deliberately excludes seniority words (intern,
# new grad, entry level). Including them was a latent bug: on an intern board
# every row matches "intern", so the domain gate passed everything. That was
# invisible while only the SWE board was scraped and would have flooded triage
# with clinical roles once healthcare was enabled.
DOMAIN = re.compile(
    r"(software|\bswe\b|engineer|developer|programmer|\bdata\b|machine\s*learning|"
    r"\bml\b|\bai\b|\bllm\b|\bnlp\b|computer\s*vision|deep\s*learning|cloud|platform|"
    r"backend|front[\s-]?end|full[\s-]?stack|infra|devops|\bsre\b|distributed|compiler|"
    r"firmware|embedded|robotics|quant|analytics|bioinformatic|computational|informatics|"
    r"research\s*scientist|security|database|\bapi\b)",
    re.I,
)

# Clinical and non-technical roles that the healthcare and analysis boards carry.
DROP = re.compile(
    r"(nurse|\brn\b|\blpn\b|physician|surgeon|pharmac|therapist|therapy|clinician|"
    r"patient\s*care|medical\s*assistant|caregiver|phlebotom|dental|veterinar|"
    r"social\s*work|counselor|dietit|respiratory|paramedic|technologist|technician|"
    r"medical\s*cod|scribe|billing|sales\b|marketing|account\s*executive|recruit|"
    r"human\s*resources|\bhr\b|customer\s*success|customer\s*service|cashier|driver|"
    r"warehouse|janitor|receptionist)",
    re.I,
)

# A DROP hit is overridden when the title also carries a strong engineering
# signal, so "Radiology AI Engineer" survives while "Radiologic Technologist"
# does not.
STRONG = re.compile(
    r"(engineer|software|developer|machine\s*learning|data\s*scien|\bml\b|\bai\b|"
    r"\bswe\b|research\s*scientist)",
    re.I,
)


def build_boards(only: list[str] | None, track_filter: str) -> list[dict]:
    boards = []
    for tr in TRACKS:
        if track_filter != "both" and tr["kind"] != track_filter:
            continue
        for cat in BOARD_CATEGORIES:
            if only:
                if cat["slug"] not in only:
                    continue
            elif not cat["enabled"]:
                continue
            boards.append(
                {
                    "source": tr["source"],
                    "track": tr["track"],
                    "category": cat["slug"],
                    "cluster_hint": cat["cluster_hint"] or "",
                    "list_url": LIST_URL.format(kind=tr["kind"], slug=cat["slug"]),
                    "out_suffix": f"{tr['kind']}_{cat['slug']}",
                }
            )
    return boards


def is_target(company: str, role: str) -> bool:
    blob = f"{company} {role}"
    if not DOMAIN.search(blob):
        return False
    if DROP.search(blob) and not STRONG.search(blob):
        return False
    return True


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


def scrape_minisite_table(page, board: dict, fetched_at: str, cap: int | None) -> list[dict]:
    list_url = board["list_url"]
    source, track = board["source"], board["track"]
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

        if not is_target(company, role):
            continue

        rows_out.append(
            {
                "company": company,
                "role": role,
                "url": url,
                "source": source,
                "track": track,
                "category": board["category"],
                "date_discovered": fetched_at[:10],
                "fetched_at": fetched_at,
                "posted_relative": posted_rel,
                "location": location,
                "work_model": work_model,
                "h1b_signal": h1b,
                "is_new_grad_signal": is_new_grad,
                "list_url": list_url.split("?")[0],
                "notes": (
                    f"minisite_scrape;category={board['category']};"
                    f"cluster_hint={board['cluster_hint']};posted={posted_rel}"
                ),
            }
        )
        if cap and len(rows_out) >= cap:
            break
    return rows_out


def write_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "company",
        "role",
        "url",
        "source",
        "track",
        "category",
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--only",
        nargs="+",
        metavar="SLUG",
        help="scrape only these category slugs, ignoring the enabled flag",
    )
    ap.add_argument("--track", choices=["intern", "newgrad", "both"], default="both")
    ap.add_argument(
        "--cap",
        type=int,
        default=None,
        help="max kept rows per board; use to hold triage volume down",
    )
    args = ap.parse_args()

    load_env()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install: pip install -r requirements-automation.txt", file=sys.stderr)
        return 1

    boards = build_boards(args.only, args.track)
    if not boards:
        print("No boards selected.", file=sys.stderr)
        return 2

    headless = os.environ.get("PLAYWRIGHT_HEADLESS", "true").lower() in {"1", "true", "yes"}
    fetched_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    day = fetched_at[:10]

    print(f"fetched_at={fetched_at}")
    print(f"boards={len(boards)} track={args.track} cap={args.cap or 'none'}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, channel="chrome")
        page = browser.new_page()
        totals: list[int] = []
        failures: list[str] = []
        for board in boards:
            label = f"{board['source']}/{board['category']}"
            try:
                rows = scrape_minisite_table(page, board, fetched_at, args.cap)
            except Exception as e:
                print(f"FAIL {label}: {type(e).__name__}: {e}", file=sys.stderr)
                failures.append(label)
                continue
            out = OUT_DIR / f"{day}_{board['out_suffix']}.csv"
            write_csv(rows, out)
            print(f"{label:<34} → {len(rows):>3} rows → {out.name}")
            totals.append(len(rows))
        browser.close()

    if not totals:
        return 3
    print(f"done boards_ok={len(totals)} total_rows={sum(totals)}")
    if failures:
        print(f"failed boards: {', '.join(failures)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
