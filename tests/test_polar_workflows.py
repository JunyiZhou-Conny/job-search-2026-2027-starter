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
    PROMOTION_OUTCOMES,
    QUEUE_COLUMNS,
    REQUIRED_QUEUE_READBACK,
    bootstrap_prompt,
    parse_contract_block,
    raw_workflow_url,
    sanitize_learning_text,
)
from polar_workflows import WORKFLOW_RENDERERS, render_workflow  # noqa: E402

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
            self.assertEqual(lease.get("needs_browser_lock"), "false")
            self.assertIn("historical control state", text)
            if name == "apply-ready-jobs":
                claim = parse_contract_block(text, "Work claim")
                self.assertEqual(claim.get("ownership"), "queue.claim_run_id")
                self.assertIn("already_claimed", text)
                self.assertIn("Do not write SKIPPED_LOCKED", text)

    def test_apply_priority_and_simplify_contracts(self):
        text = read_workflow("apply-ready-jobs")
        priority = parse_contract_block(text, "Priority contract")
        self.assertEqual(priority.get("reserved_priority_slots"), "1")
        self.assertEqual(priority.get("max_new_jobs"), "3")
        self.assertEqual(priority.get("shared_pool"), "true")
        self.assertEqual(priority.get("reservation_is_from_pool"), "true")
        self.assertEqual(priority.get("worker_budget"), "per_run")
        self.assertEqual(priority.get("daily_regular_cap"), "none")
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
        self.assertEqual(simplify.get("role"), "required_precondition")
        self.assertEqual(simplify.get("max_attempts_per_application"), "1")
        self.assertEqual(simplify.get("silent_manual_fallback"), "false")
        self.assertEqual(simplify.get("missing_action"), "owner_action_required")
        self.assertEqual(simplify.get("consume_job"), "false")
        self.assertEqual(simplify.get("control_key"), "env_simplify_copilot")
        self.assertIn("do not fall back to traditional clicking", text.lower())
        self.assertIn("OWNER_ACTION_REQUIRED", text)
        self.assertIn("## Memory ownership", text)
        self.assertIn("Polar Preferences Delta", read_workflow("production-learning-daily"))
        self.assertIn("## Employer requisition dedupe", text)
        self.assertIn("## Apply-time hard eligibility", text)
        self.assertIn("Sponsorship unknown, unavailable, or generally not offered is not a skip.", text)
        self.assertIn("phd candidates only", text)
        self.assertIn("degree_level_gate_missed_at_discovery", text)
        self.assertIn("before login or form work", text)
        self.assertIn("Do not pick a sibling from the employer's current openings.", text)
        self.assertIn("clearly says answer Yes or answer No", text)
        self.assertIn("polar_policy.auth_form_action", text)
        self.assertIn("Required future-sponsorship widget: Yes.", text)
        self.assertIn("A blocked authorization field must not stop the rest of the worker.", text)
        self.assertIn("Barriers removed is not a closed page.", text)
        self.assertIn("Do not move Original Job Post resolution into hourly discovery.", text)
        self.assertNotIn("optional_accelerator", text)
        self.assertNotIn("preferences-learning-daily", text)
        learning = read_workflow("production-learning-daily")
        self.assertIn("Do not upload the raw file", learning)
        self.assertIn("local_private", learning.lower())
        self.assertIn("SECRET_OR_CREDENTIAL", learning)
        self.assertNotIn("preferences-learning-daily", learning)
        self.assertIn("Do not create a preferences-cleanup workflow.", learning)
        self.assertIn("Emitting the report does not resolve it.", learning)
        self.assertIn("Do not emit keep_local ids.", learning)
        self.assertIn("Never reuse an id.", learning)
        self.assertIn("candidate_id", learning)
        self.assertIn("An open Cursor PR is not canonical.", learning)
        self.assertIn("## Preferences reconcile", read_workflow("discover-jobs-hourly"))
        self.assertIn("## Preferences reconcile", text)
        cursor = read_workflow("cursor-production-maintenance")
        for outcome in PROMOTION_OUTCOMES:
            self.assertIn(outcome, cursor, outcome)
        self.assertIn("Do not treat PREFERENCES.md as the Cursor target list.", cursor)
        self.assertIn("knowledge/preference_resolutions.yaml", cursor)
        self.assertIn("An open PR is not canonical.", cursor)

    def test_generated_workflows_match_compiler(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        for name in WORKFLOW_RENDERERS:
            self.assertEqual(
                read_workflow(name),
                render_workflow(name, operator),
                name,
            )

    def test_control_writes_are_key_upserts(self):
        apply_text = read_workflow("apply-ready-jobs")
        canary = read_workflow("polar-github-write-canary")
        for text in (apply_text, canary):
            self.assertIn("Locate the row by the key cell", text)
            self.assertIn("must never overwrite polar_browser.", text)
            self.assertIn("The reread is the proof.", text)
        self.assertIn("upsert a run_log row for this run_id", apply_text)
        self.assertIn("claim_run_id", apply_text)
        self.assertIn("INC-YYYYMMDD-NNN", apply_text)
        self.assertIn("01 and 001 count as the same number", apply_text)
        self.assertIn("If 001 and 003 exist, write 004.", apply_text)
        self.assertIn("The sequence is monotonic.", apply_text)
        self.assertIn("MISSING_FACT, not MISSING_DOCUMENT", apply_text)
        self.assertIn("acquired_at, and expires_at", canary)
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
            self.assertLess(len(prompt), 2500)
            self.assertIn("TRUST DELEGATION", prompt)
            self.assertIn(url, prompt)

    def test_apply_url_confidence_stays_in_queue_schema(self):
        header = (ROOT / "generated" / "polar" / "queue_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(header.split(","), QUEUE_COLUMNS)
        self.assertEqual(QUEUE_COLUMNS[8], APPLY_URL_CONFIDENCE)
        self.assertIn("resume_cluster", QUEUE_COLUMNS)
        self.assertEqual(
            QUEUE_COLUMNS[-4:],
            [
                "resume_family",
                "route_confidence",
                "route_reason",
                "resume_variant",
            ],
        )
        self.assertLess(
            QUEUE_COLUMNS.index("resume_cluster"),
            QUEUE_COLUMNS.index("resume_family"),
        )


if __name__ == "__main__":
    unittest.main()
