#!/usr/bin/env python3
"""Invariants for the compiled Polar runtime artifact."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_polar_runtime import OUT_DEFAULT, main, render, compile_sections  # noqa: E402

REQUIRED_HEADINGS = [
    "## A. Candidate facts",
    "## B. Discovery sources",
    "## C. Triage rules",
    "## D. Regular vs prioritized policy",
    "## E. Resume-cluster selection",
    "## F. Writing evidence and writing rules",
    "## G. Blocker handling",
    "## H. Submission behavior",
    "## I. Prohibited fabrication",
    "## J. Runtime status semantics",
]

STATUSES = [
    "NEW",
    "READY_REGULAR",
    "READY_PRIORITY",
    "IN_PROGRESS",
    "REVIEW_READY",
    "SUBMITTED",
    "SUBMISSION_UNKNOWN",
    "BLOCKED",
    "SKIP",
]

SECRET_LINE = re.compile(
    r"(?i)(password\s*[:=]\s*\S+|cookie\s*[:=]\s*\S+|set-cookie\s*[:=]"
    r"|otp\s*[:=]\s*\d{4,8}|2fa\s*[:=]\s*\S+|storage_state)"
)


def compile_text() -> str:
    return render(compile_sections())


class TestPolarRuntime(unittest.TestCase):
    def test_banner_and_required_sections(self):
        text = compile_text()
        self.assertIn("COMPILED ARTIFACT. Not canonical.", text)
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text, heading)

    def test_no_secret_assignments(self):
        text = compile_text()
        self.assertIsNone(SECRET_LINE.search(text), SECRET_LINE.search(text))
        self.assertIn("No passwords, cookies, OTP codes", text)

    def test_identity_facts_agree(self):
        text = compile_text()
        self.assertIn("Junyi Zhou", text)
        self.assertIn("Citizenship country (form and fact): China", text)
        self.assertIn("Current visa type when asked: F-1", text)
        self.assertIn("Broad visa-sponsorship widget: No", text)
        self.assertIn("Future sponsorship required (standing fact): True", text)
        self.assertIn("Program end / I-20 date: 2026-12-18", text)
        self.assertIn("Year-only graduation widget: 2027", text)
        self.assertIn("Earliest full-time start: 2027-01-18", text)
        self.assertIn("Remote ok: False", text)
        self.assertNotIn("Citizenship country (form and fact): United States", text)
        self.assertNotIn("Broad visa-sponsorship widget: Yes", text)

    def test_phone_and_email_are_not_copied(self):
        text = compile_text()
        self.assertIn("Phone and email live in the local Polar profile", text)
        self.assertNotRegex(text, r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
        self.assertNotRegex(text, r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

    def test_statuses_and_caps(self):
        text = compile_text()
        for status in STATUSES:
            self.assertIn(status, text, status)
        self.assertIn("Regular jobs per apply-ready-jobs run: 3", text)
        self.assertIn("Regular submissions per local calendar day (America/New_York): 10", text)
        self.assertIn("Prioritized auto-submit: False", text)
        self.assertIn("writing_observation_mode: True", text)
        self.assertIn("SUBMISSION_UNKNOWN first", text)

    def test_committed_file_matches_compiler(self):
        generated = compile_text()
        self.assertTrue(OUT_DEFAULT.is_file(), str(OUT_DEFAULT))
        self.assertEqual(OUT_DEFAULT.read_text(encoding="utf-8"), generated)

    def test_compiler_is_idempotent(self):
        first = compile_text()
        second = compile_text()
        self.assertEqual(first, second)

    def test_cli_writes_the_same_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "POLAR_RUNTIME.md"
            self.assertEqual(main(["--out", str(out)]), 0)
            self.assertEqual(out.read_text(encoding="utf-8"), compile_text())

    def test_queue_schema_matches_operator(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        header = (ROOT / "generated" / "polar" / "queue_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(header.split(","), operator["queue_columns"])
        writing = (ROOT / "generated" / "polar" / "writing_log_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(writing.split(","), operator["writing_log_columns"])
        heartbeat = (ROOT / "generated" / "polar" / "heartbeat_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(heartbeat.split(","), operator["heartbeat_columns"])

    def test_workflow_prompts_are_paste_ready(self):
        text = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in (
            "discover-jobs-hourly",
            "apply-ready-jobs",
            "daily-job-summary",
            "polar-scheduler-heartbeat",
        ):
            self.assertIn(name, text)
        self.assertIn("Never click Jobright APPLY WITH AUTOFILL", text)
        self.assertIn("Never blindly resubmit", text)
        self.assertIn("REVIEW_READY", text)
        self.assertIn("example.com", text)

    def test_apply_ledger_still_loads_gates(self):
        from apply_ledger import load_gates

        gates = load_gates()
        self.assertIn("ashby", gates["gates"])
        self.assertEqual(gates["regular_submit_cap_per_run"], 3)
        self.assertEqual(gates["polar_local"]["regular_submit_cap_per_local_day"], 10)


if __name__ == "__main__":
    unittest.main()
