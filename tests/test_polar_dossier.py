#!/usr/bin/env python3
"""polar/check_dossier.py must pass on this branch."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
