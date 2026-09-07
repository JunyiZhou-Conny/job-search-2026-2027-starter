#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLAR = ROOT / "polar"

REQUIRED_FILES = (
    "README.md",
    "JOURNEY.md",
    "FRONTIER_MAP.md",
    "EVIDENCE.md",
    "ARCHITECTURE.md",
    "DEMO.md",
    "NEXT_EXPERIMENTS.md",
    "EMAIL_DRAFT.md",
)

EVIDENCE_TYPES = {
    "directly_measured",
    "owner_observed",
    "repository_verified",
    "public_polar",
    "architectural_inference",
    "hypothesis",
    "unknown",
}

CONFIDENCE = {"high", "medium", "low"}

FIELD_KEYS = (
    "claim",
    "evidence_type",
    "sources",
    "date",
    "confidence",
    "does_not_prove",
)

BANNED = (
    "solved everything",
    "the llm was stupid",
    "universally bypasses",
    "invisible to ats",
    "polar solved",
    "the spawn is rejected",
    "spam-flagged",
)

CLAIM_HEAD = re.compile(r"^### (C\d+)\.\s+(.+)$")
FIELD_LINE = re.compile(r"^- ([a-z_]+):\s*(.*)$")
GIT_SOURCE = re.compile(r"^git:([0-9a-f]{7,40}):(.+)$")
HTTP_SOURCE = re.compile(r"^https?://")
PHONE = re.compile(r"\+1\s*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}")


def _git_ok(sha: str, path: str) -> bool:
    spec = f"{sha}:{path}"
    result = subprocess.run(
        ["git", "cat-file", "-e", spec],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def parse_claims(text: str) -> list[dict]:
    claims: list[dict] = []
    current = None
    current_field = None
    for raw in text.splitlines():
        head = CLAIM_HEAD.match(raw)
        if head:
            if current:
                claims.append(current)
            current = {
                "id": head.group(1),
                "title": head.group(2).strip(),
                "claim": "",
                "evidence_type": "",
                "sources": [],
                "date": "",
                "confidence": "",
                "does_not_prove": "",
            }
            current_field = None
            continue
        if current is None:
            continue
        field = FIELD_LINE.match(raw)
        if field:
            key, value = field.group(1), field.group(2).strip()
            if key not in FIELD_KEYS:
                continue
            current_field = key
            if key == "sources":
                if value:
                    current["sources"].append(value.lstrip("- ").strip())
            else:
                current[key] = value
            continue
        if current_field == "sources" and raw.startswith("  - "):
            current["sources"].append(raw[4:].strip())
            continue
        if current_field and current_field != "sources" and raw.startswith("  "):
            current[current_field] = (current[current_field] + " " + raw.strip()).strip()
    if current:
        claims.append(current)
    return claims


def check() -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_FILES:
        path = POLAR / name
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    readme = ROOT / "README.md"
    if readme.is_file():
        head = "".join(readme.read_text(encoding="utf-8").splitlines(True)[:20])
        if "polar/README.md" not in head:
            errors.append("root README.md first 20 lines must point at polar/README.md")
    else:
        errors.append("missing README.md")

    evidence_path = POLAR / "EVIDENCE.md"
    if not evidence_path.is_file():
        return errors

    evidence = evidence_path.read_text(encoding="utf-8")
    claims = parse_claims(evidence)
    if len(claims) < 8:
        errors.append(f"EVIDENCE.md has {len(claims)} claims; need at least 8")

    seen_ids: set[str] = set()
    for claim in claims:
        cid = claim["id"]
        if cid in seen_ids:
            errors.append(f"duplicate claim id {cid}")
        seen_ids.add(cid)
        for key in FIELD_KEYS:
            if key == "sources":
                if not claim["sources"]:
                    errors.append(f"{cid} missing sources")
            elif not claim[key]:
                errors.append(f"{cid} missing {key}")
        if claim["evidence_type"] and claim["evidence_type"] not in EVIDENCE_TYPES:
            errors.append(f"{cid} bad evidence_type {claim['evidence_type']}")
        if claim["confidence"] and claim["confidence"] not in CONFIDENCE:
            errors.append(f"{cid} bad confidence {claim['confidence']}")
        for source in claim["sources"]:
            git_match = GIT_SOURCE.match(source)
            if git_match:
                sha, path = git_match.group(1), git_match.group(2)
                if not _git_ok(sha, path):
                    errors.append(f"{cid} missing git object {source}")
                continue
            if HTTP_SOURCE.match(source):
                continue
            repo_path = ROOT / source
            if not repo_path.exists():
                errors.append(f"{cid} missing source {source}")

    email = POLAR / "EMAIL_DRAFT.md"
    if email.is_file():
        email_text = email.read_text(encoding="utf-8")
        if "do not send" not in email_text.lower():
            errors.append("EMAIL_DRAFT.md must say Do not send")
        if "hiring@polarbrowser.com" not in email_text:
            errors.append("EMAIL_DRAFT.md must name hiring@polarbrowser.com")

    for name in REQUIRED_FILES:
        path = POLAR / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in BANNED:
            if phrase in lowered:
                errors.append(f"{path.relative_to(ROOT)} contains banned phrase: {phrase}")
        if PHONE.search(text):
            errors.append(f"{path.relative_to(ROOT)} looks like it contains a phone number")

    return errors


def main() -> int:
    errors = check()
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
