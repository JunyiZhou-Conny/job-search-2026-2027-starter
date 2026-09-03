#!/usr/bin/env python3
"""Attempt-level ledger for autonomous applies.

`data/applications.csv` stays the current-state ledger. This module adds an
append-only attempt table, `data/apply_attempts.csv`, so that "Submit was
clicked", "the banner said success", and "the tracker shows Applied" are
recorded as separate facts, and so a rerun can refuse to apply twice.

    precheck  -> is this posting already applied, attempted, passed, or closed
    start     -> open an attempt (creates the application row if needed)
    finish    -> close the attempt with an outcome and evidence, update status
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import js_lib  # noqa: E402
from js_lib import (  # noqa: E402
    APP_FIELDS, APPLIED_PLUS, LOG_FIELDS, canonical_url, company_role_key,
    ensure_csv, next_id, now_iso, read_rows, sync_app_aliases, today_iso, write_rows,
)

ATTEMPT_FIELDS = [
    "attempt_id", "job_id", "run_id", "started_at", "ended_at", "ats", "apply_url",
    "gate", "weight", "outcome", "banner_text", "tracker_status", "email_evidence",
    "application_id", "resume_version", "answers_used", "screens_dir", "agent_url", "notes",
]

OUTCOMES = {
    "in_progress",
    "submitted_verified",   # success banner plus an independent signal (tracker or email)
    "submitted_unverified", # Submit clicked, banner seen, no second signal yet
    "submit_failed",        # spam wall or error after Submit
    "blocked",              # stop-the-line rule fired before Submit
    "review_packet",        # prioritized row prepared and handed to the human
    "posting_closed",
    "not_run",
}

DECISION_FIELDS = ["url", "company", "role", "job_id", "decision", "reason", "decided_at", "source"]


class Ledger:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data = Path(data_dir) if data_dir else js_lib.DATA
        self.applications = self.data / "applications.csv"
        self.attempts = self.data / "apply_attempts.csv"
        self.decisions = self.data / "job_decisions.csv"
        self.log = self.data / "activity_log.csv"
        ensure_csv(self.applications, APP_FIELDS)
        ensure_csv(self.attempts, ATTEMPT_FIELDS)
        ensure_csv(self.decisions, DECISION_FIELDS)
        ensure_csv(self.log, LOG_FIELDS)

    def _append_log(self, job_id: str, event: str, frm: str, to: str, note: str) -> None:
        rows = read_rows(self.log)
        rows.append({"timestamp": now_iso(), "job_id": job_id, "contact_id": "",
                     "event_type": event, "from_status": frm, "to_status": to, "note": note})
        write_rows(self.log, LOG_FIELDS, rows)

    def precheck(self, url: str, company: str, role: str, stale_hours: int = 24) -> Dict:
        key_url = canonical_url(url)
        key_cr = company_role_key(company, role)
        matches: List[Dict] = []
        for r in read_rows(self.applications):
            same_url = key_url and canonical_url(r.get("job_url", "")) == key_url
            same_cr = company_role_key(r.get("company", ""), r.get("role", "")) == key_cr
            if not (same_url or same_cr):
                continue
            st = r.get("status", "")
            blocking = st in APPLIED_PLUS or st in {"passed", "closed", "withdrawn"}
            matches.append({"table": "applications", "job_id": r["id"], "status": st,
                            "by": "url" if same_url else "company_role", "blocking": blocking})
        for r in read_rows(self.decisions):
            if key_url and canonical_url(r.get("url", "")) == key_url:
                matches.append({"table": "job_decisions", "job_id": r.get("job_id", ""),
                                "status": r.get("decision", ""), "by": "url", "blocking": True})
        for r in self._simplify_rows():
            same_url = key_url and canonical_url(r["url"]) == key_url
            same_cr = company_role_key(r["company"], r["title"]) == key_cr
            if same_url or same_cr:
                st = r["status"].strip().lower()
                matches.append({"table": "simplify_tracker", "job_id": "", "status": st,
                                "by": "url" if same_url else "company_role",
                                "blocking": st not in {"", "saved", "screening_saved"},
                                "source_file": r["source_file"]})
        cutoff = datetime.now() - timedelta(hours=stale_hours)
        for r in read_rows(self.attempts):
            if key_url and canonical_url(r.get("apply_url", "")) != key_url:
                continue
            if not key_url:
                continue
            outcome = r.get("outcome", "")
            started = datetime.fromisoformat(r["started_at"]) if r.get("started_at") else cutoff
            live = outcome == "in_progress" and started > cutoff
            done = outcome in {"submitted_verified", "submitted_unverified"}
            if live or done:
                matches.append({"table": "apply_attempts", "job_id": r.get("job_id", ""),
                                "status": outcome, "by": "url", "blocking": True,
                                "attempt_id": r["attempt_id"]})
        return {"duplicate": any(m["blocking"] for m in matches), "matches": matches}

    def _simplify_rows(self) -> List[Dict[str, str]]:
        """Rows from the newest Simplify export. Both export shapes are read:
        the site download (Job Title, Company Name, Job URL, Status) and the
        older scrape (Title, Company, URL, Status)."""
        folder = self.data / "imports" / "simplify"
        files = sorted(folder.glob("*.csv")) if folder.exists() else []
        if not files:
            return []
        latest = files[-1]
        out = []
        for r in read_rows(latest):
            out.append({
                "url": r.get("Job URL") or r.get("URL") or "",
                "company": r.get("Company Name") or r.get("Company") or "",
                "title": r.get("Job Title") or r.get("Title") or "",
                "status": r.get("Status") or "",
                "source_file": latest.name,
            })
        return out

    def close_posting(self, *, url: str, company: str, role: str, reason: str, source: str) -> Dict:
        decisions = read_rows(self.decisions)
        key = canonical_url(url)
        if any(canonical_url(d.get("url", "")) == key and d.get("decision") == "closed" for d in decisions):
            return {"decision": "closed", "already_recorded": True}
        app = self._find_app(url, company, role)
        decisions.append({"url": url, "company": company, "role": role, "job_id": app["id"] if app else "",
                          "decision": "closed", "reason": reason, "decided_at": now_iso(), "source": source})
        write_rows(self.decisions, DECISION_FIELDS, decisions)
        self._append_log(app["id"] if app else "", "posting_closed", "", "closed", f"{company} — {role}: {reason}")
        return {"decision": "closed", "already_recorded": False}

    def _find_app(self, url: str, company: str, role: str) -> Optional[Dict[str, str]]:
        key_url, key_cr = canonical_url(url), company_role_key(company, role)
        for r in read_rows(self.applications):
            if (key_url and canonical_url(r.get("job_url", "")) == key_url) or \
               company_role_key(r.get("company", ""), r.get("role", "")) == key_cr:
                return r
        return None

    def start(self, *, url: str, company: str, role: str, ats: str, gate: str, weight: str,
              run_id: str, source: str, pursuit_lane: str, role_cluster: str,
              agent_url: str = "", allow_duplicate: bool = False) -> Dict:
        check = self.precheck(url, company, role)
        if check["duplicate"] and not allow_duplicate:
            raise SystemExit(json.dumps({"error": "duplicate", **check}))
        apps = read_rows(self.applications)
        app = self._find_app(url, company, role)
        if app is None:
            app = sync_app_aliases({
                "id": next_id("J", apps, "id"), "company": company, "role": role, "job_url": url,
                "source": source, "role_cluster": role_cluster, "date_discovered": today_iso(),
                "status": "ready_to_apply", "pursuit_lane": pursuit_lane,
                "label_source": "manual", "needs_review": "false",
                "created_at": today_iso(), "updated_at": today_iso(),
            })
            apps.append(app)
            write_rows(self.applications, APP_FIELDS, apps)
            self._append_log(app["id"], "job_added", "", "ready_to_apply", f"{company} — {role} ({source})")
        attempts = read_rows(self.attempts)
        attempt = {k: "" for k in ATTEMPT_FIELDS}
        attempt.update({
            "attempt_id": next_id("A", attempts, "attempt_id"), "job_id": app["id"], "run_id": run_id,
            "started_at": now_iso(), "ats": ats, "apply_url": url, "gate": gate, "weight": weight,
            "outcome": "in_progress", "agent_url": agent_url,
        })
        attempts.append(attempt)
        write_rows(self.attempts, ATTEMPT_FIELDS, attempts)
        self._append_log(app["id"], "submit_attempt_started", app.get("status", ""), "",
                         f"attempt {attempt['attempt_id']} gate={gate} weight={weight} ats={ats}")
        return {"attempt_id": attempt["attempt_id"], "job_id": app["id"]}

    def finish(self, *, attempt_id: str, outcome: str, banner_text: str = "", tracker_status: str = "",
               email_evidence: str = "", application_id: str = "", resume_version: str = "",
               answers_used: str = "", screens_dir: str = "", notes: str = "",
               next_action: str = "", next_action_date: str = "") -> Dict:
        if outcome not in OUTCOMES:
            raise SystemExit(f"unknown outcome {outcome}; choose from {sorted(OUTCOMES)}")
        attempts = read_rows(self.attempts)
        attempt = next((a for a in attempts if a["attempt_id"] == attempt_id), None)
        if attempt is None:
            raise SystemExit(f"no attempt {attempt_id}")
        if outcome == "submitted_verified" and not banner_text:
            raise SystemExit("submitted_verified needs banner_text")
        if outcome == "submitted_verified" and not (tracker_status or email_evidence or application_id):
            raise SystemExit("submitted_verified needs a second signal: tracker_status, email_evidence, or application_id")
        attempt.update({
            "ended_at": now_iso(), "outcome": outcome, "banner_text": banner_text,
            "tracker_status": tracker_status, "email_evidence": email_evidence,
            "application_id": application_id, "resume_version": resume_version,
            "answers_used": answers_used, "screens_dir": screens_dir, "notes": notes,
        })
        write_rows(self.attempts, ATTEMPT_FIELDS, attempts)

        apps = read_rows(self.applications)
        app = next(a for a in apps if a["id"] == attempt["job_id"])
        before = app.get("status", "")
        after = before
        if outcome in {"submitted_verified", "submitted_unverified"}:
            after = "applied"
            app["date_applied"] = app.get("date_applied") or today_iso()
            if resume_version:
                app["resume_version"] = resume_version
        elif outcome == "posting_closed":
            after = "closed"
            decisions = read_rows(self.decisions)
            decisions.append({"url": attempt["apply_url"], "company": app["company"], "role": app["role"],
                              "job_id": app["id"], "decision": "closed", "reason": notes or "posting closed at apply time",
                              "decided_at": now_iso(), "source": "apply_ledger"})
            write_rows(self.decisions, DECISION_FIELDS, decisions)
        app["status"] = app["application_status"] = after
        app["stage_current"] = after
        app["stage_highest_reached"] = js_lib.bump_highest(app.get("stage_highest_reached", ""), after)
        if next_action:
            app["next_action"] = next_action
            app["next_action_date"] = next_action_date
        elif outcome == "submitted_verified":
            app["next_action"] = "Watch inbox and Simplify tracker for a response"
            app["next_action_date"] = (datetime.now() + timedelta(days=10)).date().isoformat()
        app["updated_at"] = app["last_update"] = today_iso()
        note = f"attempt {attempt_id} {outcome}"
        if banner_text:
            note += f"; banner: {banner_text[:120]}"
        if tracker_status:
            note += f"; tracker: {tracker_status}"
        app["notes"] = (app.get("notes", "") + " | " if app.get("notes") else "") + note
        write_rows(self.applications, APP_FIELDS, apps)
        self._append_log(app["id"], "status_changed" if after != before else "submit_attempt_finished",
                         before, after, note)
        return {"job_id": app["id"], "status": after, "outcome": outcome}


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, default=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("precheck", help="exit 3 if the posting is already applied, attempted, passed, or closed")
    a.add_argument("--url", required=True)
    a.add_argument("--company", required=True)
    a.add_argument("--role", required=True)

    b = sub.add_parser("start", help="open an attempt; refuses duplicates")
    b.add_argument("--url", required=True)
    b.add_argument("--company", required=True)
    b.add_argument("--role", required=True)
    b.add_argument("--ats", required=True, choices=["ashby", "greenhouse", "lever", "workday", "other"])
    b.add_argument("--gate", required=True, choices=["G0", "G1", "G2", "G3"])
    b.add_argument("--weight", required=True, choices=["regular", "prioritized"])
    b.add_argument("--run-id", required=True)
    b.add_argument("--source", default="apply_run")
    b.add_argument("--pursuit-lane", default="broad", choices=["core", "broad", "practice"])
    b.add_argument("--role-cluster", default="")
    b.add_argument("--agent-url", default="")
    b.add_argument("--allow-duplicate", action="store_true")

    c = sub.add_parser("finish", help="record the outcome and evidence of an attempt")
    c.add_argument("--attempt-id", required=True)
    c.add_argument("--outcome", required=True, choices=sorted(OUTCOMES - {"in_progress"}))
    for name in ("banner-text", "tracker-status", "email-evidence", "application-id", "resume-version",
                 "answers-used", "screens-dir", "notes", "next-action", "next-action-date"):
        c.add_argument(f"--{name}", default="")

    d = sub.add_parser("close-posting", help="record a closed or vanished apply URL so no run resurfaces it")
    d.add_argument("--url", required=True)
    d.add_argument("--company", required=True)
    d.add_argument("--role", required=True)
    d.add_argument("--reason", required=True)
    d.add_argument("--source", default="apply_precheck")

    args = p.parse_args(argv)
    ledger = Ledger(args.data_dir)
    if args.cmd == "close-posting":
        print(json.dumps(ledger.close_posting(url=args.url, company=args.company, role=args.role,
                                              reason=args.reason, source=args.source)))
        return 0
    if args.cmd == "precheck":
        result = ledger.precheck(args.url, args.company, args.role)
        print(json.dumps(result, indent=2))
        return 3 if result["duplicate"] else 0
    if args.cmd == "start":
        print(json.dumps(ledger.start(
            url=args.url, company=args.company, role=args.role, ats=args.ats, gate=args.gate,
            weight=args.weight, run_id=args.run_id, source=args.source, pursuit_lane=args.pursuit_lane,
            role_cluster=args.role_cluster, agent_url=args.agent_url, allow_duplicate=args.allow_duplicate)))
        return 0
    if args.cmd == "finish":
        print(json.dumps(ledger.finish(
            attempt_id=args.attempt_id, outcome=args.outcome, banner_text=args.banner_text,
            tracker_status=args.tracker_status, email_evidence=args.email_evidence,
            application_id=args.application_id, resume_version=args.resume_version,
            answers_used=args.answers_used, screens_dir=args.screens_dir, notes=args.notes,
            next_action=args.next_action, next_action_date=args.next_action_date)))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
