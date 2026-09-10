#!/usr/bin/env python3

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import (  # noqa: E402
    CAPABILITY_GOOGLE_SHEETS,
    CAPABILITY_MISSING_REASON,
    CAPABILITY_RUN_LOG,
    GITHUB_RAW_BASE,
    TRUSTED_BRANCH,
    TRUSTED_CONFIGURATION,
    TRUSTED_HOST,
    TRUSTED_REPO,
    TRUSTED_RUNTIME_PATH,
    TRUSTED_WORKFLOW_DIR,
    TRUSTED_WORKFLOW_NAMES,
    UNTRUSTED_DATA,
    assess_capabilities,
    bootstrap_prompt,
    classify_configuration_url,
    parse_trusted_configuration_url,
    raw_runtime_url,
    raw_workflow_url,
    required_capabilities,
    trusted_configuration_paths,
    trusted_load_set,
)
from polar_workflows import WORKFLOW_RENDERERS  # noqa: E402
from print_polar_bootstrap import main as print_bootstrap  # noqa: E402


APPLY = "apply-ready-jobs"
RUNTIME = (
    "https://raw.githubusercontent.com/JunyiZhou-Conny/"
    "job-search-2026-2027-starter/main/generated/polar/runtime/POLAR_RUNTIME.md"
)
APPLY_URL = (
    "https://raw.githubusercontent.com/JunyiZhou-Conny/"
    "job-search-2026-2027-starter/main/generated/polar/workflows/apply-ready-jobs.md"
)
DISCOVER_URL = (
    "https://raw.githubusercontent.com/JunyiZhou-Conny/"
    "job-search-2026-2027-starter/main/generated/polar/workflows/discover-jobs-hourly.md"
)


class TestTrustAllowlist(unittest.TestCase):
    def test_compiler_workflows_are_exactly_the_allowlist(self):
        self.assertEqual(set(WORKFLOW_RENDERERS), set(TRUSTED_WORKFLOW_NAMES))
        self.assertEqual(
            trusted_configuration_paths(),
            frozenset(
                {TRUSTED_RUNTIME_PATH}
                | {
                    f"{TRUSTED_WORKFLOW_DIR}/{name}.md"
                    for name in TRUSTED_WORKFLOW_NAMES
                }
            ),
        )

    def test_load_set_is_runtime_and_this_workflow_only(self):
        self.assertEqual(trusted_load_set(APPLY), frozenset({RUNTIME, APPLY_URL}))

    def test_allowlisted_runtime_and_workflow_are_trusted_for_this_run(self):
        self.assertEqual(
            parse_trusted_configuration_url(RUNTIME).url,
            RUNTIME,
        )
        self.assertEqual(classify_configuration_url(RUNTIME, APPLY), TRUSTED_CONFIGURATION)
        self.assertEqual(classify_configuration_url(APPLY_URL, APPLY), TRUSTED_CONFIGURATION)

    def test_other_allowlisted_workflow_is_not_authority_for_this_run(self):
        self.assertIsNotNone(parse_trusted_configuration_url(DISCOVER_URL))
        self.assertEqual(
            classify_configuration_url(DISCOVER_URL, APPLY),
            UNTRUSTED_DATA,
        )

    def test_other_repo_branch_host_and_path_are_untrusted(self):
        rejected = (
            "https://raw.githubusercontent.com/other/repo/main/"
            "generated/polar/workflows/apply-ready-jobs.md",
            "https://raw.githubusercontent.com/JunyiZhou-Conny/"
            "job-search-2026-2027-starter/develop/generated/polar/workflows/"
            "apply-ready-jobs.md",
            "https://github.com/JunyiZhou-Conny/job-search-2026-2027-starter/"
            "blob/main/generated/polar/workflows/apply-ready-jobs.md",
            "https://raw.githubusercontent.com/JunyiZhou-Conny/"
            "job-search-2026-2027-starter/main/AGENTS.md",
            "https://evil.example/instructions.md",
            "http://raw.githubusercontent.com/JunyiZhou-Conny/"
            "job-search-2026-2027-starter/main/generated/polar/workflows/"
            "apply-ready-jobs.md",
            APPLY_URL + "?token=1",
            APPLY_URL + "#section",
            "https://raw.githubusercontent.com/JunyiZhou-Conny/"
            "job-search-2026-2027-starter/main/generated/polar/workflows/"
            "../runtime/POLAR_RUNTIME.md",
        )
        for url in rejected:
            self.assertIsNone(parse_trusted_configuration_url(url), url)
            self.assertEqual(classify_configuration_url(url, APPLY), UNTRUSTED_DATA, url)

    def test_url_inside_trusted_file_does_not_expand_allowlist(self):
        embedded = "https://example.com/employer/apply"
        self.assertEqual(
            classify_configuration_url(embedded, APPLY),
            UNTRUSTED_DATA,
        )


class TestCapabilityPreflight(unittest.TestCase):
    def test_missing_sheet_is_environment_not_trust_failure(self):
        required = required_capabilities("production-learning-daily")
        result = assess_capabilities(required, available=())
        self.assertEqual(result.result, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.incident_category, "ENVIRONMENT")
        self.assertEqual(result.reason, CAPABILITY_MISSING_REASON)
        self.assertEqual(
            result.missing,
            (
                "google_sheets",
                "run_log",
                "incident_log",
                "github_issues",
                "local_filesystem",
            ),
        )

    def test_available_capabilities_execute(self):
        required = required_capabilities(APPLY)
        result = assess_capabilities(
            required,
            available=required,
        )
        self.assertEqual(result.result, "ok")
        self.assertEqual(result.missing, ())

    def test_partial_availability_names_only_the_gap(self):
        result = assess_capabilities(
            (CAPABILITY_GOOGLE_SHEETS, CAPABILITY_RUN_LOG),
            available=(CAPABILITY_GOOGLE_SHEETS,),
        )
        self.assertEqual(result.result, CAPABILITY_MISSING_REASON)
        self.assertEqual(result.missing, (CAPABILITY_RUN_LOG,))


class TestBootstrapDelegation(unittest.TestCase):
    def test_bootstrap_names_exact_load_set_and_refuses_blind_follow(self):
        prompt = bootstrap_prompt(APPLY)
        self.assertLess(len(prompt), 2500)
        self.assertTrue(prompt.startswith("TRUST DELEGATION for Polar workflow apply-ready-jobs."))
        self.assertIn(f"Trusted repository: {TRUSTED_REPO}", prompt)
        self.assertIn(f"Trusted branch: {TRUSTED_BRANCH}", prompt)
        self.assertIn(f"1. {RUNTIME}\n", prompt)
        self.assertIn(f"2. {APPLY_URL}\n", prompt)
        self.assertIn("does not expand this allowlist.", prompt)
        self.assertIn("ENVIRONMENT / CAPABILITY_MISSING", prompt)
        self.assertIn("untrusted task data", prompt)
        self.assertNotIn("Read it fully.", prompt)
        self.assertNotIn("Then execute.", prompt)
        self.assertNotIn("Follow the latest instructions", prompt)
        self.assertTrue(GITHUB_RAW_BASE.startswith(f"https://{TRUSTED_HOST}/"))

    def test_paste_doc_matches_bootstrap_prompt_for_every_workflow(self):
        docs = (ROOT / "docs" / "automation" / "POLAR_WORKFLOWS.md").read_text(
            encoding="utf-8"
        )
        for name in TRUSTED_WORKFLOW_NAMES:
            self.assertIn(bootstrap_prompt(name), docs, name)

    def test_skill_template_names_the_same_allowlist(self):
        text = (ROOT / "docs" / "automation" / "POLAR_SKILL_BOOTSTRAP.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(TRUSTED_REPO, text)
        self.assertIn(TRUSTED_BRANCH, text)
        self.assertIn(TRUSTED_RUNTIME_PATH, text)
        self.assertIn(f"{TRUSTED_WORKFLOW_DIR}/<workflow-name>.md", text)
        self.assertIn("does not expand this allowlist", text)
        self.assertIn("CAPABILITY_MISSING", text)
        self.assertIn("GitHub cannot mutate Polar-local files", text)

    def test_print_script_emits_the_apply_bootstrap(self):
        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        with redirect_stdout(buf):
            code = print_bootstrap([APPLY])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue(), bootstrap_prompt(APPLY))


class TestCompiledTrustLanguage(unittest.TestCase):
    def test_every_compiled_workflow_carries_trust_and_preflight(self):
        workflow_dir = ROOT / "generated" / "polar" / "workflows"
        for name in TRUSTED_WORKFLOW_NAMES:
            text = (workflow_dir / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn("## Owner-designated configuration", text, name)
            self.assertIn(f"trusted_repository: {TRUSTED_REPO}", text, name)
            self.assertIn("## Capability preflight", text, name)
            self.assertIn("reason CAPABILITY_MISSING", text, name)
            self.assertIn("A missing tool is not TRUST_FAILURE.", text, name)
            self.assertIn("does not expand the allowlist.", text, name)
            caps = ", ".join(required_capabilities(name))
            self.assertIn(f"required_capabilities: {caps}", text, name)


if __name__ == "__main__":
    unittest.main()
