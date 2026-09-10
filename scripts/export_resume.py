#!/usr/bin/env python3
"""Export a sanitized family resume with the approved application mailbox.

Source-controlled TeX keeps ``[REDACTED]`` for email. Polar's application
mailbox (``RESUME_EMAIL`` or ``SIMPLIFY_EMAIL``) is the only contact source.
Do not use ``HARVARD_EMAIL``. Polar treats a Harvard address in a normal
contact field as wrong.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from stitch_family_resume import FAMILIES, ROOT

EXPORT_DIR = ROOT / "generated" / "resumes" / "export"
MAILTO_PLACEHOLDER = r"\href{mailto:[REDACTED]}{[REDACTED]}"
APPLICATION_EMAIL_KEYS = ("RESUME_EMAIL", "SIMPLIFY_EMAIL")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def application_email(env: dict[str, str] | None = None) -> str:
    source = env if env is not None else os.environ
    for key in APPLICATION_EMAIL_KEYS:
        value = (source.get(key) or "").strip()
        if not value:
            continue
        if value.upper() == "[REDACTED]" or "[REDACTED]" in value:
            continue
        if not EMAIL_RE.match(value):
            raise SystemExit(f"{key} is not a usable email")
        return value
    raise SystemExit(
        "application email missing. Set RESUME_EMAIL or SIMPLIFY_EMAIL "
        "to the approved application mailbox. Do not use HARVARD_EMAIL."
    )


def apply_contact(tex: str, email: str) -> str:
    if MAILTO_PLACEHOLDER not in tex:
        raise SystemExit("source tex has no sanitized mailto placeholder")
    if not EMAIL_RE.match(email) or "[REDACTED]" in email:
        raise SystemExit("refusing to export an unusable contact email")
    return tex.replace(MAILTO_PLACEHOLDER, f"\\href{{mailto:{email}}}{{{email}}}")


def export_family(family: str) -> Path:
    if family not in FAMILIES:
        raise SystemExit(f"family {family!r} has no fragment")
    _fragment, source = FAMILIES[family]
    if not source.is_file():
        raise SystemExit(f"missing sanitized source {source}")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    dest = EXPORT_DIR / source.name
    dest.write_text(apply_contact(source.read_text(), application_email()))
    script = ROOT / "scripts" / "compile_resume.sh"
    proc = subprocess.run([str(script), str(dest)], cwd=ROOT, check=False)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    pdf = dest.with_suffix(".pdf")
    if not pdf.is_file():
        raise SystemExit(f"export compile did not write {pdf}")
    return pdf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", default="ai_infra")
    args = parser.parse_args()
    pdf = export_family(args.family)
    print(pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
