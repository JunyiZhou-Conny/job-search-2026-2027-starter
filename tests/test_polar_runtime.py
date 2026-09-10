#!/usr/bin/env python3

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
    "## K. Historical duplicate guard",
    "## L. Schema-safe Sheet writes",
    "## M. Browser lease",
    "## N. Run and incident telemetry",
    "## O. Employer requisition identity",
    "## P. Memory ownership and Copilot preflight",
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


def workflow_prompt(name: str) -> str:
    return (ROOT / "generated" / "polar" / "workflows" / f"{name}.md").read_text(
        encoding="utf-8"
    )


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
        self.assertIn("Required future-sponsorship widget: Yes.", text)
        self.assertIn("Future sponsorship required (standing fact): True", text)
        self.assertIn("Answer only the asked semantic.", text)
        self.assertIn("Optional identity or status fields stay blank.", text)
        self.assertIn("Program end / I-20 date: 2026-12-18", text)
        self.assertIn("Year-only graduation widget: 2027", text)
        self.assertIn("Earliest full-time start: 2027-01-18", text)
        self.assertIn("Remote ok: False", text)
        self.assertNotIn("Citizenship country (form and fact): United States", text)
        self.assertIn("visa_sponsorship: Yes.", text)
        self.assertIn("DO NOT AUTO-MAP", text)
        self.assertIn("require work authorization", text)
        self.assertIn("Do not treat that wording as this answer", text)
        self.assertIn("eeo_self_identification:", text)
        self.assertIn("Do not clear them", text)
        self.assertIn("Do not change them", text)
        self.assertIn("gender Male", text)
        self.assertIn("hispanic_latino No", text)
        self.assertIn("race Asian", text)
        self.assertIn("veteran_status I am not a protected veteran", text)

    def test_phone_and_email_are_not_copied(self):
        text = compile_text()
        self.assertIn("Phone numbers live in the local Polar profile", text)
        self.assertIn("dedicated local APPLICATION mailbox", text)
        self.assertIn("street_address_source: local Polar or private profile", text)
        self.assertNotRegex(text, r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
        self.assertNotRegex(text, r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

    def test_statuses_and_caps(self):
        text = compile_text()
        for status in STATUSES:
            self.assertIn(status, text, status)
        self.assertIn("Shared new-execution pool per apply-ready-jobs run: 3.", text)
        self.assertIn("taken from that pool, not added to it", text)
        self.assertNotIn("Regular jobs per apply-ready-jobs run:", text)
        self.assertIn("Regular submissions per local calendar day (America/New_York): 10", text)
        self.assertIn("Prioritized auto-submit: True", text)
        self.assertIn("polar_policy.priority_submit_permitted", text)
        self.assertIn("writing_observation_mode: True", text)
        self.assertIn("SUBMISSION_UNKNOWN first", text)
        self.assertIn("degree_level_gate_missed_at_discovery", text)
        self.assertIn("github_write_canary must not overwrite polar_browser", text)
        self.assertIn("clearly says answer Yes or answer No", text)
        self.assertIn("Simplify Copilot is a required apply precondition.", text)
        self.assertIn("OWNER_ACTION_REQUIRED", text)
        self.assertNotIn("optional_accelerator", text)
        self.assertIn("PREFERENCES.md is not a second strategy database.", text)
        self.assertIn("preference_resolutions: none", text)
        self.assertIn("An open Cursor PR is not canonical.", text)
        self.assertIn("Match candidate_id only.", text)
        self.assertIn("Never reuse. Never fill gaps.", text)
        self.assertIn("KEEP_LOCAL leaves pending", text)

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
        for name, key in (
            ("run_log_schema.csv", "run_log_columns"),
            ("incident_log_schema.csv", "incident_log_columns"),
            ("control_schema.csv", "control_columns"),
            ("learning_reports_schema.csv", "learning_reports_columns"),
        ):
            header = (ROOT / "generated" / "polar" / name).read_text(encoding="utf-8").strip()
            self.assertEqual(header.split(","), operator[key], name)
        self.assertIn("apply_url_confidence", operator["queue_columns"])
        self.assertEqual(operator["queue_columns"].index("apply_url_confidence"), 8)

    def test_workflow_prompts_are_paste_ready(self):
        text = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in (
            "discover-jobs-hourly",
            "apply-ready-jobs",
            "daily-job-summary",
            "production-learning-daily",
            "polar-scheduler-heartbeat",
        ):
            self.assertIn(name, text)
            self.assertIn(
                f"generated/polar/workflows/{name}.md",
                text,
            )
        self.assertIn("thin bootstrap", text)

    def test_apply_ledger_still_loads_gates(self):
        import yaml
        from apply_ledger import load_gates

        raw = yaml.safe_load((ROOT / "config" / "submit_gates.yaml").read_text(encoding="utf-8"))
        self.assertIn("ashby", raw["cursor_cloud"]["gates"])
        self.assertNotIn("gates", raw)
        gates = load_gates()
        self.assertIn("ashby", gates["gates"])
        self.assertEqual(gates["regular_submit_cap_per_run"], 3)
        self.assertEqual(gates["polar_local"]["regular_submit_cap_per_local_day"], 10)

    def test_historical_guard_includes_known_ledger_keys(self):
        text = compile_text()
        self.assertIn("## K. Historical duplicate guard", text)
        self.assertIn("An empty Google Sheet is not a clean slate.", text)
        self.assertIn("6a9b1602fe45b8490f606c9f", text)
        self.assertIn(
            "https://job-boards.greenhouse.io/embed/job_app?for=quantbot-technologies&jr_id=6a9b1602fe45b8490f606c9f",
            text,
        )
        self.assertIn("6a9b756513883870605981ea", text)
        self.assertIn("https://jobs.smartrecruiters.com/solidigm/744000147613769", text)
        self.assertIn("6a7a308fbb6ca93ae561a556", text)
        self.assertIn(
            "https://www.citadel.com/careers/details/sector-data-scientist-2027-intern-us",
            text,
        )
        self.assertIn(
            "https://job-boards.greenhouse.io/togetherai/jobs/5157661007", text
        )
        self.assertIn(
            "https://jobs.ashbyhq.com/chartahealth/3088555d-de93-4236-add1-41005bf0933b",
            text,
        )

    def test_historical_guard_is_compact(self):
        text = compile_text()
        self.assertNotIn("id,job_id,company,role,job_url", text)
        self.assertNotIn("Widget says work authorization", text)
        self.assertNotIn("System trial: compile cloud_swe", text)
        self.assertNotIn("attempt_id,job_id,run_id", text)

    def test_discover_forbids_ojp_apply_still_resolves(self):
        discover = workflow_prompt("discover-jobs-hourly")
        apply = workflow_prompt("apply-ready-jobs")
        self.assertIn("Do not open Original Job Post in this Workflow.", discover)
        self.assertNotIn("click Original Job Post", discover)
        self.assertIn("section K", discover)
        self.assertIn("Original Job Post", apply)
        self.assertIn("section K", apply)

    def test_ready_priority_auto_assign_without_label_gate(self):
        text = compile_text()
        self.assertIn(
            "Polar may assign READY_PRIORITY when a strong configured signal is present.",
            text,
        )
        self.assertNotIn("Labels stay suggestions until Junyi confirms.", text)

    def test_graduation_window_is_note_not_skip(self):
        text = compile_text()
        self.assertIn(
            "An exclusive graduation or enrollment window is an eligibility note, not a skip.",
            text,
        )
        self.assertIn("non-blocking eligibility note, not a skip", text)


if __name__ == "__main__":
    unittest.main()
