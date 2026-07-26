#!/usr/bin/env python3
"""Merge today's discovery CSVs → data/discovery/YYYY-MM-DD_all.csv + jobs/inbox.

Dedupes by canonical job URL. Keeps newest fetched_at when colliding.
Does NOT write into applications.csv (triage first).
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "data" / "discovery"
INBOX = ROOT / "jobs" / "inbox"

FIELDS = [
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


def load_day_files(day: str) -> list[Path]:
    files = sorted(DISC.glob(f"{day}_*.csv"))
    # exclude prior merged all file when re-merging
    return [p for p in files if not p.name.endswith("_all.csv")]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def merge(rows: list[dict]) -> list[dict]:
    by_url: dict[str, dict] = {}
    for r in rows:
        url = (r.get("url") or "").strip()
        if not url:
            continue
        # normalize jobright query noise
        if "?" in url and "jobright.ai" in url:
            url = url.split("?", 1)[0]
            r = {**r, "url": url}
        prev = by_url.get(url)
        if not prev:
            by_url[url] = r
            continue
        # prefer row with later fetched_at
        if (r.get("fetched_at") or "") >= (prev.get("fetched_at") or ""):
            by_url[url] = r
    # stable-ish sort: track, source, company
    out = list(by_url.values())
    out.sort(key=lambda x: (x.get("track", ""), x.get("source", ""), x.get("company", ""), x.get("role", "")))
    return out


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def write_inbox(rows: list[dict], day: str, fetched_note: str) -> Path:
    INBOX.mkdir(parents=True, exist_ok=True)
    path = INBOX / f"daily-{day}.md"
    by_source = Counter(r.get("source") or "unknown" for r in rows)
    by_track = Counter(r.get("track") or "unknown" for r in rows)
    lines = [
        f"# Discovery inbox — {day}",
        "",
        f"_Merged discovery. {fetched_note}_",
        "",
        "## Volume",
        "",
        f"- Total unique URLs: **{len(rows)}**",
        f"- By source: {dict(by_source)}",
        f"- By track: {dict(by_track)}",
        "",
        "## How this fits",
        "",
        "```text",
        "board minisites + Jobright matches → data/discovery/* → THIS inbox",
        "                              ↓ triage keep/skip",
        "                     data/applications.csv (+ Simplify import)",
        "```",
        "",
        "Not auto-applied. Cadence: morning fetch + optional afternoon refresh.",
        "",
        "## Sample (first 25)",
        "",
    ]
    for r in rows[:25]:
        posted = r.get("posted_relative") or "unknown"
        fetched = r.get("fetched_at") or "unknown"
        lines.append(
            f"- [{r.get('source')}|{r.get('track')}] **{r.get('company')}** — {r.get('role')} "
            f"— {r.get('url')} _(posted {posted}; fetched {fetched})_"
        )
    if len(rows) > 25:
        lines.append(f"\n…and {len(rows) - 25} more in `data/discovery/{day}_all.csv`.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()
    day = args.date

    files = load_day_files(day)
    if not files:
        print(f"No discovery CSVs for {day} under {DISC}", file=__import__("sys").stderr)
        return 2

    all_rows: list[dict] = []
    for path in files:
        chunk = read_rows(path)
        print(f"read {path.name}: {len(chunk)}")
        all_rows.extend(chunk)

    merged = merge(all_rows)
    out = DISC / f"{day}_all.csv"
    write_csv(merged, out)

    fetched_times = sorted({r.get("fetched_at") for r in merged if r.get("fetched_at")})
    note = f"sources={len(files)}; fetched_at values={fetched_times[:4]}{'…' if len(fetched_times) > 4 else ''}"
    inbox = write_inbox(merged, day, note)
    print(f"merged={len(merged)} → {out}")
    print(f"inbox → {inbox}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
