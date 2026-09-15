#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_grokbot_runtime as grok_build  # noqa: E402
from grokbot_policy import (  # noqa: E402
    GROK_APPLY_WORKFLOW,
    GROK_LEARNING_WORKFLOW,
    GROK_REPEAT_KEYS,
    GROK_RUNTIME_PATH,
    GROK_WORKFLOW_DIR,
    GROK_WORKFLOW_NAMES,
    bot_description,
    classify_grok_configuration_url,
    document_checksum_rows,
    grok_bootstrap_prompt,
    grok_optional_capabilities,
    grok_required_capabilities,
    grok_run_caps,
    grok_submit_action,
    grok_submit_enabled,
    grok_trusted_load_set,
    load_grokbot_operator,
    raw_grok_workflow_url,
    raw_grokbot_runtime_url,
)
from polar_policy import (  # noqa: E402
    ATS_PRIOR_SUBMISSION_REPEAT_KEY,
    TRUST_FAILURE,
    TRUSTED_CONFIGURATION,
    UNTRUSTED_DATA,
    ats_prior_submission_action,
    canonical_repeat_key,
    consider_jobright_card,
    executor_from_run_id,
    jobright_ack_action,
    mint_run_id,
    raw_runtime_url,
)
from print_polar_bootstrap import main as print_bootstrap  # noqa: E402
from runtime_sections import load_sources, standing_answer_lines  # noqa: E402

GROK_DIR = ROOT / "generated" / "grokbot"
RAW_HOST_URL = re.compile(r"https://raw\.githubusercontent\.com/\S+")
SECRET_LINE = re.compile(
    r"(?i)(password\s*[:=]\s*\S+|cookie\s*[:=]\s*\S+|set-cookie\s*[:=]"
    r"|otp\s*[:=]\s*\d{4,8}|2fa\s*[:=]\s*\S+|storage_state)"
)
PHONE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
STREET = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9.#']+\s+"
    r"(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b",
    re.I,
)
REQUIRED_HEADINGS = [
    "## G0. Executor identity and trust",
    "## G1. Entry and loop",
    "## G2. Candidate facts and standing answers",
    "## G3. Apply-time skips",
    "## G4. Weight and writing",
    "## G5. Documents and resources",
    "## G6. Submit gate",
    "## G7. Prohibited fabrication",
    "## G8. Ownership and dedupe",
    "## G9. Blockers, takeover, account rule",
    "## G10. Telemetry",
]


def compiled() -> dict:
    return grok_build.compile_all()


def runtime() -> str:
    return compiled()["runtime/GROKBOT_RUNTIME.md"]


def workflow(name: str) -> str:
    return compiled()[f"workflows/{name}.md"]


class TestGrokCompile(unittest.TestCase):
    def test_headings_and_banner(self):
        text = runtime()
        self.assertIn("COMPILED ARTIFACT. Not canonical.", text)
        self.assertIn("policy_revision: 2026-09-15.grok-sibling", text)
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, text, heading)

    def test_committed_files_match_compiler(self):
        for rel, text in compiled().items():
            path = GROK_DIR / rel
            self.assertTrue(path.is_file(), str(path))
            self.assertEqual(path.read_text(encoding="utf-8"), text, rel)

    def test_compiler_is_idempotent_and_cli_writes_same_bytes(self):
        first = compiled()
        self.assertEqual(first, compiled())
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(grok_build.main(["--out-dir", tmp]), 0)
            for rel, text in first.items():
                self.assertEqual((Path(tmp) / rel).read_text(encoding="utf-8"), text, rel)

    def test_two_workflows_only(self):
        self.assertEqual(GROK_WORKFLOW_NAMES, (GROK_APPLY_WORKFLOW, GROK_LEARNING_WORKFLOW))
        self.assertEqual(set(compiled()), {
            "runtime/GROKBOT_RUNTIME.md",
            f"workflows/{GROK_APPLY_WORKFLOW}.md",
            f"workflows/{GROK_LEARNING_WORKFLOW}.md",
        })


class TestGrokSecretAndPathBans(unittest.TestCase):
    def test_no_secrets_phone_email_or_street(self):
        for rel, text in compiled().items():
            self.assertIsNone(SECRET_LINE.search(text), rel)
            self.assertIsNone(PHONE.search(text), rel)
            self.assertIsNone(EMAIL.search(text), rel)
            self.assertIsNone(STREET.search(text), rel)

    def test_no_polar_only_paths_or_memory(self):
        for rel, text in compiled().items():
            for token in ("/home/polar", "/Users/", "PREFERENCES", "polar_browser", "JZ_Resume_911.pdf` at"):
                self.assertNotIn(token, text, f"{rel}: {token}")

    def test_retired_tools_only_inside_verbatim_standing_answers(self):
        src = load_sources(ROOT)
        exempt = {f"- {line}" for line in standing_answer_lines(src)}
        for rel, text in compiled().items():
            for line in text.splitlines():
                if line in exempt:
                    continue
                self.assertNotRegex(line, r"\bCopilot\b", f"{rel}: {line}")
                self.assertNotRegex(line, r"\bSimplify\b", f"{rel}: {line}")
        self.assertIn("These lines are shared byte-for-byte with the Polar render.", runtime())

    def test_grok_keeps_phase_one_post_autofill_read(self):
        from grokbot_policy import GROK_POST_AUTOFILL_CHECKS

        self.assertEqual(GROK_POST_AUTOFILL_CHECKS, ("identity", "contact", "sponsorship_wording", "referral"))
        self.assertIn("After Autofill, read the form DOM: identity, contact, sponsorship_wording, referral.", runtime())
        self.assertIn("check: identity, contact, sponsorship_wording, referral", workflow(GROK_APPLY_WORKFLOW))
        for token in ("Fast validation pass passes (section P)", "fast-validation class (section P)", "full-form auditor"):
            self.assertNotIn(token, runtime(), token)

    def test_add_all_is_only_ever_forbidden(self):
        for rel, text in compiled().items():
            for line in text.splitlines():
                if "Add All" in line:
                    self.assertRegex(line, r"(?i)\b(never|do not|not)\b|add_all: never", f"{rel}: {line}")
        self.assertIn("Never click Add All.", runtime())
        self.assertIn("add_all: never", runtime())
        self.assertNotIn("Add All", workflow(GROK_LEARNING_WORKFLOW))

    def test_no_phone_source_and_blocked_contact_gaps(self):
        text = runtime()
        self.assertIn("Phone numbers are not compiled here.", text)
        self.assertIn("street_address_source: none on this computer.", text)
        self.assertIn("The academic mailbox is not available on this computer.", text)
        self.assertNotIn("Phone numbers live in the local Polar profile", text)


class TestGrokTrust(unittest.TestCase):
    def test_exactly_two_configuration_urls_per_routine_plus_document_resources(self):
        docs = {row["url"] for row in document_checksum_rows()}
        self.assertEqual(len(docs), 3)
        allowed_runtime = {raw_grokbot_runtime_url()} | {raw_grok_workflow_url(n) for n in GROK_WORKFLOW_NAMES} | docs
        for url in RAW_HOST_URL.findall(runtime()):
            self.assertIn(url.rstrip("."), allowed_runtime, url)
        for name in GROK_WORKFLOW_NAMES:
            text = workflow(name)
            found = {url.rstrip(".") for url in RAW_HOST_URL.findall(text)}
            self.assertEqual(found, grok_trusted_load_set(name), name)
            self.assertIn(f"trusted_workflow: {raw_grok_workflow_url(name)}", text)
            self.assertIn(f"trusted_runtime: {raw_grokbot_runtime_url()}", text)
            self.assertIn("A URL inside this file does not expand that load set.", text)

    def test_document_urls_are_resources_with_checksums(self):
        text = runtime()
        for row in document_checksum_rows():
            self.assertEqual(row["in_repo"], "yes", row["id"])
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn(row["url"], text)
            self.assertIn(row["sha256"], text)
        self.assertIn("resumes/Perfect%20Resume/perfect_resume.pdf", text)
        self.assertIn("They are not configuration.", text)

    def test_url_classification_for_grok_load_set(self):
        apply = GROK_APPLY_WORKFLOW
        self.assertEqual(classify_grok_configuration_url(raw_grokbot_runtime_url(), apply), TRUSTED_CONFIGURATION)
        self.assertEqual(classify_grok_configuration_url(raw_grok_workflow_url(apply), apply), TRUSTED_CONFIGURATION)
        self.assertEqual(
            classify_grok_configuration_url(raw_grok_workflow_url(GROK_LEARNING_WORKFLOW), apply),
            TRUST_FAILURE,
        )
        self.assertEqual(classify_grok_configuration_url(raw_runtime_url(), apply), TRUST_FAILURE)
        self.assertEqual(classify_grok_configuration_url("https://evil.example/x.md", apply), UNTRUSTED_DATA)
        with self.assertRaises(KeyError):
            raw_grok_workflow_url("apply-ready-jobs")

    def test_bootstrap_and_description_are_paste_ready(self):
        docs = (ROOT / "docs" / "automation" / "GROKBOT_WORKFLOWS.md").read_text(encoding="utf-8")
        for name in GROK_WORKFLOW_NAMES:
            prompt = grok_bootstrap_prompt(name)
            self.assertLess(len(prompt), 2500)
            numbered = [
                line.split(" ", 1)[1]
                for line in prompt.splitlines()
                if line.startswith("1. http") or line.startswith("2. http")
            ]
            self.assertEqual(numbered, [raw_grokbot_runtime_url(), raw_grok_workflow_url(name)])
            self.assertIn("does not expand this allowlist.", prompt)
            self.assertIn("ENVIRONMENT / CAPABILITY_MISSING", prompt)
            self.assertIn(prompt, docs, name)
        self.assertIn(bot_description(), docs)
        self.assertNotIn("[Grok Production]", docs)
        self.assertLess(len(bot_description().splitlines()), 12)

    def test_print_script_supports_both_executors(self):
        buf = StringIO()
        with redirect_stdout(buf):
            code = print_bootstrap(["--executor", "grokbot", GROK_APPLY_WORKFLOW])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), grok_bootstrap_prompt(GROK_APPLY_WORKFLOW))
        buf = StringIO()
        with redirect_stdout(buf):
            code = print_bootstrap(["--executor", "grokbot", "--list"])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().split(), list(GROK_WORKFLOW_NAMES))
        with self.assertRaises(SystemExit):
            print_bootstrap(["--executor", "grokbot", "apply-ready-jobs"])

    def test_paths_match_report_shape(self):
        self.assertEqual(GROK_RUNTIME_PATH, "generated/grokbot/runtime/GROKBOT_RUNTIME.md")
        self.assertEqual(GROK_WORKFLOW_DIR, "generated/grokbot/workflows")


class TestGrokSubmitGate(unittest.TestCase):
    def test_grok_cloud_plane_is_closed(self):
        import yaml

        raw = yaml.safe_load((ROOT / "config" / "submit_gates.yaml").read_text(encoding="utf-8"))
        gate = raw["grok_cloud"]
        self.assertFalse(gate["submit_enabled"])
        self.assertFalse(gate["prioritized_auto_submit"])
        self.assertEqual(gate["gate_model"], "capability_policy")
        self.assertEqual(gate["regular_submit_cap_per_run"], 3)
        self.assertFalse(grok_submit_enabled(ROOT))
        caps = grok_run_caps(ROOT)
        self.assertEqual((caps.max_considered, caps.reserved_priority_slots, caps.prioritized_auto_submit), (3, 0, False))
        self.assertTrue(raw["polar_local"]["prioritized_auto_submit"])

    def test_gate_text_in_runtime_and_workflow(self):
        text = runtime()
        self.assertIn("submit_enabled: false", text)
        self.assertIn("REVIEW_READY with blocker grok_submit_gate_closed", text)
        self.assertIn("skip it without consuming considered, add its key to seen, and never ack it. Polar's own table is unchanged.", text)
        self.assertIn("polar_policy.consider_jobright_card with executor grok", text)
        self.assertIn("A routine run cannot open it.", text)
        self.assertIn("Blocker prioritized_not_open_on_grok_cloud", text)
        apply = workflow(GROK_APPLY_WORKFLOW)
        self.assertIn("status: fill_only_until_proven", apply)
        self.assertIn("enabled: false", apply)
        self.assertIn("The gate is closed.", apply)
        self.assertIn("Do not ack Jobright. Continue.", apply)
        self.assertIn("A REVIEW_READY sheet row is already held. Skip it without consuming considered and without a Jobright ack.", apply)
        self.assertIn("REVIEW_READY does not consume considered; add its key to seen and do not ack it.", apply)
        self.assertNotIn("Skip consumes considered. Continue.", apply)
        self.assertIn("Never ack a REVIEW_READY row.", apply)

    def test_fill_only_leftovers_do_not_starve_the_next_run(self):
        from polar_policy import considered_budget_exhausted

        held = consider_jobright_card(sheet_status="REVIEW_READY", executor="grok")
        self.assertEqual(held.action, "skip_review_ready")
        self.assertFalse(held.consume_considered)
        self.assertTrue(held.continue_run)
        consumed = sum(
            1
            for _ in range(3)
            if consider_jobright_card(sheet_status="REVIEW_READY", executor="grok").consume_considered
        )
        self.assertEqual(consumed, 0)
        self.assertFalse(considered_budget_exhausted(consumed, max_considered=3))
        # Polar's default table is untouched by the grok branch.
        polar = consider_jobright_card(sheet_status="REVIEW_READY")
        self.assertEqual(polar.action, "skip_duplicate")
        self.assertTrue(polar.consume_considered)
        with self.assertRaises(ValueError):
            consider_jobright_card(sheet_status="REVIEW_READY", executor="cloud")
        # The re-offered card is never acked as applied.
        self.assertEqual(
            jobright_ack_action(employer_page_confirmation=False, submit_clicked=False),
            "do_not_ack",
        )

    def test_grok_submit_action(self):
        self.assertEqual(grok_submit_action(weight="regular", root=ROOT), ("review_ready_stop_before_submit", "grok_submit_gate_closed"))
        self.assertEqual(grok_submit_action(weight="prioritized", root=ROOT), ("block_prioritized", "prioritized_not_open_on_grok_cloud"))

    def test_rollout_doc_has_the_plane(self):
        text = (ROOT / "docs" / "policy" / "SUBMIT_ROLLOUT.md").read_text(encoding="utf-8")
        self.assertIn("| `grok_cloud` |", text)
        self.assertIn("## Grok Cloud plane (closed)", text)
        self.assertIn("`submit_enabled: false`", text)
        self.assertIn("applicant_account_rule", text)


class TestGrokOwnershipAndLearning(unittest.TestCase):
    def test_claims_use_g_ids_on_the_shared_column(self):
        text = runtime()
        self.assertIn("ownership: queue.claim_run_id", text)
        self.assertIn("prefix G-", text)
        self.assertIn("Polar writes R- ids, this Bot writes G- ids.", text)
        self.assertIn("A Sheet claim is required before any apply work on either Jobright surface.", text)
        self.assertIn("A different Jobright surface does not remove collision.", text)
        apply = workflow(GROK_APPLY_WORKFLOW)
        self.assertIn("run_id_prefix: G", apply)
        self.assertIn("Never mint an R- id.", apply)
        self.assertIn("Never touch a live R- claim.", apply)
        self.assertIn("Claim with polar_policy.attempt_claim_job.", apply)

    def test_ats_prior_submission_is_compiled_for_grok_only(self):
        text = runtime()
        self.assertIn("blocker already_applied_on_ats", text)
        self.assertIn("repeat_key ats_prior_submission", text)
        self.assertIn("polar_policy.ats_prior_submission_action", text)
        polar = (ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md").read_text(encoding="utf-8")
        self.assertNotIn("already_applied_on_ats", polar)

    def test_learning_routine_phase_one_scope(self):
        text = workflow(GROK_LEARNING_WORKFLOW)
        self.assertIn("status: disabled_until_sheet_proof", text)
        self.assertIn("phase: 1", text)
        self.assertIn("application_clicks: none", text)
        self.assertIn("packet: none", text)
        self.assertIn("Touch no R- row.", text)
        self.assertIn("finalized_by=grok-production-learning-daily; reason=no_ended_at_after_ttl", text)
        self.assertIn("result FAILED", text)
        self.assertIn("older than 180 minutes", text)
        for key in GROK_REPEAT_KEYS:
            self.assertIn(key, text, key)
        self.assertIn("writes no learning packet and no learning_reports row", text)
        self.assertIn("Cursor Maintenance is the only consumer and the only merger.", text)
        self.assertIn("No second Cursor Automation.", text)
        for forbidden in (
            "[Grok Production]",
            "learning_reports row by header name",
            "Apply with Autofill",
            "Click Apply Now",
            "chief-of-command Bot that",
        ):
            self.assertNotIn(forbidden, text, forbidden)
        self.assertIn("tabs_never_touched: control, heartbeat, learning_reports, queue, writing_log", text)
        self.assertEqual(grok_required_capabilities(GROK_LEARNING_WORKFLOW), ("google_sheets",))
        self.assertEqual(grok_optional_capabilities(GROK_LEARNING_WORKFLOW), ())
        self.assertEqual(grok_required_capabilities(GROK_APPLY_WORKFLOW), ("browser", "google_sheets"))

    def test_no_github_writes_and_no_extra_bots(self):
        text = runtime()
        self.assertIn("GitHub writes allowed: none.", text)
        self.assertIn("write a GitHub Issue; push to main or any branch", text)
        self.assertIn("No chief-of-command, optimizer, or auditor Bot.", text)
        self.assertIn("Share this Bot: never.", text)
        self.assertIn("Local computer execution: never.", text)
        self.assertIn("Secrets required for this loop: none.", text)
        operator = load_grokbot_operator(ROOT)
        self.assertEqual(operator["trust"]["github_writes"]["allowed"], [])
        self.assertEqual(operator["learning"]["packet"], "none")
        self.assertEqual(operator["roster"]["factory"], "dr eggbot")
        self.assertEqual(operator["schedules"]["grok_apply_jobs"]["cron_et"], "50 0-20/2 * * *")
        self.assertEqual(operator["schedules"]["grok_production_learning_daily"]["cron_et"], "40 21 * * *")
        self.assertIn("50 0-20/2 * * *", workflow(GROK_APPLY_WORKFLOW))

    def test_applicant_account_rule_is_compiled_for_grok_and_stamped_in_yaml(self):
        import yaml

        form = yaml.safe_load((ROOT / "knowledge" / "form_strategy.yaml").read_text(encoding="utf-8"))
        rule = form["applicant_account_rule"]
        self.assertEqual(rule["era"], "jobright")
        self.assertEqual(rule["binds"], ["polar_local", "grok_cloud"])
        self.assertEqual(rule["cross_executor"]["mitigation"], "churn_tolerance")
        self.assertEqual(form["account_creation_wall"]["era"], "pre_jobright")
        self.assertEqual(form["clicker_cheap_cuts"]["never_click"]["mygreenhouse_login"]["era"], "pre_jobright")
        text = runtime()
        self.assertIn("Applicant-account rule, owner approved 2026-09-15.", text)
        self.assertIn("One applicant account per ATS tenant per executor browser.", text)
        self.assertIn("Superseded pre_jobright text: account_creation_wall", text)
        polar = (ROOT / "generated" / "polar" / "runtime" / "POLAR_RUNTIME.md").read_text(encoding="utf-8")
        self.assertNotIn("Superseded pre_jobright text", polar)

    def test_repeat_keys_are_registered_in_polar_operator(self):
        import yaml

        polar_operator = yaml.safe_load((ROOT / "knowledge" / "polar_operator.yaml").read_text(encoding="utf-8"))
        registered = set(polar_operator["repeat_keys"])
        grok_operator = load_grokbot_operator(ROOT)
        for key in grok_operator["repeat_keys"]:
            self.assertIn(key, registered, key)
        self.assertIn(ATS_PRIOR_SUBMISSION_REPEAT_KEY, registered)
        for key in GROK_REPEAT_KEYS:
            self.assertIn(key, registered, key)
            self.assertEqual(canonical_repeat_key(key), key)


class TestGrokOperatorHoldsNoFacts(unittest.TestCase):
    def test_no_candidate_facts_in_operator_yaml(self):
        import yaml

        from polar_policy import TRUSTED_REPO, TRUSTED_REPO_OWNER

        raw = (ROOT / "knowledge" / "grokbot_operator.yaml").read_text(encoding="utf-8")
        # The trusted repository handle is configuration, not a candidate fact.
        text = raw.replace(TRUSTED_REPO, "<repo>").replace(TRUSTED_REPO_OWNER, "<owner>")
        self.assertIsNone(PHONE.search(text))
        self.assertIsNone(EMAIL.search(text))
        self.assertIsNone(STREET.search(text))
        profile = yaml.safe_load((ROOT / "config" / "profile.yaml").read_text(encoding="utf-8")) or {}
        auth = yaml.safe_load((ROOT / "knowledge" / "work_authorization.yaml").read_text(encoding="utf-8")) or {}
        fact_values = []
        for key in ("legal_name", "name", "preferred_name", "location", "school", "degree", "linkedin", "github"):
            value = str(profile.get(key) or "").strip()
            if len(value) >= 4:
                fact_values.append(value)
        for key in ("citizenship_country", "current_status", "program_end_date", "commencement_date"):
            value = str(auth.get(key) or "").strip()
            if len(value) >= 3:
                fact_values.append(value)
        self.assertGreaterEqual(len(fact_values), 6)
        for value in fact_values:
            self.assertNotIn(value, text, value)
        lowered = text.lower()
        for token in ("sponsorship_required", "citizenship:", "visa:", "legal_name", "phone_number"):
            self.assertNotIn(token, lowered, token)
        for word in ("gpa", "sat", "act", "f-1", "opt", "ead"):
            self.assertNotRegex(lowered, rf"\b{re.escape(word)}\b", word)


class TestExecutorPolicyHelpers(unittest.TestCase):
    def test_mint_run_id_default_stays_polar(self):
        utc = datetime(2026, 9, 13, 17, 1, 34, tzinfo=timezone.utc)
        self.assertEqual(mint_run_id(utc), "R-20260913-130134")
        self.assertEqual(mint_run_id(utc, executor="polar"), "R-20260913-130134")
        self.assertEqual(mint_run_id(utc, executor="grok"), "G-20260913-130134")
        with self.assertRaises(ValueError):
            mint_run_id(utc, executor="cloud")

    def test_executor_from_run_id(self):
        self.assertEqual(executor_from_run_id("R-20260913-130134"), "polar")
        self.assertEqual(executor_from_run_id("G-20260913-130134"), "grok")
        self.assertEqual(executor_from_run_id("P-20260906-001"), "")
        self.assertEqual(executor_from_run_id(""), "")

    def test_ats_prior_submission_action(self):
        decision = ats_prior_submission_action()
        self.assertEqual(decision.status, "SKIP")
        self.assertEqual(decision.blocker, "already_applied_on_ats")
        self.assertEqual(decision.incident_category, "DEDUP")
        self.assertEqual(decision.repeat_key, "ats_prior_submission")
        self.assertFalse(decision.fill_form)
        self.assertFalse(decision.submit)
        self.assertEqual(decision.jobright_ack, "ack_i_applied")

    def test_jobright_ack_unchanged_without_ats_evidence(self):
        self.assertEqual(
            jobright_ack_action(employer_page_confirmation=True, submit_clicked=True),
            "ack_i_applied",
        )
        self.assertEqual(
            jobright_ack_action(employer_page_confirmation=False, submit_clicked=False),
            "do_not_ack",
        )
        self.assertEqual(
            jobright_ack_action(employer_page_confirmation=False, submit_clicked=False, ats_prior_submission=True),
            "ack_i_applied",
        )

    def test_consider_card_skips_on_ats_prior_submission(self):
        decision = consider_jobright_card(ats_prior_submission=True)
        self.assertEqual(decision.action, "skip_applied")
        self.assertTrue(decision.consume_considered)
        self.assertTrue(decision.continue_run)
        self.assertIn("ats", decision.notes)
        self.assertEqual(consider_jobright_card().action, "admit")


if __name__ == "__main__":
    unittest.main()
