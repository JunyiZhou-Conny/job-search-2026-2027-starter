#!/usr/bin/env python3
"""Compile generated/polar/runtime/POLAR_RUNTIME.md from canonical repo files.

The markdown is COMPILED. Edit the YAML and docs this script reads.
Do not treat the output as a second source of truth.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md"

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
]


def load_yaml(path: Path) -> Any:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def bullet(items: List[str], indent: str = "- ") -> str:
    return "\n".join(f"{indent}{item}" for item in items if item)


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    return " ".join(text.split())


def form_answer_line(name: str, block: Any) -> str:
    if not isinstance(block, dict):
        return ""
    if block.get("status") == "needs_human" or block.get("form_answer") == "unknown":
        when = md_escape(block.get("when", name))
        return f"{name}: leave for Junyi. No approved answer. When: {when}"
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
    if answer is None:
        return ""
    shown = "(blank)" if answer == "" else md_escape(answer)
    when = md_escape(block.get("when", ""))
    extra = f" When: {when}." if when else ""
    return f"{name}: {shown}.{extra}"


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

    always = form.get("always") or {}
    anchors = triage.get("profile_anchors") or {}
    polar_local = gates.get("polar_local") or {}
    canary = operator.get("canary") or {}

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
    sponsorship_form = md_escape((auth_form.get("visa_sponsorship") or {}).get("form_answer") or "No")

    section_a = "\n".join(
        [
            "Phone and email live in the local Polar profile and in Simplify.",
            "They are not compiled here.",
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
                    f"Broad visa-sponsorship widget: {sponsorship_form}",
                    "H-1B-named widget: No",
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
            "Triage after discover and dedupe. Then resolve Original Job Post only for READY jobs.",
            "SKIP and obvious later rows keep the Jobright URL. Do not resolve them.",
            "If Original Job Post fails, keep the Jobright URL. Resolution is an optimization.",
            "",
            bullet(rule_lines),
            "",
            "Sponsorship unknown or no is not a skip.",
            "Do not invent work_model, location, graduation windows, or H1B facts.",
            "Blank location is not an automatic skip.",
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
            "Labels stay suggestions until Junyi confirms.",
            "FDE / Forward Deployed titles stay and are marked prioritized.",
            "Do not claim customer on-site FDE work already done.",
        ]
    )

    clusters = targets.get("role_clusters") or {}
    cluster_lines = []
    for name, body in clusters.items():
        if not isinstance(body, dict):
            continue
        titles = ", ".join(str(x) for x in body.get("titles") or [])
        cluster_lines.append(
            f"{name}: resume `{body.get('default_resume')}`. Titles: {titles}"
        )
    section_e = "\n".join(
        [
            "Pick one existing cluster resume. Do not invent a new resume for every job.",
            "Prefer the Simplify resume that matches the cluster file below.",
            "",
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
            "Prioritized writing stays in the review packet. Do not Submit.",
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
        ]
    )

    section_h = "\n".join(
        [
            "Two Submit planes. Do not mix them.",
            "",
            "cursor_cloud still uses ATS-family gates in config/submit_gates.yaml `gates`.",
            f"Cloud open gates: {md_escape(gates.get('gates'))}.",
            f"Cloud regular cap per run: {gates.get('regular_submit_cap_per_run')}.",
            "Cloud G2 remains closed. Polar Local does not inherit those ATS gates.",
            "",
            "polar_local uses capability and policy checks, not ATS family.",
            f"Gate model: {polar_local.get('gate_model')}.",
            f"Regular jobs per apply-ready-jobs run: {canary.get('max_regular_jobs_per_run') or polar_local.get('regular_submit_cap_per_run')}.",
            f"Regular submissions per local calendar day ({operator.get('timezone')}): {canary.get('max_regular_submissions_per_local_day') or polar_local.get('regular_submit_cap_per_local_day')}.",
            f"Prioritized auto-submit: {canary.get('prioritized_auto_submit')}.",
            "",
            "A regular job may be submitted once only when every item holds:",
            bullet(
                [
                    "Duplicate check passes against the Sheet and known ledger memory.",
                    "Company and title on the page match the queue row.",
                    "Correct cluster resume is attached.",
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
            "Prioritized jobs stop at REVIEW_READY. Include them in the daily digest.",
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
            "",
            "Statuses:",
            bullet(
                [
                    "NEW: seen and written. Not yet READY.",
                    "READY_REGULAR: triaged keep, regular weight, eligible to execute.",
                    "READY_PRIORITY: triaged keep, prioritized weight, eligible to prepare.",
                    "IN_PROGRESS: this job is the active execution. At most one should be live.",
                    "REVIEW_READY: prioritized form is complete. Stop before Submit.",
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
            "If the Mac slept during Job 6 IN_PROGRESS, resume Job 6. Do not restart Job 1.",
            "",
            "Queue columns: " + ", ".join(str(x) for x in columns),
            md_escape(operator.get("job_key_rule")),
            "",
            "Workflows never apply during discover-jobs-hourly.",
            "apply-ready-jobs inspects SUBMISSION_UNKNOWN first, then IN_PROGRESS, then READY rows.",
            "daily-job-summary never includes passwords, OTP codes, or cookies.",
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
        "- `knowledge/work_authorization.yaml`",
        "- `knowledge/form_strategy.yaml`",
        "- `knowledge/application_priority.yaml`",
        "- `knowledge/discovery_triage_rules.yaml`",
        "- `knowledge/target_roles.yaml`",
        "- `knowledge/evidence_bank.yaml`",
        "- `knowledge/written_response_bank.yaml`",
        "- `knowledge/role_families.yaml`",
        "- `docs/policy/SUBMIT_ROLLOUT.md`",
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
