#!/usr/bin/env python3

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from ingest_discovery_triage import cluster_resume_version  # noqa: E402
from queue_writeback import default_resume_for_cluster  # noqa: E402
from test_polar_runtime import compile_text  # noqa: E402

GONE_DIRS = ("cloud_swe", "data_ml", "health_ai", "clusters")
GHOST_VERSIONS = (
    "2026-08-24_cloud-swe_v1.3",
    "2026-08-24_data-ml_v1.3",
    "2026-08-24_health-ai_v1.3",
)


def active_base_from_registry() -> str:
    rows = []
    with (ROOT / "data" / "resume_versions.csv").open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            cluster = (row.get("cluster") or "").strip()
            active = (row.get("active") or "").strip().lower()
            if cluster == "base" and active in {"true", "1", "yes"}:
                rows.append(row)
    if len(rows) != 1:
        raise AssertionError(f"expected one active cluster=base row, got {len(rows)}")
    version = (rows[0].get("resume_version") or "").strip()
    if not version:
        raise AssertionError("active base row has an empty resume_version")
    return version


class TestResumeFolder(unittest.TestCase):
    def test_cluster_directories_are_gone(self):
        for name in GONE_DIRS:
            path = ROOT / "resumes" / name
            self.assertFalse(path.exists(), path)

    def test_active_base_files_exist(self):
        self.assertTrue((ROOT / "resumes" / "base" / "JZ_resume.tex").is_file())
        self.assertTrue((ROOT / "resumes" / "base" / "JZ_resume.pdf").is_file())

    def test_build_clusters_is_gone(self):
        self.assertFalse((ROOT / "scripts" / "build_clusters.py").exists())

    def test_default_resume_matches_active_base_registry(self):
        expected = active_base_from_registry()
        self.assertEqual(default_resume_for_cluster("cloud_swe"), expected)
        self.assertEqual(default_resume_for_cluster("data_ml"), expected)
        self.assertEqual(default_resume_for_cluster(""), expected)

    def test_ingest_cluster_resume_is_active_base(self):
        expected = active_base_from_registry()
        for cluster in ("cloud_swe", "data_ml", "health_ai"):
            version = cluster_resume_version(cluster)
            self.assertEqual(version, expected, cluster)
            self.assertFalse(version.startswith("2026-07-20_"), version)

    def test_polar_runtime_names_base_not_cluster_files(self):
        text = compile_text()
        self.assertIn("## E. Resume-cluster selection", text)
        self.assertIn("JZ_resume", text)
        self.assertIn("Prefer the Simplify resume", text)
        self.assertIn("missing_production_resume", text)
        self.assertNotIn("If the widget is empty, upload `resumes/base/JZ_resume.pdf` only.", text)
        self.assertNotIn("Pick one existing cluster resume", text)
        for ghost in GHOST_VERSIONS:
            self.assertNotIn(ghost, text)


if __name__ == "__main__":
    unittest.main()
