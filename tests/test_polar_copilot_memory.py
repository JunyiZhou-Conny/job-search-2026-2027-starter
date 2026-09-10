#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    COPILOT_REPEAT_KEY,
    ENV_SIMPLIFY_KEY,
    LEASE_KEY,
    LOCAL_PREFERENCES_PATH,
    RUN_LOG_RESULTS,
    assign_preference_ids,
    candidate_survives_resolution,
    classify_preference_entry,
    compact_preferences_markdown,
    control_write_persisted,
    copilot_allows_apply,
    copilot_state,
    CopilotObservation,
    env_simplify_control_fields,
    format_env_simplify_notes,
    local_overrides_github,
    missing_copilot_run_result,
    missing_copilot_should_release_lease,
    parse_env_simplify_notes,
    plan_control_write,
    preference_conflicts_github,
    preference_export_mode,
    PreferenceCandidate,
    PreferenceDeltaRow,
    PreferenceResolution,
    export_retains_candidate,
    parse_pending_candidates,
    proposed_github_destination,
    reconcile_preference_candidates,
    render_preferences_delta,
    restore_queue_after_copilot_miss,
    simplify_jobs_session_is_copilot_proof,
    winning_memory_source,
)


class TestCopilotPreflight(unittest.TestCase):
    def test_present_ui_allows_apply(self):
        state = copilot_state(
            CopilotObservation(
                employer_page_copilot_ui=True,
                simplify_jobs_session=False,
                evidence="sidebar Autofill This Page",
            )
        )
        self.assertEqual(state, "PRESENT")
        self.assertTrue(copilot_allows_apply(state))

    def test_missing_ui_forbids_manual_fallback(self):
        state = copilot_state(
            CopilotObservation(
                employer_page_copilot_ui=False,
                simplify_jobs_session=True,
                evidence="no Copilot sidebar on Workday apply page",
            )
        )
        self.assertEqual(state, "MISSING")
        self.assertFalse(copilot_allows_apply(state))

    def test_simplify_jobs_login_is_not_proof(self):
        self.assertFalse(simplify_jobs_session_is_copilot_proof(True))
        self.assertFalse(simplify_jobs_session_is_copilot_proof(False))

    def test_unknown_without_evidence(self):
        state = copilot_state(
            CopilotObservation(
                employer_page_copilot_ui=False,
                simplify_jobs_session=False,
                evidence="",
            )
        )
        self.assertEqual(state, "UNKNOWN")
        self.assertFalse(copilot_allows_apply(state))

    def test_missing_is_environment_blocker_not_job_block(self):
        restore = restore_queue_after_copilot_miss(
            ready_status="READY_PRIORITY",
            attempt_count_before_run=2,
        )
        self.assertEqual(restore.status, "READY_PRIORITY")
        self.assertEqual(restore.attempt_count, 2)
        self.assertFalse(restore.consume_job)
        self.assertEqual(missing_copilot_run_result(), "OWNER_ACTION_REQUIRED")
        self.assertIn("OWNER_ACTION_REQUIRED", RUN_LOG_RESULTS)
        self.assertTrue(missing_copilot_should_release_lease())
        self.assertEqual(COPILOT_REPEAT_KEY, "simplify_copilot_missing")

    def test_restore_rejects_blocked_status(self):
        with self.assertRaises(ValueError):
            restore_queue_after_copilot_miss(
                ready_status="BLOCKED",
                attempt_count_before_run=1,
            )

    def test_control_row_is_not_the_browser_lease(self):
        fields = env_simplify_control_fields(
            run_id="run-9",
            workflow="apply-ready-jobs",
            checked_at="2026-09-10T02:00:00",
            state="MISSING",
            evidence="password: hunter2 no sidebar",
        )
        self.assertEqual(fields["key"], ENV_SIMPLIFY_KEY)
        self.assertNotEqual(fields["key"], LEASE_KEY)
        self.assertEqual(fields["expires_at"], "")
        self.assertNotIn("hunter2", fields["notes"])
        state, evidence = parse_env_simplify_notes(fields["notes"])
        self.assertEqual(state, "MISSING")
        self.assertIn("[REDACTED_PASSWORD]", evidence)

    def test_env_write_does_not_overwrite_lease(self):
        before = [
            {
                "key": LEASE_KEY,
                "owner_run_id": "run-9",
                "acquired_at": "a",
                "expires_at": "b",
                "notes": "held",
            }
        ]
        plan = plan_control_write(before, ENV_SIMPLIFY_KEY)
        self.assertEqual(plan.action, "append")
        after = before + [
            env_simplify_control_fields(
                run_id="run-9",
                workflow="apply-ready-jobs",
                checked_at="2026-09-10T02:00:00",
                state="PRESENT",
                evidence="sidebar visible",
            )
        ]
        self.assertTrue(
            control_write_persisted(
                after,
                key=ENV_SIMPLIFY_KEY,
                intended={"key": ENV_SIMPLIFY_KEY, "notes": format_env_simplify_notes("PRESENT", "sidebar visible")},
                protected_keys=(LEASE_KEY,),
                before_rows=before,
            )
        )

    def test_next_run_recovers_when_copilot_is_visible(self):
        missed = copilot_state(
            CopilotObservation(
                employer_page_copilot_ui=False,
                simplify_jobs_session=True,
                evidence="no Copilot sidebar",
            )
        )
        self.assertEqual(missed, "MISSING")
        self.assertFalse(copilot_allows_apply(missed))
        recovered = copilot_state(
            CopilotObservation(
                employer_page_copilot_ui=True,
                simplify_jobs_session=True,
                evidence="sidebar Autofill This Page",
            )
        )
        self.assertEqual(recovered, "PRESENT")
        self.assertTrue(copilot_allows_apply(recovered))
        fields = env_simplify_control_fields(
            run_id="run-10",
            workflow="apply-ready-jobs",
            checked_at="2026-09-10T03:00:00",
            state=recovered,
            evidence="sidebar Autofill This Page",
        )
        self.assertIn("state=PRESENT", fields["notes"])
        self.assertNotIn("state=MISSING", fields["notes"])


class TestPreferencesMemory(unittest.TestCase):
    def test_secret_is_never_exported(self):
        cls = classify_preference_entry("login", "password: hunter2")
        self.assertEqual(cls, "SECRET_OR_CREDENTIAL")
        self.assertEqual(preference_export_mode(cls), "omit")
        delta = render_preferences_delta(
            [
                PreferenceDeltaRow(
                    title="login",
                    cls=cls,
                    evidence="password: hunter2",
                    proposed_destination="none",
                    already_in_github=False,
                    body="password: hunter2",
                )
            ]
        )
        self.assertNotIn("hunter2", delta)
        self.assertIn("secret_or_credential_count: 1", delta)

    def test_local_private_is_count_only(self):
        cls = classify_preference_entry("home", "123 Maple Street")
        self.assertEqual(cls, "LOCAL_PRIVATE")
        self.assertEqual(preference_export_mode(cls), "count_only")
        self.assertFalse(local_overrides_github(cls))
        self.assertTrue(local_overrides_github(cls, kind="private_value"))
        delta = render_preferences_delta(
            [
                PreferenceDeltaRow(
                    title="home",
                    cls=cls,
                    evidence="123 Maple Street",
                    proposed_destination="none",
                    already_in_github=False,
                    body="123 Maple Street",
                )
            ]
        )
        self.assertNotIn("123 Maple Street", delta)
        self.assertIn("local_private_count: 1", delta)

    def test_github_duplicate_is_redundant(self):
        github = "Simplify Copilot is a required precondition for Polar application execution."
        cls = classify_preference_entry(
            "copilot",
            "Simplify Copilot is a required precondition for Polar application execution.",
            github_corpus=github,
        )
        self.assertEqual(cls, "REDUNDANT")

    def test_one_off_is_not_promoted_in_delta_as_canonical(self):
        cls = classify_preference_entry(
            "paypal",
            "PayPal duplicate-draft one-off workaround on this employer only",
        )
        self.assertEqual(cls, "ONE_OFF")
        self.assertEqual(preference_export_mode(cls), "sanitized")

    def test_learning_candidate_appears_sanitized(self):
        cls = classify_preference_entry(
            "copilot address",
            "Copilot sometimes fills a wrong street address. Re-read the visible widget.",
        )
        self.assertEqual(cls, "LEARNING_CANDIDATE")
        dest = proposed_github_destination("Copilot autofill widget street")
        self.assertEqual(dest, "knowledge/form_strategy.yaml")
        delta = render_preferences_delta(
            [
                PreferenceDeltaRow(
                    title="copilot address",
                    cls=cls,
                    evidence="wrong street after Autofill This Page",
                    proposed_destination=dest,
                    already_in_github=False,
                )
            ]
        )
        self.assertIn("## Polar Preferences Delta", delta)
        self.assertIn("class LEARNING_CANDIDATE", delta)
        self.assertIn("already_in_github no", delta)
        self.assertIn("unassigned", delta)

    def test_github_wins_strategy_conflict(self):
        body = "standing form answer is No for future sponsorship"
        github = "form_answer: Yes"
        self.assertTrue(preference_conflicts_github(body, github))
        self.assertEqual(winning_memory_source("LEARNING_CANDIDATE"), "canonical_github")
        self.assertEqual(winning_memory_source("LOCAL_PRIVATE"), "canonical_github")
        self.assertEqual(
            winning_memory_source("LOCAL_PRIVATE", kind="private_value"),
            "local_private",
        )

    def test_no_longer_optional_is_not_auto_stale(self):
        cls = classify_preference_entry(
            "copilot",
            "Copilot is no longer optional. Require it on the employer page.",
        )
        self.assertEqual(cls, "LEARNING_CANDIDATE")

    def test_api_key_is_secret(self):
        cls = classify_preference_entry("token", "api_key: sk-test-123")
        self.assertEqual(cls, "SECRET_OR_CREDENTIAL")
        self.assertEqual(preference_export_mode(cls), "omit")

    def test_compact_preferences_stays_thin(self):
        text = compact_preferences_markdown(
            local_private=[("street", "kept locally")],
            candidates=[
                PreferenceCandidate("pref_20260910_001", "re-read after autofill")
            ],
            last_reconciled="2026-09-10T22:00:00-04:00",
            github_runtime_url="https://example.invalid/POLAR_RUNTIME.md",
            main_revision="2026-09-10.pref-reconcile",
        )
        self.assertIn("# Polar Preferences", text)
        self.assertIn("## Canonical behavior", text)
        self.assertIn("## Local-only facts", text)
        self.assertIn("## Pending learning candidates", text)
        self.assertIn("## Sync state", text)
        self.assertIn("kept locally", text)
        self.assertIn("pref_20260910_001", text)
        self.assertIn("last_reconciled:", text)
        self.assertNotIn("optional_accelerator", text)
        self.assertLess(len(text.splitlines()), 26)
        self.assertEqual(LOCAL_PREFERENCES_PATH, "/home/polar/PREFERENCES.md")


class TestPreferenceLifecycle(unittest.TestCase):
    def test_export_assigns_id_and_retains_unresolved(self):
        assigned = assign_preference_ids(
            ["Copilot filled the wrong address on PayPal"],
            day="2026-09-10",
        )
        self.assertEqual(assigned[0].candidate_id, "pref_20260910_001")
        self.assertTrue(export_retains_candidate("LEARNING_CANDIDATE"))
        self.assertFalse(export_retains_candidate("EPHEMERAL"))
        delta = render_preferences_delta(
            [
                PreferenceDeltaRow(
                    title="copilot address",
                    cls="LEARNING_CANDIDATE",
                    evidence="wrong street after Autofill This Page",
                    proposed_destination="knowledge/form_strategy.yaml",
                    already_in_github=False,
                    candidate_id=assigned[0].candidate_id,
                )
            ]
        )
        self.assertIn("pref_20260910_001", delta)
        compact = compact_preferences_markdown(
            local_private=[],
            candidates=assigned,
            last_reconciled="2026-09-10T22:00:00-04:00",
            github_runtime_url="https://example.invalid/POLAR_RUNTIME.md",
        )
        self.assertIn("pref_20260910_001", compact)
        self.assertEqual(parse_pending_candidates(compact), assigned)

    def test_promote_in_open_pr_is_retained(self):
        candidate = PreferenceCandidate(
            "pref_20260910_001",
            "Copilot filled the wrong address on PayPal",
        )
        resolution = PreferenceResolution(
            candidate_id="pref_20260910_001",
            outcome="PROMOTE",
            canonical_destination="knowledge/form_strategy.yaml",
            resolved_revision="open-pr",
        )
        kept = reconcile_preference_candidates(
            [candidate],
            [resolution],
            on_main=False,
        )
        self.assertEqual(kept, [candidate])

    def test_promote_on_main_is_removed(self):
        candidate = PreferenceCandidate(
            "pref_20260910_001",
            "Verify address fields after Copilot autofill.",
        )
        resolution = PreferenceResolution(
            candidate_id="pref_20260910_001",
            outcome="PROMOTE",
            canonical_destination="knowledge/form_strategy.yaml",
            resolved_revision="64c558f",
        )
        kept = reconcile_preference_candidates(
            [candidate],
            [resolution],
            on_main=True,
        )
        self.assertEqual(kept, [])

    def test_drop_one_off_on_main_is_removed(self):
        candidate = PreferenceCandidate("pref_20260910_002", "PayPal duplicate draft")
        kept = reconcile_preference_candidates(
            [candidate],
            [
                PreferenceResolution(
                    candidate_id="pref_20260910_002",
                    outcome="DROP_ONE_OFF",
                )
            ],
            on_main=True,
        )
        self.assertEqual(kept, [])

    def test_keep_local_is_retained(self):
        candidate = PreferenceCandidate("pref_20260910_005", "consent prompt choice")
        kept = reconcile_preference_candidates(
            [candidate],
            [
                PreferenceResolution(
                    candidate_id="pref_20260910_005",
                    outcome="KEEP_LOCAL",
                )
            ],
            on_main=True,
        )
        self.assertEqual(kept, [candidate])

    def test_needs_more_evidence_is_retained(self):
        candidate = PreferenceCandidate("pref_20260910_003", "Workday date widget")
        kept = reconcile_preference_candidates(
            [candidate],
            [
                PreferenceResolution(
                    candidate_id="pref_20260910_003",
                    outcome="NEEDS_MORE_EVIDENCE",
                )
            ],
            on_main=True,
        )
        self.assertEqual(kept, [candidate])

    def test_owner_decision_is_retained(self):
        candidate = PreferenceCandidate("pref_20260910_004", "consent prompt")
        kept = reconcile_preference_candidates(
            [candidate],
            [
                PreferenceResolution(
                    candidate_id="pref_20260910_004",
                    outcome="OWNER_DECISION",
                )
            ],
            on_main=True,
        )
        self.assertEqual(kept, [candidate])

    def test_local_private_stays_in_compact(self):
        compact = compact_preferences_markdown(
            local_private=[("street", "kept locally")],
            candidates=[],
            last_reconciled="2026-09-10T22:00:00-04:00",
            github_runtime_url="https://example.invalid/POLAR_RUNTIME.md",
        )
        self.assertIn("kept locally", compact)
        self.assertEqual(parse_pending_candidates(compact), [])

    def test_reconcile_twice_is_noop(self):
        candidate = PreferenceCandidate("pref_20260910_001", "address after autofill")
        resolution = PreferenceResolution(
            candidate_id="pref_20260910_001",
            outcome="PROMOTE",
            canonical_destination="knowledge/form_strategy.yaml",
        )
        first = reconcile_preference_candidates(
            [candidate],
            [resolution],
            on_main=True,
        )
        second = reconcile_preference_candidates(
            first,
            [resolution],
            on_main=True,
        )
        self.assertEqual(first, [])
        self.assertEqual(second, first)

    def test_same_id_different_wording_is_deterministic(self):
        observed = PreferenceCandidate(
            "pref_20260910_001",
            "Copilot filled the wrong address on PayPal",
        )
        generalized = PreferenceCandidate(
            "pref_20260910_001",
            "Verify address fields after Copilot autofill.",
        )
        resolution = PreferenceResolution(
            candidate_id="pref_20260910_001",
            outcome="PROMOTE",
            canonical_destination="knowledge/form_strategy.yaml",
        )
        self.assertEqual(
            reconcile_preference_candidates([observed], [resolution], on_main=True),
            [],
        )
        self.assertEqual(
            reconcile_preference_candidates([generalized], [resolution], on_main=True),
            [],
        )

    def test_no_resolution_is_not_destructive(self):
        candidate = PreferenceCandidate("pref_20260910_001", "address after autofill")
        self.assertTrue(candidate_survives_resolution(None, on_main=True))
        self.assertEqual(
            reconcile_preference_candidates([candidate], [], on_main=True),
            [candidate],
        )
        self.assertTrue(export_retains_candidate("ONE_OFF"))
        self.assertTrue(export_retains_candidate("STALE"))

    def test_assign_preserves_existing_id(self):
        existing = PreferenceCandidate("pref_20260910_001", "old summary")
        assigned = assign_preference_ids(
            [existing, "new observation"],
            day="2026-09-10",
        )
        self.assertEqual(assigned[0].candidate_id, "pref_20260910_001")
        self.assertEqual(assigned[1].candidate_id, "pref_20260910_002")


if __name__ == "__main__":
    unittest.main()
