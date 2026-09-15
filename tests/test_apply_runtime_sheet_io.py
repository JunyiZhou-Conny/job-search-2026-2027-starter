#!/usr/bin/env python3
"""Phase 3 compile locks: Sheet I/O batching, no full scans."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    APPLY_START_QUERY_CONCERNS,
    CARD_QUERY_CONCERNS,
    INCIDENT_QUERY_CONCERNS,
    SHEET_WRITE_MODE,
    apply_start_query_concerns,
    capability_reprove_mid_run_permitted,
    capability_reprove_permitted,
    card_query_concerns,
    company_role_location_query_permitted,
    dump_ready_inventory_permitted,
    full_queue_scan_permitted,
    incident_query_concerns,
    live_apply_query_is_batched,
    one_cell_then_reread_permitted,
    recovery_query_is_batched,
    run_log_history_scan_permitted,
    sheet_io_batching_lines,
    sheet_io_batching_required,
    sheet_query_after_claim_permitted,
    sheet_query_plan,
    sheet_query_remaining,
    sheet_write_batch_required,
    sheet_write_mode,
    sheet_write_readback_is_repeat_query,
)
from polar_workflows import render_workflow  # noqa: E402
from build_grokbot_runtime import compile_all as compile_grok  # noqa: E402
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


def apply_text() -> str:
    return render_workflow("apply-ready-jobs", _operator())


def discover_text() -> str:
    return render_workflow("discover-jobs-hourly", _operator())


def grok_apply_text() -> str:
    return compile_grok()["workflows/grok-apply-jobs.md"]


def grok_learning_text() -> str:
    return compile_grok()["workflows/grok-production-learning-daily.md"]


class TestSheetIoHelpers(unittest.TestCase):
    def test_batching_flags(self):
        self.assertTrue(sheet_io_batching_required())
        self.assertFalse(full_queue_scan_permitted())
        self.assertFalse(dump_ready_inventory_permitted())
        self.assertTrue(sheet_write_batch_required())
        self.assertEqual(sheet_write_mode(), SHEET_WRITE_MODE)
        self.assertEqual(SHEET_WRITE_MODE, "named_header_batch")
        self.assertFalse(one_cell_then_reread_permitted())
        self.assertFalse(capability_reprove_mid_run_permitted())
        self.assertFalse(capability_reprove_permitted(already_proven=True))
        self.assertFalse(run_log_history_scan_permitted())
        self.assertTrue(recovery_query_is_batched())
        self.assertTrue(live_apply_query_is_batched())
        self.assertFalse(sheet_write_readback_is_repeat_query())
        self.assertFalse(sheet_query_after_claim_permitted())

    def test_one_query_per_concern(self):
        self.assertEqual(apply_start_query_concerns(), APPLY_START_QUERY_CONCERNS)
        self.assertEqual(
            APPLY_START_QUERY_CONCERNS,
            ("live_apply_partial", "recovery_unknown_in_progress"),
        )
        self.assertEqual(card_query_concerns(), CARD_QUERY_CONCERNS)
        self.assertEqual(CARD_QUERY_CONCERNS, ("job_key",))
        self.assertEqual(incident_query_concerns(), INCIDENT_QUERY_CONCERNS)
        self.assertEqual(
            sheet_query_plan(phase="apply_start"),
            APPLY_START_QUERY_CONCERNS,
        )
        self.assertEqual(
            sheet_query_plan(
                phase="apply_start",
                already_queried=("live_apply_partial",),
            ),
            ("recovery_unknown_in_progress",),
        )
        self.assertEqual(
            sheet_query_plan(phase="apply_start", already_queried=APPLY_START_QUERY_CONCERNS),
            (),
        )
        self.assertEqual(sheet_query_plan(phase="card"), ("job_key",))
        self.assertEqual(
            sheet_query_plan(phase="card", already_queried=("job_key",)),
            (),
        )
        self.assertEqual(
            sheet_query_plan(phase="incident"),
            ("incident_id_today_prefix",),
        )
        self.assertEqual(sheet_query_remaining(already_queried_this_concern=False), 1)
        self.assertEqual(sheet_query_remaining(already_queried_this_concern=True), 0)
        self.assertFalse(company_role_location_query_permitted(job_key_miss=False))
        self.assertTrue(company_role_location_query_permitted(job_key_miss=True))
        with self.assertRaises(ValueError):
            sheet_query_plan(phase="full_queue")

    def test_batching_lines_are_shared(self):
        apply_lines = sheet_io_batching_lines(apply_start=True)
        card_lines = sheet_io_batching_lines(apply_start=False)
        self.assertIn("Start Sheet I/O is two QUERYs, then stop", apply_lines[0])
        self.assertNotIn("Start Sheet I/O is two QUERYs, then stop", card_lines)
        self.assertTrue(set(card_lines) <= set(apply_lines))
        self.assertIn("named_header_batch", "\n".join(apply_lines))


class TestSheetIoCompile(unittest.TestCase):
    def test_polar_apply_batches_start_and_card_queries(self):
        text = apply_text()
        for line in sheet_io_batching_lines(apply_start=True):
            self.assertIn(line, text)
        self.assertIn("write_mode: named_header_batch", text)
        self.assertIn("batch: required", text)
        self.assertIn("one_cell_then_reread: false", text)
        self.assertIn("One QUERY of run_log for every open apply PARTIAL", text)
        self.assertIn("Do not repeat this QUERY later in the run.", text)
        self.assertIn("One QUERY for SUBMISSION_UNKNOWN and IN_PROGRESS together.", text)
        self.assertIn("One QUERY of that job_key, then stop.", text)
        self.assertIn("Immediately upsert a run_log row for this run_id", text)
        self.assertIn("If it returns stale_close", text)
        self.assertIn("Required future-sponsorship widget: Yes.", text)
        self.assertNotIn("Required future-sponsorship widget: No.", text)
        self.assertIn("mode: fast_validation_pass", text)
        self.assertIn("Do not create a Sheet tab named scratch", text)

    def test_discover_batches_writes_without_stale_close(self):
        text = discover_text()
        for line in sheet_io_batching_lines(apply_start=False):
            self.assertIn(line, text)
        self.assertNotIn("Start Sheet I/O is two QUERYs, then stop", text)
        self.assertNotIn("stale_close", text)
        self.assertNotIn("including after stale_close", text)
        self.assertIn("Immediately upsert a run_log row for this run_id", text)
        self.assertIn("one job_key QUERY then one named-header batch write", text)

    def test_grok_apply_matches_polar_batching(self):
        text = grok_apply_text()
        for line in sheet_io_batching_lines(apply_start=True):
            self.assertIn(line, text)
        self.assertIn("write_mode: named_header_batch", text)
        self.assertIn("One QUERY of that job_key, then stop.", text)
        self.assertIn("Unless this run exited NO_WORK, upsert this run_id as PARTIAL", text)
        self.assertIn("including after stale_close", text)
        self.assertIn("Cheap SKIP first.", text)

    def test_grok_learning_is_not_an_apply_query_plan(self):
        text = grok_learning_text()
        self.assertIn("Do not run polar_policy.start_apply_run_action", text)
        self.assertNotIn("Start Sheet I/O is two QUERYs, then stop", text)
        self.assertIn("write_mode: named_header_batch", text)

    def test_polar_runtime_keeps_fences(self):
        polar = render_polar(compile_sections())
        self.assertNotIn("grok-apply-jobs", polar)
        self.assertIn("Required future-sponsorship widget: Yes.", polar)
        self.assertIn("one named-header batch per row mutation", polar)
        self.assertIn("Do not scan the full queue.", polar)
        self.assertIn("Do not re-prove google_sheets mid-run.", polar)


if __name__ == "__main__":
    unittest.main()
