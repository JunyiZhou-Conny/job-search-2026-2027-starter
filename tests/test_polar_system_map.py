#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import TRUSTED_WORKFLOW_NAMES, load_operator  # noqa: E402
from validate_polar_system_map import (  # noqa: E402
    APPLY,
    COMPANION,
    CONCURRENCY,
    LEARNING,
    MASTER,
    validate,
)


class PolarSystemMapTests(unittest.TestCase):
    def test_validator_passes_against_live_maps(self) -> None:
        self.assertEqual(validate(), [])

    def test_every_trusted_workflow_is_on_the_master_map(self) -> None:
        master = MASTER.read_text(encoding="utf-8")
        for name in TRUSTED_WORKFLOW_NAMES:
            self.assertIn(name, master)

    def test_companion_names_the_live_revision(self) -> None:
        revision = load_operator(ROOT)["policy_revision"]
        self.assertIn(revision, COMPANION.read_text(encoding="utf-8"))

    def test_map_sources_exist(self) -> None:
        for path in (MASTER, APPLY, CONCURRENCY, LEARNING, COMPANION):
            self.assertTrue(path.is_file(), path)


if __name__ == "__main__":
    unittest.main()
