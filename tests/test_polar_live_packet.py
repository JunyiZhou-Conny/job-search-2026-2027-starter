#!/usr/bin/env python3
"""LIVE.md stays a bounded Polar packet."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "generated" / "polar" / "LIVE.md"


class TestPolarLivePacket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = LIVE.read_text(encoding="utf-8")

    def test_names_the_rakuten_keep(self):
        self.assertIn("Rakuten Rewards", self.text)
        self.assertIn("Platform Engineer", self.text)
        self.assertIn(
            "https://jobright.ai/jobs/info/6a99ffb990a313642c653fe3",
            self.text,
        )
        self.assertIn("apply_url: none", self.text)

    def test_uses_original_job_post_only(self):
        self.assertIn("Original Job Post", self.text)
        self.assertIn("Do not click APPLY WITH AUTOFILL", self.text)
        self.assertNotIn("APPLY WITH AUTOFILL as the path", self.text.lower())

    def test_stops_before_submit(self):
        self.assertIn("Stop immediately before Submit", self.text)
        self.assertIn("submitted: yes/no", self.text)
        self.assertNotRegex(self.text, r"(?m)^.*[Cc]lick Submit exactly")

    def test_omits_phone_email_and_board_urls(self):
        self.assertIsNone(re.search(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", self.text))
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", self.text))
        self.assertNotIn("myworkdayjobs.com", self.text)
        self.assertNotIn("jobs.ashbyhq.com", self.text)
        self.assertNotIn("job-boards.greenhouse.io", self.text)

    def test_does_not_auto_map_work_authorization(self):
        self.assertIn("require work authorization", self.text)
        self.assertIn("do not treat that as the visa-sponsorship No", self.text)

    def test_forbids_yaml_homework(self):
        self.assertNotIn("form_strategy.yaml", self.text)
        self.assertNotIn("work_authorization.yaml", self.text)
        self.assertNotIn("SUBMIT_ROLLOUT.md", self.text)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
