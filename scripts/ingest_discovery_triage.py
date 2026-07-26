#!/usr/bin/env python3
"""Ingest keep rows from generated/discovery_triage_YYYY-MM-DD.csv into applications.csv.

Default: rows with decision=keep (or user_confirm=keep).
Does not auto-apply. Dedupes by canonical job URL.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (
    DATA,  # noqa: E402
    ACTIVITY,
    APP_FIELDS,
    APPLICATIONS,
    BACKUPS,
    LOG_FIELDS,
    ensure_csv,
    now_iso,
    read_rows,
    sync_app_aliases,
    write_rows,
)


def next_id(prefix: str, rows: list[dict], field: str) -> str:
    day = date.today().strftime("%Y%m%d")
    stem = f"{prefix}{day}-"
    nums = []
    for r in rows:
        value = r.get(field) or r.get("id") or ""
        if value.startswith(stem):
            try:
                nums.append(int(value.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{stem}{max(nums, default=0) + 1:03d}"


def log_event(job_id: str, event_type: str, to_status: str = "", note: str = "") -> None:
    ensure_csv(ACTIVITY, LOG_FIELDS)
    rows = read_rows(ACTIVITY)
    rows.append(
        {
            "timestamp": now_iso(),
            "job_id": job_id,
            "contact_id": "",
            "event_type": event_type,
            "from_status": "",
            "to_status": to_status,
            "note": note,
        }
    )
    write_rows(ACTIVITY, LOG_FIELDS, rows)

GEN = ROOT / "generated"

CLUSTER_RESUME = {
    "cloud_swe": "2026-07-20_cloud-swe_v1.1",
    "data_ml": "2026-07-20_data-ml_v1.1",
    "health_ai": "2026-07-20_health-ai_v1.1",
}

LANE_PRIORITY = {"core": "A", "broad": "B", "practice": "C"}


def canon(url: str) -> str:
    return (url or "").strip().split("?")[0]



def passed_urls() -> set[str]:
    path = DATA / "job_decisions.csv"
    if not path.exists():
        return set()
    out = set()
    for r in read_rows(path):
        if (r.get("decision") or "").lower() == "pass":
            u = canon(r.get("url", ""))
            if u:
                out.add(u)
    # applications already passed
    if APPLICATIONS.exists():
        for r in read_rows(APPLICATIONS):
            if (r.get("status") or "").lower() == "passed":
                u = canon(r.get("job_url") or r.get("posting_url") or "")
                if u:
                    out.add(u)
    return out

def existing_urls(apps: list[dict]) -> set[str]:
    out = set()
    for a in apps:
        for k in ("job_url", "posting_url"):
            u = canon(a.get(k, ""))
            if u:
                out.add(u)
    return out


def employment_type(role: str, track: str) -> str:
    blob = f"{role} {track}".lower()
    if "intern" in blob:
        return "internship"
    return "new_grad"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument(
        "--require-user-confirm",
        action="store_true",
        help="Only ingest rows where user_confirm=keep (stricter)",
    )
    args = ap.parse_args()
    day = args.date
    triage_path = GEN / f"discovery_triage_{day}.csv"
    if not triage_path.exists():
        raise SystemExit(f"Missing {triage_path}")

    with triage_path.open(newline="", encoding="utf-8-sig") as f:
        triage = list(csv.DictReader(f))

    picks = []
    for r in triage:
        uc = (r.get("user_confirm") or "").strip().lower()
        dec = (r.get("decision") or "").strip().lower()
        if args.require_user_confirm:
            if uc == "keep":
                picks.append(r)
        elif uc == "keep" or (not uc and dec == "keep"):
            picks.append(r)

    if not picks:
        print("No keep rows to ingest.")
        return 0

    ensure_csv(APPLICATIONS, APP_FIELDS)
    apps = read_rows(APPLICATIONS)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    # lightweight backup
    write_rows(BACKUPS / f"applications_before_triage_ingest_{stamp}.csv", APP_FIELDS, apps)

    seen = existing_urls(apps) | passed_urls()
    today = date.today().isoformat()
    created = []
    skipped = []

    for r in picks:
        url = canon(r.get("url", ""))
        if not url or not r.get("company") or not r.get("role"):
            skipped.append(("bad_row", r.get("company"), r.get("role")))
            continue
        if url in seen:
            skipped.append(("duplicate", r.get("company"), r.get("role")))
            continue

        lane = (r.get("suggested_lane") or "broad").strip()
        cluster = (r.get("suggested_cluster") or "cloud_swe").strip()
        priority = LANE_PRIORITY.get(lane, "B")
        job_id = next_id("J", apps, "id")
        emp = employment_type(r.get("role", ""), r.get("track", ""))
        discovered = (r.get("fetched_at") or today)[:10]

        row = {field: "" for field in APP_FIELDS}
        row.update(
            {
                "id": job_id,
                "job_id": job_id,
                "company": r.get("company", ""),
                "role": r.get("role", ""),
                "job_url": url,
                "posting_url": url,
                "source": r.get("source") or "discovery_triage",
                "source_detail": f"triage:{day}",
                "location": r.get("location", ""),
                "work_model": r.get("work_model", ""),
                "employment_type": emp,
                "role_cluster": cluster,
                "date_discovered": discovered,
                "date_found": discovered,
                "status": "discovered",
                "application_status": "discovered",
                "resume_version": CLUSTER_RESUME.get(cluster, ""),
                "pursuit_lane": lane,
                "priority": priority,
                "eligibility": "unclear",
                "hard_eligibility": "uncertain",
                "sponsorship_signal": "unclear",
                "auth_work_authorized": "not_asked",
                "auth_needs_sponsorship": "not_asked",
                "label_source": "triage_confirmed",
                "label_reason": (r.get("reason") or "")[:500],
                "needs_review": "false",
                "next_action": (
                    f"Open posting → Simplify autofill with {CLUSTER_RESUME.get(cluster, 'cluster resume')} → submit if still open"
                ),
                "next_action_date": today,
                "notes": f"[triage:{day} decision=keep] {r.get('reason', '')}".strip(),
                "created_at": today,
                "updated_at": today,
                "last_update": today,
            }
        )
        row = sync_app_aliases(row)
        apps.append(row)
        seen.add(url)
        created.append(job_id)
        log_event(
            job_id=job_id,
            event_type="triage_ingested",
            to_status="discovered",
            note=f"{r.get('company')} — {r.get('role')}",
        )

    write_rows(APPLICATIONS, APP_FIELDS, [sync_app_aliases(a) for a in apps])

    # mark user_confirm on triage file
    fields = list(triage[0].keys()) if triage else []
    if "user_confirm" not in fields:
        fields.append("user_confirm")
    keep_urls = {canon(r.get("url", "")) for r in picks}
    for r in triage:
        if canon(r.get("url", "")) in keep_urls:
            r["user_confirm"] = "keep"
    with triage_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in triage:
            w.writerow({k: r.get(k, "") for k in fields})

    print(f"created={len(created)} skipped={len(skipped)} total_apps={len(apps)}")
    for jid in created:
        print(f"  {jid}")
    for kind, co, role in skipped:
        print(f"  skip:{kind} {co} — {role}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
