#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import urlparse

from js_lib import canonical_url, normalize_text

ROOT = Path(__file__).resolve().parents[1]

LEASE_KEY = "polar_browser"
LEASE_TTL_MINUTES = 180
LEASE_REFRESH_IF_REMAINING_BELOW_MINUTES = 60

GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/JunyiZhou-Conny/"
    "job-search-2026-2027-starter/main"
)

INCIDENT_CATEGORIES = (
    "UI_ONE_OFF",
    "LOCAL_PRIVATE_FACT",
    "MISSING_DOCUMENT",
    "FACT_POLICY",
    "TRIAGE",
    "QUEUE_STATE",
    "DEDUP",
    "WRITING",
    "AUTH",
    "PERFORMANCE",
    "NO_ACTION",
)

TIME_LOST_CATEGORIES = (
    "AUTH",
    "ACCOUNT_CREATION",
    "SIMPLIFY",
    "MISSING_FACT",
    "MISSING_DOCUMENT",
    "WRITING",
    "DROPDOWN_UI",
    "DUPLICATE",
    "SUBMIT_VERIFY",
    "OTHER",
)

RUN_LOG_RESULTS = (
    "SUCCESS",
    "PARTIAL",
    "FAILED",
    "SKIPPED_LOCKED",
    "NO_WORK",
)

LOCK_RESULTS = (
    "ACQUIRED",
    "REFRESHED",
    "RELEASED",
    "SKIPPED_LOCKED",
    "NOT_REQUIRED",
)

REQUIRED_QUEUE_READBACK = ("job_key", "status", "last_stage")

BROWSER_LOCK_WORKFLOWS = (
    "discover-jobs-hourly",
    "apply-ready-jobs",
)

NO_BROWSER_LOCK_WORKFLOWS = (
    "daily-job-summary",
    "polar-scheduler-heartbeat",
    "production-learning-daily",
    "polar-github-write-canary",
    "chatgpt-production-review",
    "cursor-production-maintenance",
    "polar-sheet-migration",
)

APPLY_URL_CONFIDENCE = "apply_url_confidence"

QUEUE_COLUMNS = [
    "job_key",
    "discovered_at",
    "company",
    "role",
    "location",
    "track",
    "source_url",
    "apply_url",
    APPLY_URL_CONFIDENCE,
    "weight",
    "priority_reason",
    "lane",
    "resume_cluster",
    "status",
    "last_stage",
    "attempt_count",
    "blocker",
    "writing_summary",
    "submitted_at",
    "confirmation",
    "updated_at",
    "employer_requisition_id",
    "ats_job_id",
]

WRITING_LOG_COLUMNS = [
    "job_key",
    "company",
    "role",
    "weight",
    "exact_question",
    "answer_used",
    "evidence_note",
    "recorded_at",
]

HEARTBEAT_COLUMNS = [
    "recorded_at",
    "workflow",
    "result",
    "page_opened",
    "notes",
]

RUN_LOG_COLUMNS = [
    "run_id",
    "workflow",
    "workflow_version",
    "started_at",
    "ended_at",
    "duration_minutes",
    "result",
    "lock_result",
    "jobs_seen",
    "jobs_attempted",
    "submitted_regular",
    "submitted_priority",
    "blocked",
    "skipped",
    "submission_unknown",
    "simplify_attempted",
    "simplify_fallback_count",
    "notes",
]

INCIDENT_LOG_COLUMNS = [
    "incident_id",
    "run_id",
    "job_key",
    "company",
    "stage",
    "category",
    "time_lost_category",
    "severity",
    "summary",
    "evidence",
    "minutes_lost",
    "resolved_in_run",
    "repeat_key",
    "durable_candidate",
    "recorded_at",
]

CONTROL_COLUMNS = [
    "key",
    "owner_run_id",
    "workflow",
    "acquired_at",
    "expires_at",
    "notes",
]

LEARNING_REPORTS_COLUMNS = [
    "report_date",
    "recorded_at",
    "workflow_version",
    "body_markdown",
    "publish_status",
    "github_url",
    "notes",
]

SCHEMA_TABS = {
    "queue": QUEUE_COLUMNS,
    "writing_log": WRITING_LOG_COLUMNS,
    "heartbeat": HEARTBEAT_COLUMNS,
    "run_log": RUN_LOG_COLUMNS,
    "incident_log": INCIDENT_LOG_COLUMNS,
    "control": CONTROL_COLUMNS,
    "learning_reports": LEARNING_REPORTS_COLUMNS,
}

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE_RE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
OTP_ASSIGN_RE = re.compile(r"(?i)\b(otp|2fa|one[ -]?time(?: code| password)?)\s*[:=]\s*\S+")
PASSWORD_ASSIGN_RE = re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*\S+")
COOKIE_ASSIGN_RE = re.compile(
    r"(?i)\b(cookie|set-cookie|session[_ -]?token|storage_state)\s*[:=]\s*\S+"
)
STREET_RE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9.#']+\s+"
    r"(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|"
    r"Court|Ct|Place|Pl|Terrace|Ter)\b",
    re.I,
)
TRANSCRIPT_LEAK_RE = re.compile(
    r"(?i)\b(gpa\s*[:=]\s*\d\.\d{1,3}|credit hours\s*[:=]|course title\s*[:=])"
)

SANITIZE_REPLACEMENTS = (
    (PASSWORD_ASSIGN_RE, "[REDACTED_PASSWORD]"),
    (COOKIE_ASSIGN_RE, "[REDACTED_SECRET]"),
    (OTP_ASSIGN_RE, "[REDACTED_OTP]"),
    (EMAIL_RE, "[REDACTED_EMAIL]"),
    (PHONE_RE, "[REDACTED_PHONE]"),
    (STREET_RE, "[REDACTED_STREET]"),
    (TRANSCRIPT_LEAK_RE, "[REDACTED_TRANSCRIPT]"),
)


def load_yaml(path: Path) -> Any:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_operator(root: Optional[Path] = None) -> Dict[str, Any]:
    base = Path(root) if root else ROOT
    data = load_yaml(base / "knowledge" / "polar_operator.yaml")
    if not isinstance(data, dict):
        raise ValueError("polar_operator.yaml must be a mapping")
    return data


def load_documents(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    base = Path(root) if root else ROOT
    data = load_yaml(base / "knowledge" / "polar_documents.yaml")
    docs = (data or {}).get("documents") or []
    return [row for row in docs if isinstance(row, dict)]


def header_map(headers: Sequence[str]) -> Dict[str, int]:
    mapping: Dict[str, int] = {}
    for index, raw in enumerate(headers):
        name = str(raw or "").strip()
        if name:
            mapping[name] = index
    return mapping


def named_row(headers: Sequence[str], fields: Mapping[str, Any]) -> List[str]:
    mapping = header_map(headers)
    unknown = [key for key in fields if key not in mapping]
    if unknown:
        raise ValueError("unknown sheet fields: " + ", ".join(unknown))
    row = [""] * len(headers)
    for key, value in fields.items():
        row[mapping[key]] = "" if value is None else str(value)
    return row


def readback_fields(headers: Sequence[str], row: Sequence[str]) -> Dict[str, str]:
    mapping = header_map(headers)
    out: Dict[str, str] = {}
    for key in REQUIRED_QUEUE_READBACK:
        index = mapping.get(key)
        if index is None or index >= len(row):
            out[key] = ""
        else:
            out[key] = str(row[index])
    return out


def parse_timestamp(value: str) -> Optional[datetime]:
    text = (value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


@dataclass(frozen=True)
class LeaseDecision:
    action: str
    lock_result: str
    owner_run_id: str
    workflow: str
    expires_at: str
    notes: str


def decide_lease(
    current: Optional[Mapping[str, str]],
    *,
    now: datetime,
    run_id: str,
    workflow: str,
    needs_lock: bool,
    ttl_minutes: int = LEASE_TTL_MINUTES,
    key: str = LEASE_KEY,
) -> LeaseDecision:
    if not needs_lock:
        return LeaseDecision(
            action="skip",
            lock_result="NOT_REQUIRED",
            owner_run_id="",
            workflow=workflow,
            expires_at="",
            notes=f"{key} lock not required for {workflow}",
        )
    row = current or {}
    owner = str(row.get("owner_run_id") or "").strip()
    expires = parse_timestamp(str(row.get("expires_at") or ""))
    expired = expires is None or expires <= now
    expiry = (now + timedelta(minutes=ttl_minutes)).isoformat()
    if owner and owner != run_id and not expired:
        return LeaseDecision(
            action="abort",
            lock_result="SKIPPED_LOCKED",
            owner_run_id=owner,
            workflow=str(row.get("workflow") or ""),
            expires_at=str(row.get("expires_at") or ""),
            notes=f"{key} held by {owner}",
        )
    if owner == run_id and not expired:
        remaining = expires - now if expires else timedelta(0)
        if remaining <= timedelta(minutes=LEASE_REFRESH_IF_REMAINING_BELOW_MINUTES):
            return LeaseDecision(
                action="refresh",
                lock_result="REFRESHED",
                owner_run_id=run_id,
                workflow=workflow,
                expires_at=expiry,
                notes=f"refreshed {key}",
            )
        return LeaseDecision(
            action="hold",
            lock_result="ACQUIRED",
            owner_run_id=run_id,
            workflow=workflow,
            expires_at=str(row.get("expires_at") or expiry),
            notes=f"already holds {key}",
        )
    return LeaseDecision(
        action="acquire",
        lock_result="ACQUIRED",
        owner_run_id=run_id,
        workflow=workflow,
        expires_at=expiry,
        notes=f"acquired {key}",
    )


def release_lease(run_id: str, workflow: str, now: datetime) -> LeaseDecision:
    return LeaseDecision(
        action="release",
        lock_result="RELEASED",
        owner_run_id="",
        workflow=workflow,
        expires_at=now.isoformat(),
        notes=f"released by {run_id}",
    )


@dataclass(frozen=True)
class ApplyBatch:
    recovery: Tuple[str, ...]
    priority: Tuple[str, ...]
    regular: Tuple[str, ...]

    @property
    def job_keys(self) -> Tuple[str, ...]:
        return self.recovery + self.priority + self.regular


def _sort_key(row: Mapping[str, str]) -> Tuple[str, str]:
    return (
        str(row.get("updated_at") or row.get("discovered_at") or ""),
        str(row.get("job_key") or ""),
    )


def select_apply_batch(
    rows: Sequence[Mapping[str, str]],
    *,
    max_new_jobs: int = 3,
    reserved_priority_slots: int = 1,
) -> ApplyBatch:
    unknown = [r for r in rows if r.get("status") == "SUBMISSION_UNKNOWN"]
    in_progress = sorted(
        [r for r in rows if r.get("status") == "IN_PROGRESS"],
        key=_sort_key,
    )
    priority = [r for r in rows if r.get("status") == "READY_PRIORITY"]
    regular = [r for r in rows if r.get("status") == "READY_REGULAR"]
    recovery = [str(r.get("job_key") or "") for r in unknown + in_progress]
    chosen_priority: List[str] = []
    remaining = max_new_jobs
    if reserved_priority_slots > 0 and priority and remaining > 0:
        take = min(reserved_priority_slots, remaining, len(priority))
        chosen_priority = [str(r.get("job_key") or "") for r in priority[:take]]
        remaining -= take
    chosen_regular = [str(r.get("job_key") or "") for r in regular[:remaining]]
    return ApplyBatch(
        recovery=tuple(k for k in recovery if k),
        priority=tuple(k for k in chosen_priority if k),
        regular=tuple(k for k in chosen_regular if k),
    )


def requisition_identity(
    *,
    employer_requisition_id: str = "",
    ats_job_id: str = "",
    apply_url: str = "",
) -> Optional[Tuple[str, str]]:
    req = normalize_text(employer_requisition_id)
    if req:
        return ("requisition", req)
    ats = normalize_text(ats_job_id)
    if ats:
        return ("ats", ats)
    url = canonical_url(apply_url)
    if not url:
        return None
    host = (urlparse(url).hostname or "").lower()
    if host == "jobright.ai" or host.endswith(".jobright.ai"):
        return None
    return ("url", url)


_CANONICAL_STATUSES = (
    "SUBMITTED",
    "SUBMISSION_UNKNOWN",
    "IN_PROGRESS",
    "REVIEW_READY",
    "READY_PRIORITY",
    "READY_REGULAR",
    "BLOCKED",
    "NEW",
)


def pick_canonical_requisition_row(
    rows: Sequence[Mapping[str, str]],
    identity: Tuple[str, str],
) -> Optional[str]:
    matches: List[Mapping[str, str]] = []
    for row in rows:
        key = requisition_identity(
            employer_requisition_id=str(row.get("employer_requisition_id") or ""),
            ats_job_id=str(row.get("ats_job_id") or ""),
            apply_url=str(row.get("apply_url") or ""),
        )
        if key == identity:
            matches.append(row)
    if not matches:
        return None
    ranked = sorted(
        matches,
        key=lambda row: (
            _CANONICAL_STATUSES.index(str(row.get("status") or "NEW"))
            if str(row.get("status") or "NEW") in _CANONICAL_STATUSES
            else 99,
            str(row.get("discovered_at") or ""),
            str(row.get("job_key") or ""),
        ),
    )
    return str(ranked[0].get("job_key") or "") or None


def sibling_job_keys(
    rows: Sequence[Mapping[str, str]],
    identity: Tuple[str, str],
    canonical_job_key: str,
) -> Tuple[str, ...]:
    keys: List[str] = []
    for row in rows:
        job_key = str(row.get("job_key") or "")
        if not job_key or job_key == canonical_job_key:
            continue
        key = requisition_identity(
            employer_requisition_id=str(row.get("employer_requisition_id") or ""),
            ats_job_id=str(row.get("ats_job_id") or ""),
            apply_url=str(row.get("apply_url") or ""),
        )
        if key == identity:
            keys.append(job_key)
    return tuple(keys)


def sanitize_learning_text(text: str) -> str:
    cleaned = text or ""
    for pattern, replacement in SANITIZE_REPLACEMENTS:
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned


def learning_text_is_clean(text: str) -> bool:
    return sanitize_learning_text(text) == (text or "")


def workflow_version(policy_revision: str, body: str) -> str:
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
    revision = (policy_revision or "unknown").strip() or "unknown"
    return f"{revision}+{digest}"


def csv_header(columns: Sequence[str]) -> str:
    return ",".join(columns) + "\n"


def raw_workflow_url(name: str) -> str:
    return f"{GITHUB_RAW_BASE}/generated/polar/workflows/{name}.md"


def raw_runtime_url() -> str:
    return f"{GITHUB_RAW_BASE}/generated/polar/runtime/POLAR_RUNTIME.md"


def bootstrap_prompt(name: str) -> str:
    url = raw_workflow_url(name)
    return (
        f"Open {url}\n"
        "Read it fully.\n"
        f"Follow the latest instructions for this workflow ({name}).\n"
        "Then execute.\n"
        "Do not browse the rest of GitHub.\n"
    )


def document_availability(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    base = Path(root) if root else ROOT
    rows = []
    for doc in load_documents(base):
        rel = str(doc.get("approved_path") or "").strip()
        path = (base / rel) if rel else None
        exists = bool(path and path.is_file())
        rows.append(
            {
                **doc,
                "exists": exists,
                "availability": "in_repo" if exists else "not_in_repo",
            }
        )
    return rows


def needs_browser_lock(workflow: str) -> bool:
    return workflow in BROWSER_LOCK_WORKFLOWS


def parse_contract_block(text: str, heading: str) -> Dict[str, str]:
    marker = f"## {heading}"
    if marker not in text:
        return {}
    rest = text.split(marker, 1)[1]
    body = rest.split("\n## ", 1)[0]
    fields: Dict[str, str] = {}
    for line in body.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            fields[key] = value.strip()
    return fields
