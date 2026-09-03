#!/usr/bin/env python3
"""Merge one run's discovery CSVs → data/discovery/{RUN}_all.csv + jobs/inbox.

RUN is the UTC run stamp YYYY-MM-DDTHH, so the morning and evening runs of one
day write distinct files. A plain YYYY-MM-DD is still accepted.

Dedupes by canonical job URL. Keeps newest fetched_at when colliding.
Does NOT write into applications.csv (triage first).
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISC = ROOT / "data" / "discovery"
INBOX = ROOT / "jobs" / "inbox"
GEN = ROOT / "generated"

STAMP_FORMAT = "%Y-%m-%dT%H"
STAMP_RE = re.compile(r"(\d{4}-\d{2}-\d{2})(T\d{2})?")

FIELDS = [
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


def run_stamp(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    return now.astimezone(timezone.utc).strftime(STAMP_FORMAT)


def source_day(stamp: str) -> str:
    """Calendar day the exporters keyed their CSVs by.

    Exporters use the machine's local date while the stamp is UTC, so the
    stamp's hour is converted back to local time before taking the date.
    """
    m = STAMP_RE.fullmatch(stamp)
    if not m:
        raise ValueError(f"bad run stamp {stamp!r}; expected YYYY-MM-DD or YYYY-MM-DDTHH")
    if not m.group(2):
        return stamp
    utc = datetime.strptime(stamp, STAMP_FORMAT).replace(tzinfo=timezone.utc)
    return utc.astimezone().date().isoformat()


def load_day_files(day: str) -> list[Path]:
    files = sorted(DISC.glob(f"{day}_*.csv"))
    # exclude prior merged all file when re-merging
    return [p for p in files if not p.name.endswith("_all.csv")]


def sweep_csv(run: str) -> Path:
    return GEN / f"ashby_sweep_{run}.csv"


def sweep_row_to_discovery(row: dict, fetched_at: str) -> dict:
    """Map one Ashby-sweep posting onto the merge schema.

    applyUrl is the identity the apply stage uses. jobUrl stays in list_url.
    Form facts ride in notes so the existing merge columns do not fork.
    """
    url = (row.get("applyUrl") or row.get("jobUrl") or "").strip()
    employment = row.get("employmentType") or ""
    track = "internship_if_eligible" if employment == "Intern" else "new_grad"
    facts = []
    flag = row.get("g2_candidate")
    if flag in {True, "True", "true"}:
        facts.append("g2_candidate")
    if row.get("required_corrections"):
        facts.append(f"corrections={row['required_corrections']}")
    if row.get("g2_blockers"):
        facts.append(f"blockers={row['g2_blockers']}")
    extra = (row.get("notes") or "").strip()
    notes = ";".join(x for x in (*facts, extra) if x)
    return {
        "company": row.get("company") or "",
        "role": row.get("title") or "",
        "url": url,
        "source": "ashby_sweep",
        "track": track,
        "category": "swe",
        "date_discovered": (row.get("publishedAt") or "")[:10],
        "fetched_at": fetched_at,
        "posted_relative": row.get("publishedAt") or "",
        "location": row.get("location") or "",
        "work_model": "",
        "h1b_signal": "",
        "is_new_grad_signal": "",
        "list_url": row.get("jobUrl") or "",
        "notes": notes,
    }


def load_ashby_sweep(run: str, fetched_at: str | None = None) -> list[dict]:
    path = sweep_csv(run)
    if not path.exists():
        return []
    fetched_at = fetched_at or datetime.now(timezone.utc).isoformat()
    out = []
    for row in read_rows(path):
        if not (row.get("applyUrl") or row.get("jobUrl")):
            continue
        out.append(sweep_row_to_discovery(row, fetched_at))
    return out


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
    by_category = Counter(r.get("category") or "unknown" for r in rows)
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
        f"- By category: {dict(by_category)}",
        "",
        "## How this fits",
        "",
        "```text",
        "board minisites + Jobright + Ashby sweep → data/discovery/* → THIS inbox",
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--date",
        default=None,
        metavar="RUN",
        help="run stamp YYYY-MM-DDTHH in UTC, or a plain YYYY-MM-DD; default: the current UTC hour",
    )
    args = ap.parse_args(argv)
    day = args.date or run_stamp()
    try:
        input_day = source_day(day)
    except ValueError as exc:
        ap.error(str(exc))

    files = load_day_files(input_day)
    sweep_rows = load_ashby_sweep(day)
    if not files and not sweep_rows:
        print(f"No discovery CSVs for {input_day} under {DISC}", file=__import__("sys").stderr)
        return 2

    all_rows: list[dict] = []
    for path in files:
        chunk = read_rows(path)
        print(f"read {path.name}: {len(chunk)}")
        all_rows.extend(chunk)
    if sweep_rows:
        print(f"read {sweep_csv(day).name}: {len(sweep_rows)}")
        all_rows.extend(sweep_rows)

    merged = merge(all_rows)
    out = DISC / f"{day}_all.csv"
    write_csv(merged, out)

    fetched_times = sorted({r.get("fetched_at") for r in merged if r.get("fetched_at")})
    note = f"sources={len(files)}; fetched_at values={fetched_times[:4]}{'…' if len(fetched_times) > 4 else ''}"
    inbox = write_inbox(merged, day, note)
    print(f"run={day}")
    print(f"merged={len(merged)} → {out}")
    print(f"inbox → {inbox}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
