#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "polar"))

import check_dossier as dossier  # noqa: E402


class TestPolarDossier(unittest.TestCase):
    def test_check_dossier_passes(self):
        script = ROOT / "polar" / "check_dossier.py"
        result = subprocess.run(
            ["python3", str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_parse_claims_reads_required_fields(self):
        text = (
            "### C099. Example\n"
            "- claim: A measured count.\n"
            "- evidence_type: directly_measured\n"
            "- sources:\n"
            "  - docs/automation/POLAR.md\n"
            "- date: 2026-09-04\n"
            "- confidence: high\n"
            "- does_not_prove: A general Polar capability.\n"
        )
        claims = dossier.parse_claims(text)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["id"], "C099")
        self.assertEqual(claims[0]["sources"], ["docs/automation/POLAR.md"])
        self.assertEqual(claims[0]["evidence_type"], "directly_measured")


if __name__ == "__main__":
    unittest.main()
