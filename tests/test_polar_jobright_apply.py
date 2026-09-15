#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    abandon_application_on_email_otp,
    after_confirm_persistence_action,
    apply_entry_source,
    apply_run_caps,
    apply_run_counters,
    attempt_claim_job,
    autofill_action,
    autofill_corrections_note,
    autofill_owner,
    consider_jobright_card,
    considered_budget_exhausted,
    discover_is_apply_entry,
    do_not_use_simplify_copilot_autofill,
    email_verification_action,
    form_complexity,
    full_form_audit_permitted,
    full_queue_read_permitted,
    incident_learning_era,
    jobright_ack_action,
    known_autofill_failure_classes,
    legacy_ready_disposition,
    mailbox_unreadable_is_blocker,
    missing_references_action,
    missing_required_fact_action,
    native_resume_action,
    page_surface,
    post_autofill_checks,
    post_autofill_field_action,
    post_autofill_sidebar_is_proof,
    post_autofill_trust_source,
    post_autofill_trusted_classes,
    queue_read_scope,
    referral_field_action,
    select_apply_batch,
    select_next_apply_job,
    uncertain_submit_action,
    user_only_auth_steps,
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
        self.assertTrue(dup.consume_considered)
        self.assertTrue(dup.continue_run)

        applied = consider_jobright_card(already_applied_on_jobright=True)
        self.assertEqual(applied.action, "skip_applied")
        self.assertTrue(applied.consume_considered)
        self.assertTrue(applied.continue_run)

        conflict = consider_jobright_card(hard_fact_conflict=True)
        self.assertEqual(conflict.action, "skip_hard_fact")
        self.assertTrue(conflict.consume_considered)
        self.assertTrue(conflict.continue_run)

        blocked = consider_jobright_card(sheet_status="BLOCKED")
        self.assertEqual(blocked.action, "skip_blocked")
        self.assertTrue(blocked.consume_considered)
        self.assertTrue(blocked.continue_run)

        # Polar production table is unchanged: a REVIEW_READY hold Polar
        # re-sees on recommendations is a duplicate skip that counts considered.
        held = consider_jobright_card(sheet_status="REVIEW_READY")
        self.assertEqual(held.action, "skip_duplicate")
        self.assertTrue(held.consume_considered)
        self.assertTrue(held.continue_run)
        self.assertEqual(
            consider_jobright_card(sheet_status="REVIEW_READY", executor="polar"),
            held,
        )
        for status in ("SUBMITTED", "BLOCKED", "IN_PROGRESS", "SUBMISSION_UNKNOWN", "SKIP"):
            polar = consider_jobright_card(sheet_status=status)
            self.assertTrue(polar.consume_considered, status)
            self.assertEqual(
                consider_jobright_card(sheet_status=status, executor="grok"), polar, status
            )

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
        self.assertIn("Fence Simplify probe/fallback, Copilot-as-autofill, READY_* FIFO", learning)
        self.assertIn("Do not paste architecture audits into this report.", learning)
        self.assertIn("Do not dump the READY_* backlog.", learning)
        discover = render_workflow("discover-jobs-hourly", operator)
        self.assertIn("retired_from_apply_path", discover)
        self.assertIn("apply_path: false", discover)
        self.assertNotIn("set READY_REGULAR or READY_PRIORITY using section D", discover)
        apply = render_workflow("apply-ready-jobs", operator)
        self.assertIn("entry: jobright_recommendations", apply)
        self.assertIn("sheet_queue_is_prerequisite: false", apply)
        self.assertNotIn("Never click Jobright APPLY WITH AUTOFILL.", apply)
        self.assertIn("Apply with Autofill", apply)
        self.assertIn("Skip closed, duplicate, Applied, or hard-fact-conflict. Count considered. Continue.", apply)
        self.assertIn(
            "If confirm_claim_readback is not CLAIMED, add the key to seen and continue. That miss does not consume considered.",
            apply,
        )
        self.assertIn("After a successful new-card claim, increment considered.", apply)
        self.assertIn(
            "If that gate is false, do not Submit. Mark BLOCKED. Continue.",
            apply,
        )
        self.assertFalse(operator["schedules"]["discover_jobs_hourly"]["enabled"])
        self.assertIn("scope: targeted", apply)
        self.assertIn("full_scan: false", apply)
        self.assertIn("trust: form_dom", apply)
        self.assertIn("readable: true", apply)
        self.assertIn("read_application_outlook", apply)
        self.assertIn("abandon_on_email_otp: false", apply)
        self.assertNotIn("Missing Copilot is not OWNER_ACTION_REQUIRED", apply)
        self.assertNotIn("simplify_attempted or simplify_fallback_count. Increment", apply)


class TestJobrightEraContract(unittest.TestCase):
    def test_queue_reads_are_targeted(self):
        self.assertEqual(queue_read_scope(), "targeted")
        self.assertFalse(full_queue_read_permitted())

    def test_form_dom_beats_sidebar(self):
        self.assertEqual(post_autofill_trust_source(), "form_dom")
        self.assertFalse(post_autofill_sidebar_is_proof())
        self.assertEqual(referral_field_action(filled_value="Event"), "clear_invented")
        self.assertEqual(referral_field_action(filled_value=""), "leave_blank")


class TestFastValidationPass(unittest.TestCase):
    def test_five_high_risk_classes_only(self):
        self.assertFalse(full_form_audit_permitted())
        self.assertEqual(
            post_autofill_checks(),
            (
                "identity",
                "work_authorization",
                "eligibility_critical",
                "required_empty_or_error",
                "required_legal_compliance",
            ),
        )
        self.assertNotIn("contact", post_autofill_checks())
        self.assertNotIn("eeo_demographics", post_autofill_checks())
        self.assertEqual(
            post_autofill_trusted_classes(),
            (
                "eeo_demographics",
                "phone_address_formatting",
                "resume_filename",
                "populated_education_employment",
                "routine_non_material",
            ),
        )
        self.assertIn("nickname_on_legal_first_name", known_autofill_failure_classes())
        self.assertIn("sponsorship_yes_on_future_sponsorship_widget", known_autofill_failure_classes())
        self.assertNotIn("sponsorship_no_on_future_sponsorship_widget", known_autofill_failure_classes())

    def test_populated_routine_widgets_are_trusted(self):
        for klass in post_autofill_trusted_classes():
            self.assertEqual(
                post_autofill_field_action(field_class=klass, required=True, populated=True),
                "trust_skip",
                klass,
            )
        self.assertEqual(
            post_autofill_field_action(field_class="eeo_demographics", required=False, populated=False),
            "leave_optional_blank",
        )

    def test_high_risk_classes_are_verified(self):
        for klass in post_autofill_checks():
            self.assertEqual(
                post_autofill_field_action(field_class=klass, required=True, populated=True),
                "verify_against_facts",
                klass,
            )

    def test_empty_error_and_known_failures_are_repaired_not_invented(self):
        self.assertEqual(
            post_autofill_field_action(field_class="routine_non_material", required=True, populated=False),
            "fill_from_facts_or_block",
        )
        self.assertEqual(
            post_autofill_field_action(field_class="routine_non_material", required=True, populated=True, has_error=True),
            "repair_from_facts",
        )
        self.assertEqual(
            post_autofill_field_action(field_class="identity", required=True, populated=True, known_failure=True),
            "repair_from_facts",
        )
        self.assertEqual(
            post_autofill_field_action(field_class="eeo_demographics", required=False, populated=True, conflicts_with_fact=True),
            "repair_from_facts",
        )

    def test_every_classified_auth_kind_is_reread_and_answered_from_facts(self):
        from polar_policy import (
            AUTH_QUESTION_KINDS,
            auth_form_action,
            classify_auth_question,
            load_auth_facts,
            work_authorization_verify_kinds,
        )

        kinds = work_authorization_verify_kinds()
        self.assertEqual(set(kinds), set(AUTH_QUESTION_KINDS) - {"unknown"})
        self.assertEqual(len(kinds), len(set(kinds)))
        # A populated work-authorization widget is verified, never trusted.
        self.assertEqual(
            post_autofill_field_action(field_class="work_authorization", required=True, populated=True),
            "verify_against_facts",
        )
        self.assertEqual(
            post_autofill_field_action(field_class="work_authorization", required=False, populated=True),
            "verify_against_facts",
        )
        facts = load_auth_facts()
        # The five kinds Bugbot flagged, plus the wording each one comes from.
        expected = {
            "Will you now or in the future require visa sponsorship?": ("future_sponsorship", "answer_no"),
            "Do you require sponsorship to begin employment?": ("sponsorship_to_begin", "leave_unresolved"),
            "Do you have an EAD?": ("ead_possession", "answer_no"),
            "Has your OPT been approved?": ("opt_approval", "answer_no"),
            "Will you be eligible for OPT?": ("opt_eligibility", "answer_yes"),
            "Are you legally eligible to begin employment immediately?": ("authorization_at_start", "answer_yes"),
            "Are you currently authorized to work in the U.S.?": ("current_work_authorization", "leave_unresolved"),
            "Are you an F-1 student?": ("status_yes_no", "answer_yes"),
            "Are you authorized to work without sponsorship?": ("authorization_without_sponsorship", "leave_unresolved"),
        }
        for prompt, (kind, required_action) in expected.items():
            self.assertEqual(classify_auth_question(prompt), kind, prompt)
            self.assertIn(kind, kinds, prompt)
            action, _reason = auth_form_action(widget_text=prompt, required=True, facts=facts)
            self.assertEqual(action, required_action, prompt)
            optional_action, optional_reason = auth_form_action(widget_text=prompt, required=False, facts=facts)
            self.assertEqual(optional_action, "leave_blank", prompt)
            self.assertEqual(optional_reason, "optional_identity_field", prompt)
        country_action, country_reason = auth_form_action(
            widget_text="Do you require sponsorship for the United Kingdom, Germany, or Serbia?",
            required=True,
            names_non_us_countries_only=True,
            facts=facts,
        )
        self.assertEqual((country_action, country_reason), ("leave_unresolved", "country_specific_sponsorship"))
        self.assertIn("country_specific_sponsorship", kinds)

    def test_routine_is_default_complexity(self):
        self.assertEqual(form_complexity(), "routine")
        self.assertEqual(form_complexity("greenhouse"), "routine")
        self.assertEqual(form_complexity("workday_or_eightfold_multistep"), "complex")
        self.assertEqual(form_complexity("account_or_otp_required"), "complex")
        self.assertEqual(form_complexity("nontrivial_writing"), "complex")

    def test_corrections_note_is_minimal(self):
        self.assertEqual(autofill_corrections_note([]), "")
        self.assertEqual(
            autofill_corrections_note(["nickname_on_legal_first_name", "nickname_on_legal_first_name", "invented_referral"]),
            "autofill_corrections=nickname_on_legal_first_name,invented_referral",
        )

    def test_outlook_mailbox_is_recoverable(self):
        self.assertEqual(email_verification_action(), "read_application_outlook")
        self.assertFalse(mailbox_unreadable_is_blocker())
        self.assertFalse(abandon_application_on_email_otp())
        self.assertIn("sms_on_mac_if_outlook_has_no_code", user_only_auth_steps())

    def test_simplify_counters_stay_blank(self):
        fields = apply_run_counters(considered=1, forms_reached=1)
        self.assertEqual(fields["simplify_attempted"], "")
        self.assertEqual(fields["simplify_fallback_count"], "")

    def test_pre_jobright_incidents_are_fenced(self):
        self.assertEqual(
            incident_learning_era(repeat_key="simplify_copilot_missing"),
            "pre_jobright",
        )
        self.assertEqual(
            incident_learning_era(time_lost_category="SIMPLIFY"),
            "pre_jobright",
        )
        self.assertEqual(
            incident_learning_era(summary="IBM funnel probe on old discovery"),
            "pre_jobright",
        )
        self.assertEqual(
            incident_learning_era(workflow_version="2026-09-14.perfect-resume+abc"),
            "pre_jobright",
        )
        self.assertEqual(
            incident_learning_era(
                summary="Jobright extension invented Event referral",
                workflow_version="2026-09-15.jobright-era+abc",
            ),
            "jobright",
        )


if __name__ == "__main__":
    unittest.main()
