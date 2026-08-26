#!/usr/bin/env python3
"""Check that THINKING.md blockquotes appear in SOURCES.md.

  python3 scripts/research/verify_grok_management_quotes.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "docs/grok-bot-management/SOURCES.md"
THINKING = ROOT / "docs/grok-bot-management/THINKING.md"


def strip_quote_markers(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("> "):
            lines.append(line[2:])
        elif line.startswith(">"):
            lines.append(line[1:])
        else:
            lines.append(line)
    return "\n".join(lines)


def normalize(text: str) -> str:
    return " ".join(
        strip_quote_markers(text).replace("\u2019", "'").replace("\u2014", "-").split()
    )


def blockquotes(text: str) -> list[str]:
    quotes: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith(">"):
            current.append(line[2:] if line.startswith("> ") else line[1:])
        elif current:
            quotes.append(" ".join(current))
            current = []
    if current:
        quotes.append(" ".join(current))
    return quotes


def main() -> int:
    source_norm = normalize(SOURCES.read_text(encoding="utf-8"))
    quotes = blockquotes(THINKING.read_text(encoding="utf-8"))
    missing = []
    for quote in quotes:
        if normalize(quote) not in source_norm:
            missing.append(quote)
    print(f"checked {len(quotes)} quotes")
    if missing:
        for quote in missing:
            print(f"MISSING: {quote}")
        return 1
    print("all THINKING.md blockquotes appear in SOURCES.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
