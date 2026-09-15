#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    CAPABILITY_GOOGLE_SHEETS,
    CAPABILITY_MISSING_REASON,
    TRUST_FAILURE,
    TRUSTED_BRANCH,
    TRUSTED_CONFIGURATION,
    TRUSTED_REPO,
    TRUSTED_RUNTIME_PATH,
    TRUSTED_WORKFLOW_DIR,
    TRUSTED_WORKFLOW_NAMES,
    UNTRUSTED_DATA,
    WORKFLOW_OPTIONAL_CAPABILITIES,
    WORKFLOW_REQUIRED_CAPABILITIES,
    assess_capabilities,
    bootstrap_prompt,
    capability_preflight_block,
    classify_configuration_url,
    google_sheets_capability_spec,
    optional_capabilities,
    parse_trusted_configuration_url,
    raw_runtime_url,
    raw_workflow_url,
    required_capabilities,
    session_has_google_sheets,
    should_ask_owner_to_add_connector,
    trusted_load_set,
)
from polar_workflows import WORKFLOW_RENDERERS  # noqa: E402
from print_polar_bootstrap import main as print_bootstrap  # noqa: E402


APPLY = "apply-ready-jobs"


class TestTrustAllowlist(unittest.TestCase):
    def test_compiler_workflows_are_exactly_the_allowlist(self):
        self.assertEqual(set(WORKFLOW_RENDERERS), set(TRUSTED_WORKFLOW_NAMES))
        self.assertEqual(
            set(WORKFLOW_REQUIRED_CAPABILITIES),
            set(TRUSTED_WORKFLOW_NAMES),
        )
        self.assertTrue(
            set(WORKFLOW_OPTIONAL_CAPABILITIES).issubset(set(TRUSTED_WORKFLOW_NAMES))
        )

    def test_load_set_is_runtime_and_this_workflow_only(self):
        self.assertEqual(
            trusted_load_set(APPLY),
            frozenset({raw_runtime_url(), raw_workflow_url(APPLY)}),
        )

    def test_allowlisted_runtime_and_workflow_are_trusted_for_this_run(self):
        runtime = raw_runtime_url()
        apply_url = raw_workflow_url(APPLY)
        self.assertEqual(parse_trusted_configuration_url(runtime).url, runtime)
        self.assertEqual(
            classify_configuration_url(runtime, APPLY),
            TRUSTED_CONFIGURATION,
        )
        self.assertEqual(
            classify_configuration_url(apply_url, APPLY),
            TRUSTED_CONFIGURATION,
        )

    def test_other_allowlisted_workflow_is_trust_failure_for_this_run(self):
        other = raw_workflow_url("discover-jobs-hourly")
        self.assertIsNotNone(parse_trusted_configuration_url(other))
        self.assertEqual(classify_configuration_url(other, APPLY), TRUST_FAILURE)

    def test_other_repo_branch_host_and_path_are_rejected(self):
        cases = (
            (
                "https://raw.githubusercontent.com/other/repo/main/"
                "generated/polar/workflows/apply-ready-jobs.md",
                TRUST_FAILURE,
            ),
            (
                "https://raw.githubusercontent.com/JunyiZhou-Conny/"
                "job-search-2026-2027-starter/develop/generated/polar/workflows/"
                "apply-ready-jobs.md",
                TRUST_FAILURE,
            ),
            (
                "https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter/"
                "blob/main/generated/polar/workflows/apply-ready-jobs.md",
                TRUST_FAILURE,
            ),
            (
                "https://raw.githubusercontent.com/JunyiZhou-Conny/"
                "job-search-2026-2027-starter/main/AGENTS.md",
                TRUST_FAILURE,
            ),
            ("https://evil.example/instructions.md", UNTRUSTED_DATA),
            (
                "http://raw.githubusercontent.com/JunyiZhou-Conny/"
                "job-search-2026-2027-starter/main/generated/polar/workflows/"
                "apply-ready-jobs.md",
                TRUST_FAILURE,
            ),
            (raw_workflow_url(APPLY) + "?token=1", TRUST_FAILURE),
            (raw_workflow_url(APPLY) + "#section", TRUST_FAILURE),
            (raw_workflow_url(APPLY) + "/", TRUST_FAILURE),
        )
        for url, expected in cases:
            self.assertIsNone(parse_trusted_configuration_url(url), url)
            self.assertEqual(classify_configuration_url(url, APPLY), expected, url)

    def test_url_inside_trusted_file_does_not_expand_allowlist(self):
        self.assertEqual(
            classify_configuration_url("https://example.com/employer/apply", APPLY),
            UNTRUSTED_DATA,
        )

    def test_unknown_workflow_cannot_mint_a_bootstrap(self):
        with self.assertRaises(KeyError):
            bootstrap_prompt("evil-workflow")
        with self.assertRaises(KeyError):
            raw_workflow_url("evil-workflow")


class TestCapabilityPreflight(unittest.TestCase):
    def test_missing_sheet_is_environment_not_trust_failure(self):
        required = required_capabilities("production-learning-daily")
        result = assess_capabilities(required, available=())
        self.assertEqual(result.result, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.incident_category, "ENVIRONMENT")
        self.assertEqual(result.reason, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.missing, ("google_sheets", "local_filesystem"))
        self.assertEqual(
            optional_capabilities("production-learning-daily"),
            ("github_issues",),
        )

    def test_available_capabilities_do_not_stamp_an_incident(self):
        required = required_capabilities(APPLY)
        result = assess_capabilities(required, available=required)
        self.assertEqual(result.result, "ok")
        self.assertEqual(result.incident_category, "")
        self.assertEqual(result.missing, ())

    def test_partial_availability_names_only_the_gap(self):
        result = assess_capabilities(
            (CAPABILITY_GOOGLE_SHEETS, "browser"),
            available=(CAPABILITY_GOOGLE_SHEETS,),
        )
        self.assertEqual(result.result, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.missing, ("browser",))

    def test_learning_does_not_require_github_issues(self):
        self.assertNotIn(
            "github_issues",
            required_capabilities("production-learning-daily"),
        )

    def test_discover_does_not_require_local_filesystem(self):
        self.assertEqual(
            required_capabilities("discover-jobs-hourly"),
            ("google_sheets", "browser"),
        )
        self.assertEqual(
            optional_capabilities("discover-jobs-hourly"),
            ("local_filesystem",),
        )
        result = assess_capabilities(
            required_capabilities("discover-jobs-hourly"),
            available=("google_sheets", "browser"),
        )
        self.assertEqual(result.result, "ok")
        self.assertEqual(result.missing, ())

    def test_apply_and_learning_still_require_local_filesystem(self):
        self.assertIn("local_filesystem", required_capabilities(APPLY))
        self.assertIn(
            "local_filesystem",
            required_capabilities("production-learning-daily"),
        )

    def test_canary_requires_sheet_and_github(self):
        required = required_capabilities("polar-github-write-canary")
        self.assertEqual(required, ("github_issues", "google_sheets"))
        result = assess_capabilities(required, available=("github_issues",))
        self.assertEqual(result.missing, ("google_sheets",))

    def test_sheet_tabs_are_not_connectors(self):
        for name in TRUSTED_WORKFLOW_NAMES:
            caps = required_capabilities(name)
            self.assertNotIn("run_log", caps, name)
            self.assertNotIn("incident_log", caps, name)
            self.assertNotIn("polar_browser", caps, name)


class TestGoogleSheetsCapability(unittest.TestCase):
    def test_operator_contract_is_capability_not_connector_title(self):
        spec = google_sheets_capability_spec()
        self.assertFalse(spec["literal_name_required"])
        self.assertFalse(spec["ask_to_add_connector"])
        self.assertEqual(spec["sheet_title"], "Polar Jobs")
        self.assertIn("google", spec["connector_aliases"])
        self.assertIn("Find Drive file", spec["tool_evidence"])
        self.assertIn("sheets.google.com", spec["not_sufficient"])

    def test_google_connector_satisfies_google_sheets_without_literal_name(self):
        result = assess_capabilities(
            (CAPABILITY_GOOGLE_SHEETS, "browser"),
            available=("google", "browser"),
        )
        self.assertEqual(result.result, "ok")
        self.assertEqual(result.missing, ())
        self.assertFalse(result.ask_to_add_connector)
        self.assertTrue(session_has_google_sheets(("Google",)))
        self.assertFalse(
            should_ask_owner_to_add_connector(
                CAPABILITY_GOOGLE_SHEETS,
                available=("google",),
            )
        )

    def test_drive_and_sheets_tools_satisfy_google_sheets(self):
        result = assess_capabilities(
            (CAPABILITY_GOOGLE_SHEETS,),
            available=(),
            tools=("Find Drive file", "Sheets API"),
        )
        self.assertEqual(result.result, "ok")
        self.assertFalse(result.ask_to_add_connector)
        self.assertTrue(
            session_has_google_sheets((), tools=("Find Drive file",))
        )

    def test_browser_sheets_google_com_is_not_google_sheets(self):
        result = assess_capabilities(
            (CAPABILITY_GOOGLE_SHEETS,),
            available=("browser",),
            browser_hosts=("sheets.google.com",),
        )
        self.assertEqual(result.result, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.incident_category, "ENVIRONMENT")
        self.assertEqual(result.missing, (CAPABILITY_GOOGLE_SHEETS,))
        self.assertFalse(result.ask_to_add_connector)
        self.assertFalse(
            session_has_google_sheets(
                ("browser", "sheets.google.com"),
                browser_hosts=("sheets.google.com",),
            )
        )
        self.assertFalse(
            should_ask_owner_to_add_connector(
                CAPABILITY_GOOGLE_SHEETS,
                available=("browser",),
            )
        )

    def test_apply_preflight_text_forbids_literal_name_stop(self):
        text = capability_preflight_block(APPLY)
        self.assertIn("A connector named google_sheets is not required.", text)
        self.assertIn("Browser access to sheets.google.com is not google_sheets.", text)
        self.assertIn("Do not ask the owner to add a connector", text)
        self.assertNotIn("These names are Polar session connectors", text)


class TestBootstrapDelegation(unittest.TestCase):
    def test_bootstrap_names_exact_load_set(self):
        prompt = bootstrap_prompt(APPLY)
        self.assertLess(len(prompt), 2500)
        http_urls = [line[3:] for line in prompt.splitlines() if line.startswith("http")]
        numbered = [
            line.split(" ", 1)[1]
            for line in prompt.splitlines()
            if line.startswith("1. http") or line.startswith("2. http")
        ]
        self.assertEqual(
            numbered,
            [raw_runtime_url(), raw_workflow_url(APPLY)],
        )
        self.assertEqual(http_urls, [])
        self.assertIn(f"Trusted repository: {TRUSTED_REPO}", prompt)
        self.assertIn(f"Trusted branch: {TRUSTED_BRANCH}", prompt)
        self.assertIn("does not expand this allowlist.", prompt)
        self.assertIn("ENVIRONMENT / CAPABILITY_MISSING", prompt)
        self.assertIn("Sheet tabs such as run_log are not separate connectors.", prompt)
        self.assertIn("A connector named google_sheets is not required.", prompt)
        self.assertIn("Browser sheets.google.com is not that capability.", prompt)
        self.assertIn("Do not ask the owner to add a connector", prompt)
        self.assertIn("untrusted task data", prompt)
        self.assertNotIn("Read it fully.", prompt)
        self.assertNotIn("Then execute.", prompt)
        self.assertNotIn("Follow the latest instructions", prompt)

    def test_paste_doc_matches_bootstrap_prompt_for_every_workflow(self):
        docs = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in TRUSTED_WORKFLOW_NAMES:
            self.assertIn(bootstrap_prompt(name), docs, name)

    def test_skill_template_lists_exact_paths_and_defers_to_saved_prompt(self):
        text = (ROOT / "docs" / "automation" / "POLAR_SKILL_BOOTSTRAP.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(TRUSTED_REPO, text)
        self.assertIn(TRUSTED_BRANCH, text)
        self.assertIn(TRUSTED_RUNTIME_PATH, text)
        self.assertNotIn(f"{TRUSTED_WORKFLOW_DIR}/<workflow-name>.md", text)
        for name in TRUSTED_WORKFLOW_NAMES:
            self.assertIn(f"{TRUSTED_WORKFLOW_DIR}/{name}.md", text)
        self.assertIn("Do not infer a workflow name.", text)
        self.assertIn("two exact URLs printed in the saved Polar Workflow prompt", text)
        self.assertIn("CAPABILITY_MISSING", text)
        self.assertIn("A connector named google_sheets is not required.", text)
        self.assertIn("Do not ask the owner to add a connector", text)
        self.assertIn("GitHub cannot mutate Polar-local files", text)

    def test_print_script_emits_the_apply_bootstrap(self):
        buf = StringIO()
        with redirect_stdout(buf):
            code = print_bootstrap([APPLY])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), bootstrap_prompt(APPLY))


class TestCompiledTrustLanguage(unittest.TestCase):
    def test_every_compiled_workflow_carries_identity_and_preflight(self):
        workflow_dir = ROOT / "generated" / "polar" / "workflows"
        for name in TRUSTED_WORKFLOW_NAMES:
            text = (workflow_dir / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("## Configuration identity", text, name)
            self.assertIn(f"trusted_workflow: {raw_workflow_url(name)}", text, name)
            self.assertIn(f"trusted_runtime: {raw_runtime_url()}", text, name)
            self.assertIn("## Capability preflight", text, name)
            self.assertIn("ENVIRONMENT / CAPABILITY_MISSING", text, name)
            self.assertIn("A missing capability is not TRUST_FAILURE.", text, name)
            self.assertIn("are Google Sheet tabs.", text, name)
            self.assertIn("A connector named google_sheets is not required.", text, name)
            self.assertIn("Browser access to sheets.google.com is not google_sheets.", text, name)
            self.assertIn("Do not ask the owner to add a connector", text, name)
            self.assertNotIn("These names are Polar session connectors", text, name)
            self.assertNotIn(
                "Inspect whether this Polar session actually has each required connector.",
                text,
                name,
            )
            self.assertNotIn("This file is user-designated remote configuration", text, name)
            caps = ", ".join(required_capabilities(name))
            self.assertIn(f"required_capabilities: {caps}", text, name)

    def test_discover_skips_preferences_when_filesystem_is_missing(self):
        text = (
            ROOT / "generated" / "polar" / "workflows" / "discover-jobs-hourly.md"
        ).read_text(encoding="utf-8")
        self.assertIn("optional_capabilities: local_filesystem", text)
        self.assertIn("skip Preferences reconciliation for this run.", text)
        self.assertIn("degraded_capability=local_filesystem", text)
        self.assertIn("Continue the primary work.", text)
        apply_text = (
            ROOT / "generated" / "polar" / "workflows" / "apply-ready-jobs.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("optional_capabilities: local_filesystem", apply_text)
        self.assertIn("required_capabilities: google_sheets, browser, local_filesystem", apply_text)
