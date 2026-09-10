#!/usr/bin/env python3
"""Behavior tests for the Resume Quality Engine."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from rqe.judge import validate_tex  # noqa: E402
from rqe.jd import parse_jd  # noqa: E402
from rqe.load import (  # noqa: E402
    BANK_PATH,
    assert_catalog_grounded,
    load_bank,
    load_yaml,
)
from rqe.plan import build_strategy, match_job  # noqa: E402
from rqe.render import BaseDoc, build_candidate  # noqa: E402
from resume_quality import main as rqe_main  # noqa: E402


def _usable_claim(bank, project_id: str) -> str:
    for claim in bank.projects[project_id].claims:
        if claim.usable_on_resume:
            return claim.id
    raise AssertionError(f"no usable claim on {project_id}")


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.bank = load_bank()
        tex = (ROOT / "resumes" / "base" / "JZ_resume.tex").read_text()
        self.shell = tex.split("\\begin{document}")[0] + (
            "\\begin{document}\n"
            "Junyi (Conny) Zhou\n"
            "\\section{Projects}\n"
            "\\resumeItemListStart\n"
            "      \\item PLACEHOLDER\n"
            "\\resumeItemListEnd\n"
            "\\end{document}\n"
        )

    def test_planted_latency_metric_fails(self) -> None:
        tex = self.shell.replace("PLACEHOLDER", "Cut inference latency 40% on a made-up serving stack.")
        report = validate_tex(self.bank, tex, (_usable_claim(self.bank, "airway_chatbot"),))
        codes = [i.code for i in report.issues if i.severity == "fail"]
        self.assertIn("unsupported_metric", codes, report.issues)

    def test_forbidden_kubernetes_fails(self) -> None:
        tex = self.shell.replace("PLACEHOLDER", "Deployed the chatbot on Kubernetes.")
        report = validate_tex(self.bank, tex, (_usable_claim(self.bank, "airway_chatbot"),))
        codes = [i.code for i in report.issues if i.severity == "fail"]
        self.assertIn("forbidden_token", codes, report.issues)

    def test_planned_grpo_as_done_fails(self) -> None:
        tex = self.shell.replace("PLACEHOLDER", "Trained a GRPO policy on PanNuke slides.")
        report = validate_tex(self.bank, tex, ())
        codes = [i.code for i in report.issues if i.severity == "fail"]
        self.assertIn("planned_as_done", codes, report.issues)

    def test_bank_metric_passes(self) -> None:
        tex = self.shell.replace(
            "PLACEHOLDER",
            "Reached 9.38 BLEU on English-to-German translation.",
        )
        report = validate_tex(self.bank, tex, (_usable_claim(self.bank, "transformer_reimpl"),))
        metric_fails = [i for i in report.issues if i.code == "unsupported_metric"]
        self.assertEqual(metric_fails, [])


class TestMatcher(unittest.TestCase):
    def test_etl_requirement_matches_compleg(self) -> None:
        bank = load_bank()
        job = parse_jd(
            "---\ncompany: Acme\ntitle: Data Scientist Intern\n---\n"
            "## Job text\n"
            "- Required: build Python ETL pipelines over messy public data.\n"
            "- Required: SQL and relational schema design.\n"
        )
        matches = match_job(bank, job)
        compleg = [m for m in matches if m.project_id == "compleg_uk_nz" and m.strength == "strong_direct"]
        self.assertTrue(compleg, matches)

    def test_cuda_kernels_are_unsupported(self) -> None:
        bank = load_bank()
        job = parse_jd(
            "---\ncompany: GPUCo\ntitle: Software Engineer\n---\n"
            "## Job text\n"
            "- Required: author CUDA and Triton kernels for custom GPU ops.\n"
        )
        matches = match_job(bank, job)
        strong = [m for m in matches if m.strength == "strong_direct"]
        self.assertFalse(strong, strong)


class TestCatalog(unittest.TestCase):
    def test_invented_metric_is_rejected(self) -> None:
        body = load_yaml(BANK_PATH)["projects"]["compleg_uk_nz"]
        with self.assertRaises(ValueError):
            assert_catalog_grounded({"id": "x", "claim": "Cut latency 40% with a new warehouse"}, body)

    def test_bank_has_no_authored_claims_key(self) -> None:
        raw = load_yaml(BANK_PATH)
        authored = [pid for pid, body in raw["projects"].items() if body.get("claims")]
        self.assertEqual(authored, [])


class TestPipeline(unittest.TestCase):
    def test_run_is_idempotent_and_does_not_touch_versions(self) -> None:
        versions = ROOT / "data" / "resume_versions.csv"
        before_sha = hashlib.sha256(versions.read_bytes()).hexdigest()
        jd = ROOT / "tests" / "fixtures" / "resume_quality" / "jds" / "citadel-sds.md"
        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "a"
            out2 = Path(tmp) / "b"
            self.assertEqual(rqe_main(["run", "--jd", str(jd), "--out", str(out1)]), 0)
            self.assertEqual(rqe_main(["run", "--jd", str(jd), "--out", str(out2)]), 0)
            self.assertTrue((out1 / "resume.tex").is_file())
            for name in (
                "requirement_map.yaml",
                "claim_map.yaml",
                "strategy.md",
                "rejected_claims.md",
                "arena_report.md",
                "validation_report.md",
                "interview_defense.md",
            ):
                self.assertTrue((out1 / name).is_file(), name)
            self.assertEqual((out1 / "resume.tex").read_text(), (out2 / "resume.tex").read_text())
        self.assertEqual(hashlib.sha256(versions.read_bytes()).hexdigest(), before_sha)

    def test_engine_wording_differs_from_historical_baseline(self) -> None:
        jd = ROOT / "tests" / "fixtures" / "resume_quality" / "jds" / "citadel-sds.md"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "citadel"
            self.assertEqual(rqe_main(["run", "--jd", str(jd), "--out", str(out)]), 0)
            generated = (out / "resume.tex").read_text()
            baseline = (out / "baseline.tex").read_text()
            self.assertNotEqual(generated, baseline)
            self.assertIn("22,606", generated)

    def test_missing_master_entry_synthesizes_heading(self) -> None:
        bank = load_bank()
        job = parse_jd(
            "---\ncompany: TestCo\ntitle: Software Engineer\n---\n"
            "## Job text\n"
            "- Required: Python backend and REST APIs.\n"
        )
        matches = match_job(bank, job)
        strategy = build_strategy(bank, job, matches, "impact")
        tex = (ROOT / "resumes" / "base" / "JZ_resume.tex").read_text()
        stripped = tex
        for needle in ("Airway Management Simulation Chatbot",):
            start = stripped.find(needle)
            if start < 0:
                continue
            head = stripped.rfind("\\resumeSubheading", 0, start)
            end = stripped.find("\\resumeItemListEnd", start)
            stripped = stripped[:head] + stripped[end + len("\\resumeItemListEnd") :]
        doc = BaseDoc(stripped)
        cand = build_candidate(bank, strategy, doc)
        if "airway_chatbot" in strategy.include_projects:
            self.assertIn("Airway Management Simulation Chatbot", cand.tex)
        report = validate_tex(bank, cand.tex, cand.used_claim_ids)
        self.assertTrue(report.ok, report.issues)

    def test_build_candidate_uses_only_bank_wording(self) -> None:
        bank = load_bank()
        job = parse_jd(
            "---\ncompany: TestCo\ntitle: Machine Learning Engineer\n---\n"
            "## Job text\n"
            "- Required: PyTorch training and evaluation.\n"
            "- Required: LoRA or parameter-efficient fine-tuning.\n"
        )
        matches = match_job(bank, job)
        strategy = build_strategy(bank, job, matches, "impact")
        cand = build_candidate(bank, strategy)
        report = validate_tex(bank, cand.tex, cand.used_claim_ids)
        self.assertTrue(report.ok, report.issues)


class TestCliValidate(unittest.TestCase):
    def test_validate_historical_baseline_exit(self) -> None:
        tex = (
            ROOT
            / "tests"
            / "fixtures"
            / "resume_quality"
            / "baselines"
            / "2026-08-24_data-ml_v1.3.tex"
        )
        rc = rqe_main(["validate", str(tex)])
        self.assertIn(rc, (0, 1))


if __name__ == "__main__":
    unittest.main()
