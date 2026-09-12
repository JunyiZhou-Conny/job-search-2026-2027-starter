#!/usr/bin/env python3
"""Retarget Polar trusted-repo constants and operator raw URLs on a personal fork.

    python3 scripts/set_polar_trusted_repo.py OWNER/REPO
    python3 scripts/set_polar_trusted_repo.py OWNER/REPO --write
    python3 scripts/set_polar_trusted_repo.py OWNER/REPO --write --rebuild
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional, Sequence

from init_personal_copy import looks_like_upstream

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_RELATIVE = Path("scripts") / "polar_policy.py"
OPERATOR_RELATIVE = Path("knowledge") / "polar_operator.yaml"
UPSTREAM_TEMPLATE = "JunyiZhou-Conny/job-search-2026-2027-starter"
REPO_SPEC_RE = re.compile(r"^([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)$")
OWNER_ASSIGN_RE = re.compile(r'^TRUSTED_REPO_OWNER = "([^"]*)"$', re.M)
NAME_ASSIGN_RE = re.compile(r'^TRUSTED_REPO_NAME = "([^"]*)"$', re.M)


class RepoSpec(NamedTuple):
    owner: str
    name: str

    def __str__(self) -> str:
        return f"{self.owner}/{self.name}"


def parse_repo_spec(raw: str) -> Optional[RepoSpec]:
    match = REPO_SPEC_RE.fullmatch(raw.strip())
    if match is None:
        return None
    return RepoSpec(match.group(1), match.group(2))


def read_trusted_repo(text: str) -> Optional[RepoSpec]:
    owner = OWNER_ASSIGN_RE.search(text)
    name = NAME_ASSIGN_RE.search(text)
    if owner is None or name is None:
        return None
    return RepoSpec(owner.group(1), name.group(1))


def rewrite_trusted_repo(text: str, spec: RepoSpec) -> str:
    if read_trusted_repo(text) is None:
        raise ValueError("missing TRUSTED_REPO_OWNER / TRUSTED_REPO_NAME assignment lines")
    text = OWNER_ASSIGN_RE.sub(f'TRUSTED_REPO_OWNER = "{spec.owner}"', text, count=1)
    return NAME_ASSIGN_RE.sub(f'TRUSTED_REPO_NAME = "{spec.name}"', text, count=1)


def rewrite_operator_urls(text: str, spec: RepoSpec) -> str:
    return text.replace(UPSTREAM_TEMPLATE, str(spec))


def rebuild_polar_runtime(root: Path) -> int:
    completed = subprocess.run(
        ["python3", "scripts/build_polar_runtime.py"],
        cwd=root,
    )
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", help="OWNER/REPO of the personal fork")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Rewrite Polar trust URLs on this fork. Default is dry-run.",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="After --write, run scripts/build_polar_runtime.py from the repo root.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    spec = parse_repo_spec(args.repo)
    if spec is None:
        print("Refusing: expected OWNER/REPO with each side matching [A-Za-z0-9._-]+.")
        return 2
    if str(spec) == UPSTREAM_TEMPLATE:
        print(f"Refusing: OWNER/REPO is the upstream template {UPSTREAM_TEMPLATE}.")
        return 2
    if args.rebuild and not args.write:
        print("Refusing: --rebuild requires --write.")
        return 2

    path = root / POLICY_RELATIVE
    if not path.is_file():
        print(f"Missing {POLICY_RELATIVE}.")
        return 1
    text = path.read_text(encoding="utf-8")
    current = read_trusted_repo(text)
    if current is None:
        print("Could not find TRUSTED_REPO_OWNER / TRUSTED_REPO_NAME assignment lines.")
        return 1

    upstream_origin = looks_like_upstream(root)
    print(f"Current: {current}")
    print(f"Requested: {spec}")
    print(f"Origin looks like the upstream template: {'yes' if upstream_origin else 'no'}")

    if not args.write:
        print("Dry-run only. Re-run with --write to apply.")
        return 0

    if upstream_origin:
        print(f"Refusing to write: origin points at {UPSTREAM_TEMPLATE}.")
        return 2

    path.write_text(rewrite_trusted_repo(text, spec), encoding="utf-8")
    print(f"Wrote {POLICY_RELATIVE}")
    operator_path = root / OPERATOR_RELATIVE
    if operator_path.is_file():
        operator_path.write_text(
            rewrite_operator_urls(operator_path.read_text(encoding="utf-8"), spec),
            encoding="utf-8",
        )
        print(f"Wrote {OPERATOR_RELATIVE}")

    if args.rebuild:
        code = rebuild_polar_runtime(root)
        if code != 0:
            print(f"Rebuild failed with exit {code}.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
