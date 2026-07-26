#!/usr/bin/env python3
"""Suggest labels for a job (eligibility, sponsorship, lane, cluster, priority).

Never overwrites label_source=manual unless --force-manual-override with confirmation flag.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, APP_FIELDS, log, read_rows, sync_app_aliases, today_iso, write_rows,
)

CITIZEN_RE = re.compile(r"us citizen|u\.s\. citizen|united states citizen|must be a citizen", re.I)
CLEARANCE_RE = re.compile(r"security clearance|active clearance|ts/sci", re.I)
RETURN_SCHOOL_RE = re.compile(r"return to school|returning to school|enrolled .* after", re.I)
NO_SPONSOR_RE = re.compile(r"not sponsor|no sponsorship|unable to sponsor|cannot sponsor|will not sponsor", re.I)
SPONSOR_OK_RE = re.compile(r"visa sponsorship|sponsor h-1b|h-1b .* available|immigration sponsorship", re.I)
REMOTE_RE = re.compile(r"\bremote\b|work from home|fully remote", re.I)
INTERNSHIP_RE = re.compile(r"intern(ship)?", re.I)


def score_priority(tech: int, evidence: int, preference: int, company: int, freshness: int, network: int, efficiency: int) -> Tuple[int, str]:
    total = tech + evidence + preference + company + freshness + network + efficiency
    if total >= 75:
        band = "A"
    elif total >= 55:
        band = "B"
    else:
        band = "C"
    return total, band


def suggest_from_text(text: str, role: str = "", company: str = "") -> Dict[str, Any]:
    blob = f"{role}\n{company}\n{text}"
    evidence: List[str] = []
    hard = "uncertain"
    hard_reason = ""
    hard_conf = 0.40

    if CITIZEN_RE.search(blob):
        hard = "ineligible"
        hard_reason = "Posting appears to require U.S. citizenship"
        hard_conf = 0.85
        evidence.append("citizen_requirement_regex")
    elif CLEARANCE_RE.search(blob):
        hard = "ineligible"
        hard_reason = "Posting appears to require security clearance"
        hard_conf = 0.80
        evidence.append("clearance_requirement_regex")
    elif RETURN_SCHOOL_RE.search(blob) and INTERNSHIP_RE.search(blob):
        hard = "uncertain"
        hard_reason = "Internship may require return-to-school — verify against Dec 2026 graduation"
        hard_conf = 0.55
        evidence.append("return_to_school_language")
    else:
        hard = "eligible"
        hard_reason = "No hard citizenship/clearance/return-school conflict detected in text"
        hard_conf = 0.55
        evidence.append("no_hard_block_detected")

    if REMOTE_RE.search(blob) and re.search(r"fully remote|remote only|100%\s*remote", blob, re.I):
        hard = "ineligible"
        hard_reason = "Fully remote conflicts with user hard preference (in-person)"
        hard_conf = 0.75
        evidence.append("remote_hard_constraint")

    # Sponsorship — NEVER drives hard ineligible alone
    if NO_SPONSOR_RE.search(blob):
        sponsor = "explicit_no"
        sponsor_conf = 0.85
        sponsor_ev = "explicit no-sponsorship language"
    elif SPONSOR_OK_RE.search(blob):
        sponsor = "supportive"
        sponsor_conf = 0.70
        sponsor_ev = "sponsorship-positive language"
    else:
        sponsor = "unclear"
        sponsor_conf = 0.50
        sponsor_ev = "no clear sponsorship statement"

    # Cluster
    role_l = (role + " " + blob).lower()
    if any(k in role_l for k in ["health", "clinical", "biomed", "digital health"]):
        cluster = "health_ai"
        cluster_conf = 0.65
    elif any(k in role_l for k in ["machine learning", "ml engineer", "applied ai", "data scientist", "llm", "genai"]):
        cluster = "data_ml"
        cluster_conf = 0.70
    elif any(k in role_l for k in ["data engineer", "analytics engineer"]):
        cluster = "data_engineering"
        cluster_conf = 0.65
    elif any(k in role_l for k in ["platform", "infrastructure", "sre", "cloud", "backend"]):
        cluster = "cloud_swe"
        cluster_conf = 0.70
    elif "software" in role_l or "swe" in role_l:
        cluster = "general_swe"
        cluster_conf = 0.60
    else:
        cluster = "other"
        cluster_conf = 0.40

    # Lane suggestion
    tech = 22 if cluster in {"cloud_swe", "data_ml", "general_swe", "health_ai"} else 12
    evidence_s = 16  # user has strong chatbot/transformer evidence generally
    pref = 12 if cluster in {"cloud_swe", "data_ml", "general_swe"} else 8
    company_i = 5
    freshness = 6
    network = 3
    efficiency = 4
    total, band = score_priority(tech, evidence_s, pref, company_i, freshness, network, efficiency)

    if hard == "ineligible":
        lane = "practice"
        lane_reason = "Hard-ineligible roles may still be practice-only if user explicitly wants reps; default practice"
        lane_conf = 0.60
    elif sponsor == "explicit_no" and total >= 55:
        lane = "broad"
        lane_reason = "Solid technical fit but explicit no sponsorship → broad (not ineligible)"
        lane_conf = 0.70
    elif total >= 75 and hard != "ineligible":
        lane = "core"
        lane_reason = "High match score and no hard block"
        lane_conf = 0.65
    elif total >= 55:
        lane = "broad"
        lane_reason = "Medium match — pursue with standard cluster resume"
        lane_conf = 0.60
    else:
        lane = "practice"
        lane_reason = "Lower match — volume/practice lane if pursued"
        lane_conf = 0.55

    resume_map = {
        "cloud_swe": "2026-07-20_cloud-swe_v1.1",
        "general_swe": "2026-07-20_cloud-swe_v1.1",
        "backend_platform": "2026-07-20_cloud-swe_v1.1",
        "data_ml": "2026-07-20_data-ml_v1.1",
        "data_engineering": "2026-07-20_data-ml_v1.1",
        "data_analytics": "2026-07-20_data-ml_v1.1",
        "ml_ai": "2026-07-20_data-ml_v1.1",
        "health_ai": "2026-07-20_health-ai_v1.1",
    }

    return {
        "hard_eligibility": {"value": hard, "confidence": hard_conf, "reason": hard_reason, "evidence": evidence},
        "sponsorship_signal": {"value": sponsor, "confidence": sponsor_conf, "reason": sponsor_ev, "evidence": [sponsor_ev]},
        "role_cluster": {"value": cluster, "confidence": cluster_conf, "reason": f"Title/JD keyword match → {cluster}"},
        "pursuit_lane": {"value": lane, "confidence": lane_conf, "reason": lane_reason},
        "priority": {"value": band, "confidence": 0.55, "score": total, "reason": f"Score {total} → {band}"},
        "resume_version": {"value": resume_map.get(cluster, "2026-07-20_data-ml_v1.1"), "confidence": 0.60},
        "needs_review": hard_conf < 0.7 or sponsor_conf < 0.7 or cluster_conf < 0.55,
        "source": "auto",
        "note": "Sponsorship never alone sets hard_eligibility=ineligible",
    }


def apply_suggestions(job_id: str, suggestions: Dict[str, Any], force: bool) -> None:
    rows = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    found = False
    for row in rows:
        if (row.get("job_id") or row.get("id")) != job_id:
            continue
        found = True
        if row.get("label_source") == "manual" and not force:
            log(f"SKIP write: {job_id} has label_source=manual (pass --force-manual-override to replace)")
            return
        row["hard_eligibility"] = suggestions["hard_eligibility"]["value"]
        row["hard_eligibility_reason"] = suggestions["hard_eligibility"]["reason"]
        row["sponsorship_signal"] = suggestions["sponsorship_signal"]["value"]
        row["sponsorship_evidence"] = suggestions["sponsorship_signal"]["reason"]
        row["role_cluster"] = suggestions["role_cluster"]["value"]
        row["pursuit_lane"] = suggestions["pursuit_lane"]["value"]
        row["priority"] = suggestions["priority"]["value"]
        row["priority_score"] = str(suggestions["priority"]["score"])
        if not row.get("resume_version"):
            row["resume_version"] = suggestions["resume_version"]["value"]
        row["label_confidence"] = f"{min(suggestions['hard_eligibility']['confidence'], suggestions['pursuit_lane']['confidence']):.2f}"
        row["label_reason"] = suggestions["pursuit_lane"]["reason"]
        row["label_source"] = "auto" if not force else "mixed"
        row["needs_review"] = "true" if suggestions["needs_review"] else "false"
        row["updated_at"] = today_iso()
        row["last_update"] = today_iso()
        break
    if not found:
        raise SystemExit(f"Unknown job id: {job_id}")
    write_rows(APPLICATIONS, APP_FIELDS, rows)
    log(f"updated labels for {job_id}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--job-id", help="Existing job id to label")
    p.add_argument("--role", default="")
    p.add_argument("--company", default="")
    p.add_argument("--jd-file", help="Path to JD text file")
    p.add_argument("--jd-text", default="")
    p.add_argument("--apply", action="store_true", help="Write suggestions to applications.csv")
    p.add_argument("--force-manual-override", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    text = args.jd_text
    if args.jd_file:
        text = Path(args.jd_file).read_text(encoding="utf-8")
    if args.job_id and not text:
        for r in read_rows(APPLICATIONS):
            if (r.get("job_id") or r.get("id")) == args.job_id:
                text = r.get("notes") or ""
                args.role = args.role or r.get("role", "")
                args.company = args.company or r.get("company", "")
                break

    if not text and not args.role:
        p.error("Provide --jd-text/--jd-file and/or --role, optionally --job-id")

    suggestions = suggest_from_text(text, role=args.role, company=args.company)
    if args.json:
        print(json.dumps(suggestions, indent=2))
    else:
        print("=== Label suggestions (auto) ===")
        for key in ("hard_eligibility", "sponsorship_signal", "role_cluster", "pursuit_lane", "priority", "resume_version"):
            block = suggestions[key]
            print(f"- {key}: {block.get('value')}  conf={block.get('confidence')}  {block.get('reason', '')}")
        print(f"- needs_review: {suggestions['needs_review']}")
        print(f"- note: {suggestions['note']}")

    if args.apply:
        if not args.job_id:
            p.error("--apply requires --job-id")
        apply_suggestions(args.job_id, suggestions, force=args.force_manual_override)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
