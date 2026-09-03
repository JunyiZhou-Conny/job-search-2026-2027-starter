"""CLI for applications, contacts, Simplify import, and dashboards."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APP_FIELDS, APPLICATIONS, ACTIVITY, HARD_ELIG, LANES, LEGACY_NETWORKING_FIELDS,
    LOG_FIELDS, NETWORKING, SPONSORSHIP, TERMINAL, VALID_STATUSES, bump_highest,
    canonical_url, company_role_key, ensure_csv, map_sponsorship, now_iso,
    read_rows, sync_app_aliases, today_iso, write_rows
)

# append_row may not exist in js_lib — keep local
NETWORKING_FIELDS = LEGACY_NETWORKING_FIELDS
DASHBOARD = ROOT / "generated" / "dashboard.md"
WEEKLY = ROOT / "generated" / "weekly-review.md"
IMPORTS_DIR = ROOT / "data" / "imports" / "simplify"

CONTACT_FIELDS = NETWORKING_FIELDS
VALID_PURSUIT_LANES = LANES
VALID_ELIGIBILITY = {"verified", "likely", "unclear", "ineligible"} | HARD_ELIG
VALID_SPONSORSHIP = SPONSORSHIP
VALID_AUTH_ANSWER = {"yes", "no", "unknown", "not_asked"}
INTERVIEW_STAGES = {"oa", "recruiter_screen", "technical_screen", "onsite", "final_round", "offer", "accepted"}
APPLIED_OR_LATER = {"applied"} | INTERVIEW_STAGES | {"rejected"}



def append_row(path: Path, fields: List[str], row: Dict[str, str]) -> None:
    ensure_csv(path, fields)
    with path.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=fields, extrasaction="ignore").writerow(row)


# Simplify and common tracker export aliases → local field
SIMPLIFY_ALIASES = {
    "company": ["company", "company name", "employer"],
    "role": ["role", "title", "job title", "position", "job"],
    "posting_url": ["posting_url", "url", "job url", "link", "job link", "posting", "application url"],
    "location": ["location", "job location", "city"],
    "date_applied": ["date_applied", "applied", "date applied", "applied date", "application date"],
    "status": ["status", "application status", "stage", "pipeline status"],
    "notes": ["notes", "note", "comments"],
    "source": ["source", "board", "job board"],
}

STATUS_MAP = {
    "saved": "discovered",
    "wishlist": "discovered",
    "bookmarked": "discovered",
    "interested": "discovered",
    "discovered": "discovered",
    "researching": "researching",
    "preparing": "ready_to_apply",
    "ready": "ready_to_apply",
    "ready to apply": "ready_to_apply",
    "applied": "applied",
    "application submitted": "applied",
    "submitted": "applied",
    "oa": "oa",
    "online assessment": "oa",
    "assessment": "oa",
    "phone screen": "recruiter_screen",
    "recruiter screen": "recruiter_screen",
    "recruiter": "recruiter_screen",
    "hiring manager": "technical_screen",
    "technical": "technical_screen",
    "technical screen": "technical_screen",
    "interview": "technical_screen",
    "onsite": "onsite",
    "final": "onsite",
    "offer": "offer",
    "rejected": "rejected",
    "rejected / archived": "rejected",
    "archived": "closed",
    "ghosted": "closed",
    "withdrawn": "withdrawn",
    "closed": "closed",
}


def migrate_applications() -> None:
    """Rewrite applications.csv to the current schema without dropping values."""
    ensure_csv(APPLICATIONS, APP_FIELDS)
    rows = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    write_rows(APPLICATIONS, APP_FIELDS, rows)


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


def log_event(
    job_id: str = "",
    contact_id: str = "",
    event_type: str = "",
    from_status: str = "",
    to_status: str = "",
    note: str = "",
) -> None:
    append_row(ACTIVITY, LOG_FIELDS, {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "job_id": job_id,
        "contact_id": contact_id,
        "event_type": event_type,
        "from_status": from_status,
        "to_status": to_status,
        "note": note,
    })


def normalize_key(company: str, role: str) -> str:
    def clean(text: str) -> str:
        text = (text or "").lower().strip()
        return re.sub(r"\s+", " ", text)

    return f"{clean(company)}|{clean(role)}"


def pick_alias(row: Dict[str, str], field: str) -> str:
    lowered = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
    for alias in SIMPLIFY_ALIASES.get(field, []):
        if lowered.get(alias):
            return lowered[alias]
    return ""


def map_simplify_status(raw: str) -> str:
    key = (raw or "").strip().lower()
    if not key:
        return "applied"
    if key in VALID_STATUSES:
        return key
    return STATUS_MAP.get(key, "applied")


def cmd_add_job(args: argparse.Namespace) -> None:
    rows = read_rows(APPLICATIONS)
    job_id = next_id("J", rows, "id")
    today = date.today().isoformat()
    lane = args.pursuit_lane or ""
    row = {field: "" for field in APP_FIELDS}
    row.update({
        "id": job_id,
        "job_id": job_id,
        "company": args.company,
        "role": args.role,
        "role_cluster": args.cluster,
        "employment_type": args.employment_type,
        "location": args.location,
        "work_model": args.work_model,
        "posting_url": args.url,
        "job_url": args.url,
        "source": args.source,
        "date_found": today,
        "date_discovered": today,
        "status": "discovered",
        "application_status": "discovered",
        "eligibility": args.eligibility,
        "graduation_fit": args.graduation_fit,
        "sponsorship_signal": map_sponsorship(args.sponsorship),
        "pursuit_lane": lane,
        "priority": args.priority,
        "auth_work_authorized": "not_asked",
        "auth_needs_sponsorship": "not_asked",
        "label_source": "manual" if lane else "",
        "needs_review": "false",
        "next_action": args.next_action or "Verify hard eligibility and assign pursuit lane",
        "next_action_date": args.next_action_date,
        "last_update": today,
        "created_at": today,
        "updated_at": today,
        "notes": args.notes,
    })
    row = sync_app_aliases(row)
    append_row(APPLICATIONS, APP_FIELDS, row)
    log_event(job_id=job_id, event_type="job_added", to_status="discovered", note=f"{args.company} — {args.role}")
    print(job_id)


def cmd_update_job(args: argparse.Namespace) -> None:
    rows = read_rows(APPLICATIONS)
    found = False
    today = date.today().isoformat()
    for row in rows:
        if (row.get("id") or row.get("job_id")) != args.job_id:
            continue
        found = True
        old_status = row.get("status", "")
        updates = {
            "status": args.status,
            "eligibility": args.eligibility,
            "priority": args.priority,
            "pursuit_lane": args.pursuit_lane,
            "sponsorship_signal": map_sponsorship(args.sponsorship) if args.sponsorship else None,
            "date_applied": args.date_applied,
            "resume_version": args.resume_version,
            "referral_status": args.referral_status,
            "auth_work_authorized": args.auth_work_authorized,
            "auth_needs_sponsorship": args.auth_needs_sponsorship,
            "auth_qa_notes": args.auth_qa_notes,
            "next_action": args.next_action,
            "next_action_date": args.next_action_date,
            "notes": args.notes,
            "label_source": "manual",
        }
        for key, value in updates.items():
            if value is not None:
                if key == "pursuit_lane" and value and value not in VALID_PURSUIT_LANES:
                    raise SystemExit(f"Invalid pursuit_lane: {value}")
                if key in ("auth_work_authorized", "auth_needs_sponsorship") and value not in VALID_AUTH_ANSWER:
                    raise SystemExit(f"Invalid {key}: {value}")
                row[key] = value
        if args.status:
            row["application_status"] = args.status
            row["stage_highest_reached"] = bump_highest(row.get("stage_highest_reached", ""), args.status)
        row["last_update"] = today
        row["updated_at"] = today
        if args.status and args.status != old_status:
            log_event(
                job_id=args.job_id,
                event_type="status_changed",
                from_status=old_status,
                to_status=args.status,
                note=args.log_note or "",
            )
        elif args.log_note:
            log_event(job_id=args.job_id, event_type="job_updated", note=args.log_note)
        break
    if not found:
        raise SystemExit(f"Unknown job id: {args.job_id}")
    write_rows(APPLICATIONS, APP_FIELDS, [sync_app_aliases(r) for r in rows])
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


def find_match(apps: List[Dict[str, str]], url: str, company: str, role: str) -> Optional[Dict[str, str]]:
    norm_url = canonical_url(url)
    if norm_url:
        for row in apps:
            if canonical_url(row.get("posting_url", "")) == norm_url:
                return row
    key = normalize_key(company, role)
    if company and role:
        for row in apps:
            if normalize_key(row.get("company", ""), row.get("role", "")) == key:
                return row
    return None


def cmd_import_simplify(args: argparse.Namespace) -> None:
    path = Path(args.file)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    with path.open(newline="", encoding="utf-8-sig") as f:
        incoming = list(csv.DictReader(f))
    if not incoming:
        print("No rows in import file.")
        return

    apps = read_rows(APPLICATIONS)
    today = date.today().isoformat()
    created = updated = skipped = 0

    for raw in incoming:
        company = pick_alias(raw, "company")
        role = pick_alias(raw, "role")
        url = pick_alias(raw, "posting_url")
        if not company or not role:
            skipped += 1
            continue

        status = map_simplify_status(pick_alias(raw, "status"))
        date_applied = pick_alias(raw, "date_applied")
        location = pick_alias(raw, "location")
        source = pick_alias(raw, "source") or "Simplify"
        notes_in = pick_alias(raw, "notes")

        match = find_match(apps, url, company, role)
        if match:
            old_status = match.get("status", "")
            # Simplify-owned only: company, role, url, location, date_applied, base status.
            # Never overwrite resume_version, pursuit_lane, sponsorship, auth, referral, labels.
            if company and not match.get("company"):
                match["company"] = company
            if role and not match.get("role"):
                match["role"] = role
            if url and not match.get("posting_url"):
                match["posting_url"] = url
                match["job_url"] = url
            if date_applied:
                match["date_applied"] = date_applied
            if location:
                match["location"] = location
            if status and status != old_status:
                order = [
                    "discovered", "saved", "researching", "preparing", "ready_to_apply",
                    "referral_requested", "applied", "oa", "recruiter_screen",
                    "technical_screen", "onsite", "final_round", "offer", "accepted",
                    "rejected", "withdrawn", "closed",
                ]
                old_i = order.index(old_status) if old_status in order else -1
                new_i = order.index(status) if status in order else -1
                if new_i >= old_i:
                    match["status"] = status
                    match["application_status"] = status
                    match["stage_highest_reached"] = bump_highest(
                        match.get("stage_highest_reached", ""), status
                    )
                    log_event(
                        job_id=match.get("job_id") or match.get("id", ""),
                        event_type="simplify_import_status",
                        from_status=old_status,
                        to_status=status,
                        note=path.name,
                    )
            match["last_update"] = today
            match["updated_at"] = today
            if notes_in:
                existing = match.get("notes") or ""
                marker = f"[simplify:{path.name}] {notes_in}"
                if marker not in existing:
                    match["notes"] = f"{existing}; {marker}".strip("; ").strip()
            if not match.get("next_action") and match.get("status") not in TERMINAL:
                match["next_action"] = "Enrich local strategy fields after Simplify sync"
            updated += 1
        else:
            job_id = next_id("J", apps, "id")
            row = {field: "" for field in APP_FIELDS}
            row.update({
                "id": job_id,
                "job_id": job_id,
                "company": company,
                "role": role,
                "posting_url": url,
                "job_url": url,
                "location": location,
                "source": source,
                "date_found": today,
                "date_discovered": today,
                "date_applied": date_applied or (today if status in APPLIED_OR_LATER else ""),
                "status": status,
                "application_status": status,
                "eligibility": "unclear",
                "hard_eligibility": "uncertain",
                "sponsorship_signal": "unclear",
                "pursuit_lane": "",
                "priority": "B",
                "auth_work_authorized": "not_asked",
                "auth_needs_sponsorship": "not_asked",
                "needs_review": "true",
                "next_action": "Assign pursuit lane and record resume version",
                "next_action_date": today,
                "last_update": today,
                "created_at": today,
                "updated_at": today,
                "notes": f"[simplify:{path.name}] {notes_in}".strip(),
            })
            apps.append(sync_app_aliases(row))
            log_event(job_id=job_id, event_type="simplify_import_created", to_status=status, note=f"{company} — {role}")
            created += 1

    write_rows(APPLICATIONS, APP_FIELDS, [sync_app_aliases(r) for r in apps])
    print(f"imported={path}")
    print(f"created={created} updated={updated} skipped={skipped} total_now={len(apps)}")


def parse_iso(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def overdue_actions(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    today = date.today()
    output = []
    for row in rows:
        due = parse_iso(row.get("next_action_date", ""))
        if due and due < today and row.get("status") not in TERMINAL:
            output.append(row)
    return sorted(output, key=lambda r: r.get("next_action_date", ""))


def render_table(rows: List[Dict[str, str]], fields: List[str]) -> str:
    if not rows:
        return "_None._\n"
    header = "| " + " | ".join(fields) + " |\n"
    sep = "|" + "|".join(["---"] * len(fields)) + "|\n"
    body = "".join(
        "| " + " | ".join((row.get(f, "") or "").replace("|", "\\|") for f in fields) + " |\n"
        for row in rows
    )
    return header + sep + body


def rate_table(apps: List[Dict[str, str]], group_field: str) -> List[Dict[str, str]]:
    groups: Dict[str, List[Dict[str, str]]] = {}
    for row in apps:
        key = row.get(group_field) or "unknown"
        groups.setdefault(key, []).append(row)
    out = []
    for key, rows in sorted(groups.items()):
        applied_n = sum(1 for r in rows if r.get("status") in APPLIED_OR_LATER)
        interview_n = sum(1 for r in rows if r.get("status") in INTERVIEW_STAGES)
        oa_n = sum(1 for r in rows if r.get("status") in {"oa"} | INTERVIEW_STAGES)
        denom = applied_n if applied_n else 0
        oa_rate = f"{(oa_n / denom):.0%}" if denom else "n/a"
        int_rate = f"{(interview_n / denom):.0%}" if denom else "n/a"
        out.append({
            group_field: key,
            "n": str(len(rows)),
            "applied": str(applied_n),
            "oa+": str(oa_n),
            "interview+": str(interview_n),
            "oa_rate": oa_rate,
            "interview_rate": int_rate,
        })
    return out


def practice_share(apps: List[Dict[str, str]]) -> str:
    applied = [r for r in apps if r.get("status") in APPLIED_OR_LATER]
    if not applied:
        return "n/a (no applied rows)"
    practice = sum(1 for r in applied if r.get("pursuit_lane") == "practice")
    return f"{practice}/{len(applied)} ({practice / len(applied):.0%})"


def dashboard_text() -> str:
    apps = read_rows(APPLICATIONS)
    contacts = read_rows(NETWORKING)
    status_counts = Counter(r.get("status") or "unknown" for r in apps)
    priority_counts = Counter(r.get("priority") or "unknown" for r in apps)
    cluster_counts = Counter(r.get("role_cluster") or "unknown" for r in apps)
    lane_counts = Counter(r.get("pursuit_lane") or "unassigned" for r in apps)
    active = [r for r in apps if r.get("status") not in TERMINAL]
    active = sorted(
        active,
        key=lambda r: (
            {"A": 0, "B": 1, "C": 2}.get(r.get("priority", ""), 9),
            {"core": 0, "broad": 1, "practice": 2}.get(r.get("pursuit_lane", ""), 9),
            r.get("next_action_date", "9999"),
        ),
    )
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
        f"- Practice-lane share of applied: **{practice_share(apps)}** (target 15–25%)\n",
        "\n## By status\n",
        render_table([{"status": k, "count": str(v)} for k, v in sorted(status_counts.items())], ["status", "count"]),
        "\n## By pursuit lane\n",
        render_table([{"pursuit_lane": k, "count": str(v)} for k, v in sorted(lane_counts.items())], ["pursuit_lane", "count"]),
        "\n## By priority\n",
        render_table([{"priority": k, "count": str(v)} for k, v in sorted(priority_counts.items())], ["priority", "count"]),
        "\n## By role cluster\n",
        render_table([{"role_cluster": k, "count": str(v)} for k, v in sorted(cluster_counts.items())], ["role_cluster", "count"]),
        "\n## Conversion by pursuit lane\n",
        "_Rates use applied-or-later as denominator. Small n → do not overfit._\n\n",
        render_table(rate_table(apps, "pursuit_lane"), ["pursuit_lane", "n", "applied", "oa+", "interview+", "oa_rate", "interview_rate"]),
        "\n## Conversion by sponsorship signal\n",
        render_table(rate_table(apps, "sponsorship_signal"), ["sponsorship_signal", "n", "applied", "oa+", "interview+", "oa_rate", "interview_rate"]),
        "\n## Conversion by resume version\n",
        render_table(rate_table(apps, "resume_version"), ["resume_version", "n", "applied", "oa+", "interview+", "oa_rate", "interview_rate"]),
        "\n## Overdue next actions\n",
        render_table(overdue, ["id", "company", "role", "status", "pursuit_lane", "next_action", "next_action_date"]),
        "\n## Active pipeline\n",
        render_table(
            active[:50],
            ["id", "priority", "pursuit_lane", "company", "role", "status", "eligibility", "sponsorship_signal", "next_action", "next_action_date"],
        ),
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
    lanes = Counter(r.get("pursuit_lane") or "unassigned" for r in apps)
    text = [
        f"# Weekly review — {date.today().isoformat()}\n\n",
        "## Funnel facts\n\n",
        f"- Roles tracked: {len(apps)}\n",
        f"- Applications confirmed: {statuses.get('applied', 0)}\n",
        f"- OA/interview stages: {sum(statuses.get(s, 0) for s in ['oa', 'recruiter_screen', 'technical_screen', 'onsite'])}\n",
        f"- Offers: {statuses.get('offer', 0)}\n",
        f"- Rejections: {statuses.get('rejected', 0)}\n",
        f"- Contacts tracked: {len(contacts)}\n",
        f"- Overdue next actions: {len(overdue_actions(apps))}\n",
        f"- Practice-lane share of applied: {practice_share(apps)}\n\n",
        "## Pursuit lanes\n\n",
        render_table([{"lane": k, "n": str(v)} for k, v in lanes.most_common()], ["lane", "n"]),
        "\n## Conversion by pursuit lane\n\n",
        render_table(rate_table(apps, "pursuit_lane"), ["pursuit_lane", "n", "applied", "oa+", "interview+", "oa_rate", "interview_rate"]),
        "\n## Conversion by sponsorship signal\n\n",
        render_table(rate_table(apps, "sponsorship_signal"), ["sponsorship_signal", "n", "applied", "oa+", "interview+", "oa_rate", "interview_rate"]),
        "\n## Source sample sizes\n\n",
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
    p.add_argument("--eligibility", choices=sorted(VALID_ELIGIBILITY), default="unclear")
    p.add_argument("--graduation-fit", default="")
    p.add_argument("--sponsorship", choices=sorted(VALID_SPONSORSHIP), default="unclear")
    p.add_argument("--pursuit-lane", choices=sorted(VALID_PURSUIT_LANES), default=None)
    p.add_argument("--priority", choices=["A", "B", "C"], default="B")
    p.add_argument("--next-action", default="")
    p.add_argument("--next-action-date", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_add_job)

    p = sub.add_parser("update-job", help="Update an existing job")
    p.add_argument("job_id")
    p.add_argument("--status", choices=sorted(VALID_STATUSES))
    p.add_argument("--eligibility", choices=sorted(VALID_ELIGIBILITY))
    p.add_argument("--priority", choices=["A", "B", "C"])
    p.add_argument("--pursuit-lane", choices=sorted(VALID_PURSUIT_LANES))
    p.add_argument("--sponsorship", choices=sorted(VALID_SPONSORSHIP))
    p.add_argument("--date-applied")
    p.add_argument("--resume-version")
    p.add_argument("--referral-status")
    p.add_argument("--auth-work-authorized", choices=sorted(VALID_AUTH_ANSWER))
    p.add_argument("--auth-needs-sponsorship", choices=sorted(VALID_AUTH_ANSWER))
    p.add_argument("--auth-qa-notes")
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

    p = sub.add_parser("import-simplify", help="One-way import from a Simplify (or similar) CSV export")
    p.add_argument("--file", required=True, help="Path to CSV under data/imports/simplify/ or absolute path")
    p.set_defaults(func=cmd_import_simplify)

    p = sub.add_parser("dashboard", help="Generate dashboard markdown")
    p.set_defaults(func=cmd_dashboard)

    p = sub.add_parser("weekly", help="Generate weekly review template with current counts")
    p.set_defaults(func=cmd_weekly)
    return parser


def main() -> int:
    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    migrate_applications()
    ensure_csv(NETWORKING, CONTACT_FIELDS)
    ensure_csv(ACTIVITY, LOG_FIELDS)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
