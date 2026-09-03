#!/usr/bin/env python3
"""normalize_careers_boards.py keeps knowledge/careers_boards.yaml in one order."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

import normalize_careers_boards as ncb  # noqa: E402
from resolve_apply_url import _parse_simple_yaml  # noqa: E402

REAL = ROOT / "knowledge" / "careers_boards.yaml"

MESSY = """\
# Known boards.
#
# - Only add boards you have verified.

# Greenhouse board token
greenhouse:
  Zeta: zeta
  "Together AI": togetherai
  alpha: alpha-old
  Gemini: gemini
  # Google DeepMind product branding sometimes appears as Gemini on boards
  alpha: alpha  # verified 2026-08-23

# Ashby board slug
ashby:
  Traba: traba

  # added after a blank line
  Baseten: baseten

lever: {}

# Workday CXS
workday:
  Nvidia:
    host: nvidia.wd5
    tenant: nvidia
    site: NVIDIAExternalCareerSite
  NVIDIA:  # verified
    host: nvidia.wd5
    tenant: nvidia
    site: NVIDIAExternalCareerSite
  Waystar:
    site: Waystar
    host: waystar.wd1
    tenant: waystar
"""


class TestCanonicalForm(unittest.TestCase):
    def test_running_twice_yields_identical_bytes(self):
        once = ncb.canonical(MESSY)
        self.assertEqual(ncb.canonical(once), once)

    def test_committed_file_is_canonical(self):
        text = REAL.read_text(encoding="utf-8")
        self.assertEqual(ncb.canonical(text), text)

    def test_sorts_companies_case_insensitively(self):
        out = ncb.canonical(MESSY)
        self.assertEqual(list(yaml.safe_load(out)["greenhouse"]), ["alpha", "Gemini", "Together AI", "Zeta"])

    def test_case_variants_with_one_board_collapse_to_first_spelling(self):
        out = yaml.safe_load(ncb.canonical(MESSY))
        self.assertEqual(list(out["workday"]), ["Nvidia", "Waystar"])
        self.assertEqual(out["workday"]["Nvidia"]["site"], "NVIDIAExternalCareerSite")

    def test_case_variants_with_different_boards_both_stay(self):
        text = "greenhouse:\n  Acme: acme\n  ACME: acme-labs\n"
        out = yaml.safe_load(ncb.canonical(text))
        self.assertEqual(out["greenhouse"], {"Acme": "acme", "ACME": "acme-labs"})

    def test_repeated_key_keeps_last_value_like_pyyaml(self):
        out = yaml.safe_load(ncb.canonical(MESSY))
        self.assertEqual(out["greenhouse"]["alpha"], yaml.safe_load(MESSY)["greenhouse"]["alpha"])
        self.assertEqual(out["greenhouse"]["alpha"], "alpha")

    def test_no_entry_is_dropped(self):
        before = yaml.safe_load(MESSY)
        after = yaml.safe_load(ncb.canonical(MESSY))
        for section, entries in before.items():
            for company, board in (entries or {}).items():
                match = {k.casefold(): v for k, v in after[section].items()}
                self.assertEqual(match[company.casefold()], board, (section, company))

    def test_comments_survive_in_place(self):
        out = ncb.canonical(MESSY)
        self.assertTrue(out.startswith("# Known boards.\n#\n# - Only add boards you have verified.\n\n# Greenhouse board token\ngreenhouse:\n"))
        self.assertIn("\n# Ashby board slug\nashby:\n", out)
        self.assertIn("  Gemini: gemini\n  # Google DeepMind product branding sometimes appears as Gemini on boards\n", out)
        self.assertIn("  alpha: alpha  # verified 2026-08-23\n", out)
        self.assertIn("  # added after a blank line\n  Baseten: baseten\n", out)
        self.assertIn("  Nvidia:  # verified\n", out)

    def test_workday_keys_keep_host_tenant_site_order(self):
        out = ncb.canonical(MESSY)
        self.assertIn("  Waystar:\n    host: waystar.wd1\n    tenant: waystar\n    site: Waystar\n", out)

    def test_resolver_fallback_parser_reads_the_same_boards(self):
        out = ncb.canonical(MESSY)
        loaded = {k: v for k, v in yaml.safe_load(out).items() if v}
        self.assertEqual(_parse_simple_yaml(out), loaded)

    def test_quotes_keys_and_values_yaml_would_mistype(self):
        text = 'greenhouse:\n  "Caterpillar Inc.": cat\n  Yes: yes\n  "3M": 3m\n'
        out = ncb.canonical(text)
        self.assertIn('  "3M": "3m"\n', out)
        self.assertIn('  "Caterpillar Inc.": cat\n', out)
        self.assertIn('  "Yes": "yes"\n', out)
        self.assertEqual(yaml.safe_load(out)["greenhouse"], {"Caterpillar Inc.": "cat", "Yes": "yes", "3M": "3m"})


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "careers_boards.yaml"
        self.path.write_text(MESSY, encoding="utf-8")

    def test_check_reports_without_writing(self):
        self.assertEqual(ncb.main(["--check", "--path", str(self.path)]), 1)
        self.assertEqual(self.path.read_text(encoding="utf-8"), MESSY)

    def test_rewrite_then_check_passes(self):
        self.assertEqual(ncb.main(["--path", str(self.path)]), 0)
        self.assertEqual(ncb.main(["--check", "--path", str(self.path)]), 0)
        self.assertEqual(self.path.read_text(encoding="utf-8"), ncb.canonical(MESSY))


if __name__ == "__main__":
    unittest.main()
