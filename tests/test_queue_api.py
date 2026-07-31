#!/usr/bin/env python3
"""Tests for apply-queue identity, write-back and undo.

These exercise the paths a click takes through the repo, because the failure
mode that matters is silent: a role written to the ledger that still looks
untouched in the queue, or an undo that quietly loses a field.

The write-back module resolves paths at import time, so each test points it at
a throwaway copy of the data directory rather than the real ledger.
"""

from __future__ import annotations

import csv
import importlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import APP_FIELDS, canonical_url  # noqa: E402


class TestCanonicalUrl(unittest.TestCase):
    def test_drops_tracking_but_keeps_identity(self):
        self.assertEqual(
            canonical_url("https://boards.greenhouse.io/embed/job_app?token=4034001009&utm_source=jobright"),
            "https://boards.greenhouse.io/embed/job_app?token=4034001009",
        )

    def test_distinct_jobs_stay_distinct(self):
        a = canonical_url("https://boards.greenhouse.io/embed/job_app?token=111")
        b = canonical_url("https://boards.greenhouse.io/embed/job_app?token=222")
        self.assertNotEqual(a, b)

    def test_case_slash_and_fragment(self):
        self.assertEqual(
            canonical_url("https://JobRight.ai/jobs/info/ABC/#apply"),
            "https://jobright.ai/jobs/info/abc",
        )

    def test_param_order_is_irrelevant(self):
        self.assertEqual(
            canonical_url("https://x.com/j?b=2&a=1"),
            canonical_url("https://x.com/j?a=1&b=2"),
        )

    def test_empty(self):
        self.assertEqual(canonical_url(""), "")
        self.assertEqual(canonical_url(None), "")

    def test_queue_and_ledger_agree(self):
        import generate_apply_queue as gaq
        import queue_writeback as qw

        url = "https://job-boards.greenhouse.io/acme/jobs/123?utm_campaign=x&gh_jid=9"
        self.assertEqual(gaq.norm_url(url), qw.canon(url))


class WriteBackCase(unittest.TestCase):
    """Runs queue_writeback against an isolated data directory."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        (base / "data").mkdir()

        self.apps_path = base / "data" / "applications.csv"
        with self.apps_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=APP_FIELDS)
            writer.writeheader()
            writer.writerow(self._row())

        import js_lib
        import queue_writeback as qw

        self.js_lib = js_lib
        self.qw = qw
        self._saved = {
            "DATA": js_lib.DATA,
            "APPLICATIONS": js_lib.APPLICATIONS,
            "ACTIVITY": js_lib.ACTIVITY,
            "BACKUPS": js_lib.BACKUPS,
            "RESUME_VERSIONS": js_lib.RESUME_VERSIONS,
            "qw_APPLICATIONS": qw.APPLICATIONS,
            "qw_ACTIVITY": qw.ACTIVITY,
            "qw_BACKUPS": qw.BACKUPS,
            "qw_DECISIONS": qw.DECISIONS,
            "qw_JOURNAL": qw.JOURNAL,
            "qw_RESUME": qw.RESUME_VERSIONS,
        }
        js_lib.DATA = base / "data"
        js_lib.APPLICATIONS = self.apps_path
        js_lib.ACTIVITY = base / "data" / "activity_log.csv"
        js_lib.BACKUPS = base / "data" / "backups"
        js_lib.RESUME_VERSIONS = base / "data" / "resume_versions.csv"
        qw.APPLICATIONS = self.apps_path
        qw.ACTIVITY = js_lib.ACTIVITY
        qw.BACKUPS = js_lib.BACKUPS
        qw.DECISIONS = base / "data" / "job_decisions.csv"
        qw.JOURNAL = base / "data" / "queue_undo_journal.json"
        qw.RESUME_VERSIONS = js_lib.RESUME_VERSIONS

    def tearDown(self):
        for key, value in self._saved.items():
            if key.startswith("qw_"):
                setattr(self.qw, key[3:], value)
            else:
                setattr(self.js_lib, key, value)
        self.tmp.cleanup()

    def _row(self, **overrides):
        row = {field: "" for field in APP_FIELDS}
        row.update(
            {
                "id": "J20260720-013",
                "job_id": "J20260720-013",
                "company": "Lila Sciences",
                "role": "Intern, Security & Cloud Engineering",
                "job_url": "https://boards.greenhouse.io/embed/job_app?token=4034001009",
                "posting_url": "https://boards.greenhouse.io/embed/job_app?token=4034001009",
                "status": "saved",
                "application_status": "saved",
                "stage_current": "saved",
                "next_action": "Assign pursuit lane and record resume version",
                "next_action_date": "2026-07-20",
                "date_applied": "N/A",
                "notes": "[simplify:2026-07-20.csv]",
            }
        )
        row.update(overrides)
        return row

    def _read(self):
        with self.apps_path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    URL = "https://boards.greenhouse.io/embed/job_app?token=4034001009&utm_source=jobright"

    def _restore_diffs(self, before: dict, after: dict) -> dict:
        """Fields undo is responsible for. Timestamps move by design, and saving
        backfills schema defaults (eligibility, created_at, ...) — that is
        normalisation by sync_app_aliases, not a failed undo."""
        ignored = {"updated_at", "last_update", "created_at", "eligibility", "hard_eligibility"}
        return {
            k: (before[k], after[k])
            for k in before
            if before[k] != after[k] and k not in ignored
        }


class TestApplied(WriteBackCase):
    def test_applied_then_undo_restores_every_field(self):
        before = self._read()[0]

        self.qw.record_applied([{"url": self.URL, "company": "Lila Sciences", "role": "x", "cluster": "data_ml"}])
        mid = self._read()[0]
        self.assertEqual(mid["status"], "applied")
        self.assertTrue(mid["date_applied"])

        result = self.qw.undo_applied(self.URL)
        self.assertTrue(result["ok"])
        after = self._read()[0]

        diffs = self._restore_diffs(before, after)
        self.assertEqual(diffs, {}, f"undo did not restore cleanly: {diffs}")

    def test_undo_removes_a_row_the_queue_created(self):
        url = "https://example.com/brand-new-role"
        self.qw.record_applied([{"url": url, "company": "NewCo", "role": "Engineer", "cluster": "data_ml"}])
        self.assertEqual(len(self._read()), 2)

        result = self.qw.undo_applied(url)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "removed")
        self.assertEqual(len(self._read()), 1)

    def test_does_not_downgrade_a_live_pipeline(self):
        rows = self._read()
        rows[0]["status"] = "onsite"
        with self.apps_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=APP_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        self.qw.record_applied([{"url": self.URL, "company": "Lila", "role": "x"}])
        self.assertEqual(self._read()[0]["status"], "onsite")

        result = self.qw.undo_applied(self.URL)
        self.assertFalse(result["ok"])

    def test_tracking_params_do_not_create_a_second_row(self):
        self.qw.record_applied([{"url": self.URL, "company": "Lila", "role": "x"}])
        self.qw.undo_applied(self.URL)
        # Same posting, different tracking noise — must still be one row.
        self.qw.record_applied(
            [{"url": "https://boards.greenhouse.io/embed/job_app?token=4034001009&ref=slack", "company": "Lila", "role": "x"}]
        )
        self.assertEqual(len(self._read()), 1)


class TestPass(WriteBackCase):
    def test_pass_then_undo_restores_status_and_clears_decision(self):
        before = self._read()[0]

        self.qw.record_pass([{"url": self.URL, "company": "Lila", "role": "x", "reason": "needs clearance"}])
        self.assertEqual(self._read()[0]["status"], "passed")
        self.assertEqual(len(self.qw.passed_records()), 1)

        result = self.qw.undo_pass(self.URL)
        self.assertTrue(result["ok"])
        self.assertEqual(len(self.qw.passed_records()), 0)

        after = self._read()[0]
        diffs = self._restore_diffs(before, after)
        self.assertEqual(diffs, {}, f"undo did not restore cleanly: {diffs}")

    def test_undo_without_a_record_is_reported_not_guessed(self):
        result = self.qw.undo_pass("https://example.com/never-seen")
        self.assertFalse(result["ok"])


class TestBootstrapPayload(unittest.TestCase):
    def test_payload_shape(self):
        import generate_apply_queue as gaq

        items = [
            {
                "tier": "A", "note": "", "company": "Acme", "role": "Engineer",
                "url": "https://acme.com/jobs/1?utm_source=x", "lane": "core",
                "cluster": "data_ml", "grad": "program_end", "job_id": "", "source": "triage_keep",
                "location": "Boston, MA", "reason": "fit", "confidence": "high",
                "track": "", "posted_relative": "2 hours ago",
                "company_class": "startup", "geo": "boston_ma", "gtc_sponsor": "no",
                "gtc_match": "", "tier_label": "Today", "class_label": "Startup / scaleup",
                "geo_label": "Boston / MA",
            }
        ]
        payload = gaq.bootstrap_payload("2026-07-28", items, live=True)
        self.assertEqual(payload["day"], "2026-07-28")
        self.assertTrue(payload["live"])
        self.assertEqual(payload["counts"]["total"], 1)
        self.assertEqual(payload["counts"]["boston_ma"], 1)
        self.assertEqual(payload["items"][0]["key"], "https://acme.com/jobs/1")

    def test_render_html_has_no_placeholders(self):
        import generate_apply_queue as gaq

        html = gaq.render_html("2026-07-28", [], live=False, inline=True)
        for placeholder in ("__DAY__", "__BOOTSTRAP__", "__HEAD_ASSETS__", "__BODY_ASSETS__"):
            self.assertNotIn(placeholder, html)
        self.assertIn("queue-bootstrap", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
