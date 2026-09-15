#!/usr/bin/env python3
"""Owner-listed apply-runtime tests: PERFORMANCE, STATE/CONCURRENCY, SCHEMA, LOGGING.

Locks uniqueness, one live apply, cheap SKIP, no scratch, and telemetry
duration. READY_* FIFO and scratch-tab lookup are not apply admission.
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    APPLY_WORKFLOW_NAMES,
    DUPLICATE_JOB_KEY_REPEAT_KEY,
    SHEET_QUERY_NA_REPEAT_KEY,
    TELEMETRY_INCONSISTENCY,
    apply_run_is_live,
    attempt_claim_job,
    capability_reprove_permitted,
    cheap_skip_claims_in_progress,
    cheap_skip_generates_resume,
    cheap_skip_opens_employer_ats,
    cheap_skip_write_action,
    claim_job_key,
    eligibility_surface_action,
    full_queue_read_permitted,
    incident_id_day_prefix,
    incident_ids_for_day,
    live_apply_run_id,
    locate_rows_by_key,
    named_row,
    plan_queue_upsert_by_job_key,
    plan_run_log_write,
    preferences_reconcile_action,
    recovery_lookup_statuses,
    run_duration_minutes,
    scratch_tab_permitted,
    sheet_query_failure_action,
    skip_path_action,
    start_apply_run_action,
    tab_is_forbidden_scratch,
    telemetry_duration_status,
)
from polar_workflows import render_workflow  # noqa: E402
from build_grokbot_runtime import compile_all as compile_grok  # noqa: E402

NOW = datetime(2026, 9, 15, 10, 20, 0, tzinfo=ZoneInfo("America/New_York"))
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


def grok_apply_text() -> str:
    return compile_grok()["workflows/grok-apply-jobs.md"]


class TestPerformance(unittest.TestCase):
    def test_cheap_skip_does_not_open_ats_or_generate_resume(self):
        self.assertEqual(
            skip_path_action(hard_fact_on_card=True),
            "cheap_skip_no_ats",
        )
        self.assertEqual(
            skip_path_action(sheet_status="BLOCKED"),
            "cheap_skip_no_ats",
        )
        self.assertEqual(
            skip_path_action(already_applied_on_jobright=True),
            "cheap_skip_no_ats",
        )
        self.assertEqual(
            skip_path_action(section_k_hit=True),
            "cheap_skip_no_ats",
        )
        self.assertEqual(
            skip_path_action(card_jd_sufficient=False),
            "open_employer_jd_only",
        )
        self.assertEqual(
            skip_path_action(),
            "continue_toward_claim",
        )
        self.assertFalse(cheap_skip_opens_employer_ats())
        self.assertFalse(cheap_skip_generates_resume())
        self.assertFalse(cheap_skip_claims_in_progress())
        self.assertEqual(eligibility_surface_action(card_jd_sufficient=True), "decide_on_card")
        self.assertEqual(
            eligibility_surface_action(card_jd_sufficient=False),
            "open_employer_jd_only",
        )

    def test_terminal_sheet_memory_is_left_alone(self):
        for status in (
            "BLOCKED",
            "SUBMITTED",
            "SKIP",
            "REVIEW_READY",
            "IN_PROGRESS",
            "SUBMISSION_UNKNOWN",
        ):
            self.assertEqual(cheap_skip_write_action(status), "leave_existing_row", status)
        self.assertEqual(cheap_skip_write_action(""), "write_skip_row")
        self.assertEqual(cheap_skip_write_action("NEW"), "write_skip_row")

    def test_startup_helpers_are_cheap_noops(self):
        self.assertFalse(capability_reprove_permitted(already_proven=True))
        self.assertTrue(capability_reprove_permitted(already_proven=False))
        self.assertEqual(preferences_reconcile_action(), "noop")
        self.assertEqual(
            preferences_reconcile_action(pending_ids=["pref_20260912_003"]),
            "reconcile",
        )
        self.assertFalse(full_queue_read_permitted())
        self.assertEqual(
            recovery_lookup_statuses(),
            ("SUBMISSION_UNKNOWN", "IN_PROGRESS"),
        )
        self.assertEqual(
            sheet_query_failure_action("#N/A"),
            "treat_as_miss_no_scratch",
        )
        self.assertEqual(sheet_query_failure_action("#REF!"), "treat_as_miss_no_scratch")
        self.assertEqual(sheet_query_failure_action("6aa9414eeff87f571fc98c26"), "use_value")

    def test_compile_orders_cheap_skip_before_generate_resume(self):
        apply = apply_text()
        cheap = apply.index("Cheap SKIP first.")
        generate = apply.index("Generate My Resume")
        self.assertLess(cheap, generate)
        self.assertIn("Do not claim IN_PROGRESS. Do not Generate My Resume. Do not Apply Now.", apply)
        self.assertIn("These labels are the application path. They are not the SKIP path.", apply)
        grok = grok_apply_text()
        self.assertIn("Cheap SKIP first.", grok)
        self.assertLess(grok.index("Cheap SKIP first."), grok.index("Apply Now opens the employer ATS."))


class TestStateConcurrency(unittest.TestCase):
    def test_unique_job_key_is_one_row(self):
        rows = [
            {"job_key": "aaa", "status": "SKIP"},
            {"job_key": "bbb", "status": "NEW"},
            {"job_key": "aaa", "status": "SUBMITTED"},
        ]
        self.assertEqual(locate_rows_by_key(rows, "aaa", "job_key"), (0, 2))
        plan = plan_queue_upsert_by_job_key(rows, "aaa")
        self.assertEqual(plan.action, "abort")
        self.assertEqual(plan.match_count, 2)
        self.assertEqual(plan.repeat_key, DUPLICATE_JOB_KEY_REPEAT_KEY)
        self.assertEqual(plan_queue_upsert_by_job_key(rows, "bbb").action, "update")
        self.assertEqual(plan_queue_upsert_by_job_key(rows, "ccc").action, "append")

    def test_duplicate_key_never_claims(self):
        rows = [
            {"job_key": "oversight", "status": "IN_PROGRESS", "claim_run_id": "R-20260915-0816"},
            {"job_key": "oversight", "status": "NEW"},
        ]
        decision = claim_job_key(rows, "oversight", run_id="R-20260915-0824", now=NOW)
        self.assertEqual(decision.result, "DUPLICATE_KEY")
        self.assertEqual(decision.action, "abort")
        self.assertEqual(decision.fields, {})
        single = [{"job_key": "capgemini", "status": "NEW", "attempt_count": "0"}]
        claimed = claim_job_key(single, "capgemini", run_id="R-20260915-0920", now=NOW)
        self.assertEqual(claimed.result, "CLAIMED")
        missing = claim_job_key([], "fresh", run_id="R-20260915-0920", now=NOW)
        self.assertEqual(missing.result, "CLAIMED")
        self.assertEqual(missing.prior_status, "NEW")

    def test_one_live_apply_across_executors(self):
        self.assertEqual(APPLY_WORKFLOW_NAMES, frozenset({"apply-ready-jobs", "grok-apply-jobs"}))
        live = {
            "run_id": "R-20260915-0816",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "ended_at": "",
        }
        self.assertTrue(apply_run_is_live(live))
        self.assertEqual(start_apply_run_action([live]), "NO_WORK")
        self.assertEqual(
            start_apply_run_action([live], this_run_id="R-20260915-0816"),
            "continue",
        )
        grok_live = {
            "run_id": "G-20260915-105000",
            "workflow": "grok-apply-jobs",
            "result": "PARTIAL",
            "ended_at": "",
        }
        self.assertEqual(start_apply_run_action([grok_live]), "NO_WORK")
        self.assertEqual(live_apply_run_id([grok_live]), "G-20260915-105000")
        closed_partial = {
            "run_id": "R-20260914-1631",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "ended_at": "2026-09-14T17:02:08-04:00",
        }
        self.assertFalse(apply_run_is_live(closed_partial))
        self.assertEqual(start_apply_run_action([closed_partial]), "continue")
        discover = {
            "run_id": "R-20260913-180123",
            "workflow": "discover-jobs-hourly",
            "result": "PARTIAL",
            "ended_at": "",
        }
        self.assertFalse(apply_run_is_live(discover))
        success = {
            "run_id": "R-20260915-0920",
            "workflow": "apply-ready-jobs",
            "result": "SUCCESS",
            "ended_at": "2026-09-15T09:52:00-04:00",
        }
        self.assertEqual(start_apply_run_action([success]), "continue")

    def test_foreign_per_row_claim_still_holds_when_key_is_unique(self):
        row = {
            "job_key": "plymouth",
            "status": "IN_PROGRESS",
            "claim_run_id": "R-other",
            "updated_at": "2026-09-15T10:00:00-04:00",
        }
        decision = attempt_claim_job(row, run_id="R-me", now=NOW)
        self.assertEqual(decision.result, "ALREADY_CLAIMED")


class TestSchema(unittest.TestCase):
    def test_named_writes_do_not_depend_on_confidence_index(self):
        headers = ["job_key", "status", "last_stage", "claim_run_id", "apply_url_confidence"]
        row = named_row(
            headers,
            {
                "job_key": "k",
                "status": "SKIP",
                "last_stage": "discovered",
                "claim_run_id": "",
                "apply_url_confidence": "",
            },
        )
        self.assertEqual(row[1], "SKIP")
        moved = ["apply_url_confidence", "status", "job_key"]
        moved_row = named_row(
            moved,
            {"job_key": "k", "status": "IN_PROGRESS", "apply_url_confidence": "none"},
        )
        self.assertEqual(moved_row[0], "none")
        self.assertEqual(moved_row[1], "IN_PROGRESS")
        self.assertEqual(moved_row[2], "k")

    def test_ready_fifo_is_not_apply_admission(self):
        operator = _operator()
        self.assertEqual(operator["legacy_ready_rows"]["disposition"], "inventory_only")
        self.assertTrue(operator["concurrency"]["one_job_key_one_row"])
        self.assertTrue(operator["concurrency"]["one_live_apply"])
        self.assertFalse(operator["queue_read"]["full_scan"])
        self.assertFalse(operator["skip_path"]["generate_resume_on_skip"])
        apply = apply_text()
        self.assertIn("Do not FIFO the Sheet READY_* backlog.", apply)
        self.assertNotIn("silent FIFO", apply)

    def test_scratch_tabs_are_banned(self):
        self.assertFalse(scratch_tab_permitted())
        self.assertTrue(tab_is_forbidden_scratch("scratch_scan_R20260915_0120"))
        self.assertTrue(tab_is_forbidden_scratch("scratch2_R20260915_0120"))
        self.assertTrue(tab_is_forbidden_scratch("scratch_recovery_R20260915_0520"))
        self.assertFalse(tab_is_forbidden_scratch("queue"))
        self.assertFalse(tab_is_forbidden_scratch("run_log"))
        apply = apply_text()
        self.assertIn("Do not create a Sheet tab named scratch", apply)
        self.assertIn(SHEET_QUERY_NA_REPEAT_KEY, apply)
        grok = grok_apply_text()
        self.assertIn("scratch", grok.lower())
        self.assertIn("Do not create grok_browser", grok)
        self.assertNotIn("acquire grok_browser", grok)


class TestLogging(unittest.TestCase):
    def test_duration_is_ended_minus_started(self):
        started = "2026-09-15T09:20:00-04:00"
        ended = "2026-09-15T09:52:00-04:00"
        self.assertEqual(run_duration_minutes(started, ended), 32)
        self.assertEqual(
            telemetry_duration_status(
                started_at=started,
                ended_at=ended,
                recorded_minutes=32,
            ),
            "ok",
        )
        self.assertEqual(
            telemetry_duration_status(
                started_at=started,
                ended_at=ended,
                recorded_minutes=85,
            ),
            TELEMETRY_INCONSISTENCY,
        )
        self.assertEqual(
            telemetry_duration_status(
                started_at=started,
                ended_at="",
                recorded_minutes=32,
            ),
            TELEMETRY_INCONSISTENCY,
        )
        self.assertEqual(
            run_duration_minutes(
                "2026-09-15T08:20:00-04:00",
                "2026-09-15T08:36:00-04:00",
            ),
            16,
        )

    def test_one_run_id_updates_existing_row(self):
        rows = [{"run_id": "R-20260915-0920", "result": "PARTIAL"}]
        plan = plan_run_log_write(rows, "R-20260915-0920")
        self.assertEqual(plan.action, "update")
        self.assertEqual(plan.row_index, 0)
        self.assertEqual(plan_run_log_write([], "R-20260915-1020").action, "append")
        dup = [
            {"run_id": "R-20260914-1120", "result": "SUCCESS"},
            {"run_id": "R-20260914-1120", "result": "FAILED"},
        ]
        self.assertEqual(plan_run_log_write(dup, "R-20260914-1120").action, "abort")

    def test_incident_id_query_is_today_only(self):
        self.assertEqual(incident_id_day_prefix("2026-09-15"), "INC-20260915-")
        existing = (
            "INC-20260914-099",
            "INC-20260915-012",
            "INC-20260915-013",
        )
        self.assertEqual(
            incident_ids_for_day(existing, "2026-09-15"),
            ("INC-20260915-012", "INC-20260915-013"),
        )

    def test_compile_writes_duration_and_one_apply_gate(self):
        apply = apply_text()
        self.assertIn("polar_policy.run_duration_minutes(started_at, ended_at)", apply)
        self.assertIn(TELEMETRY_INCONSISTENCY, apply)
        self.assertIn("polar_policy.start_apply_run_action", apply)
        self.assertIn("Do not acquire polar_browser. Do not create grok_browser.", apply)
        grok = grok_apply_text()
        self.assertIn("polar_policy.start_apply_run_action", grok)
        self.assertIn("polar_policy.run_duration_minutes(started_at, ended_at)", grok)


if __name__ == "__main__":
    unittest.main()
