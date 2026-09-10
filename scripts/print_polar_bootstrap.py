#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from polar_policy import TRUSTED_WORKFLOW_NAMES, bootstrap_prompt  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the Polar trust-delegation bootstrap for one saved Workflow."
    )
    parser.add_argument("--list", action="store_true", help="Print workflow names.")
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=TRUSTED_WORKFLOW_NAMES,
        help="Saved Polar Workflow name.",
    )
    args = parser.parse_args(argv)
    if args.list:
        for name in TRUSTED_WORKFLOW_NAMES:
            print(name)
        return 0
    if not args.workflow:
        parser.print_help()
        return 2
    sys.stdout.write(bootstrap_prompt(args.workflow))
    return 0


if __name__ == "__main__":
    sys.exit(main())
