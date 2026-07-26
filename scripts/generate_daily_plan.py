#!/usr/bin/env python3
"""Generate a bounded daily plan from local CSVs (no external sends)."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, TERMINAL, log, parse_iso, read_rows, sync_app_aliases, today_iso,
)

OUT_DIR = ROOT / "generated" / "daily"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date", default=today_iso())
    args = p.parse_args()
    today = date.fromisoformat(args.date)
    soon = today + timedelta(days=2)

    apps = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    active = [a for a in apps if a.get("status") not in TERMINAL]

    must = []
    for a in active:
        for field, label in (("deadline", "deadline"), ("next_action_date", "next_action"),
                             ("oa_received_date", "OA")):
            d = parse_iso(a.get(field, ""))
            if d and d <= soon:
                must.append(f"- **{label}** `{a.get('company')}` / {a.get('role')} — {a.get('next_action') or field} ({d.isoformat()})")
        if a.get("status") in {"oa", "recruiter_screen", "technical_screen", "onsite"}:
            must.append(f"- **Interview pipeline** `{a.get('company')}` at stage `{a.get('status')}` — prepare + confirm logistics")

    # Application suggestions
    apply_q = sorted(
        [a for a in active if a.get("status") in {"discovered", "saved", "researching", "preparing", "ready_to_apply"}],
        key=lambda a: ({"A": 0, "B": 1, "C": 2}.get(a.get("priority", ""), 9),
                       {"core": 0, "broad": 1, "practice": 2}.get(a.get("pursuit_lane", ""), 9)),
    )[:5]

    overdue = []
    for a in active:
        d = parse_iso(a.get("next_action_date", ""))
        if d and d < today:
            overdue.append(a)

    resume_default = {
        "cloud_swe": "2026-07-20_cloud-swe_v1.1",
        "general_swe": "2026-07-20_cloud-swe_v1.1",
        "data_ml": "2026-07-20_data-ml_v1.1",
        "health_ai": "2026-07-20_health-ai_v1.1",
    }

    lines = [
        f"# Daily plan — {args.date}\n\n",
        "_Auto-generated caps: ≤3 must-do, ≤5 apps, ≤3 outreach, ≤2 follow-ups, 1 prep block._\n\n",
        "## 1. Must Do Today\n\n",
    ]
    if must:
        lines.extend(m + "\n" for m in must[:3])
    else:
        lines.append("- No hard deadlines detected in CSV. Keep trial/system sync moving.\n")

    lines.append("\n## 2. Applications\n\n")
    if not apply_q:
        lines.append("- No queued discoveries. Find 3 roles (Jobright/LinkedIn) and ingest.\n")
    for a in apply_q:
        rv = a.get("resume_version") or resume_default.get(a.get("role_cluster", ""), "2026-07-20_data-ml_v1.1")
        lane = a.get("pursuit_lane") or "broad"
        tailor = "light" if lane == "core" else "none"
        minutes = {"none": 15, "light": 35, "deep": 75}.get(tailor, 20)
        lines.append(
            f"- `{a.get('job_id') or a.get('id')}` **{a.get('company')}** — {a.get('role')}\n"
            f"  - lane/priority: {lane} / {a.get('priority') or '?'}\n"
            f"  - resume: `{rv}` | tailoring: {tailor} | ~{minutes} min\n"
            f"  - next: {a.get('next_action') or 'Triage + apply via Simplify'}\n"
        )

    lines.append("\n## 3. Networking\n\n")
    lines.append(f"- Open `generated/outreach/{args.date}.md` (run `generate_outreach_queue.py` if missing).\n")
    lines.append("- Send only after editing; no auto-send.\n")

    lines.append("\n## 4. Interview Preparation\n\n")
    stages = {a.get("status") for a in active}
    if "technical_screen" in stages or "onsite" in stages:
        lines.append("- 45–60 min: coding + one system/ML story tied to agentic chatbot project.\n")
    elif "oa" in stages:
        lines.append("- 30 min: OA practice matching the vendor (if known) + resume story refresh.\n")
    else:
        lines.append("- 30 min diagnostic: 2 easy/medium LeetCode + rewrite one behavioral STAR from chatbot leadership.\n")

    lines.append("\n## 5. Administrative\n\n")
    lines.append("- Import latest Simplify CSV if you applied today.\n")
    lines.append("- Run `validate_data.py`; clear errors in `generated/review_queue.csv`.\n")
    lines.append(f"- Overdue next actions: **{len(overdue)}**\n")
    for a in overdue[:5]:
        lines.append(f"  - `{a.get('job_id') or a.get('id')}` {a.get('company')}: {a.get('next_action')} (due {a.get('next_action_date')})\n")

    lines.append("\n## 6. Suggested time blocks\n\n")
    lines.append("```text\n")
    lines.append("09:00–09:45  Core / queued applications (Simplify)\n")
    lines.append("10:00–10:25  Outreach (2–3 personalized)\n")
    lines.append("15:00–15:30  Technical prep module\n")
    lines.append("18:00–18:20  Tracker sync + validate + dashboard\n")
    lines.append("```\n")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{args.date}.md"
    out.write_text("".join(lines), encoding="utf-8")
    log(f"wrote {out}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
