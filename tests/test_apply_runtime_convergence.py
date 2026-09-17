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
    APPLY_AGENT_WORKFLOW,
    APPLY_WORKFLOW_NAMES,
    DUPLICATE_JOB_KEY_REPEAT_KEY,
    START_APPLY_RESUME,
    STALE_APPLY_CLOSE_NOTE,
    STALE_APPLY_CLOSE_RESULT,
    SHEET_QUERY_NA_REPEAT_KEY,
    TELEMETRY_INCONSISTENCY,
    agent_continuous_caps,
    apply_agent_partial_is_stale,
    daily_submit_quota_action,
    practice_share_stop_action,
    apply_run_is_live,
    apply_run_is_stale,
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
    stale_apply_close_fields,
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
        self.assertEqual(
            APPLY_WORKFLOW_NAMES,
            frozenset({"apply-ready-jobs", "apply-agent-jobs", "grok-apply-jobs"}),
        )
        live = {
            "run_id": "R-20260915-0816",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:16:00-04:00",
            "ended_at": "",
        }
        self.assertTrue(apply_run_is_live(live, now=NOW))
        self.assertFalse(apply_run_is_stale(live, now=NOW))
        self.assertEqual(start_apply_run_action([live], now=NOW), "NO_WORK")
        self.assertEqual(
            start_apply_run_action([live], this_run_id="R-20260915-0816", now=NOW),
            "continue",
        )
        grok_live = {
            "run_id": "G-20260915-105000",
            "workflow": "grok-apply-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:50:00-04:00",
            "ended_at": "",
        }
        self.assertEqual(start_apply_run_action([grok_live], now=NOW), "NO_WORK")
        self.assertEqual(live_apply_run_id([grok_live], now=NOW), "G-20260915-105000")
        agent_live = {
            "run_id": "R-20260915-0915",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:15:00-04:00",
            "ended_at": "",
        }
        self.assertEqual(start_apply_run_action([agent_live], now=NOW), "NO_WORK")
        self.assertEqual(live_apply_run_id([agent_live], now=NOW), "R-20260915-0915")
        closed_partial = {
            "run_id": "R-20260914-1631",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-14T16:31:00-04:00",
            "ended_at": "2026-09-14T17:02:08-04:00",
        }
        self.assertFalse(apply_run_is_live(closed_partial, now=NOW))
        self.assertEqual(start_apply_run_action([closed_partial], now=NOW), "continue")
        discover = {
            "run_id": "R-20260913-180123",
            "workflow": "discover-jobs-hourly",
            "result": "PARTIAL",
            "started_at": "2026-09-13T18:01:23-04:00",
            "ended_at": "",
        }
        self.assertFalse(apply_run_is_live(discover, now=NOW))
        success = {
            "run_id": "R-20260915-0920",
            "workflow": "apply-ready-jobs",
            "result": "SUCCESS",
            "ended_at": "2026-09-15T09:52:00-04:00",
        }
        self.assertEqual(start_apply_run_action([success], now=NOW), "continue")

    def test_stale_partial_closes_so_recovery_can_run(self):
        crashed = {
            "run_id": "R-20260915-0620",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T06:20:00-04:00",
            "ended_at": "",
            "notes": "browser disconnect",
        }
        self.assertTrue(apply_run_is_stale(crashed, now=NOW))
        self.assertFalse(apply_run_is_live(crashed, now=NOW))
        self.assertEqual(start_apply_run_action([crashed], now=NOW), "stale_close")
        fields = stale_apply_close_fields(crashed, now=NOW)
        self.assertEqual(fields["result"], STALE_APPLY_CLOSE_RESULT)
        self.assertEqual(fields["ended_at"], "2026-09-15T10:20:00-04:00")
        self.assertEqual(fields["duration_minutes"], "240")
        self.assertIn(STALE_APPLY_CLOSE_NOTE, fields["notes"])
        closed = {**crashed, **fields}
        self.assertFalse(apply_run_is_live(closed, now=NOW))
        self.assertFalse(apply_run_is_stale(closed, now=NOW))
        self.assertEqual(start_apply_run_action([closed], now=NOW), "continue")
        missing_start = {
            "run_id": "R-crash-no-start",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "",
            "ended_at": "",
        }
        self.assertTrue(apply_run_is_stale(missing_start, now=NOW))
        self.assertEqual(start_apply_run_action([missing_start], now=NOW), "stale_close")
        naive_start = {
            "run_id": "R-crash-naive-start",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T10:00:00",
            "ended_at": "",
        }
        self.assertTrue(apply_run_is_stale(naive_start, now=NOW))
        self.assertEqual(start_apply_run_action([naive_start], now=NOW), "stale_close")
        naive_fields = stale_apply_close_fields(naive_start, now=NOW)
        self.assertEqual(naive_fields["result"], STALE_APPLY_CLOSE_RESULT)
        self.assertEqual(naive_fields["ended_at"], "2026-09-15T10:20:00-04:00")
        self.assertNotIn("duration_minutes", naive_fields)
        self.assertIsNone(
            run_duration_minutes("2026-09-15T10:00:00", "2026-09-15T10:20:00-04:00")
        )

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
        self.assertIn("polar_policy.stale_apply_close_fields", grok)
        self.assertIn("polar_policy.run_duration_minutes(started_at, ended_at)", grok)
        learning = compile_grok()["workflows/grok-production-learning-daily.md"]
        self.assertIn("This routine is not an apply. Do not run polar_policy.start_apply_run_action.", learning)
        self.assertEqual(learning.count("start_apply_run_action"), 1)
        self.assertNotIn("If NO_WORK, write this run_id as NO_WORK", learning)
        self.assertIn("stale_apply_close_fields", apply)
        self.assertIn("stale_close", apply)

    def test_grok_apply_upserts_partial_after_stale_close(self):
        grok = grok_apply_text()
        self.assertNotIn("Otherwise upsert", grok)
        self.assertIn("Do not filter this QUERY to young started_at", grok)
        self.assertIn("every open apply PARTIAL with blank ended_at", grok)
        self.assertIn("including after stale_close", grok)
        self.assertIn(
            "Unless this run exited NO_WORK, upsert this run_id as PARTIAL",
            grok,
        )
        runtime = compile_grok()["runtime/GROKBOT_RUNTIME.md"]
        self.assertNotIn("Otherwise upsert", runtime)
        self.assertIn("including after stale_close", runtime)
        self.assertIn("Do not filter this QUERY to young started_at", runtime)
        learning = compile_grok()["workflows/grok-production-learning-daily.md"]
        self.assertIn(
            "This routine is not an apply. Do not run polar_policy.start_apply_run_action.",
            learning,
        )
        self.assertEqual(learning.count("start_apply_run_action"), 1)
        self.assertNotIn("Otherwise upsert", learning)
        self.assertNotIn("including after stale_close", learning)

    def test_polar_runtime_queries_all_open_apply_partials(self):
        polar_rt = (ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("every open apply PARTIAL with blank ended_at", polar_rt)
        self.assertIn("Do not filter this QUERY to young started_at", polar_rt)
        self.assertIn("including after stale_close", polar_rt)
        self.assertNotIn("blank ended_at younger than work_claim.ttl_minutes", polar_rt)
        self.assertNotIn("grok-apply-jobs", polar_rt)
        apply = apply_text()
        self.assertIn("Do not filter this QUERY to young started_at", apply)
        self.assertIn("every open apply PARTIAL", apply)
        self.assertIn("Immediately upsert a run_log row", apply)
        self.assertNotIn("this_workflow=apply-agent-jobs", apply)
        self.assertNotIn("If resume:", apply)


class TestAgentContinuousFollowOn(unittest.TestCase):
    def test_default_start_still_bounces_a_live_agent_row(self):
        agent_live = {
            "run_id": "R-20260915-0915",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:15:00-04:00",
            "ended_at": "",
        }
        self.assertEqual(start_apply_run_action([agent_live], now=NOW), "NO_WORK")

    def test_agent_path_resumes_same_polar_agent_run(self):
        agent_live = {
            "run_id": "R-20260915-0915",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:15:00-04:00",
            "ended_at": "",
        }
        self.assertEqual(
            start_apply_run_action(
                [agent_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            START_APPLY_RESUME,
        )

    def test_agent_path_does_not_attach_to_ready_or_grok(self):
        agent_live = {
            "run_id": "R-20260915-0915",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:15:00-04:00",
            "ended_at": "",
        }
        ready_live = {
            "run_id": "R-20260916-2320",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:16:00-04:00",
            "ended_at": "",
        }
        grok_live = {
            "run_id": "G-20260915-105000",
            "workflow": "grok-apply-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T09:50:00-04:00",
            "ended_at": "",
        }
        writing_agent = {
            "run_id": "R-20260915-0621",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T06:20:00-04:00",
            "ended_at": "",
        }
        ready_stale = {
            "run_id": "R-20260915-0620",
            "workflow": "apply-ready-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T06:20:00-04:00",
            "ended_at": "",
        }
        self.assertEqual(
            start_apply_run_action(
                [ready_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            "NO_WORK",
        )
        self.assertEqual(
            start_apply_run_action(
                [grok_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            "NO_WORK",
        )
        self.assertEqual(
            start_apply_run_action(
                [agent_live, ready_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            "NO_WORK",
        )
        self.assertEqual(
            start_apply_run_action(
                [agent_live, grok_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            "NO_WORK",
        )
        self.assertEqual(
            start_apply_run_action(
                [writing_agent, ready_live],
                this_workflow=APPLY_AGENT_WORKFLOW,
                last_writes_by_run_id={
                    "R-20260915-0621": "2026-09-15T10:00:00-04:00"
                },
                now=NOW,
            ),
            "NO_WORK",
        )
        self.assertEqual(
            start_apply_run_action(
                [agent_live, ready_stale],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            START_APPLY_RESUME,
        )

    def test_write_liveness_is_agent_path_only(self):
        old_agent = {
            "run_id": "R-20260915-0620",
            "workflow": "apply-agent-jobs",
            "result": "PARTIAL",
            "started_at": "2026-09-15T06:20:00-04:00",
            "ended_at": "",
        }
        self.assertTrue(apply_run_is_stale(old_agent, now=NOW))
        self.assertTrue(apply_agent_partial_is_stale(old_agent, now=NOW))
        self.assertFalse(
            apply_agent_partial_is_stale(
                old_agent,
                last_write_at="2026-09-15T10:00:00-04:00",
                now=NOW,
            )
        )
        self.assertEqual(start_apply_run_action([old_agent], now=NOW), "stale_close")
        self.assertEqual(
            start_apply_run_action(
                [old_agent],
                this_workflow=APPLY_AGENT_WORKFLOW,
                now=NOW,
            ),
            "stale_close",
        )
        self.assertEqual(
            start_apply_run_action(
                [old_agent],
                this_workflow=APPLY_AGENT_WORKFLOW,
                last_writes_by_run_id={"R-20260915-0620": "2026-09-15T10:00:00-04:00"},
                now=NOW,
            ),
            START_APPLY_RESUME,
        )

    def test_quota_uses_first_cap_not_owner_ceiling(self):
        caps = agent_continuous_caps()
        self.assertEqual(caps.owner_ceiling, 100)
        self.assertEqual(caps.first_enabled_cap, 3)
        self.assertLess(caps.first_enabled_cap, caps.owner_ceiling)
        self.assertEqual(daily_submit_quota_action(2, 0), "continue")
        self.assertEqual(daily_submit_quota_action(3, 0), "stop")
        self.assertEqual(daily_submit_quota_action(2, 1), "stop")
        self.assertEqual(daily_submit_quota_action(99, 0, cap=100), "continue")

    def test_practice_share_stop_after_submitted_exists(self):
        self.assertEqual(practice_share_stop_action(0, 0), "continue")
        self.assertEqual(practice_share_stop_action(4, 1), "continue")
        self.assertEqual(practice_share_stop_action(3, 1), "stop")


if __name__ == "__main__":
    unittest.main()
