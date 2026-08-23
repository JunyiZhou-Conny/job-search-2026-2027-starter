#!/usr/bin/env python3
"""Report whether this machine can run Simplify autofill.

Ready means two things, both in the profile computer-use will attach to:

1. Software — Simplify Copilot is installed. Detected by publisher signals
   in the extension manifest (short_name / author / homepage), not by a
   pinned Chrome folder id. Store and unpacked installs get different ids.
2. Session — a Simplify login cookie named ``refresh`` exists in that
   profile. Playwright ``secrets/simplify_storage.json`` is export-only
   and does not count.

A folder id is the extension *package*, not the person. Identity match
against ``config/profile.yaml`` is reported separately and does not flip
``ready`` — Chrome encrypts cookies, so this script cannot prove the
account is yours without decrypting secrets.

Usage:
  python3 scripts/automation/check_apply_harness.py
  python3 scripts/automation/check_apply_harness.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

COPILOT_SHORT_NAME = "Simplify Copilot"
COPILOT_AUTHOR = "Simplify Jobs Inc."
COPILOT_HOMEPAGE = "https://simplify.jobs"
SESSION_COOKIE_NAME = "refresh"
SESSION_COOKIE_HOST_SUFFIX = "simplify.jobs"
BRANDED_CHROME = Path("/opt/google/chrome/chrome")
BRANDED_PATH_MARKERS = (
    "/opt/google/chrome/chrome",
    "/opt/google/chrome/google-chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
)
_COOKIE_SIDECARS = ("-wal", "-shm")


def _is_branded_browser_path(path: str | None) -> bool:
    if not path:
        return False
    return any(path == marker or path.endswith(marker) for marker in BRANDED_PATH_MARKERS)


def _first_playwright_chromium(home: Path) -> Path | None:
    cache = home / ".cache" / "ms-playwright"
    if not cache.exists():
        return None
    matches = sorted(cache.glob("chromium-*/chrome-linux*/chrome"))
    return matches[-1] if matches else None


def _list_extension_ids(profile: Path) -> list[str]:
    ids: list[str] = []
    for base in (profile / "Default" / "Extensions", profile / "Extensions"):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and not child.name.startswith("Temp"):
                ids.append(child.name)
    return ids


def _iter_extension_manifests(profile: Path) -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    for ext_id in _list_extension_ids(profile):
        for base in (profile / "Default" / "Extensions" / ext_id, profile / "Extensions" / ext_id):
            if not base.is_dir():
                continue
            manifests = sorted(base.rglob("manifest.json"))
            if not manifests:
                continue
            try:
                data = json.loads(manifests[0].read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict):
                found.append((ext_id, data))
            break
    return found


def is_copilot_manifest(manifest: dict[str, Any]) -> bool:
    """True when the manifest looks like Simplify Copilot, regardless of folder id."""
    short = str(manifest.get("short_name") or "").strip()
    name = str(manifest.get("name") or "").strip()
    author = str(manifest.get("author") or "").strip()
    homepage = str(manifest.get("homepage_url") or "").strip().rstrip("/").lower()
    if short == COPILOT_SHORT_NAME:
        return True
    if COPILOT_SHORT_NAME in name and "simplify.jobs" in homepage:
        return True
    if author == COPILOT_AUTHOR and homepage == COPILOT_HOMEPAGE:
        return True
    return False


def find_copilot(profile: Path) -> dict[str, Any]:
    matches = [
        ext_id for ext_id, manifest in _iter_extension_manifests(profile) if is_copilot_manifest(manifest)
    ]
    return {
        "installed": bool(matches),
        "extension_ids": matches,
    }


def _cookie_db_paths(profile: Path) -> list[Path]:
    return [
        profile / "Default" / "Network" / "Cookies",
        profile / "Default" / "Cookies",
    ]


def _sidecar_path(db_path: Path, suffix: str) -> Path:
    return Path(str(db_path) + suffix)


def _unlink_copied_db(dest_path: Path) -> None:
    dest_path.unlink(missing_ok=True)
    for suffix in _COOKIE_SIDECARS:
        _sidecar_path(dest_path, suffix).unlink(missing_ok=True)


def _copy_readable(src: Path) -> Path | None:
    if not src.is_file():
        return None
    fd, dest = tempfile.mkstemp(prefix="harness-cookies-")
    os.close(fd)
    dest_path = Path(dest)
    try:
        shutil.copy2(src, dest_path)
        # Chromium uses WAL; a fresh login cookie may exist only in -wal.
        # Copy sidecars as a pair. A partial copy can make the snapshot
        # unreadable even when the main file already has the cookie.
        try:
            for suffix in _COOKIE_SIDECARS:
                sibling = _sidecar_path(src, suffix)
                if sibling.is_file():
                    shutil.copy2(sibling, _sidecar_path(dest_path, suffix))
        except OSError:
            for suffix in _COOKIE_SIDECARS:
                _sidecar_path(dest_path, suffix).unlink(missing_ok=True)
    except OSError:
        _unlink_copied_db(dest_path)
        return None
    return dest_path


def _cookie_db_query_refresh(db_path: Path) -> bool | None:
    """True/False if queried; None if this snapshot could not be read."""
    try:
        # Private temp copy: allow SQLite to rebuild -shm from -wal.
        con = sqlite3.connect(db_path)
    except sqlite3.Error:
        return None
    try:
        cols = {row[1] for row in con.execute("PRAGMA table_info(cookies)")}
        if not {"host_key", "name"} <= cols:
            return None
        select = "SELECT host_key, name, value"
        if "encrypted_value" in cols:
            select += ", encrypted_value"
        for row in con.execute(select + " FROM cookies"):
            host = str(row[0] or "").lower()
            name = str(row[1] or "")
            if name != SESSION_COOKIE_NAME:
                continue
            if not host.endswith(SESSION_COOKIE_HOST_SUFFIX):
                continue
            value = row[2]
            encrypted = row[3] if len(row) > 3 else b""
            if value:
                return True
            if encrypted:
                return True
        return False
    except sqlite3.Error:
        return None
    finally:
        con.close()


def cookie_db_has_simplify_refresh(db_path: Path) -> bool | None:
    """True if a Simplify ``refresh`` cookie exists. Never returns cookie values.

    None means the snapshot could not be queried — not a conclusive miss.
    """
    found = _cookie_db_query_refresh(db_path)
    if found is not None:
        return found
    # Drop -shm first so SQLite can rebuild it from -wal; then the WAL
    # itself if the pair is still unreadable (torn copy while Chrome wrote).
    for suffix in ("-shm", "-wal"):
        sidecar = _sidecar_path(db_path, suffix)
        if not sidecar.is_file():
            continue
        sidecar.unlink(missing_ok=True)
        found = _cookie_db_query_refresh(db_path)
        if found is not None:
            return found
    return None


def inspect_session(profile: Path) -> dict[str, Any]:
    """Look for a Simplify refresh cookie. Status is present / missing / unknown."""
    dbs = [p for p in _cookie_db_paths(profile) if p.is_file()]
    if not dbs:
        return {"status": "missing", "reason": "no Chrome cookie database in this profile"}

    readable = False
    for src in dbs:
        copied = _copy_readable(src)
        if copied is None:
            continue
        try:
            found = cookie_db_has_simplify_refresh(copied)
            if found:
                return {"status": "present", "reason": "simplify.jobs refresh cookie exists"}
            if found is False:
                readable = True
        finally:
            _unlink_copied_db(copied)
    if not readable:
        return {"status": "unknown", "reason": "Chrome cookie database exists but could not be read"}
    return {"status": "missing", "reason": "no simplify.jobs refresh cookie"}


def _storage_state_path() -> Path | None:
    candidate = ROOT / "secrets" / "simplify_storage.json"
    if candidate.is_file() and candidate.stat().st_size > 0:
        return candidate
    return None


def inspect_identity() -> dict[str, str]:
    profile_yaml = ROOT / "config" / "profile.yaml"
    if not profile_yaml.is_file():
        return {
            "identity_match": "unknown",
            "identity_match_reason": "config/profile.yaml is missing",
        }
    return {
        "identity_match": "unknown",
        "identity_match_reason": (
            "Simplify account identity is not readable from encrypted cookies. "
            "Confirm the dashboard name/email against config/profile.yaml; "
            "that is a person check, not a package-id check."
        ),
    }


def _profile_report(path: Path) -> dict[str, Any]:
    copilot = find_copilot(path)
    return {
        "path": str(path),
        "exists": path.is_dir(),
        "extension_ids": _list_extension_ids(path),
        "simplify_installed": copilot["installed"],
        "copilot_extension_ids": copilot["extension_ids"],
    }


def inspect(home: Path | None = None) -> dict[str, Any]:
    home = home or Path.home()
    chrome_profile = home / ".config" / "google-chrome"
    chromium_profile = home / ".config" / "chromium"
    harness_profile = home / ".config" / "simplify-harness"
    playwright_path = _first_playwright_chromium(home)
    playwright = str(playwright_path) if playwright_path else None
    branded = BRANDED_CHROME.exists()

    computer_use_browser = os.environ.get("CHROME_EXECUTABLE_PATH") or (
        str(BRANDED_CHROME) if branded else playwright
    )
    using_branded = _is_branded_browser_path(computer_use_browser)

    profiles = {
        "google-chrome": _profile_report(chrome_profile),
        "chromium": _profile_report(chromium_profile),
        "simplify-harness": _profile_report(harness_profile),
    }

    if using_branded:
        attached = [("google-chrome", chrome_profile)]
    else:
        attached = [("simplify-harness", harness_profile), ("chromium", chromium_profile)]

    copilot_ids: list[str] = []
    attached_name = None
    attached_profile: Path | None = None
    for name, path in attached:
        ids = profiles[name]["copilot_extension_ids"]
        if ids:
            copilot_ids = ids
            attached_name = name
            attached_profile = path
            break
    if attached_profile is None:
        attached_name, attached_profile = attached[0]

    session_file = _storage_state_path()
    cookie_session = inspect_session(attached_profile)
    session_status = cookie_session["status"]
    session_reason = cookie_session["reason"]

    copilot_visible = bool(copilot_ids)
    session_ok = session_status == "present"
    ready = copilot_visible and session_ok

    blockers: list[str] = []
    if not copilot_visible:
        if using_branded:
            blockers.append(
                "Simplify Copilot (publisher signals) is not in ~/.config/google-chrome; "
                "branded Chrome also ignores --load-extension, so install from the Store"
            )
        else:
            blockers.append(
                "Simplify Copilot (publisher signals) is not in the computer-use "
                "Chromium / simplify-harness profile"
            )
    if session_status == "missing":
        blockers.append(
            "No Simplify session: log into simplify.jobs in the computer-use browser "
            "(refresh cookie)"
        )
    elif session_status == "unknown":
        blockers.append(f"Simplify session unknown: {session_reason}")
    if playwright is None and not branded:
        blockers.append("Playwright Chromium is not installed")
    legacy_tmp = Path("/tmp/apply_trial").is_dir()
    if legacy_tmp:
        blockers.append(
            "/tmp/apply_trial exists on this VM only — it will not survive the next agent"
        )

    identity = inspect_identity()

    if ready:
        next_step = "Harness ready. Open ATS tabs, autofill, do not Submit."
    elif not copilot_visible:
        next_step = (
            "See docs/automation/APPLY_HARNESS.md — Take Control, install "
            "Simplify Copilot from the Store in the computer-use browser."
        )
    else:
        next_step = (
            "See docs/automation/APPLY_HARNESS.md — Copilot is installed; "
            "log into Simplify in this browser, then snapshot the personal environment."
        )

    return {
        "ready": ready,
        "copilot": {
            "installed": copilot_visible,
            "extension_ids": copilot_ids,
            "detected_by": "publisher_signals",
            "profile": attached_name,
        },
        "session": {
            "status": session_status,
            "reason": session_reason,
            "storage_state": str(session_file) if session_file else None,
        },
        "identity_match": identity["identity_match"],
        "identity_match_reason": identity["identity_match_reason"],
        "branded_chrome_present": branded,
        "playwright_chromium": playwright,
        "computer_use_browser": computer_use_browser,
        "using_branded_chrome": using_branded,
        "profiles": profiles,
        "session_storage_state": str(session_file) if session_file else None,
        "legacy_tmp_harness": legacy_tmp,
        "blockers": blockers,
        "next_step": next_step,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = inspect()
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("Apply harness check")
        print(f"  ready: {report['ready']}")
        print(f"  computer-use browser: {report['computer_use_browser']}")
        print(f"  branded Chrome: {report['using_branded_chrome']}")
        print(f"  playwright chromium: {report['playwright_chromium']}")
        copilot = report["copilot"]
        print(f"  copilot installed: {copilot['installed']}")
        print(f"  copilot ids (informational): {copilot['extension_ids'] or '(none)'}")
        print(f"  copilot detected by: {copilot['detected_by']}")
        print(f"  session: {report['session']['status']} ({report['session']['reason']})")
        print(f"  identity_match: {report['identity_match']}")
        chrome = report["profiles"]["google-chrome"]
        print(f"  chrome profile extensions: {chrome['extension_ids'] or '(none)'}")
        if report["blockers"]:
            print("  blockers:")
            for item in report["blockers"]:
                print(f"    - {item}")
        print(f"  next: {report['next_step']}")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
