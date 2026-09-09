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
    "MISSING_FACT",
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
CONTROL_REQUIRED_READBACK = ("key", "owner_run_id", "notes")
CONTROL_LEASE_READBACK = ("key", "owner_run_id", "acquired_at", "expires_at")
DEGREE_LEVEL_REPEAT_KEY = "degree_level_gate_missed_at_discovery"
INCIDENT_ID_RE = re.compile(r"^INC-(\d{8})-(\d{1,3})$")

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
class ControlWritePlan:
    action: str
    row_index: Optional[int]
    key: str
    notes: str


def locate_row_by_key(
    rows: Sequence[Mapping[str, Any]],
    key: str,
    field: str = "key",
) -> Optional[int]:
    target = normalize_text(key)
    matches = [
        index
        for index, row in enumerate(rows)
        if normalize_text(str(row.get(field) or "")) == target
    ]
    if len(matches) > 1:
        raise ValueError(f"duplicate {field} {key}")
    if not matches:
        return None
    return matches[0]


def control_row_is_writable(row: Mapping[str, Any], intended_key: str) -> bool:
    existing = normalize_text(str(row.get("key") or ""))
    if not existing:
        return False
    return existing == normalize_text(intended_key)


def inspect_visible_control_row(
    row: Mapping[str, Any],
    intended_key: str,
) -> ControlWritePlan:
    existing = normalize_text(str(row.get("key") or ""))
    if not existing:
        return ControlWritePlan(
            "abort",
            None,
            intended_key,
            "do not write a visually empty row",
        )
    if existing != normalize_text(intended_key):
        return ControlWritePlan(
            "abort",
            None,
            intended_key,
            "visible row has a different key",
        )
    return ControlWritePlan("update", None, intended_key, "visible row is the intended key")


def plan_control_write(
    rows: Sequence[Mapping[str, Any]],
    key: str,
) -> ControlWritePlan:
    index = locate_row_by_key(rows, key, "key")
    if index is None:
        return ControlWritePlan("append", None, key, "append new control key")
    return ControlWritePlan("update", index, key, "update existing control key")


def control_write_persisted(
    after_rows: Sequence[Mapping[str, Any]],
    *,
    key: str,
    intended: Mapping[str, Any],
    protected_keys: Sequence[str] = (),
    before_rows: Sequence[Mapping[str, Any]] = (),
) -> bool:
    index = locate_row_by_key(after_rows, key, "key")
    if index is None:
        return False
    row = after_rows[index]
    for field, value in intended.items():
        if str(row.get(field) or "") != str(value):
            return False
    before_by_key = {
        normalize_text(str(row.get("key") or "")): row
        for row in before_rows
        if str(row.get("key") or "").strip()
    }
    for protected in protected_keys:
        protected_norm = normalize_text(protected)
        if protected_norm == normalize_text(key):
            continue
        prior = before_by_key.get(protected_norm)
        if prior is None:
            continue
        later_index = locate_row_by_key(after_rows, protected, "key")
        if later_index is None:
            return False
        later = after_rows[later_index]
        for field in CONTROL_LEASE_READBACK:
            if str(later.get(field) or "") != str(prior.get(field) or ""):
                return False
    return True


def lease_checkpoint_notes(job_key: str, last_stage: str) -> str:
    return f"checkpoint job_key={job_key} last_stage={last_stage}"


def parse_lease_checkpoint(notes: str) -> Optional[Tuple[str, str]]:
    text = notes or ""
    job_match = re.search(r"job_key=([A-Za-z0-9._:-]+)", text)
    stage_match = re.search(r"last_stage=([A-Za-z0-9._:-]+)", text)
    if not job_match or not stage_match:
        return None
    return job_match.group(1), stage_match.group(1)


def plan_run_log_write(
    rows: Sequence[Mapping[str, Any]],
    run_id: str,
) -> ControlWritePlan:
    index = locate_row_by_key(rows, run_id, "run_id")
    if index is None:
        return ControlWritePlan("append", None, run_id, "append new run_log row")
    return ControlWritePlan("update", index, run_id, "update existing run_log row")


def parse_incident_id(value: str) -> Optional[Tuple[str, int]]:
    match = INCIDENT_ID_RE.match((value or "").strip())
    if not match:
        return None
    return match.group(1), int(match.group(2))


def next_incident_id(existing: Sequence[str], day: str) -> str:
    compact = (day or "").replace("-", "")
    if len(compact) != 8 or not compact.isdigit():
        raise ValueError("incident day must be YYYY-MM-DD or YYYYMMDD")
    used = {
        number
        for parsed in (parse_incident_id(raw) for raw in existing)
        if parsed and parsed[0] == compact
        for number in (parsed[1],)
    }
    next_number = max(used) + 1 if used else 1
    return f"INC-{compact}-{next_number:03d}"


def incident_ids_are_unique(existing: Sequence[str]) -> bool:
    values = [str(raw).strip() for raw in existing if str(raw).strip()]
    if len(values) != len(set(values)):
        return False
    parsed = [parse_incident_id(value) for value in values]
    valid = [item for item in parsed if item]
    return len(valid) == len(set(valid))


def _marker_without_negation(text: str, marker: str) -> bool:
    for match in re.finditer(re.escape(marker), text):
        prefix = text[max(0, match.start() - 28) : match.start()]
        if re.search(r"\b(not|no longer|except)\b.{0,20}$", prefix):
            continue
        return True
    return False


def degree_level_hard_skip(jd_text: str) -> Optional[str]:
    text = normalize_text(jd_text)
    if not text:
        return None
    phd_markers = (
        "phd only",
        "ph.d. only",
        "ph.d only",
        "doctoral students only",
        "doctoral candidates only",
        "phd students only",
        "phd candidates only",
        "must be a current phd",
        "must be pursuing a phd",
        "must be enrolled in a phd",
        "must be enrolled in a ph.d",
        "candidates must be pursuing a phd",
    )
    undergrad_markers = (
        "undergraduate students only",
        "undergraduates only",
        "current undergraduate students only",
        "must be an undergraduate",
        "bachelor's students only",
        "bachelors students only",
    )
    if any(_marker_without_negation(text, marker) for marker in phd_markers):
        return "phd_only"
    if any(_marker_without_negation(text, marker) for marker in undergrad_markers):
        return "undergrad_only"
    return None


_CLOSED_PAGE_RE = re.compile(
    r"(?:\b404\b|page not found|no longer open|no longer accepting|"
    r"(?:this |the )?(?:job|requisition|posting|application)(?: has been)? "
    r"(?:removed|closed))"
)


def closed_posting_action(page_signal: str) -> str:
    text = normalize_text(page_signal)
    if _CLOSED_PAGE_RE.search(text):
        return "skip_no_sibling"
    return "continue"


_STATUS_RE = re.compile(r"\b(f-1|f1|j-1|j1|m-1|m1)\b")
_YES_OR_NO_RE = re.compile(r"\byes\s+or\s+no\b|\bno\s+or\s+yes\b")
_NEGATION_RE = re.compile(r"\b(not|never|do not|don't|dont|cannot|must not)\b")
_ANSWER_YES_RE = re.compile(r"\b(?:answer|select|choose|pick)\s+yes\b")
_ANSWER_NO_RE = re.compile(r"\b(?:answer|select|choose|pick)\s+no\b")


def _explicit_status_answer(text: str) -> Optional[str]:
    normalized = normalize_text(text)
    if not normalized or not _STATUS_RE.search(normalized):
        return None
    if _YES_OR_NO_RE.search(normalized):
        return None
    has_yes = bool(_ANSWER_YES_RE.search(normalized))
    has_no = bool(_ANSWER_NO_RE.search(normalized))
    if has_yes and has_no:
        return None
    if _NEGATION_RE.search(normalized) and (has_yes or has_no):
        return None
    if has_yes:
        return "yes"
    if has_no:
        return "no"
    return None


def _unclear_status_instruction(*texts: str) -> bool:
    for text in texts:
        normalized = normalize_text(text)
        if not normalized or not _STATUS_RE.search(normalized):
            continue
        if re.search(r"\b(answer|select|choose|pick)\b", normalized):
            return True
    return False


@dataclass(frozen=True)
class SponsorshipFacts:
    future_sponsorship_required: Optional[bool]
    standing_form_answer: Optional[str]


def _optional_bool(value: Any) -> Optional[bool]:
    if value is True or value is False:
        return value
    text = normalize_text(str(value or ""))
    if text in {"true", "yes"}:
        return True
    if text in {"false", "no"}:
        return False
    return None


def _yes_no_token(value: Any) -> Optional[str]:
    text = normalize_text(str(value or ""))
    if text in {"yes", "true", "answer_yes", "answer yes"}:
        return "yes"
    if text in {"no", "false", "answer_no", "answer no"}:
        return "no"
    return None


def load_sponsorship_facts(root: Optional[Path] = None) -> SponsorshipFacts:
    base = Path(root) if root else ROOT
    data = load_yaml(base / "knowledge" / "work_authorization.yaml")
    if not isinstance(data, dict):
        raise ValueError("work_authorization.yaml must be a mapping")
    visa = ((data.get("form_strategy") or {}).get("visa_sponsorship") or {})
    return SponsorshipFacts(
        future_sponsorship_required=_optional_bool(data.get("future_sponsorship_required")),
        standing_form_answer=_yes_no_token(visa.get("form_answer")),
    )


def _broad_sponsorship_from_facts(facts: SponsorshipFacts) -> Tuple[str, str]:
    derived = None
    if facts.future_sponsorship_required is True:
        derived = "yes"
    elif facts.future_sponsorship_required is False:
        derived = "no"
    mapping = facts.standing_form_answer
    if derived and mapping and derived != mapping:
        return "leave_unresolved", "fact_mapping_conflict"
    if derived:
        return f"answer_{derived}", "canonical_fact"
    if mapping:
        return f"answer_{mapping}", "standing_form_answer"
    return "leave_unresolved", "sponsorship_fact_unknown"


def sponsorship_form_action(
    *,
    widget_text: str,
    explicit_status_instruction: str = "",
    names_non_us_countries_only: bool = False,
    says_work_authorization_not_sponsorship: bool = False,
    facts: Optional[SponsorshipFacts] = None,
) -> Tuple[str, str]:
    instructed = _explicit_status_answer(explicit_status_instruction) or _explicit_status_answer(
        widget_text
    )
    if instructed == "yes":
        return "answer_yes", "explicit_status_instruction"
    if instructed == "no":
        return "answer_no", "explicit_status_instruction"
    if instructed is None and _unclear_status_instruction(
        explicit_status_instruction, widget_text
    ):
        return "leave_unresolved", "explicit_status_instruction_unclear"
    if names_non_us_countries_only:
        return "leave_unresolved", "country_specific_sponsorship"
    if says_work_authorization_not_sponsorship:
        return "leave_unresolved", "work_authorization_wording"
    text = normalize_text(widget_text)
    if "work authorization" in text and "sponsorship" not in text:
        return "leave_unresolved", "work_authorization_wording"
    return _broad_sponsorship_from_facts(facts if facts is not None else load_sponsorship_facts())


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
