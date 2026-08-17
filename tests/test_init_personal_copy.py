#!/usr/bin/env python3
"""Safety tests for collaborator personal-copy reset."""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import init_personal_copy as ipc  # noqa: E402


def _seed_mini_repo(dest: Path) -> None:
    shutil.copytree(ROOT / "docs" / "collaborators" / "templates", dest / "docs" / "collaborators" / "templates")
    (dest / "config").mkdir(parents=True)
    (dest / "knowledge").mkdir(parents=True)
    (dest / "data").mkdir(parents=True)
    (dest / "generated").mkdir(parents=True)
    (dest / "resumes" / "base").mkdir(parents=True)
    (dest / "docs" / "automation").mkdir(parents=True)
    (dest / "config" / "profile.yaml").write_text("legal_name: \"Junyi Zhou\"\n", encoding="utf-8")
    (dest / "knowledge" / "work_authorization.yaml").write_text("current_status: F-1\n", encoding="utf-8")
    (dest / "knowledge" / "evidence_bank.yaml").write_text("projects: {}\n", encoding="utf-8")
    (dest / "data" / "applications.csv").write_text("id,company\nJ1,Optiver\n", encoding="utf-8")
    (dest / "data" / "activity_log.csv").write_text("timestamp,note\nx,y\n", encoding="utf-8")
    (dest / "data" / "job_decisions.csv").write_text("url,company\n", encoding="utf-8")
    (dest / "data" / "contacts.csv").write_text("contact_id,name\n", encoding="utf-8")
    (dest / "data" / "networking.csv").write_text("contact_id,name\n", encoding="utf-8")
    (dest / "data" / "networking_interactions.csv").write_text("interaction_id\n", encoding="utf-8")
    (dest / "data" / "networking_experiments.csv").write_text("experiment_id\n", encoding="utf-8")
    (dest / "data" / "resume_versions.csv").write_text("resume_version,file_path\nJZ_resume,resumes/base/JZ_resume.tex\n", encoding="utf-8")
    (dest / "data" / "outreach_templates.csv").write_text("template_id,body\nT1,Harvard Health Data Science\n", encoding="utf-8")
    (dest / "resumes" / "base" / "JZ_resume.tex").write_text("% Junyi Zhou\n", encoding="utf-8")
    (dest / "knowledge" / "discovery_triage_rules.yaml").write_text("profile_anchors: {}\n", encoding="utf-8")
    (dest / "docs" / "automation" / "DAILY_JOB_DISCOVERY.md").write_text("Name: Junyi Zhou\n", encoding="utf-8")
    (dest / "docs" / "eligibility.md").write_text("example\n", encoding="utf-8")


class TestInitPersonalCopy(unittest.TestCase):
    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            code = ipc.main(["--root", str(dest)])
            self.assertEqual(code, 0)
            self.assertEqual((dest / "config" / "profile.yaml").read_text(encoding="utf-8"), 'legal_name: "Junyi Zhou"\n')
            with (dest / "data" / "applications.csv").open(encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[1][0], "J1")

    def test_refuses_write_without_fork_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            code = ipc.main(["--root", str(dest), "--write"])
            self.assertEqual(code, 2)
            self.assertIn("Junyi Zhou", (dest / "config" / "profile.yaml").read_text(encoding="utf-8"))

    def test_write_resets_identity_and_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            code = ipc.main(["--root", str(dest), "--i-am-on-a-personal-fork", "--write"])
            self.assertEqual(code, 0)
            profile = (dest / "config" / "profile.yaml").read_text(encoding="utf-8")
            self.assertIn("REPLACE_ME", profile)
            self.assertNotIn("Junyi Zhou", profile)
            with (dest / "data" / "applications.csv").open(encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(len(rows), 1)
            self.assertIn("id", rows[0])
            self.assertTrue((dest / "generated" / "collaborator_setup_status.md").exists())
            backups = list((dest / "data" / "backups").glob("personal-reset-*"))
            self.assertEqual(len(backups), 1)

    def test_refuses_upstream_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            subprocess.check_call(["git", "init"], cwd=dest, stdout=subprocess.DEVNULL)
            subprocess.check_call(
                ["git", "remote", "add", "origin", "https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter.git"],
                cwd=dest,
            )
            self.assertTrue(ipc.looks_like_upstream(dest))
            code = ipc.main(["--root", str(dest), "--i-am-on-a-personal-fork", "--write"])
            self.assertEqual(code, 2)
            self.assertIn("Junyi Zhou", (dest / "config" / "profile.yaml").read_text(encoding="utf-8"))

    def test_check_detects_template_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            code = ipc.main(["--root", str(dest), "--check"])
            self.assertEqual(code, 1)

    def test_check_detects_leftover_profile_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            (dest / "config" / "profile.yaml").write_text('legal_name: "Ada Lovelace"\n', encoding="utf-8")
            (dest / "resumes" / "base" / "JZ_resume.tex").write_text("% Ada Lovelace\n", encoding="utf-8")
            (dest / "docs" / "automation" / "DAILY_JOB_DISCOVERY.md").write_text("Name: Ada Lovelace\n", encoding="utf-8")
            (dest / "knowledge" / "discovery_triage_rules.yaml").write_text(
                "profile_anchors:\n  program_end_date: \"2026-12-18\"\n"
                "guide_rules:\n  - id: hard_gate\n",
                encoding="utf-8",
            )
            code = ipc.main(["--root", str(dest), "--check"])
            self.assertEqual(code, 1)

    def test_check_ignores_template_dates_in_guide_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            dest.mkdir()
            _seed_mini_repo(dest)
            (dest / "config" / "profile.yaml").write_text('legal_name: "Ada Lovelace"\n', encoding="utf-8")
            (dest / "resumes" / "base" / "JZ_resume.tex").write_text("% Ada Lovelace\n", encoding="utf-8")
            (dest / "docs" / "automation" / "DAILY_JOB_DISCOVERY.md").write_text("Name: Ada Lovelace\n", encoding="utf-8")
            (dest / "knowledge" / "discovery_triage_rules.yaml").write_text(
                "profile_anchors:\n  program_end_date: \"2028-05-15\"\n"
                "guide_rules:\n  - id: hard_gate\n    guidance: program end 2026-12-18\n",
                encoding="utf-8",
            )
            code = ipc.main(["--root", str(dest), "--check"])
            self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
