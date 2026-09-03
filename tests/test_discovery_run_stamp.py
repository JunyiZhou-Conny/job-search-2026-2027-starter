#!/usr/bin/env python3
"""Run-stamped discovery artifacts: one file set per run, not per day."""

from __future__ import annotations

import csv
import os
import sys
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

import merge_discovery  # noqa: E402
import triage_discovery  # noqa: E402

ROW = {
    "company": "Acme",
    "role": "Software Engineer Intern",
    "url": "https://jobright.ai/jobs/info/abc?utm=x",
    "source": "intern_list",
    "track": "internship_if_eligible",
    "category": "swe",
    "date_discovered": "2026-09-03",
    "fetched_at": "2026-09-03T13:02:00+00:00",
}


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=merge_discovery.FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in merge_discovery.FIELDS})


class TestRunStamp(unittest.TestCase):
    def test_stamp_is_utc_day_and_hour(self):
        self.assertEqual(
            merge_discovery.run_stamp(datetime(2026, 9, 3, 13, 7, tzinfo=timezone.utc)),
            "2026-09-03T13",
        )

    def test_stamp_converts_local_time_to_utc(self):
        new_york = timezone(timedelta(hours=-4))
        self.assertEqual(
            merge_discovery.run_stamp(datetime(2026, 9, 3, 18, 11, tzinfo=new_york)),
            "2026-09-03T22",
        )

    def test_plain_day_passes_through(self):
        self.assertEqual(merge_discovery.source_day("2026-09-03"), "2026-09-03")

    def test_source_day_follows_local_date_of_the_stamp(self):
        old = os.environ.get("TZ")
        os.environ["TZ"] = "America/New_York"
        time.tzset()
        try:
            self.assertEqual(merge_discovery.source_day("2026-09-04T00"), "2026-09-03")
            self.assertEqual(merge_discovery.source_day("2026-09-03T13"), "2026-09-03")
        finally:
            if old is None:
                del os.environ["TZ"]
            else:
                os.environ["TZ"] = old
            time.tzset()

    def test_source_day_rejects_other_shapes(self):
        for bad in ("20260903", "2026-09-03T1", "2026-09-03T13:05", "today"):
            with self.assertRaises(ValueError):
                merge_discovery.source_day(bad)


class TestMergeNaming(unittest.TestCase):
    def run_merge(self, argv: list[str], exporter_day: str = "2026-09-03") -> tuple[Path, Path]:
        disc = Path(self.tmp.name) / "discovery"
        inbox = Path(self.tmp.name) / "inbox"
        write_csv(disc / f"{exporter_day}_intern_swe.csv", [ROW])
        old = merge_discovery.DISC, merge_discovery.INBOX
        merge_discovery.DISC, merge_discovery.INBOX = disc, inbox
        try:
            self.assertEqual(merge_discovery.main(argv), 0)
        finally:
            merge_discovery.DISC, merge_discovery.INBOX = old
        return disc, inbox

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_run_stamp_names_merged_csv_and_inbox(self):
        disc, inbox = self.run_merge(["--date", "2026-09-03T13"])
        self.assertTrue((disc / "2026-09-03T13_all.csv").exists())
        self.assertTrue((inbox / "daily-2026-09-03T13.md").exists())
        self.assertFalse((disc / "2026-09-03_all.csv").exists())

    def test_two_runs_on_one_day_do_not_collide(self):
        disc, inbox = self.run_merge(["--date", "2026-09-03T13"])
        write_csv(disc / "2026-09-03_intern_swe.csv", [ROW])
        old = merge_discovery.DISC, merge_discovery.INBOX
        merge_discovery.DISC, merge_discovery.INBOX = disc, inbox
        try:
            self.assertEqual(merge_discovery.main(["--date", "2026-09-03T22"]), 0)
        finally:
            merge_discovery.DISC, merge_discovery.INBOX = old
        self.assertEqual(
            sorted(p.name for p in disc.glob("*_all.csv")),
            ["2026-09-03T13_all.csv", "2026-09-03T22_all.csv"],
        )

    def test_plain_day_still_works(self):
        disc, inbox = self.run_merge(["--date", "2026-09-03"])
        self.assertTrue((disc / "2026-09-03_all.csv").exists())
        self.assertTrue((inbox / "daily-2026-09-03.md").exists())

    def test_default_stamp_is_current_utc_hour(self):
        now = datetime.now(timezone.utc)
        disc, _ = self.run_merge([], exporter_day=now.astimezone().date().isoformat())
        self.assertTrue((disc / f"{merge_discovery.run_stamp(now)}_all.csv").exists())


class TestTriagePackNaming(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.disc = base / "discovery"
        self.gen = base / "generated"
        rules = base / "rules.yaml"
        rules.write_text("guide_rules: []\n", encoding="utf-8")
        self.old = triage_discovery.DISC, triage_discovery.GEN, triage_discovery.RULES, triage_discovery.ROOT
        triage_discovery.DISC, triage_discovery.GEN, triage_discovery.RULES, triage_discovery.ROOT = (
            self.disc,
            self.gen,
            rules,
            base,
        )
        self.addCleanup(self.restore)

    def restore(self):
        triage_discovery.DISC, triage_discovery.GEN, triage_discovery.RULES, triage_discovery.ROOT = self.old

    def test_pack_and_prompt_carry_the_run_stamp(self):
        write_csv(self.disc / "2026-09-03T13_all.csv", [ROW])
        self.assertEqual(triage_discovery.main(["--date", "2026-09-03T13"]), 0)
        self.assertTrue((self.gen / "discovery_for_triage_2026-09-03T13.csv").exists())
        prompt = (self.gen / "discovery_triage_prompt_2026-09-03T13.md").read_text(encoding="utf-8")
        self.assertIn("generated/discovery_triage_2026-09-03T13.csv", prompt)
        self.assertIn("generated/discovery_triage_2026-09-03T13.md", prompt)

    def test_plain_day_pack_still_builds(self):
        write_csv(self.disc / "2026-09-03_all.csv", [ROW])
        self.assertEqual(triage_discovery.main(["--date", "2026-09-03"]), 0)
        self.assertTrue((self.gen / "discovery_for_triage_2026-09-03.csv").exists())

    def test_default_is_the_newest_merged_file(self):
        older = self.disc / "2026-09-03_all.csv"
        newer = self.disc / "2026-09-03T13_all.csv"
        write_csv(older, [ROW])
        write_csv(newer, [ROW])
        past = time.time() - 3600
        os.utime(older, (past, past))
        self.assertEqual(triage_discovery.main([]), 0)
        self.assertTrue((self.gen / "discovery_for_triage_2026-09-03T13.csv").exists())
        self.assertFalse((self.gen / "discovery_for_triage_2026-09-03.csv").exists())

    def test_missing_merge_is_a_clear_error(self):
        with self.assertRaises(SystemExit):
            triage_discovery.main([])


if __name__ == "__main__":
    unittest.main()
