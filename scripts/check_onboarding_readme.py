#!/usr/bin/env python3
"""Prove README.md still points at real files and keeps the bilingual journey."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
PATH_RE = re.compile(
    r"`((?:docs|knowledge|scripts|config|data|generated|resumes|secrets|\.cursor)/[^`]+)`"
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
REQUIRED_MARKERS = (
    "## 中文",
    "## English",
    "Polar",
    "Google Sheet",
    "RESUME_EMAIL",
    "set_polar_trusted_repo.py",
    "print_polar_bootstrap.py",
    "polarbrowser.com",
    "CAPABILITY_MISSING",
    "Original Job Post",
)


def _resolve(raw: str) -> Path | None:
    target = raw.strip()
    if target.startswith("http://") or target.startswith("https://"):
        return None
    if target.startswith("#"):
        return None
    if "YYYY-MM-DD" in target or "<YOU>" in target or "<REPO>" in target:
        return None
    if target in {"secrets/.env"}:
        return None
    target = target.split("#", 1)[0]
    if "*" in target:
        matches = list(ROOT.glob(target))
        return ROOT if matches else ROOT / target
    path = (ROOT / target).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return path
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    text = README.read_text(encoding="utf-8")
    errors: list[str] = []

    chinese = text.find("## 中文")
    english = text.find("## English")
    if chinese < 0 or english < 0:
        errors.append("README.md must contain ## 中文 and ## English")
    elif chinese > english:
        errors.append("Chinese section must come before English")

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"missing required marker: {marker}")

    for match in EMAIL_RE.finditer(text):
        value = match.group(0)
        if value.startswith("git@"):
            continue
        if "example.com" in value:
            continue
        errors.append(f"possible email address leaked: {value}")

    seen: set[str] = set()
    for raw in [m.group(1) for m in LINK_RE.finditer(text)] + [
        m.group(1) for m in PATH_RE.finditer(text)
    ]:
        if raw in seen:
            continue
        seen.add(raw)
        path = _resolve(raw)
        if path is None:
            continue
        if path == ROOT:
            continue
        if not path.exists():
            errors.append(f"missing path: {raw}")

    if errors:
        print("README onboarding check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1
    print("README onboarding check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
