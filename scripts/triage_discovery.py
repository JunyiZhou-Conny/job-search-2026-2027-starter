#!/usr/bin/env python3
"""Prepare a discovery pack for AI triage — does NOT decide keep/later/skip.

Flow:
  1) Discovery scrapers write data/discovery/YYYY-MM-DD_all.csv
  2) This script copies/normalizes a review pack + prints instructions
  3) AI agent reads knowledge/discovery_triage_rules.yaml + the CSV
     and writes generated/discovery_triage_YYYY-MM-DD.csv

No regex hardcode for remote / grad windows / role filters here.
Those live as guide rules for the AI in knowledge/discovery_triage_rules.yaml.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "data" / "discovery"
GEN = ROOT / "generated"
RULES = ROOT / "knowledge" / "discovery_triage_rules.yaml"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()
    day = args.date

    src = DISC / f"{day}_all.csv"
    if not src.exists():
        raise SystemExit(
            f"Missing {src}\nRun: python3 scripts/automation/run_discovery.py"
        )
    if not RULES.exists():
        raise SystemExit(f"Missing triage rules: {RULES}")

    GEN.mkdir(parents=True, exist_ok=True)
    pack = GEN / f"discovery_for_triage_{day}.csv"
    shutil.copyfile(src, pack)

    with pack.open(newline="", encoding="utf-8-sig") as f:
        n = sum(1 for _ in csv.DictReader(f))

    prompt = GEN / f"discovery_triage_prompt_{day}.md"
    prompt.write_text(
        "\n".join(
            [
                f"# AI triage pack — {day}",
                "",
                f"- Rows: **{n}**",
                f"- Input CSV: `{pack.relative_to(ROOT)}`",
                f"- Rules: `{RULES.relative_to(ROOT)}`",
                f"- Profile: `config/profile.yaml`",
                "",
                "## Agent task",
                "",
                "1. Read the rules YAML (guide_rules) — do not invent new hard gates.",
                "2. Read every row of the input CSV (board fields only unless ambiguous).",
                "3. Write:",
                f"   - `generated/discovery_triage_{day}.csv`",
                f"   - `generated/discovery_triage_{day}.md`",
                "4. Leave `user_confirm` empty. Do not edit `data/applications.csv`.",
                "",
                "In Cursor: run `/triage-discovery` or ask the agent to triage this pack.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(pack)
    print(prompt)
    print(f"rows={n}")
    print("Next: AI reads rules + CSV → writes generated/discovery_triage_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
