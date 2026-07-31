#!/usr/bin/env python3
"""Cheap change detection for the files the apply queue renders from.

The queue is only useful if it tells the truth. If a CSV is edited by another
script, by a git pull, or by a second browser tab, an open page must notice —
so the server fingerprints the inputs and pushes an event when they move.

mtime+size over a handful of small CSVs is enough here: no dependency, no
inotify/FSEvents portability problem, and it costs microseconds per poll.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GENERATED = ROOT / "generated"


def watched_paths() -> list[Path]:
    paths = [
        DATA / "applications.csv",
        DATA / "job_decisions.csv",
        DATA / "activity_log.csv",
    ]
    paths.extend(sorted(GENERATED.glob("discovery_triage_*.csv")))
    return paths


def fingerprint() -> str:
    """Stable string that changes whenever any watched file changes."""
    parts: list[str] = []
    for path in watched_paths():
        try:
            stat = path.stat()
            parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
        except FileNotFoundError:
            parts.append(f"{path.name}:missing")
    return "|".join(parts)


class Watcher:
    """Tracks the last fingerprint and reports transitions."""

    def __init__(self) -> None:
        self.current = fingerprint()

    def changed(self) -> bool:
        latest = fingerprint()
        if latest != self.current:
            self.current = latest
            return True
        return False
