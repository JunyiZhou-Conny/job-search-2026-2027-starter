#!/usr/bin/env python3
"""Prepare a personal collaborator copy of this job-search toolkit.

Default is dry-run. The script refuses to wipe identity files on the upstream
template repository unless the caller passes --i-am-on-a-personal-fork.

Typical agent flow:

    python3 scripts/init_personal_copy.py
    python3 scripts/init_personal_copy.py --i-am-on-a-personal-fork --write
    python3 scripts/init_personal_copy.py --check
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_MARKERS = (
    "JunyiZhou-Conny/job-search-2026-2027-starter",
    "junyizhou-conny/job-search-2026-2027-starter",
)
TEMPLATE_OWNER_NEEDLES = (
    "Junyi Zhou",
    "JunyiZhou-Conny",
    "junyi-zhou-270208247",
    "4046635601",
)
# Dates that live in knowledge/discovery_triage_rules.yaml profile_anchors.
# Do not scan the whole file: the same strings appear in shared guide_rules.
TEMPLATE_OWNER_ANCHOR_NEEDLES = (
    "2026-12-18",
    "2027-03",
    "2027-01-18",
    "December 2026 (program completion)",
)
TRIAGE_RULES_RELATIVE = "knowledge/discovery_triage_rules.yaml"

IDENTITY_RELATIVE: Sequence[Tuple[str, str]] = (
    ("docs/collaborators/templates/profile.template.yaml", "config/profile.yaml"),
    ("docs/collaborators/templates/work_authorization.template.yaml", "knowledge/work_authorization.yaml"),
    ("docs/collaborators/templates/evidence_bank.template.yaml", "knowledge/evidence_bank.yaml"),
    ("docs/collaborators/templates/outreach_templates.template.csv", "data/outreach_templates.csv"),
)

LEDGER_HEADERS: Sequence[Tuple[str, Sequence[str]]] = (
    (
        "data/applications.csv",
        [
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
            "current_authorization_answer", "future_sponsorship_answer", "answer_question_text",
            "auth_qa_notes",
            "networking_before_apply", "networking_after_apply",
            "referral_status", "referrer_contact_id", "recruiter",
            "label_confidence", "label_reason", "label_source", "needs_review",
            "next_action", "next_action_date", "deadline", "job_post_age_days",
            "notes", "created_at", "updated_at", "last_update",
        ],
    ),
    ("data/activity_log.csv", ["timestamp", "job_id", "contact_id", "event_type", "from_status", "to_status", "note"]),
    ("data/job_decisions.csv", ["url", "company", "role", "job_id", "decision", "reason", "decided_at", "source"]),
    (
        "data/contacts.csv",
        [
            "contact_id", "name", "company", "title", "team", "location", "linkedin_url", "email",
            "relationship_type", "school_connection", "shared_background", "target_role_cluster",
            "source", "last_verified", "notes",
        ],
    ),
    (
        "data/networking.csv",
        [
            "contact_id", "name", "company", "role", "relation", "source",
            "profile_url", "target_job_id", "outreach_date", "follow_up_date",
            "response_status", "coffee_chat_date", "referral_status", "last_update", "notes",
        ],
    ),
    (
        "data/networking_interactions.csv",
        [
            "interaction_id", "contact_id", "job_id", "interaction_type", "channel",
            "date_planned", "date_completed", "message_version", "response_status", "response_date",
            "follow_up_date", "coffee_chat_date", "referral_requested", "referral_result",
            "next_action", "next_action_date", "notes",
        ],
    ),
    (
        "data/networking_experiments.csv",
        [
            "experiment_id", "hypothesis", "start_date", "end_date", "target_sample",
            "variable_changed", "control_group", "success_metric", "result", "decision",
        ],
    ),
    (
        "data/resume_versions.csv",
        [
            "resume_version", "parent_version", "cluster", "created_date", "change_summary",
            "hypothesis", "target_roles", "active", "applications_count", "oa_count",
            "screen_count", "technical_count", "offer_count", "notes", "file_path",
        ],
    ),
)

CHECK_RELATIVE: Sequence[str] = (
    "config/profile.yaml",
    "knowledge/work_authorization.yaml",
    "knowledge/evidence_bank.yaml",
    "knowledge/discovery_triage_rules.yaml",
    "docs/automation/DAILY_JOB_DISCOVERY.md",
    "docs/eligibility.md",
    "data/applications.csv",
    "data/outreach_templates.csv",
    "resumes/base/JZ_resume.tex",
)


def _git_remotes(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "remote", "-v"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def looks_like_upstream(root: Path) -> bool:
    remotes = _git_remotes(root)
    if not remotes:
        return False
    for line in remotes.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == "origin":
            url = parts[1].lower()
            if any(marker.lower() in url for marker in UPSTREAM_MARKERS):
                return True
    return False


def _write_header_only(path: Path, fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=list(fields)).writeheader()


def _backup(root: Path, paths: Iterable[Path], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if not path.exists():
            continue
        target = dest / path.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def plan_actions() -> List[str]:
    actions = [f"copy {src} → {dest}" for src, dest in IDENTITY_RELATIVE]
    actions.extend(f"reset {dest} to header-only" for dest, _fields in LEDGER_HEADERS)
    actions.append("write generated/collaborator_setup_status.md")
    return actions


def write_status(root: Path, note: str) -> None:
    path = root / "generated" / "collaborator_setup_status.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().isoformat(timespec="seconds")
    path.write_text(
        f"""# Collaborator setup status

Updated: {now}

{note}

## Remaining human / agent work

- [ ] Fill `config/profile.yaml` with confirmed facts only
- [ ] Fill `knowledge/work_authorization.yaml` (non-sensitive only)
- [ ] Fill `knowledge/evidence_bank.yaml` from resume / repos — invent nothing
- [ ] Rewrite `profile_anchors` in `knowledge/discovery_triage_rules.yaml`
- [ ] Rewrite the candidate block in `docs/automation/DAILY_JOB_DISCOVERY.md` (fork only; do not PR that rewrite upstream)
- [ ] Replace `resumes/base/` with the collaborator's resume
- [ ] Register resume versions in `data/resume_versions.csv`
- [ ] Create Simplify account + fill profile from the evidence bank
- [ ] Connect GitHub in Cursor and create a Cloud Agent environment on **this fork**
- [ ] Create a private Daily Job Discovery automation pointing at **this fork**
- [ ] Run `python3 scripts/init_personal_copy.py --check` until template-owner strings are gone from identity files
- [ ] Run `python3 scripts/validate_data.py`

See `docs/collaborators/SETUP.md`.
""",
        encoding="utf-8",
    )


def apply_reset(root: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_dir = root / "data" / "backups" / f"personal-reset-{stamp}"
    to_backup = [root / dest for _src, dest in IDENTITY_RELATIVE] + [root / dest for dest, _ in LEDGER_HEADERS]
    _backup(root, to_backup, backup_dir)
    for src, dest in IDENTITY_RELATIVE:
        target = root / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / src, target)
    for dest, fields in LEDGER_HEADERS:
        _write_header_only(root / dest, fields)
    write_status(
        root,
        f"Personal-copy reset applied. Previous identity/ledger files are in `{backup_dir.relative_to(root)}` (gitignored).",
    )
    return backup_dir


def _top_level_yaml_block(text: str, key: str) -> str:
    """Return a top-level YAML key and its indented body, or empty string."""
    header = f"{key}:"
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        stripped = line.split("#", 1)[0].rstrip()
        if stripped == header or stripped.startswith(f"{header} "):
            start = i
            break
    if start is None:
        return ""
    collected = [lines[start]]
    for line in lines[start + 1 :]:
        if line and not line[0].isspace() and not line.lstrip().startswith("#"):
            break
        collected.append(line)
    return "\n".join(collected)


def check_template_owner_strings(root: Path) -> List[str]:
    hits: List[str] = []
    for rel in CHECK_RELATIVE:
        path = root / rel
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        needles: Sequence[str] = TEMPLATE_OWNER_NEEDLES
        scan_text = text
        if rel == TRIAGE_RULES_RELATIVE:
            scan_text = _top_level_yaml_block(text, "profile_anchors")
            needles = (*TEMPLATE_OWNER_NEEDLES, *TEMPLATE_OWNER_ANCHOR_NEEDLES)
        for needle in needles:
            if needle in scan_text:
                hits.append(f"{rel} contains `{needle}`")
                break
    return hits


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Apply the reset. Default is dry-run.")
    parser.add_argument(
        "--i-am-on-a-personal-fork",
        action="store_true",
        help="Required to write. Confirms this checkout is the collaborator's copy, not the upstream template.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Scan identity files for leftover template-owner strings and exit 1 if any remain.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.check:
        hits = check_template_owner_strings(root)
        if hits:
            print("Template-owner identity still present:")
            for hit in hits:
                print(f"  - {hit}")
            print("Rewrite those files for the collaborator, or keep them only if this is the upstream template.")
            return 1
        print("No template-owner identity strings found in the checked files.")
        return 0

    print("Planned actions:")
    for action in plan_actions():
        print(f"  - {action}")

    if looks_like_upstream(root):
        print(
            "\nRefusing to treat this checkout as a personal copy: `origin` points at "
            "JunyiZhou-Conny/job-search-2026-2027-starter.\n"
            "Fork the repo (or change origin), then re-run with --i-am-on-a-personal-fork --write."
        )
        if args.write:
            return 2
        return 0

    if not args.write:
        print("\nDry-run only. Re-run with --i-am-on-a-personal-fork --write to apply.")
        return 0

    if not args.i_am_on_a_personal_fork:
        print("Refusing to write without --i-am-on-a-personal-fork.")
        return 2

    missing = [root / src for src, _dest in IDENTITY_RELATIVE if not (root / src).exists()]
    if missing:
        print("Missing templates:")
        for src in missing:
            print(f"  - {src}")
        return 2

    backup_dir = apply_reset(root)
    print(f"Reset complete. Backup: {backup_dir}")
    print("Next: fill the template files with the collaborator's confirmed facts. See docs/collaborators/SETUP.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
