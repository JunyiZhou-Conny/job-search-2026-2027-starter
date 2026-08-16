#!/usr/bin/env python3
"""Tests for employer apply-URL resolution."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_apply_url import (  # noqa: E402
    ENRICH_FIELDS,
    confidence_for,
    from_workday,
    load_board_map,
    score_title,
    slugs_for,
)


class TestHelpers(unittest.TestCase):
    def test_confidence_bands(self):
        self.assertEqual(confidence_for(0.9), "exact")
        self.assertEqual(confidence_for(0.5), "strong")
        self.assertEqual(confidence_for(0.3), "weak")
        self.assertIsNone(confidence_for(0.1))

    def test_title_overlap_similar_roles(self):
        self.assertGreaterEqual(
            score_title("Software Engineer Intern", "Software Engineering Intern"),
            0.5,
        )

    def test_slugs(self):
        self.assertIn("apptronik", slugs_for("Apptronik Inc."))
        self.assertIn("togetherai", slugs_for("Together AI"))


class TestBoardMap(unittest.TestCase):
    def test_yaml_loads(self):
        boards = load_board_map()
        self.assertIn("greenhouse", boards)
        self.assertIn("workday", boards)
        self.assertEqual(boards["greenhouse"]["Apptronik"], "apptronik")
        nvidia = boards["workday"]["NVIDIA"]
        self.assertEqual(nvidia["host"], "nvidia.wd5")


class TestWorkdayLive(unittest.TestCase):
    """Hits the live NVIDIA CXS endpoint — skip-friendly if the network flakes."""

    def test_nvidia_returns_postings(self):
        posts = from_workday(
            "nvidia.wd5",
            "nvidia",
            "NVIDIAExternalCareerSite",
            search_text="Software Engineering Intern",
        )
        if not posts:
            self.skipTest("Workday CXS returned no postings (network or rate limit)")
        self.assertTrue(any("intern" in t.lower() for t, _, _ in posts))
        self.assertTrue(posts[0][1].startswith("https://nvidia.wd5.myworkdayjobs.com/"))


class TestEnrichContract(unittest.TestCase):
    def test_enrich_fields_stable(self):
        self.assertEqual(
            ENRICH_FIELDS,
            [
                "apply_url",
                "apply_url_confidence",
                "apply_ats",
                "apply_matched_title",
                "apply_resolve_evidence",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
