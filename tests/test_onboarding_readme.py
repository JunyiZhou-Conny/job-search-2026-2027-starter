#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_onboarding_readme as checker  # noqa: E402


class TestOnboardingReadme(unittest.TestCase):
    def test_readme_paths_and_markers(self):
        self.assertEqual(checker.main([]), 0)


if __name__ == "__main__":
    unittest.main()
