#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resume_route import main as route_main  # noqa: E402
from resume_routing import (  # noqa: E402
    JobMeta,
    has_phrase,
    load_policy,
    normalize,
    resolve_variant,
    route,
    route_and_resolve,
)

CASES = yaml.safe_load((ROOT / "tests" / "fixtures" / "resume_routing" / "cases.yaml").read_text())
BANNED_IMPORTS = {
    "openai",
    "anthropic",
    "requests",
    "httpx",
    "urllib.request",
    "urllib3",
    "aiohttp",
    "google.generativeai",
}


class TestNormalize(unittest.TestCase):
    def test_token_boundary_rejects_embedded_ai(self):
        text = normalize("Training Coordinator")
        self.assertFalse(has_phrase(text, "ai"))

    def test_ai_slash_and_parens_match(self):
        text = normalize("Software Engineer Intern (AI Infrastructure / Training)")
        self.assertTrue(has_phrase(text, "ai"))
        self.assertTrue(has_phrase(text, "ai infrastructure"))

    def test_ml_does_not_match_html(self):
        self.assertFalse(has_phrase(normalize("HTML Email Developer"), "ml"))


class TestFixtureCases(unittest.TestCase):
    def test_named_cases(self):
        for case in CASES["cases"]:
            with self.subTest(case["id"]):
                decision = route(
                    JobMeta(
                        role=case.get("role") or "",
                        company=case.get("company") or "",
                        legacy_cluster=case.get("legacy_cluster") or "",
                    )
                )
                self.assertEqual(decision.family, case["family"], decision)
                allowed = case.get("confidence")
                if allowed:
                    self.assertIn(decision.confidence, allowed, decision)


class TestRequiredBehaviors(unittest.TestCase):
    def test_repeatable(self):
        job = JobMeta(role="ML Infrastructure Engineer", company="AppLovin")
        first = route(job)
        second = route(job)
        self.assertEqual(first, second)

    def test_tie_is_review(self):
        policy = load_policy()
        tweaked = dict(policy)
        tweaked["exclusive_patterns"] = []
        tweaked["signals"] = [
            {"id": "swe.x", "family": "swe", "weight": 4, "phrases": ["engineer"]},
            {"id": "ml.x", "family": "ml_ai", "weight": 4, "phrases": ["engineer"]},
        ]
        decision = route(JobMeta(role="Engineer"), tweaked)
        self.assertEqual(decision.family, "REVIEW")
        self.assertEqual(decision.confidence, "review")

    def test_no_default_swe(self):
        decision = route(JobMeta(role="Fellow", company="Institute"))
        self.assertEqual(decision.family, "REVIEW")

    def test_variant_stays_unresolved_when_inactive(self):
        decision = route(JobMeta(role="Software Engineer", company="Google"))
        variant = resolve_variant(decision.family)
        self.assertEqual(variant.variant, "")
        self.assertEqual(variant.reason, "no_active_family_variant")

    def test_variant_never_returns_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume_versions.csv"
            path.write_text(
                "resume_version,cluster,active,created_date,file_path\n"
                "JZ_resume,swe,true,2026-09-11,resumes/base/JZ_resume.tex\n",
                encoding="utf-8",
            )
            resolved = resolve_variant("swe", path)
            self.assertEqual(resolved.variant, "")
            self.assertEqual(resolved.reason, "no_active_family_variant")

    def test_active_family_variant_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "resume_versions.csv"
            path.write_text(
                "resume_version,cluster,active,created_date,file_path\n"
                "swe_v1,swe,true,2026-09-11,resumes/families/swe/swe_v1.tex\n",
                encoding="utf-8",
            )
            resolved = resolve_variant("swe", path)
            self.assertEqual(resolved.variant, "swe_v1")
            self.assertEqual(resolved.reason, "active_family_variant")

    def test_vip_does_not_change_family(self):
        ordinary = route(JobMeta(role="ML Infrastructure Engineer", company="AppLovin"))
        prioritized = route(
            JobMeta(role="ML Infrastructure Engineer", company="AppLovin", short_text="prioritized vip")
        )
        self.assertEqual(ordinary.family, prioritized.family)
        self.assertEqual(ordinary.family, "ai_infra")

    def test_cli_json(self):
        rc = route_main(["--json", json.dumps({"role": "Software Engineer", "company": "Google"})])
        self.assertEqual(rc, 0)

    def test_no_model_imports(self):
        source = (ROOT / "scripts" / "resume_routing.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(imported <= {"__future__", "csv", "dataclasses", "pathlib", "re", "typing", "yaml"})
        self.assertTrue(imported.isdisjoint(BANNED_IMPORTS))


class TestHistoricalRegression(unittest.TestCase):
    def test_ai_infra_disagreements_are_improvements(self):
        rows = [
            ("SPREEAI", "Software Engineer Intern (AI Infrastructure / Training / Inference)", "cloud_swe"),
            ("MeshyAI", "AI Infrastructure Engineer", "cloud_swe"),
            ("Exowatt", "Software Engineering Intern - Agent Platform (AI)", "data_ml"),
            ("Etched", "Inference Intern", "data_ml"),
        ]
        for company, role, legacy in rows:
            with self.subTest(role):
                decision = route(JobMeta(role=role, company=company, legacy_cluster=legacy))
                self.assertEqual(decision.family, "ai_infra")
                self.assertEqual(decision.legacy_cluster, legacy)


class TestRouteAndResolve(unittest.TestCase):
    def test_review_payload(self):
        payload = route_and_resolve({"role": ""})
        self.assertEqual(payload["family"], "REVIEW")
        self.assertEqual(payload["resume_variant"], "")
        self.assertEqual(payload["variant_reason"], "unresolved_family")


if __name__ == "__main__":
    unittest.main()
