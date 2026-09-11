#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_resume_attach import (  # noqa: E402
    ingest_pdf,
    load_attach_policy,
    runtime_lines,
    submit_check,
    workflow_lines,
)


class TestPolarResumeAttach(unittest.TestCase):
    def test_ingest_pdf_exists(self):
        path = ingest_pdf()
        self.assertEqual(path, "resumes/Perfect Resume/perfect_resume.pdf")
        self.assertTrue((ROOT / path).is_file(), path)

    def test_never_upload_master(self):
        policy = load_attach_policy()
        self.assertIn("resumes/base/JZ_resume.pdf", policy["never_upload"])

    def test_runtime_and_workflow_name_perfect_resume(self):
        joined = "\n".join(runtime_lines() + workflow_lines() + [submit_check()])
        self.assertIn("resumes/Perfect Resume/perfect_resume.pdf", joined)
        self.assertIn("Do not upload `resumes/base/JZ_resume.pdf`.", joined)
        self.assertNotIn("missing_production_resume", joined)
        self.assertNotIn(
            "mark REVIEW_READY with blocker missing_production_resume", joined
        )

    def test_readme_no_longer_blocks_empty_widget(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("resumes/Perfect Resume/perfect_resume.pdf", readme)
        self.assertNotIn("Mark REVIEW_READY.", readme)
        self.assertNotIn("routed family one-pager", readme)


if __name__ == "__main__":
    unittest.main()
