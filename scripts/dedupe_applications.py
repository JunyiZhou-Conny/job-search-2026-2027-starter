#!/usr/bin/env python3
"""Find duplicate applications; never auto-delete — write review queue proposals."""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from js_lib import (  # noqa: E402
    APPLICATIONS, REVIEW_QUEUE, company_role_key, log, normalize_text,
    normalize_url, read_rows, sync_app_aliases, write_rows,
)

OUT = ROOT / "generated" / "review_queue_dedupe.csv"
FIELDS = ["match_type", "keep_id", "dup_id", "company", "role", "url", "action", "confidence", "notes"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply-mark", action="store_true",
                   help="Append notes on duplicate rows; does not delete")
    args = p.parse_args()

    rows = [sync_app_aliases(r) for r in read_rows(APPLICATIONS)]
    by_url: Dict[str, List[dict]] = defaultdict(list)
    by_cr: Dict[str, List[dict]] = defaultdict(list)
    by_crl: Dict[str, List[dict]] = defaultdict(list)

    for r in rows:
        jid = r.get("job_id") or r.get("id")
        url = normalize_url(r.get("job_url") or r.get("posting_url") or "")
        if url:
            by_url[url].append(r)
        cr = company_role_key(r.get("company", ""), r.get("role", ""))
        if cr != "|":
            by_cr[cr].append(r)
        loc = normalize_text(r.get("location", ""))
        by_crl[f"{cr}|{loc}"].append(r)

    proposals = []

    def add_group(match_type: str, group: List[dict], conf: str) -> None:
        if len(group) < 2:
            return
        # prefer earliest id / applied as keep
        group_sorted = sorted(group, key=lambda x: x.get("job_id") or x.get("id") or "")
        keep = group_sorted[0]
        kid = keep.get("job_id") or keep.get("id")
        for dup in group_sorted[1:]:
            did = dup.get("job_id") or dup.get("id")
            proposals.append({
                "match_type": match_type,
                "keep_id": kid,
                "dup_id": did,
                "company": keep.get("company", ""),
                "role": keep.get("role", ""),
                "url": keep.get("job_url") or keep.get("posting_url") or "",
                "action": "review_merge",
                "confidence": conf,
                "notes": "Manual merge required; auto-delete disabled",
            })

    for g in by_url.values():
        add_group("normalized_url", g, "0.95")
    for g in by_cr.values():
        # only if not already caught by url
        urls = {normalize_url(x.get("job_url") or x.get("posting_url") or "") for x in g}
        if len(urls) == 1 and list(urls)[0]:
            continue
        add_group("company_role_exact", g, "0.80")
    for g in by_crl.values():
        if len(g) < 2:
            continue
        add_group("company_role_location", g, "0.70")

    # dedupe proposal rows
    seen = set()
    unique = []
    for p_ in proposals:
        key = (p_["keep_id"], p_["dup_id"], p_["match_type"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(p_)

    write_rows(OUT, FIELDS, unique)
    log(f"dedupe proposals={len(unique)} → {OUT}")

    if args.apply_mark and unique:
        by_id = { (r.get("job_id") or r.get("id")): r for r in rows }
        for p_ in unique:
            d = by_id.get(p_["dup_id"])
            if not d:
                continue
            note = d.get("notes") or ""
            marker = f"[dedupe_candidate keep={p_['keep_id']} via {p_['match_type']}]"
            if marker not in note:
                d["notes"] = f"{note}; {marker}".strip("; ")
        from js_lib import APP_FIELDS, write_rows as wr
        wr(APPLICATIONS, APP_FIELDS, [sync_app_aliases(r) for r in rows])
        log("marked duplicate candidates in notes (no deletes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
