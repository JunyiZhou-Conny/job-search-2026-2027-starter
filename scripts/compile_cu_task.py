#!/usr/bin/env python3
"""Compile a Computer Use action sheet and lint Task strings.

The clicker starts with a clean Task context. The parent is the brain.
This module is the parent compiler: a sheet of final actions becomes a
bounded Task string, and known Twitch-style anti-patterns fail lint.

Usage:
  python3 scripts/compile_cu_task.py compile path/to/sheet.yaml
  python3 scripts/compile_cu_task.py lint path/to/task.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MODES = ("execute", "verify", "repair", "submit")
FORBIDDEN_ALWAYS = ("autofill_again", "generate_with_ai", "reload")
SEARCHABLE_DROPDOWN = "searchable_dropdown"

ANTI_PATTERNS = (
    (re.compile(r"verify each", re.I), "verify_each_mutation"),
    (re.compile(r"reading the widget back", re.I), "verify_each_mutation"),
    (re.compile(r"for EVERY question", re.I), "report_every_field"),
    (re.compile(r"Report every widget", re.I), "report_every_field"),
    (re.compile(r"report the values of:", re.I), "report_untouched_fields"),
    (re.compile(r"covering the whole filled form", re.I), "full_form_audit"),
    (re.compile(r"screenshots covering the whole", re.I), "full_form_audit"),
    (re.compile(r"both in one", re.I), "cosmetic_composition"),
    (re.compile(r"fit both", re.I), "cosmetic_composition"),
    (re.compile(r"same screenshot", re.I), "cosmetic_composition"),
    (re.compile(r"keep (trying|scrolling|retrying)", re.I), "unbounded_retry"),
    (re.compile(r"until (it|the value) (works|sticks|persists)", re.I), "unbounded_retry"),
    (re.compile(r"Fill-and-review", re.I), "execute_plus_audit"),
    (re.compile(r"Only scroll\.", re.I), "scroll_only_method"),
)


def lint_task(text: str) -> list[str]:
    hits = []
    for pat, name in ANTI_PATTERNS:
        if pat.search(text) and name not in hits:
            hits.append(name)
    if re.search(r"showing widgets \d+ to \d+", text, re.I):
        if "cosmetic_composition" not in hits:
            hits.append("cosmetic_composition")
    return hits


def _require(sheet: dict, key: str):
    if key not in sheet:
        raise ValueError(f"action sheet missing {key}")
    return sheet[key]


def lint_sheet(sheet: dict) -> list[str]:
    hits = []
    mode = sheet.get("mode")
    if mode not in MODES:
        hits.append("unknown_mode")
        return hits
    target = sheet.get("target") or {}
    if not target.get("url"):
        hits.append("missing_target_url")
    mutations = sheet.get("mutations") or []
    evidence = sheet.get("evidence") or []
    bootstrap = sheet.get("bootstrap") or {}
    if mode == "verify":
        if mutations:
            hits.append("verify_has_mutations")
        if not sheet.get("read"):
            hits.append("verify_missing_reads")
        sections = {item.get("section") for item in sheet.get("read") or [] if item.get("section")}
        for shot in evidence:
            covers = shot.get("covers") or []
            cover_sections = {item.get("section") for item in (sheet.get("read") or []) if item.get("field") in covers}
            if len(cover_sections) > 1:
                hits.append("evidence_spans_distant_sections")
    if mode in {"execute", "repair"} and not mutations:
        if not (mode == "execute" and bootstrap.get("autofill_once")):
            hits.append("execute_missing_mutations")
    if bootstrap.get("autofill_once") and mutations:
        hits.append("autofill_plus_mutations")
    if mode == "submit":
        if not sheet.get("submit_permitted"):
            hits.append("submit_without_permission")
    else:
        forbidden = set(sheet.get("forbidden") or [])
        if "submit" not in forbidden and mode != "submit":
            hits.append("submit_not_forbidden")
    if mode == "execute" and any(item.get("audit") for item in mutations):
        hits.append("execute_plus_audit")
    names = [m.get("field") for m in mutations]
    if len(names) != len(set(names)):
        hits.append("duplicate_mutation_fields")
    for item in mutations:
        if "value" in item and not isinstance(item.get("value"), str):
            hits.append("non_string_value")
    if len(evidence) > 3 and mode != "submit":
        hits.append("too_many_screenshots")
    return hits


def _forbidden_lines(sheet: dict) -> list[str]:
    forbidden = list(sheet.get("forbidden") or [])
    for item in FORBIDDEN_ALWAYS:
        if item not in forbidden:
            forbidden.append(item)
    if sheet.get("mode") != "submit" and "submit" not in forbidden:
        forbidden.append("submit")
    labels = {
        "submit": "Do not click Submit or any final Apply button.",
        "autofill_again": "Do not click Run Autofill Again or Autofill This Page.",
        "generate_with_ai": "Do not click Generate with AI.",
        "reload": "Do not reload the page.",
    }
    return [labels.get(item, f"Do not {item}.") for item in forbidden]


def _commit_hint(commit: str) -> str:
    if commit == SEARCHABLE_DROPDOWN:
        return (
            "Searchable dropdown: type the value, click the matching option "
            "(highlight is not a commit), then Tab off the widget. Wait for "
            "the value to settle. Read it once. If it reverted, try one other "
            "commit (Enter if you clicked, or click if you Entered). If it "
            "still reverted, mark the field unresolved and stop. Do not loop."
        )
    if commit == "radio":
        return "Click the exact option. Do not reopen the group after it shows the value."
    if commit == "paste":
        return "Ctrl+A, paste once, click outside the box. Do not type key by key."
    if commit == "clear":
        return "Select all, press Delete, click outside the box. Do not type a replacement."
    return "Set the value through the widget's normal control, then move on."


def compile_sheet(sheet: dict) -> str:
    problems = lint_sheet(sheet)
    if problems:
        raise ValueError("action sheet failed lint: " + ", ".join(problems))
    mode = sheet["mode"]
    target = sheet["target"]
    lines = [
        f"MODE {mode.upper()}. You are hands only. Do not rediscover the form.",
        f"Tab: {target.get('tab') or (target.get('company', '') + ' — ' + target.get('role', ''))}",
        f"URL contains: {target['url']}",
    ]
    if target.get("already_autofilled"):
        lines.append("The form is already filled. Touch only the named mutations.")
    bootstrap = sheet.get("bootstrap") or {}
    if bootstrap.get("identity_url"):
        lines.append(f"Open {bootstrap['identity_url']}. Read the visible account name only.")
        if bootstrap.get("identity_expected"):
            lines.append(f"Expected account name: {bootstrap['identity_expected']}.")
        lines.append("Do not click jobs, settings, or export on that site.")
    if bootstrap.get("open_apply"):
        lines.append(f"Open the apply URL in one tab: {target['url']}")
    if bootstrap.get("autofill_once"):
        lines.append("Click Simplify Copilot Autofill once. Wait until it finishes.")
        lines.append("Do not scroll the form to inspect or report fields after Autofill.")
    lines.extend(_forbidden_lines(sheet))
    untouched = sheet.get("do_not_touch") or []
    if untouched:
        lines.append("Do not touch: " + "; ".join(untouched) + ".")
    if mode == "verify":
        lines.append("Read only these facts. Do not click. Do not type.")
        for item in sheet["read"]:
            lines.append(f"- {item['field']}" + (f" ({item['section']})" if item.get("section") else ""))
        lines.append("Once each named fact is readable, stop.")
        lines.append("Do not scroll to compose a prettier screenshot.")
        lines.append("If two facts are far apart, take two screenshots. Never hunt for one viewport that shows both.")
        lines.append("Maximum 8 scroll actions. Then report what you have.")
    if mode in {"execute", "repair"} and (sheet.get("mutations") or []):
        lines.append("Mutations in page order. Do all of them, then stop.")
        lines.append("Do not screenshot or read back after each field.")
        if mode == "repair":
            lines.append("Repair only the mismatches listed. Nothing else.")
        for item in sheet["mutations"]:
            commit = item.get("commit") or "control"
            lines.append(f"- {item['field']} → {item['value']}")
            lines.append(f"  {_commit_hint(commit)}")
        lines.append("After the last mutation, wait for the page to settle.")
        lines.append("One bounded retry per field that failed to persist, then mark it unresolved.")
    if mode == "submit":
        lines.append("Click Submit exactly once. Do not retry.")
        lines.append("Capture the result page. Then stop.")
    evidence = sheet.get("evidence") or []
    if evidence:
        lines.append("Evidence (separate shots if the facts are far apart):")
        for shot in evidence:
            covers = ", ".join(shot.get("covers") or [])
            lines.append(f"- {shot['name']}" + (f" covers {covers}" if covers else ""))
    lines.append("Stop. Do not write a field-by-field audit of untouched widgets.")
    return "\n".join(lines) + "\n"


def _load_sheet(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("action sheet must be a mapping")
        return data
    # Tiny fallback for the leftover-paste case used in tests without PyYAML.
    import json
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile", help="print a Task string from an action sheet")
    c.add_argument("sheet")
    el = sub.add_parser("lint", help="lint a Task string; exit 1 on hits")
    el.add_argument("task")
    args = ap.parse_args(argv)
    if args.cmd == "compile":
        sheet = _load_sheet(Path(args.sheet))
        sys.stdout.write(compile_sheet(sheet))
        return 0
    text = Path(args.task).read_text(encoding="utf-8")
    hits = lint_task(text)
    if hits:
        print("anti-patterns: " + ", ".join(hits), file=sys.stderr)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
