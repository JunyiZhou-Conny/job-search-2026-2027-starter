#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    APPLY_URL_CONFIDENCE,
    GITHUB_RAW_BASE,
    QUEUE_COLUMNS,
    REQUIRED_QUEUE_READBACK,
    bootstrap_prompt,
    lease_ttl_minutes,
    parse_contract_block,
    raw_workflow_url,
    sanitize_learning_text,
)
from polar_workflows import WORKFLOW_RENDERERS  # noqa: E402

WORKFLOW_DIR = ROOT / "generated" / "polar" / "workflows"
SECRET_LINE = re.compile(
    r"(?i)(password\s*[:=]\s*\S+|cookie\s*[:=]\s*\S+|set-cookie\s*[:=]"
    r"|otp\s*[:=]\s*\d{4,8}|2fa\s*[:=]\s*\S+|storage_state)"
)
STREET_VALUE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9.#']+\s+"
    r"(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b",
    re.I,
)
PRODUCTION = (
    "discover-jobs-hourly",
    "apply-ready-jobs",
    "daily-job-summary",
    "production-learning-daily",
)


def read_workflow(name: str) -> str:
    return (WORKFLOW_DIR / f"{name}.md").read_text(encoding="utf-8")


class TestGeneratedWorkflows(unittest.TestCase):
    def test_required_workflow_files_exist(self):
        for name in WORKFLOW_RENDERERS:
            path = WORKFLOW_DIR / f"{name}.md"
            self.assertTrue(path.is_file(), str(path))
        self.assertTrue((WORKFLOW_DIR / "WORKFLOW_MANIFEST.md").is_file())

    def test_production_workflows_have_required_contracts(self):
        for name in PRODUCTION:
            text = read_workflow(name)
            self.assertIn("workflow_version:", text)
            self.assertIn(f"workflow: {name}", text)
            sheet = parse_contract_block(text, "Sheet write contract")
            self.assertEqual(sheet.get("mode"), "named_header_mapping")
            self.assertEqual(
                sheet.get("required_readback"),
                ", ".join(REQUIRED_QUEUE_READBACK),
            )
            self.assertEqual(sheet.get("never_omit"), APPLY_URL_CONFIDENCE)
            lease = parse_contract_block(text, "Browser lease")
            if name in ("discover-jobs-hourly", "apply-ready-jobs"):
                self.assertEqual(lease.get("needs_browser_lock"), "true")
                self.assertEqual(lease.get("ttl_minutes"), str(lease_ttl_minutes(ROOT)))
                self.assertIn("SKIPPED_LOCKED", text)
            else:
                self.assertEqual(lease.get("needs_browser_lock"), "false")

    def test_apply_priority_and_simplify_contracts(self):
        text = read_workflow("apply-ready-jobs")
        priority = parse_contract_block(text, "Priority contract")
        self.assertEqual(priority.get("reserved_priority_slots"), "1")
        self.assertEqual(priority.get("max_new_jobs"), "3")
        self.assertEqual(priority.get("shared_pool"), "true")
        self.assertEqual(priority.get("reservation_is_from_pool"), "true")
        self.assertEqual(priority.get("prioritized_auto_submit"), "true")
        self.assertEqual(
            priority.get("writing_log_required_before_priority_submit"),
            "true",
        )
        self.assertEqual(
            priority.get("priority_submit_gate"),
            "polar_policy.priority_submit_permitted",
        )
        simplify = parse_contract_block(text, "Simplify contract")
        self.assertEqual(simplify.get("max_attempts_per_application"), "1")
        self.assertEqual(simplify.get("fallback"), "polar_runtime_plus_local_profile")
        self.assertIn("## Employer requisition dedupe", text)
        self.assertIn("## Apply-time hard eligibility", text)
        self.assertIn("Sponsorship unknown or no is not a skip.", text)
        self.assertIn("degree_level_hard_skip", text)
        self.assertIn("degree_level_gate_missed_at_discovery", text)
        self.assertIn("before login or form work", text)
        self.assertIn("Do not pick a sibling from the employer's current openings.", text)
        self.assertIn("sponsorship_form_action", text)
        self.assertIn("Do not apply standing No over that instruction.", text)
        self.assertIn("Do not move Original Job Post resolution into hourly discovery.", text)

    def test_control_writes_are_key_upserts(self):
        apply_text = read_workflow("apply-ready-jobs")
        canary = read_workflow("polar-github-write-canary")
        for text in (apply_text, canary):
            self.assertIn("Locate the row by the key cell", text)
            self.assertIn("github_write_canary must never overwrite polar_browser.", text)
            self.assertIn("The reread is the proof.", text)
        self.assertIn("upsert a run_log row for this run_id", apply_text)
        self.assertIn("lease_checkpoint_notes", apply_text)
        self.assertIn("next_incident_id", apply_text)
        self.assertIn("INC-YYYYMMDD-NNN", apply_text)
        self.assertIn("MISSING_FACT, not MISSING_DOCUMENT", apply_text)
        self.assertIn("Never write into the polar_browser row.", canary)

    def test_daily_summary_highlights_priority_submits(self):
        text = read_workflow("daily-job-summary")
        self.assertIn("PRIORITY APPLICATIONS SUBMITTED TODAY", text)

    def test_phase_three_forbids_autonomous_merge(self):
        text = read_workflow("cursor-production-maintenance")
        self.assertIn("STOP BEFORE MERGE", text)
        self.assertIn("status: disabled_until_proven", text)
        self.assertIn("Do not run gh pr merge.", text)
        self.assertIn("Do not click Merge pull request.", text)
        self.assertIn("Do not enable auto-merge.", text)
        self.assertNotIn("then merge the PR", text)
        self.assertNotIn("merge it after tests pass", text)

    def test_phase_two_is_disabled(self):
        text = read_workflow("chatgpt-production-review")
        self.assertIn("status: disabled_until_proven", text)
        self.assertIn("Do not schedule this Workflow.", text)

    def test_compiled_artifacts_have_no_secrets(self):
        paths = list(WORKFLOW_DIR.glob("*.md"))
        paths.append(ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md")
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(SECRET_LINE.search(text), path)
            self.assertIsNone(STREET_VALUE.search(text), path)
            if path.parent == WORKFLOW_DIR:
                self.assertEqual(sanitize_learning_text(text), text, path)

    def test_bootstraps_are_thin_main_pointers(self):
        docs = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in (
            "discover-jobs-hourly",
            "apply-ready-jobs",
            "daily-job-summary",
            "production-learning-daily",
            "polar-scheduler-heartbeat",
        ):
            url = raw_workflow_url(name)
            self.assertIn(url, docs)
            self.assertTrue(url.startswith(GITHUB_RAW_BASE))
            prompt = bootstrap_prompt(name)
            self.assertLess(len(prompt), 400)
            self.assertIn("Read it fully.", prompt)

    def test_apply_url_confidence_stays_in_queue_schema(self):
        header = (ROOT / "generated" / "polar" / "queue_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(header.split(","), QUEUE_COLUMNS)
        self.assertEqual(QUEUE_COLUMNS[8], APPLY_URL_CONFIDENCE)


if __name__ == "__main__":
    unittest.main()
