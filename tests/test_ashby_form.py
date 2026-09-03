#!/usr/bin/env python3
"""The Ashby form summary must name the G2 blockers the rollout policy cares about."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ashby_form import parse_url, summarize  # noqa: E402


def _form(fields):
    return {"url": "u", "org": "o", "open": True, "title": "t", "location": None, "workplace": None,
            "employment": None, "published": None, "fields": fields}


def f(title, type_="String", required=True, options=None):
    return {"title": title, "type": type_, "required": required, "options": options or []}


class TestAshbyForm(unittest.TestCase):
    def test_parse_url(self):
        self.assertEqual(parse_url("https://jobs.ashbyhq.com/clera/3dc0a0f6-6a53-4a8c-bc70-b007113c348a/application"),
                         {"org": "clera", "id": "3dc0a0f6-6a53-4a8c-bc70-b007113c348a"})
        self.assertIsNone(parse_url("https://boards.greenhouse.io/x/jobs/1"))

    def test_minimal_form_has_no_blockers(self):
        form = summarize(_form([f("Name"), f("Email", "Email"), f("Resume", "File"), f("LinkedIn", "Url"),
                                f("Do you have work authorization to work in that country?", "Boolean")]))
        self.assertEqual(form["g2_blockers"], [])

    def test_broad_sponsorship_blocks_but_h1b_named_does_not(self):
        broad = summarize(_form([f("Do you now, or will you in the future, need US visa sponsorship?", "Boolean")]))
        self.assertIn("broad_sponsorship_question", broad["g2_blockers"])
        # Live Ashby/Greenhouse copy lists H-1B as an example inside the broad ask.
        example = summarize(_form([
            f("Will you now or in the future require sponsorship for employment visa status (e.g., H-1B visa status)?", "Boolean"),
        ]))
        self.assertIn("broad_sponsorship_question", example["g2_blockers"])
        named = summarize(_form([f("Will you require H-1B sponsorship?", "Boolean")]))
        self.assertNotIn("broad_sponsorship_question", named["g2_blockers"])
        self.assertEqual(len(named["summary"]["sponsorship_questions"]), 1)

    def test_essay_export_and_artifact_block(self):
        form = summarize(_form([
            f("Why are you a fit for this role?", "LongText"),
            f("The person hired will have access to ITAR controlled items", "ValueSelect", options=["A United States citizen"]),
            f("Project URL", "Url"),
            f("Optional essay", "LongText", required=False),
        ]))
        self.assertEqual(sorted(form["g2_blockers"]), ["export_control_question", "external_artifact", "required_essay"])
        self.assertEqual(form["summary"]["required_essays"], ["Why are you a fit for this role?"])


if __name__ == "__main__":
    unittest.main()
