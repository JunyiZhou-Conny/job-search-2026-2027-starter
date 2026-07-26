#!/usr/bin/env python3
"""Generate a Job Search ICS file (dry-run by default)."""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import APPLICATIONS, TERMINAL, log, parse_iso, read_rows, sync_app_aliases, today_iso  # noqa: E402

OUT = ROOT / "generated" / "calendar" / "job_search.ics"


def uid_for(*parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode()).hexdigest()[:12]
    return f"jobsearch-{h}@local"


def ics_event(uid: str, summary: str, day: date, hour: int = 9, minutes: int = 60, description: str = "") -> str:
    start = datetime(day.year, day.month, day.day, hour, 0, 0)
    end = start + timedelta(minutes=minutes)
    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")
    desc = description.replace("\n", "\\n")
    return "\n".join([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{fmt(start)}",
        f"DTEND:{fmt(end)}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT",
    ])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", default=True)
    p.add_argument("--write", action="store_true", help="Actually write ICS (disables dry-run)")
    p.add_argument("--date", default=today_iso())
    args = p.parse_args()
    dry = not args.write

    today = date.fromisoformat(args.date)
    apps = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    events = []
    plan = []

    # Weekly review Friday 17:00
    days_ahead = (4 - today.weekday()) % 7
    friday = today + timedelta(days=days_ahead)
    events.append(ics_event(uid_for("weekly", friday.isoformat()), "Job search weekly review", friday, 17, 45,
                            "Run weekly + dashboard; ≤3 experiments"))
    plan.append(f"CREATE weekly review {friday}")

    # Daily focus blocks Mon–Fri
    for i in range(5):
        d = today + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        events.append(ics_event(uid_for("applyblock", d.isoformat()), "Job search: applications block", d, 9, 45))
        events.append(ics_event(uid_for("outreachblock", d.isoformat()), "Job search: outreach block", d, 10, 30))
        plan.append(f"CREATE blocks {d}")

    for a in apps:
        if a.get("status") in TERMINAL:
            continue
        for field, label, hour in (
            ("deadline", "Deadline", 9),
            ("next_action_date", "Follow-up", 11),
            ("oa_received_date", "OA focus", 14),
        ):
            d = parse_iso(a.get(field, ""))
            if not d:
                continue
            summary = f"{label}: {a.get('company')} — {a.get('role')}"
            events.append(ics_event(
                uid_for(field, a.get("job_id") or a.get("id") or "", d.isoformat()),
                summary, d, hour, 45, a.get("next_action") or "",
            ))
            plan.append(f"CREATE {label} {a.get('company')} {d}")

    log(f"calendar events planned={len(events)}")
    for line in plan[:30]:
        log(f"  {line}")
    if dry:
        log("dry-run only — pass --write to emit ICS")
        print("dry-run OK")
        return 0

    body = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//JobSearch OS//EN", "CALSCALE:GREGORIAN"]
    body.extend(events)
    body.append("END:VCALENDAR")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body) + "\n", encoding="utf-8")
    log(f"wrote {OUT}")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
