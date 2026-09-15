#!/usr/bin/env python3
"""Shared runtime section builders.

One canonical source, two rendered runtimes. `build_polar_runtime.py`
renders POLAR_RUNTIME.md for Polar Local. `build_grokbot_runtime.py`
renders GROKBOT_RUNTIME.md for the Grok Bot applier. Both call the
builders here. A line tagged for both executors must appear with the
same bytes in both files. Executor-specific mechanics are tagged so the
Polar render stays byte-identical to the compile that Polar already
loads.

Pure functions over loaded YAML. No network. No secrets.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union
from urllib.parse import urlparse

from js_lib import (
    canonical_url,
    company_role_location_key,
    jobright_ids_from_text,
    normalize_text,
    read_rows,
)
from polar_policy import (
    ApplyRunCaps,
    CONTROL_COLUMNS,
    CONTROL_KEY_DUPLICATE_REPEAT_KEY,
    DEGREE_LEVEL_REPEAT_KEY,
    HEARTBEAT_COLUMNS,
    INCIDENT_LOG_COLUMNS,
    JOBRIGHT_ONBOARDING_REPEAT_KEY,
    LEARNING_REPORTS_COLUMNS,
    QUEUE_COLUMNS,
    RUN_LOG_COLUMNS,
    WRITING_LOG_COLUMNS,
    document_availability,
    format_approved_document_line,
)
from polar_resume_attach import runtime_lines as resume_runtime_lines
from polar_resume_attach import submit_check as resume_submit_check

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

POLAR = "polar"
GROK = "grok"
EXECUTORS = (POLAR, GROK)
ALL_EXECUTORS = frozenset(EXECUTORS)

BLOCKING_ATTEMPT_OUTCOMES = frozenset(
    {"submitted_verified", "submitted_unverified", "in_progress"}
)
HTTP_URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)

PROFILE_SKIP_KEYS = {
    "phone",
    "email",
    "mobile",
    "password",
    "cookie",
    "cookies",
    "otp",
    "secret",
}


# ---------------------------------------------------------------------------
# Executor-tagged lines
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Line:
    text: str
    executors: frozenset = ALL_EXECUTORS


Row = Union[str, Line]


def shared(text: str) -> Line:
    return Line(text, ALL_EXECUTORS)


def polar_only(text: str) -> Line:
    return Line(text, frozenset({POLAR}))


def grok_only(text: str) -> Line:
    return Line(text, frozenset({GROK}))


def variant(*, polar: str, grok: str) -> Tuple[Line, Line]:
    """Two wordings for one slot. Both executors get exactly one line."""
    return (polar_only(polar), grok_only(grok))


def assert_executor(executor: str) -> str:
    if executor not in EXECUTORS:
        raise ValueError(f"unknown executor {executor!r}; expected one of {EXECUTORS}")
    return executor


def render_lines(rows: Sequence[Row], executor: str) -> List[str]:
    assert_executor(executor)
    out: List[str] = []
    for row in rows:
        if isinstance(row, Line):
            if executor in row.executors:
                out.append(row.text)
        else:
            out.append(row)
    return out


def join_rows(rows: Sequence[Row], executor: str) -> str:
    return "\n".join(render_lines(rows, executor))


def shared_texts(rows: Sequence[Row]) -> List[str]:
    """Lines that both executors must render byte-identically."""
    out: List[str] = []
    for row in rows:
        if isinstance(row, Line) and row.executors == ALL_EXECUTORS and row.text:
            out.append(row.text)
    return out


# ---------------------------------------------------------------------------
# Loading and small formatting helpers
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> Any:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def bullet(items: Sequence[str], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{item}" for item in items if item)


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return " ".join(text.split())


def forbidden_profile_values(profile: Dict[str, Any]) -> List[str]:
    values: List[str] = []
    for key in PROFILE_SKIP_KEYS:
        raw = profile.get(key)
        if raw is None:
            continue
        text = str(raw).strip()
        if text and text.upper() != "[REDACTED]":
            values.append(text)
    return values


def assert_operator_columns(operator: Dict[str, Any]) -> None:
    expected = {
        "queue_columns": QUEUE_COLUMNS,
        "writing_log_columns": WRITING_LOG_COLUMNS,
        "heartbeat_columns": HEARTBEAT_COLUMNS,
        "run_log_columns": RUN_LOG_COLUMNS,
        "incident_log_columns": INCIDENT_LOG_COLUMNS,
        "control_columns": CONTROL_COLUMNS,
        "learning_reports_columns": LEARNING_REPORTS_COLUMNS,
    }
    for key, columns in expected.items():
        got = operator.get(key)
        if got != columns:
            raise SystemExit(f"{key} in polar_operator.yaml does not match polar_policy.py")
    spec = (operator.get("capabilities") or {}).get("google_sheets")
    if not isinstance(spec, dict):
        raise SystemExit("polar_operator.yaml capabilities.google_sheets is required")
    if spec.get("literal_name_required") is not False:
        raise SystemExit("google_sheets.literal_name_required must be false")
    if spec.get("ask_to_add_connector") is not False:
        raise SystemExit("google_sheets.ask_to_add_connector must be false")
    if spec.get("sheet_title") != "Polar Jobs":
        raise SystemExit("google_sheets.sheet_title must be Polar Jobs")


@dataclass
class RuntimeSources:
    profile: Dict[str, Any]
    auth: Dict[str, Any]
    form: Dict[str, Any]
    triage: Dict[str, Any]
    priority: Dict[str, Any]
    targets: Dict[str, Any]
    writing: Dict[str, Any]
    bank: Dict[str, Any]
    roles: Dict[str, Any]
    operator: Dict[str, Any]
    gates: Dict[str, Any]
    documents: List[Dict[str, Any]] = field(default_factory=list)


def load_sources(root: Optional[Path] = None) -> RuntimeSources:
    base = Path(root) if root else ROOT
    operator = load_yaml(base / "knowledge" / "polar_operator.yaml")
    assert_operator_columns(operator)
    return RuntimeSources(
        profile=load_yaml(base / "config" / "profile.yaml") or {},
        auth=load_yaml(base / "knowledge" / "work_authorization.yaml") or {},
        form=load_yaml(base / "knowledge" / "form_strategy.yaml") or {},
        triage=load_yaml(base / "knowledge" / "discovery_triage_rules.yaml") or {},
        priority=load_yaml(base / "knowledge" / "application_priority.yaml") or {},
        targets=load_yaml(base / "knowledge" / "target_roles.yaml") or {},
        writing=load_yaml(base / "knowledge" / "written_response_bank.yaml") or {},
        bank=load_yaml(base / "knowledge" / "evidence_bank.yaml") or {},
        roles=load_yaml(base / "knowledge" / "role_families.yaml") or {},
        operator=operator,
        gates=load_yaml(base / "config" / "submit_gates.yaml") or {},
        documents=document_availability(base),
    )


# ---------------------------------------------------------------------------
# Form-answer rendering (section A standing answers)
# ---------------------------------------------------------------------------


def auto_map_ban(block: Dict[str, Any]) -> str:
    banned = block.get("do_not_auto_map")
    if not banned:
        return ""
    if isinstance(banned, str):
        phrases = [md_escape(banned)]
    else:
        phrases = [md_escape(x) for x in banned if md_escape(x)]
    if not phrases:
        return ""
    extra = (
        " DO NOT AUTO-MAP: "
        + " / ".join(phrases)
        + ". Do not treat that wording as this answer. Leave it unresolved."
    )
    seen = md_escape(block.get("do_not_auto_map_seen", ""))
    if seen:
        extra += f" Seen: {seen}"
    return extra


def form_answer_line(name: str, block: Any) -> str:
    if not isinstance(block, dict):
        return ""
    if block.get("execution") == "leave_unresolved":
        when = md_escape(block.get("when", name))
        return (
            f"{name}: leave unresolved. Do not apply a historical Yes or No "
            f"while it conflicts with a stored fact. When: {when}"
            + auto_map_ban(block)
        )
    if block.get("status") == "needs_human" or block.get("form_answer") == "unknown":
        when = md_escape(block.get("when", name))
        return (
            f"{name}: leave for Junyi. No approved answer. When: {when}"
            + auto_map_ban(block)
        )
    answer = block.get("form_answer")
    if answer is None and "harvard_masters" in block:
        return (
            f"{name}: Harvard master's GPA {block.get('harvard_masters')}; "
            f"Emory undergrad {block.get('emory_undergrad')}; "
            f"single box {block.get('if_only_one_gpa_box')}"
        )
    if answer is None and "if_page_has_no_number" in block:
        return (
            f"{name}: listed minimum when the page prints a range; "
            f"otherwise {block.get('if_page_has_no_number')}"
        )
    if answer is None and "when_jd_has_no_term" in block:
        return (
            f"{name}: use the posting term when named; "
            f"otherwise {block.get('when_jd_has_no_term')}"
        )
    if "prefer_in_order" in block and answer is None:
        order = ", ".join(str(x) for x in block["prefer_in_order"])
        return f"{name}: prefer in order {order}"
    if answer is None and block.get("rule"):
        line = f"{name}: {md_escape(block.get('rule'))}"
        confirmed = block.get("junyi_confirmed_values")
        if isinstance(confirmed, dict) and confirmed:
            bits = [f"{k} {md_escape(v)}" for k, v in confirmed.items()]
            line += " Confirmed: " + "; ".join(bits) + "."
        return line + auto_map_ban(block)
    if answer is None:
        return ""
    shown = "(blank)" if answer == "" else md_escape(answer)
    when = md_escape(block.get("when", ""))
    extra = f" When: {when}." if when else ""
    return f"{name}: {shown}.{extra}" + auto_map_ban(block)


def eligible_skills(bank: Dict[str, Any]) -> List[str]:
    skills = bank.get("skills") or {}
    rows: List[str] = []
    for key, body in skills.items():
        if not isinstance(body, dict):
            continue
        if body.get("verified") is True and body.get("resume_eligible") is True:
            name = md_escape(body.get("name") or key)
            level = md_escape(body.get("level") or "unknown")
            rows.append(f"{name} ({level})")
    return rows


def project_lines(bank: Dict[str, Any]) -> List[str]:
    projects = bank.get("projects") or {}
    rows: List[str] = []
    for key, body in projects.items():
        if not isinstance(body, dict):
            continue
        title = md_escape(body.get("title") or key)
        org = md_escape(body.get("org") or "")
        role = md_escape(body.get("role") or "")
        dates = md_escape(body.get("dates") or "")
        rows.append(f"{title} / {org} / {role} / {dates}")
    return rows


# ---------------------------------------------------------------------------
# Historical duplicate guard (section K)
# ---------------------------------------------------------------------------


def _http_urls(text: str) -> List[str]:
    return HTTP_URL_RE.findall(text or "")


def _is_jobright_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == "jobright.ai" or host.endswith(".jobright.ai")


def _employer_urls(text: str) -> List[str]:
    keys: List[str] = []
    for raw in _http_urls(text):
        if _is_jobright_host(raw):
            continue
        key = canonical_url(raw)
        if key:
            keys.append(key)
    return keys


def _usable_company_role_location(company: str, role: str, location: str = "") -> str:
    if not normalize_text(company) and not normalize_text(role):
        return ""
    return company_role_location_key(company, role, location)


GUARD_CHECKERS = {
    POLAR: "discover-jobs-hourly and apply-ready-jobs check this guard in addition to the Sheet.",
    GROK: "grok-apply-jobs checks this guard in addition to the Sheet.",
}


@dataclass(frozen=True)
class HistoricalGuard:
    jobright_ids: tuple[str, ...]
    urls: tuple[str, ...]
    company_role_locations: tuple[str, ...]

    @classmethod
    def compile(cls, data_dir: Optional[Path] = None) -> "HistoricalGuard":
        data = Path(data_dir) if data_dir else DATA
        ids: Set[str] = set()
        urls: Set[str] = set()
        crls: Set[str] = set()

        for row in read_rows(data / "applications.csv"):
            ids.update(jobright_ids_from_text(row.get("source_detail", "")))
            ids.update(jobright_ids_from_text(row.get("job_url", "")))
            ids.update(jobright_ids_from_text(row.get("posting_url", "")))
            urls.update(_employer_urls(row.get("job_url", "")))
            urls.update(_employer_urls(row.get("posting_url", "")))
            crl = _usable_company_role_location(
                row.get("company", ""), row.get("role", ""), row.get("location", "")
            )
            if crl:
                crls.add(crl)

        for row in read_rows(data / "job_decisions.csv"):
            ids.update(jobright_ids_from_text(row.get("url", "")))
            urls.update(_employer_urls(row.get("url", "")))
            crl = _usable_company_role_location(
                row.get("company", ""), row.get("role", ""), row.get("location", "")
            )
            if crl:
                crls.add(crl)

        for row in read_rows(data / "apply_attempts.csv"):
            if row.get("outcome", "") not in BLOCKING_ATTEMPT_OUTCOMES:
                continue
            apply_url = row.get("apply_url", "")
            ids.update(jobright_ids_from_text(apply_url))
            urls.update(_employer_urls(apply_url))

        return cls(
            jobright_ids=tuple(sorted(ids)),
            urls=tuple(sorted(urls)),
            company_role_locations=tuple(sorted(crls)),
        )

    def render(self, executor: str = POLAR) -> str:
        assert_executor(executor)
        return "\n".join(
            [
                "An empty Google Sheet is not a clean slate.",
                "The GitHub ledger already holds applied, closed, ready, and in-progress keys.",
                GUARD_CHECKERS[executor],
                "If any key matches, do not set READY_REGULAR or READY_PRIORITY.",
                "Do not auto-Submit.",
                "Write SKIP or leave the row non-READY.",
                "Match order: Jobright id, then trusted employer/application URL, then company|role|location.",
                "",
                "Jobright ids:",
                bullet(list(self.jobright_ids)),
                "",
                "Employer / application URLs:",
                bullet(list(self.urls)),
                "",
                "Company|role|location:",
                bullet(list(self.company_role_locations)),
            ]
        )


def section_historical_guard(executor: str, data_dir: Optional[Path] = None) -> str:
    return HistoricalGuard.compile(data_dir).render(executor)


# ---------------------------------------------------------------------------
# A. Candidate facts
# ---------------------------------------------------------------------------


def candidate_fact_bullets(src: RuntimeSources) -> List[str]:
    """Fact lines. Identical bytes in every runtime that renders them."""
    profile = src.profile
    auth = src.auth
    always = src.form.get("always") or {}
    anchors = src.triage.get("profile_anchors") or {}
    auth_form = auth.get("form_strategy") or {}
    citizenship = md_escape(
        auth.get("citizenship_country")
        or auth_form.get("citizenship_country", {}).get("form_answer")
    )
    visa = md_escape(auth.get("current_status") or "F-1")
    program_end = md_escape(auth.get("program_end_date") or anchors.get("program_end_date"))
    commencement = md_escape(auth.get("commencement_date") or anchors.get("commencement_date"))
    earliest_ft = md_escape(
        auth.get("earliest_full_time_start") or profile.get("earliest_start_date")
    )
    visa_block = auth_form.get("visa_sponsorship") or {}
    sponsorship_form = md_escape(visa_block.get("form_answer") or "unknown")
    sponsorship_execution = md_escape(visa_block.get("execution") or "")
    return [
        f"Legal name: {md_escape(profile.get('legal_name') or profile.get('name'))}",
        f"Preferred name: {md_escape(profile.get('preferred_name'))}",
        f"Location: {md_escape(profile.get('location'))}",
        f"School: {md_escape(profile.get('school'))}",
        f"Degree: {md_escape(profile.get('degree'))}",
        f"LinkedIn: {md_escape(profile.get('linkedin'))}",
        f"GitHub: {md_escape(profile.get('github'))}",
        f"Personal website: {md_escape((always.get('personal_website') or {}).get('form_answer') or '')}",
        f"Citizenship country (form and fact): {citizenship}",
        "Permanent resident elsewhere since citizenship: No",
        f"Current visa type when asked: {visa}",
        f"Future sponsorship required (standing fact): {auth.get('future_sponsorship_required')}",
        f"Required future-sponsorship widget: {sponsorship_form}. Execution: {sponsorship_execution or 'answer the asked fact only'}.",
        "Answer only the asked semantic. Do not volunteer F-1, OPT, EAD, citizenship, or sponsorship on a field that did not ask.",
        "Optional identity or status fields stay blank. Required and clear fields get the one matching fact. Required and unclear fields BLOCK that job only.",
        "If the form names F-1, J-1, or M-1 and clearly says answer Yes or answer No, follow that polarity on that widget. If polarity is unclear, leave the field.",
        "Country-only sponsorship lists and work-authorization-without-sponsorship wording stay unresolved when required, and blank when optional.",
        "H-1B-named widget: No",
        "Authorized-for-any-employer widget: Yes",
        "Required currently-authorized widget: leave unresolved. The current-authorization fact is unknown.",
        "Required EAD widget: No. Required OPT-approval widget: No. Required OPT-eligibility widget: Yes.",
        f"Program end / I-20 date: {program_end}",
        f"Commencement: {commencement}",
        f"Graduation date widget: {program_end}",
        f"Year-only graduation widget: {md_escape((always.get('graduation_year_on_forms') or {}).get('form_answer') or '2027')}",
        f"Earliest full-time start: {earliest_ft}",
        f"Preferred intern term: {md_escape(anchors.get('preferred_intern_term'))}",
        f"Remote ok: {anchors.get('remote_ok', profile.get('remote_ok', False))}",
        f"Preferred work mode: {md_escape(anchors.get('preferred_work_mode') or 'in-person or hybrid')}",
        "Search country: United States. Any US city is fine. Boston preferred.",
        "Non-US work location is a skip.",
        "Eligible to begin employment immediately: Yes",
        "US Person / export control: I am not a U.S. Person. Export-control country China.",
    ]


def standing_answer_lines(src: RuntimeSources) -> List[str]:
    always = src.form.get("always") or {}
    standing: List[str] = []
    for name, block in always.items():
        line = form_answer_line(name, block)
        if line:
            standing.append(line)
    return standing


def approved_document_lines(src: RuntimeSources) -> List[str]:
    return [format_approved_document_line(doc) for doc in src.documents]


def facts_rows(src: RuntimeSources) -> List[Row]:
    doc_lines = approved_document_lines(src)
    return [
        *variant(
            polar="Phone numbers live in the local Polar profile. They are not compiled here.",
            grok="Phone numbers are not compiled here. If a required phone field is empty after Jobright autofill, leave it and mark BLOCKED on that job only. Do not invent or look up a phone number.",
        ),
        shared("Normal ATS email, candidate account email, preferred application contact, and password-reset email"),
        *variant(
            polar="use the dedicated local APPLICATION mailbox from Polar or the browser profile.",
            grok="use the APPLICATION mailbox that Jobright autofill writes and that is signed in on this computer's browser.",
        ),
        *variant(
            polar="If a field asks for school email, university email, or institutional email, use the local academic mailbox.",
            grok="If a field asks for school email, university email, or institutional email and autofill left it empty, leave it and mark BLOCKED on that job only. The academic mailbox is not available on this computer.",
        ),
        *variant(
            polar="The application Outlook inbox is readable in the Polar browser. polar_policy.email_verification_action is read_application_outlook.",
            grok="The application Outlook inbox is readable in this computer's browser. polar_policy.email_verification_action is read_application_outlook.",
        ),
        shared("Retrieve an email verification code or link from that inbox and continue. Do not abandon a recoverable email OTP."),
        *variant(
            polar="Do not write the code into the Sheet, git, or a report.",
            grok="Do not write the code into the Sheet, git, chat, Bot memory, /workspace, or a report.",
        ),
        shared("A resume parser that fills the Harvard or school mailbox into a normal ATS account, contact, or password-reset field is wrong."),
        *variant(
            polar="Correct that field to the local APPLICATION mailbox before continuing. Do not finish account creation on the academic mailbox.",
            grok="Correct that field to the APPLICATION mailbox before continuing. Do not finish account creation on the academic mailbox.",
        ),
        shared("Do not create a second employer account only to change email."),
        shared("polar_policy.contact_email_action is the engineer table for that reread."),
        *variant(
            polar="street_address_source: local Polar or private profile. Do not compile or log the street value.",
            grok="street_address_source: none on this computer. If a required street field is empty after autofill, leave it and mark BLOCKED on that job only. Do not compile or log the street value.",
        ),
        "",
        polar_only("Approved documents. Attach only when the form asks for that class. Never paste contents."),
        polar_only(bullet(doc_lines) if doc_lines else "- No approved documents are registered."),
        polar_only(""),
        bullet(candidate_fact_bullets(src)),
        "",
        *variant(
            polar="Standing widget answers (owner-confirmed). Apply them verbatim when you fill a widget that is empty, in error, or in a fast-validation class (section P).",
            grok="Standing widget answers (owner-confirmed). Apply them verbatim.",
        ),
        polar_only("This list is a fill table. Do not walk it against every populated widget after Autofill."),
        grok_only("These lines are shared byte-for-byte with the Polar render. Where one names an older autofill sidebar by product name, read it as the autofill tool on this computer, the Jobright extension."),
        "",
        bullet(standing_answer_lines(src)),
    ]


def section_facts(src: RuntimeSources, executor: str) -> str:
    return join_rows(facts_rows(src), executor)


# ---------------------------------------------------------------------------
# C. Triage rules and apply-time skips
# ---------------------------------------------------------------------------


def triage_rule_lines(src: RuntimeSources) -> List[str]:
    rules = src.triage.get("guide_rules") or []
    rule_lines: List[str] = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_lines.append(
            f"`{rule.get('id')}` ({rule.get('severity')}, default {rule.get('default_decision')}): "
            f"{md_escape(rule.get('guidance'))}"
        )
    return rule_lines


def triage_rows(src: RuntimeSources) -> List[Row]:
    return [
        *variant(
            polar="Triage at apply time from the Jobright card and the employer JD. Dedupe against the Sheet and section K.",
            grok="Triage at apply time from the Jobright Agent job card and the employer JD. Dedupe against the Sheet and the historical duplicate guard in section G8.",
        ),
        polar_only("discover-jobs-hourly is not apply admission."),
        "",
        bullet(triage_rule_lines(src)),
        "",
        shared("An exclusive graduation or enrollment window is an eligibility note, not a skip."),
        shared("Do not invent a graduation date."),
        shared("Sponsorship unknown, unavailable, or generally not offered is not a skip."),
        shared("F-1 or OPT mentioned on a board is not a skip."),
        shared("Do not invent work_model, location, graduation windows, or H1B facts."),
        shared("Blank location is not an automatic skip."),
        *variant(
            polar="apply-ready-jobs reads the full employer posting immediately after it is open, before login or form fill.",
            grok="grok-apply-jobs reads the full employer posting immediately after it is open, before login or form fill.",
        ),
        shared("A fuller JD can reveal a 2026 start, a start before 2027-01-18, a non-US role, PhD-only, undergraduate-only, or TS-SCI/polygraph skip."),
        shared("Those degree-level misses share repeat_key degree_level_gate_missed_at_discovery."),
    ]


def section_triage(src: RuntimeSources, executor: str) -> str:
    return join_rows(triage_rows(src), executor)


# ---------------------------------------------------------------------------
# D. Regular vs prioritized policy
# ---------------------------------------------------------------------------


def prioritized_signal_lines(src: RuntimeSources) -> List[str]:
    weight = src.priority.get("application_weight") or {}
    subfields = (weight.get("prioritized") or {}).get("subfields") or []
    sub_lines: List[str] = []
    for item in subfields:
        if isinstance(item, dict):
            sub_lines.append(f"{item.get('id')}: {md_escape(item.get('meaning'))}")
    return sub_lines + [
        "fortune_500_or_major: a major company Junyi values, not every large employer.",
        "biotech_health_ai: biomedical or health AI with real product fit.",
        "biostat_data_science_bio: unusually strong biostatistics, data-science, or bio fit.",
        "personal_fit: unusually strong personal fit. Rare.",
        "Do not mark a generic analyst or data role prioritized only because the title contains data.",
    ]


STRONG_PRIORITY_SIGNALS = [
    "fde (title)",
    "gtc_2026 (company on the NVIDIA GTC 2026 list)",
    "confirmed_prioritized (YAML list match)",
    "clear fortune_500_or_major",
    "clear biotech_health_ai",
]

WEAK_PRIORITY_SIGNALS = [
    "startup or prestige hints",
    "personal_fit",
    "generic data or analyst titles",
]


def weight_rows(src: RuntimeSources, caps: ApplyRunCaps) -> List[Row]:
    weight = src.priority.get("application_weight") or {}
    regular = (weight.get("regular") or {}).get("meaning", "")
    prioritized = (weight.get("prioritized") or {}).get("meaning", "")
    return [
        *variant(
            polar=f"Regular: {md_escape(regular)}",
            grok="Regular: fast, truthful execution. Jobright-generated resume or the checksum-verified Perfect Resume. Do not upload the two-page master. Short, prompt-faithful free response. Submit only under the grok_cloud gate in section G6.",
        ),
        *variant(
            polar=f"Prioritized: {md_escape(prioritized)}",
            grok="Prioritized: extra judgment, a JD-tuned resume from the evidence bank only, a real answer to the prompt, full form prep, and a mandatory writing_log row for every meaningful custom question. Not open on the grok_cloud plane. Owner decision 2026-09-15: blocked until later.",
        ),
        "",
        "Prioritized signals, only when strongly applicable:",
        "",
        bullet(prioritized_signal_lines(src)),
        "",
        *variant(
            polar="Polar may mark weight=prioritized when a strong configured signal is visible on the Jobright card or JD.",
            grok="Grok may mark weight=prioritized when a strong configured signal is visible on the Jobright card or JD.",
        ),
        shared("That mark is writing depth and post-submit audit. It is not apply-queue admission and not a slot reservation."),
        *variant(
            polar="Polar Local may Submit a prioritized row when writing_log is complete and final validation passes.",
            grok="Prioritized rows are not open on the grok_cloud plane. Owner decision 2026-09-15: BLOCKED until later. Do not claim a job whose card or JD already shows a strong prioritized signal; leave that Sheet row untouched so Polar Local can own it. If the signal appears only after the claim, stop that job before any Submit, write blocker prioritized_not_open_on_grok_cloud with last_stage, leave the row IN_PROGRESS under this run, and continue. When this run's run_log result is final and not PARTIAL, Polar recovers that claim by the abandoned-claim rule.",
        ),
        shared("It is not permission to invent company facts."),
        "",
        "Strong signals. Mark weight prioritized:",
        bullet(STRONG_PRIORITY_SIGNALS),
        "",
        "Weak signals. Stay regular unless clearly justified:",
        bullet(WEAK_PRIORITY_SIGNALS),
        "",
        shared("FDE / Forward Deployed titles stay and are marked prioritized."),
        shared("Do not claim customer on-site FDE work already done."),
        polar_only("READY_* rows are inventory. Do not FIFO them as apply source."),
        *variant(
            polar=f"Priority slot reservation is {caps.reserved_priority_slots}. Jobright ranks new cards.",
            grok=f"Priority slot reservation is {caps.reserved_priority_slots}. Jobright ranks. Grok claims at most {caps.max_considered} jobs per run, and only regular ones.",
        ),
    ]


def section_weight(src: RuntimeSources, executor: str, caps: ApplyRunCaps) -> str:
    return join_rows(weight_rows(src, caps), executor)


# ---------------------------------------------------------------------------
# E. Resume-cluster selection
# ---------------------------------------------------------------------------


def role_cluster_lines(src: RuntimeSources) -> List[str]:
    clusters = src.targets.get("role_clusters") or {}
    cluster_lines: List[str] = []
    for name, body in clusters.items():
        if not isinstance(body, dict):
            continue
        titles = ", ".join(str(x) for x in body.get("titles") or [])
        cluster_lines.append(f"{name}: {titles}")
    return cluster_lines


RESUME_TAIL_ROWS: List[Row] = [
    shared("Title families are job taxonomy only. resume_cluster is not a file."),
]

RESUME_TAILORING_ROWS: List[Row] = [
    shared("Prioritized rows may tailor from the evidence bank only when the JD justifies it."),
    shared("Do not invent lab hardware, customer on-site FDE, or technologies that are not resume-eligible."),
]


def polar_section_resume(src: RuntimeSources) -> str:
    return "\n".join(
        [
            *resume_runtime_lines(),
            "",
            *render_lines(RESUME_TAIL_ROWS, POLAR),
            bullet(role_cluster_lines(src)),
            "",
            *render_lines(RESUME_TAILORING_ROWS, POLAR),
        ]
    )


# ---------------------------------------------------------------------------
# F. Writing evidence and writing rules
# ---------------------------------------------------------------------------


def writing_rows(src: RuntimeSources) -> List[Row]:
    ideology = src.writing.get("ideology") or {}
    why = src.writing.get("why_company_shape") or {}
    fde = src.roles.get("forward_deployed_engineer") or {}
    return [
        shared(f"writing_observation_mode: {src.operator.get('writing_observation_mode')}"),
        shared("For every nontrivial free-response question, append one writing_log row."),
        shared("Record company, role, exact question, answer used, and a short evidence note."),
        shared("Regular writing may still submit when the facts support it."),
        shared("Prioritized writing must be logged before Submit. Missing writing_log is a Submit blocker."),
        "",
        shared("Ideology bank is for week, meaning, and culture prompts only."),
        "Use when:",
        bullet([md_escape(x) for x in ideology.get("use_when") or []]),
        "",
        "Do not use ideology when:",
        bullet([md_escape(x) for x in ideology.get("do_not_use_when") or []]),
        "",
        "Why-us shape:",
        bullet([md_escape(x) for x in why.get("parts") or []]),
        "",
        "Why-us must not:",
        bullet([md_escape(x) for x in why.get("do_not") or []]),
        "",
        shared("Tone: " + md_escape(why.get("tone"))),
        shared("Punctuation: " + md_escape((why.get("punctuation") or {}).get("rule"))),
        "",
        "Verified resume-eligible skills:",
        bullet(eligible_skills(src.bank)),
        "",
        "Projects you may name at the evidence-bank ceiling:",
        bullet(project_lines(src.bank)),
        "",
        shared("FDE ceiling: " + md_escape(fde.get("closest_verified_ceiling"))),
        "FDE do not claim:",
        bullet([md_escape(x) for x in fde.get("do_not_claim") or []]),
        "",
        shared("Per-application drafts live in docs/apply/written_answers/. A file there is not a submit."),
    ]


def section_writing(src: RuntimeSources, executor: str) -> str:
    return join_rows(writing_rows(src), executor)


WRITING_TIER_LINES = [
    "Tier 0 standing widget: a compiled standing answer matches the exact question. Fill it verbatim. No writing_log row.",
    "Tier 1 short factual: the prompt asks a fact or a one-line preference such as relocation, salary, start date, or location interest. One or two sentences from compiled facts. No generation. writing_log row if nontrivial.",
    "Tier 2 Jobright-generated draft: Jobright placed a generated answer on the form or in the Missing fields panel. Review, do not rewrite. Check that it answers every clause, starts from their mission, invents no employer fact, metric, FDE, or on-site claim, mentions no immigration unless asked, carries no resume-internal label, uses no em dash or hyphen aside, and has no I-do-not-outsource hedge. Pass: keep. Minor fail: trim the offending sentence. Major fail: regenerate once if Jobright offers it, then re-check. writing_log evidence_note starts with source=jobright_generated; edit=none, trim, or regenerated. Two fails go to Tier 3.",
    "Tier 3 executor-written: no usable draft and the prompt is a real Why-us or motivation question. Regular weight: one short prompt-faithful paragraph, at most about 120 words, from the compiled Why-us shape and verified surfaces only. writing_log evidence_note starts with source=executor_written. Facts missing from the bank go to Tier 4.",
    "Tier 4 blocked for drafting: the prompt needs facts the evidence bank does not hold, or a required essay longer than about 250 words, or a company-specific claim the bank cannot support. Do not write. Leave the field. BLOCKED with blocker writing_needs_draft. Continue the batch. writing_log row with the exact question and an empty answer. Cursor or Junyi drafts into docs/apply/written_answers/ and the next run finds an approved answer.",
    "Per-run budget for executor-written text is about 400 words. A long form must not turn the clicker into an essayist.",
    "Jobright generation is allowed because it is Jobright's own product path. It is reviewed, never trusted.",
    "Do not store phrasings in Bot memory. Learning flows through the writing_log tab into the nightly packet.",
]


# ---------------------------------------------------------------------------
# G. Blocker handling
# ---------------------------------------------------------------------------


def blocker_rows() -> List[Row]:
    return [
        shared("A required new application account is normal work, not a blocker by default."),
        *variant(
            polar="Attempt ordinary user-facing completion for account creation, a browser-generated strong password, saved credentials, forgot-password, email verification, email OTP, SMS on the Mac, ordinary consent, multi-page forms, unknown widgets, and required writing.",
            grok="Attempt ordinary user-facing completion for account creation, a browser-generated strong password saved in this computer's browser, saved credentials, forgot-password, email verification, email OTP, ordinary consent, multi-page forms, unknown widgets, and required writing.",
        ),
        *variant(
            polar="Email OTP and verification links are recoverable. Polar may open the application Outlook inbox in the browser and continue. polar_policy.email_verification_action.",
            grok="Email OTP and verification links are recoverable. Grok may open the application Outlook inbox in this computer's browser and continue. polar_policy.email_verification_action.",
        ),
        shared("Do not mark a verification-code gate unrecoverable. Do not abandon a recoverable application."),
        *variant(
            polar="User-only remaining steps: SMS on the Mac when Outlook has no code, hardware security key, CAPTCHA after a normal browser attempt, and phone-app push.",
            grok="User-only remaining steps: SMS-only verification with no Outlook alternative, hardware security key, CAPTCHA after a normal browser attempt, phone-app push, an ID or SSN upload, and payment. Hand those to Junyi with a takeover request or mark BLOCKED. Do not type credentials or codes into chat.",
        ),
        polar_only("A PREFERENCES.md or Polar site note on jobright.ai that says the mailbox cannot be read is stale. GitHub wins."),
        shared("Use only normal browser flows for security or anti-abuse challenges."),
        shared("Do not implement CAPTCHA-bypass services, fingerprint spoofing, or anti-abuse evasion."),
        *variant(
            polar="Escalate to BLOCKED only after this local environment cannot complete a required step, and that step is not a recoverable Outlook code.",
            grok="Escalate to BLOCKED only after this computer cannot complete a required step, and that step is not a recoverable Outlook code.",
        ),
        *variant(
            polar="A blocked job must not stall the worker. Persist the blocker and continue to the next Jobright card.",
            grok="A blocked job must not stall the worker. Persist the blocker and continue to the next claimed job.",
        ),
        shared("ATS family is diagnostic metadata only. Do not organize work by ATS worker class."),
        *variant(
            polar="Jobright extension owns autofill. Trust the form DOM. See section P.",
            grok="Jobright extension owns autofill. Trust the form DOM. See section G1.",
        ),
        polar_only("Jobright Autofill is the default filler. Polar is anomaly detection and targeted repair, not a full-form auditor."),
        polar_only("Do not click Simplify Copilot Autofill on this path."),
        shared("Do not read every queue row. polar_policy.queue_read_scope is targeted."),
    ]


def section_blockers(executor: str) -> str:
    return join_rows(blocker_rows(), executor)


def applicant_account_lines(src: RuntimeSources) -> List[str]:
    """Executor-neutral applicant-account rule from form_strategy.yaml.

    Rendered into the Grok runtime now. The Polar render waits for the
    next Polar compile window (docs/automation/GROKBOT.md, sequencing).
    """
    block = src.form.get("applicant_account_rule") or {}
    if not isinstance(block, dict) or not block.get("rule"):
        return []
    lines = [md_escape(block.get("rule"))]
    lines.extend(md_escape(x) for x in block.get("conditions") or [])
    cross = block.get("cross_executor") or {}
    if isinstance(cross, dict) and cross.get("meaning"):
        lines.append(md_escape(cross.get("meaning")))
    for old in block.get("supersedes") or []:
        lines.append(f"Superseded pre_jobright text: {md_escape(old)}")
    return lines


# ---------------------------------------------------------------------------
# H. Submission behavior
# ---------------------------------------------------------------------------


def regular_submit_rows() -> List[Row]:
    """The regular Submit checklist. Grok drops only the Copilot clauses."""
    return [
        *variant(
            polar="Duplicate check passes against the Sheet and section K.",
            grok="Duplicate check passes against the Sheet and the historical duplicate guard in section G8.",
        ),
        shared("Company and title on the page match the queue row."),
        shared(
            resume_submit_check()
            or "Approved production resume is Perfect Resume. Do not upload the two-page master or any ai_infra file."
        ),
        shared("Identity fields (First Name, Last Name, application email) are correct after a visible form DOM read-back. Extension sidebar progress is not proof."),
        shared("Normal account and contact email fields show the APPLICATION mailbox, not the academic mailbox."),
        shared("Referral / how-heard is blank unless a verified fact exists. Clear invented Event referrals."),
        shared("Required factual fields are resolved from this runtime or left for Junyi."),
        shared("No unsupported claim was invented."),
        shared("Writing is evidence-grounded."),
        shared("application_weight is regular."),
        *variant(
            polar="Fast validation pass passes (section P): identity, work authorization, eligibility-critical, required-empty-or-error, required legal/compliance. Populated routine widgets with no error and no known failure class are trusted, not re-read.",
            grok="Final review of visible widgets passes.",
        ),
        shared("One final Submit is used."),
        *variant(
            polar="Employer-page confirmation text is visible. Copilot Completed is not confirmation.",
            grok="Employer-page confirmation text is visible. Jobright Apply Now is not confirmation.",
        ),
        shared("Queue confirmation, submitted_at, and the visible resume filename match that page. polar_policy.submit_outcome is the engineer table."),
        shared("If the page confirmation is missing or the queue readback does not match, status is SUBMISSION_UNKNOWN. Do not click Submit again."),
    ]


def regular_submit_items(executor: str) -> List[str]:
    return render_lines(regular_submit_rows(), executor)


def polar_section_submit(src: RuntimeSources, caps: ApplyRunCaps) -> str:
    gates = src.gates
    polar_local = gates.get("polar_local") or {}
    cloud = gates.get("cursor_cloud") or {}
    cloud_ladder = cloud.get("gates") or gates.get("gates") or {}
    cloud_cap = cloud.get("regular_submit_cap_per_run", gates.get("regular_submit_cap_per_run"))
    return "\n".join(
        [
            "Two Submit planes. Do not mix them.",
            "",
            "cursor_cloud still uses ATS-family gates in config/submit_gates.yaml `cursor_cloud.gates`.",
            f"Cloud open gates: {md_escape(cloud_ladder)}.",
            f"Cloud regular cap per run: {cloud_cap}.",
            "Cloud G2 remains closed. Polar Local does not inherit those ATS gates.",
            "",
            "polar_local uses capability and policy checks, not ATS family.",
            f"Gate model: {polar_local.get('gate_model')}.",
            f"Per-run worker budget on apply-ready-jobs: {caps.max_considered} considered candidates, not {caps.max_considered} submissions.",
            f"READY_PRIORITY reservation: {caps.reserved_priority_slots}. Allocation is obsolete. Jobright ranks.",
            "An empty READY queue is a valid start.",
            "Another apply-ready-jobs run has its own budget. There is no shared daily regular submission pool.",
            f"Prioritized auto-submit: {caps.prioritized_auto_submit}.",
            "",
            "A regular job may be submitted once only when every item holds:",
            bullet(regular_submit_items(POLAR)),
            "",
            "A prioritized job may be submitted once when every regular item holds and polar_policy.priority_submit_permitted is true.",
            "That function is false when writing_log is missing a custom question, the answer is blank, or the evidence note is blank.",
            "Include prioritized SUBMITTED rows in the daily digest under PRIORITY APPLICATIONS SUBMITTED TODAY.",
            "REVIEW_READY is only for a missing owner fact or an explicit hold.",
        ]
    )


# ---------------------------------------------------------------------------
# I. Prohibited fabrication
# ---------------------------------------------------------------------------


FABRICATION_ITEMS = [
    "metrics",
    "projects",
    "domain experience",
    "referrals",
    "citizenship other than China",
    "clearance",
    "customer on-site experience",
    "employment or employers",
    "technologies that are not verified and resume-eligible",
    "GPA, SAT, or ACT values other than the standing GPA answers",
    "passwords, cookies, OTP codes, or 2FA secrets in git, the Sheet, or email",
]


def fabrication_rows() -> List[Row]:
    return [
        shared("Do not invent any of the following:"),
        bullet(FABRICATION_ITEMS),
        "",
        shared("If a required fact is missing, leave the widget and mark needs_human or BLOCKED."),
        shared("Extension sidebar Completed is not proof a widget has a value. Look at the form DOM."),
        polar_only("Copilot Completed is not proof a widget has a value."),
        polar_only("That sidebar rule catches required widgets that are still empty. It is not a license to re-read every populated widget. Section P scopes the pass."),
    ]


def section_fabrication(executor: str) -> str:
    return join_rows(fabrication_rows(), executor)


# ---------------------------------------------------------------------------
# J. Runtime status semantics
# ---------------------------------------------------------------------------


STATUS_LINES = [
    "NEW: seen and written. Claimable when Jobright shows the card.",
    "READY_REGULAR: historical inventory, regular weight. Not silent apply FIFO.",
    "READY_PRIORITY: historical inventory, prioritized writing depth. Not silent apply FIFO.",
    "IN_PROGRESS: this run owns the job via claim_run_id. Different jobs may be IN_PROGRESS at the same time.",
    "REVIEW_READY: form is complete but Polar stopped for a missing owner fact or explicit hold.",
    "SUBMITTED: employer-page confirmation is visible and the queue readback matches that page.",
    "SUBMISSION_UNKNOWN: Submit may have happened, or the page confirmation is missing, or the queue readback does not match. Verify before any retry. Never blindly resubmit. Copilot Completed is not confirmation.",
    "BLOCKED: this environment cannot finish a required step. Queue continues.",
    "SKIP: hard skip, closed posting, or owner skip.",
]

GROK_STATUS_LINES = [
    "NEW: seen and written. Claimable when Jobright shows the job.",
    "READY_REGULAR: historical inventory, regular weight. Not silent apply FIFO. Grok never reads it as a queue.",
    "READY_PRIORITY: historical inventory, prioritized writing depth. Not silent apply FIFO. Grok never reads it as a queue.",
    "IN_PROGRESS: this run owns the job via claim_run_id. Different jobs may be IN_PROGRESS at the same time.",
    "REVIEW_READY: form is complete but the executor stopped for a missing owner fact or an explicit hold, including the closed grok_cloud Submit gate.",
    "SUBMITTED: employer-page confirmation is visible and the queue readback matches that page.",
    "SUBMISSION_UNKNOWN: Submit may have happened, or the page confirmation is missing, or the queue readback does not match. Verify before any retry. Never blindly resubmit.",
    "BLOCKED: this environment cannot finish a required step. Queue continues.",
    "SKIP: hard skip, closed posting, owner skip, or already_applied_on_ats.",
]


def status_rows(src: RuntimeSources) -> List[Row]:
    operator = src.operator
    statuses = operator.get("statuses") or []
    stages = operator.get("last_stages") or []
    recovery = operator.get("recovery_order") or []
    columns = operator.get("queue_columns") or []
    return [
        shared("GitHub holds configuration, policy, evidence, and audit."),
        shared("The Google Sheet holds runtime queue state. It is not a second applications.csv."),
        *variant(
            polar="An empty Sheet is not a clean slate. Check section K in addition to the Sheet.",
            grok="An empty Sheet is not a clean slate. Check the historical duplicate guard below in addition to the Sheet.",
        ),
        "",
        "Statuses:",
        polar_only(bullet(STATUS_LINES)),
        grok_only(bullet(GROK_STATUS_LINES)),
        "",
        shared("Allowed status values: " + ", ".join(str(x) for x in statuses)),
        shared("Allowed last_stage values: " + ", ".join(str(x) for x in stages)),
        shared("Recovery order: " + " then ".join(str(x) for x in recovery) + "."),
        polar_only("If the Mac slept during Job 6 IN_PROGRESS and the claim is abandoned or self-owned, resume Job 6. Do not restart Job 1."),
        "",
        shared("Queue columns: " + ", ".join(str(x) for x in columns)),
        shared(md_escape(operator.get("job_key_rule"))),
        "",
        polar_only("discover-jobs-hourly is retired from apply admission. It never applies."),
        *variant(
            polar="apply-ready-jobs inspects SUBMISSION_UNKNOWN first, then abandoned or self-owned IN_PROGRESS.",
            grok="grok-apply-jobs inspects its own SUBMISSION_UNKNOWN and self-owned IN_PROGRESS rows first. It recovers abandoned claims only when the run id prefix is G-. Polar claims are Polar's.",
        ),
        polar_only("New work comes from Jobright recommendations. READY_* is inventory only."),
        shared("Queue reads are targeted. Do not dump READY_* backlog as apply FIFO."),
        polar_only("daily-job-summary never includes passwords, OTP codes, or cookies."),
        polar_only("production-learning-daily writes a sanitized report and does not change GitHub policy."),
        polar_only("Fence pre_jobright incidents. polar_policy.incident_learning_era. Do not treat Simplify/Copilot/READY FIFO/IBM-funnel as current reliability evidence."),
    ]


def section_status(src: RuntimeSources, executor: str) -> str:
    return join_rows(status_rows(src), executor)


# ---------------------------------------------------------------------------
# L. Schema-safe Sheet writes
# ---------------------------------------------------------------------------


def sheet_write_rows() -> List[Row]:
    return [
        shared("Read the actual header row before every Sheet write."),
        shared("Build a field-name to column mapping from those headers."),
        shared("Write by header name. Write explicit blanks. Do not shorten a positional row."),
        shared("apply_url_confidence must stay in its named column even when the value is none or blank."),
        shared("After an important queue write, read back job_key, status, last_stage, and claim_run_id."),
        shared("If job_key, status, or last_stage do not match, repair those fields."),
        shared("If claim_run_id is another run_id, do not overwrite it."),
        *variant(
            polar="If the queue header has no claim_run_id, do not append it from apply or discover.",
            grok="If the queue header has no claim_run_id, do not append it. Write OWNER_ACTION_REQUIRED and stop this run.",
        ),
        polar_only("polar-sheet-migration is the only schema mutator for that column."),
        polar_only("Control writes locate the row by key. Never pick a visually empty row."),
        polar_only("Read every row with that key first. polar_policy.plan_control_write aborts when two rows share the key."),
        polar_only(f"That abort uses repeat_key {CONTROL_KEY_DUPLICATE_REPEAT_KEY}. Do not invent control_duplicate_key variants."),
        polar_only("If the visible row has a different key, or no key, abort. github_write_canary must not overwrite polar_browser."),
        polar_only("After a canary write, reread polar_browser key, owner_run_id, acquired_at, and expires_at."),
        grok_only("Never write the control, heartbeat, or learning_reports tabs. Those belong to Polar Local and Cursor. This executor writes queue, run_log, incident_log, and writing_log only."),
        *variant(
            polar="Commit the edit, then reread key, owner_run_id, and notes. Looking correct is not persistence.",
            grok="Commit the edit, then reread the named fields you wrote. Looking correct is not persistence.",
        ),
        shared("Do not increment simplify_attempted or simplify_fallback_count. Those columns are historical."),
        polar_only("google_sheets means the Google connector can read and write Polar Jobs. Drive Find-file and Sheets tools count. A connector named google_sheets is not required."),
        polar_only("Browser sheets.google.com is not google_sheets. Do not ask the owner to add a connector when Google connector tools already exist."),
        grok_only("google_sheets on this computer means a Google Sheets plugin or connector that can read and write Polar Jobs. Reading sheets.google.com in the browser is not that capability."),
        grok_only("If google_sheets is missing, report ENVIRONMENT / CAPABILITY_MISSING in this run's own output and stop before any claim. No claim means no fill and no Submit."),
        grok_only("If the Sheet was reachable at start and a later write fails, do not resubmit and do not invent state. Keep the job note in this conversation, retry the write once, then write an incident with repeat_key grok_sheet_unreachable when the Sheet answers again."),
    ]


def section_sheet_writes(executor: str) -> str:
    return join_rows(sheet_write_rows(), executor)


# ---------------------------------------------------------------------------
# N. Run and incident telemetry
# ---------------------------------------------------------------------------


def telemetry_rows() -> List[Row]:
    return [
        shared("One workflow invocation upserts one run_log row by run_id and copies workflow_version from the instruction file."),
        *variant(
            polar="Mint run_id with polar_policy.mint_run_id on the America/New_York wall clock. Do not use UTC for the suffix.",
            grok="Mint run_id with polar_policy.mint_run_id(executor=grok) on the America/New_York wall clock. The prefix is G-. Do not use UTC for the suffix. Do not mint an R- id.",
        ),
        shared("started_at and ended_at use polar_policy.format_sheet_timestamp. ISO-8601 with a numeric offset. Do not write EDT or EST."),
        shared("A run_log row is not final until polar_policy.run_log_row_is_final is true, including ended_at."),
        shared("Write incident_log rows for material events. Use the small category list in knowledge/polar_operator.yaml."),
        shared("incident_id is INC-YYYYMMDD-NNN with three digits on today's America/New_York date, not UTC."),
        shared("The sequence is monotonic. Reread existing ids for that date before write. The next id is one more than the highest number. If 001 and 003 exist, write 004. 01 and 001 count as the same number. Never reuse."),
        shared("Write incident_log.repeat_key with polar_policy.canonical_repeat_key."),
        shared(f"Jobright Matches onboarding uses repeat_key {JOBRIGHT_ONBOARDING_REPEAT_KEY}."),
        shared("Do not invent jobright_onboarding_* variants."),
        shared(f"Degree-level apply-time skips share repeat_key {DEGREE_LEVEL_REPEAT_KEY}."),
        polar_only(f"Duplicate control-tab keys use repeat_key {CONTROL_KEY_DUPLICATE_REPEAT_KEY}."),
        shared("A missing birth date or OPT-months answer is MISSING_FACT, not MISSING_DOCUMENT."),
        shared("Authorization telemetry uses auth_outcome answered, optional_left_blank, ambiguous_required_blocked, hard_eligibility_skip, or disclosure_prevented."),
        shared("If time was lost, set time_lost_category so later review can explain a 35 minute run versus a 105 minute run."),
        shared("Do not count every click. Coarse stage timing is enough."),
        polar_only("production-learning-daily aggregates today's telemetry into a sanitized Markdown report."),
        grok_only("grok-production-learning-daily finalizes this executor's non-final G- run_log rows and writes Grok environment incidents. It writes no learning packet and no learning_reports row. Polar's production-learning-daily reads today's rows by date, so G- rows land in the existing Polar packet."),
        polar_only("Fence polar_policy.incident_learning_era=pre_jobright. Do not optimize current apply around Simplify or Copilot-as-autofill."),
        grok_only("Cursor Maintenance at 23:00 Eastern is the only consumer of that packet and the only merger. Grok never writes a GitHub Issue, never pushes main, never opens or merges a pull request, and never edits GitHub policy files."),
        shared("Do not put secrets in telemetry."),
    ]


def section_telemetry(executor: str) -> str:
    return join_rows(telemetry_rows(), executor)


# ---------------------------------------------------------------------------
# O. Employer requisition identity
# ---------------------------------------------------------------------------


def requisition_rows() -> List[Row]:
    return [
        shared("After the employer application is resolved, capture employer_requisition_id,"),
        shared("canonical employer apply_url, and ats_job_id."),
        shared("If multiple Jobright rows point at the same employer requisition, keep one canonical row."),
        shared("requisition_submit_blocked ignores SKIP and abandoned IN_PROGRESS, then pick_canonical_requisition_row ranks the rest."),
        shared("That rank is SUBMITTED, SUBMISSION_UNKNOWN, IN_PROGRESS, earlier discovered_at, then job_key."),
        shared("Mark siblings SKIP with the canonical job_key."),
        shared("Do not submit the same employer requisition twice."),
        shared("Jobright ids and company+role+location remain useful. They are not enough once the employer identity is known."),
        *variant(
            polar="Section K still applies.",
            grok="The historical duplicate guard still applies.",
        ),
    ]


def section_requisition(executor: str) -> str:
    return join_rows(requisition_rows(), executor)


# ---------------------------------------------------------------------------
# Shared-line inventory for tests
# ---------------------------------------------------------------------------


def shared_line_inventory(src: RuntimeSources, caps: ApplyRunCaps) -> List[str]:
    """Every line both runtimes must carry byte-identically."""
    rows: List[Row] = []
    rows.extend(facts_rows(src))
    rows.extend(triage_rows(src))
    rows.extend(weight_rows(src, caps))
    rows.extend(writing_rows(src))
    rows.extend(blocker_rows())
    rows.extend(fabrication_rows())
    rows.extend(status_rows(src))
    rows.extend(sheet_write_rows())
    rows.extend(telemetry_rows())
    rows.extend(requisition_rows())
    lines = shared_texts(rows)
    # Rendered as bullets in both runtimes.
    lines.extend(f"- {item}" for item in shared_texts(regular_submit_rows()))
    lines.extend(f"- {item}" for item in candidate_fact_bullets(src))
    lines.extend(f"- {item}" for item in standing_answer_lines(src))
    return lines
