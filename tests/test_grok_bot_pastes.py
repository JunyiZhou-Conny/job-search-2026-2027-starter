#!/usr/bin/env python3
"""Checks on Grok Bot Settings pastes. Does not spawn Bots."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORG = ROOT / "docs" / "grok-bot-management"


def paste_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"```text\n(.*?)END PASTE", text, flags=re.S)


class ArchitectPasteTests(unittest.TestCase):
    def setUp(self) -> None:
        blocks = paste_blocks(ORG / "ARCHITECT.md")
        self.assertEqual(len(blocks), 1)
        self.paste = blocks[0]

    def test_conny_not_connie(self) -> None:
        self.assertIn("Conny", self.paste)
        self.assertNotIn("Connie", self.paste)

    def test_outside_every_company(self) -> None:
        self.assertIn("outside every company", self.paste)
        self.assertIn("spawn", self.paste.lower())
        self.assertIn("Name", self.paste)
        self.assertIn("Label", self.paste)
        self.assertIn("Description", self.paste)
        self.assertIn("Notifications", self.paste)

    def test_not_an_apply_role(self) -> None:
        lowered = self.paste.lower()
        self.assertNotIn("ashby", lowered)
        self.assertNotIn("linkedin", lowered)
        self.assertNotIn("jobs.ashbyhq.com", lowered)
        self.assertNotIn("ceo of auto application", lowered)


class CeoPasteTests(unittest.TestCase):
    def setUp(self) -> None:
        blocks = paste_blocks(ORG / "BOT_DESCRIPTIONS.md")
        ceo = [b for b in blocks if "CEO of Auto Application" in b and "You run this company" in b]
        self.assertEqual(len(ceo), 1)
        self.paste = ceo[0]

    def test_conny_not_connie(self) -> None:
        self.assertIn("Conny", self.paste)
        self.assertNotIn("Connie", self.paste)

    def test_one_ashby_job_one_teammate(self) -> None:
        self.assertIn("ONE live Ashby job", self.paste)
        self.assertIn("ONE existing teammate", self.paste)
        self.assertIn("do not spawn bots", self.paste.lower())
        self.assertIn("do not Submit", self.paste)

    def test_architect_is_outside(self) -> None:
        self.assertIn("Architect sits outside this company", self.paste)


class HandoffPasteTests(unittest.TestCase):
    def test_live_paste_uses_ceo_and_conny(self) -> None:
        text = (ORG / "GROK_BOT_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("CEO of Auto Application", text)
        self.assertIn("People also call me Conny", text)
        self.assertNotIn("Connie", text)


if __name__ == "__main__":
    unittest.main()
