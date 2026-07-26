#!/usr/bin/env python3
"""Import apply-queue Pass decisions into the repo.

JSON export shape from the apply-queue HTML:

  {
    "decisions": [
      {
        "url": "...",
        "company": "...",
        "role": "...",
        "job_id": "J...",
        "decision": "pass",
        "reason": "needs 1+ YOE",
        "decided_at": "ISO-8601"
      }
    ]
  }

Writes/updates:
  - data/job_decisions.csv  (URL archive — apply queue will hide these)
  - data/applications.csv   (status=passed when a matching row exists)
  - data/activity_log.csv

Usage:
  python3 scripts/sync_queue_decisions.py --file ~/Downloads/queue_decisions_....json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from js_lib import (  # noqa: E402
    ACTIVITY,
    APPLICATIONS,
    APP_FIELDS,
    BACKUPS,
    LOG_FIELDS,
    ensure_csv,
    now_iso,
    read_rows,
    write_rows,
)

DECISIONS = ROOT / "data" / "job_decisions.csv"
DECISION_FIELDS = [
    "url",
    "company",
    "role",
    "job_id",
    "decision",
    "reason",
    "decided_at",
    "source",
]


def canon(url: str) -> str:
    return (url or "").strip().split("?")[0].rstrip("/").lower()


def load_export(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return list(data.get("decisions") or [])


def upsert_decisions(rows: list[dict]) -> tuple[int, int]:
    ensure_csv(DECISIONS, DECISION_FIELDS)
    existing = read_rows(DECISIONS)
    by_url = {canon(r.get("url", "")): r for r in existing if r.get("url")}
    added = updated = 0
    for row in rows:
        url = (row.get("url") or "").strip()
        if not url:
            continue
        key = canon(url)
        decision = (row.get("decision") or "pass").strip().lower() or "pass"
        rec = {
            "url": url.split("?")[0],
            "company": row.get("company") or "",
            "role": row.get("role") or "",
            "job_id": row.get("job_id") or "",
            "decision": decision,
            "reason": row.get("reason") or "",
            "decided_at": row.get("decided_at") or now_iso(),
            "source": row.get("source") or "apply_queue",
        }
        if key in by_url:
            prev = by_url[key]
            if prev.get("decided_at") and not row.get("decided_at"):
                rec["decided_at"] = prev["decided_at"]
            by_url[key] = {**prev, **rec}
            updated += 1
        else:
            by_url[key] = rec
            added += 1
    write_rows(DECISIONS, DECISION_FIELDS, list(by_url.values()))
    return added, updated


def log_event(job_id: str, from_status: str, to_status: str, note: str) -> None:
    ensure_csv(ACTIVITY, LOG_FIELDS)
    rows = read_rows(ACTIVITY)
    rows.append(
        {
            "timestamp": now_iso(),
            "job_id": job_id,
            "contact_id": "",
            "event_type": "status_change",
            "from_status": from_status,
            "to_status": to_status,
            "note": note,
        }
    )
    write_rows(ACTIVITY, LOG_FIELDS, rows)


def update_applications(rows: list[dict]) -> int:
    if not APPLICATIONS.exists():
        return 0
    apps = read_rows(APPLICATIONS)
    by_url: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    for r in apps:
        for k in ("job_url", "posting_url"):
            u = canon(r.get(k, ""))
            if u:
                by_url[u] = r
        if r.get("job_id"):
            by_id[r["job_id"]] = r

    changed = 0
    stamp = now_iso()
    protect = {"applied", "oa", "recruiter_screen", "technical_screen", "onsite", "offer", "accepted"}
    for row in rows:
        if (row.get("decision") or "pass").lower() != "pass":
            continue
        app = None
        jid = (row.get("job_id") or "").strip()
        if jid and jid in by_id:
            app = by_id[jid]
        else:
            app = by_url.get(canon(row.get("url", "")))
        if not app:
            continue
        old = (app.get("status") or "").strip()
        if old in protect:
            continue
        reason = (row.get("reason") or "").strip()
        if old == "passed":
            if reason and reason not in (app.get("notes") or ""):
                app["notes"] = ((app.get("notes") or "").rstrip() + f" | pass: {reason}").strip(" |")
                app["updated_at"] = stamp
                app["last_update"] = stamp
                changed += 1
            continue
        app["status"] = "passed"
        app["application_status"] = "passed"
        app["next_action"] = ""
        app["next_action_date"] = ""
        note = f"passed via apply queue: {reason}" if reason else "passed via apply queue"
        app["notes"] = ((app.get("notes") or "").rstrip() + f" | {note}").strip(" |")
        app["updated_at"] = stamp
        app["last_update"] = stamp
        log_event(app.get("job_id") or "", old, "passed", reason or "user passed after JD review")
        changed += 1

    if changed:
        BACKUPS.mkdir(parents=True, exist_ok=True)
        dest = BACKUPS / f"applications_{stamp.replace(':', '').replace('-', '')[:15]}.csv"
        dest.write_text(APPLICATIONS.read_text(encoding="utf-8"), encoding="utf-8")
        fields = list(apps[0].keys()) if apps else list(APP_FIELDS)
        for f in APP_FIELDS:
            if f not in fields:
                fields.append(f)
        write_rows(APPLICATIONS, fields, apps)
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="JSON export from apply-queue HTML")
    args = ap.parse_args()
    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 1
    rows = [r for r in load_export(path) if (r.get("url") or "").strip()]
    if not rows:
        print("no decisions in export")
        return 0
    added, updated = upsert_decisions(rows)
    app_n = update_applications(rows)
    print(f"job_decisions: +{added} new, ~{updated} updated → {DECISIONS}")
    print(f"applications status→passed: {app_n}")
    print("Re-run: python3 scripts/generate_apply_queue.py --date YYYY-MM-DD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
