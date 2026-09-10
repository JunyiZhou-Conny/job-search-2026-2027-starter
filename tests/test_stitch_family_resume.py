#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from stitch_family_resume import (  # noqa: E402
    BEGIN,
    EDUCATION,
    HYPERREF_HIDELINKS,
    MASTER,
    SKILLS,
    assemble,
    require_sentinel,
    with_hidelinks,
)


class TestStitchSentinels(unittest.TestCase):
    def test_real_master_has_ordered_sentinels(self) -> None:
        master = MASTER.read_text()
        begin = require_sentinel(master, BEGIN)
        education = require_sentinel(master, EDUCATION)
        skills = require_sentinel(master, SKILLS)
        self.assertLess(begin, education)
        self.assertLess(education, skills)

    def test_assemble_keeps_master_identity_and_fragment_body(self) -> None:
        fragment = "% Technical Skills\n\\section{Technical Skills}\nFRAGMENT_BODY\n\\end{document}\n"
        tex = assemble(MASTER.read_text(), fragment)
        self.assertIn("Junyi (Conny) Zhou", tex)
        self.assertIn("FRAGMENT_BODY", tex)
        self.assertIn("% Education", tex)
        self.assertEqual(tex.count("\\begin{document}"), 1)
        self.assertTrue(tex.rstrip().endswith("\\end{document}"))
        self.assertIn(HYPERREF_HIDELINKS, tex)

    def test_with_hidelinks_fails_when_hyperref_is_missing(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with_hidelinks("no hyperref here")
        self.assertIn("hyperref", str(ctx.exception))

    def test_missing_education_sentinel_exits(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            assemble("\\begin{document}\n% Technical Skills\n", "% fragment\n")
        self.assertIn("% Education", str(ctx.exception))

    def test_missing_skills_sentinel_exits(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            assemble("\\begin{document}\n% Education\n", "% fragment\n")
        self.assertIn("% Technical Skills", str(ctx.exception))

    def test_out_of_order_sentinels_exit(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            assemble("% Technical Skills\n\\begin{document}\n% Education\n", "x")
        self.assertIn("out of order", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
