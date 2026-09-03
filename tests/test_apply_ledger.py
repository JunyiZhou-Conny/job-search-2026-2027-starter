#!/usr/bin/env python3
"""The attempt ledger must refuse a second apply to the same posting and must
not call an attempt verified on a banner alone."""

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


def _rows(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


class TestApplyLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.ledger = Ledger(self.data)

    def tearDown(self):
        self.tmp.cleanup()

    def _start(self, **kw):
        base = dict(url=URL, company="Acme", role="Software Engineer", ats="ashby", gate="G2",
                    weight="regular", run_id="run-1", source="test", pursuit_lane="broad", role_cluster="cloud_swe")
        base.update(kw)
        return self.ledger.start(**base)

    def test_precheck_clean_then_blocked_after_verified_submit(self):
        self.assertFalse(self.ledger.precheck(URL, "Acme", "Software Engineer")["duplicate"])
        res = self._start()
        self.assertTrue(self.ledger.precheck(URL, "Acme", "Software Engineer")["duplicate"], "in-progress attempt blocks")
        self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified",
                           banner_text="Success. Your application was successfully submitted.",
                           tracker_status="Applied 9/3/26", resume_version="2026-08-24_cloud-swe_v1.3")
        check = self.ledger.precheck("https://jobs.ashbyhq.com/acme/1111-2222", "acme", "software engineer")
        self.assertTrue(check["duplicate"])
        tables = {m["table"] for m in check["matches"]}
        self.assertIn("applications", tables)
        self.assertIn("apply_attempts", tables)
        app = _rows(self.data / "applications.csv")[0]
        self.assertEqual(app["status"], "applied")
        self.assertEqual(app["resume_version"], "2026-08-24_cloud-swe_v1.3")
        self.assertTrue(app["date_applied"])
        events = [r["event_type"] for r in _rows(self.data / "activity_log.csv")]
        self.assertEqual(events, ["job_added", "submit_attempt_started", "status_changed"])

    def test_start_refuses_duplicate(self):
        res = self._start()
        self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified",
                           banner_text="Success", tracker_status="Applied")
        with self.assertRaises(SystemExit):
            self._start(run_id="run-2")

    def test_verified_needs_second_signal(self):
        res = self._start()
        with self.assertRaises(SystemExit):
            self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified", banner_text="Success")
        out = self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_unverified", banner_text="Success")
        self.assertEqual(out["status"], "applied")
        self.assertEqual(_rows(self.data / "apply_attempts.csv")[0]["outcome"], "submitted_unverified")

    def test_blocked_leaves_status_and_is_not_a_duplicate(self):
        res = self._start()
        self.ledger.finish(attempt_id=res["attempt_id"], outcome="blocked", notes="eeo_touched",
                           next_action="human review", next_action_date="2026-09-05")
        app = _rows(self.data / "applications.csv")[0]
        self.assertEqual(app["status"], "ready_to_apply")
        self.assertEqual(app["next_action"], "human review")
        self.assertFalse(self.ledger.precheck(URL, "Acme", "Software Engineer")["duplicate"])

    def test_posting_closed_writes_decision(self):
        res = self._start()
        self.ledger.finish(attempt_id=res["attempt_id"], outcome="posting_closed", notes="404")
        self.assertEqual(_rows(self.data / "applications.csv")[0]["status"], "closed")
        dec = _rows(self.data / "job_decisions.csv")
        self.assertEqual(dec[0]["decision"], "closed")
        self.assertTrue(self.ledger.precheck(URL, "Acme", "Software Engineer")["duplicate"])

    def test_cli_precheck_exit_codes(self):
        argv = ["--data-dir", str(self.data), "precheck", "--url", URL, "--company", "Acme", "--role", "SWE"]
        self.assertEqual(main(argv), 0)
        res = self._start(role="SWE")
        self.ledger.finish(attempt_id=res["attempt_id"], outcome="submitted_verified",
                           banner_text="Success", email_evidence="Ashby confirmation 2026-09-03")
        self.assertEqual(main(argv), 3)


if __name__ == "__main__":
    unittest.main()
