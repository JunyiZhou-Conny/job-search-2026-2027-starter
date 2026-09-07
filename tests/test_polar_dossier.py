#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "polar"))

import check_dossier as dossier  # noqa: E402


def _claim_block(cid: str, source: str = "polar/README.md", evidence_type: str = "directly_measured") -> str:
    return (
        f"### {cid}. Example\n"
        "- claim: A measured count.\n"
        f"- evidence_type: {evidence_type}\n"
        "- sources:\n"
        f"  - {source}\n"
        "- date: 2026-09-04\n"
        "- confidence: high\n"
        "- does_not_prove: A general Polar capability.\n"
    )


def _stub_tree(root: Path) -> None:
    polar = root / "polar"
    polar.mkdir()
    (root / "README.md").write_text("pointer polar/README.md\n")
    for name in dossier.REQUIRED_FILES:
        text = "ok\n"
        if name == "EMAIL_DRAFT.md":
            text = "Do not send\nhiring@polarbrowser.com\n"
        elif name == "EVIDENCE.md":
            text = "\n".join(_claim_block(f"C{i:03d}") for i in range(1, 9))
        (polar / name).write_text(text)


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

    def test_check_matches_check_paths_on_repo(self):
        self.assertEqual(dossier.check(), dossier.check_paths(ROOT))

    def test_parse_claims_reads_required_fields(self):
        text = _claim_block("C099", source="docs/automation/POLAR.md")
        claims = dossier.parse_claims(text)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["id"], "C099")
        self.assertEqual(claims[0]["sources"], ["docs/automation/POLAR.md"])
        self.assertEqual(claims[0]["evidence_type"], "directly_measured")

    def test_executor_self_report_is_a_valid_type(self):
        self.assertIn("executor_self_report", dossier.EVIDENCE_TYPES)

    def test_rejects_unknown_evidence_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "polar" / "EVIDENCE.md").write_text(
                "\n".join(
                    [
                        _claim_block("C001", evidence_type="vibes"),
                        *(_claim_block(f"C{i:03d}") for i in range(2, 9)),
                    ]
                )
            )
            errors = dossier.check_paths(root)
            self.assertTrue(any("bad evidence_type" in e for e in errors), errors)

    def test_rejects_missing_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "polar" / "EVIDENCE.md").write_text(
                "\n".join(
                    [
                        _claim_block("C001", source="no/such/file.md"),
                        *(_claim_block(f"C{i:03d}") for i in range(2, 9)),
                    ]
                )
            )
            errors = dossier.check_paths(root)
            self.assertTrue(any("missing source no/such/file.md" in e for e in errors), errors)

    def test_rejects_banned_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "polar" / "README.md").write_text("the clicker starts clean\n")
            errors = dossier.check_paths(root)
            self.assertTrue(any("banned phrase: starts clean" in e for e in errors), errors)

    def test_rejects_phone_in_polar_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "polar" / "JOURNEY.md").write_text("call +1 404-555-0100 later\n")
            errors = dossier.check_paths(root)
            self.assertTrue(any("phone number" in e for e in errors), errors)

    def test_rejects_untracked_source_in_git_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "loose.md").write_text("not committed\n")
            (root / "polar" / "EVIDENCE.md").write_text(
                "\n".join(
                    [
                        _claim_block("C001", source="loose.md"),
                        *(_claim_block(f"C{i:03d}") for i in range(2, 9)),
                    ]
                )
            )
            subprocess.run(
                ["git", "init"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "add", "README.md", "polar"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            errors = dossier.check_paths(root)
            self.assertTrue(any("untracked source loose.md" in e for e in errors), errors)

    def test_http_sources_are_not_fetched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _stub_tree(root)
            (root / "polar" / "EVIDENCE.md").write_text(
                "\n".join(
                    [
                        _claim_block("C001", source="https://polarbrowser.com/blog/frontier-problems"),
                        *(_claim_block(f"C{i:03d}") for i in range(2, 9)),
                    ]
                )
            )
            errors = dossier.check_paths(root)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
