#!/usr/bin/env python3
"""The Ashby sweep keeps fresh early-career engineering postings and resolves their form facts.

Fixtures under tests/fixtures/ashby/ are recorded from the public API on
2026-09-03: the KAYAK board with description and compensation fields removed,
and the GraphQL form of its Associate Software Engineer posting with the
country list trimmed to five options.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

import export_ashby_boards as sweep_mod  # noqa: E402
from export_ashby_boards import (  # noqa: E402
    COLUMNS, compile_domain, digest, g2_candidate, load_orgs, published_within, remote_only, row_for,
    select_jobs, sweep, title_ok, write_csv,
)
import ashby_form  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "ashby"
BOARD = json.loads((FIXTURES / "board_kayak.json").read_text())["jobs"]
FORM_RESPONSE = (FIXTURES / "form_kayak_associate_swe.json").read_bytes()
DOMAIN = compile_domain(["Software Engineer", "Machine Learning Engineer", "Data Scientist", "ML Intern/New Grad", "Health Informatics"])
NOW = datetime(2026, 8, 26, 12, tzinfo=timezone.utc)
ORG = {"slug": "kayak", "company": "KAYAK"}
ASSOCIATE_SWE = next(j for j in BOARD if j["title"] == "Associate Software Engineer" and j["location"] == "Cambridge Office")


EMPLOYER = {"slug": "acme", "company": "Acme", "kind": "employer"}

def job(**over):
    base = {"title": "Software Engineer", "location": "San Francisco", "employmentType": "FullTime",
            "publishedAt": "2026-08-25T10:00:00.000+00:00", "isRemote": False, "workplaceType": "OnSite",
            "jobUrl": "https://jobs.ashbyhq.com/acme/3dc0a0f6-6a53-4a8c-bc70-b007113c348a",
            "applyUrl": "https://jobs.ashbyhq.com/acme/3dc0a0f6-6a53-4a8c-bc70-b007113c348a/application"}
    base.update(over)
    return base


def clean_form(**over):
    fields = [{"title": t, "type": ty, "required": True, "options": []}
              for t, ty in (("Name", "String"), ("Email", "Email"), ("Resume", "File"))]
    form = ashby_form.summarize({"url": "u", "org": "acme", "open": True, "title": "t", "location": None,
                                 "workplace": None, "employment": None, "published": None, "fields": fields})
    form.update(over)
    return form


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fetch_recorded_form(url):
    original = ashby_form.urllib.request.urlopen
    ashby_form.urllib.request.urlopen = lambda *a, **k: _Response(FORM_RESPONSE)
    try:
        return ashby_form.fetch(url)
    finally:
        ashby_form.urllib.request.urlopen = original


class TestTitleFilter(unittest.TestCase):
    def test_includes_early_career_engineering_titles(self):
        for title in ["New Grad Software Engineer", "Software Engineering Intern (2027 Summer Internship)",
                      "Associate Software Engineer", "Machine Learning Intern", "Junior Platform Engineer",
                      "Engineer I, Backend", "Data Scientist", "Member of Technical Staff (Software Engineer, Multimodal)",
                      "Early Career AI Engineer", "Health Informatics Analyst"]:
            self.assertTrue(title_ok(title, DOMAIN), title)

    def test_excludes_seniority_off_target_and_2026_cycles(self):
        for title in ["Senior Software Engineer", "Staff JAVA Software Engineer", "Engineering Manager, Platform Team",
                      "Director of Cyber Security", "Principal ML Engineer", "Lead Software Engineer", "Head of Software",
                      "Software Engineering Intern (Summer 2026)", "Marketing Intern", "Generalist Intern",
                      "Hardware Engineer, Test", "PhD Research Scientist", "Office Manager (Part-Time)",
                      "Sr. Director, Media Planning and Buying"]:
            self.assertFalse(title_ok(title, DOMAIN), title)

    def test_domain_grows_from_role_titles(self):
        self.assertTrue(title_ok("Clinical Data Intern", compile_domain(["Clinical Data"])))
        self.assertFalse(title_ok("Clinical Research Coordinator", compile_domain(["Clinical Data"])))


class TestSelection(unittest.TestCase):
    def test_published_window_uses_ashby_published_at(self):
        kept = sorted(j["title"] for j in select_jobs(BOARD, DOMAIN, NOW, 7))
        self.assertEqual(kept, ["Associate JAVA Software Engineer", "Java Software Engineer, Search team"])
        self.assertFalse(published_within(ASSOCIATE_SWE, NOW, 7))
        self.assertTrue(published_within(ASSOCIATE_SWE, NOW, 60))
        self.assertFalse(published_within(job(publishedAt=None), NOW, 7))
        self.assertFalse(published_within(job(publishedAt="yesterday"), NOW, 7))

    def test_hybrid_is_not_remote_even_when_ashby_flags_is_remote(self):
        self.assertTrue(ASSOCIATE_SWE["isRemote"])
        self.assertFalse(remote_only(ASSOCIATE_SWE))

    def test_remote_only_detection(self):
        self.assertTrue(remote_only(job(workplaceType="Remote", isRemote=True, location="New York")))
        self.assertTrue(remote_only(job(workplaceType=None, isRemote=True)))
        self.assertTrue(remote_only(job(workplaceType=None, isRemote=None, location="remote")))
        self.assertTrue(remote_only(job(workplaceType=None, isRemote=None, location="Australia - Remote")))
        self.assertFalse(remote_only(job(workplaceType=None, isRemote=None, location="San Francisco or Remote")))
        self.assertFalse(remote_only(job(workplaceType=None, isRemote=None, location="Torrance, CA")))
        self.assertEqual(select_jobs([job(workplaceType="Remote")], DOMAIN, NOW, 7), [])


class TestG2Candidate(unittest.TestCase):
    def test_recorded_kayak_form_is_blocked_by_broad_sponsorship(self):
        row = row_for(ORG, ASSOCIATE_SWE, fetch_recorded_form(ASSOCIATE_SWE["jobUrl"]))
        self.assertEqual(row["g2_blockers"], "broad_sponsorship_question")
        self.assertTrue(row["broad_sponsorship_question"])
        self.assertFalse(row["export_control_question"])
        self.assertFalse(row["external_artifact"])
        self.assertEqual(row["required_count"], 11)
        self.assertEqual(row["required_essays"], "")
        self.assertFalse(row["g2_candidate"])
        self.assertEqual(row["applyUrl"], ASSOCIATE_SWE["applyUrl"])
        self.assertIn("workplaceType=Hybrid", row["notes"])

    def test_clean_open_form_on_fulltime_or_intern_onsite_posting(self):
        self.assertTrue(g2_candidate(EMPLOYER, job(), clean_form()))
        self.assertTrue(g2_candidate(EMPLOYER, job(employmentType="Intern"), clean_form()))
        self.assertFalse(g2_candidate(EMPLOYER, job(employmentType="PartTime"), clean_form()))
        self.assertFalse(g2_candidate(EMPLOYER, job(workplaceType="Remote"), clean_form()))
        self.assertFalse(g2_candidate(EMPLOYER, job(), clean_form(g2_blockers=["required_essay"])))
        self.assertFalse(g2_candidate(EMPLOYER, job(), {"url": "u", "org": "acme", "open": False}))
        self.assertFalse(g2_candidate(EMPLOYER, job(), {"url": "u", "org": "acme", "error": "HTTPError: 500"}))
        self.assertFalse(g2_candidate({"slug": "clera", "company": "Clera", "kind": "agency"}, job(), clean_form()),
                         "an agency board is triage material, never a G2 row")

    def test_closed_or_failed_probe_leaves_form_facts_blank(self):
        closed = row_for(ORG, job(), {"url": "u", "org": "acme", "open": False})
        self.assertEqual(closed["required_count"], "")
        self.assertEqual(closed["broad_sponsorship_question"], "")
        self.assertIn("form: closed", closed["notes"])
        failed = row_for(ORG, job(), {"url": "u", "org": "acme", "error": "OSError: reset"})
        self.assertIn("form: OSError: reset", failed["notes"])
        self.assertFalse(failed["g2_candidate"])


class TestSweep(unittest.TestCase):
    def test_board_error_is_one_row_and_the_sweep_continues(self):
        orgs = [{"slug": "broken", "company": "Broken"}, {"slug": "acme", "company": "Acme"}]

        def fetch_board(slug):
            if slug == "broken":
                raise OSError("HTTP Error 404: Not Found")
            return [job(), job(title="Senior Software Engineer")]

        rows, stats = sweep(orgs, DOMAIN, NOW, 7, fetch_board=fetch_board, fetch_form=lambda url: clean_form(), pause=0)
        self.assertEqual([r["slug"] for r in rows], ["broken", "acme"])
        self.assertEqual(rows[0]["notes"], "board: OSError: HTTP Error 404: Not Found")
        self.assertEqual(rows[0]["title"], "")
        self.assertTrue(rows[1]["g2_candidate"])
        self.assertEqual(stats, {"orgs": 2, "orgs_failed": 1, "jobs_seen": 2, "kept": 1, "g2_candidates": 1})

    def test_form_exception_lands_in_notes(self):
        def fetch_form(url):
            raise ValueError("bad json")

        rows, _ = sweep([ORG], DOMAIN, NOW, 7, fetch_board=lambda slug: [job()], fetch_form=fetch_form, pause=0)
        self.assertEqual(rows[0]["notes"], "form: ValueError: bad json;workplaceType=OnSite")
        self.assertFalse(rows[0]["g2_candidate"])


class TestOutputs(unittest.TestCase):
    def test_csv_columns_and_round_trip(self):
        rows, _ = sweep([ORG], DOMAIN, NOW, 7, fetch_board=lambda slug: [job()], fetch_form=lambda url: clean_form(), pause=0)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sweep.csv"
            write_csv(rows, path)
            with path.open(newline="") as f:
                reader = csv.DictReader(f)
                self.assertEqual(tuple(reader.fieldnames), COLUMNS)
                back = list(reader)
        self.assertEqual(len(back), 1)
        self.assertEqual(back[0]["g2_candidate"], "True")
        self.assertEqual(back[0]["required_count"], "3")
        self.assertEqual(back[0]["applyUrl"], job()["applyUrl"])

    def test_digest_lists_candidates_first(self):
        rows = [row_for(ORG, job(title="Blocked Software Engineer"), clean_form(g2_blockers=["required_essay"])),
                row_for(ORG, job(title="Clean Software Engineer"), clean_form()),
                sweep_mod.error_row({"slug": "broken", "company": "Broken"}, "board: OSError: down")]
        text = digest(rows, {"orgs": 2, "orgs_failed": 1, "jobs_seen": 2, "kept": 2, "g2_candidates": 1}, "2026-09-03T14", 7)
        head, tail = text.split("## Kept, blocked or closed")
        self.assertIn("Clean Software Engineer", head)
        self.assertNotIn("Blocked Software Engineer", head)
        self.assertIn("required_essay", tail)
        self.assertIn("- broken: board: OSError: down", tail)


class TestSeedList(unittest.TestCase):
    def test_orgs_sorted_and_cover_careers_boards_and_verified_slugs(self):
        orgs = load_orgs(ROOT / "knowledge" / "ashby_orgs.yaml")
        slugs = [o["slug"] for o in orgs]
        self.assertEqual(slugs, sorted(slugs))
        self.assertEqual(len(slugs), len(set(slugs)))
        boards = yaml.safe_load((ROOT / "knowledge" / "careers_boards.yaml").read_text())
        self.assertTrue(set(boards["ashby"].values()) <= set(slugs))
        verified = {"kayak", "anyscale", "meshy", "midjourney", "runway", "chartahealth", "clera", "bland",
                    "northwoodspace", "notion", "datologyai", "lightfield"}
        self.assertTrue(verified <= set(slugs))
        self.assertTrue(all(o["company"] for o in orgs))


if __name__ == "__main__":
    unittest.main()
