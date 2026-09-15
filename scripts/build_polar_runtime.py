#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

from polar_policy import (
    ENV_SIMPLIFY_KEY,
    LEASE_KEY,
    LOCAL_PREFERENCES_PATH,
    MEMORY_PRECEDENCE,
    PREFERENCE_CLASSES,
    apply_run_caps,
    format_runtime_resolutions,
    load_preference_resolutions,
    raw_runtime_url,
    work_claim_ttl_minutes,
)
from polar_workflows import fast_validation_lines, write_schema_csvs, write_workflows
from runtime_sections import (
    POLAR,
    RuntimeSources,
    bullet,
    forbidden_profile_values,
    load_sources,
    load_yaml,
    md_escape,
    polar_section_resume,
    polar_section_submit,
    section_blockers,
    section_fabrication,
    section_facts,
    section_historical_guard,
    section_requisition,
    section_sheet_writes,
    section_status,
    section_telemetry,
    section_triage,
    section_weight,
    section_writing,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DEFAULT = ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md"

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
    ("P. Memory ownership and autofill", "section_p"),
]


def polar_section_discovery(src: RuntimeSources) -> str:
    targets = src.targets
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
    return "\n".join(
        [
            "Use the authenticated Jobright session. Do not scrape the public internet as a substitute.",
            "Apply entry is Jobright recommendations at https://jobright.ai/jobs/recommend.",
            "On that path, use Apply with Autofill, then Quick Edit, Select All, Generate My Resume, Apply Now.",
            "Jobright extension owns autofill. Do not click Simplify Copilot Autofill.",
            "discover-jobs-hourly is retired from apply admission.",
            "Cloud Ashby board sweep stays on Cursor. Polar does not rerun it.",
            "",
            "Primary apply surface:",
            "",
            bullet(
                [
                    "Jobright recommendations: https://jobright.ai/jobs/recommend",
                    "Tracks are co-primary: internship and new grad.",
                    "Enabled category slugs: " + ", ".join(slugs),
                    "Minisite boards below are inventory only. They are not apply entry.",
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


def polar_section_lease(src: RuntimeSources) -> str:
    lease = src.operator.get("lease") or {}
    return "\n".join(
        [
            f"Historical control key: {lease.get('key') or LEASE_KEY} on tab {lease.get('tab') or 'control'}.",
            "polar_browser is not a production mutex. Do not acquire it. Do not run a claim-race on that row.",
            "Do not write run_log result SKIPPED_LOCKED because that row looks held.",
            "Independent Polar workflows may use their own browser surfaces at the same time.",
            "Apply ownership is queue.claim_run_id on one job_key. That is the live claim, not a browser lease.",
            "Each apply-ready-jobs run claims one job at a time until its considered budget is used.",
            "The same employer requisition has one canonical owner via pick_canonical_requisition_row.",
            "Two live sibling claims do not both back off.",
            "Before Submit, reread claim_run_id and rerun requisition_submit_blocked.",
            f"Abandoned IN_PROGRESS claims older than {work_claim_ttl_minutes()} minutes may be recovered.",
            "Empty claim_run_id on IN_PROGRESS is abandoned.",
            "On start, QUERY run_log for a live apply PARTIAL with blank ended_at. polar_policy.start_apply_run_action. NO_WORK if another apply is live (started_at younger than work_claim.ttl_minutes). stale_close if the PARTIAL is older or started_at is unparseable: write ended_at and FAILED with polar_policy.stale_apply_close_fields, then continue. That is the mutex close, not a browser lease. Then upsert this run_id with result PARTIAL so a crash still leaves a row.",
            "job_key is unique. polar_policy.plan_queue_upsert_by_job_key. Two rows with the same key: abort that job, do not claim, do not Submit.",
            "Do not create scratch tabs. Do not acquire polar_browser. Do not create grok_browser.",
            "After each job stage, write last_stage and updated_at on that queue row.",
            "Heartbeat, daily summary, and production-learning-daily do not claim queue jobs.",
        ]
    )


def polar_section_memory(src: RuntimeSources, preference_resolutions) -> str:
    profile = src.profile if isinstance(src.profile, dict) else {}
    return "\n".join(
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
            "Cursor writes generalized lessons and knowledge/preference_resolutions.yaml.",
            "Default for Polar and for unattended nightly maintenance: STOP BEFORE MERGE.",
            "Junyi-authorized maintenance path: after tests pass, merge verified maintenance changes with gh. Record merged by this agent. Do not enable GitHub auto-merge. Do not bypass required checks. Do not merge personal-fact values or apply-policy guesses.",
            "",
            "Jobright extension owns autofill on the apply path. polar_policy.autofill_owner.",
            "Do not click Simplify Copilot Autofill. Do not let Copilot fight the Jobright extension.",
            "polar_policy.page_surface and polar_policy.autofill_action are the engineer tables.",
            "login, JD landing, apply CTA, and No fillable form exists are investigate_not_unsupported.",
            "Autofill once on the real application form. Then Polar runs the fast validation pass on the form DOM.",
            "Trust the form, not the extension sidebar. polar_policy.post_autofill_trust_source.",
            "Clear invented referrals. Re-classify sponsorship vs future-sponsorship. polar_policy.referral_field_action.",
            "Missing Copilot does not stop the run. Copilot is not the autofill owner.",
            f"Historical control_key {ENV_SIMPLIFY_KEY} is not an apply gate. Never overwrite polar_browser.",
            "The application Outlook inbox is readable. Do not treat mailbox access as a hard blocker.",
            "",
            "Fast validation pass after Autofill:",
            "",
            *fast_validation_lines(src.operator, profile),
        ]
    )


def compile_sections() -> Dict[str, str]:
    src = load_sources(ROOT)
    preference_resolutions = load_preference_resolutions(
        load_yaml(ROOT / "knowledge" / "preference_resolutions.yaml")
    )
    caps = apply_run_caps()

    sections = {
        "section_a": section_facts(src, POLAR),
        "section_b": polar_section_discovery(src),
        "section_c": section_triage(src, POLAR),
        "section_d": section_weight(src, POLAR, caps),
        "section_e": polar_section_resume(src),
        "section_f": section_writing(src, POLAR),
        "section_g": section_blockers(POLAR),
        "section_h": polar_section_submit(src, caps),
        "section_i": section_fabrication(POLAR),
        "section_j": section_status(src, POLAR),
        "section_k": section_historical_guard(POLAR),
        "section_l": section_sheet_writes(POLAR),
        "section_m": polar_section_lease(src),
        "section_n": section_telemetry(POLAR),
        "section_o": section_requisition(POLAR),
        "section_p": polar_section_memory(src, preference_resolutions),
    }

    probe = "\n".join(sections[key] for _, key in SECTION_ORDER)
    profile = src.profile if isinstance(src.profile, dict) else {}
    for value in forbidden_profile_values(profile):
        if value in probe:
            raise SystemExit("compiled runtime leaked a forbidden profile value")
    return sections


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
        "- `knowledge/polar_resume_attach.yaml`",
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
