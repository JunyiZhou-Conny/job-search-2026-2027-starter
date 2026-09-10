#!/usr/bin/env python3
"""Copy identity and education from the master resume into a family fragment."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "resumes" / "base" / "JZ_resume.tex"
FAMILIES = {
    "ai_infra": (
        ROOT / "resumes" / "families" / "ai_infra" / "body_fragment.tex",
        ROOT / "resumes" / "families" / "ai_infra" / "ai_infra_v1.tex",
    )
}


def stitch(family: str) -> Path:
    if family not in FAMILIES:
        raise SystemExit(f"family {family!r} has no fragment")
    fragment_path, dest = FAMILIES[family]
    master = MASTER.read_text()
    fragment = fragment_path.read_text()
    preamble = master[: master.index("\\begin{document}")]
    header = master[master.index("\\begin{document}") : master.index("% Education")]
    education = master[master.index("% Education") : master.index("% Technical Skills")]
    dest.write_text(preamble + header + education + fragment)
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
