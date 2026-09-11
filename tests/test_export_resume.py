#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_resume import (  # noqa: E402
    MAILTO_PLACEHOLDER,
    application_email,
    apply_contact,
)
from stitch_family_resume import PRODUCTION_FAMILIES  # noqa: E402


class TestExportResume(unittest.TestCase):
    def test_source_family_tex_stays_sanitized(self) -> None:
        for name, spec in PRODUCTION_FAMILIES.items():
            with self.subTest(family=name):
                tex = spec.tex.read_text()
                self.assertIn(MAILTO_PLACEHOLDER, tex)
                self.assertNotIn("[GitHub]", tex)

    def test_apply_contact_replaces_placeholder(self) -> None:
        source = f"Email: {MAILTO_PLACEHOLDER}"
        out = apply_contact(source, "owner@example.com")
        self.assertEqual(out, r"Email: \href{mailto:owner@example.com}{owner@example.com}")
        self.assertNotIn("[REDACTED]", out)

    def test_apply_contact_requires_placeholder(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            apply_contact("Email: already-set", "owner@example.com")
        self.assertIn("placeholder", str(ctx.exception))

    def test_application_email_uses_resume_then_simplify(self) -> None:
        self.assertEqual(
            application_email({"RESUME_EMAIL": "a@example.com", "SIMPLIFY_EMAIL": "b@example.com"}),
            "a@example.com",
        )
        self.assertEqual(application_email({"SIMPLIFY_EMAIL": "b@example.com"}), "b@example.com")

    def test_application_email_ignores_harvard_and_redacted(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            application_email({"HARVARD_EMAIL": "school@example.edu", "SIMPLIFY_EMAIL": "[REDACTED]"})
        self.assertIn("application email missing", str(ctx.exception))
        self.assertIn("HARVARD_EMAIL", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
