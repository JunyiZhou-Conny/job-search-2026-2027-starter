#!/usr/bin/env python3
"""The attempt ledger must refuse a second apply to the same posting, must not
start without a passing preflight, must not call an attempt verified on a
banner plus a sentence, and must never rewrite a finished attempt."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from apply_ledger import Ledger, main  # noqa: E402

URL = "https://jobs.ashbyhq.com/acme/1111-2222?utm_source=jobright"
OPEN_GATES = {"gates": {"ashby": "G2", "greenhouse": "G1", "lever": "G0", "workday": "G0", "other": "G0"},
              "regular_submit_cap_per_run": 2}
MINIMAL_FORM = {"url": URL, "org": "acme", "open": True, "fields": [], "summary": {}, "g2_blockers": []}


def _rows(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


class TestApplyLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data"
        self.data.mkdir()
        self.ledger = Ledger(self.data, gates=OPEN_GATES)
        self.export = self.data / "imports" / "simplify" / "2026-09-03_simplify_download.csv"
        self.export.parent.mkdir(parents=True)
        self.export.write_text("Job Title,Company Name,Location,Job URL,Applied Date,Status\n")

    def tearDown(self):
        self.tmp.cleanup()

    def _pre(self, **kw):
        base = dict(url=URL, company="Acme", role="Software Engineer", ats="ashby", gate="G2", weight="regular",
                    run_id="run-1", harness_ready=True, identity_ok=True, form=MINIMAL_FORM)
        base.update(kw)
        return self.ledger.preflight(**base)

    def _start(self, pre=None, **kw):
        pre = pre or self._pre()
        base = dict(url=URL, company="Acme", role="Software Engineer", ats="ashby", gate="G2", weight="regular",
                    run_id="run-1", source="test", pursuit_lane="broad", role_cluster="cloud_swe", preflight=pre)
        base.update(kw)
        return self.ledger.start(**base)

    def _verified(self, attempt_id, **kw):
        base = dict(attempt_id=attempt_id, outcome="submitted_verified",
                    banner_text="Success. Your application was successfully submitted.",
                    tracker_status=f"Applied per {self.export.relative_to(self.data.parent)}")
        base.update(kw)
        return self.ledger.finish(**base)

    def test_happy_path_then_rerun_is_blocked(self):
        self.assertEqual(self._pre()["verdict"], "pass")
        res = self._start()
        self.assertEqual(self._pre()["reasons"], ["duplicate"], "an in-progress attempt blocks a rerun")
        self._verified(res["attempt_id"], resume_version="2026-08-24_cloud-swe_v1.3")
        again = self._pre(url="https://jobs.ashbyhq.com/acme/1111-2222/application?embed=true", company="acme",
                          role="software engineer", run_id="run-2")
        self.assertEqual(again["verdict"], "blocked")
        self.assertIn("duplicate", again["reasons"])
        with self.assertRaises(SystemExit):
            self._start(pre=again, run_id="run-2")
        app = _rows(self.data / "applications.csv")[0]
        self.assertEqual((app["status"], app["resume_version"]), ("applied", "2026-08-24_cloud-swe_v1.3"))
        events = [r["event_type"] for r in _rows(self.data / "activity_log.csv")]
        self.assertEqual(events, ["job_added", "submit_attempt_started", "status_changed"])

    def test_start_needs_a_matching_passing_preflight(self):
        with self.assertRaises(SystemExit):
            self.ledger.start(url=URL, company="Acme", role="SWE", ats="ashby", gate="G2", weight="regular",
                              run_id="run-1", source="t", pursuit_lane="broad", role_cluster="", preflight=None)
        pre = self._pre()
        with self.assertRaises(SystemExit):
            self._start(pre=pre, run_id="run-other")
        with self.assertRaises(SystemExit):
            self._start(pre=pre, url="https://jobs.ashbyhq.com/acme/9999")

    def test_gate_table_is_enforced(self):
        closed = Ledger(self.data, gates={"gates": {"ashby": "G1"}, "regular_submit_cap_per_run": 3})
        pre = closed.preflight(url=URL, company="Acme", role="SWE", ats="ashby", gate="G2", weight="regular",
                               run_id="r", harness_ready=True, identity_ok=True, form=MINIMAL_FORM)
        self.assertEqual(pre["reasons"], ["gate_closed:ashby=G1<G2"])
        fill_only = closed.preflight(url=URL, company="Acme", role="SWE", ats="ashby", gate="G1", weight="regular",
                                     run_id="r", harness_ready=False, identity_ok=False, form=MINIMAL_FORM)
        self.assertEqual(fill_only["verdict"], "pass", "G1 does not need harness or identity flags")

    def test_prioritized_harness_identity_and_form_blockers(self):
        self.assertIn("prioritized_needs_review_packet", self._pre(weight="prioritized")["reasons"])
        g3 = Ledger(self.data, gates={"gates": {"ashby": "G3"}, "regular_submit_cap_per_run": 3})
        self.assertIn("prioritized_needs_review_packet", g3.preflight(
            url=URL, company="Acme", role="SWE", ats="ashby", gate="G3", weight="prioritized", run_id="r",
            harness_ready=True, identity_ok=True, form=MINIMAL_FORM)["reasons"])
        self.assertIn("harness_not_ready", self._pre(harness_ready=False)["reasons"])
        self.assertIn("identity_unverified", self._pre(identity_ok=False)["reasons"])
        essay = dict(MINIMAL_FORM, g2_blockers=["required_essay", "broad_sponsorship_question"])
        self.assertEqual(self._pre(form=essay)["reasons"], ["form:required_essay", "form:broad_sponsorship_question"])
        self.assertEqual(self._pre(form={"url": URL, "org": "acme", "open": False})["reasons"], ["posting_closed"])
        review = self._pre(gate="G1", weight="prioritized", form=essay, harness_ready=False, identity_ok=False)
        self.assertEqual(review["verdict"], "pass", "a G1 fill-and-review may open a form with an essay")
        self.assertEqual(self._pre(gate="G1", form={"url": URL, "org": "acme", "open": False})["reasons"], ["posting_closed"])

    def test_run_cap(self):
        a = self._start()
        self._verified(a["attempt_id"])
        b_url = "https://jobs.ashbyhq.com/acme/2222"
        b = self._start(pre=self._pre(url=b_url, role="Backend Engineer"), url=b_url, role="Backend Engineer")
        self._verified(b["attempt_id"])
        third = self._pre(url="https://jobs.ashbyhq.com/acme/3333", role="Platform Engineer")
        self.assertIn("run_cap_reached:2", third["reasons"])

    def test_verified_needs_a_durable_second_signal(self):
        res = self._start()
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success")
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success",
                               tracker_status="Simplify overlay said Application Submitted")
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success",
                               tracker_status="data/imports/simplify/does_not_exist.csv")
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success",
                               tracker_status="see data/applications.csv")
        out = self._verified(res["attempt_id"])
        self.assertEqual(out["outcome"], "submitted_verified")

    def test_application_id_counts_as_second_signal(self):
        res = self._start()
        out = self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success",
                                 application_id="app_123")
        self.assertEqual(out["status"], "applied")

    def test_finished_attempts_are_immutable(self):
        res = self._start()
        self._verified(res["attempt_id"])
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="blocked", notes="rewrite")
        self.assertEqual(_rows(self.data / "apply_attempts.csv")[0]["outcome"], "submitted_verified")

    def test_unverified_blocked_and_closed_outcomes(self):
        res = self._start()
        out = self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_unverified", banner_text="Success")
        self.assertEqual(out["status"], "applied")
        url2 = "https://jobs.ashbyhq.com/acme/2222"
        res2 = self._start(pre=self._pre(url=url2, role="Backend Engineer"), url=url2, role="Backend Engineer")
        self.ledger.finish(attempt_id=res2["attempt_id"], outcome="blocked", notes="eeo_touched",
                           next_action="human review", next_action_date="2026-09-05")
        app2 = [r for r in _rows(self.data / "applications.csv") if r["role"] == "Backend Engineer"][0]
        self.assertEqual((app2["status"], app2["next_action"]), ("ready_to_apply", "human review"))
        self.assertFalse(self.ledger.precheck(url2, "Acme", "Backend Engineer")["duplicate"])
        url3 = "https://jobs.ashbyhq.com/acme/3333"
        closed_pre = self.ledger.preflight(url=url3, company="Acme", role="Data Engineer", ats="ashby", gate="G1",
                                           weight="regular", run_id="run-9", harness_ready=False, identity_ok=False,
                                           form=MINIMAL_FORM)
        res3 = self._start(pre=closed_pre, url=url3, role="Data Engineer", gate="G1", run_id="run-9")
        self.ledger.finish(attempt_id=res3["attempt_id"], outcome="posting_closed", notes="404")
        self.assertEqual(_rows(self.data / "job_decisions.csv")[0]["decision"], "closed")
        self.assertTrue(self.ledger.precheck(url3, "Acme", "Data Engineer")["duplicate"])

    def test_simplify_tracker_is_a_second_memory(self):
        with self.export.open("a", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Founding AI Engineer", "Clera", "SF", "https://jobs.ashbyhq.com/clera/abc/application?embed=true", "2026-08-25", "APPLIED"])
            w.writerow(["ML Engineer", "Hive", "Seattle", "https://jobs.ashbyhq.com/hive/def", "", "SAVED"])
        applied = self.ledger.precheck("https://jobs.ashbyhq.com/clera/abc", "Clera", "Founding AI Engineer")
        self.assertTrue(applied["duplicate"])
        self.assertEqual(applied["matches"][0]["table"], "simplify_tracker")
        self.assertTrue(self.ledger.precheck("https://other.example/x", "clera", "founding ai engineer")["duplicate"])
        self.assertFalse(self.ledger.precheck("https://jobs.ashbyhq.com/hive/def", "Hive", "ML Engineer")["duplicate"])

    def test_close_posting_is_idempotent_and_blocks(self):
        url = "https://jobs.ashbyhq.com/datologyai/gone"
        first = self.ledger.close_posting(url=url, company="DatologyAI", role="SWE Intern", reason="gone", source="test")
        second = self.ledger.close_posting(url=url, company="DatologyAI", role="SWE Intern", reason="again", source="test")
        self.assertEqual((first["already_recorded"], second["already_recorded"]), (False, True))
        self.assertEqual(len(_rows(self.data / "job_decisions.csv")), 1)
        self.assertTrue(self.ledger.precheck(url, "DatologyAI", "SWE Intern")["duplicate"])

    def test_cli_precheck_exit_codes(self):
        argv = ["--data-dir", str(self.data), "precheck", "--url", URL, "--company", "Acme", "--role", "SWE"]
        self.assertEqual(main(argv), 0)
        res = self._start(pre=self._pre(role="SWE"), role="SWE")
        self._verified(res["attempt_id"])
        self.assertEqual(main(argv), 3)


if __name__ == "__main__":
    unittest.main()
