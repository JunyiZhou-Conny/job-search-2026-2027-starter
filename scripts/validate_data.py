#!/usr/bin/env python3
"""Validate job-search CSV integrity; write review queue for issues."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, APPLIED_PLUS, CONTACTS, HARD_ELIG, INTERVIEW_PLUS, LANES,
    NETWORKING, PRIORITIES, RESUME_VERSIONS, REVIEW_QUEUE, SPONSORSHIP,
    TERMINAL, VALID_STATUSES, ensure_csv, log, parse_iso, read_rows, sync_app_aliases,
    write_rows,
)

ISSUE_FIELDS = ["entity", "id", "field", "severity", "message"]


def validate_apps() -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    rows = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    ids = []
    for row in rows:
        jid = row.get("job_id") or row.get("id") or ""
        if not jid:
            issues.append({"entity": "application", "id": "", "field": "job_id", "severity": "error",
                           "message": "Missing job_id"})
            continue
        if jid in ids:
            issues.append({"entity": "application", "id": jid, "field": "job_id", "severity": "error",
                           "message": "Duplicate job_id"})
        ids.append(jid)

        st = row.get("status") or ""
        if st and st not in VALID_STATUSES:
            issues.append({"entity": "application", "id": jid, "field": "status", "severity": "error",
                           "message": f"Invalid status '{st}'"})

        if st in APPLIED_PLUS or st == "applied":
            if not row.get("date_applied"):
                issues.append({"entity": "application", "id": jid, "field": "date_applied", "severity": "error",
                               "message": "applied+ missing date_applied"})
            if not row.get("resume_version"):
                issues.append({"entity": "application", "id": jid, "field": "resume_version", "severity": "error",
                               "message": "applied+ missing resume_version"})

        if st not in TERMINAL:
            if not (row.get("next_action") or "").strip():
                issues.append({"entity": "application", "id": jid, "field": "next_action", "severity": "error",
                               "message": "active row missing next_action"})

        he = row.get("hard_eligibility") or ""
        if he and he not in HARD_ELIG:
            issues.append({"entity": "application", "id": jid, "field": "hard_eligibility", "severity": "error",
                           "message": f"Invalid hard_eligibility '{he}'"})

        sp = row.get("sponsorship_signal") or ""
        if sp and sp not in SPONSORSHIP:
            issues.append({"entity": "application", "id": jid, "field": "sponsorship_signal", "severity": "warn",
                           "message": f"Unexpected sponsorship_signal '{sp}'"})

        lane = row.get("pursuit_lane") or ""
        if lane and lane not in LANES:
            issues.append({"entity": "application", "id": jid, "field": "pursuit_lane", "severity": "error",
                           "message": f"Invalid pursuit_lane '{lane}'"})

        pr = row.get("priority") or ""
        if pr and pr not in PRIORITIES:
            issues.append({"entity": "application", "id": jid, "field": "priority", "severity": "error",
                           "message": f"Invalid priority '{pr}'"})

        # date order checks
        d_app = parse_iso(row.get("date_applied", ""))
        d_disc = parse_iso(row.get("date_discovered") or row.get("date_found") or "")
        if d_app and d_disc and d_app < d_disc:
            issues.append({"entity": "application", "id": jid, "field": "date_applied", "severity": "warn",
                           "message": "date_applied before date_discovered"})

        if row.get("label_source") == "manual" and row.get("needs_review") == "true":
            issues.append({"entity": "application", "id": jid, "field": "needs_review", "severity": "info",
                           "message": "manual label flagged needs_review — human owns resolution"})

        if st in INTERVIEW_PLUS:
            # soft: encourage stage dates
            pass

    return issues


def validate_contacts() -> List[Dict[str, str]]:
    issues = []
    rows = read_rows(CONTACTS)
    ids = []
    for row in rows:
        cid = row.get("contact_id") or ""
        if not cid:
            continue
        if cid in ids:
            issues.append({"entity": "contact", "id": cid, "field": "contact_id", "severity": "error",
                           "message": "Duplicate contact_id"})
        ids.append(cid)
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict", action="store_true", help="exit 1 on any error-severity issue")
    args = p.parse_args()

    issues = validate_apps() + validate_contacts()
    REVIEW_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    write_rows(REVIEW_QUEUE, ISSUE_FIELDS, issues)

    errors = [i for i in issues if i["severity"] == "error"]
    warns = [i for i in issues if i["severity"] == "warn"]
    log(f"validate: errors={len(errors)} warnings={len(warns)} total={len(issues)} → {REVIEW_QUEUE}")
    for i in issues[:20]:
        log(f"  {i['severity']}: {i['entity']} {i['id']} {i['field']}: {i['message']}")
    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
