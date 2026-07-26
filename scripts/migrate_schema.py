#!/usr/bin/env python3
"""Additive schema migration for applications + contacts split. Safe to re-run."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APP_FIELDS, APPLICATIONS, BACKUPS, CONTACT_FIELDS, CONTACTS,
    INTERACTION_FIELDS, LEGACY_NETWORKING_FIELDS, NETWORKING,
    RESUME_VERSION_FIELDS, RESUME_VERSIONS, bump_highest, ensure_csv, log,
    map_hard_eligibility, map_sponsorship, now_iso, read_rows, sync_app_aliases,
    today_iso, write_rows,
)


def backup(path: Path) -> Path:
    BACKUPS.mkdir(parents=True, exist_ok=True)
    dest = BACKUPS / f"{path.stem}_{now_iso().replace(':', '')}{path.suffix}"
    if path.exists():
        shutil.copy2(path, dest)
        log(f"backup → {dest}")
    return dest


def migrate_applications(dry_run: bool) -> int:
    rows = read_rows(APPLICATIONS)
    migrated = [sync_app_aliases(r) for r in rows]
    for row in migrated:
        row["sponsorship_signal"] = map_sponsorship(row.get("sponsorship_signal", ""))
        row["hard_eligibility"] = row.get("hard_eligibility") or map_hard_eligibility(row.get("eligibility", ""))
        st = row.get("status") or "discovered"
        row["stage_highest_reached"] = bump_highest(row.get("stage_highest_reached", ""), st)
        if not row.get("label_source"):
            row["label_source"] = "manual" if row.get("pursuit_lane") else ""
        if not row.get("needs_review"):
            row["needs_review"] = "false"
    log(f"applications rows={len(migrated)} fields={len(APP_FIELDS)}")
    if not dry_run:
        backup(APPLICATIONS)
        write_rows(APPLICATIONS, APP_FIELDS, migrated)
    return len(migrated)


def migrate_contacts_and_interactions(dry_run: bool) -> None:
    ensure_csv(CONTACTS, CONTACT_FIELDS)
    # New interactions file
    interactions_path = ROOT / "data" / "networking_interactions.csv"
    ensure_csv(interactions_path, INTERACTION_FIELDS)

    legacy = read_rows(NETWORKING)
    contacts = read_rows(CONTACTS)
    existing_ids = {c.get("contact_id") for c in contacts}
    added = 0
    for row in legacy:
        cid = row.get("contact_id") or ""
        if not cid or cid in existing_ids:
            continue
        contacts.append({
            "contact_id": cid,
            "name": row.get("name", ""),
            "company": row.get("company", ""),
            "title": row.get("role", ""),
            "team": "",
            "location": "",
            "linkedin_url": row.get("profile_url", ""),
            "email": "",
            "relationship_type": row.get("relation", "") or "unknown",
            "school_connection": "",
            "shared_background": "",
            "target_role_cluster": "",
            "source": row.get("source", ""),
            "last_verified": row.get("last_update", ""),
            "notes": row.get("notes", ""),
        })
        existing_ids.add(cid)
        added += 1
        # seed interaction if outreach exists
        if row.get("outreach_date"):
            # will append after read
            pass
    log(f"contacts migrated/added={added} total_will_be={len(contacts)}")
    if not dry_run:
        backup(NETWORKING)
        write_rows(CONTACTS, CONTACT_FIELDS, contacts)
        # Keep legacy networking.csv header-compatible for old scripts
        ensure_csv(NETWORKING, LEGACY_NETWORKING_FIELDS)


def seed_resume_versions(dry_run: bool) -> None:
    ensure_csv(RESUME_VERSIONS, RESUME_VERSION_FIELDS)
    existing = {r.get("resume_version") for r in read_rows(RESUME_VERSIONS)}
    seeds = [
        {
            "resume_version": "2026-07-20_cloud-swe_v1.1",
            "parent_version": "JZ_resume",
            "cluster": "cloud_swe",
            "created_date": "2026-07-20",
            "change_summary": "Base bullets preserved; reorder Chatbot→Transformer→AlphaFold→Wyss; Cloud/Tools skills up",
            "hypothesis": "Systems-first order improves SWE/platform OA without diluting specificity",
            "target_roles": "SWE, backend, platform, cloud, infra",
            "active": "true",
            "file_path": "resumes/cloud_swe/2026-07-20_cloud-swe_v1.1.tex",
        },
        {
            "resume_version": "2026-07-20_data-ml_v1.1",
            "parent_version": "JZ_resume",
            "cluster": "data_ml",
            "created_date": "2026-07-20",
            "change_summary": "Base bullets preserved; reorder Chatbot→Transformer→Wyss→AlphaFold",
            "hypothesis": "LLM/agent + foundations first improves applied AI / MLE response rate",
            "target_roles": "MLE, applied AI, data science/engineering, RAG roles",
            "active": "true",
            "file_path": "resumes/data_ml/2026-07-20_data-ml_v1.1.tex",
        },
        {
            "resume_version": "2026-07-20_health-ai_v1.1",
            "parent_version": "JZ_resume",
            "cluster": "health_ai",
            "created_date": "2026-07-20",
            "change_summary": "Base bullets preserved; domain-forward order",
            "hypothesis": "Clinical/bio framing helps when company is health/life-science",
            "target_roles": "healthcare AI, clinical data, digital health",
            "active": "true",
            "file_path": "resumes/health_ai/2026-07-20_health-ai_v1.1.tex",
        },
        {
            "resume_version": "JZ_resume",
            "parent_version": "",
            "cluster": "base",
            "created_date": "2026-07-20",
            "change_summary": "Master evidence resume",
            "hypothesis": "Quality baseline for all clusters",
            "target_roles": "source of truth",
            "active": "true",
            "file_path": "resumes/base/JZ_resume.tex",
        },
    ]
    rows = read_rows(RESUME_VERSIONS)
    for s in seeds:
        if s["resume_version"] in existing:
            continue
        full = {k: "" for k in RESUME_VERSION_FIELDS}
        full.update(s)
        for k in ("applications_count", "oa_count", "screen_count", "technical_count", "offer_count"):
            full[k] = full.get(k) or "0"
        rows.append(full)
    log(f"resume_versions rows={len(rows)}")
    if not dry_run:
        write_rows(RESUME_VERSIONS, RESUME_VERSION_FIELDS, rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    migrate_applications(args.dry_run)
    migrate_contacts_and_interactions(args.dry_run)
    seed_resume_versions(args.dry_run)
    log("migration complete" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
