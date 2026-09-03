#!/usr/bin/env python3
"""Prepare a discovery pack for AI triage — does NOT decide keep/later/skip.

Flow:
  1) merge_discovery.py writes data/discovery/{RUN}_all.csv
     (RUN = UTC run stamp YYYY-MM-DDTHH; older files use YYYY-MM-DD)
  2) This script copies/normalizes a review pack + prints instructions
  3) AI agent reads knowledge/discovery_triage_rules.yaml + the CSV
     and writes generated/discovery_triage_{RUN}.csv

No regex hardcode for remote / grad windows / role filters here.
Those live as guide rules for the AI in knowledge/discovery_triage_rules.yaml.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISC = ROOT / "data" / "discovery"
GEN = ROOT / "generated"
RULES = ROOT / "knowledge" / "discovery_triage_rules.yaml"

MERGED_SUFFIX = "_all.csv"


def newest_merged() -> Path | None:
    files = list(DISC.glob(f"*{MERGED_SUFFIX}"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def build_pack(run: str) -> tuple[Path, Path, int]:
    src = DISC / f"{run}{MERGED_SUFFIX}"
    if not src.exists():
        raise SystemExit(
            f"Missing {src}\nRun: python3 scripts/automation/run_discovery.py"
        )
    if not RULES.exists():
        raise SystemExit(f"Missing triage rules: {RULES}")

    GEN.mkdir(parents=True, exist_ok=True)
    pack = GEN / f"discovery_for_triage_{run}.csv"
    shutil.copyfile(src, pack)

    with pack.open(newline="", encoding="utf-8-sig") as f:
        n = sum(1 for _ in csv.DictReader(f))

    prompt = GEN / f"discovery_triage_prompt_{run}.md"
    prompt.write_text(
        "\n".join(
            [
                f"# AI triage pack — {run}",
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
                f"   - `generated/discovery_triage_{run}.csv`",
                f"   - `generated/discovery_triage_{run}.md`",
                "4. Leave `user_confirm` empty. Do not edit `data/applications.csv`.",
                "",
                "In Cursor: run `/triage-discovery` or ask the agent to triage this pack.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return pack, prompt, n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--date",
        default=None,
        metavar="RUN",
        help="run stamp YYYY-MM-DDTHH (UTC) or a plain YYYY-MM-DD; default: the newest *_all.csv",
    )
    args = ap.parse_args(argv)

    run = args.date
    if not run:
        src = newest_merged()
        if not src:
            raise SystemExit(
                f"No *{MERGED_SUFFIX} under {DISC}\nRun: python3 scripts/automation/run_discovery.py"
            )
        run = src.name[: -len(MERGED_SUFFIX)]

    pack, prompt, n = build_pack(run)
    print(f"run={run}")
    print(pack)
    print(prompt)
    print(f"rows={n}")
    print(f"Next: AI reads rules + CSV → writes generated/discovery_triage_{run}.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
