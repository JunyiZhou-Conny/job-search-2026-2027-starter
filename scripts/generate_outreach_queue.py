#!/usr/bin/env python3
"""Generate today's outreach queue (proposals only — never sends messages)."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, CONTACTS, NETWORKING, TERMINAL, log, parse_iso, read_rows,
    sync_app_aliases, today_iso,
)

OUT_DIR = ROOT / "generated" / "outreach"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", default=today_iso())
    args = p.parse_args()
    today = date.fromisoformat(args.date)
    week_ago = today - timedelta(days=7)

    apps = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    contacts = read_rows(CONTACTS)
    legacy_net = read_rows(NETWORKING)

    lines = [f"# Outreach queue — {args.date}\n",
             "_Proposals only. Do not send without user approval._\n",
             "## Caps today\n",
             "- 2–3 high-quality first outreach\n",
             "- 1–2 follow-ups\n",
             "- ≤1 referral request\n",
             "- Prefer different companies; no re-ping within 7 days\n"]

    items = []

    # 1. Core applied last 7d with no outreach
    for a in apps:
        if a.get("pursuit_lane") != "core":
            continue
        if a.get("status") not in {"applied", "oa", "recruiter_screen", "technical_screen"}:
            continue
        d = parse_iso(a.get("date_applied", ""))
        if not d or d < week_ago:
            continue
        if (a.get("networking_before_apply") or "").lower() in {"yes", "true"}:
            continue
        if (a.get("networking_after_apply") or "").lower() in {"yes", "true"}:
            continue
        items.append({
            "why_today": "Core role applied in last 7 days with no recorded outreach",
            "company": a.get("company"),
            "role": a.get("role"),
            "job_id": a.get("job_id") or a.get("id"),
            "action": "Find 1 Harvard/Emory alum or team engineer; send perspective ask (not referral)",
            "objective": "Learn about team/role; open door for later intro",
            "message": (
                f"Hi {{name}} — I'm a Harvard Health Data Science master's student (Dec 2026) working on "
                f"agentic LLM/RAG systems and applied ML. I recently applied to {a.get('role')} at "
                f"{a.get('company')} and would value 15 minutes on how your team approaches "
                f"{{topic}}. Happy to share a concise background first."
            ),
            "follow_up": (today + timedelta(days=7)).isoformat(),
            "confidence": "0.70",
        })

    # 2. Interview stages without contacts
    for a in apps:
        if a.get("status") in {"oa", "recruiter_screen", "technical_screen", "onsite"}:
            items.append({
                "why_today": f"Active stage `{a.get('status')}` — add team context",
                "company": a.get("company"),
                "role": a.get("role"),
                "job_id": a.get("job_id") or a.get("id"),
                "action": "Identify 1–2 people on the hiring team; light thank-you / prep question after screen if applicable",
                "objective": "Interview signal + optional referral later",
                "message": "(Stage-specific — draft after reviewing JD and your stories)",
                "follow_up": (today + timedelta(days=3)).isoformat(),
                "confidence": "0.65",
            })

    # 3. Legacy follow-ups due
    for n in legacy_net:
        fd = parse_iso(n.get("follow_up_date", ""))
        if fd and fd <= today and (n.get("response_status") or "") in {"not_contacted", "no_response", "awaiting_reply", ""}:
            items.append({
                "why_today": "Follow-up date due",
                "company": n.get("company"),
                "role": n.get("role"),
                "job_id": n.get("target_job_id"),
                "action": f"Follow up with {n.get('name')}",
                "objective": "Bump politely; offer specific question",
                "message": f"Hi {n.get('name') or ''} — quick follow-up in case this was buried. Still interested in a brief chat about {{topic}}.",
                "follow_up": (today + timedelta(days=7)).isoformat(),
                "confidence": "0.80",
            })

    # 4. Search targets if thin queue
    if len(items) < 2:
        for a in apps:
            if a.get("status") not in TERMINAL and a.get("priority") == "A":
                items.append({
                    "why_today": "High-priority active role — build search target",
                    "company": a.get("company"),
                    "role": a.get("role"),
                    "job_id": a.get("job_id") or a.get("id"),
                    "action": (
                        f"LinkedIn search: \"{a.get('company')}\" (\"Harvard\" OR \"Emory\") "
                        f"(Engineer OR \"Machine Learning\" OR Recruiter)"
                    ),
                    "objective": "Build shortlist of 3 names",
                    "message": "(Draft after picking a person)",
                    "follow_up": (today + timedelta(days=2)).isoformat(),
                    "confidence": "0.55",
                })

    # Deduplicate by company, cap
    seen_co = set()
    final = []
    for it in items:
        co = (it.get("company") or "").lower()
        if co in seen_co and len(final) >= 3:
            continue
        seen_co.add(co)
        final.append(it)
        if len(final) >= 5:
            break

    lines.append(f"\n## Recommended targets ({len(final)})\n")
    if not final:
        lines.append("_None — add Core applications or contacts first._\n")
    for i, it in enumerate(final, 1):
        lines.append(f"### {i}. {it.get('company')} — {it.get('role')}\n")
        lines.append(f"- job_id: `{it.get('job_id')}`\n")
        lines.append(f"- why today: {it.get('why_today')}\n")
        lines.append(f"- action: {it.get('action')}\n")
        lines.append(f"- objective: {it.get('objective')}\n")
        lines.append(f"- follow_up: {it.get('follow_up')}\n")
        lines.append(f"- confidence: {it.get('confidence')}\n")
        lines.append(f"- suggested message:\n\n```\n{it.get('message')}\n```\n")

    lines.append("\n## Contacts on file\n")
    lines.append(f"- contacts.csv rows: {len(contacts)}\n")
    lines.append(f"- legacy networking.csv rows: {len(legacy_net)}\n")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.date}.md"
    out.write_text("".join(lines), encoding="utf-8")
    log(f"wrote {out}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
