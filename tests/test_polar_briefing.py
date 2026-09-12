#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from serve_polar_briefing import SPRING, BriefingHandler  # noqa: E402
from validate_polar_briefing import FORBIDDEN_PHRASES, validate  # noqa: E402


class PolarBriefingTests(unittest.TestCase):
    def test_live_model_passes(self) -> None:
        self.assertEqual(validate(), [])

    def test_designed_live_resume_fails(self) -> None:
        model = Path(ROOT / "docs" / "architecture" / "briefing" / "model.js").read_text(
            encoding="utf-8"
        )
        poisoned = model.replace("Polar is not wired to it.", "Polar attaches it on every row.")
        errors = validate(poisoned)
        self.assertTrue(any("Polar is not wired" in error for error in errors))

    def test_stale_keep_count_is_rejected(self) -> None:
        model = Path(ROOT / "docs" / "architecture" / "briefing" / "model.js").read_text(
            encoding="utf-8"
        )
        poisoned = model + "\nconst stale = '438 KEEP jobs';\n"
        errors = validate(poisoned)
        self.assertTrue(any(phrase in " ".join(errors) for phrase in FORBIDDEN_PHRASES))

    def test_server_maps_spring_from_apply_queue(self) -> None:
        handler = BriefingHandler.__new__(BriefingHandler)
        path = handler.translate_path("/spring.js")
        self.assertEqual(Path(path), SPRING)
        self.assertTrue(SPRING.is_file())


if __name__ == "__main__":
    unittest.main()
