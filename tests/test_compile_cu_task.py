#!/usr/bin/env python3
"""Computer Use Task compiler rejects Twitch-style parent prompts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compile_cu_task as cu  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "computer_use"


class TestLintTwitchPrompts(unittest.TestCase):
    def test_g1_fill_is_an_execute_plus_audit(self):
        text = (FIXTURES / "twitch_g1_fill.txt").read_text(encoding="utf-8")
        hits = cu.lint_task(text)
        self.assertIn("execute_plus_audit", hits)
        self.assertIn("full_form_audit", hits)
        self.assertIn("report_every_field", hits)

    def test_correction_asks_to_verify_each_field(self):
        text = (FIXTURES / "twitch_correction.txt").read_text(encoding="utf-8")
        hits = cu.lint_task(text)
        self.assertIn("verify_each_mutation", hits)
        self.assertIn("report_every_field", hits)
        self.assertIn("report_untouched_fields", hits)

    def test_verify_pass_invites_a_scroll_loop(self):
        text = (FIXTURES / "twitch_verify.txt").read_text(encoding="utf-8")
        hits = cu.lint_task(text)
        self.assertIn("scroll_only_method", hits)


class TestCompileSheet(unittest.TestCase):
    def test_leftover_paste_compiles_without_verify_steps(self):
        sheet = cu._load_sheet(FIXTURES / "leftover_paste.yaml")
        text = cu.compile_sheet(sheet)
        self.assertIn("MODE EXECUTE", text)
        self.assertIn("paste once", text)
        self.assertNotIn("verify each", text.lower())
        self.assertEqual(cu.lint_task(text), [])

    def test_multi_field_execute_orders_mutations_and_bounds_retry(self):
        sheet = cu._load_sheet(FIXTURES / "execute_corrections.yaml")
        text = cu.compile_sheet(sheet)
        self.assertIn("Country of citizenship → China", text)
        self.assertIn("click the matching option", text)
        self.assertIn("One bounded retry", text)
        self.assertIn("Do not screenshot or read back after each field", text)
        self.assertIn("Do not write a field-by-field audit", text)
        self.assertEqual(cu.lint_task(text), [])

    def test_submit_without_permission_is_rejected(self):
        sheet = {
            "mode": "submit",
            "target": {"url": "https://jobs.ashbyhq.com/acme/x"},
            "submit_permitted": False,
        }
        self.assertIn("submit_without_permission", cu.lint_sheet(sheet))

    def test_bootstrap_autofill_compiles_without_mutations(self):
        sheet = cu._load_sheet(FIXTURES / "bootstrap_autofill.yaml")
        text = cu.compile_sheet(sheet)
        self.assertIn("Autofill once", text)
        self.assertIn("Expected account name: Junyi Zhou", text)
        self.assertNotIn("Mutations in page order", text)
        self.assertEqual(cu.lint_task(text), [])

    def test_autofill_plus_mutations_is_rejected(self):
        sheet = cu._load_sheet(FIXTURES / "bootstrap_autofill.yaml")
        sheet["mutations"] = [{"field": "Sponsorship", "value": "No"}]
        self.assertIn("autofill_plus_mutations", cu.lint_sheet(sheet))

    def test_verify_shot_cannot_cover_two_sections(self):
        sheet = {
            "mode": "verify",
            "target": {"url": "https://example.com"},
            "forbidden": ["submit"],
            "read": [
                {"field": "Discipline", "section": "education"},
                {"field": "Familiarity", "section": "consent"},
            ],
            "evidence": [{"name": "both.png", "covers": ["Discipline", "Familiarity"]}],
        }
        self.assertIn("evidence_spans_distant_sections", cu.lint_sheet(sheet))


if __name__ == "__main__":
    unittest.main()
