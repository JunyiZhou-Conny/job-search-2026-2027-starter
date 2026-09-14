#!/usr/bin/env python3
"""Load the standing Perfect Resume attach contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
ATTACH_PATH = ROOT / "knowledge" / "polar_resume_attach.yaml"

PRODUCTION_RESUME_STORED_NAME = "Perfect Resume"
PRODUCTION_RESUME_REPO_PATH = "resumes/Perfect Resume/perfect_resume.pdf"
IDENTIFIED_MAC_RESUME_PATH = "/Users/conny/Desktop/JZ_Resume_911.pdf"
FAMILY_RESUME_EXPORT_PATH = "generated/resumes/export/ai_infra_v1.pdf"
SANITIZED_FAMILY_RESUME_PATH = "resumes/families/ai_infra/ai_infra_v1.pdf"
TWO_PAGE_MASTER_PATH = "resumes/base/JZ_resume.pdf"


def load_attach_policy() -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(ATTACH_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit("knowledge/polar_resume_attach.yaml must be a mapping")
    stored = str(data.get("stored_name") or "").strip()
    if stored != PRODUCTION_RESUME_STORED_NAME:
        raise SystemExit("polar_resume_attach.yaml stored_name must be Perfect Resume")
    return data


def stored_name() -> str:
    return str(load_attach_policy().get("stored_name") or PRODUCTION_RESUME_STORED_NAME).strip()


def repo_pdf() -> str:
    return str(load_attach_policy().get("ingest_pdf") or PRODUCTION_RESUME_REPO_PATH).strip()


def identified_mac_pdf() -> str:
    return str(
        load_attach_policy().get("identified_mac_pdf") or IDENTIFIED_MAC_RESUME_PATH
    ).strip()


def never_upload() -> tuple[str, ...]:
    rows = load_attach_policy().get("never_upload") or []
    return tuple(str(item).strip() for item in rows if str(item).strip())


def expected_visible_names() -> tuple[str, ...]:
    rows = load_attach_policy().get("expected_visible_names") or []
    return tuple(str(item).strip() for item in rows if str(item).strip())


def _norm(value: str) -> str:
    return (value or "").replace("\\", "/").lstrip("./").strip().lower()


def repo_pdf_exists(root: Path | None = None) -> bool:
    rel = repo_pdf()
    return bool(rel) and ((root or ROOT) / rel).is_file()


def mac_pdf_exists() -> bool:
    path = identified_mac_pdf()
    return bool(path) and Path(path).is_file()


def perfect_resume_file_available(root: Path | None = None) -> bool:
    return repo_pdf_exists(root) or mac_pdf_exists()


def visible_filename_is_perfect(name: str) -> bool:
    token = _norm(name)
    if not token:
        return False
    expected = {_norm(item) for item in expected_visible_names()}
    expected.add(_norm(stored_name()))
    expected.add(_norm(Path(repo_pdf()).name))
    expected.add(_norm(Path(identified_mac_pdf()).name))
    return token in expected or Path(token).name in {Path(item).name for item in expected}


def visible_filename_is_forbidden(name: str) -> bool:
    token = _norm(name)
    if not token:
        return False
    names = {_norm(item) for item in never_upload()}
    names.add(_norm(FAMILY_RESUME_EXPORT_PATH))
    names.add(_norm(SANITIZED_FAMILY_RESUME_PATH))
    names.add(_norm(TWO_PAGE_MASTER_PATH))
    basenames = {Path(item).name for item in names}
    return token in names or Path(token).name in basenames


def runtime_lines() -> list[str]:
    lines = load_attach_policy().get("runtime_lines") or []
    return [str(line) for line in lines]


def workflow_lines() -> list[str]:
    lines = load_attach_policy().get("workflow_lines") or []
    return [str(line) for line in lines]


def submit_check() -> str:
    return str(load_attach_policy().get("submit_check") or "").strip()


def format_document_line(doc: Mapping[str, Any], *, workflow: bool = False) -> str:
    stored = str(doc.get("stored_name") or "").strip()
    path = str(doc.get("approved_path") or "").strip()
    exists = bool(doc.get("exists"))
    purpose = str(doc.get("purpose") or "").strip()
    if path.startswith("/"):
        avail = "available on this Mac" if exists else "not on this Mac"
    elif workflow:
        avail = "available" if exists else "missing"
    else:
        avail = "available in repo" if exists else "not in repo"
    if stored and path:
        body = f"Polar/Simplify stored name `{stored}`; native-file `{path}` ({avail})"
    elif stored:
        body = f"Polar/Simplify stored name `{stored}` ({avail})"
    else:
        body = f"`{path}` ({avail})"
    if workflow:
        return f"- {doc.get('id')}: {body}. Use when the form asks for that document class."
    suffix = f" {purpose}." if purpose else ""
    return f"{doc.get('id')}: {body}.{suffix}"
