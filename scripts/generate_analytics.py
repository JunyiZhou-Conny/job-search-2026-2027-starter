#!/usr/bin/env python3
"""Compute funnel analytics with sample-size guards."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, APPLIED_PLUS, INTERVIEW_PLUS, log, read_rows, sync_app_aliases,
)

OUT_MD = ROOT / "generated" / "analytics" / "dashboard.md"
OUT_FUNNEL = ROOT / "generated" / "analytics" / "funnel.csv"


def rate(n: int, d: int) -> str:
    if d <= 0:
        return "n/a"
    return f"{n / d:.0%}"


def interpret(n: int) -> str:
    if n < 5:
        return "n<5: show only, no interpretation"
    if n < 15:
        return "5≤n<15: weak hypothesis only"
    return "n≥15: provisional strategy OK"


def group_funnel(rows: List[dict], field: str) -> List[dict]:
    groups: Dict[str, List[dict]] = defaultdict(list)
    for r in rows:
        groups[r.get(field) or "unknown"].append(r)
    out = []
    for key, items in sorted(groups.items()):
        applied = sum(1 for r in items if r.get("status") in APPLIED_PLUS)
        oa = sum(1 for r in items if r.get("status") in INTERVIEW_PLUS or r.get("stage_highest_reached") in INTERVIEW_PLUS)
        tech = sum(1 for r in items if (r.get("stage_highest_reached") or r.get("status")) in {
            "technical_screen", "onsite", "final_round", "offer", "accepted"})
        offers = sum(1 for r in items if (r.get("stage_highest_reached") or r.get("status")) in {"offer", "accepted"})
        out.append({
            "group_field": field,
            "group_value": key,
            "n": str(len(items)),
            "applied": str(applied),
            "oa_plus": str(oa),
            "technical_plus": str(tech),
            "offers": str(offers),
            "oa_rate": rate(oa, applied),
            "technical_rate": rate(tech, applied),
            "offer_rate": rate(offers, applied),
            "sample_rule": interpret(applied),
        })
    return out


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    rows = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    statuses = Counter(r.get("status") or "unknown" for r in rows)
    applied_n = sum(1 for r in rows if r.get("status") in APPLIED_PLUS)
    oa_n = sum(1 for r in rows if r.get("status") in INTERVIEW_PLUS)

    # minutes / efficiency
    timed = [r for r in rows if (r.get("application_minutes") or "").isdigit()]
    minutes_total = sum(int(r["application_minutes"]) for r in timed)
    interviews = sum(1 for r in rows if r.get("status") in INTERVIEW_PLUS)
    per_100 = f"{(interviews / applied_n * 100):.1f}" if applied_n else "n/a"
    per_10h = "n/a"
    if minutes_total > 0:
        per_10h = f"{(interviews / minutes_total * 600):.2f}"

    funnel_rows = []
    for field in ("source", "role_cluster", "resume_version", "pursuit_lane", "priority",
                  "tailoring_level", "referral_status", "sponsorship_signal", "employment_type"):
        funnel_rows.extend(group_funnel(rows, field))

    OUT_FUNNEL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FUNNEL.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(funnel_rows[0].keys()) if funnel_rows else [
            "group_field", "group_value", "n", "applied", "oa_plus", "technical_plus", "offers",
            "oa_rate", "technical_rate", "offer_rate", "sample_rule"])
        w.writeheader()
        w.writerows(funnel_rows)

    md = [
        "# Analytics dashboard\n\n",
        f"- Roles tracked: {len(rows)}\n",
        f"- Applied+: {applied_n}\n",
        f"- OA/interview+: {oa_n}\n",
        f"- Interviews per 100 applications: {per_100}\n",
        f"- Interviews per 10 hours (timed apps only): {per_10h}\n",
        f"- Timed applications with minutes: {len(timed)}\n\n",
        "## Status counts\n\n",
    ]
    for k, v in sorted(statuses.items()):
        md.append(f"- {k}: {v}\n")
    md.append("\n## Sample-size policy\n\n")
    md.append("- n<5: display only\n- 5–14: weak hypothesis\n- ≥15: provisional strategy\n")
    md.append("- Referral/networking groups are selection-biased.\n")
    md.append(f"\nFull funnel tables: `{OUT_FUNNEL.relative_to(ROOT)}`\n")

    OUT_MD.write_text("".join(md), encoding="utf-8")
    log(f"wrote {OUT_MD} and {OUT_FUNNEL}")
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
