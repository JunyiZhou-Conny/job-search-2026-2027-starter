"""Parse the evidence bank and keep one record per source repo."""

from __future__ import annotations

import unittest
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "knowledge" / "evidence_bank.yaml"

REQUIRED_PROJECTS = (
    "cellot_wyss",
    "autoresearch_cellot",
    "mixhvg_py",
    "job_search_os",
)


class EvidenceBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = yaml.safe_load(BANK.read_text())
        cls.projects = cls.bank["projects"]

    def test_yaml_has_projects_and_skills(self) -> None:
        self.assertIn("projects", self.bank)
        self.assertIn("skills", self.bank)

    def test_required_projects_exist(self) -> None:
        for key in REQUIRED_PROJECTS:
            self.assertIn(key, self.projects)
            body = self.projects[key]
            self.assertTrue(body.get("title"))
            self.assertIn("do_not_claim", body)
            self.assertIs(body.get("resume_eligible"), True)

    def test_no_duplicate_source_urls(self) -> None:
        urls = [
            body.get("source_url")
            for body in self.projects.values()
            if isinstance(body, dict) and body.get("source_url")
        ]
        counts = Counter(urls)
        dupes = [url for url, n in counts.items() if n > 1]
        self.assertEqual(dupes, [], f"duplicate source_url values: {dupes}")

    def test_speciesot_not_split_into_three_resume_projects(self) -> None:
        titles = " ".join(
            (body.get("title") or "") for body in self.projects.values()
        ).lower()
        self.assertIn("speciesot", titles)
        standalone = [
            key
            for key, body in self.projects.items()
            if isinstance(body, dict)
            and key not in {"cellot_wyss", "autoresearch_cellot"}
            and (body.get("canonical_name") or body.get("title") or "").lower()
            in {"scgen", "cellot"}
        ]
        self.assertEqual(standalone, [])

    def test_autoresearch_forbids_llm_directed_history(self) -> None:
        banned = " ".join(self.projects["autoresearch_cellot"].get("do_not_claim") or [])
        self.assertIn("LLM", banned)

    def test_job_os_forbids_fully_autonomous(self) -> None:
        banned = " ".join(self.projects["job_search_os"].get("do_not_claim") or [])
        self.assertIn("autonomous", banned.lower())

    def test_master_resume_numbers_appear_in_bank(self) -> None:
        tex = (ROOT / "resumes" / "base" / "JZ_resume.tex").read_text()
        blob = yaml.dump(self.bank)
        for token in (
            "0.85",
            "0.67",
            "338",
            "79.3",
            "1.0000",
            "0.980",
            "220",
            "43 GB",
        ):
            self.assertIn(token, tex, f"resume missing {token}")
            self.assertIn(token, blob, f"evidence bank missing {token}")


if __name__ == "__main__":
    unittest.main()
