#!/usr/bin/env python3
"""The apply queue reads day-keyed and run-stamped triage files alike."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_apply_queue as gaq  # noqa: E402

HEADER = "decision,company,role,url,apply_url,apply_url_confidence\n"


class TestTriageSelection(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.gen = Path(self.tmp.name) / "generated"
        self.gen.mkdir()
        self.old_root = gaq.ROOT
        gaq.ROOT = Path(self.tmp.name)
        self.addCleanup(setattr, gaq, "ROOT", self.old_root)

    def triage(self, stamp: str, company: str = "Acme") -> Path:
        p = self.gen / f"discovery_triage_{stamp}.csv"
        p.write_text(HEADER + f"keep,{company},SWE Intern,https://jobright.ai/jobs/info/{stamp},,\n", encoding="utf-8")
        return p

    def test_day_key_finds_the_legacy_file(self):
        legacy = self.triage("2026-08-23")
        self.assertEqual(gaq.latest_triage("2026-08-23"), legacy)

    def test_day_key_picks_the_newest_run_of_that_day(self):
        self.triage("2026-09-03")
        self.triage("2026-09-03T13")
        evening = self.triage("2026-09-03T22")
        self.triage("2026-09-04T13")
        self.assertEqual(gaq.latest_triage("2026-09-03"), evening)

    def test_run_stamp_is_an_exact_match(self):
        morning = self.triage("2026-09-03T13")
        self.triage("2026-09-03T22")
        self.assertEqual(gaq.latest_triage("2026-09-03T13"), morning)

    def test_no_day_means_newest_overall(self):
        self.triage("2026-09-02")
        self.triage("2026-09-03T22")
        newest = self.triage("2026-09-04")
        self.assertEqual(gaq.latest_triage(None), newest)

    def test_missing_day_returns_none(self):
        self.triage("2026-09-03T13")
        self.assertIsNone(gaq.latest_triage("2026-09-04"))

    def test_available_dates_lists_both_forms_newest_first(self):
        for stamp in ("2026-09-03", "2026-09-03T13", "2026-09-02", "2026-09-03T22"):
            self.triage(stamp)
        (self.gen / "discovery_triage_notes.csv").write_text(HEADER, encoding="utf-8")
        self.assertEqual(
            gaq.available_dates(),
            ["2026-09-03T22", "2026-09-03T13", "2026-09-03", "2026-09-02"],
        )

    def test_date_re_accepts_run_stamps_for_the_queue_api(self):
        self.assertTrue(gaq.DATE_RE.fullmatch("2026-09-03T13"))
        self.assertTrue(gaq.DATE_RE.fullmatch("2026-09-03"))
        self.assertIsNone(gaq.DATE_RE.fullmatch("2026-09-03T13:05"))
        self.assertIsNone(gaq.DATE_RE.fullmatch("../etc/passwd"))


if __name__ == "__main__":
    unittest.main()
