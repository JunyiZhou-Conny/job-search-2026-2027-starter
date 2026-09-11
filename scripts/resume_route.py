#!/usr/bin/env python3
"""CLI for deterministic resume routing.

    python3 scripts/resume_route.py --role "Software Engineer" --company Google
    python3 scripts/resume_route.py --json '{"role":"ML Infrastructure Engineer"}'
    python3 scripts/resume_route.py --csv generated/discovery_triage_2026-09-02.csv
    python3 scripts/resume_route.py --benchmark
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resume_routing import JobMeta, load_policy, route, route_and_resolve  # noqa: E402

TRIAGE_GLOB = "generated/discovery_triage_*.csv"
LEGACY_TO_FAMILY = {"cloud_swe": "swe", "data_ml": "ml_ai", "health_ai": "health_ai"}


def _print_json(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2, sort_keys=False))
    return 0


def cmd_one(args: argparse.Namespace) -> int:
    if args.json:
        raw = json.loads(args.json)
        if not isinstance(raw, dict):
            raise SystemExit("--json must be an object")
        job = JobMeta.from_mapping(raw)
    else:
        job = JobMeta(
            role=args.role or "",
            company=args.company or "",
            source=args.source or "",
            board_category=args.board_category or "",
            track=args.track or "",
            location=args.location or "",
            short_text=args.short_text or "",
            legacy_cluster=args.legacy_cluster or "",
        )
    return _print_json(route_and_resolve(job))


def _iter_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cmd_csv(args: argparse.Namespace) -> int:
    rows = _iter_csv(Path(args.csv))
    out_rows = []
    for row in rows:
        payload = route_and_resolve(JobMeta.from_mapping(row))
        merged = dict(row)
        merged["resume_family"] = payload["family"]
        merged["route_confidence"] = payload["confidence"]
        merged["route_reason"] = payload["reason"]
        merged["resume_variant"] = payload["resume_variant"]
        out_rows.append(merged)
    dest = Path(args.out) if args.out else None
    if dest is None:
        for payload in out_rows:
            print(
                json.dumps(
                    {
                        "company": payload.get("company"),
                        "role": payload.get("role"),
                        "resume_family": payload.get("resume_family"),
                        "route_confidence": payload.get("route_confidence"),
                        "route_reason": payload.get("route_reason"),
                        "resume_variant": payload.get("resume_variant"),
                        "legacy_cluster": payload.get("suggested_cluster")
                        or payload.get("resume_cluster"),
                    }
                )
            )
        return 0
    dest.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out_rows[0].keys()) if out_rows else []
    with dest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"wrote {dest} rows={len(out_rows)}")
    return 0


def _unique_historical() -> list[dict[str, str]]:
    seen: dict[tuple[str, str, str], dict[str, str]] = {}
    for path in sorted((ROOT / "generated").glob("discovery_triage_*.csv")):
        for row in _iter_csv(path):
            key = (row.get("url") or "", row.get("company") or "", row.get("role") or "")
            if key not in seen:
                seen[key] = row
    return list(seen.values())


def cmd_benchmark(args: argparse.Namespace) -> int:
    rows = _unique_historical() if not args.csv else _iter_csv(Path(args.csv))
    started = time.perf_counter()
    routed = []
    for row in rows:
        decision = route(JobMeta.from_mapping(row))
        routed.append((row, decision))
    elapsed_ms = (time.perf_counter() - started) * 1000
    families = Counter(d.family for _, d in routed)
    confidence = Counter(d.confidence for _, d in routed)
    comparable = 0
    agree = 0
    disagreements: dict[str, list[tuple[str, str, str]]] = {}
    for row, decision in routed:
        legacy = (row.get("suggested_cluster") or row.get("resume_cluster") or "").strip()
        expected = LEGACY_TO_FAMILY.get(legacy)
        if not expected or decision.family == "REVIEW":
            continue
        if decision.family == "ai_infra":
            bucket = f"{legacy}->ai_infra"
            disagreements.setdefault(bucket, []).append(
                (row.get("company") or "", row.get("role") or "", decision.reason)
            )
            continue
        comparable += 1
        if decision.family == expected:
            agree += 1
        else:
            bucket = f"{legacy}->{decision.family}"
            disagreements.setdefault(bucket, []).append(
                (row.get("company") or "", row.get("role") or "", decision.reason)
            )
    report = {
        "total_rows": len(rows),
        "routable_rows": families["swe"]
        + families["ml_ai"]
        + families["ai_infra"]
        + families["health_ai"],
        "review_rows": families["REVIEW"],
        "families": dict(families),
        "confidence": dict(confidence),
        "legacy_comparable_rows": comparable,
        "legacy_agreement": agree,
        "legacy_agreement_rate": (agree / comparable) if comparable else None,
        "elapsed_ms": round(elapsed_ms, 3),
        "ms_per_row": round(elapsed_ms / len(rows), 4) if rows else None,
        "disagreement_groups": {k: len(v) for k, v in sorted(disagreements.items())},
        "examples": {
            k: [{"company": c, "role": r, "reason": reason} for c, r, reason in v[:5]]
            for k, v in sorted(disagreements.items())
        },
    }
    dest = Path(args.out) if args.out else ROOT / "generated" / "resume_routing" / "benchmark.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"wrote {dest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    load_policy()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role")
    parser.add_argument("--company", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--board-category", default="")
    parser.add_argument("--track", default="")
    parser.add_argument("--location", default="")
    parser.add_argument("--short-text", default="")
    parser.add_argument("--legacy-cluster", default="")
    parser.add_argument("--json")
    parser.add_argument("--csv")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.benchmark:
        return cmd_benchmark(args)
    if args.csv:
        return cmd_csv(args)
    if args.json or args.role is not None:
        return cmd_one(args)
    parser.error("provide --role, --json, --csv, or --benchmark")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
