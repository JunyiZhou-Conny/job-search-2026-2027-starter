#!/usr/bin/env python3
"""Check that GROK_BOT_HANDOFF.md only names files that exist.

  python3 scripts/research/verify_grok_bot_handoff_paths.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / "docs/grok-bot-management/GROK_BOT_HANDOFF.md"
README = ROOT / "docs/grok-bot-management/README.md"

# Repo-relative paths the paste or how-to may name.
PATH_RE = re.compile(
    r"(?:(?:docs|knowledge|jobs|scripts)/[A-Za-z0-9_./-]+|AGENTS\.md)"
)


def extract_paths(text: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in PATH_RE.finditer(text):
        path = match.group(0).rstrip(").,;`")
        if path.endswith("/"):
            path = path[:-1]
        if path not in seen:
            seen.add(path)
            found.append(path)
    return found


def main() -> int:
    if not HANDOFF.is_file():
        print(f"MISSING handoff: {HANDOFF}")
        return 1
    text = HANDOFF.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    paths = extract_paths(text)
    missing = []
    present = []
    for rel in paths:
        target = ROOT / rel
        if target.exists():
            present.append(rel)
        else:
            missing.append(rel)
    print(f"checked {len(paths)} named paths")
    for rel in present:
        print(f"OK {rel}")
    if "GROK_BOT_HANDOFF.md" not in readme:
        print("MISSING README link to GROK_BOT_HANDOFF.md")
        return 1
    print("OK README links to GROK_BOT_HANDOFF.md")
    if missing:
        for rel in missing:
            print(f"MISSING {rel}")
        return 1
    print("all named paths exist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
