#!/usr/bin/env python3
"""Copy identity and education from the master resume into a family fragment."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "resumes" / "base" / "JZ_resume.tex"
BEGIN = "\\begin{document}"
EDUCATION = "% Education"
SKILLS = "% Technical Skills"
HYPERREF = "\\usepackage[pdftex]{hyperref}"
HYPERREF_HIDELINKS = "\\usepackage[pdftex,hidelinks]{hyperref}"
FAMILIES = {
    "ai_infra": (
        ROOT / "resumes" / "families" / "ai_infra" / "body_fragment.tex",
        ROOT / "resumes" / "families" / "ai_infra" / "ai_infra_v1.tex",
    )
}


def require_sentinel(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx < 0:
        raise SystemExit(f"master resume is missing required sentinel {needle!r}")
    return idx


def with_hidelinks(tex: str) -> str:
    if "hidelinks" in tex:
        return tex
    if HYPERREF not in tex:
        raise SystemExit(f"master resume is missing {HYPERREF!r}")
    return tex.replace(HYPERREF, HYPERREF_HIDELINKS, 1)


def assemble(master: str, fragment: str) -> str:
    begin = require_sentinel(master, BEGIN)
    education = require_sentinel(master, EDUCATION)
    skills = require_sentinel(master, SKILLS)
    if not begin < education < skills:
        raise SystemExit(
            "master resume sentinels are out of order: "
            f"{BEGIN}@{begin}, {EDUCATION}@{education}, {SKILLS}@{skills}"
        )
    return with_hidelinks(master[:begin] + master[begin:education] + master[education:skills] + fragment)


def stitch(family: str) -> Path:
    if family not in FAMILIES:
        raise SystemExit(f"family {family!r} has no fragment")
    fragment_path, dest = FAMILIES[family]
    dest.write_text(assemble(MASTER.read_text(), fragment_path.read_text()))
    return dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", default="ai_infra")
    args = parser.parse_args()
    dest = stitch(args.family)
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
