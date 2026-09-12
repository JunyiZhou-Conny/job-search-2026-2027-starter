#!/usr/bin/env python3
"""Safety tests for Polar trusted-repo retarget on a personal fork."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import set_polar_trusted_repo as spr  # noqa: E402

POLICY_SRC = ROOT / "scripts" / "polar_policy.py"
UPSTREAM_ORIGIN = "https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter.git"
PERSONAL_REPO = "alice/job-search"


def _seed_policy(dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "scripts" / "polar_policy.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(POLICY_SRC, path)
    return path


class TestSetPolarTrustedRepo(unittest.TestCase):
    def test_dry_run_does_not_change_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            checkout_before = POLICY_SRC.read_text(encoding="utf-8")
            code = spr.main([PERSONAL_REPO, "--root", str(dest)])
            self.assertEqual(code, 0)
            self.assertEqual(path.read_text(encoding="utf-8"), before)
            self.assertEqual(POLICY_SRC.read_text(encoding="utf-8"), checkout_before)

    def test_write_updates_only_the_two_constants(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            checkout_before = POLICY_SRC.read_text(encoding="utf-8")
            code = spr.main([PERSONAL_REPO, "--write", "--root", str(dest)])
            self.assertEqual(code, 0)
            after = path.read_text(encoding="utf-8")
            expected = before.replace(
                'TRUSTED_REPO_OWNER = "JunyiZhou-Conny"',
                'TRUSTED_REPO_OWNER = "alice"',
                1,
            ).replace(
                'TRUSTED_REPO_NAME = "job-search-2026-2027-starter"',
                'TRUSTED_REPO_NAME = "job-search"',
                1,
            )
            self.assertEqual(after, expected)
            self.assertIn('TRUSTED_REPO_OWNER = "alice"', after)
            self.assertIn('TRUSTED_REPO_NAME = "job-search"', after)
            self.assertIn('TRUSTED_REPO = f"{TRUSTED_REPO_OWNER}/{TRUSTED_REPO_NAME}"', after)
            self.assertEqual(POLICY_SRC.read_text(encoding="utf-8"), checkout_before)

    def test_refuses_upstream_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            subprocess.check_call(["git", "init"], cwd=dest, stdout=subprocess.DEVNULL)
            subprocess.check_call(
                ["git", "remote", "add", "origin", UPSTREAM_ORIGIN],
                cwd=dest,
            )
            code = spr.main([PERSONAL_REPO, "--write", "--root", str(dest)])
            self.assertEqual(code, 2)
            self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_refuses_rewriting_to_upstream_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            code = spr.main(
                ["JunyiZhou-Conny/job-search-2026-2027-starter", "--write", "--root", str(dest)]
            )
            self.assertEqual(code, 2)
            self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_refuses_bad_repo_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            for raw in ("not-a-repo", "owner/repo/extra", "owner/", "/repo", "owner/repo name"):
                with self.subTest(raw=raw):
                    code = spr.main([raw, "--write", "--root", str(dest)])
                    self.assertEqual(code, 2)
                    self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_rebuild_without_write_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "repo"
            path = _seed_policy(dest)
            before = path.read_text(encoding="utf-8")
            code = spr.main([PERSONAL_REPO, "--rebuild", "--root", str(dest)])
            self.assertEqual(code, 2)
            self.assertEqual(path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
