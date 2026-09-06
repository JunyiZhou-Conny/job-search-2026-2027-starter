#!/usr/bin/env python3
"""Rakuten Polar result is reach-only and stays off the ledger."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "generated" / "polar" / "results" / "P-20260904-002.md"
APPS = ROOT / "data" / "applications.csv"
ATTEMPTS = ROOT / "data" / "apply_attempts.csv"


class TestPolarRakutenResult(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = RESULT.read_text(encoding="utf-8")

    def test_reach_without_fill_or_submit(self):
        self.assertIn("submitted: no", self.text)
        self.assertIn("rakuten.wd1.myworkdayjobs.com", self.text)
        self.assertIn("reach: yes", self.text)
        self.assertIn("fill: no", self.text)
        self.assertIn("P1: closed", self.text)
        self.assertIn("Create Account", self.text)

    def test_does_not_invent_the_requisition_suffix(self):
        self.assertIn("requisition suffix is unknown", self.text)
        self.assertNotIn("J20260904-001", self.text)
        self.assertNotIn("A20260904-001", self.text)

    def test_ledger_has_no_rakuten_row(self):
        for path in (APPS, ATTEMPTS):
            with path.open(encoding="utf-8", newline="") as fh:
                blob = fh.read()
            self.assertNotIn("Rakuten", blob)
            self.assertNotIn("rakuten.wd1.myworkdayjobs.com", blob)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
