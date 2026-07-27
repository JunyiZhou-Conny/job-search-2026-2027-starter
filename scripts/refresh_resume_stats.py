#!/usr/bin/env python3
"""Recompute resume-version outcome counters from applications.csv.

`data/resume_versions.csv` carries applications_count / oa_count / screen_count /
technical_count / offer_count. Nothing kept them current, so every resume looked
equally untested. This derives them from the ledger instead.

Usage:
  python3 scripts/refresh_resume_stats.py          # write
  python3 scripts/refresh_resume_stats.py --dry    # show only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS,
    RESUME_VERSION_FIELDS,
    RESUME_VERSIONS,
    read_rows,
    write_rows,
)

# Which statuses prove a resume reached a given stage. A resume that produced an
# onsite also produced an OA-equivalent signal, so stages are cumulative.
SENT = {
    "applied",
    "oa",
    "recruiter_screen",
    "technical_screen",
    "onsite",
    "final_round",
    "offer",
    "accepted",
    "rejected",
}
REACHED_OA = {"oa", "recruiter_screen", "technical_screen", "onsite", "final_round", "offer", "accepted"}
REACHED_SCREEN = {"recruiter_screen", "technical_screen", "onsite", "final_round", "offer", "accepted"}
REACHED_TECH = {"technical_screen", "onsite", "final_round", "offer", "accepted"}
REACHED_OFFER = {"offer", "accepted"}


def stage_set(app: dict) -> set[str]:
    """Statuses this application can attest to, using current + highest reached."""
    values = {
        (app.get("status") or "").strip().lower(),
        (app.get("stage_current") or "").strip().lower(),
        (app.get("stage_highest_reached") or "").strip().lower(),
    }
    return {v for v in values if v}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="print without writing")
    args = ap.parse_args()

    apps = read_rows(APPLICATIONS)
    versions = read_rows(RESUME_VERSIONS)
    if not versions:
        print("no resume versions registered")
        return 0

    counts: dict[str, dict[str, int]] = {
        v["resume_version"]: {"apps": 0, "oa": 0, "screen": 0, "tech": 0, "offer": 0} for v in versions
    }
    unknown: dict[str, int] = {}

    for app in apps:
        version = (app.get("resume_version") or "").strip()
        if not version:
            continue
        if version not in counts:
            unknown[version] = unknown.get(version, 0) + 1
            continue
        stages = stage_set(app)
        if not stages & SENT:
            continue
        bucket = counts[version]
        bucket["apps"] += 1
        if stages & REACHED_OA:
            bucket["oa"] += 1
        if stages & REACHED_SCREEN:
            bucket["screen"] += 1
        if stages & REACHED_TECH:
            bucket["tech"] += 1
        if stages & REACHED_OFFER:
            bucket["offer"] += 1

    for v in versions:
        c = counts[v["resume_version"]]
        v["applications_count"] = str(c["apps"])
        v["oa_count"] = str(c["oa"])
        v["screen_count"] = str(c["screen"])
        v["technical_count"] = str(c["tech"])
        v["offer_count"] = str(c["offer"])

    width = max(len(v["resume_version"]) for v in versions)
    print(f"{'resume_version'.ljust(width)}  sent  oa  screen  tech  offer")
    for v in sorted(versions, key=lambda r: -int(r["applications_count"] or 0)):
        print(
            f"{v['resume_version'].ljust(width)}  "
            f"{v['applications_count']:>4}  {v['oa_count']:>2}  "
            f"{v['screen_count']:>6}  {v['technical_count']:>4}  {v['offer_count']:>5}"
        )
    if unknown:
        print("\nresume_version values in applications.csv with no registry row:")
        for name, n in sorted(unknown.items(), key=lambda kv: -kv[1]):
            print(f"  {name}  ({n} applications)")

    if args.dry:
        print("\ndry run — nothing written")
        return 0

    fields = list(versions[0].keys())
    for f in RESUME_VERSION_FIELDS:
        if f not in fields:
            fields.append(f)
    write_rows(RESUME_VERSIONS, fields, versions)
    print(f"\nupdated {RESUME_VERSIONS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
