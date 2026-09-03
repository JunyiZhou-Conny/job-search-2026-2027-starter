#!/usr/bin/env python3
"""Minimal tests for schema helpers, labeling, and dedupe matching."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    company_role_key, map_hard_eligibility, map_sponsorship, normalize_url,
    sync_app_aliases, bump_highest,
)
from label_job import suggest_from_text  # noqa: E402


class TestJsLib(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(
            normalize_url("https://Example.com/jobs/1/?utm=1#x"),
            "https://example.com/jobs/1/?utm=1",
        )

    def test_map_eligibility_sponsorship(self):
        self.assertEqual(map_hard_eligibility("verified"), "eligible")
        self.assertEqual(map_hard_eligibility("unclear"), "uncertain")
        self.assertEqual(map_sponsorship("no"), "explicit_no")
        self.assertEqual(map_sponsorship("verified"), "supportive")

    def test_sync_aliases(self):
        row = sync_app_aliases({"id": "J1", "posting_url": "https://a.com", "status": "applied"})
        self.assertEqual(row["job_id"], "J1")
        self.assertEqual(row["job_url"], "https://a.com")
        self.assertEqual(row["application_status"], "applied")

    def test_bump_highest(self):
        self.assertEqual(bump_highest("applied", "oa"), "oa")
        self.assertEqual(bump_highest("technical_screen", "applied"), "technical_screen")
        self.assertEqual(bump_highest("oa", "rejected"), "oa")

    def test_company_role_key(self):
        self.assertEqual(company_role_key(" Optiver ", "Graduate SWE"), company_role_key("optiver", "graduate swe"))


class TestLabeling(unittest.TestCase):
    def test_no_sponsor_is_not_hard_ineligible(self):
        s = suggest_from_text(
            "We are unable to sponsor visas for this role. Software Engineer New Grad.",
            role="Software Engineer New Grad",
            company="Acme",
        )
        self.assertEqual(s["sponsorship_signal"]["value"], "explicit_no")
        self.assertNotEqual(s["hard_eligibility"]["value"], "ineligible")
        self.assertIn(s["pursuit_lane"]["value"], {"broad", "practice", "core"})

    def test_citizen_hard_ineligible(self):
        s = suggest_from_text("Must be a U.S. citizen.", role="SWE", company="GovCo")
        self.assertEqual(s["hard_eligibility"]["value"], "ineligible")


class TestCanonicalUrlAtsSteps(unittest.TestCase):
    def test_ashby_application_and_greenhouse_confirm_collapse_onto_the_posting(self):
        from js_lib import canonical_url
        self.assertEqual(
            canonical_url("https://jobs.ashbyhq.com/Runway/82789f66-9216-4ef3-bfeb-6cef4b416e63/application?embed=true"),
            canonical_url("https://jobs.ashbyhq.com/runway/82789f66-9216-4ef3-bfeb-6cef4b416e63"),
        )
        self.assertEqual(
            canonical_url("https://job-boards.greenhouse.io/advancedspace/jobs/4324875009/confirm"),
            canonical_url("https://job-boards.greenhouse.io/advancedspace/jobs/4324875009"),
        )
        self.assertEqual(canonical_url("https://x.com/application/foo"), "https://x.com/application/foo")


if __name__ == "__main__":
    unittest.main()
