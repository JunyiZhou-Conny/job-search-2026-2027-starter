#!/usr/bin/env python3
"""Phase 2 compile locks: heartbeat retired, archive copy-not-delete, incident append-only."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    archive_queue_copy_permitted,
    archive_queue_deletes_live,
    archive_queue_row_action,
    chatty_sheet_io_permitted,
    heartbeat_is_apply_proof,
    heartbeat_writes_permitted,
    incident_overwrite_permitted,
    lock_result_carries_meaning,
    plan_archive_queue_copy,
    plan_incident_log_write,
    ready_fifo_permitted,
    run_log_full_history_permitted,
    sheet_io_repeat_lookup_permitted,
    sheet_ready_is_apply_admission,
)
from polar_workflows import render_workflow  # noqa: E402
from build_polar_runtime import compile_sections, render as render_polar  # noqa: E402

OPERATOR = None


def _operator():
    global OPERATOR
    if OPERATOR is None:
        import yaml

        OPERATOR = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
    return OPERATOR


class TestHeartbeatRetired(unittest.TestCase):
    def test_helpers_forbid_heartbeat_as_apply_proof(self):
        self.assertFalse(heartbeat_writes_permitted())
        self.assertFalse(heartbeat_is_apply_proof())
        self.assertFalse(lock_result_carries_meaning())
        self.assertFalse(_operator()["schedules"]["scheduler_heartbeat"]["enabled"])

    def test_compiled_heartbeat_exits_no_work(self):
        text = render_workflow("polar-scheduler-heartbeat", _operator())
        self.assertIn("status: retired", text)
        self.assertIn("write this run_id as finalized NO_WORK", text)
        self.assertIn("Do not append a heartbeat row", text)
        self.assertNotIn("Open https://example.com", text)

    def test_daily_summary_missing_heartbeat_is_not_failure(self):
        text = render_workflow("daily-job-summary", _operator())
        self.assertIn("A missing heartbeat is not a failure.", text)
        self.assertNotIn("- heartbeat success or failure if a heartbeat row exists today", text)


class TestArchiveQueueCopyNotDelete(unittest.TestCase):
    def test_live_apply_blocks_copy_and_never_deletes(self):
        self.assertFalse(archive_queue_deletes_live())
        self.assertFalse(archive_queue_copy_permitted(apply_is_live=True))
        self.assertTrue(archive_queue_copy_permitted(apply_is_live=False))

    def test_row_actions(self):
        self.assertEqual(archive_queue_row_action({"status": "READY_REGULAR"}), "archive")
        self.assertEqual(archive_queue_row_action({"status": "READY_PRIORITY"}), "archive")
        self.assertEqual(archive_queue_row_action({"status": "NEW"}), "archive")
        self.assertEqual(archive_queue_row_action({"status": "IN_PROGRESS"}), "keep_live")
        self.assertEqual(archive_queue_row_action({"status": "SUBMITTED"}), "keep_live")
        self.assertEqual(archive_queue_row_action({"status": "BLOCKED"}), "keep_live")
        self.assertEqual(
            archive_queue_row_action(
                {"status": "SKIP", "updated_at": "2026-09-15T09:22:00-04:00"}
            ),
            "keep_live",
        )
        self.assertEqual(
            archive_queue_row_action(
                {"status": "SKIP", "updated_at": "2026-09-13T12:00:00-04:00"}
            ),
            "archive",
        )
        self.assertEqual(
            plan_archive_queue_copy(
                (
                    {"status": "READY_REGULAR"},
                    {"status": "SUBMITTED"},
                    {"status": "SKIP", "discovered_at": "2026-09-10"},
                )
            ),
            (0, 2),
        )

    def test_migration_compile_is_copy_not_delete(self):
        text = render_workflow("polar-sheet-migration", _operator())
        self.assertIn("Create archive_queue only when that tab is missing", text)
        self.assertIn("Do not delete live rows", text)
        self.assertIn("If an apply PARTIAL is live, stop", text)


class TestIncidentAndSheetIO(unittest.TestCase):
    def test_incident_write_is_append_only(self):
        self.assertFalse(incident_overwrite_permitted())
        empty = plan_incident_log_write([], "INC-20260915-014")
        self.assertEqual(empty.action, "append")
        exists = plan_incident_log_write(
            [{"incident_id": "INC-20260915-011"}],
            "INC-20260915-011",
        )
        self.assertEqual(exists.action, "abort")
        dup = plan_incident_log_write(
            (
                {"incident_id": "INC-20260915-011"},
                {"incident_id": "INC-20260915-011"},
            ),
            "INC-20260915-011",
        )
        self.assertEqual(dup.action, "abort")

    def test_no_repeat_lookup_or_full_history(self):
        self.assertFalse(chatty_sheet_io_permitted())
        self.assertFalse(run_log_full_history_permitted())
        self.assertFalse(sheet_io_repeat_lookup_permitted(already_queried_this_key=True))
        self.assertTrue(sheet_io_repeat_lookup_permitted(already_queried_this_key=False))
        apply = render_workflow("apply-ready-jobs", _operator())
        self.assertIn("polar_policy.plan_incident_log_write", apply)
        self.assertIn("Do not QUERY the same job_key twice in one card", apply)


class TestReadyFifoAndSafetyFences(unittest.TestCase):
    def test_ready_fifo_stays_off(self):
        self.assertFalse(ready_fifo_permitted())
        self.assertFalse(sheet_ready_is_apply_admission())
        apply = render_workflow("apply-ready-jobs", _operator())
        self.assertIn("polar_policy.ready_fifo_permitted is false", apply)
        polar = render_polar(compile_sections())
        self.assertIn("polar_policy.ready_fifo_permitted is false", polar)
        self.assertNotIn("grok-apply-jobs", polar)
        self.assertIn("Required future-sponsorship widget: Yes.", polar)
        self.assertNotIn("Required future-sponsorship widget: No.", polar)
        self.assertIn("Fast validation pass", polar)


if __name__ == "__main__":
    unittest.main()
