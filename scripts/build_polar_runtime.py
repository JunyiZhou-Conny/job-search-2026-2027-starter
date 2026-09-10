#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from js_lib import (
    canonical_url,
    company_role_location_key,
    jobright_ids_from_text,
    normalize_text,
    read_rows,
)
from polar_policy import (
    COPILOT_REPEAT_KEY,
    COPILOT_STATES,
    CONTROL_COLUMNS,
    ENV_SIMPLIFY_KEY,
    LEASE_KEY,
    HEARTBEAT_COLUMNS,
    INCIDENT_LOG_COLUMNS,
    LEARNING_REPORTS_COLUMNS,
    LOCAL_PREFERENCES_PATH,
    MEMORY_PRECEDENCE,
    PREFERENCE_CLASSES,
    QUEUE_COLUMNS,
    RUN_LOG_COLUMNS,
    WRITING_LOG_COLUMNS,
    apply_run_caps,
    document_availability,
    format_runtime_resolutions,
    load_preference_resolutions,
    raw_runtime_url,
    work_claim_ttl_minutes,
)
from polar_workflows import write_schema_csvs, write_workflows

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md"
DATA = ROOT / "data"

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

SECTION_ORDER = [
    ("A. Candidate facts", "section_a"),
    ("B. Discovery sources", "section_b"),
    ("C. Triage rules", "section_c"),
    ("D. Regular vs prioritized policy", "section_d"),
    ("E. Resume-cluster selection", "section_e"),
    ("F. Writing evidence and writing rules", "section_f"),
    ("G. Blocker handling", "section_g"),
    ("H. Submission behavior", "section_h"),
    ("I. Prohibited fabrication", "section_i"),
    ("J. Runtime status semantics", "section_j"),
    ("K. Historical duplicate guard", "section_k"),
    ("L. Schema-safe Sheet writes", "section_l"),
    ("M. Browser lease", "section_m"),
    ("N. Run and incident telemetry", "section_n"),
    ("O. Employer requisition identity", "section_o"),
    ("P. Memory ownership and Copilot preflight", "section_p"),
]


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

    def render(self) -> str:
        return "\n".join(
            [
                "An empty Google Sheet is not a clean slate.",
                "The GitHub ledger already holds applied, closed, ready, and in-progress keys.",
                "discover-jobs-hourly and apply-ready-jobs check this guard in addition to the Sheet.",
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


def load_yaml(path: Path) -> Any:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


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


def bullet(items: List[str], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{item}" for item in items if item)


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return " ".join(text.split())


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


def compile_sections() -> Dict[str, str]:
    profile = load_yaml(ROOT / "config" / "profile.yaml")
    auth = load_yaml(ROOT / "knowledge" / "work_authorization.yaml")
    form = load_yaml(ROOT / "knowledge" / "form_strategy.yaml")
    triage = load_yaml(ROOT / "knowledge" / "discovery_triage_rules.yaml")
    priority = load_yaml(ROOT / "knowledge" / "application_priority.yaml")
    targets = load_yaml(ROOT / "knowledge" / "target_roles.yaml")
    writing = load_yaml(ROOT / "knowledge" / "written_response_bank.yaml")
    bank = load_yaml(ROOT / "knowledge" / "evidence_bank.yaml")
    roles = load_yaml(ROOT / "knowledge" / "role_families.yaml")
    operator = load_yaml(ROOT / "knowledge" / "polar_operator.yaml")
    gates = load_yaml(ROOT / "config" / "submit_gates.yaml")
    preference_resolutions = load_preference_resolutions(
        load_yaml(ROOT / "knowledge" / "preference_resolutions.yaml")
    )
    assert_operator_columns(operator)

    always = form.get("always") or {}
    anchors = triage.get("profile_anchors") or {}
    polar_local = gates.get("polar_local") or {}
    cloud = gates.get("cursor_cloud") or {}
    cloud_ladder = cloud.get("gates") or gates.get("gates") or {}
    cloud_cap = cloud.get("regular_submit_cap_per_run", gates.get("regular_submit_cap_per_run"))
    caps = apply_run_caps()

    standing: List[str] = []
    for name, block in always.items():
        line = form_answer_line(name, block)
        if line:
            standing.append(line)

    auth_form = auth.get("form_strategy") or {}
    citizenship = md_escape(auth.get("citizenship_country") or auth_form.get("citizenship_country", {}).get("form_answer"))
    visa = md_escape(auth.get("current_status") or "F-1")
    program_end = md_escape(auth.get("program_end_date") or anchors.get("program_end_date"))
    commencement = md_escape(auth.get("commencement_date") or anchors.get("commencement_date"))
    earliest_ft = md_escape(auth.get("earliest_full_time_start") or profile.get("earliest_start_date"))
    visa_block = auth_form.get("visa_sponsorship") or {}
    sponsorship_form = md_escape(visa_block.get("form_answer") or "unknown")
    sponsorship_execution = md_escape(visa_block.get("execution") or "")

    docs = document_availability()
    doc_lines = []
    for doc in docs:
        avail = "available in repo" if doc.get("exists") else "not in repo"
        doc_lines.append(
            f"{doc.get('id')}: `{doc.get('approved_path')}` ({avail}). "
            f"{md_escape(doc.get('purpose'))}."
        )

    section_a = "\n".join(
        [
            "Phone numbers live in the local Polar profile and in Simplify. They are not compiled here.",
            "Normal ATS email, candidate account email, preferred application contact, and password-reset email",
            "use the dedicated local APPLICATION mailbox from Polar, Simplify, or the browser profile.",
            "If a field asks for school email, university email, or institutional email, use the local academic mailbox.",
            "A resume parser that fills Harvard email into a normal contact field is wrong. Correct it before Submit.",
            "Do not create a second employer account only to change email.",
            "street_address_source: local Polar or private profile. Do not compile or log the street value.",
            "",
            "Approved documents. Attach only when the form asks for that class. Never paste contents.",
            bullet(doc_lines) if doc_lines else "- No approved documents are registered.",
            "",
            bullet(
                [
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
            ),
            "",
            "Standing widget answers (owner-confirmed). Apply them verbatim.",
            "",
            bullet(standing),
        ]
    )

    slugs = list(((targets.get("board_categories") or {}).get("enabled") or {}).keys())
    if not slugs:
        slugs = ["swe", "ml_ai", "data_science", "data_analysis", "healthcare"]
    minisites: List[str] = []
    for track in ("intern", "newgrad"):
        for slug in slugs:
            minisites.append(
                f"https://jobright.ai/minisites-jobs/{track}/us/{slug}?embed=true"
            )

    healthcare_note = ((targets.get("board_categories") or {}).get("notes") or {}).get("healthcare", "")
    section_b = "\n".join(
        [
            "Use the authenticated Jobright session. Do not scrape the public internet as a substitute.",
            "Do not use Jobright APPLY WITH AUTOFILL.",
            "Cloud Ashby board sweep stays on Cursor. Polar does not rerun it.",
            "",
            "Primary surfaces:",
            "",
            bullet(
                [
                    "Jobright Matches: https://jobright.ai/jobs/recommend",
                    "Tracks are co-primary: internship and new grad.",
                    "Enabled category slugs: " + ", ".join(slugs),
                ]
                + minisites
            ),
            "",
            "Healthcare board: "
            + (
                md_escape(healthcare_note)
                or "cheap insurance. Clinical page-one rows are usually skip."
            ),
        ]
    )

    rules = triage.get("guide_rules") or []
    rule_lines = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_lines.append(
            f"`{rule.get('id')}` ({rule.get('severity')}, default {rule.get('default_decision')}): "
            f"{md_escape(rule.get('guidance'))}"
        )
    section_c = "\n".join(
        [
            "Triage after discover and dedupe.",
            "Discovery keeps the Jobright source_url. Do not open Original Job Post during discover-jobs-hourly.",
            "apply-ready-jobs resolves Original Job Post on demand.",
            "",
            bullet(rule_lines),
            "",
            "An exclusive graduation or enrollment window is an eligibility note, not a skip.",
            "Do not invent a graduation date.",
            "Sponsorship unknown, unavailable, or generally not offered is not a skip.",
            "F-1 or OPT mentioned on a board is not a skip.",
            "Do not invent work_model, location, graduation windows, or H1B facts.",
            "Blank location is not an automatic skip.",
            "apply-ready-jobs reads the full employer posting immediately after it is open, before login or form fill.",
            "A fuller JD can reveal a 2026 start, a start before 2027-01-18, a non-US role, PhD-only, undergraduate-only, or TS-SCI/polygraph skip that discovery missed.",
            "Those degree-level misses share repeat_key degree_level_gate_missed_at_discovery.",
            "Do not reopen Original Job Post during hourly discovery to catch them.",
        ]
    )

    weight = priority.get("application_weight") or {}
    regular = (weight.get("regular") or {}).get("meaning", "")
    prioritized = (weight.get("prioritized") or {}).get("meaning", "")
    subfields = (weight.get("prioritized") or {}).get("subfields") or []
    sub_lines = []
    for item in subfields:
        if isinstance(item, dict):
            sub_lines.append(f"{item.get('id')}: {md_escape(item.get('meaning'))}")
    section_d = "\n".join(
        [
            f"Regular: {md_escape(regular)}",
            f"Prioritized: {md_escape(prioritized)}",
            "",
            "Prioritized signals, only when strongly applicable:",
            "",
            bullet(
                sub_lines
                + [
                    "fortune_500_or_major: a major company Junyi values, not every large employer.",
                    "biotech_health_ai: biomedical or health AI with real product fit.",
                    "biostat_data_science_bio: unusually strong biostatistics, data-science, or bio fit.",
                    "personal_fit: unusually strong personal fit. Rare.",
                    "Do not mark a generic analyst or data role prioritized only because the title contains data.",
                ]
            ),
            "",
            "Polar may assign READY_PRIORITY when a strong configured signal is present.",
            "Junyi does not confirm every priority label before the queue can move.",
            "Priority controls execution effort, writing depth, and post-submit writing audit.",
            "Polar Local may Submit a prioritized row when writing_log is complete and final validation passes.",
            "It is not permission to invent company facts.",
            "",
            "Strong signals. Assign READY_PRIORITY:",
            bullet(
                [
                    "fde (title)",
                    "gtc_2026 (company on the NVIDIA GTC 2026 list)",
                    "confirmed_prioritized (YAML list match)",
                    "clear fortune_500_or_major",
                    "clear biotech_health_ai",
                ]
            ),
            "",
            "Weak signals. Stay READY_REGULAR unless clearly justified:",
            bullet(
                [
                    "startup or prestige hints",
                    "personal_fit",
                    "generic data or analyst titles",
                ]
            ),
            "",
            "FDE / Forward Deployed titles stay and are marked prioritized.",
            "Do not claim customer on-site FDE work already done.",
            "READY_PRIORITY no longer waits behind a permanent READY_REGULAR backlog.",
            f"Reserve up to {caps.reserved_priority_slots} new-execution slot per apply-ready-jobs run for READY_PRIORITY when one exists.",
        ]
    )

    clusters = targets.get("role_clusters") or {}
    cluster_lines = []
    for name, body in clusters.items():
        if not isinstance(body, dict):
            continue
        titles = ", ".join(str(x) for x in body.get("titles") or [])
        cluster_lines.append(f"{name}: {titles}")
    section_e = "\n".join(
        [
            "One master resume on disk: `JZ_resume` at `resumes/base/`. It is the two-page source of truth, not a production attach.",
            "Prefer the Simplify resume already attached.",
            "If the widget is empty, do not upload `resumes/base/JZ_resume.pdf`.",
            "Mark REVIEW_READY with blocker missing_production_resume and continue the worker.",
            "Do not invent a new resume for every job.",
            "",
            "Title families are job taxonomy only. resume_cluster is not a file.",
            bullet(cluster_lines),
            "",
            "Prioritized rows may tailor from the evidence bank only when the JD justifies it.",
            "Do not invent lab hardware, customer on-site FDE, or technologies that are not resume-eligible.",
        ]
    )

    ideology = writing.get("ideology") or {}
    why = writing.get("why_company_shape") or {}
    fde = roles.get("forward_deployed_engineer") or {}
    section_f = "\n".join(
        [
            f"writing_observation_mode: {operator.get('writing_observation_mode')}",
            "For every nontrivial free-response question, append one writing_log row.",
            "Record company, role, exact question, answer used, and a short evidence note.",
            "Regular writing may still submit when the facts support it.",
            "Prioritized writing must be logged before Submit. Missing writing_log is a Submit blocker.",
            "",
            "Ideology bank is for week, meaning, and culture prompts only.",
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
            "Tone: " + md_escape(why.get("tone")),
            "Punctuation: " + md_escape((why.get("punctuation") or {}).get("rule")),
            "",
            "Verified resume-eligible skills:",
            bullet(eligible_skills(bank)),
            "",
            "Projects you may name at the evidence-bank ceiling:",
            bullet(project_lines(bank)),
            "",
            "FDE ceiling: " + md_escape(fde.get("closest_verified_ceiling")),
            "FDE do not claim:",
            bullet([md_escape(x) for x in fde.get("do_not_claim") or []]),
            "",
            "Per-application drafts live in docs/apply/written_answers/. A file there is not a submit.",
        ]
    )

    section_g = "\n".join(
        [
            "A required new application account is normal work, not a blocker by default.",
            "Attempt ordinary user-facing completion for account creation, a browser-generated strong password, saved credentials, forgot-password, email verification, email OTP, SMS on the Mac, ordinary consent, multi-page forms, unknown widgets, and required writing.",
            "Use only normal browser flows for security or anti-abuse challenges.",
            "Do not implement CAPTCHA-bypass services, fingerprint spoofing, or anti-abuse evasion.",
            "Escalate to BLOCKED only after this local environment cannot complete a required step.",
            "A blocked job must not stall the queue. Persist the blocker and continue to the next READY job.",
            "ATS family is diagnostic metadata only. Do not organize work by ATS worker class.",
            "Simplify Copilot is a required apply precondition. See section P.",
            "Missing Copilot is an ENVIRONMENT blocker. Do not mark the queue job BLOCKED.",
            "Do not silently fall back to traditional clicking.",
        ]
    )

    section_h = "\n".join(
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
            "Polar worker budget source: knowledge/polar_operator.yaml apply_worker.",
            f"Per-run worker budget on apply-ready-jobs: {caps.max_new_jobs} new jobs.",
            f"READY_PRIORITY reservation: {caps.reserved_priority_slots} slot taken from that pool, not added to it.",
            "If no READY_PRIORITY exists, READY_REGULAR may use the whole pool.",
            "Another apply-ready-jobs run has its own budget. There is no shared daily regular submission pool.",
            f"Prioritized auto-submit: {caps.prioritized_auto_submit}.",
            "",
            "A regular job may be submitted once only when every item holds:",
            bullet(
                [
                    "Duplicate check passes against the Sheet and section K.",
                    "Company and title on the page match the queue row.",
                    "Approved production resume is attached (Simplify). Do not upload the two-page master.",
                    "Identity fields are correct after a visible read-back.",
                    "Required factual fields are resolved from this runtime or left for Junyi.",
                    "No unsupported claim was invented.",
                    "Writing is evidence-grounded.",
                    "application_weight is regular.",
                    "Final review of visible widgets passes.",
                    "One final Submit is used.",
                    "Result is verified, or status becomes SUBMISSION_UNKNOWN.",
                ]
            ),
            "",
            "A prioritized job may be submitted once when every regular item holds and polar_policy.priority_submit_permitted is true.",
            "That function is false when writing_log is missing a custom question, the answer is blank, or the evidence note is blank.",
            "Include prioritized SUBMITTED rows in the daily digest under PRIORITY APPLICATIONS SUBMITTED TODAY.",
            "REVIEW_READY is only for a missing owner fact or an explicit hold.",
        ]
    )

    section_i = "\n".join(
        [
            "Do not invent any of the following:",
            bullet(
                [
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
            ),
            "",
            "If a required fact is missing, leave the widget and mark needs_human or BLOCKED.",
            "Copilot Completed is not proof a widget has a value. Look at the page.",
        ]
    )

    statuses = operator.get("statuses") or []
    stages = operator.get("last_stages") or []
    recovery = operator.get("recovery_order") or []
    columns = operator.get("queue_columns") or []
    section_j = "\n".join(
        [
            "GitHub holds configuration, policy, evidence, and audit.",
            "The Google Sheet holds runtime queue state. It is not a second applications.csv.",
            "An empty Sheet is not a clean slate. Check section K in addition to the Sheet.",
            "",
            "Statuses:",
            bullet(
                [
                    "NEW: seen and written. Not yet READY.",
                    "READY_REGULAR: triaged keep, regular weight, eligible to execute.",
                    "READY_PRIORITY: triaged keep, prioritized weight, eligible to execute with deeper writing.",
                    "IN_PROGRESS: this run owns the job via claim_run_id. Different jobs may be IN_PROGRESS at the same time.",
                    "REVIEW_READY: form is complete but Polar stopped for a missing owner fact or explicit hold.",
                    "SUBMITTED: Submit clicked and verification succeeded.",
                    "SUBMISSION_UNKNOWN: Submit may have happened. Verify before any retry. Never blindly resubmit.",
                    "BLOCKED: this environment cannot finish a required step. Queue continues.",
                    "SKIP: hard skip, closed posting, or owner skip.",
                ]
            ),
            "",
            "Allowed status values: " + ", ".join(str(x) for x in statuses),
            "Allowed last_stage values: " + ", ".join(str(x) for x in stages),
            "Recovery order: " + " then ".join(str(x) for x in recovery) + ".",
            "If the Mac slept during Job 6 IN_PROGRESS and the claim is abandoned or self-owned, resume Job 6. Do not restart Job 1.",
            "",
            "Queue columns: " + ", ".join(str(x) for x in columns),
            md_escape(operator.get("job_key_rule")),
            "",
            "Workflows never apply during discover-jobs-hourly.",
            "apply-ready-jobs inspects SUBMISSION_UNKNOWN first, then abandoned or self-owned IN_PROGRESS.",
            "It then reserves one new-execution slot for READY_PRIORITY when one exists, and uses remaining slots for READY_REGULAR.",
            "daily-job-summary never includes passwords, OTP codes, or cookies.",
            "production-learning-daily writes a sanitized report and does not change GitHub policy.",
        ]
    )

    section_k = HistoricalGuard.compile().render()

    lease = operator.get("lease") or {}
    section_l = "\n".join(
        [
            "Read the actual header row before every Sheet write.",
            "Build a field-name to column mapping from those headers.",
            "Write by header name. Write explicit blanks. Do not shorten a positional row.",
            "apply_url_confidence must stay in its named column even when the value is none or blank.",
            "After an important queue write, read back job_key, status, last_stage, and claim_run_id.",
            "If job_key, status, or last_stage do not match, repair those fields.",
            "If claim_run_id is another run_id, do not overwrite it.",
            "If the queue header has no claim_run_id, do not append it from apply or discover.",
            "polar-sheet-migration is the only schema mutator for that column.",
            "Control writes locate the row by key. Never pick a visually empty row.",
            "If the visible row has a different key, or no key, abort. github_write_canary must not overwrite polar_browser.",
            "After a canary write, reread polar_browser key, owner_run_id, acquired_at, and expires_at.",
            "Commit the edit, then reread key, owner_run_id, and notes. Looking correct is not persistence.",
        ]
    )
    section_m = "\n".join(
        [
            f"Historical control key: {lease.get('key') or LEASE_KEY} on tab {lease.get('tab') or 'control'}.",
            "polar_browser is not a production mutex. Do not acquire it.",
            "Do not write run_log result SKIPPED_LOCKED because that row looks held.",
            "Independent Polar workflows may use their own browser surfaces at the same time.",
            "Apply ownership is queue.claim_run_id on one job_key.",
            "Each apply-ready-jobs run claims one job at a time until its per-run budget is used.",
            "The same employer requisition has one canonical owner via pick_canonical_requisition_row.",
            "Two live sibling claims do not both back off.",
            "Before Submit, reread claim_run_id and rerun requisition_submit_blocked.",
            f"Abandoned IN_PROGRESS claims older than {work_claim_ttl_minutes()} minutes may be recovered.",
            "Empty claim_run_id on IN_PROGRESS is abandoned.",
            "On start, upsert a run_log row for this run_id with result PARTIAL so a crash still leaves a row.",
            "After each job stage, write last_stage and updated_at on that queue row.",
            "Heartbeat, daily summary, and production-learning-daily do not claim queue jobs.",
        ]
    )
    section_n = "\n".join(
        [
            "One workflow invocation upserts one run_log row by run_id and copies workflow_version from the instruction file.",
            "Write incident_log rows for material events. Use the small category list in knowledge/polar_operator.yaml.",
            "incident_id is INC-YYYYMMDD-NNN with three digits. The sequence is monotonic. The next id is one more than the highest number for that date. If 001 and 003 exist, write 004. 01 and 001 count as the same number.",
            "Degree-level apply-time skips share repeat_key degree_level_gate_missed_at_discovery.",
            "A missing birth date or OPT-months answer is MISSING_FACT, not MISSING_DOCUMENT.",
            "Authorization telemetry uses auth_outcome answered, optional_left_blank, ambiguous_required_blocked, hard_eligibility_skip, or disclosure_prevented.",
            "If time was lost, set time_lost_category so later review can explain a 35 minute run versus a 105 minute run.",
            "Do not count every click. Coarse stage timing is enough.",
            "production-learning-daily aggregates today's telemetry into a sanitized Markdown report.",
            "Do not put secrets in telemetry.",
        ]
    )
    section_o = "\n".join(
        [
            "After Original Job Post or the employer application is resolved, capture employer_requisition_id,",
            "canonical employer apply_url, and ats_job_id.",
            "If multiple Jobright rows point at the same employer requisition, keep one canonical row.",
            "requisition_submit_blocked ignores SKIP and abandoned IN_PROGRESS, then pick_canonical_requisition_row ranks the rest.",
            "That rank is SUBMITTED, SUBMISSION_UNKNOWN, IN_PROGRESS, earlier discovered_at, then job_key.",
            "Mark siblings SKIP with the canonical job_key.",
            "Do not submit the same employer requisition twice.",
            "Jobright ids and company+role+location remain useful. They are not enough once the employer identity is known.",
            "Section K still applies.",
        ]
    )

    section_p = "\n".join(
        [
            "GitHub is the only canonical behavioral memory.",
            f"Local inbox: {LOCAL_PREFERENCES_PATH}.",
            "Canonical pointer: " + raw_runtime_url() + ".",
            "PREFERENCES.md is not a second strategy database.",
            "precedence: " + " > ".join(MEMORY_PRECEDENCE) + ".",
            "preference_classes: " + ", ".join(PREFERENCE_CLASSES) + ".",
            "An old PREFERENCES strategy line must not override newer GitHub behavior.",
            "LOCAL_PRIVATE values stay local. SECRET_OR_CREDENTIAL is never exported.",
            "Export assigns pref_YYYYMMDD_NNN and emits Polar Preferences Delta. Unresolved ids stay pending.",
            "Mint the next id from pending ids, keep_local ids, and main preference_resolutions. Never reuse. Never fill gaps.",
            "An open Cursor PR is not canonical. Polar reconciles only after a resolution row is on main.",
            "KEEP_LOCAL leaves pending and stays in Local-only facts. Do not re-export it.",
            "Match candidate_id only. Do not compare wording.",
            format_runtime_resolutions(preference_resolutions),
            "Cursor writes generalized lessons and knowledge/preference_resolutions.yaml. STOP BEFORE MERGE.",
            "",
            "Simplify Copilot is a required apply precondition.",
            "proof: Copilot UI on the employer ATS page.",
            "not_proof: simplify.jobs login or API.",
            "states: " + ", ".join(COPILOT_STATES) + ".",
            f"control_key: {ENV_SIMPLIFY_KEY}. Locate by key. Never overwrite polar_browser.",
            "If Copilot is PRESENT, Autofill once. Then read the visible widgets.",
            "If Copilot is MISSING or UNKNOWN, do not fall back to traditional clicking.",
            "Restore the probe job to READY. Do not consume it as BLOCKED.",
            f"Incident category ENVIRONMENT. repeat_key {COPILOT_REPEAT_KEY}.",
            "run_log result OWNER_ACTION_REQUIRED. Clear claim_run_id. Exit the apply run.",
            "The next apply run rechecks the employer page. Last MISSING is not a cache that skips the check.",
        ]
    )

    probe = "\n".join(
        [
            section_a,
            section_b,
            section_c,
            section_d,
            section_e,
            section_f,
            section_g,
            section_h,
            section_i,
            section_j,
            section_k,
            section_l,
            section_m,
            section_n,
            section_o,
            section_p,
        ]
    )
    for value in forbidden_profile_values(profile if isinstance(profile, dict) else {}):
        if value in probe:
            raise SystemExit("compiled runtime leaked a forbidden profile value")

    return {
        "section_a": section_a,
        "section_b": section_b,
        "section_c": section_c,
        "section_d": section_d,
        "section_e": section_e,
        "section_f": section_f,
        "section_g": section_g,
        "section_h": section_h,
        "section_i": section_i,
        "section_j": section_j,
        "section_k": section_k,
        "section_l": section_l,
        "section_m": section_m,
        "section_n": section_n,
        "section_o": section_o,
        "section_p": section_p,
    }


def render(parts: Dict[str, str]) -> str:
    blocks = [
        "# POLAR_RUNTIME",
        "",
        "COMPILED ARTIFACT. Not canonical.",
        "",
        "Do not edit this file by hand.",
        "Run `python3 scripts/build_polar_runtime.py` after canonical YAML or policy changes.",
        "Polar should open this one file. Do not reread the whole repository every hour.",
        "",
        "Canonical sources:",
        "- `config/profile.yaml`",
        "- `config/submit_gates.yaml`",
        "- `knowledge/polar_operator.yaml`",
        "- `knowledge/preference_resolutions.yaml`",
        "- `knowledge/polar_documents.yaml`",
        "- `knowledge/work_authorization.yaml`",
        "- `knowledge/form_strategy.yaml`",
        "- `knowledge/application_priority.yaml`",
        "- `knowledge/discovery_triage_rules.yaml`",
        "- `knowledge/target_roles.yaml`",
        "- `knowledge/evidence_bank.yaml`",
        "- `knowledge/written_response_bank.yaml`",
        "- `knowledge/role_families.yaml`",
        "- `docs/policy/SUBMIT_ROLLOUT.md`",
        "- `data/applications.csv` (keys only)",
        "- `data/job_decisions.csv` (keys only)",
        "- `data/apply_attempts.csv` (keys only)",
        "",
        "Secrets stay out. No passwords, cookies, OTP codes, 2FA secrets, or session files.",
        "",
    ]
    for title, key in SECTION_ORDER:
        blocks.extend([f"## {title}", "", parts[key].rstrip(), ""])
    return "\n".join(blocks).rstrip() + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compile POLAR_RUNTIME.md")
    parser.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = parser.parse_args(argv)
    text = render(compile_sections())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(args.out)
    if args.out == OUT_DEFAULT:
        operator = load_yaml(ROOT / "knowledge" / "polar_operator.yaml")
        for path in write_schema_csvs(ROOT):
            print(path)
        _, workflow_paths = write_workflows(operator, ROOT)
        for path in workflow_paths:
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
