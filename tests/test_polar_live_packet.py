#!/usr/bin/env python3
"""LIVE.md stays a bounded Polar packet."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "generated" / "polar" / "LIVE.md"

JOBRIGHT = "https://jobright.ai/jobs/info/6a99ffb990a313642c653fe3"
ALLOWED_URLS = {
    JOBRIGHT,
    "https://www.linkedin.com/in/junyi-zhou-270208247",
    "https://github.com/JunyiZhou-Conny",
    "https://connyzhou.com",
}

# Dates, GPA, salary, and the LinkedIn slug use digits. A leaked phone is NANP-shaped.
PHONE = re.compile(r"(?:\+1[\s.-]*)?(?:\(?\d{3}\)?[\s.-]*)\d{3}[\s.-]*\d{4}")


class TestPolarLivePacket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = LIVE.read_text(encoding="utf-8")

    def test_names_the_rakuten_keep(self):
        self.assertIn("Company: Rakuten Rewards", self.text)
        self.assertIn("Platform Engineer", self.text)
        self.assertIn(JOBRIGHT, self.text)
        self.assertIn("apply_url: none", self.text)

    def test_uses_original_job_post_only(self):
        self.assertIn("Click Original Job Post only.", self.text)
        self.assertIn("Do not click APPLY WITH AUTOFILL.", self.text)

    def test_stops_before_submit(self):
        self.assertIn("Stop immediately before Submit.", self.text)
        self.assertIn("submitted: yes/no", self.text)
        self.assertNotRegex(self.text, r"(?m)^.*[Cc]lick Submit exactly")

    def test_omits_phone_email_and_board_urls(self):
        self.assertNotIn("@", self.text)
        self.assertNotIn("workdayjobs", self.text.lower())
        self.assertNotIn("jobs.ashbyhq.com", self.text)
        self.assertNotIn("job-boards.greenhouse.io", self.text)
        found = set(re.findall(r"https?://[^\s]+", self.text))
        self.assertTrue(found <= ALLOWED_URLS, found)
        self.assertIsNone(PHONE.search(self.text))

    def test_does_not_auto_map_work_authorization(self):
        self.assertIn("DO NOT AUTO-MAP", self.text)
        self.assertIn("require work authorization", self.text)
        self.assertIn("do not treat that as the visa-sponsorship No", self.text)

    def test_forbids_yaml_homework(self):
        self.assertNotIn("form_strategy.yaml", self.text)
        self.assertNotIn("work_authorization.yaml", self.text)
        self.assertNotIn("SUBMIT_ROLLOUT.md", self.text)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
