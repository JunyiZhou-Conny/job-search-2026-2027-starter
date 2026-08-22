#!/usr/bin/env python3
"""Harness check: publisher signals + session cookie, not a pinned folder id."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "automation"))

import check_apply_harness as harness  # noqa: E402

COPILOT_MANIFEST = {
    "name": "Simplify Copilot - Autofill job applications, job tracker & AI resumes",
    "short_name": "Simplify Copilot",
    "author": "Simplify Jobs Inc.",
    "homepage_url": "https://simplify.jobs/",
    "version": "3.0.8",
}

OTHER_MANIFEST = {
    "name": "Chrome Web Store Payments",
    "version": "1.0.0.6",
}


def _write_extension(profile: Path, ext_id: str, manifest: dict) -> None:
    dest = profile / "Default" / "Extensions" / ext_id / "3.0.8_0"
    dest.mkdir(parents=True)
    (dest / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _write_refresh_cookie(profile: Path, *, present: bool = True) -> None:
    db = profile / "Default" / "Cookies"
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute(
        "CREATE TABLE cookies (host_key TEXT, name TEXT, value TEXT, encrypted_value BLOB)"
    )
    if present:
        con.execute(
            "INSERT INTO cookies VALUES (?, ?, ?, ?)",
            (".simplify.jobs", "refresh", "", b"encrypted-not-a-secret"),
        )
    else:
        con.execute(
            "INSERT INTO cookies VALUES (?, ?, ?, ?)",
            (".simplify.jobs", "_ga", "", b"analytics"),
        )
    con.commit()
    con.close()


class TestPublisherSignals(unittest.TestCase):
    def test_store_manifest_is_copilot(self):
        self.assertTrue(harness.is_copilot_manifest(COPILOT_MANIFEST))

    def test_unrelated_manifest_is_not_copilot(self):
        self.assertFalse(harness.is_copilot_manifest(OTHER_MANIFEST))

    def test_find_copilot_ignores_folder_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "chrome"
            _write_extension(profile, "zzzzdifferentfolderidaaaaaaaaaaa", COPILOT_MANIFEST)
            found = harness.find_copilot(profile)
        self.assertTrue(found["installed"])
        self.assertEqual(found["extension_ids"], ["zzzzdifferentfolderidaaaaaaaaaaa"])


class TestSessionCookie(unittest.TestCase):
    def test_refresh_cookie_is_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            _write_refresh_cookie(profile, present=True)
            report = harness.inspect_session(profile)
        self.assertEqual(report["status"], "present")

    def test_other_cookies_are_not_a_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            _write_refresh_cookie(profile, present=False)
            report = harness.inspect_session(profile)
        self.assertEqual(report["status"], "missing")

    def test_unreadable_cookie_db_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            db = profile / "Default" / "Cookies"
            db.parent.mkdir(parents=True)
            db.write_bytes(b"not a sqlite database")
            report = harness.inspect_session(profile)
        self.assertEqual(report["status"], "unknown")

    def test_torn_wal_does_not_hide_checkpointed_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            db = profile / "Default" / "Cookies"
            db.parent.mkdir(parents=True)
            con = sqlite3.connect(db)
            con.execute("PRAGMA journal_mode=WAL")
            con.execute(
                "CREATE TABLE cookies (host_key TEXT, name TEXT, value TEXT, encrypted_value BLOB)"
            )
            con.execute(
                "INSERT INTO cookies VALUES (?, ?, ?, ?)",
                (".simplify.jobs", "refresh", "", b"encrypted-not-a-secret"),
            )
            con.commit()
            con.execute("PRAGMA wal_checkpoint(FULL)")
            con.close()
            Path(str(db) + "-wal").write_bytes(b"\x37\x7f\x06\x82" + b"\x00" * 28)
            report = harness.inspect_session(profile)
        self.assertEqual(report["status"], "present")

    def test_torn_wal_without_checkpoint_is_unknown_not_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp)
            db = profile / "Default" / "Cookies"
            db.parent.mkdir(parents=True)
            con = sqlite3.connect(db)
            try:
                con.execute("PRAGMA journal_mode=WAL")
                con.execute("PRAGMA wal_autocheckpoint=0")
                con.execute(
                    "CREATE TABLE cookies (host_key TEXT, name TEXT, value TEXT, encrypted_value BLOB)"
                )
                con.execute(
                    "INSERT INTO cookies VALUES (?, ?, ?, ?)",
                    (".simplify.jobs", "refresh", "", b"encrypted-not-a-secret"),
                )
                con.commit()
                Path(str(db) + "-wal").write_bytes(b"\x37\x7f\x06\x82" + b"\x00" * 28)
                report = harness.inspect_session(profile)
            finally:
                con.close()
        self.assertEqual(report["status"], "unknown")


class TestInspectReady(unittest.TestCase):
    def test_empty_home_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = harness.inspect(home=Path(tmp))
        self.assertFalse(report["ready"])
        self.assertTrue(report["blockers"])
        self.assertEqual(report["identity_match"], "unknown")

    def test_store_id_with_session_is_ready_on_branded_chrome(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".config" / "google-chrome"
            _write_extension(profile, "pbanhockgagggenencehbnadejlgchfc", COPILOT_MANIFEST)
            _write_refresh_cookie(profile, present=True)
            report = harness.inspect(home=home)
        if report["using_branded_chrome"]:
            self.assertTrue(report["ready"])
            self.assertTrue(report["copilot"]["installed"])
            self.assertEqual(report["session"]["status"], "present")
        else:
            self.assertFalse(report["ready"])

    def test_unpacked_id_with_session_is_ready_on_branded_chrome(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".config" / "google-chrome"
            _write_extension(profile, "cdcddpbdpgfipkmobdipjfheopledajg", COPILOT_MANIFEST)
            _write_refresh_cookie(profile, present=True)
            report = harness.inspect(home=home)
        if report["using_branded_chrome"]:
            self.assertTrue(report["ready"])
            self.assertEqual(
                report["copilot"]["extension_ids"],
                ["cdcddpbdpgfipkmobdipjfheopledajg"],
            )

    def test_storage_json_does_not_fake_session_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".config" / "google-chrome"
            _write_extension(profile, "pbanhockgagggenencehbnadejlgchfc", COPILOT_MANIFEST)
            fake_storage = Path(tmp) / "simplify_storage.json"
            fake_storage.write_text("{}", encoding="utf-8")
            previous = harness._storage_state_path
            harness._storage_state_path = lambda: fake_storage
            try:
                report = harness.inspect(home=home)
            finally:
                harness._storage_state_path = previous
        self.assertFalse(report["ready"])
        self.assertNotEqual(report["session"]["status"], "present")
        self.assertEqual(report["session"]["storage_state"], str(fake_storage))

    def test_copilot_without_session_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".config" / "google-chrome"
            _write_extension(profile, "pbanhockgagggenencehbnadejlgchfc", COPILOT_MANIFEST)
            report = harness.inspect(home=home)
        self.assertTrue(report["profiles"]["google-chrome"]["simplify_installed"])
        if report["using_branded_chrome"]:
            self.assertFalse(report["ready"])
            self.assertEqual(report["session"]["status"], "missing")

    def test_session_without_copilot_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            profile = home / ".config" / "google-chrome"
            _write_refresh_cookie(profile, present=True)
            report = harness.inspect(home=home)
        self.assertFalse(report["ready"])
        self.assertFalse(report["copilot"]["installed"])

    def test_chrome_profile_alone_is_not_ready_for_playwright_chromium(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            chrome = home / ".config" / "google-chrome"
            _write_extension(chrome, "pbanhockgagggenencehbnadejlgchfc", COPILOT_MANIFEST)
            _write_refresh_cookie(chrome, present=True)
            fake_chromium = (
                home / ".cache" / "ms-playwright" / "chromium-1234" / "chrome-linux64" / "chrome"
            )
            fake_chromium.parent.mkdir(parents=True)
            fake_chromium.write_text("", encoding="utf-8")
            previous = os.environ.get("CHROME_EXECUTABLE_PATH")
            os.environ["CHROME_EXECUTABLE_PATH"] = str(fake_chromium)
            try:
                report = harness.inspect(home=home)
            finally:
                if previous is None:
                    os.environ.pop("CHROME_EXECUTABLE_PATH", None)
                else:
                    os.environ["CHROME_EXECUTABLE_PATH"] = previous
        self.assertFalse(report["using_branded_chrome"])
        self.assertTrue(report["profiles"]["google-chrome"]["simplify_installed"])
        self.assertFalse(report["ready"])

    def test_playwright_uses_chromium_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            chromium = home / ".config" / "chromium"
            _write_extension(chromium, "anyfolderidforunpackedcopilotaaaa", COPILOT_MANIFEST)
            _write_refresh_cookie(chromium, present=True)
            fake_chromium = (
                home / ".cache" / "ms-playwright" / "chromium-1234" / "chrome-linux64" / "chrome"
            )
            fake_chromium.parent.mkdir(parents=True)
            fake_chromium.write_text("", encoding="utf-8")
            previous = os.environ.get("CHROME_EXECUTABLE_PATH")
            os.environ["CHROME_EXECUTABLE_PATH"] = str(fake_chromium)
            try:
                report = harness.inspect(home=home)
            finally:
                if previous is None:
                    os.environ.pop("CHROME_EXECUTABLE_PATH", None)
                else:
                    os.environ["CHROME_EXECUTABLE_PATH"] = previous
        self.assertFalse(report["using_branded_chrome"])
        self.assertTrue(report["ready"])
        self.assertEqual(report["copilot"]["profile"], "chromium")


if __name__ == "__main__":
    unittest.main()
