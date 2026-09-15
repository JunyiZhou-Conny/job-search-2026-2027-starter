#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import perfect_resume_accessible  # noqa: E402
from polar_resume_attach import (  # noqa: E402
    FAMILY_RESUME_EXPORT_PATH,
    POLAR_COMPILE_ALIAS_REPO_PATH,
    PRODUCTION_RESUME_REPO_PATH,
    PRODUCTION_RESUME_STORED_NAME,
    load_attach_policy,
    perfect_resume_file_available,
    repo_pdf,
    runtime_lines,
    stored_name,
    submit_check,
    visible_filename_is_forbidden,
    visible_filename_is_perfect,
    workflow_lines,
)


class TestPolarResumeAttach(unittest.TestCase):
    def test_stored_name_is_perfect_resume(self):
        self.assertEqual(stored_name(), PRODUCTION_RESUME_STORED_NAME)
        self.assertEqual(repo_pdf(), PRODUCTION_RESUME_REPO_PATH)
        self.assertEqual(
            PRODUCTION_RESUME_REPO_PATH,
            "resumes/Perfect Resume/JZ_Resume_2027.pdf",
        )
        self.assertTrue((ROOT / PRODUCTION_RESUME_REPO_PATH).is_file())
        self.assertTrue((ROOT / POLAR_COMPILE_ALIAS_REPO_PATH).is_file())
        self.assertEqual(
            (ROOT / PRODUCTION_RESUME_REPO_PATH).read_bytes(),
            (ROOT / POLAR_COMPILE_ALIAS_REPO_PATH).read_bytes(),
        )
        self.assertTrue(perfect_resume_file_available(ROOT))
        self.assertEqual(load_attach_policy().get("identified_mac_pdf"), "")

    def test_never_upload_family_export(self):
        policy = load_attach_policy()
        self.assertIn(FAMILY_RESUME_EXPORT_PATH, policy["never_upload"])
        self.assertTrue(visible_filename_is_forbidden(FAMILY_RESUME_EXPORT_PATH))
        self.assertTrue(visible_filename_is_forbidden("ai_infra_v1.pdf"))
        self.assertTrue(visible_filename_is_perfect("Perfect Resume"))
        self.assertTrue(visible_filename_is_perfect("JZ_Resume_2027.pdf"))
        self.assertTrue(visible_filename_is_perfect("perfect_resume.pdf"))
        self.assertFalse(visible_filename_is_perfect("JZ_Resume_911.pdf"))
        self.assertFalse(visible_filename_is_perfect("ai_infra_v1.pdf"))

    def test_runtime_forbids_family_fallback(self):
        joined = "\n".join(runtime_lines() + workflow_lines() + [submit_check()])
        self.assertIn(PRODUCTION_RESUME_STORED_NAME, joined)
        self.assertIn(POLAR_COMPILE_ALIAS_REPO_PATH, joined)
        self.assertIn("Do not silently fall back to `ai_infra_v1`.", joined)
        self.assertNotIn("attach that export", joined)

    def test_named_profile_counts_as_accessible(self):
        self.assertTrue(
            perfect_resume_accessible(polar_or_simplify_has_named_resume=True, root=ROOT)
        )
        self.assertTrue(
            perfect_resume_accessible(polar_or_simplify_has_named_resume=False, root=ROOT)
        )


if __name__ == "__main__":
    unittest.main()
