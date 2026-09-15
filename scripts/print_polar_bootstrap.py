#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grokbot_policy import GROK_WORKFLOW_NAMES, grok_bootstrap_prompt  # noqa: E402
from polar_policy import TRUSTED_WORKFLOW_NAMES, bootstrap_prompt  # noqa: E402

EXECUTORS = {
    "polar": (TRUSTED_WORKFLOW_NAMES, bootstrap_prompt),
    "grokbot": (GROK_WORKFLOW_NAMES, grok_bootstrap_prompt),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Print the trust-delegation bootstrap for one saved Polar Workflow "
            "or one Grok Bot routine."
        )
    )
    parser.add_argument("--list", action="store_true", help="Print workflow names.")
    parser.add_argument(
        "--executor",
        choices=sorted(EXECUTORS),
        default="polar",
        help="polar (saved Polar Workflow, default) or grokbot (Grok Bot routine).",
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        help="Workflow name for the chosen executor.",
    )
    args = parser.parse_args(argv)
    names, render = EXECUTORS[args.executor]
    if args.list:
        for name in names:
            print(name)
        return 0
    if not args.workflow:
        parser.print_help()
        return 2
    if args.workflow not in names:
        parser.error(
            f"unknown {args.executor} workflow {args.workflow!r}; choose from {', '.join(names)}"
        )
    sys.stdout.write(render(args.workflow))
    return 0


if __name__ == "__main__":
    sys.exit(main())
