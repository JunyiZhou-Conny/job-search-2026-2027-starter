#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_polar_runtime import OUT_DEFAULT, main, render, compile_sections  # noqa: E402
from polar_policy import AUTH_QUESTION_KINDS, WORK_AUTHORIZATION_VERIFY_KINDS  # noqa: E402

REQUIRED_HEADINGS = [
    "## A. Candidate facts",
    "## B. Discovery sources",
    "## C. Triage rules",
    "## D. Regular vs prioritized policy",
    "## E. Resume-cluster selection",
    "## F. Writing evidence and writing rules",
    "## G. Blocker handling",
    "## H. Submission behavior",
    "## I. Prohibited fabrication",
    "## J. Runtime status semantics",
    "## K. Historical duplicate guard",
    "## L. Schema-safe Sheet writes",
    "## M. Browser lease",
    "## N. Run and incident telemetry",
    "## O. Employer requisition identity",
    "## P. Memory ownership and autofill",
]

STATUSES = [
    "NEW",
    "READY_REGULAR",
    "READY_PRIORITY",
    "IN_PROGRESS",
    "REVIEW_READY",
    "SUBMITTED",
    "SUBMISSION_UNKNOWN",
    "BLOCKED",
    "SKIP",
]

SECRET_LINE = re.compile(
    r"(?i)(password\s*[:=]\s*\S+|cookie\s*[:=]\s*\S+|set-cookie\s*[:=]"
    r"|otp\s*[:=]\s*\d{4,8}|2fa\s*[:=]\s*\S+|storage_state)"
)

# Wording that would send Polar back into a post-Autofill full-form audit.
# None of it may appear in a compiled artifact, in any polarity.
BROAD_AUDIT_PHRASES = (
    "verify every field",
    "review all fields",
    "inspect every autofilled",
    "validate the entire form",
    "reread all populated",
    "re-read all populated",
    "verify all profile",
    "final review of visible widgets",
    "line-by-line",
    "line by line",
    "every autofilled answer",
    "review every field",
    "check every field",
    "verify each field",
    "verify every widget",
    "audit the whole form",
)

# Wording that may appear only as a prohibition (inside a "Do not:" list or
# on a line that itself says not).
NEGATED_ONLY_PHRASES = (
    "re-read every populated widget",
    "re-verify gender",
    "reproduce jobright profile filling",
    "distrust all autofill",
    "walk the section a standing-answer list",
    "walk it against every populated widget",
    "walk section a against populated widgets",
)

FAST_VALIDATION_CLASSES = (
    "identity",
    "work_authorization",
    "eligibility_critical",
    "required_empty_or_error",
    "required_legal_compliance",
)


def assert_no_full_form_audit(case: unittest.TestCase, text: str, label: str) -> None:
    lowered = text.lower()
    for phrase in BROAD_AUDIT_PHRASES:
        case.assertNotIn(phrase, lowered, f"{label}: {phrase!r}")
    in_do_not_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().rstrip(":") in {"do not", "why-us must not", "fde do not claim"}:
            in_do_not_list = True
            continue
        if in_do_not_list and not stripped.startswith("- "):
            in_do_not_list = False
        low = stripped.lower()
        for phrase in NEGATED_ONLY_PHRASES:
            if phrase in low:
                negated = in_do_not_list or re.search(r"\b(do not|does not|not|never)\b", low)
                case.assertTrue(negated, f"{label}: {phrase!r} appears as an instruction: {stripped!r}")


def compile_text() -> str:
    return render(compile_sections())


def workflow_prompt(name: str) -> str:
    return (ROOT / "generated" / "polar" / "workflows" / f"{name}.md").read_text(
        encoding="utf-8"
    )


class TestPolarRuntime(unittest.TestCase):
    def test_banner_and_required_sections(self):
        text = compile_text()
        self.assertIn("COMPILED ARTIFACT. Not canonical.", text)
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text, heading)

    def test_no_secret_assignments(self):
        text = compile_text()
        self.assertIsNone(SECRET_LINE.search(text), SECRET_LINE.search(text))
        self.assertIn("No passwords, cookies, OTP codes", text)

    def test_identity_facts_agree(self):
        text = compile_text()
        self.assertIn("Junyi Zhou", text)
        self.assertIn("Citizenship country (form and fact): China", text)
        self.assertIn("Current visa type when asked: F-1", text)
        self.assertIn("Required future-sponsorship widget: No.", text)
        self.assertIn("Future sponsorship required (standing fact): False", text)
        self.assertNotIn("Required future-sponsorship widget: Yes.", text)
        self.assertNotIn("Future sponsorship required (standing fact): True", text)
        self.assertIn("Answer only the asked semantic.", text)
        self.assertIn("Optional identity or status fields stay blank.", text)
        self.assertIn("Program end / I-20 date: 2026-12-18", text)
        self.assertIn("Year-only graduation widget: 2027", text)
        self.assertIn("Earliest full-time start: 2027-01-18", text)
        self.assertIn("Remote ok: False", text)
        self.assertNotIn("Citizenship country (form and fact): United States", text)
        self.assertIn("visa_sponsorship: No.", text)
        self.assertNotIn("visa_sponsorship: Yes.", text)
        self.assertIn("DO NOT AUTO-MAP", text)
        self.assertIn("require work authorization", text)
        self.assertIn("Do not treat that wording as this answer", text)
        self.assertIn("eeo_self_identification:", text)
        self.assertIn("Do not clear them", text)
        self.assertIn("Do not change them", text)
        self.assertIn("gender Male", text)
        self.assertIn("hispanic_latino No", text)
        self.assertIn("race Asian", text)
        self.assertIn("veteran_status I am not a protected veteran", text)

    def test_phone_and_email_are_not_copied(self):
        text = compile_text()
        self.assertIn("Phone numbers live in the local Polar profile", text)
        self.assertIn("dedicated local APPLICATION mailbox", text)
        self.assertIn("street_address_source: local Polar or private profile", text)
        self.assertNotRegex(text, r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
        self.assertNotRegex(text, r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")

    def test_statuses_and_caps(self):
        text = compile_text()
        for status in STATUSES:
            self.assertIn(status, text, status)
        self.assertIn("Per-run worker budget on apply-ready-jobs: 3 considered candidates", text)
        self.assertIn("Allocation is obsolete", text)
        self.assertNotIn("Regular jobs per apply-ready-jobs run:", text)
        self.assertIn("There is no shared daily regular submission pool.", text)
        self.assertNotIn("Regular submissions per local calendar day", text)
        self.assertIn("Prioritized auto-submit: True", text)
        self.assertIn("polar_policy.priority_submit_permitted", text)
        self.assertIn("writing_observation_mode: True", text)
        self.assertIn("SUBMISSION_UNKNOWN first", text)
        self.assertIn("degree_level_gate_missed_at_discovery", text)
        self.assertIn("github_write_canary must not overwrite polar_browser", text)
        self.assertIn(
            "google_sheets means the Google connector can read and write Polar Jobs.",
            text,
        )
        self.assertIn("Browser sheets.google.com is not google_sheets.", text)
        self.assertIn("clearly says answer Yes or answer No", text)
        self.assertIn("Jobright extension owns autofill", text)
        self.assertIn("The application Outlook inbox is readable", text)
        self.assertIn("Queue reads are targeted", text)
        self.assertIn("Trust the form, not the extension sidebar", text)
        self.assertNotIn("Simplify Copilot is a required apply precondition.", text)
        self.assertIn("Do not click Simplify Copilot Autofill", text)
        self.assertNotIn("optional_accelerator", text)
        self.assertIn("PREFERENCES.md is not a second strategy database.", text)
        self.assertIn("pref_20260911_005 | PROMOTE | scripts/polar_policy.py", text)
        self.assertNotIn("preference_resolutions: none", text)
        self.assertIn("jobright_matches_onboarding_gate", text)
        self.assertIn("polar_policy.canonical_repeat_key", text)
        self.assertIn("Perfect Resume", text)
        self.assertIn("resumes/Perfect Resume/JZ_Resume_2027.pdf", text)
        self.assertNotIn("/Users/conny/Desktop/JZ_Resume_911.pdf", text)
        self.assertIn("Do not upload `generated/resumes/export/ai_infra_v1.pdf`.", text)
        self.assertNotIn(
            "If the native widget is empty and `generated/resumes/export/ai_infra_v1.pdf` exists locally, attach that export.",
            text,
        )
        self.assertIn("Copilot sidebar Completed is not proof", text)
        self.assertIn("Junyi-authorized maintenance path", text)
        self.assertIn("pref_20260912_002 | STALE", text)
        self.assertIn("pref_20260914_001 | PROMOTE", text)
        self.assertIn("pref_20260915_005 | PROMOTE", text)
        self.assertIn("pref_20260915_002 | OWNER_DECISION", text)
        self.assertIn("An open Cursor PR is not canonical.", text)
        self.assertIn("Match candidate_id only.", text)
        self.assertIn("Never reuse. Never fill gaps.", text)
        self.assertIn("KEEP_LOCAL leaves pending", text)

    def test_committed_file_matches_compiler(self):
        generated = compile_text()
        self.assertTrue(OUT_DEFAULT.is_file(), str(OUT_DEFAULT))
        self.assertEqual(OUT_DEFAULT.read_text(encoding="utf-8"), generated)

    def test_compiler_is_idempotent(self):
        first = compile_text()
        second = compile_text()
        self.assertEqual(first, second)

    def test_cli_writes_the_same_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "POLAR_RUNTIME.md"
            self.assertEqual(main(["--out", str(out)]), 0)
            self.assertEqual(out.read_text(encoding="utf-8"), compile_text())

    def test_queue_schema_matches_operator(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        header = (ROOT / "generated" / "polar" / "queue_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(header.split(","), operator["queue_columns"])
        writing = (ROOT / "generated" / "polar" / "writing_log_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(writing.split(","), operator["writing_log_columns"])
        heartbeat = (ROOT / "generated" / "polar" / "heartbeat_schema.csv").read_text(
            encoding="utf-8"
        ).strip()
        self.assertEqual(heartbeat.split(","), operator["heartbeat_columns"])
        for name, key in (
            ("run_log_schema.csv", "run_log_columns"),
            ("incident_log_schema.csv", "incident_log_columns"),
            ("control_schema.csv", "control_columns"),
            ("learning_reports_schema.csv", "learning_reports_columns"),
        ):
            header = (ROOT / "generated" / "polar" / name).read_text(encoding="utf-8").strip()
            self.assertEqual(header.split(","), operator[key], name)
        self.assertIn("apply_url_confidence", operator["queue_columns"])
        self.assertEqual(operator["queue_columns"].index("apply_url_confidence"), 8)

    def test_workflow_prompts_are_paste_ready(self):
        text = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in (
            "discover-jobs-hourly",
            "apply-ready-jobs",
            "daily-job-summary",
            "production-learning-daily",
            "polar-scheduler-heartbeat",
        ):
            self.assertIn(name, text)
            self.assertIn(
                f"generated/polar/workflows/{name}.md",
                text,
            )
        self.assertIn("thin trust-delegation bootstrap", text)

    def test_apply_ledger_still_loads_gates(self):
        import yaml
        from apply_ledger import load_gates

        raw = yaml.safe_load((ROOT / "config" / "submit_gates.yaml").read_text(encoding="utf-8"))
        self.assertIn("ashby", raw["cursor_cloud"]["gates"])
        self.assertNotIn("gates", raw)
        gates = load_gates()
        self.assertIn("ashby", gates["gates"])
        self.assertEqual(gates["regular_submit_cap_per_run"], 3)
        self.assertNotIn("regular_submit_cap_per_local_day", gates["polar_local"])

    def test_historical_guard_includes_known_ledger_keys(self):
        text = compile_text()
        self.assertIn("## K. Historical duplicate guard", text)
        self.assertIn("An empty Google Sheet is not a clean slate.", text)
        self.assertIn("6a9b1602fe45b8490f606c9f", text)
        self.assertIn(
            "https://job-boards.greenhouse.io/embed/job_app?for=quantbot-technologies&jr_id=6a9b1602fe45b8490f606c9f",
            text,
        )
        self.assertIn("6a9b756513883870605981ea", text)
        self.assertIn("https://jobs.smartrecruiters.com/solidigm/744000147613769", text)
        self.assertIn("6a7a308fbb6ca93ae561a556", text)
        self.assertIn(
            "https://www.citadel.com/careers/details/sector-data-scientist-2027-intern-us",
            text,
        )
        self.assertIn(
            "https://job-boards.greenhouse.io/togetherai/jobs/5157661007", text
        )
        self.assertIn(
            "https://jobs.ashbyhq.com/chartahealth/3088555d-de93-4236-add1-41005bf0933b",
            text,
        )

    def test_historical_guard_is_compact(self):
        text = compile_text()
        self.assertNotIn("id,job_id,company,role,job_url", text)
        self.assertNotIn("Widget says work authorization", text)
        self.assertNotIn("System trial: compile cloud_swe", text)
        self.assertNotIn("attempt_id,job_id,run_id", text)

    def test_discover_forbids_ojp_apply_still_resolves(self):
        discover = workflow_prompt("discover-jobs-hourly")
        apply = workflow_prompt("apply-ready-jobs")
        self.assertIn("Do not open Original Job Post.", discover)
        self.assertNotIn("click Original Job Post", discover)
        self.assertIn("section K", discover)
        self.assertIn("retired_from_apply_path", discover)
        self.assertIn("Apply with Autofill", apply)
        self.assertIn("section K", apply)

    def test_ready_priority_auto_assign_without_label_gate(self):
        text = compile_text()
        self.assertIn(
            "Polar may mark weight=prioritized when a strong configured signal is visible on the Jobright card or JD.",
            text,
        )
        self.assertNotIn("Labels stay suggestions until Junyi confirms.", text)

    def test_graduation_window_is_note_not_skip(self):
        text = compile_text()
        self.assertIn(
            "An exclusive graduation or enrollment window is an eligibility note, not a skip.",
            text,
        )
        self.assertIn("non-blocking eligibility note, not a skip", text)

    def test_fast_validation_pass_replaces_full_form_audit(self):
        text = compile_text()
        assert_no_full_form_audit(self, text, "POLAR_RUNTIME")
        self.assertIn("Fast validation pass after Autofill:", text)
        self.assertIn("Jobright Autofill is the default filler. Polar is anomaly detection and targeted repair.", text)
        self.assertIn("polar_policy.full_form_audit_permitted is false", text)
        for name in FAST_VALIDATION_CLASSES:
            self.assertIn(f"- {name}: ", text, name)
        self.assertIn("- identity: first_name, last_name, application_email.", text)
        self.assertIn("Legal first name Junyi. Legal last name Zhou.", text)
        self.assertIn("No full profile audit.", text)
        self.assertIn(
            "- work_authorization: " + ", ".join(WORK_AUTHORIZATION_VERIFY_KINDS) + ". These are every kind polar_policy.auth_form_action classifies. Re-read each present widget of these kinds even when Autofill populated it.",
            text,
        )
        for kind in (
            "sponsorship_to_begin",
            "ead_possession",
            "opt_approval",
            "opt_eligibility",
            "authorization_at_start",
            "status_yes_no",
            "authorization_without_sponsorship",
            "country_specific_sponsorship",
            "current_work_authorization",
        ):
            self.assertIn(kind, WORK_AUTHORIZATION_VERIFY_KINDS, kind)
        self.assertIn("Required currently-authorized or sponsorship-to-begin with an unknown fact: leave the field and BLOCK that job only.", text)
        self.assertIn("Optional widgets of these kinds stay blank;", text)
        self.assertIn("Do not fill unasked OPT, EAD, or immigration widgets.", text)
        self.assertIn("knowledge/work_authorization.yaml stays authoritative", text)
        self.assertIn("Only widgets that decide eligibility for this role. Not every generic question.", text)
        self.assertIn("jobright_sidebar_complete_but_employer_dom_empty", text)
        self.assertIn("Employer DOM is truth.", text)
        self.assertIn("Do not generalize one employer's seven compliance questions to every form.", text)
        self.assertIn(
            "Trust when populated, no validation error, no known failure class: eeo_demographics, phone_address_formatting, resume_filename, populated_education_employment, routine_non_material. Do not re-read those widgets.",
            text,
        )
        self.assertIn("A visible conflict with known candidate truth, seen in passing, is repaired and noted.", text)
        self.assertIn("- re-verify gender, race, ethnicity, veteran, or disability after Autofill", text)
        self.assertIn("- reproduce Jobright profile filling by hand", text)
        self.assertIn("- distrust all Autofill output by default", text)
        self.assertIn("nickname_on_legal_first_name: wrong value Conny.", text)
        self.assertIn("gpa_dual_value_to_single: wrong value 4.0, 3.925.", text)
        self.assertIn("Do not assume the profile was fixed.", text)
        self.assertIn("Status unknown.", text)
        self.assertIn("repeat_key autofill_nickname_on_legal_first_name", text)
        self.assertIn("repeat_key autofill_sponsorship_yes_on_future_sponsorship_widget", text)
        self.assertIn("sponsorship_yes_on_future_sponsorship_widget: wrong value Yes.", text)
        self.assertNotIn("repeat_key autofill_sponsorship_no_on_future_sponsorship_widget", text)
        self.assertNotIn("sponsorship_no_on_future_sponsorship_widget: wrong value No.", text)
        self.assertIn("Three routine applications in 30 to 40 minutes is the evaluation target, not a timeout.", text)
        self.assertIn("autofill_corrections=<class tokens>", text)
        self.assertIn("Not one row per widget.", text)
        self.assertIn(
            "Fast validation pass passes (section P): identity, work authorization, eligibility-critical, required-empty-or-error, required legal/compliance.",
            text,
        )
        self.assertIn("Identity fields (First Name, Last Name, application email) are correct after a visible form DOM read-back.", text)
        self.assertIn("This list is a fill table.", text)
        self.assertIn("It is not a license to re-read every populated widget.", text)
        self.assertIn("Trusted when populated. Do not reopen or re-verify them after Autofill.", text)
        self.assertNotIn("Then Polar reads the form DOM: identity, contact, sponsorship wording, referral.", text)

    def test_fast_validation_keeps_the_safeties(self):
        text = compile_text()
        self.assertIn("Required future-sponsorship widget: No.", text)
        self.assertNotIn("Required future-sponsorship widget: Yes.", text)
        self.assertIn("H-1B-named widget: No", text)
        self.assertIn("Citizenship country (form and fact): China", text)
        self.assertIn("Never invent.", text)
        self.assertIn("Extension sidebar Completed is not proof a widget has a value. Look at the form DOM.", text)
        self.assertIn("Duplicate check passes against the Sheet and section K.", text)
        self.assertIn("One final Submit is used.", text)
        self.assertIn("Employer-page confirmation text is visible.", text)
        self.assertIn("Do not submit the same employer requisition twice.", text)
        self.assertIn("Writing is evidence-grounded.", text)
        self.assertIn("Referral / how-heard is blank unless a verified fact exists.", text)

    def test_policy_revision_is_fast_validation(self):
        import yaml

        operator = yaml.safe_load(
            (ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(operator["policy_revision"], "2026-09-15.gpa-dual-value")
        autofill = operator["autofill"]
        self.assertIs(autofill["full_form_audit"], False)
        self.assertEqual(tuple(autofill["post_autofill_checks"]), FAST_VALIDATION_CLASSES)
        self.assertEqual(autofill["polar_role"], "anomaly_detection_and_targeted_repair")
        self.assertEqual(autofill["default_filler"], "jobright_extension")
        self.assertEqual(
            tuple(autofill["fast_validation_pass"]["verify"]["work_authorization"]["widgets"]),
            WORK_AUTHORIZATION_VERIFY_KINDS,
        )
        self.assertEqual(
            set(WORK_AUTHORIZATION_VERIFY_KINDS),
            set(AUTH_QUESTION_KINDS) - {"unknown"},
        )
        known = autofill["fast_validation_pass"]["known_failure_classes"]
        self.assertEqual(known["nickname_on_legal_first_name"]["wrong_value"], "Conny")
        self.assertEqual(known["nickname_on_legal_first_name"]["upstream_status"], "unknown")
        self.assertEqual(known["sponsorship_yes_on_future_sponsorship_widget"]["wrong_value"], "Yes")
        self.assertEqual(known["sponsorship_yes_on_future_sponsorship_widget"]["upstream_status"], "unknown")
        self.assertEqual(known["gpa_dual_value_to_single"]["wrong_value"], "4.0, 3.925")
        self.assertEqual(known["gpa_dual_value_to_single"]["upstream_status"], "unknown")
        self.assertNotIn("sponsorship_no_on_future_sponsorship_widget", known)
        self.assertIs(autofill["fast_validation_pass"]["timing"]["is_timeout"], False)


if __name__ == "__main__":
    unittest.main()
