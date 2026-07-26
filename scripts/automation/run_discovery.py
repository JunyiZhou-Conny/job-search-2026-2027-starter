#!/usr/bin/env python3
"""One-shot discovery run: Jobright matches + board lists + merge.

Intended cadence (see docs/automation_macos.md):
  - Morning (~08:30): full discovery
  - Afternoon (~16:00): optional refresh for late HR postings
  - True real-time on every new posting: not yet; experiment later

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
        codes.append(run([py, str(AUTO / "merge_discovery.py")], logf))
        logf.write(f"done codes={codes}\n")

    print(log_path)
    # Jobright export may fail without session; boards+merge still valuable
    return 0 if codes[-1] == 0 and codes[-2] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
