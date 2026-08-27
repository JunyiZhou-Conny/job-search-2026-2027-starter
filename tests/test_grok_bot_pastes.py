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


class AutofillerPasteTests(unittest.TestCase):
    def setUp(self) -> None:
        blocks = paste_blocks(ORG / "BOT_DESCRIPTIONS.md")
        cooks = [b for b in blocks if "You are Junyi Zhou's Ashby Autofiller" in b]
        self.assertEqual(len(cooks), 1)
        self.paste = cooks[0]

    def test_pulls_working_branch_and_form_strategy(self) -> None:
        self.assertIn("cursor/grok-shared-computer-5db1", self.paste)
        self.assertIn("knowledge/form_strategy.yaml", self.paste)
        self.assertIn("work_authorization.yaml", self.paste)
        self.assertIn("this-job sheet", self.paste)
        self.assertIn("hand sees only the sheet", self.paste)

    def test_does_not_freeze_sponsorship_no(self) -> None:
        self.assertNotIn("sponsorship: No / None", self.paste)
        self.assertIn("H-1B-named sponsorship is No", self.paste)
        self.assertIn("no H-1B wording is Yes", self.paste)

    def test_reports_to_ceo_and_stops_without_copilot(self) -> None:
        self.assertIn("Report to the CEO", self.paste)
        self.assertIn("harness_not_ready", self.paste)
        self.assertIn("YOUR screen", self.paste)
        self.assertIn("do not submit", self.paste.lower())

    def test_checks_copilot_then_tries_store(self) -> None:
        self.assertIn("chrome://extensions", self.paste)
        self.assertIn("Simplify Copilot (Simplify Jobs Inc.)", self.paste)
        self.assertIn("Chrome Web Store", self.paste)
        self.assertIn("simplify.jobs", self.paste)
        self.assertIn("Do not ask Junyi to paste a password", self.paste)
        self.assertIn("Do not use Greenhouse Autofill my application", self.paste)


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
        self.assertIn("form_strategy.yaml", self.paste)
        self.assertIn("You do not start computer-use on the form", self.paste)

    def test_architect_is_outside(self) -> None:
        self.assertIn("Architect sits outside this company", self.paste)


class PasteIndexTests(unittest.TestCase):
    def test_readme_maps_architect_ceo_autofiller(self) -> None:
        text = (ORG / "README.md").read_text(encoding="utf-8")
        self.assertIn("Where Settings Descriptions live", text)
        self.assertIn("ARCHITECT.md", text)
        self.assertIn("BOT_DESCRIPTIONS.md", text)
        self.assertIn("CEO of Auto Application", text)
        self.assertIn("Ashby Autofiller", text)
        self.assertIn("form_strategy.yaml", text)


class HandoffPasteTests(unittest.TestCase):
    def test_live_paste_uses_ceo_and_conny(self) -> None:
        text = (ORG / "GROK_BOT_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("CEO of Auto Application", text)
        self.assertIn("People also call me Conny", text)
        self.assertIn("form_strategy.yaml", text)
        self.assertNotIn("Connie", text)
        self.assertNotIn("sponsorship No/None", text)


if __name__ == "__main__":
    unittest.main()
