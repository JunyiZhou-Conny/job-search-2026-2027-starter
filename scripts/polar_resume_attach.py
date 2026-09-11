#!/usr/bin/env python3
"""Load the Polar resume-ingest contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
ATTACH_PATH = ROOT / "knowledge" / "polar_resume_attach.yaml"


def load_attach_policy() -> dict[str, Any]:
    data = yaml.safe_load(ATTACH_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit("knowledge/polar_resume_attach.yaml must be a mapping")
    pdf = str(data.get("ingest_pdf") or "").strip()
    if not pdf:
        raise SystemExit("polar_resume_attach.yaml is missing ingest_pdf")
    if not (ROOT / pdf).is_file():
        raise SystemExit(f"polar ingest PDF missing: {pdf}")
    return data


def ingest_pdf() -> str:
    return str(load_attach_policy()["ingest_pdf"]).strip()


def runtime_lines() -> list[str]:
    lines = load_attach_policy().get("runtime_lines") or []
    return [str(line) for line in lines]


def workflow_lines() -> list[str]:
    lines = load_attach_policy().get("workflow_lines") or []
    return [str(line) for line in lines]


def submit_check() -> str:
    return str(load_attach_policy().get("submit_check") or "").strip()
