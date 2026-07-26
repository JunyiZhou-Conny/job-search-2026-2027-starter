#!/usr/bin/env python3
"""Apply or reject rows from generated/label_suggestions.csv after human review.

Never auto-applies. Interactive-by-file: mark decision=accept|reject in the CSV, then run --commit.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APP_FIELDS, APPLICATIONS, log, read_rows, sync_app_aliases, today_iso, write_rows,
)
from label_job import suggest_from_text  # noqa: E402

SUGGESTIONS = ROOT / "generated" / "label_suggestions.csv"
FIELDS = [
    "job_id", "company", "role",
    "suggested_hard_eligibility", "suggested_sponsorship_signal", "suggested_role_cluster",
    "suggested_pursuit_lane", "suggested_priority", "suggested_resume_version",
    "confidence", "evidence", "reason", "needs_review", "timestamp",
    "decision", "notes",
]


def batch_suggest(min_blank_only: bool = True) -> int:
    apps = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    existing = {}
    if SUGGESTIONS.exists():
        for r in read_rows(SUGGESTIONS):
            existing[r.get("job_id", "")] = r

    out = []
    n = 0
    for app in apps:
        jid = app.get("job_id") or app.get("id") or ""
        if not jid:
            continue
        text = " ".join([
            app.get("role", ""),
            app.get("notes", ""),
            app.get("sponsorship_evidence", ""),
            app.get("hard_eligibility_reason", ""),
        ])
        s = suggest_from_text(text, role=app.get("role", ""), company=app.get("company", ""))
        conf = min(
            s["hard_eligibility"]["confidence"],
            s["pursuit_lane"]["confidence"],
            s["role_cluster"]["confidence"],
        )
        prev = existing.get(jid, {})
        decision = prev.get("decision", "")
        notes = prev.get("notes", "")
        if app.get("label_source") == "manual":
            notes = (notes + "; manual label present — auto will not overwrite").strip("; ")
            decision = decision or "skip_manual"
        elif min_blank_only and app.get("pursuit_lane") and app.get("hard_eligibility") and conf < 0.90:
            notes = (notes + "; already labeled; suggestion for comparison only").strip("; ")

        out.append({
            "job_id": jid,
            "company": app.get("company", ""),
            "role": app.get("role", ""),
            "suggested_hard_eligibility": s["hard_eligibility"]["value"],
            "suggested_sponsorship_signal": s["sponsorship_signal"]["value"],
            "suggested_role_cluster": s["role_cluster"]["value"],
            "suggested_pursuit_lane": s["pursuit_lane"]["value"],
            "suggested_priority": s["priority"]["value"],
            "suggested_resume_version": s["resume_version"]["value"],
            "confidence": f"{conf:.2f}",
            "evidence": "; ".join(s["hard_eligibility"].get("evidence") or []),
            "reason": s["pursuit_lane"]["reason"],
            "needs_review": "yes" if s["needs_review"] or conf < 0.90 or app.get("label_source") == "manual" else "no",
            "timestamp": today_iso(),
            "decision": decision,
            "notes": notes,
        })
        n += 1

    SUGGESTIONS.parent.mkdir(parents=True, exist_ok=True)
    write_rows(SUGGESTIONS, FIELDS, out)
    log(f"wrote {len(out)} suggestions ({n} newly scored) → {SUGGESTIONS}")
    print(SUGGESTIONS)
    return 0


def commit_decisions() -> int:
    if not SUGGESTIONS.exists():
        raise SystemExit(f"Missing {SUGGESTIONS}. Run --batch first.")
    suggestions = read_rows(SUGGESTIONS)
    apps = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    by_id = {(r.get("job_id") or r.get("id")): r for r in apps}
    applied = skipped = 0
    for s in suggestions:
        if (s.get("decision") or "").strip().lower() != "accept":
            continue
        jid = s.get("job_id", "")
        row = by_id.get(jid)
        if not row:
            skipped += 1
            continue
        if row.get("label_source") == "manual":
            log(f"skip {jid}: manual label")
            skipped += 1
            continue
        row["hard_eligibility"] = s["suggested_hard_eligibility"]
        row["sponsorship_signal"] = s["suggested_sponsorship_signal"]
        row["role_cluster"] = s["suggested_role_cluster"]
        row["pursuit_lane"] = s["suggested_pursuit_lane"]
        row["priority"] = s["suggested_priority"]
        if not row.get("resume_version"):
            row["resume_version"] = s["suggested_resume_version"]
        row["label_confidence"] = s["confidence"]
        row["label_reason"] = s["reason"]
        row["label_source"] = "auto"
        row["needs_review"] = "true" if s.get("needs_review") == "yes" else "false"
        row["updated_at"] = today_iso()
        row["last_update"] = today_iso()
        applied += 1
    write_rows(APPLICATIONS, APP_FIELDS, [sync_app_aliases(r) for r in apps])
    log(f"committed accepts={applied} skipped={skipped}")
    print(f"applied={applied} skipped={skipped}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--batch", action="store_true", help="Generate/refresh label suggestions CSV")
    g.add_argument("--commit", action="store_true", help="Apply rows marked decision=accept")
    args = p.parse_args()
    if args.batch:
        return batch_suggest()
    return commit_decisions()


if __name__ == "__main__":
    raise SystemExit(main())
