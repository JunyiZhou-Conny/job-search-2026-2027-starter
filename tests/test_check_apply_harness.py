#!/usr/bin/env python3
"""Harness check: branded Chrome without Copilot is not ready."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

import check_apply_harness as harness  # noqa: E402


class TestCheckApplyHarness(unittest.TestCase):
    def test_empty_home_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = harness.inspect(home=Path(tmp))
        self.assertFalse(report["ready"])
        self.assertTrue(report["blockers"])

    def test_simplify_in_chrome_profile_is_ready_when_using_that_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            ext = (
                home
                / ".config"
                / "google-chrome"
                / "Default"
                / "Extensions"
                / harness.SIMPLIFY_EXTENSION_ID
                / "3.0.0_0"
            )
            ext.mkdir(parents=True)
            report = harness.inspect(home=home)
        # Branded Chrome binary may still exist on this VM; readiness then
        # depends on whether inspect thinks computer-use is branded.
        self.assertTrue(
            report["profiles"]["google-chrome"]["simplify_installed"]
        )
        if report["using_branded_chrome"]:
            self.assertTrue(report["ready"])


if __name__ == "__main__":
    unittest.main()
