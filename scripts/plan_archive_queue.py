#!/usr/bin/env python3
"""Read-only archive_queue plan. Never writes the Sheet."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    archive_queue_copy_permitted,
    archive_queue_deletes_live,
    archive_queue_row_action,
    plan_archive_queue_copy,
)


def plan_from_rows(rows: list[dict], *, apply_is_live: bool) -> dict:
    actions = Counter(archive_queue_row_action(row) for row in rows)
    by_status = Counter(
        (archive_queue_row_action(row), str(row.get("status") or "").strip())
        for row in rows
    )
    return {
        "rows": len(rows),
        "archive": len(plan_archive_queue_copy(rows)),
        "keep_live": int(actions.get("keep_live", 0)),
        "copy_permitted": archive_queue_copy_permitted(apply_is_live=apply_is_live),
        "deletes_live": archive_queue_deletes_live(),
        "by_status": dict(by_status),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue-csv", type=Path, required=True)
    parser.add_argument("--apply-live", action="store_true")
    args = parser.parse_args(argv)
    rows = list(csv.DictReader(args.queue_csv.read_text(encoding="utf-8").splitlines()))
    plan = plan_from_rows(rows, apply_is_live=args.apply_live)
    print(f"queue_rows={plan['rows']}")
    print(f"archive={plan['archive']}")
    print(f"keep_live={plan['keep_live']}")
    print(f"copy_permitted={plan['copy_permitted']}")
    print(f"deletes_live={plan['deletes_live']}")
    for (action, status), count in sorted(
        plan["by_status"].items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"{count} {action} {status or 'blank'}")
    if args.apply_live:
        print("APPLY_LIVE: do not copy")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
