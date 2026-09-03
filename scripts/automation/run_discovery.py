#!/usr/bin/env python3
"""One-shot discovery run: Jobright matches + board lists + Ashby sweep + merge.

Cadence (see docs/automation/DAILY_JOB_DISCOVERY.md): two Cursor Automations,
morning at 09:00 and evening at 18:00 America/New_York (13:xx and 22:xx UTC in
summer). Each run stamps its merged output with the UTC run stamp
YYYY-MM-DDTHH, so the two runs of one day never overwrite each other.
True real-time on every new posting: not yet; experiment later.

Stamps fetched_at inside each exporter so we know WHEN data was pulled.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTO = ROOT / "scripts" / "automation"
LOG_DIR = ROOT / "generated" / "logs"


def run(cmd: list[str], logf) -> int:
    logf.write(f"$ {' '.join(cmd)}\n")
    logf.flush()
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if proc.stdout:
        logf.write(proc.stdout + ("" if proc.stdout.endswith("\n") else "\n"))
    if proc.stderr:
        logf.write(proc.stderr + ("" if proc.stderr.endswith("\n") else "\n"))
    logf.write(f"exit={proc.returncode}\n\n")
    return proc.returncode


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"discovery_{stamp}.log"
    py = sys.executable
    codes = []

    with log_path.open("w", encoding="utf-8") as logf:
        logf.write(f"run_discovery start {datetime.now().isoformat()}\n\n")
        # Personalized shortlist (needs jobright_storage.json; OK if thin)
        codes.append(run([py, str(AUTO / "export_jobright_discovery.py")], logf))
        # Balanced board lists (intern + newgrad minisites)
        codes.append(run([py, str(AUTO / "export_board_lists.py")], logf))
        # Credential-free Ashby boards + form facts (ok if a board is down)
        codes.append(run([py, str(AUTO / "export_ashby_boards.py"), "--days", "7"], logf))
        codes.append(run([py, str(AUTO / "merge_discovery.py")], logf))
        logf.write(f"done codes={codes}\n")

    print(log_path)
    # Jobright and the Ashby sweep may fail without session or on a down board.
    # Boards plus merge are still a useful run.
    return 0 if codes[-1] == 0 and codes[1] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
