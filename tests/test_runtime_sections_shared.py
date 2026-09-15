#!/usr/bin/env python3
"""One source, two renders.

Locks two contracts. First, the Polar compile is byte-identical to the
committed files after the shared-builder extraction. Second, every line
tagged for both executors renders with the same bytes in POLAR_RUNTIME.md
and GROKBOT_RUNTIME.md, including every candidate fact and standing
answer.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_grokbot_runtime as grok_build  # noqa: E402
import build_polar_runtime as polar_build  # noqa: E402
from grokbot_policy import grok_run_caps  # noqa: E402
from polar_policy import apply_run_caps  # noqa: E402
from polar_workflows import WORKFLOW_RENDERERS, render_manifest, render_workflow, write_schema_csvs  # noqa: E402
from runtime_sections import (  # noqa: E402
    ALL_EXECUTORS,
    GROK,
    POLAR,
    Line,
    candidate_fact_bullets,
    load_sources,
    load_yaml,
    polar_only,
    render_lines,
    shared,
    shared_line_inventory,
    standing_answer_lines,
    variant,
)

POLAR_DIR = ROOT / "generated" / "polar"
GROK_RUNTIME = ROOT / "generated" / "grokbot" / "runtime" / "GROKBOT_RUNTIME.md"


def polar_runtime_text() -> str:
    return polar_build.render(polar_build.compile_sections())


def grok_runtime_text() -> str:
    return grok_build.compile_all()["runtime/GROKBOT_RUNTIME.md"]


class TestPolarCompileIsByteIdentical(unittest.TestCase):
    def test_runtime_matches_committed_file(self):
        self.assertEqual(
            (POLAR_DIR / "runtime" / "POLAR_RUNTIME.md").read_text(encoding="utf-8"),
            polar_runtime_text(),
        )

    def test_every_workflow_and_manifest_match_committed_files(self):
        operator = load_yaml(ROOT / "knowledge" / "polar_operator.yaml")
        versions = {}
        for name in WORKFLOW_RENDERERS:
            text = render_workflow(name, operator)
            committed = (POLAR_DIR / "workflows" / f"{name}.md").read_text(encoding="utf-8")
            self.assertEqual(committed, text, name)
            for line in text.splitlines():
                if line.startswith("workflow_version:"):
                    versions[name] = line.split(":", 1)[1].strip()
                    break
        manifest = (POLAR_DIR / "workflows" / "WORKFLOW_MANIFEST.md").read_text(encoding="utf-8")
        self.assertEqual(manifest, render_manifest(operator, versions))

    def test_schema_csvs_match_committed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for path in write_schema_csvs(root):
                committed = (POLAR_DIR / path.name).read_text(encoding="utf-8")
                self.assertEqual(committed, path.read_text(encoding="utf-8"), path.name)

    def test_full_cli_compile_leaves_git_tree_clean_for_polar(self):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_polar_runtime.py")],
            check=True,
            cwd=ROOT,
            capture_output=True,
        )
        diff = subprocess.run(
            ["git", "status", "--porcelain", "--", "generated/polar"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(diff.stdout.strip(), "", diff.stdout)

    def test_policy_revision_matches_the_committed_compile(self):
        operator = load_yaml(ROOT / "knowledge" / "polar_operator.yaml")
        revision = str(operator["policy_revision"])
        self.assertTrue(revision.startswith("2026-"), revision)
        apply = (POLAR_DIR / "workflows" / "apply-ready-jobs.md").read_text(encoding="utf-8")
        self.assertIn(f"workflow_version: {revision}+", apply)


class TestLineTagging(unittest.TestCase):
    def test_variant_yields_exactly_one_line_per_executor(self):
        rows = [shared("both"), *variant(polar="p", grok="g"), polar_only("only p"), ""]
        self.assertEqual(render_lines(rows, POLAR), ["both", "p", "only p", ""])
        self.assertEqual(render_lines(rows, GROK), ["both", "g", ""])

    def test_unknown_executor_is_rejected(self):
        with self.assertRaises(ValueError):
            render_lines([shared("x")], "cloud")

    def test_default_tag_is_both_executors(self):
        self.assertEqual(Line("x").executors, ALL_EXECUTORS)


class TestSharedLinesRenderIdentically(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.polar = polar_runtime_text()
        cls.grok = grok_runtime_text()
        cls.src = load_sources(ROOT)

    def test_every_shared_line_is_in_both_runtimes(self):
        polar_lines = set(self.polar.splitlines())
        grok_lines = set(self.grok.splitlines())
        inventory = shared_line_inventory(self.src, grok_run_caps(ROOT))
        self.assertGreater(len(inventory), 120)
        for line in inventory:
            for piece in line.splitlines():
                self.assertIn(piece, polar_lines, piece)
                self.assertIn(piece, grok_lines, piece)

    def test_fact_and_standing_lines_are_byte_identical(self):
        facts = [f"- {item}" for item in candidate_fact_bullets(self.src)]
        standing = [f"- {item}" for item in standing_answer_lines(self.src)]
        self.assertGreaterEqual(len(facts), 30)
        self.assertGreaterEqual(len(standing), 5)
        for line in facts + standing:
            self.assertIn(line, self.polar, line)
            self.assertIn(line, self.grok, line)
        self.assertIn("- Citizenship country (form and fact): China", self.grok)
        self.assertIn("- Graduation date widget: 2026-12-18", self.grok)
        # The future-sponsorship answer is owner policy in work_authorization.yaml.
        # Both renders carry the same compiled value; neither pins its own.
        auth = load_yaml(ROOT / "knowledge" / "work_authorization.yaml")
        answer = ((auth.get("form_strategy") or {}).get("visa_sponsorship") or {}).get("form_answer")
        self.assertIn(answer, ("Yes", "No"))
        sponsorship_line = next(
            line for line in self.polar.splitlines()
            if line.startswith("- Required future-sponsorship widget: ")
        )
        self.assertTrue(sponsorship_line.startswith(f"- Required future-sponsorship widget: {answer}."))
        self.assertIn(sponsorship_line, self.grok)

    def test_caps_agree_across_planes(self):
        polar = apply_run_caps(ROOT)
        grok = grok_run_caps(ROOT)
        self.assertEqual(polar.max_considered, grok.max_considered)
        self.assertEqual(grok.reserved_priority_slots, 0)
        self.assertTrue(polar.prioritized_auto_submit)
        self.assertFalse(grok.prioritized_auto_submit)

    def test_polar_render_carries_no_grok_mechanics(self):
        for token in (
            "grok-apply-jobs",
            "grok_cloud",
            "G- run",
            "jobright.ai/agent",
            "Add All",
            "already_applied_on_ats",
            "Superseded pre_jobright text",
        ):
            self.assertNotIn(token, self.polar, token)

    def test_grok_render_carries_no_polar_only_mechanics(self):
        for token in (
            "/home/polar",
            "/Users/",
            "PREFERENCES",
            "polar_browser",
            "discover-jobs-hourly",
            "READY_* rows are inventory. Do not FIFO them",
            "If the Mac slept",
        ):
            self.assertNotIn(token, self.grok, token)

    def test_committed_grok_runtime_matches_compiler(self):
        self.assertTrue(GROK_RUNTIME.is_file(), str(GROK_RUNTIME))
        self.assertEqual(GROK_RUNTIME.read_text(encoding="utf-8"), self.grok)


if __name__ == "__main__":
    unittest.main()
