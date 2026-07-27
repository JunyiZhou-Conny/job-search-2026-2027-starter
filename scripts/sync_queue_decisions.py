#!/usr/bin/env python3
"""Import apply-queue decisions exported from a static queue page.

Only needed when you opened the queue as a plain HTML file. If you run
`scripts/serve_apply_queue.py`, Pass and Applied already write straight to the
repo and this script is unnecessary.

Export shape (either key may be present):

  {
    "decisions": [ {url, company, role, job_id, decision: "pass", reason, decided_at} ],
    "applied":   [ {url, company, role, job_id, cluster, lane, resume_version, decided_at} ]
  }

A bare list is treated as pass decisions for backward compatibility.

Usage:
  python3 scripts/sync_queue_decisions.py --file ~/Downloads/queue_decisions_2026-07-27.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from queue_writeback import DECISIONS, record_applied, record_pass  # noqa: E402


def load_export(path: Path) -> tuple[list[dict], list[dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data, []
    passes = list(data.get("decisions") or data.get("passes") or [])
    applied = list(data.get("applied") or [])
    return passes, applied


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="JSON export from the apply-queue page")
    args = ap.parse_args()
    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 1

    passes, applied = load_export(path)
    passes = [r for r in passes if (r.get("url") or "").strip()]
    applied = [r for r in applied if (r.get("url") or "").strip()]
    if not passes and not applied:
        print("no decisions in export")
        return 0

    if passes:
        result = record_pass(passes)
        print(
            f"job_decisions: +{result['decisions_added']} new, "
            f"~{result['decisions_updated']} updated → {DECISIONS}"
        )
        print(f"applications status→passed: {result['applications_updated']}")

    if applied:
        result = record_applied(applied)
        print(f"applications status→applied: {len(result['applied'])}")
        if result["created"]:
            print(f"  created rows: {', '.join(result['created'])}")
        if result["already_in_pipeline"]:
            print(f"  already in pipeline (untouched): {len(result['already_in_pipeline'])}")

    print("Re-run: python3 scripts/generate_apply_queue.py --date YYYY-MM-DD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
