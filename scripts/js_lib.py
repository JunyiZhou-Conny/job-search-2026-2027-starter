#!/usr/bin/env python3
"""Shared helpers for the job-search operating system."""

from __future__ import annotations

import csv
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
APPLICATIONS = DATA / "applications.csv"
NETWORKING = DATA / "networking.csv"
CONTACTS = DATA / "contacts.csv"
ACTIVITY = DATA / "activity_log.csv"
RESUME_VERSIONS = DATA / "resume_versions.csv"
REVIEW_QUEUE = ROOT / "generated" / "review_queue.csv"
BACKUPS = DATA / "backups"

# Canonical application fields (additive supersets of v1 schema).
APP_FIELDS: List[str] = [
    "id", "job_id", "company", "role", "job_url", "posting_url", "source", "source_detail",
    "location", "work_model", "employment_type", "role_cluster", "role_cluster_secondary",
    "date_discovered", "date_found", "posting_date", "date_applied",
    "status", "application_status", "stage_highest_reached", "stage_current",
    "response_date", "oa_received_date", "recruiter_screen_date", "technical_screen_date",
    "final_interview_date", "offer_date", "rejection_date", "rejection_stage",
    "resume_version", "cover_letter_version", "tailoring_level", "application_minutes",
    "pursuit_lane", "priority", "priority_score",
    "eligibility", "hard_eligibility", "hard_eligibility_reason", "graduation_fit",
    "sponsorship_signal", "sponsorship_evidence",
    "auth_work_authorized", "auth_needs_sponsorship",
    "current_authorization_answer", "future_sponsorship_answer", "answer_question_text", "auth_qa_notes",
    "networking_before_apply", "networking_after_apply",
    "referral_status", "referrer_contact_id", "recruiter",
    "label_confidence", "label_reason", "label_source", "needs_review",
    "next_action", "next_action_date", "deadline", "job_post_age_days",
    "notes", "created_at", "updated_at", "last_update",
]

CONTACT_FIELDS = [
    "contact_id", "name", "company", "title", "team", "location", "linkedin_url", "email",
    "relationship_type", "school_connection", "shared_background", "target_role_cluster",
    "source", "last_verified", "notes",
]

# Interactions (outreach history). Replaces overloading of old networking.csv over time.
INTERACTION_FIELDS = [
    "interaction_id", "contact_id", "job_id", "interaction_type", "channel",
    "date_planned", "date_completed", "message_version", "response_status", "response_date",
    "follow_up_date", "coffee_chat_date", "referral_requested", "referral_result",
    "next_action", "next_action_date", "notes",
]

# Legacy networking.csv fields retained for backward compatibility reads.
LEGACY_NETWORKING_FIELDS = [
    "contact_id", "name", "company", "role", "relation", "source",
    "profile_url", "target_job_id", "outreach_date", "follow_up_date",
    "response_status", "coffee_chat_date", "referral_status", "last_update", "notes",
]

RESUME_VERSION_FIELDS = [
    "resume_version", "parent_version", "cluster", "created_date", "change_summary",
    "hypothesis", "target_roles", "active", "applications_count", "oa_count",
    "screen_count", "technical_count", "offer_count", "notes", "file_path",
]

LOG_FIELDS = ["timestamp", "job_id", "contact_id", "event_type", "from_status", "to_status", "note"]

VALID_STATUSES = {
    "discovered", "saved", "researching", "preparing", "ready_to_apply", "referral_requested",
    "applied", "oa", "recruiter_screen", "technical_screen", "onsite", "final_round",
    "offer", "accepted", "withdrawn", "rejected", "closed",
    "passed",  # user reviewed JD and chose not to pursue (not an employer rejection)
}
TERMINAL = {"offer", "accepted", "withdrawn", "rejected", "closed", "passed"}
INTERVIEW_PLUS = {"oa", "recruiter_screen", "technical_screen", "onsite", "final_round", "offer", "accepted"}
APPLIED_PLUS = {"applied"} | INTERVIEW_PLUS | {"rejected"}

HARD_ELIG = {"eligible", "uncertain", "ineligible"}
SPONSORSHIP = {
    "supportive", "historically_possible", "unclear", "unlikely", "explicit_no",
    # legacy
    "verified", "likely", "no",
}
LANES = {"core", "broad", "practice"}
PRIORITIES = {"A", "B", "C"}
LABEL_SOURCES = {"auto", "manual", "mixed", ""}
TAILORING = {"none", "light", "deep", ""}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", file=sys.stderr)


def ensure_csv(path: Path, fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=list(fields)).writeheader()


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_rows(path: Path, fields: Sequence[str], rows: Iterable[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") or "" for k in fields})


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    p = urlparse(url)
    return urlunparse(p._replace(fragment="")).rstrip("/").lower()


# Tracking parameters carry no identity, but some boards put the job id in the
# query string (Greenhouse `?token=`, Workday `?jobId=`), so those must survive:
# dropping the whole query collapses every embedded Greenhouse posting onto one key.
TRACKING_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gh_src",
    "source",
    "src",
    "ref",
    "referrer",
    "trk",
    "trackingid",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


def canonical_url(url: str) -> str:
    """Identity key for a posting: stable across tracking noise, never lossy.

    One implementation shared by the queue renderer and the write-back layer —
    they used to disagree, so a role could be written as applied and still come
    back looking untouched.
    """
    raw = (url or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    kept = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=False)
        if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm")
    ]
    query = urlencode(sorted(kept))
    cleaned = parsed._replace(query=query, fragment="")
    return urlunparse(cleaned).rstrip("/").lower()


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").lower().strip())


def company_role_key(company: str, role: str) -> str:
    return f"{normalize_text(company)}|{normalize_text(role)}"


def parse_iso(value: str) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def next_id(prefix: str, rows: Iterable[Dict[str, str]], field: str) -> str:
    day = date.today().strftime("%Y%m%d")
    stem = f"{prefix}{day}-"
    nums = []
    for row in rows:
        value = row.get(field) or row.get("id") or ""
        if value.startswith(stem):
            try:
                nums.append(int(value.rsplit("-", 1)[1]))
            except ValueError:
                pass
    return f"{stem}{max(nums, default=0) + 1:03d}"


def today_iso() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def map_hard_eligibility(old: str) -> str:
    m = {
        "verified": "eligible",
        "likely": "eligible",
        "unclear": "uncertain",
        "ineligible": "ineligible",
        "eligible": "eligible",
        "uncertain": "uncertain",
    }
    return m.get((old or "").strip().lower(), "uncertain")


def map_sponsorship(old: str) -> str:
    m = {
        "verified": "supportive",
        "likely": "historically_possible",
        "unclear": "unclear",
        "no": "explicit_no",
        "supportive": "supportive",
        "historically_possible": "historically_possible",
        "unlikely": "unlikely",
        "explicit_no": "explicit_no",
    }
    return m.get((old or "").strip().lower(), "unclear")


def sync_app_aliases(row: Dict[str, str]) -> Dict[str, str]:
    """Keep dual field names in sync for transition period."""
    out = {k: (row.get(k) or "") for k in APP_FIELDS}
    # ids
    jid = out.get("job_id") or out.get("id") or ""
    out["id"] = jid
    out["job_id"] = jid
    # urls
    url = out.get("job_url") or out.get("posting_url") or ""
    out["job_url"] = url
    out["posting_url"] = url
    # dates discovered
    discovered = out.get("date_discovered") or out.get("date_found") or ""
    out["date_discovered"] = discovered
    out["date_found"] = discovered
    # status
    st = out.get("application_status") or out.get("status") or ""
    out["status"] = st
    out["application_status"] = st
    out["stage_current"] = out.get("stage_current") or st
    # eligibility
    if not out.get("hard_eligibility"):
        out["hard_eligibility"] = map_hard_eligibility(out.get("eligibility", ""))
    if not out.get("eligibility"):
        # reverse-ish for legacy tooling
        rev = {"eligible": "verified", "uncertain": "unclear", "ineligible": "ineligible"}
        out["eligibility"] = rev.get(out["hard_eligibility"], "unclear")
    # sponsorship normalize to new enum when legacy present
    if out.get("sponsorship_signal") in {"verified", "likely", "no"}:
        out["sponsorship_signal"] = map_sponsorship(out["sponsorship_signal"])
    # auth mirrors
    if not out.get("current_authorization_answer"):
        out["current_authorization_answer"] = out.get("auth_work_authorized", "")
    if not out.get("future_sponsorship_answer"):
        out["future_sponsorship_answer"] = out.get("auth_needs_sponsorship", "")
    if not out.get("answer_question_text"):
        out["answer_question_text"] = out.get("auth_qa_notes", "")
    # timestamps
    if not out.get("updated_at"):
        out["updated_at"] = out.get("last_update") or today_iso()
    out["last_update"] = out.get("last_update") or out["updated_at"][:10]
    if not out.get("created_at"):
        out["created_at"] = out.get("date_discovered") or out.get("date_found") or today_iso()
    return out


def stage_rank(status: str) -> int:
    order = [
        "discovered", "saved", "researching", "preparing", "ready_to_apply", "referral_requested",
        "applied", "oa", "recruiter_screen", "technical_screen", "onsite", "final_round",
        "offer", "accepted",
    ]
    if status in {"rejected", "withdrawn", "closed"}:
        return -1
    try:
        return order.index(status)
    except ValueError:
        return -1


def bump_highest(current_highest: str, new_status: str) -> str:
    if stage_rank(new_status) < 0:
        return current_highest or ""
    if stage_rank(new_status) >= stage_rank(current_highest or "discovered"):
        return new_status
    return current_highest or new_status
