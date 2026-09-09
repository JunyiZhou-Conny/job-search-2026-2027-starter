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
    INCIDENT_CATEGORIES,
    QUEUE_COLUMNS,
    REQUIRED_QUEUE_READBACK,
    TIME_LOST_CATEGORIES,
    apply_run_caps,
    closed_posting_action,
    control_row_is_writable,
    control_write_persisted,
    decide_lease,
    degree_level_hard_skip,
    document_availability,
    header_map,
    incident_ids_are_unique,
    lease_checkpoint_notes,
    named_row,
    next_incident_id,
    parse_lease_checkpoint,
    pick_canonical_requisition_row,
    plan_control_write,
    plan_run_log_write,
    priority_submit_permitted,
    readback_fields,
    release_lease,
    requisition_identity,
    resolve_apply_run_caps,
    sanitize_learning_text,
    select_apply_batch,
    sibling_job_keys,
    sponsorship_form_action,
    workflow_version,
    writing_log_status,
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


class TestApplyRunCaps(unittest.TestCase):
    def test_live_repo_caps_are_one_shared_pool(self):
        caps = apply_run_caps(ROOT)
        self.assertEqual(caps.max_new_jobs, 3)
        self.assertEqual(caps.reserved_priority_slots, 1)
        self.assertEqual(caps.max_regular_submissions_per_local_day, 10)
        self.assertTrue(caps.prioritized_auto_submit)
        batch = select_apply_batch(
            [
                {"job_key": "p1", "status": "READY_PRIORITY"},
                {"job_key": "r1", "status": "READY_REGULAR"},
                {"job_key": "r2", "status": "READY_REGULAR"},
                {"job_key": "r3", "status": "READY_REGULAR"},
            ],
            root=ROOT,
        )
        self.assertEqual(len(batch.priority) + len(batch.regular), caps.max_new_jobs)
        self.assertEqual(batch.priority, ("p1",))
        self.assertEqual(batch.regular, ("r1", "r2"))

    def test_divergent_caps_are_rejected(self):
        canary = {
            "max_jobs_per_run": 3,
            "max_regular_jobs_per_run": 3,
            "reserved_priority_slots_per_run": 1,
            "max_regular_submissions_per_local_day": 10,
            "prioritized_auto_submit": True,
        }
        polar_local = {
            "regular_submit_cap_per_run": 3,
            "regular_submit_cap_per_local_day": 10,
            "prioritized_auto_submit": True,
        }
        with self.assertRaises(ValueError):
            resolve_apply_run_caps(
                {**canary, "max_regular_jobs_per_run": 4},
                polar_local,
            )
        with self.assertRaises(ValueError):
            resolve_apply_run_caps(
                canary,
                {**polar_local, "regular_submit_cap_per_run": 4},
            )


class TestPrioritySubmitGate(unittest.TestCase):
    def setUp(self):
        self.question = "Why do you want to work here?"
        self.complete_row = {
            "job_key": "prio-1",
            "exact_question": self.question,
            "answer_used": "I want to ship the product with the field team.",
            "evidence_note": "evidence_bank: field_team_project",
        }

    def _decide(self, **kwargs):
        payload = {
            "weight": "prioritized",
            "plane": "polar_local",
            "prioritized_auto_submit": True,
            "job_key": "prio-1",
            "custom_questions": [self.question],
            "writing_rows": [self.complete_row],
        }
        payload.update(kwargs)
        return priority_submit_permitted(**payload)

    def test_empty_log_blocks_when_questions_exist(self):
        decision = self._decide(writing_rows=[])
        self.assertFalse(decision.permitted)
        self.assertEqual(decision.reason, "writing_log_missing_question")

    def test_logged_question_and_answer_permits(self):
        decision = self._decide()
        self.assertTrue(decision.permitted)
        self.assertEqual(decision.reason, "writing_log_complete")

    def test_blank_answer_blocks(self):
        decision = self._decide(
            writing_rows=[
                {
                    **self.complete_row,
                    "answer_used": "   ",
                }
            ]
        )
        self.assertFalse(decision.permitted)
        self.assertEqual(decision.reason, "writing_log_blank_answer")

    def test_missing_evidence_note_blocks(self):
        decision = self._decide(
            writing_rows=[
                {
                    **self.complete_row,
                    "evidence_note": "",
                }
            ]
        )
        self.assertFalse(decision.permitted)
        self.assertEqual(decision.reason, "writing_log_missing_evidence")

    def test_other_job_log_does_not_count(self):
        decision = self._decide(
            writing_rows=[{**self.complete_row, "job_key": "other"}]
        )
        self.assertFalse(decision.permitted)
        self.assertEqual(decision.reason, "writing_log_missing_question")

    def test_no_custom_questions_permits(self):
        decision = writing_log_status(
            job_key="prio-1",
            custom_questions=[],
            writing_rows=[],
        )
        self.assertTrue(decision.permitted)
        self.assertEqual(decision.reason, "no_custom_questions")

    def test_cloud_priority_stays_review_first(self):
        decision = self._decide(plane="cursor_cloud")
        self.assertFalse(decision.permitted)
        self.assertEqual(decision.reason, "cursor_cloud_prioritized_needs_review_packet")

    def test_regular_weight_skips_this_gate(self):
        decision = self._decide(weight="regular", writing_rows=[])
        self.assertTrue(decision.permitted)
        self.assertEqual(decision.reason, "regular_weight_does_not_use_this_gate")


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

    def test_incident_categories_include_missing_fact(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(tuple(operator["incident_categories"]), INCIDENT_CATEGORIES)
        self.assertIn("MISSING_FACT", INCIDENT_CATEGORIES)
        self.assertGreater(
            INCIDENT_CATEGORIES.index("MISSING_FACT"),
            INCIDENT_CATEGORIES.index("MISSING_DOCUMENT"),
        )


class TestControlKeyUpsert(unittest.TestCase):
    def test_canary_must_not_overwrite_browser_lock(self):
        rows = [
            {
                "key": "polar_browser",
                "owner_run_id": "R-20260909-0420",
                "notes": "",
            }
        ]
        self.assertFalse(control_row_is_writable(rows[0], "github_write_canary"))
        plan = plan_control_write(rows, "github_write_canary")
        self.assertEqual(plan.action, "append")
        self.assertIsNone(plan.row_index)

    def test_empty_looking_lock_row_is_still_protected(self):
        row = {"key": "polar_browser", "owner_run_id": "", "notes": ""}
        self.assertFalse(control_row_is_writable(row, "github_write_canary"))

    def test_persisted_canary_keeps_browser_lock(self):
        before = [
            {"key": "polar_browser", "owner_run_id": "R-1", "notes": "checkpoint job_key=abc last_stage=form_filled"},
        ]
        after_bad = [
            {"key": "github_write_canary", "owner_run_id": "", "notes": "success"},
        ]
        self.assertFalse(
            control_write_persisted(
                after_bad,
                key="github_write_canary",
                intended={"key": "github_write_canary", "notes": "success"},
                protected_keys=("polar_browser",),
                before_rows=before,
            )
        )
        after_good = [
            {"key": "polar_browser", "owner_run_id": "R-1", "notes": "checkpoint job_key=abc last_stage=form_filled"},
            {"key": "github_write_canary", "owner_run_id": "", "notes": "success; https://example.com/114"},
        ]
        self.assertTrue(
            control_write_persisted(
                after_good,
                key="github_write_canary",
                intended={
                    "key": "github_write_canary",
                    "notes": "success; https://example.com/114",
                },
                protected_keys=("polar_browser",),
                before_rows=before,
            )
        )


class TestCrashCheckpoint(unittest.TestCase):
    def test_checkpoint_round_trip(self):
        notes = lease_checkpoint_notes("uber-301056", "application_open")
        self.assertEqual(parse_lease_checkpoint(notes), ("uber-301056", "application_open"))

    def test_run_log_upserts_same_run_id(self):
        rows = [{"run_id": "R-20260909-0420", "result": "PARTIAL"}]
        plan = plan_run_log_write(rows, "R-20260909-0420")
        self.assertEqual(plan.action, "update")
        self.assertEqual(plan.row_index, 0)
        self.assertEqual(plan_run_log_write([], "R-20260909-0420").action, "append")


class TestIncidentIds(unittest.TestCase):
    def test_mixed_widths_and_duplicate_do_not_reuse(self):
        existing = ["INC-20260909-001", "INC-20260909-01", "INC-20260909-003", "INC-20260909-003"]
        self.assertFalse(incident_ids_are_unique(existing))
        self.assertFalse(incident_ids_are_unique(["INC-20260909-001", "INC-20260909-01"]))
        self.assertEqual(next_incident_id(existing, "2026-09-09"), "INC-20260909-002")

    def test_next_id_after_three_is_four(self):
        existing = ["INC-20260909-001", "INC-20260909-002", "INC-20260909-003"]
        self.assertEqual(next_incident_id(existing, "20260909"), "INC-20260909-004")
        self.assertTrue(incident_ids_are_unique(existing))


class TestDegreeLevelGate(unittest.TestCase):
    def test_phd_only_full_jd_is_skip(self):
        self.assertEqual(
            degree_level_hard_skip("This internship is PhD students only."),
            "phd_only",
        )

    def test_undergrad_only_full_jd_is_skip(self):
        self.assertEqual(
            degree_level_hard_skip("Current undergraduate students only may apply."),
            "undergrad_only",
        )

    def test_pursuing_a_degree_is_not_a_skip(self):
        self.assertIsNone(degree_level_hard_skip("Must be currently pursuing a degree."))

    def test_phd_preferred_is_not_a_skip(self):
        self.assertIsNone(degree_level_hard_skip("PhD preferred. Master's students are welcome."))

    def test_phd_and_masters_is_not_a_skip(self):
        self.assertIsNone(
            degree_level_hard_skip("This position is for PhD and Master's students.")
        )


class TestClosedPostingAndSponsorship(unittest.TestCase):
    def test_removed_posting_does_not_open_a_sibling(self):
        self.assertEqual(closed_posting_action("This requisition has been removed"), "skip_no_sibling")
        self.assertEqual(closed_posting_action("404"), "skip_no_sibling")
        self.assertEqual(closed_posting_action("Apply now"), "continue")

    def test_explicit_f1_instruction_overrides_standing_no(self):
        action, reason = sponsorship_form_action(
            widget_text="Will you require visa sponsorship now or in the future?",
            explicit_status_instruction="F-1, J-1, or M-1 holders must answer Yes",
        )
        self.assertEqual(action, "answer_yes")
        self.assertEqual(reason, "explicit_status_instruction")

    def test_standing_broad_widget_stays_no(self):
        action, reason = sponsorship_form_action(
            widget_text="Will you now or in the future require visa sponsorship?"
        )
        self.assertEqual(action, "answer_no")
        self.assertEqual(reason, "standing_visa_sponsorship")

    def test_work_authorization_wording_stays_unresolved(self):
        action, reason = sponsorship_form_action(
            widget_text="Will you now or in the future require work authorization to work in the U.S.?"
        )
        self.assertEqual(action, "leave_unresolved")
        self.assertEqual(reason, "work_authorization_wording")

    def test_country_list_stays_unresolved(self):
        action, reason = sponsorship_form_action(
            widget_text="Does HPE sponsor in the United Kingdom or Germany?",
            names_non_us_countries_only=True,
        )
        self.assertEqual(action, "leave_unresolved")
        self.assertEqual(reason, "country_specific_sponsorship")

    def test_f1_welcome_without_yes_no_keeps_standing_no(self):
        action, reason = sponsorship_form_action(
            widget_text="Will you now or in the future require visa sponsorship?",
            explicit_status_instruction="F-1 students are welcome to apply.",
        )
        self.assertEqual(action, "answer_no")
        self.assertEqual(reason, "standing_visa_sponsorship")

    def test_unclear_f1_select_instruction_stays_unresolved(self):
        action, reason = sponsorship_form_action(
            widget_text="Will you now or in the future require visa sponsorship?",
            explicit_status_instruction="F-1 holders must select the first option.",
        )
        self.assertEqual(action, "leave_unresolved")
        self.assertEqual(reason, "explicit_status_instruction_unclear")


if __name__ == "__main__":
    unittest.main()
