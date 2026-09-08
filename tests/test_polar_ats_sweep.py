#!/usr/bin/env python3
"""ATS sweep packets stay bounded and Polar-facing."""

from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "generated" / "polar" / "ats_sweep"
SOLIDIGM = SWEEP / "solidigm.md"
CITADEL = SWEEP / "citadel.md"
MANIFEST = SWEEP / "manifest.md"

SOLIDIGM_APPLY = "https://jobs.smartrecruiters.com/solidigm/744000147613769"
SOLIDIGM_JR = "https://jobright.ai/jobs/info/6a9b756513883870605981ea"
CITADEL_JR = "https://jobright.ai/jobs/info/6a7a308fbb6ca93ae561a556"
PROFILE_URLS = {
    "https://www.linkedin.com/in/junyi-zhou-270208247",
    "https://github.com/JunyiZhou-Conny",
    "https://connyzhou.com",
}
CITADEL_PROJECT = "https://github.com/JunyiZhou-Conny/Comput-Leg-UK-NZ"

REPORT_KEYS = (
    "packet_id",
    "company",
    "role",
    "starting URL",
    "final URL / host",
    "ATS family actually observed",
    "Original Job Post used: yes/no",
    "posting matched: yes/no",
    "auth wall: yes/no + exact type",
    "Simplify used: yes/no",
    "fill status: full / partial / none",
    "corrections made",
    "written responses used",
    "unresolved required fields",
    "ready to submit: yes/no",
    "submitted: no",
    "CAPTCHA / anti-abuse issue",
    "approximate elapsed time",
    "approximate retries / repeated navigation",
    "stop reason",
)

NANP_LEAK = re.compile(
    r"(?:\+1[\s.-]+)?(?:\(\d{3}\)[\s.-]*|\d{3}[\s.-]+)\d{3}[\s.-]+\d{4}"
)
def urls_in(text: str) -> set[str]:
    return set(re.findall(r"https?://[^\s]+", text))


class TestPolarAtsSweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solidigm = SOLIDIGM.read_text(encoding="utf-8")
        cls.citadel = CITADEL.read_text(encoding="utf-8")
        cls.manifest = MANIFEST.read_text(encoding="utf-8")

    def test_manifest_names_only_cursor_selected_jobs(self):
        self.assertIn("P-20260906-001", self.manifest)
        self.assertIn("P-20260906-002", self.manifest)
        self.assertIn("Solidigm", self.manifest)
        self.assertIn("Citadel", self.manifest)
        self.assertIn("no_current_candidate", self.manifest)
        self.assertIn("Ashby", self.manifest)
        self.assertIn("Lever", self.manifest)
        self.assertIn("iCIMS", self.manifest)
        self.assertNotIn("KEEP list", self.manifest)

    def test_solidigm_uses_trusted_apply_url(self):
        self.assertIn("packet_id: P-20260906-001", self.solidigm)
        self.assertIn("Company: Solidigm", self.solidigm)
        self.assertIn(SOLIDIGM_APPLY, self.solidigm)
        self.assertIn(SOLIDIGM_JR, self.solidigm)
        self.assertIn("apply_url confidence: exact", self.solidigm)
        self.assertIn("Open the starting URL directly", self.solidigm)
        found = urls_in(self.solidigm)
        allowed = PROFILE_URLS | {SOLIDIGM_APPLY, SOLIDIGM_JR}
        self.assertTrue(found <= allowed, found - allowed)

    def test_citadel_does_not_invent_an_apply_url(self):
        self.assertIn("packet_id: P-20260906-002", self.citadel)
        self.assertIn("Company: Citadel", self.citadel)
        self.assertIn(CITADEL_JR, self.citadel)
        self.assertIn("apply_url: none", self.citadel)
        self.assertIn("Click Original Job Post only.", self.citadel)
        self.assertNotIn("https://www.citadel.com", self.citadel)
        self.assertNotIn("jobs.lever.co", self.citadel)
        self.assertNotIn("smartrecruiters.com", self.citadel)
        found = urls_in(self.citadel)
        allowed = PROFILE_URLS | {CITADEL_JR, CITADEL_PROJECT}
        self.assertTrue(found <= allowed, found - allowed)

    def test_packets_stop_before_submit_and_omit_secrets(self):
        for text in (self.solidigm, self.citadel):
            self.assertIn("Stop immediately before Submit.", text)
            self.assertIn("submitted: no", text)
            self.assertRegex(text, r"click Apply(?: or I'm interested)? once")
            self.assertIn("final Apply button", text)
            self.assertNotIn("form_strategy.yaml", text)
            self.assertNotIn("work_authorization.yaml", text)
            self.assertNotIn("SUBMIT_ROLLOUT.md", text)
            self.assertNotIn("@", text)
            self.assertIsNone(NANP_LEAK.search(text))
            for key in REPORT_KEYS:
                self.assertIn(key, text)
            self.assertIn("DO NOT AUTO-MAP", text)
            self.assertIn("Never click Generate with AI.", text)
            self.assertIn("Do not create an employer ATS account.", text)

    def test_written_answers_are_inlined(self):
        self.assertIn("I want to spend a summer on software that sits next to real storage hardware.", self.solidigm)
        self.assertIn("I am not claiming SSD or firmware experience.", self.solidigm)
        self.assertIn("I am not claiming finance-domain work.", self.citadel)
        self.assertIn("22,606 member-level division vote records", self.citadel)
        self.assertIn("statement of interest in investing or trading", self.citadel)

    def test_quantbot_ids_stay_unique(self):
        apps_path = ROOT / "data" / "applications.csv"
        attempts_path = ROOT / "data" / "apply_attempts.csv"
        with apps_path.open(encoding="utf-8", newline="") as fh:
            job_ids = [row.get("job_id") or row.get("id") for row in csv.DictReader(fh)]
        with attempts_path.open(encoding="utf-8", newline="") as fh:
            attempt_ids = [row.get("attempt_id") or row.get("id") for row in csv.DictReader(fh)]
        self.assertEqual(job_ids.count("J20260904-001"), 1)
        self.assertEqual(attempt_ids.count("A20260904-001"), 1)
        self.assertIn("Quantbot Technologies LP", apps_path.read_text(encoding="utf-8"))
        self.assertNotIn("J20260906-001", job_ids)

    def test_activity_log_keeps_both_pilot_rows(self):
        log = (ROOT / "data" / "activity_log.csv").read_text(encoding="utf-8")
        self.assertIn("J20260904-001", log)
        self.assertIn("P-20260904-002", log)
        self.assertIn("Quantbot", log)
        self.assertIn("Rakuten", log)

    def test_precheck_selected_urls_are_clean(self):
        import subprocess
        import sys

        cases = [
            (SOLIDIGM_APPLY, "Solidigm", "2027 Graduate Software, Firmware & AI Engineering Internships - US"),
            (CITADEL_JR, "Citadel", "Sector Data Scientist – 2027 Intern (US)"),
        ]
        script = ROOT / "scripts" / "apply_ledger.py"
        for url, company, role in cases:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "precheck",
                    "--url",
                    url,
                    "--company",
                    company,
                    "--role",
                    role,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn('"duplicate": false', proc.stdout)


class TestPolarLineageDecisions(unittest.TestCase):
    def test_decisions_keep_both_siblings(self):
        path = ROOT / "docs" / "state" / "decisions.tsv"
        with path.open(encoding="utf-8") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        blob = "\n".join("\t".join(row) for row in rows)
        self.assertIn("Quantbot Polar fill recorded as ready_to_apply", blob)
        self.assertIn("Rakuten OJP reached Workday", blob)
        self.assertIn("selected Solidigm SmartRecruiters and Citadel custom", blob)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
