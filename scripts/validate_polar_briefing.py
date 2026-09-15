#!/usr/bin/env python3
"""Refuse briefing copy that paints designed work as Polar production."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "docs" / "architecture" / "briefing" / "model.js"
README = ROOT / "docs" / "architecture" / "briefing" / "README.md"

REQUIRED_SCENES = (
    "open",
    "market",
    "doing",
    "tools",
    "loop",
    "clock",
    "states",
    "worker",
    "weight",
    "resume",
    "learn",
    "use",
    "map",
)
REQUIRED_PHRASES = (
    "claim_run_id",
    "READY_PRIORITY",
    "production-learning-daily",
    "missing_production_resume",
    "Polar is not wired",
    "human merge",
    "Original Job Post",
)
FORBIDDEN_PHRASES = (
    "438 unique",
    "438 KEEP",
    "42.5%",
)
ALLOWED_TRUTH = (
    "production",
    "designed",
    "unproven",
    "historical",
    "press",
    "unknown",
)


def validate(model_text: str | None = None) -> list[str]:
    text = model_text if model_text is not None else MODEL.read_text(encoding="utf-8")
    errors: list[str] = []
    if not MODEL.is_file():
        errors.append(f"missing {MODEL}")
        return errors
    if not README.is_file():
        errors.append(f"missing {README}")
    for scene_id in REQUIRED_SCENES:
        if f'id: "{scene_id}"' not in text:
            errors.append(f"missing scene {scene_id}")
    truths = re.findall(r'truth: "([a-z]+)"', text)
    if not truths:
        errors.append("no truth labels")
    for label in truths:
        if label not in ALLOWED_TRUTH:
            errors.append(f"illegal truth {label}")
    if "truth: \"press\"" not in text:
        errors.append("market scene must stay labeled press")
    if "truth: \"production\"" not in text:
        errors.append("production scenes are missing")
    if text.count('id: "B') < 6:
        errors.append("need six bands")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"missing required phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in text:
            errors.append(f"forbidden metric or stale count {phrase!r}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("polar briefing copy is not honest:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("polar briefing copy keeps production and designed work apart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
