#!/usr/bin/env python3
"""Small, dependency-free CLI for the job-search repository."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS = ROOT / "data" / "applications.csv"
NETWORKING = ROOT / "data" / "networking.csv"
ACTIVITY = ROOT / "data" / "activity_log.csv"
DASHBOARD = ROOT / "generated" / "dashboard.md"
WEEKLY = ROOT / "generated" / "weekly-review.md"

APP_FIELDS = [
    "id", "company", "role", "role_cluster", "employment_type", "location",
    "work_model", "posting_url", "source", "date_found", "date_applied",
    "status", "eligibility", "graduation_fit", "sponsorship_signal", "priority",
    "resume_version", "referral_status", "recruiter", "next_action",
    "next_action_date", "last_update", "rejection_stage", "notes",
]
CONTACT_FIELDS = [
    "contact_id", "name", "company", "role", "relation", "source",
    "profile_url", "target_job_id", "outreach_date", "follow_up_date",
    "response_status", "coffee_chat_date", "referral_status", "last_update", "notes",
]
LOG_FIELDS = ["timestamp", "job_id", "contact_id", "event_type", "from_status", "to_status", "note"]
VALID_STATUSES = {
    "discovered", "researching", "referral_requested", "ready_to_apply", "applied",
    "oa", "recruiter_screen", "technical_screen", "onsite", "offer", "rejected",
    "withdrawn", "closed",
}


def ensure_csv(path: Path, fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, fields: List[str], rows: Iterable[Dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_row(path: Path, fields: List[str], row: Dict[str, str]) -> None:
    ensure_csv(path, fields)
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields, extrasaction="ignore").writerow(row)


def next_id(prefix: str, rows: List[Dict[str, str]], field: str) -> str:
    day = date.today().strftime("%Y%m%d")
    stem = f"{prefix}{day}-"
    nums = []
    for row in rows:
        value = row.get(field, "")
        if value.startswith(stem):
            try:
                nums.append(int(value.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{stem}{max(nums, default=0) + 1:03d}"


def log_event(job_id: str = "", contact_id: str = "", event_type: str = "", from_status: str = "", to_status: str = "", note: str = "") -> None:
    append_row(ACTIVITY, LOG_FIELDS, {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "job_id": job_id,
        "contact_id": contact_id,
        "event_type": event_type,
        "from_status": from_status,
        "to_status": to_status,
        "note": note,
    })


def cmd_add_job(args: argparse.Namespace) -> None:
    rows = read_rows(APPLICATIONS)
    job_id = next_id("J", rows, "id")
    today = date.today().isoformat()
    row = {field: "" for field in APP_FIELDS}
    row.update({
        "id": job_id,
        "company": args.company,
        "role": args.role,
        "role_cluster": args.cluster,
        "employment_type": args.employment_type,
        "location": args.location,
        "work_model": args.work_model,
        "posting_url": args.url,
        "source": args.source,
        "date_found": today,
        "status": "discovered",
        "eligibility": args.eligibility,
        "graduation_fit": args.graduation_fit,
        "sponsorship_signal": args.sponsorship,
        "priority": args.priority,
        "next_action": args.next_action or "Verify eligibility and role fit",
        "next_action_date": args.next_action_date,
        "last_update": today,
        "notes": args.notes,
    })
    append_row(APPLICATIONS, APP_FIELDS, row)
    log_event(job_id=job_id, event_type="job_added", to_status="discovered", note=f"{args.company} — {args.role}")
    print(job_id)


def cmd_update_job(args: argparse.Namespace) -> None:
    rows = read_rows(APPLICATIONS)
    found = False
    today = date.today().isoformat()
    for row in rows:
        if row.get("id") != args.job_id:
            continue
        found = True
        old_status = row.get("status", "")
        updates = {
            "status": args.status,
            "eligibility": args.eligibility,
            "priority": args.priority,
            "date_applied": args.date_applied,
            "resume_version": args.resume_version,
            "referral_status": args.referral_status,
            "next_action": args.next_action,
            "next_action_date": args.next_action_date,
            "notes": args.notes,
        }
        for key, value in updates.items():
            if value is not None:
                row[key] = value
        row["last_update"] = today
        if args.status and args.status != old_status:
            log_event(job_id=args.job_id, event_type="status_changed", from_status=old_status, to_status=args.status, note=args.log_note or "")
        elif args.log_note:
            log_event(job_id=args.job_id, event_type="job_updated", note=args.log_note)
        break
    if not found:
        raise SystemExit(f"Unknown job id: {args.job_id}")
    write_rows(APPLICATIONS, APP_FIELDS, rows)
    print(args.job_id)


def cmd_add_contact(args: argparse.Namespace) -> None:
    rows = read_rows(NETWORKING)
    contact_id = next_id("C", rows, "contact_id")
    today = date.today().isoformat()
    row = {field: "" for field in CONTACT_FIELDS}
    row.update({
        "contact_id": contact_id,
        "name": args.name,
        "company": args.company,
        "role": args.role,
        "relation": args.relation,
        "source": args.source,
        "profile_url": args.profile_url,
        "target_job_id": args.target_job_id,
        "outreach_date": args.outreach_date,
        "follow_up_date": args.follow_up_date,
        "response_status": args.response_status,
        "referral_status": args.referral_status,
        "last_update": today,
        "notes": args.notes,
    })
    append_row(NETWORKING, CONTACT_FIELDS, row)
    log_event(contact_id=contact_id, job_id=args.target_job_id, event_type="contact_added", note=f"{args.name} — {args.company}")
    print(contact_id)


def parse_iso(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def overdue_actions(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    today = date.today()
    terminal = {"offer", "rejected", "withdrawn", "closed"}
    output = []
    for row in rows:
        due = parse_iso(row.get("next_action_date", ""))
        if due and due < today and row.get("status") not in terminal:
            output.append(row)
    return sorted(output, key=lambda r: r.get("next_action_date", ""))


def render_table(rows: List[Dict[str, str]], fields: List[str]) -> str:
    if not rows:
        return "_None._\n"
    header = "| " + " | ".join(fields) + " |\n"
    sep = "|" + "|".join(["---"] * len(fields)) + "|\n"
    body = "".join("| " + " | ".join((row.get(f, "") or "").replace("|", "\\|") for f in fields) + " |\n" for row in rows)
    return header + sep + body


def dashboard_text() -> str:
    apps = read_rows(APPLICATIONS)
    contacts = read_rows(NETWORKING)
    status_counts = Counter(r.get("status") or "unknown" for r in apps)
    priority_counts = Counter(r.get("priority") or "unknown" for r in apps)
    cluster_counts = Counter(r.get("role_cluster") or "unknown" for r in apps)
    active = [r for r in apps if r.get("status") not in {"offer", "rejected", "withdrawn", "closed"}]
    active = sorted(active, key=lambda r: ({"A": 0, "B": 1, "C": 2}.get(r.get("priority", ""), 9), r.get("next_action_date", "9999")))
    overdue = overdue_actions(apps)
    lines = [
        "# Job Search Dashboard\n",
        f"Generated: {datetime.now().isoformat(timespec='minutes')}\n",
        "## Summary\n",
        f"- Applications/roles tracked: **{len(apps)}**\n",
        f"- Contacts tracked: **{len(contacts)}**\n",
        f"- Applied: **{status_counts.get('applied', 0)}**\n",
        f"- Interview-stage records: **{sum(status_counts.get(s, 0) for s in ['oa', 'recruiter_screen', 'technical_screen', 'onsite'])}**\n",
        f"- Offers: **{status_counts.get('offer', 0)}**\n",
        f"- Overdue next actions: **{len(overdue)}**\n",
        "\n## By status\n",
        render_table([{"status": k, "count": str(v)} for k, v in sorted(status_counts.items())], ["status", "count"]),
        "\n## By priority\n",
        render_table([{"priority": k, "count": str(v)} for k, v in sorted(priority_counts.items())], ["priority", "count"]),
        "\n## By role cluster\n",
        render_table([{"role_cluster": k, "count": str(v)} for k, v in sorted(cluster_counts.items())], ["role_cluster", "count"]),
        "\n## Overdue next actions\n",
        render_table(overdue, ["id", "company", "role", "status", "next_action", "next_action_date"]),
        "\n## Active pipeline\n",
        render_table(active[:50], ["id", "priority", "company", "role", "status", "eligibility", "next_action", "next_action_date"]),
    ]
    return "".join(lines)


def cmd_dashboard(_: argparse.Namespace) -> None:
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD.write_text(dashboard_text(), encoding="utf-8")
    print(DASHBOARD)


def cmd_weekly(_: argparse.Namespace) -> None:
    apps = read_rows(APPLICATIONS)
    contacts = read_rows(NETWORKING)
    statuses = Counter(r.get("status") or "unknown" for r in apps)
    sources = Counter(r.get("source") or "unknown" for r in apps)
    clusters = Counter(r.get("role_cluster") or "unknown" for r in apps)
    text = [
        f"# Weekly review — {date.today().isoformat()}\n\n",
        "## Funnel facts\n\n",
        f"- Roles tracked: {len(apps)}\n",
        f"- Applications confirmed: {statuses.get('applied', 0)}\n",
        f"- OA/interview stages: {sum(statuses.get(s, 0) for s in ['oa', 'recruiter_screen', 'technical_screen', 'onsite'])}\n",
        f"- Offers: {statuses.get('offer', 0)}\n",
        f"- Rejections: {statuses.get('rejected', 0)}\n",
        f"- Contacts tracked: {len(contacts)}\n",
        f"- Overdue next actions: {len(overdue_actions(apps))}\n\n",
        "## Source sample sizes\n\n",
        render_table([{"source": k, "n": str(v)} for k, v in sources.most_common()], ["source", "n"]),
        "\n## Role-cluster sample sizes\n\n",
        render_table([{"cluster": k, "n": str(v)} for k, v in clusters.most_common()], ["cluster", "n"]),
        "\n## Observations\n\n- \n\n## Hypotheses to test\n\n- \n\n## No more than three changes\n\n1. \n2. \n3. \n\n## Next seven days\n\n- \n",
    ]
    WEEKLY.parent.mkdir(parents=True, exist_ok=True)
    WEEKLY.write_text("".join(text), encoding="utf-8")
    print(WEEKLY)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-job", help="Add a discovered job")
    p.add_argument("--company", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--cluster", default="cloud_swe")
    p.add_argument("--employment-type", default="new_grad")
    p.add_argument("--location", default="")
    p.add_argument("--work-model", default="")
    p.add_argument("--eligibility", choices=["verified", "likely", "unclear", "ineligible"], default="unclear")
    p.add_argument("--graduation-fit", default="")
    p.add_argument("--sponsorship", default="unclear")
    p.add_argument("--priority", choices=["A", "B", "C"], default="B")
    p.add_argument("--next-action", default="")
    p.add_argument("--next-action-date", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add_job)

    p = sub.add_parser("update-job", help="Update an existing job")
    p.add_argument("job_id")
    p.add_argument("--status", choices=sorted(VALID_STATUSES))
    p.add_argument("--eligibility", choices=["verified", "likely", "unclear", "ineligible"])
    p.add_argument("--priority", choices=["A", "B", "C"])
    p.add_argument("--date-applied")
    p.add_argument("--resume-version")
    p.add_argument("--referral-status")
    p.add_argument("--next-action")
    p.add_argument("--next-action-date")
    p.add_argument("--notes")
    p.add_argument("--log-note")
    p.set_defaults(func=cmd_update_job)

    p = sub.add_parser("add-contact", help="Add a networking contact")
    p.add_argument("--name", required=True)
    p.add_argument("--company", required=True)
    p.add_argument("--role", default="")
    p.add_argument("--relation", default="")
    p.add_argument("--source", default="LinkedIn")
    p.add_argument("--profile-url", default="")
    p.add_argument("--target-job-id", default="")
    p.add_argument("--outreach-date", default="")
    p.add_argument("--follow-up-date", default="")
    p.add_argument("--response-status", default="not_contacted")
    p.add_argument("--referral-status", default="not_requested")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add_contact)

    p = sub.add_parser("dashboard", help="Generate dashboard markdown")
    p.set_defaults(func=cmd_dashboard)

    p = sub.add_parser("weekly", help="Generate weekly review template with current counts")
    p.set_defaults(func=cmd_weekly)
    return parser


def main() -> int:
    ensure_csv(APPLICATIONS, APP_FIELDS)
    ensure_csv(NETWORKING, CONTACT_FIELDS)
    ensure_csv(ACTIVITY, LOG_FIELDS)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
