#!/usr/bin/env python3
"""ATS sweep Polar results stay redacted and do not Submit."""

from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R1 = ROOT / "generated" / "polar" / "results" / "P-20260906-001.md"
R2 = ROOT / "generated" / "polar" / "results" / "P-20260906-002.md"
SCALE = ROOT / "docs" / "automation" / "POLAR_SCALE.md"
MATRIX = ROOT / "docs" / "experiments" / "polar_ats_matrix.md"

NANP_LEAK = re.compile(
    r"(?:\+1[\s.-]+)?(?:\(\d{3}\)[\s.-]*|\d{3}[\s.-]+)\d{3}[\s.-]+\d{4}"
)


class TestPolarAtsSweepResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solidigm = R1.read_text(encoding="utf-8")
        cls.citadel = R2.read_text(encoding="utf-8")
        cls.scale = SCALE.read_text(encoding="utf-8")
        cls.matrix = MATRIX.read_text(encoding="utf-8")

    def test_solidigm_is_clean_fill_not_submitted(self):
        self.assertIn("submitted: no", self.solidigm)
        self.assertIn("ready to submit: yes", self.solidigm)
        self.assertIn("fill: yes", self.solidigm)
        self.assertIn("auth wall: no", self.solidigm)
        self.assertIn("jobs.smartrecruiters.com", self.solidigm)
        self.assertIn("J20260907-001", self.solidigm)
        self.assertIn("P1: opened", self.solidigm)
        self.assertNotIn("@", self.solidigm)
        self.assertIsNone(NANP_LEAK.search(self.solidigm))

    def test_citadel_is_partial_fill_not_submitted(self):
        self.assertIn("submitted: no", self.citadel)
        self.assertIn("ready to submit: no", self.citadel)
        self.assertIn("fill: partial", self.citadel)
        self.assertIn("www.citadel.com", self.citadel)
        self.assertIn("J20260907-002", self.citadel)
        self.assertIn("return offer", self.citadel)
        self.assertIn("late stage", self.citadel)
        self.assertNotIn("@", self.citadel)
        self.assertIsNone(NANP_LEAK.search(self.citadel))
        self.assertNotIn("404663", self.citadel)

    def test_p1_open_and_matrix_updated(self):
        self.assertIn("P1 is open", self.scale)
        self.assertIn("3 to 5 job serial Polar", self.scale)
        self.assertIn("batch is now permitted", self.scale)
        self.assertIn("SmartRecruiters", self.matrix)
        self.assertIn("P1 opened", self.matrix)
        self.assertIn("partial", self.matrix)

    def test_ledger_rows_exist_and_quantbot_stays_unique(self):
        apps = ROOT / "data" / "applications.csv"
        attempts = ROOT / "data" / "apply_attempts.csv"
        with apps.open(encoding="utf-8", newline="") as fh:
            job_ids = [row["id"] for row in csv.DictReader(fh)]
        with attempts.open(encoding="utf-8", newline="") as fh:
            attempt_ids = [row["attempt_id"] for row in csv.DictReader(fh)]
        self.assertEqual(job_ids.count("J20260904-001"), 1)
        self.assertEqual(job_ids.count("J20260907-001"), 1)
        self.assertEqual(job_ids.count("J20260907-002"), 1)
        self.assertEqual(attempt_ids.count("A20260907-001"), 1)
        self.assertEqual(attempt_ids.count("A20260907-002"), 1)
        with apps.open(encoding="utf-8", newline="") as fh:
            by_id = {row["id"]: row for row in csv.DictReader(fh)}
        self.assertEqual(by_id["J20260907-001"]["status"], "ready_to_apply")
        self.assertEqual(by_id["J20260907-002"]["status"], "ready_to_apply")
        self.assertEqual(by_id["J20260907-001"]["company"], "Solidigm")
        self.assertEqual(by_id["J20260907-002"]["company"], "Citadel")
        self.assertEqual(by_id["J20260904-001"]["employment_type"], "internship")
        self.assertEqual(by_id["J20260907-001"]["employment_type"], "internship")
        self.assertEqual(by_id["J20260907-002"]["employment_type"], "internship")
        self.assertEqual(by_id["J20260907-002"]["needs_review"], "true")
        self.assertNotIn("J20260906-001", job_ids)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
