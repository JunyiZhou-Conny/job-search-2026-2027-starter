#!/usr/bin/env python3
"""Rewrite knowledge/careers_boards.yaml in one canonical order.

Sections keep a fixed order, companies sort case-insensitively inside each
section, and two spellings of one company that point at the same board
collapse to the first spelling seen. Comments survive: the header block, the
comment block above each section, trailing comments on an entry, and comment
lines that follow an entry.

Run it before committing a discovery run. Two runs that each add a company
then differ by one line each in a stable position, which git merges cleanly.

The grammar mirrors resolve_apply_url._parse_simple_yaml, the resolver's
fallback reader, so the output stays readable without PyYAML.

Usage:
  python3 scripts/automation/normalize_careers_boards.py          # rewrite in place
  python3 scripts/automation/normalize_careers_boards.py --check  # exit 1 if not canonical
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOARDS_YAML = ROOT / "knowledge" / "careers_boards.yaml"

SECTION_ORDER = ("greenhouse", "ashby", "lever", "workday")
WORKDAY_KEYS = ("host", "tenant", "site")
PLAIN_SCALAR = re.compile(r"[A-Za-z][A-Za-z0-9_.-]*")
YAML_WORDS = {"true", "false", "yes", "no", "on", "off", "null", "y", "n"}


@dataclass
class Entry:
    key: str
    value: str | dict[str, str]
    comment: str = ""
    leading: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Section:
    name: str
    comments: list[str] = field(default_factory=list)
    entries: list[Entry] = field(default_factory=list)


@dataclass
class Boards:
    header: list[str]
    sections: list[Section]

    def as_dict(self) -> dict:
        return {s.name: {e.key: e.value for e in s.entries} for s in self.sections}


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _split_comment(raw: str) -> tuple[str, str]:
    code, sep, comment = raw.partition("#")
    return code.rstrip(), comment.strip() if sep else ""


def parse(text: str) -> Boards:
    header: list[str] = []
    sections: list[Section] = []
    pending_comments: list[str] = []
    section: Section | None = None
    entry: Entry | None = None

    for raw in text.splitlines():
        code, comment = _split_comment(raw)
        if not code.strip():
            if section is None:
                header.append(raw.rstrip())
            elif not comment:
                entry = None
            elif entry is not None:
                entry.notes.append(comment)
            else:
                pending_comments.append(comment)
            continue
        indent = len(code) - len(code.lstrip(" "))
        stripped = code.strip()
        if indent == 0:
            if section is None:
                attached = []
                while header and header[-1].strip():
                    attached.insert(0, _split_comment(header.pop())[1])
                pending_comments = attached + pending_comments
            name = stripped.partition(":")[0]
            section = Section(name=name.strip(), comments=pending_comments)
            pending_comments = []
            sections.append(section)
            entry = None
            continue
        if section is None:
            raise ValueError(f"entry before any section: {raw!r}")
        if indent == 2:
            key, _, val = stripped.partition(":")
            value: str | dict[str, str] = _unquote(val) if val.strip() else {}
            entry = Entry(_unquote(key), value, comment, leading=pending_comments)
            pending_comments = []
            section.entries.append(entry)
            continue
        if entry is None or not isinstance(entry.value, dict):
            raise ValueError(f"nested value without a mapping entry: {raw!r}")
        k, _, v = stripped.partition(":")
        entry.value[k.strip()] = _unquote(v)

    while header and not header[-1].strip():
        header.pop()
    return Boards(header=header, sections=sections)


def _absorb(keep: Entry, other: Entry) -> None:
    keep.comment = keep.comment or other.comment
    keep.leading += [n for n in other.leading if n not in keep.leading]
    keep.notes += [n for n in other.notes if n not in keep.notes]


def dedupe(entries: list[Entry]) -> list[Entry]:
    """One entry per company. Repeated keys keep the last value, as PyYAML does.

    Spellings that differ only by case and point at the same board collapse to
    the first spelling seen; if they point at different boards both stay.
    """
    exact: dict[str, Entry] = {}
    for e in entries:
        prev = exact.get(e.key)
        if prev is None:
            exact[e.key] = e
            continue
        prev.value = e.value
        _absorb(prev, e)

    groups: dict[str, list[Entry]] = {}
    for e in exact.values():
        groups.setdefault(e.key.casefold(), []).append(e)

    out: list[Entry] = []
    for group in groups.values():
        first = group[0]
        if all(e.value == first.value for e in group):
            for e in group[1:]:
                _absorb(first, e)
            out.append(first)
        else:
            out.extend(group)
    return sorted(out, key=lambda e: (e.key.casefold(), e.key))


def normalize(boards: Boards) -> Boards:
    grouped: dict[str, list[Section]] = {}
    for s in boards.sections:
        grouped.setdefault(s.name, []).append(s)
    order = [n for n in SECTION_ORDER if n in grouped] + sorted(n for n in grouped if n not in SECTION_ORDER)
    sections = []
    for name in order:
        group = grouped[name]
        comments: list[str] = []
        entries: list[Entry] = []
        for s in group:
            comments += [c for c in s.comments if c not in comments]
            entries.extend(s.entries)
        sections.append(Section(name=name, comments=comments, entries=dedupe(entries)))
    return Boards(header=boards.header, sections=sections)


def scalar(s: str) -> str:
    if PLAIN_SCALAR.fullmatch(s) and s.lower() not in YAML_WORDS:
        return s
    return json.dumps(s, ensure_ascii=False)


def render(boards: Boards) -> str:
    lines = list(boards.header)
    for s in boards.sections:
        lines.append("")
        lines.extend(f"# {c}" for c in s.comments)
        if not s.entries:
            lines.append(f"{s.name}: {{}}")
            continue
        lines.append(f"{s.name}:")
        for e in s.entries:
            lines.extend(f"  # {n}" for n in e.leading)
            trail = f"  # {e.comment}" if e.comment else ""
            if isinstance(e.value, dict):
                lines.append(f"  {scalar(e.key)}:{trail}")
                keys = [k for k in WORKDAY_KEYS if k in e.value] + sorted(k for k in e.value if k not in WORKDAY_KEYS)
                lines.extend(f"    {k}: {scalar(e.value[k])}" for k in keys)
            else:
                lines.append(f"  {scalar(e.key)}: {scalar(e.value)}{trail}")
            lines.extend(f"  # {n}" for n in e.notes)
    return "\n".join(lines).lstrip("\n") + "\n"


def canonical(text: str) -> str:
    boards = normalize(parse(text))
    out = render(boards)
    if parse(out).as_dict() != boards.as_dict():
        raise RuntimeError("normalized output does not re-parse to the same boards")
    try:
        import yaml  # type: ignore
    except ImportError:
        return out
    loaded = yaml.safe_load(out) or {}
    expected = {name: (v or {}) for name, v in boards.as_dict().items()}
    if {k: (v or {}) for k, v in loaded.items()} != expected:
        raise RuntimeError("normalized output does not load as the same YAML")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report instead of rewriting; exit 1 when not canonical")
    ap.add_argument("--path", type=Path, default=BOARDS_YAML)
    args = ap.parse_args(argv)

    before = args.path.read_text(encoding="utf-8")
    after = canonical(before)
    if after == before:
        print(f"{args.path}: canonical")
        return 0
    if args.check:
        print(f"{args.path}: not canonical", file=sys.stderr)
        return 1
    args.path.write_text(after, encoding="utf-8")
    print(f"normalized {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
