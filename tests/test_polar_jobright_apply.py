#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    after_confirm_persistence_action,
    apply_entry_source,
    apply_run_caps,
    apply_run_counters,
    attempt_claim_job,
    autofill_action,
    autofill_owner,
    consider_jobright_card,
    considered_budget_exhausted,
    discover_is_apply_entry,
    do_not_use_simplify_copilot_autofill,
    jobright_ack_action,
    legacy_ready_disposition,
    missing_references_action,
    missing_required_fact_action,
    native_resume_action,
    page_surface,
    select_apply_batch,
    select_next_apply_job,
    uncertain_submit_action,
)
from polar_workflows import render_workflow  # noqa: E402

NOW = datetime(2026, 9, 14, 15, 30, 0)


class TestJobrightFirstEntry(unittest.TestCase):
    def test_apply_starts_without_ready_queue(self):
        self.assertEqual(apply_entry_source(), "jobright_recommendations")
        self.assertFalse(discover_is_apply_entry())
        self.assertIsNone(select_next_apply_job([]))
        batch = select_apply_batch(
            [
                {"job_key": "p1", "status": "READY_PRIORITY"},
                {"job_key": "r1", "status": "READY_REGULAR"},
                {"job_key": "r2", "status": "READY_REGULAR"},
            ],
            max_new_jobs=3,
        )
        self.assertEqual(batch.recovery, ())
        self.assertEqual(batch.priority, ())
        self.assertEqual(batch.regular, ())

    def test_legacy_ready_is_inventory_not_fifo(self):
        self.assertEqual(legacy_ready_disposition("READY_REGULAR"), "inventory_only")
        self.assertEqual(legacy_ready_disposition("READY_PRIORITY"), "inventory_only")
        self.assertEqual(legacy_ready_disposition("SUBMISSION_UNKNOWN"), "recover")
        self.assertEqual(legacy_ready_disposition("IN_PROGRESS"), "recover")
        self.assertEqual(legacy_ready_disposition("NEW"), "ignore")

    def test_recovery_still_wins_over_ready_backlog(self):
        rows = [
            {"job_key": "u1", "status": "SUBMISSION_UNKNOWN"},
            {"job_key": "old", "status": "IN_PROGRESS", "updated_at": "2026-09-08T10:00:00"},
            {"job_key": "p1", "status": "READY_PRIORITY"},
        ]
        batch = select_apply_batch(rows, max_new_jobs=3)
        self.assertEqual(batch.recovery, ("u1", "old"))
        self.assertEqual(batch.priority, ())
        self.assertEqual(batch.regular, ())


class TestSkipAndContinue(unittest.TestCase):
    def test_closed_and_dup_consume_considered_and_continue(self):
        closed = consider_jobright_card(closed=True)
        self.assertEqual(closed.action, "skip_closed")
        self.assertTrue(closed.consume_considered)
        self.assertTrue(closed.continue_run)

        dup = consider_jobright_card(section_k_hit=True)
        self.assertEqual(dup.action, "skip_duplicate")
        self.assertTrue(dup.continue_run)

        applied = consider_jobright_card(already_applied_on_jobright=True)
        self.assertEqual(applied.action, "skip_applied")
        self.assertTrue(applied.continue_run)

        conflict = consider_jobright_card(hard_fact_conflict=True)
        self.assertEqual(conflict.action, "skip_hard_fact")
        self.assertTrue(conflict.continue_run)

        admit = consider_jobright_card()
        self.assertEqual(admit.action, "admit")
        self.assertFalse(admit.consume_considered)
        self.assertTrue(admit.continue_run)
        self.assertFalse(considered_budget_exhausted(2, max_considered=3))
        self.assertTrue(considered_budget_exhausted(3, max_considered=3))


class TestLandingVsFormAutofill(unittest.TestCase):
    def test_landing_is_not_the_form(self):
        self.assertEqual(page_surface("application_form"), "form")
        self.assertEqual(page_surface("login_signup"), "login")
        self.assertEqual(page_surface("jd_landing"), "landing")
        self.assertEqual(page_surface("no_fillable_form_exists"), "investigate")

    def test_autofill_once_on_real_form_only(self):
        self.assertEqual(autofill_owner(), "jobright_extension")
        self.assertTrue(do_not_use_simplify_copilot_autofill())
        self.assertEqual(
            autofill_action(page_kind="application_form", already_autofilled=False),
            "autofill_once",
        )
        self.assertEqual(
            autofill_action(page_kind="application_form", already_autofilled=True),
            "skip_already_done",
        )
        self.assertEqual(
            autofill_action(page_kind="no_fillable_form_exists", already_autofilled=False),
            "investigate_not_unsupported",
        )
        self.assertEqual(
            autofill_action(page_kind="login_signup", already_autofilled=False),
            "investigate_not_unsupported",
        )


class TestResumeAndFacts(unittest.TestCase):
    def test_generated_or_911_is_used(self):
        self.assertEqual(
            native_resume_action(
                native_widget_has_file=True,
                perfect_resume_accessible=True,
                visible_filename="generated_resume.pdf",
                generated_resume_available=True,
            ),
            "keep_visible_file",
        )
        self.assertEqual(
            native_resume_action(
                native_widget_has_file=False,
                perfect_resume_accessible=True,
                generated_resume_available=True,
            ),
            "attach_generated_resume",
        )
        self.assertEqual(
            native_resume_action(
                native_widget_has_file=False,
                perfect_resume_accessible=True,
                generated_resume_available=False,
            ),
            "attach_perfect_resume",
        )
        self.assertEqual(
            native_resume_action(
                native_widget_has_file=True,
                perfect_resume_accessible=True,
                visible_filename="ai_infra_v1.pdf",
                generated_resume_available=True,
            ),
            "replace_with_generated_resume",
        )

    def test_missing_facts_do_not_fabricate(self):
        self.assertEqual(missing_required_fact_action(), "leave_unresolved_continue")
        self.assertEqual(missing_references_action(), "record_and_continue")


class TestSubmitSafety(unittest.TestCase):
    def test_uncertain_submit_does_not_retry(self):
        self.assertEqual(uncertain_submit_action(), "submission_unknown_no_retry")

    def test_sheet_fail_after_confirm_does_not_resubmit(self):
        self.assertEqual(
            after_confirm_persistence_action(sheet_write_ok=True),
            "persist",
        )
        self.assertEqual(
            after_confirm_persistence_action(sheet_write_ok=False),
            "repair_do_not_resubmit",
        )

    def test_jobright_ack_only_after_employer_confirm(self):
        self.assertEqual(
            jobright_ack_action(
                employer_page_confirmation=True,
                submit_clicked=True,
            ),
            "ack_i_applied",
        )
        self.assertEqual(
            jobright_ack_action(
                employer_page_confirmation=False,
                submit_clicked=True,
            ),
            "do_not_ack",
        )
        self.assertEqual(
            jobright_ack_action(
                employer_page_confirmation=True,
                submit_clicked=False,
            ),
            "do_not_ack",
        )

    def test_new_row_is_claimable_from_jobright_card(self):
        decision = attempt_claim_job(
            {"job_key": "jr-1", "status": "NEW", "attempt_count": "0"},
            run_id="R-1",
            now=NOW,
        )
        self.assertEqual(decision.result, "CLAIMED")
        self.assertEqual(decision.prior_status, "NEW")


class TestLearningAndDiscoverPath(unittest.TestCase):
    def test_counters_map_onto_existing_run_log(self):
        caps = apply_run_caps(ROOT)
        self.assertEqual(caps.max_considered, 3)
        self.assertEqual(caps.reserved_priority_slots, 0)
        fields = apply_run_counters(
            considered=3,
            forms_reached=1,
            confirmed_regular=1,
            skipped=2,
        )
        self.assertEqual(fields["jobs_seen"], "3")
        self.assertEqual(fields["jobs_attempted"], "1")
        self.assertEqual(fields["submitted_regular"], "1")
        self.assertEqual(fields["skipped"], "2")

    def test_learning_still_sees_outcomes_and_forbids_old_entry(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        learning = render_workflow("production-learning-daily", operator)
        self.assertIn("run_log, incident_log, writing_log, and queue", learning)
        self.assertIn("Do not recommend restoring discover-jobs-hourly as apply entry.", learning)
        discover = render_workflow("discover-jobs-hourly", operator)
        self.assertIn("retired_from_apply_path", discover)
        self.assertIn("apply_path: false", discover)
        self.assertNotIn("set READY_REGULAR or READY_PRIORITY using section D", discover)
        apply = render_workflow("apply-ready-jobs", operator)
        self.assertIn("entry: jobright_recommendations", apply)
        self.assertIn("sheet_queue_is_prerequisite: false", apply)
        self.assertNotIn("Never click Jobright APPLY WITH AUTOFILL.", apply)
        self.assertIn("Apply with Autofill", apply)
        self.assertFalse(operator["schedules"]["discover_jobs_hourly"]["enabled"])


if __name__ == "__main__":
    unittest.main()
