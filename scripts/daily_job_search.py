#!/usr/bin/env python3
"""Daily runner: validate → import → dedupe → plans → dashboard → calendar dry-run."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOG_DIR = ROOT / "generated" / "logs"


def run(cmd: list[str], logf) -> int:
    logf.write(f"$ {' '.join(cmd)}\n")
    logf.flush()
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if proc.stdout:
        logf.write(proc.stdout + ("\n" if not proc.stdout.endswith("\n") else ""))
    if proc.stderr:
        logf.write(proc.stderr + ("\n" if not proc.stderr.endswith("\n") else ""))
    logf.write(f"exit={proc.returncode}\n\n")
    return proc.returncode


def latest_simplify() -> Path | None:
    folder = ROOT / "data" / "imports" / "simplify"
    files = sorted(folder.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skip-import", action="store_true")
    p.add_argument("--write-calendar", action="store_true")
    args = p.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    py = sys.executable
    codes = []

    with log_path.open("w", encoding="utf-8") as logf:
        logf.write(f"daily_job_search start {datetime.now().isoformat()}\n\n")
        codes.append(run([py, str(SCRIPTS / "migrate_schema.py")], logf))
        codes.append(run([py, str(SCRIPTS / "validate_data.py")], logf))

        if not args.skip_import:
            latest = latest_simplify()
            if latest:
                codes.append(run([py, str(SCRIPTS / "jobsearch.py"), "import-simplify", "--file", str(latest)], logf))
            else:
                logf.write("no Simplify CSV found; skip import\n\n")

        # Discovery boards (intern + newgrad + Jobright matches). Safe to re-run; stamps fetched_at.
        codes.append(run([py, str(SCRIPTS / "automation" / "run_discovery.py")], logf))

        codes.append(run([py, str(SCRIPTS / "dedupe_applications.py")], logf))
        codes.append(run([py, str(SCRIPTS / "confirm_labels.py"), "--batch"], logf))
        codes.append(run([py, str(SCRIPTS / "generate_outreach_queue.py")], logf))
        codes.append(run([py, str(SCRIPTS / "generate_daily_plan.py")], logf))
        codes.append(run([py, str(SCRIPTS / "generate_analytics.py")], logf))
        codes.append(run([py, str(SCRIPTS / "jobsearch.py"), "dashboard"], logf))
        cal = [py, str(SCRIPTS / "generate_calendar.py")]
        if args.write_calendar:
            cal.append("--write")
        else:
            cal.append("--dry-run")
        codes.append(run(cal, logf))
        logf.write(f"done max_exit={max(codes) if codes else 0}\n")

    print(log_path)
    # validate errors should not hard-fail daily planning during trial
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
