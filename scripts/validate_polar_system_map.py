#!/usr/bin/env python3
"""Check Polar architecture maps against live operator policy."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import TRUSTED_WORKFLOW_NAMES, load_operator  # noqa: E402

ARCH = ROOT / "docs" / "architecture"
MASTER = ARCH / "polar-system-map.mmd"
APPLY = ARCH / "polar-apply-worker.mmd"
CONCURRENCY = ARCH / "polar-state-concurrency.mmd"
LEARNING = ARCH / "polar-learning-loop.mmd"
COMPANION = ARCH / "POLAR_SYSTEM.md"

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
REQUIRED_HEADINGS = (
    "How to read this map / 怎么看这张图",
    "Major components",
    "Workflow responsibilities",
    "State meanings",
    "Concurrency model",
    "READY_REGULAR vs READY_PRIORITY",
    "Simplify environment model",
    "Recovery model",
    "State ownership table",
    "Self-improvement loop",
    "Human intervention boundaries",
    "What is automatic today vs what still needs a human",
    "Source-of-truth references",
)
REQUIRED_STATES = (
    "NEW",
    "READY_REGULAR",
    "READY_PRIORITY",
    "IN_PROGRESS",
    "REVIEW_READY",
    "SUBMITTED",
    "SUBMISSION_UNKNOWN",
    "BLOCKED",
    "SKIP",
)
REQUIRED_MASTER_PHRASES = (
    "claim_run_id",
    "select_next_apply_job",
    "attempt_claim_job",
    "max_new_jobs",
    "Historical duplicate guard",
    "Copilot UI actually injected?",
    "env_simplify_copilot",
    "OWNER_ACTION_REQUIRED",
    "writing_log",
    "submit_claim_still_held",
    "pick_canonical_requisition_row",
    "production-learning-daily",
    "human merge",
    "PREFERENCES.md",
    "polar-sheet-migration",
    "historical only",
    "岗位仍有效",
    "禁止盲投",
    "重点岗位",
)
FORBIDDEN_ACTIVE = (
    "acquire polar_browser",
    "needs_browser_lock: true",
    "shared daily regular submission pool",
)
TRACE_REQUIREMENTS: Dict[str, Tuple[Path, Sequence[str]]] = {
    "ordinary_job": (
        MASTER,
        ("discover-jobs-hourly", "READY_REGULAR", "apply-ready-jobs", "SUBMITTED"),
    ),
    "prioritized_job": (
        MASTER,
        ("READY_PRIORITY", "writing_log", "priority_submit_permitted"),
    ),
    "concurrent_workers": (
        MASTER,
        ("Worker A → Job X", "Worker B → Job Y", "Worker C → Job Z"),
    ),
    "claim_race": (
        CONCURRENCY,
        ("last write + readback", "already_claimed", "claim_run_id"),
    ),
    "requisition": (
        CONCURRENCY,
        ("pick_canonical_requisition_row", "只有 canonical 可 Submit"),
    ),
    "copilot_missing": (
        MASTER,
        ("MISSING / UNKNOWN", "restore READY", "env_simplify_copilot"),
    ),
    "crash_before_submit": (
        CONCURRENCY,
        ("崩溃在 ATS 前", "崩溃在填表中"),
    ),
    "crash_after_submit": (
        CONCURRENCY,
        ("崩溃在 Submit 点击后", "SUBMISSION_UNKNOWN"),
    ),
    "submission_unknown": (
        MASTER,
        ("SUBMISSION_UNKNOWN", "禁止盲投"),
    ),
    "learning_loop": (
        LEARNING,
        ("production-learning-daily", "human merge", "next Polar bootstrap"),
    ),
    "schema_migration": (
        MASTER,
        ("polar-sheet-migration", "apply 不得自补列"),
    ),
    "chatgpt_not_required": (
        MASTER,
        ("chatgpt-production-review", "非必经"),
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _errors_for_missing(label: str, haystack: str, needles: Iterable[str]) -> List[str]:
    errors: List[str] = []
    for needle in needles:
        if needle not in haystack:
            errors.append(f"{label} missing {needle!r}")
    return errors


def _mermaid_balance(path: Path, text: str) -> List[str]:
    errors: List[str] = []
    head = "\n".join(text.splitlines()[:12])
    if "flowchart" not in head:
        errors.append(f"{path.name} has no flowchart declaration near the top")
    opens = len(re.findall(r"\bsubgraph\b", text))
    closes = len(re.findall(r"(?m)^[ \t]*end\b", text))
    if opens != closes:
        errors.append(f"{path.name} subgraph/end imbalance: {opens} subgraph, {closes} end")
    if "\t" in text:
        errors.append(f"{path.name} contains tabs")
    if not CJK_RE.search(text):
        errors.append(f"{path.name} has no Chinese labels")
    return errors


def _disabled_marked(master: str, name: str) -> bool:
    block = re.search(
        rf'{re.escape(name)}.*?(?:\n\s*class |\n\s*end\b)',
        master,
        re.S,
    )
    if block and "disabled" in block.group(0):
        return True
    return bool(
        re.search(
            rf'class [^\n]*\bW[6-9]\b[^\n]*disabled|{re.escape(name)}<br/>disabled',
            master,
        )
    )


def validate() -> List[str]:
    errors: List[str] = []
    for path in (MASTER, APPLY, CONCURRENCY, LEARNING, COMPANION):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        return errors

    operator = load_operator(ROOT)
    schedules = operator.get("schedules") or {}
    master = _read(MASTER)
    apply_text = _read(APPLY)
    concurrency = _read(CONCURRENCY)
    learning = _read(LEARNING)
    companion = _read(COMPANION)
    all_maps = "\n".join((master, apply_text, concurrency, learning))

    for name in TRUSTED_WORKFLOW_NAMES:
        if name not in master:
            errors.append(f"master map missing workflow {name}")
        meta = next(
            (row for row in schedules.values() if row.get("workflow") == name),
            None,
        )
        if meta is None:
            errors.append(f"polar_operator.yaml missing schedule for {name}")
            continue
        enabled = bool(meta.get("enabled"))
        if enabled and name in ("chatgpt-production-review", "cursor-production-maintenance"):
            errors.append(f"{name} is enabled in YAML but the map treats it as optional")
        if not enabled and not _disabled_marked(master, name):
            errors.append(f"disabled workflow {name} is not visually distinguished")

    errors.extend(_mermaid_balance(MASTER, master))
    errors.extend(_mermaid_balance(APPLY, apply_text))
    errors.extend(_mermaid_balance(CONCURRENCY, concurrency))
    errors.extend(_mermaid_balance(LEARNING, learning))
    errors.extend(_errors_for_missing("master", master, REQUIRED_STATES))
    errors.extend(_errors_for_missing("master", master, REQUIRED_MASTER_PHRASES))
    errors.extend(_errors_for_missing("companion", companion, REQUIRED_HEADINGS))

    if "acquire polar_browser" in all_maps.lower().replace("禁止 acquire", ""):
        if re.search(r"(?i)(?<!禁止 )acquire polar_browser", all_maps):
            errors.append("maps treat acquire polar_browser as an active step")
    for phrase in FORBIDDEN_ACTIVE:
        if phrase in all_maps:
            errors.append(f"maps contain forbidden active phrase {phrase!r}")

    if "needs_browser_lock = false" not in apply_text:
        errors.append("apply-worker map does not state needs_browser_lock = false")
    if "historical only" not in master or "historical only" not in concurrency:
        errors.append("polar_browser is not labeled historical only on master and concurrency maps")
    if "ChatGPT" in companion and "Not a required hop" not in companion:
        if "not a required hop" not in companion:
            errors.append("companion does not say ChatGPT is not a required hop")

    for trace, (path, needles) in TRACE_REQUIREMENTS.items():
        errors.extend(_errors_for_missing(f"trace {trace}", _read(path), needles))

    revision = str(operator.get("policy_revision") or "")
    if revision and revision not in companion:
        errors.append(f"companion does not name policy_revision {revision}")
    if int((operator.get("canary") or {}).get("max_jobs_per_run") or 0) != 3:
        errors.append("live canary.max_jobs_per_run is not 3")
    elif "max_new_jobs = 3" not in master:
        errors.append("master does not state max_new_jobs = 3")

    return errors


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    errors = validate()
    if errors:
        for item in errors:
            print(f"FAIL {item}")
        print(f"{len(errors)} polar system map check(s) failed")
        return 1
    print("polar system map checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
