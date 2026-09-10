#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    QUEUE_COLUMNS,
    attempt_claim_job,
    claim_is_abandoned,
    confirm_claim_readback,
    discover_may_overwrite_execution_fields,
    ensure_claim_column,
    regular_submit_remaining,
    requisition_identity,
    requisition_submit_blocked,
    restore_queue_after_copilot_miss,
    select_apply_batch,
    submit_claim_still_held,
)
from polar_workflows import render_workflow  # noqa: E402

NOW = datetime.fromisoformat("2026-09-10T16:00:00")
STALE = (NOW - timedelta(hours=4)).isoformat()
FRESH = (NOW - timedelta(minutes=5)).isoformat()


def _last_write(base, first, second):
    row = dict(base)
    row.update(first.fields)
    row.update(second.fields)
    return row


def _ready(job_key: str, status: str = "READY_REGULAR", **extra):
    row = {
        "job_key": job_key,
        "status": status,
        "last_stage": "discovered",
        "attempt_count": "0",
        "claim_run_id": "",
        "weight": "regular",
        "updated_at": FRESH,
    }
    row.update(extra)
    return row


class TestGlobalBrowserLeaseIsGone(unittest.TestCase):
    def setUp(self):
        import yaml

        self.operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )

    def test_discover_and_apply_ignore_stale_polar_browser(self):
        for name in ("discover-jobs-hourly", "apply-ready-jobs"):
            text = render_workflow(name, self.operator)
            self.assertIn("needs_browser_lock: false", text, name)
            self.assertIn(
                "A stale polar_browser owner_run_id must not stop this workflow.",
                text,
                name,
            )
            self.assertNotIn("Exit SKIPPED_LOCKED if blocked", text, name)
            self.assertNotIn("If another non-expired production workflow owns it", text, name)

    def test_heartbeat_does_not_create_a_browser_mutex(self):
        text = render_workflow("polar-scheduler-heartbeat", self.operator)
        self.assertIn("does not treat polar_browser as a mutex", text)
        self.assertIn("needs_browser_lock: false", text)


class TestWorkClaim(unittest.TestCase):
    def test_same_ready_job_has_one_owner_after_last_write(self):
        row = _ready("job-x")
        first = attempt_claim_job(row, run_id="run-a", now=NOW)
        second = attempt_claim_job(row, run_id="run-b", now=NOW)
        self.assertEqual(first.result, "CLAIMED")
        self.assertEqual(second.result, "CLAIMED")
        after = _last_write(row, first, second)
        self.assertEqual(confirm_claim_readback(after, run_id="run-a", job_key="job-x"), "ALREADY_CLAIMED")
        self.assertEqual(confirm_claim_readback(after, run_id="run-b", job_key="job-x"), "CLAIMED")

    def test_different_jobs_claim_without_a_shared_mutex(self):
        left = attempt_claim_job(_ready("job-x"), run_id="run-a", now=NOW)
        right = attempt_claim_job(_ready("job-y"), run_id="run-b", now=NOW)
        self.assertEqual(left.result, "CLAIMED")
        self.assertEqual(right.result, "CLAIMED")
        self.assertEqual(left.fields["claim_run_id"], "run-a")
        self.assertEqual(right.fields["claim_run_id"], "run-b")

    def test_live_foreign_claim_is_not_stolen(self):
        row = _ready(
            "job-x",
            status="IN_PROGRESS",
            claim_run_id="run-a",
            attempt_count="1",
            updated_at=FRESH,
        )
        decision = attempt_claim_job(row, run_id="run-b", now=NOW)
        self.assertEqual(decision.result, "ALREADY_CLAIMED")
        self.assertEqual(decision.action, "skip")

    def test_abandoned_claim_is_recovered_without_blocking_other_jobs(self):
        abandoned = _ready(
            "job-x",
            status="IN_PROGRESS",
            claim_run_id="run-dead",
            attempt_count="1",
            updated_at=STALE,
        )
        ready = _ready("job-y")
        recovered = attempt_claim_job(abandoned, run_id="run-b", now=NOW)
        other = attempt_claim_job(ready, run_id="run-c", now=NOW)
        self.assertEqual(recovered.result, "RECOVERED")
        self.assertEqual(recovered.attempt_count, 1)
        self.assertEqual(other.result, "CLAIMED")

    def test_empty_claim_on_in_progress_is_abandoned(self):
        row = _ready("job-x", status="IN_PROGRESS", claim_run_id="", updated_at=FRESH)
        self.assertTrue(claim_is_abandoned(row, now=NOW))
        self.assertEqual(attempt_claim_job(row, run_id="run-b", now=NOW).result, "RECOVERED")

    def test_terminal_owner_run_log_is_abandoned(self):
        row = _ready(
            "job-x",
            status="IN_PROGRESS",
            claim_run_id="run-dead",
            updated_at=FRESH,
        )
        logs = [{"run_id": "run-dead", "result": "FAILED"}]
        self.assertTrue(claim_is_abandoned(row, now=NOW, run_logs=logs))

    def test_same_requisition_cannot_be_submitted_twice(self):
        rows = [
            {
                "job_key": "jr-1",
                "status": "IN_PROGRESS",
                "claim_run_id": "run-b",
                "employer_requisition_id": "EPIC-1",
                "updated_at": FRESH,
            },
            {
                "job_key": "jr-2",
                "status": "SUBMITTED",
                "employer_requisition_id": "EPIC-1",
            },
        ]
        identity = requisition_identity(employer_requisition_id="EPIC-1")
        self.assertEqual(
            requisition_submit_blocked(rows, identity, "jr-1", now=NOW),
            "jr-2",
        )

    def test_live_sibling_in_progress_blocks_submit(self):
        rows = [
            _ready("jr-1", employer_requisition_id="EPIC-1"),
            {
                "job_key": "jr-2",
                "status": "IN_PROGRESS",
                "claim_run_id": "run-a",
                "employer_requisition_id": "EPIC-1",
                "updated_at": FRESH,
            },
        ]
        identity = requisition_identity(employer_requisition_id="EPIC-1")
        self.assertEqual(
            requisition_submit_blocked(rows, identity, "jr-1", now=NOW),
            "jr-2",
        )

    def test_select_skips_live_foreign_claims_and_keeps_caps(self):
        rows = [
            _ready(
                "live",
                status="IN_PROGRESS",
                claim_run_id="run-a",
                updated_at=FRESH,
            ),
            _ready("p1", "READY_PRIORITY"),
            _ready("r1"),
            _ready("r2"),
            _ready("r3"),
        ]
        batch = select_apply_batch(
            rows,
            max_new_jobs=3,
            reserved_priority_slots=1,
            run_id="run-b",
            now=NOW,
        )
        self.assertNotIn("live", batch.recovery)
        self.assertEqual(batch.priority, ("p1",))
        self.assertEqual(batch.regular, ("r1", "r2"))

    def test_daily_cap_counts_submitted_and_clicked_regulars(self):
        rows = [
            {
                "job_key": "s1",
                "status": "SUBMITTED",
                "weight": "regular",
                "submitted_at": "2026-09-10T09:00:00",
            },
            {
                "job_key": "s2",
                "status": "IN_PROGRESS",
                "weight": "regular",
                "last_stage": "submit_clicked",
                "submitted_at": "2026-09-10T10:00:00",
            },
            {
                "job_key": "p1",
                "status": "SUBMITTED",
                "weight": "prioritized",
                "submitted_at": "2026-09-10T11:00:00",
            },
        ]
        self.assertEqual(regular_submit_remaining(rows, "2026-09-10", cap=10), 8)

    def test_missing_claim_header_is_appended_not_inserted(self):
        headers = [name for name in QUEUE_COLUMNS if name != "claim_run_id"]
        self.assertNotIn("claim_run_id", headers)
        self.assertEqual(ensure_claim_column(headers)[-1], "claim_run_id")
        self.assertEqual(ensure_claim_column(QUEUE_COLUMNS), tuple(QUEUE_COLUMNS))

    def test_discover_does_not_clobber_live_execution_rows(self):
        for status in (
            "IN_PROGRESS",
            "SUBMITTED",
            "SUBMISSION_UNKNOWN",
            "REVIEW_READY",
            "BLOCKED",
        ):
            self.assertFalse(discover_may_overwrite_execution_fields(status), status)
        self.assertTrue(discover_may_overwrite_execution_fields("READY_REGULAR"))
        self.assertTrue(discover_may_overwrite_execution_fields("NEW"))

    def test_submit_requires_this_run_to_still_own_the_row(self):
        row = {
            "job_key": "job-x",
            "status": "IN_PROGRESS",
            "claim_run_id": "run-a",
        }
        self.assertTrue(submit_claim_still_held(row, "run-a"))
        self.assertFalse(submit_claim_still_held(row, "run-b"))
        self.assertFalse(
            submit_claim_still_held({**row, "status": "READY_REGULAR"}, "run-a")
        )

    def test_copilot_miss_clears_claim_and_not_a_browser_lock(self):
        restore = restore_queue_after_copilot_miss(
            ready_status="READY_REGULAR",
            attempt_count_before_run=4,
        )
        self.assertEqual(restore.status, "READY_REGULAR")
        self.assertEqual(restore.claim_run_id, "")


class TestCompiledConcurrencyContract(unittest.TestCase):
    def setUp(self):
        import yaml

        self.operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )

    def test_discover_and_apply_do_not_emit_browser_lockout(self):
        discover = render_workflow("discover-jobs-hourly", self.operator)
        apply = render_workflow("apply-ready-jobs", self.operator)
        heartbeat = render_workflow("polar-scheduler-heartbeat", self.operator)
        for text, name in (
            (discover, "discover-jobs-hourly"),
            (apply, "apply-ready-jobs"),
            (heartbeat, "polar-scheduler-heartbeat"),
        ):
            self.assertIn("needs_browser_lock: false", text, name)
            self.assertNotIn("Exit SKIPPED_LOCKED if blocked", text, name)
            self.assertNotIn("If another non-expired production workflow owns it", text, name)
        self.assertIn("polar_browser is historical control state", discover)
        self.assertIn("already_claimed", apply)
        self.assertIn("recovered_claim", apply)
        self.assertIn("requisition_suppressed", apply)
        self.assertIn("regular_submit_remaining", apply)
        self.assertIn("submit_claim_still_held", apply)
        self.assertIn("append that header at the far right", apply)
        self.assertIn("discover_may_overwrite_execution_fields", discover)
        self.assertIn("Do not write SKIPPED_LOCKED", apply)
        self.assertIn("claim_run_id", apply)
        self.assertNotIn("Release the polar_browser lease", apply)
        self.assertIn("does not treat polar_browser as a mutex", heartbeat)


if __name__ == "__main__":
    unittest.main()
