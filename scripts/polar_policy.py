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

INCIDENT_CATEGORY_ALIASES = {
    "ONE_OFF_UI": "UI_ONE_OFF",
    "LOCAL_PRIVATE": "LOCAL_PRIVATE_FACT",
    "MISSING_ARTIFACT": "MISSING_DOCUMENT",
    "DURABLE_POLICY": "FACT_POLICY",
}

MAINTENANCE_DISPOSITIONS = (
    "FIX",
    "OBSERVE",
    "LOCAL_ONLY",
    "NO_ACTION",
    "FIXED_ALREADY",
)

PERFORMANCE_PRIORITY = (
    "correctness_integrity",
    "duplicate_submit_risk",
    "repeated_blockers",
    "repeated_time_sinks",
    "cosmetic_one_off",
)

MAINTENANCE_PLAYBOOK_WHEN = {
    "interrogate": (
        "A report claim is ambiguous or may be misleading. "
        "Challenge the premise before any code change."
    ),
    "arena": (
        "At least two credible fixes have meaningful tradeoffs. "
        "Do not run it for an obvious one-path fix."
    ),
    "architect": (
        "The lesson needs a new durable data shape, state machine, "
        "compiler contract, or GitHub/Sheet/local-private boundary."
    ),
}

POLAR_PRODUCTION_TITLE_RE = re.compile(r"^\[Polar Production\] (\d{4}-\d{2}-\d{2})$")

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


def load_submit_gates(root: Optional[Path] = None) -> Dict[str, Any]:
    base = Path(root) if root else ROOT
    data = load_yaml(base / "config" / "submit_gates.yaml")
    if not isinstance(data, dict):
        raise ValueError("submit_gates.yaml must be a mapping")
    return data


def lease_ttl_minutes(root: Optional[Path] = None) -> int:
    raw = (load_operator(root).get("lease") or {}).get("ttl_minutes")
    if raw is None:
        raise ValueError("lease.ttl_minutes is missing from polar_operator.yaml")
    return int(raw)


def lease_refresh_minutes(root: Optional[Path] = None) -> int:
    raw = (load_operator(root).get("lease") or {}).get(
        "refresh_if_remaining_below_minutes"
    )
    if raw is None:
        raise ValueError(
            "lease.refresh_if_remaining_below_minutes is missing from polar_operator.yaml"
        )
    return int(raw)


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
    ttl_minutes: Optional[int] = None,
    refresh_below_minutes: Optional[int] = None,
    key: str = LEASE_KEY,
) -> LeaseDecision:
    ttl = lease_ttl_minutes() if ttl_minutes is None else ttl_minutes
    refresh_after = (
        lease_refresh_minutes()
        if refresh_below_minutes is None
        else refresh_below_minutes
    )
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
    expiry = (now + timedelta(minutes=ttl)).isoformat()
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
        if remaining <= timedelta(minutes=refresh_after):
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


@dataclass(frozen=True)
class ApplyRunCaps:
    max_new_jobs: int
    reserved_priority_slots: int
    max_regular_submissions_per_local_day: int
    prioritized_auto_submit: bool


@dataclass(frozen=True)
class PrioritySubmitDecision:
    permitted: bool
    reason: str


def _positive_int(value: Any, label: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a positive integer") from exc
    if number <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return number


def resolve_apply_run_caps(
    canary: Mapping[str, Any],
    polar_local: Mapping[str, Any],
) -> ApplyRunCaps:
    max_jobs = _positive_int(canary.get("max_jobs_per_run"), "canary.max_jobs_per_run")
    regular_alias = _positive_int(
        canary.get("max_regular_jobs_per_run"),
        "canary.max_regular_jobs_per_run",
    )
    gate_cap = _positive_int(
        polar_local.get("regular_submit_cap_per_run"),
        "polar_local.regular_submit_cap_per_run",
    )
    if not (max_jobs == regular_alias == gate_cap):
        raise ValueError(
            "apply run cap mismatch: canary.max_jobs_per_run, "
            "canary.max_regular_jobs_per_run, and "
            "polar_local.regular_submit_cap_per_run must be the same "
            "shared new-execution pool, not additive numbers"
        )
    day_canary = _positive_int(
        canary.get("max_regular_submissions_per_local_day"),
        "canary.max_regular_submissions_per_local_day",
    )
    day_gate = _positive_int(
        polar_local.get("regular_submit_cap_per_local_day"),
        "polar_local.regular_submit_cap_per_local_day",
    )
    if day_canary != day_gate:
        raise ValueError(
            "regular day cap mismatch between polar_operator canary "
            "and submit_gates polar_local"
        )
    reserved = canary.get("reserved_priority_slots_per_run")
    try:
        reserved_slots = int(reserved)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "canary.reserved_priority_slots_per_run must be an integer"
        ) from exc
    if reserved_slots < 0 or reserved_slots > max_jobs:
        raise ValueError(
            "reserved_priority_slots_per_run must be between 0 and max_jobs_per_run"
        )
    auto = canary.get("prioritized_auto_submit")
    gate_auto = polar_local.get("prioritized_auto_submit")
    if bool(auto) != bool(gate_auto):
        raise ValueError(
            "prioritized_auto_submit mismatch between polar_operator canary "
            "and submit_gates polar_local"
        )
    return ApplyRunCaps(
        max_new_jobs=max_jobs,
        reserved_priority_slots=reserved_slots,
        max_regular_submissions_per_local_day=day_canary,
        prioritized_auto_submit=bool(auto),
    )


def apply_run_caps(root: Optional[Path] = None) -> ApplyRunCaps:
    operator = load_operator(root)
    gates = load_submit_gates(root)
    return resolve_apply_run_caps(
        operator.get("canary") or {},
        gates.get("polar_local") or {},
    )


@dataclass(frozen=True)
class MaintenancePolicy:
    chatgpt_required: bool
    chatgpt_role: str
    cursor_reads_report_directly: bool
    status: str
    recommended_cron_et: str
    report_title_pattern: str


@dataclass(frozen=True)
class MaintenanceDecision:
    disposition: str
    category: str
    reason: str


def resolve_maintenance_policy(raw: Mapping[str, Any]) -> MaintenancePolicy:
    chatgpt_required = bool(raw.get("chatgpt_required"))
    if chatgpt_required:
        raise ValueError(
            "maintenance.chatgpt_required must be false. "
            "ChatGPT is optional and must not gate Cursor"
        )
    reads_direct = raw.get("cursor_reads_report_directly")
    if reads_direct is False:
        raise ValueError("maintenance.cursor_reads_report_directly must be true")
    return MaintenancePolicy(
        chatgpt_required=False,
        chatgpt_role=str(raw.get("chatgpt_role") or "optional_independent_review"),
        cursor_reads_report_directly=True,
        status=str(raw.get("status") or "disabled_until_proven"),
        recommended_cron_et=str(raw.get("recommended_cron_et") or "35 22 * * *"),
        report_title_pattern=str(
            raw.get("report_title_pattern") or "[Polar Production] YYYY-MM-DD"
        ),
    )


def load_maintenance_policy(root: Optional[Path] = None) -> MaintenancePolicy:
    operator = load_operator(root)
    return resolve_maintenance_policy(operator.get("maintenance") or {})


def maintenance_contract(root: Optional[Path] = None) -> Dict[str, str]:
    policy = load_maintenance_policy(root)
    return {
        "chatgpt_required": "false",
        "chatgpt_role": policy.chatgpt_role,
        "cursor_reads_report_directly": "true",
        "needs_browser_lock": "false",
        "recommended_cron_et": policy.recommended_cron_et,
        "report_title_pattern": policy.report_title_pattern,
        "status": policy.status,
        "classify_with": "polar_policy.classify_maintenance_item",
    }


def polar_production_issue_title(report_date: str) -> str:
    return f"[Polar Production] {report_date}"


def parse_polar_production_title(title: str) -> Optional[str]:
    match = POLAR_PRODUCTION_TITLE_RE.match((title or "").strip())
    if not match:
        return None
    return match.group(1)


def maintenance_input_ready(
    *,
    github_issue_title: str = "",
    report_body: str = "",
) -> Tuple[bool, str]:
    body = (report_body or "").strip()
    report_date = parse_polar_production_title(github_issue_title)
    if report_date and body:
        return True, "github_issue"
    if body and not (github_issue_title or "").strip():
        return True, "supplied_report"
    return False, "missing_report"


def canonicalize_incident_category(raw: str) -> str:
    text = normalize_text(raw).upper().replace(" ", "_")
    return INCIDENT_CATEGORY_ALIASES.get(text, text)


def classify_maintenance_item(
    *,
    category: str,
    recurrence: int = 1,
    high_risk_correctness: bool = False,
    mechanistic_evidence: bool = False,
    already_fixed_on_main: bool = False,
    local_private: bool = False,
) -> MaintenanceDecision:
    canonical = canonicalize_incident_category(category)
    if already_fixed_on_main:
        return MaintenanceDecision("FIXED_ALREADY", canonical, "current_main_already_fixes_it")
    if local_private or canonical == "LOCAL_PRIVATE_FACT":
        return MaintenanceDecision("LOCAL_ONLY", canonical, "local_private_fact")
    if canonical == "NO_ACTION":
        return MaintenanceDecision("NO_ACTION", canonical, "marked_no_action")
    if high_risk_correctness:
        return MaintenanceDecision("FIX", canonical, "high_risk_correctness")
    if canonical == "QUEUE_STATE":
        return MaintenanceDecision("FIX", canonical, "queue_state_integrity")
    repeated = recurrence >= 2 or mechanistic_evidence
    if repeated and canonical in {
        "PERFORMANCE",
        "DEDUP",
        "WRITING",
        "TRIAGE",
        "FACT_POLICY",
        "AUTH",
        "MISSING_DOCUMENT",
        "DURABLE_BUG",
        "DURABLE_POLICY",
    }:
        return MaintenanceDecision("FIX", canonical, "recurring_or_mechanistic")
    if canonical == "UI_ONE_OFF":
        return MaintenanceDecision("OBSERVE", canonical, "one_off_ui")
    return MaintenanceDecision("OBSERVE", canonical, "insufficient_evidence")


def writing_row_is_complete(row: Mapping[str, Any]) -> bool:
    question = str(row.get("exact_question") or "").strip()
    answer = str(row.get("answer_used") or "").strip()
    evidence = str(row.get("evidence_note") or "").strip()
    return bool(question and answer and evidence)


def writing_log_rows_for_job(
    rows: Sequence[Mapping[str, Any]],
    job_key: str,
) -> List[Mapping[str, Any]]:
    key = normalize_text(job_key)
    return [
        row
        for row in rows
        if normalize_text(str(row.get("job_key") or "")) == key
    ]


def writing_log_status(
    *,
    job_key: str,
    custom_questions: Sequence[str],
    writing_rows: Sequence[Mapping[str, Any]],
) -> PrioritySubmitDecision:
    questions = [str(q).strip() for q in custom_questions if str(q or "").strip()]
    if not questions:
        return PrioritySubmitDecision(True, "no_custom_questions")
    job_rows = writing_log_rows_for_job(writing_rows, job_key)
    for question in questions:
        matches = [
            row
            for row in job_rows
            if normalize_text(str(row.get("exact_question") or ""))
            == normalize_text(question)
        ]
        if not matches:
            return PrioritySubmitDecision(False, "writing_log_missing_question")
        if not any(str(row.get("answer_used") or "").strip() for row in matches):
            return PrioritySubmitDecision(False, "writing_log_blank_answer")
        if not any(str(row.get("evidence_note") or "").strip() for row in matches):
            return PrioritySubmitDecision(False, "writing_log_missing_evidence")
        if not any(writing_row_is_complete(row) for row in matches):
            return PrioritySubmitDecision(False, "writing_log_incomplete")
    return PrioritySubmitDecision(True, "writing_log_complete")


def priority_submit_permitted(
    *,
    weight: str,
    plane: str,
    prioritized_auto_submit: bool,
    job_key: str,
    custom_questions: Sequence[str],
    writing_rows: Sequence[Mapping[str, Any]],
) -> PrioritySubmitDecision:
    if normalize_text(weight) != "prioritized":
        return PrioritySubmitDecision(True, "regular_weight_does_not_use_this_gate")
    if normalize_text(plane) != "polar_local":
        return PrioritySubmitDecision(False, "cursor_cloud_prioritized_needs_review_packet")
    if not prioritized_auto_submit:
        return PrioritySubmitDecision(False, "prioritized_auto_submit_disabled")
    return writing_log_status(
        job_key=job_key,
        custom_questions=custom_questions,
        writing_rows=writing_rows,
    )


def _sort_key(row: Mapping[str, str]) -> Tuple[str, str]:
    return (
        str(row.get("updated_at") or row.get("discovered_at") or ""),
        str(row.get("job_key") or ""),
    )


def select_apply_batch(
    rows: Sequence[Mapping[str, str]],
    *,
    max_new_jobs: Optional[int] = None,
    reserved_priority_slots: Optional[int] = None,
    root: Optional[Path] = None,
) -> ApplyBatch:
    if max_new_jobs is None or reserved_priority_slots is None:
        caps = apply_run_caps(root)
        if max_new_jobs is None:
            max_new_jobs = caps.max_new_jobs
        if reserved_priority_slots is None:
            reserved_priority_slots = caps.reserved_priority_slots
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
