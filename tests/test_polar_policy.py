#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    APPLY_URL_CONFIDENCE,
    QUEUE_COLUMNS,
    REQUIRED_QUEUE_READBACK,
    TIME_LOST_CATEGORIES,
    decide_lease,
    document_availability,
    header_map,
    named_row,
    pick_canonical_requisition_row,
    readback_fields,
    release_lease,
    requisition_identity,
    sanitize_learning_text,
    select_apply_batch,
    sibling_job_keys,
    workflow_version,
)

APPLY_URL_CONFIDENCE_INDEX = QUEUE_COLUMNS.index(APPLY_URL_CONFIDENCE)


class TestSheetNamedWrites(unittest.TestCase):
    def test_named_write_keeps_status_when_confidence_is_blank(self):
        fields = {name: "x" for name in QUEUE_COLUMNS}
        fields["apply_url_confidence"] = ""
        fields["status"] = "READY_REGULAR"
        fields["last_stage"] = "discovered"
        fields["job_key"] = "abc123"
        row = named_row(QUEUE_COLUMNS, fields)
        self.assertEqual(row[APPLY_URL_CONFIDENCE_INDEX], "")
        self.assertEqual(row[QUEUE_COLUMNS.index("status")], "READY_REGULAR")
        self.assertEqual(row[QUEUE_COLUMNS.index("weight")], "x")
        self.assertEqual(
            readback_fields(QUEUE_COLUMNS, row),
            {
                "job_key": "abc123",
                "status": "READY_REGULAR",
                "last_stage": "discovered",
            },
        )

    def test_positional_omission_of_confidence_shifts_status(self):
        values = ["v"] * len(QUEUE_COLUMNS)
        values[QUEUE_COLUMNS.index("status")] = "READY_REGULAR"
        shortened = values[:APPLY_URL_CONFIDENCE_INDEX] + values[APPLY_URL_CONFIDENCE_INDEX + 1 :]
        self.assertEqual(shortened[QUEUE_COLUMNS.index("status") - 1], "READY_REGULAR")
        self.assertNotEqual(shortened[QUEUE_COLUMNS.index("status")], "READY_REGULAR")

    def test_unknown_field_is_rejected(self):
        with self.assertRaises(ValueError):
            named_row(QUEUE_COLUMNS, {"not_a_column": "x"})

    def test_header_map_uses_names_not_positions(self):
        headers = ["status", "job_key", "apply_url_confidence"]
        mapping = header_map(headers)
        row = named_row(headers, {"job_key": "k", "status": "SKIP", "apply_url_confidence": ""})
        self.assertEqual(row[mapping["job_key"]], "k")
        self.assertEqual(row[mapping["status"]], "SKIP")
        self.assertEqual(row[mapping["apply_url_confidence"]], "")

    def test_required_readback_fields_are_job_status_stage(self):
        self.assertEqual(REQUIRED_QUEUE_READBACK, ("job_key", "status", "last_stage"))


class TestLease(unittest.TestCase):
    def setUp(self):
        self.now = datetime.fromisoformat("2026-09-08T20:00:00")

    def test_missing_lock_is_acquired(self):
        decision = decide_lease(
            None,
            now=self.now,
            run_id="run-1",
            workflow="apply-ready-jobs",
            needs_lock=True,
        )
        self.assertEqual(decision.lock_result, "ACQUIRED")
        self.assertEqual(decision.action, "acquire")
        self.assertEqual(decision.owner_run_id, "run-1")

    def test_foreign_unexpired_lock_skips(self):
        decision = decide_lease(
            {
                "owner_run_id": "run-other",
                "workflow": "discover-jobs-hourly",
                "expires_at": (self.now + timedelta(hours=2)).isoformat(),
            },
            now=self.now,
            run_id="run-2",
            workflow="apply-ready-jobs",
            needs_lock=True,
        )
        self.assertEqual(decision.lock_result, "SKIPPED_LOCKED")
        self.assertEqual(decision.action, "abort")
        self.assertEqual(decision.owner_run_id, "run-other")

    def test_expired_lock_is_stolen(self):
        decision = decide_lease(
            {
                "owner_run_id": "run-dead",
                "expires_at": (self.now - timedelta(minutes=1)).isoformat(),
            },
            now=self.now,
            run_id="run-3",
            workflow="discover-jobs-hourly",
            needs_lock=True,
        )
        self.assertEqual(decision.lock_result, "ACQUIRED")
        self.assertEqual(decision.owner_run_id, "run-3")

    def test_summary_does_not_need_lock(self):
        decision = decide_lease(
            {
                "owner_run_id": "run-apply",
                "expires_at": (self.now + timedelta(hours=2)).isoformat(),
            },
            now=self.now,
            run_id="run-summary",
            workflow="daily-job-summary",
            needs_lock=False,
        )
        self.assertEqual(decision.lock_result, "NOT_REQUIRED")

    def test_same_run_refreshes_near_expiry(self):
        decision = decide_lease(
            {
                "owner_run_id": "run-1",
                "expires_at": (self.now + timedelta(minutes=30)).isoformat(),
            },
            now=self.now,
            run_id="run-1",
            workflow="apply-ready-jobs",
            needs_lock=True,
        )
        self.assertEqual(decision.lock_result, "REFRESHED")
        self.assertEqual(decision.action, "refresh")

    def test_release_clears_owner(self):
        decision = release_lease("run-1", "apply-ready-jobs", self.now)
        self.assertEqual(decision.lock_result, "RELEASED")
        self.assertEqual(decision.owner_run_id, "")


class TestPriorityScheduling(unittest.TestCase):
    def test_reserves_one_priority_and_fills_regular(self):
        rows = [
            {"job_key": "u1", "status": "SUBMISSION_UNKNOWN"},
            {"job_key": "p1", "status": "READY_PRIORITY"},
            {"job_key": "p2", "status": "READY_PRIORITY"},
            {"job_key": "r1", "status": "READY_REGULAR"},
            {"job_key": "r2", "status": "READY_REGULAR"},
            {"job_key": "r3", "status": "READY_REGULAR"},
        ]
        batch = select_apply_batch(rows, max_new_jobs=3, reserved_priority_slots=1)
        self.assertEqual(batch.recovery, ("u1",))
        self.assertEqual(batch.priority, ("p1",))
        self.assertEqual(batch.regular, ("r1", "r2"))

    def test_regular_gets_all_slots_when_no_priority(self):
        rows = [
            {"job_key": "r1", "status": "READY_REGULAR"},
            {"job_key": "r2", "status": "READY_REGULAR"},
            {"job_key": "r3", "status": "READY_REGULAR"},
            {"job_key": "r4", "status": "READY_REGULAR"},
        ]
        batch = select_apply_batch(rows, max_new_jobs=3, reserved_priority_slots=1)
        self.assertEqual(batch.priority, ())
        self.assertEqual(batch.regular, ("r1", "r2", "r3"))

    def test_in_progress_is_recovered_before_new_work(self):
        rows = [
            {"job_key": "old", "status": "IN_PROGRESS", "updated_at": "2026-09-08T10:00:00"},
            {"job_key": "p1", "status": "READY_PRIORITY"},
        ]
        batch = select_apply_batch(rows, max_new_jobs=3)
        self.assertEqual(batch.recovery, ("old",))
        self.assertEqual(batch.priority, ("p1",))


class TestRequisitionDedupe(unittest.TestCase):
    def test_same_requisition_id_matches(self):
        self.assertEqual(
            requisition_identity(employer_requisition_id="R-99"),
            ("requisition", "r-99"),
        )

    def test_jobright_url_is_not_an_employer_identity(self):
        self.assertIsNone(
            requisition_identity(
                apply_url="https://jobright.ai/jobs/info/6a9b1602fe45b8490f606c9f"
            )
        )

    def test_canonical_url_ignores_utm(self):
        self.assertEqual(
            requisition_identity(
                apply_url="https://jobs.ashbyhq.com/acme/abc?utm_source=jobright"
            ),
            requisition_identity(apply_url="https://jobs.ashbyhq.com/acme/abc"),
        )

    def test_submitted_row_wins_and_siblings_are_listed(self):
        rows = [
            {
                "job_key": "jr-1",
                "status": "READY_REGULAR",
                "employer_requisition_id": "EPIC-1",
                "discovered_at": "2026-09-08T10:00:00",
            },
            {
                "job_key": "jr-2",
                "status": "SUBMITTED",
                "employer_requisition_id": "EPIC-1",
                "discovered_at": "2026-09-08T11:00:00",
            },
        ]
        identity = requisition_identity(employer_requisition_id="EPIC-1")
        canonical = pick_canonical_requisition_row(rows, identity)
        self.assertEqual(canonical, "jr-2")
        self.assertEqual(sibling_job_keys(rows, identity, canonical), ("jr-1",))


class TestSanitizer(unittest.TestCase):
    def test_redacts_private_material(self):
        dirty = (
            "password: hunter2 "
            "cookie: abc "
            "otp: 123456 "
            "mail me at apply.box@example.com "
            "call 617-555-0142 "
            "123 Fake Street "
            "GPA: 3.92"
        )
        clean = sanitize_learning_text(dirty)
        self.assertEqual(
            clean,
            "[REDACTED_PASSWORD] "
            "[REDACTED_SECRET] "
            "[REDACTED_OTP] "
            "mail me at [REDACTED_EMAIL] "
            "call [REDACTED_PHONE] "
            "[REDACTED_STREET] "
            "[REDACTED_TRANSCRIPT]",
        )
        self.assertNotIn("hunter2", clean)
        self.assertNotIn("apply.box@example.com", clean)
        self.assertNotIn("123 Fake Street", clean)

    def test_leaves_ordinary_incident_text(self):
        text = "Simplify onboarding wall. repeat_key=simplify_onboarding"
        self.assertEqual(sanitize_learning_text(text), text)


class TestWorkflowVersionAndDocuments(unittest.TestCase):
    def test_version_changes_when_body_changes(self):
        first = workflow_version("2026-09-08.learning-loop", "alpha")
        second = workflow_version("2026-09-08.learning-loop", "beta")
        self.assertTrue(first.startswith("2026-09-08.learning-loop+"))
        self.assertNotEqual(first, second)

    def test_transcript_files_are_present(self):
        docs = {row["id"]: row for row in document_availability(ROOT)}
        self.assertTrue(docs["emory_official_transcript"]["exists"])
        self.assertTrue(docs["harvard_unofficial_transcript"]["exists"])
        self.assertEqual(
            docs["emory_official_transcript"]["approved_path"],
            "Emory_Official_Transcript.pdf",
        )
        self.assertEqual(
            docs["harvard_unofficial_transcript"]["approved_path"],
            "Harvard_unofficial_transcript.pdf",
        )

    def test_time_lost_categories_cover_measured_bottlenecks(self):
        self.assertEqual(
            TIME_LOST_CATEGORIES,
            (
                "AUTH",
                "ACCOUNT_CREATION",
                "SIMPLIFY",
                "MISSING_FACT",
                "MISSING_DOCUMENT",
                "WRITING",
                "DROPDOWN_UI",
                "DUPLICATE",
                "SUBMIT_VERIFY",
                "OTHER",
            ),
        )


if __name__ == "__main__":
    unittest.main()
