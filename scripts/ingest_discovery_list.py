#!/usr/bin/env python3
"""Parse a pasted discovery list (markdown/links) into data/discovery/YYYY-MM-DD.csv.

Supports lines like:
  - Company — Role — https://...
  Company | Role | https://...
  https://... (role unknown)

No passwords. No network calls. Exp B helper.
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "discovery"
URL_RE = re.compile(r"https?://\S+")


def parse_lines(text: str) -> list[dict]:
    rows = []
    for raw in text.splitlines():
        line = raw.strip().lstrip("-*").strip()
        if not line or line.startswith("#"):
            continue
        m = URL_RE.search(line)
        if not m:
            continue
        url = m.group(0).rstrip(").,]")
        left = line[: m.start()].strip(" -—|\t")
        company, role = "", ""
        if "—" in left:
            parts = [p.strip() for p in left.split("—")]
            company = parts[0] if parts else ""
            role = parts[1] if len(parts) > 1 else ""
        elif "|" in left:
            parts = [p.strip() for p in left.split("|")]
            company = parts[0] if parts else ""
            role = parts[1] if len(parts) > 1 else ""
        else:
            company = left
        rows.append({
            "company": company,
            "role": role,
            "url": url,
            "source": "manual_paste",
            "date_discovered": date.today().isoformat(),
            "notes": "",
        })
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, help="Path to markdown/text list")
    p.add_argument("--date", default=date.today().isoformat())
    args = p.parse_args()
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise SystemExit(f"Not found: {path}")
    rows = parse_lines(path.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.date}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["company", "role", "url", "source", "date_discovered", "notes"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
