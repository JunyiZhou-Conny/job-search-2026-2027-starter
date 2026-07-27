#!/usr/bin/env python3
"""Durable write-back for apply-queue decisions.

Single place where queue actions become repo state, so the live server and the
batch JSON import cannot drift apart.

Two actions:
  record_pass(rows)     → data/job_decisions.csv + status=passed
  record_applied(rows)  → status=applied (+ creates the application row if the
                          role only existed in a triage CSV)

A queue row looks like:
  {url, company, role, job_id, cluster, lane, location, source,
   reason (pass only), resume_version (applied only), decided_at}
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    ACTIVITY,
    APPLICATIONS,
    APP_FIELDS,
    BACKUPS,
    DATA,
    LOG_FIELDS,
    RESUME_VERSIONS,
    ensure_csv,
    next_id,
    now_iso,
    read_rows,
    sync_app_aliases,
    today_iso,
    write_rows,
)

DECISIONS = DATA / "job_decisions.csv"
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

# Statuses that a queue click must never downgrade.
PIPELINE_ACTIVE = {
    "applied",
    "oa",
    "recruiter_screen",
    "technical_screen",
    "onsite",
    "final_round",
    "offer",
    "accepted",
}

FALLBACK_CLUSTER_RESUME = {
    "cloud_swe": "2026-07-20_cloud-swe_v1.1",
    "data_ml": "2026-07-20_data-ml_v1.1",
    "health_ai": "2026-07-20_health-ai_v1.1",
}

LANE_PRIORITY = {"core": "A", "broad": "B", "practice": "C"}


def canon(url: str) -> str:
    return (url or "").strip().split("?")[0].rstrip("/").lower()


def default_resume_for_cluster(cluster: str) -> str:
    """Newest active resume registered for this cluster, else a known fallback."""
    cluster = (cluster or "").strip()
    if not cluster:
        return ""
    candidates = [
        r
        for r in read_rows(RESUME_VERSIONS)
        if (r.get("cluster") or "").strip() == cluster
        and (r.get("active") or "").strip().lower() in {"true", "1", "yes"}
    ]
    if candidates:
        candidates.sort(key=lambda r: r.get("created_date") or "", reverse=True)
        return candidates[0].get("resume_version") or ""
    return FALLBACK_CLUSTER_RESUME.get(cluster, "")


def _index(apps: list[dict]) -> tuple[dict, dict]:
    by_url: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    for r in apps:
        for key in ("job_url", "posting_url"):
            u = canon(r.get(key, ""))
            if u:
                by_url[u] = r
        if r.get("job_id"):
            by_id[r["job_id"]] = r
    return by_url, by_id


def _find(apps: list[dict], row: dict) -> dict | None:
    by_url, by_id = _index(apps)
    jid = (row.get("job_id") or "").strip()
    if jid and jid in by_id:
        return by_id[jid]
    return by_url.get(canon(row.get("url", "")))


def _save_apps(apps: list[dict]) -> None:
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = now_iso().replace(":", "").replace("-", "")[:15]
    if APPLICATIONS.exists():
        (BACKUPS / f"applications_{stamp}.csv").write_text(
            APPLICATIONS.read_text(encoding="utf-8"), encoding="utf-8"
        )
    write_rows(APPLICATIONS, APP_FIELDS, [sync_app_aliases(a) for a in apps])


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


def _create_app(apps: list[dict], row: dict) -> dict:
    """Create an application row for a role that only existed in a triage CSV."""
    job_id = next_id("J", apps, "id")
    url = (row.get("url") or "").split("?")[0]
    cluster = (row.get("cluster") or "").strip()
    lane = (row.get("lane") or "").strip()
    today = today_iso()
    app = {field: "" for field in APP_FIELDS}
    app.update(
        {
            "id": job_id,
            "job_id": job_id,
            "company": row.get("company") or "",
            "role": row.get("role") or "",
            "job_url": url,
            "posting_url": url,
            "source": row.get("source") or "apply_queue",
            "source_detail": "apply_queue",
            "location": row.get("location") or "",
            "employment_type": "internship" if "intern" in (row.get("role") or "").lower() else "new_grad",
            "role_cluster": cluster,
            "date_discovered": today,
            "date_found": today,
            "status": "discovered",
            "application_status": "discovered",
            "pursuit_lane": lane,
            "priority": LANE_PRIORITY.get(lane, "B"),
            "eligibility": "unclear",
            "hard_eligibility": "uncertain",
            "sponsorship_signal": "unclear",
            "auth_work_authorized": "not_asked",
            "auth_needs_sponsorship": "not_asked",
            "label_source": "apply_queue",
            "needs_review": "false",
            "created_at": today,
            "updated_at": today,
            "last_update": today,
        }
    )
    app = sync_app_aliases(app)
    apps.append(app)
    return app


def record_pass(rows: list[dict]) -> dict:
    """Archive Pass decisions by URL and mark any matching application passed."""
    ensure_csv(DECISIONS, DECISION_FIELDS)
    existing = read_rows(DECISIONS)
    by_url = {canon(r.get("url", "")): r for r in existing if r.get("url")}
    added = updated = 0

    for row in rows:
        url = (row.get("url") or "").strip()
        if not url:
            continue
        key = canon(url)
        rec = {
            "url": url.split("?")[0],
            "company": row.get("company") or "",
            "role": row.get("role") or "",
            "job_id": row.get("job_id") or "",
            "decision": (row.get("decision") or "pass").strip().lower() or "pass",
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

    apps = read_rows(APPLICATIONS)
    changed = 0
    stamp = now_iso()
    for row in rows:
        if (row.get("decision") or "pass").lower() != "pass":
            continue
        app = _find(apps, row)
        if not app:
            continue
        old = (app.get("status") or "").strip()
        if old in PIPELINE_ACTIVE:
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
        _save_apps(apps)
    return {"decisions_added": added, "decisions_updated": updated, "applications_updated": changed}


def record_applied(rows: list[dict], follow_up_days: int = 7) -> dict:
    """Mark roles applied. Creates the application row when it does not exist yet."""
    apps = read_rows(APPLICATIONS)
    created: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    stamp = now_iso()
    today = today_iso()
    follow_up = (date.today() + timedelta(days=follow_up_days)).isoformat()

    for row in rows:
        if not (row.get("url") or "").strip():
            continue
        app = _find(apps, row)
        if app is None:
            app = _create_app(apps, row)
            created.append(app["job_id"])

        old = (app.get("status") or "").strip()
        if old in PIPELINE_ACTIVE:
            unchanged.append(app.get("job_id") or "")
            continue

        cluster = (row.get("cluster") or app.get("role_cluster") or "").strip()
        resume = (
            (row.get("resume_version") or "").strip()
            or (app.get("resume_version") or "").strip()
            or default_resume_for_cluster(cluster)
        )

        app["status"] = "applied"
        app["application_status"] = "applied"
        app["stage_current"] = "applied"
        app["stage_highest_reached"] = "applied"
        app["date_applied"] = (row.get("decided_at") or today)[:10]
        if resume:
            app["resume_version"] = resume
        if cluster and not app.get("role_cluster"):
            app["role_cluster"] = cluster
        if row.get("lane") and not app.get("pursuit_lane"):
            app["pursuit_lane"] = row["lane"]
        app["next_action"] = "Confirm in Simplify ledger; follow up if no reply"
        app["next_action_date"] = follow_up
        app["notes"] = (
            (app.get("notes") or "").rstrip() + f" | applied via apply queue ({resume or 'resume unrecorded'})"
        ).strip(" |")
        app["updated_at"] = stamp
        app["last_update"] = stamp
        log_event(
            app.get("job_id") or "",
            old or "unknown",
            "applied",
            f"{app.get('company')} — {app.get('role')}",
        )
        updated.append(app.get("job_id") or "")

    if created or updated:
        _save_apps(apps)
    return {
        "created": created,
        "applied": updated,
        "already_in_pipeline": unchanged,
    }


def applied_urls() -> set[str]:
    """URLs already applied or further along — used to hydrate queue checkboxes."""
    out: set[str] = set()
    for r in read_rows(APPLICATIONS):
        if (r.get("status") or "").strip().lower() in PIPELINE_ACTIVE:
            u = canon(r.get("job_url") or r.get("posting_url") or "")
            if u:
                out.add(u)
    return out


def passed_records() -> list[dict]:
    return [r for r in read_rows(DECISIONS) if (r.get("decision") or "").lower() == "pass"]
