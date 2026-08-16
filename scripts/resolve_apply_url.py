#!/usr/bin/env python3
"""Resolve a discovery row to the employer's real application URL.

Why this exists: every row discovery produces points at `jobright.ai/jobs/info/...`,
and Jobright puts its own signup wall in front of "Apply". Those links are fine for
reading a summary and useless for actually applying, so the queue and any autofill
run need the posting on the employer's own ATS.

Approach:
  1. Prefer known boards from knowledge/careers_boards.yaml (verified hosts).
  2. Fall back to guessing Greenhouse/Ashby/Lever/… slugs from the company name.
  3. Match on title-token overlap. Never invent an apply URL.

A match is only reported when the title lines up; otherwise the row comes back
unresolved. A wrong link means applying to the wrong requisition.

Usage:
  python3 scripts/resolve_apply_url.py --date 2026-07-28 --limit 10
  python3 scripts/resolve_apply_url.py --date 2026-07-28 --write-csv
  python3 scripts/resolve_apply_url.py --company Apptronik --role "Software Engineer Intern - ML Systems"
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
BOARDS_YAML = ROOT / "knowledge" / "careers_boards.yaml"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)
TIMEOUT = 15

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "at", "with",
    "usa", "us", "united", "states", "remote", "hybrid", "onsite",
}

# Extra columns written by --write-csv (appended; never remove existing ones).
ENRICH_FIELDS = [
    "apply_url",
    "apply_url_confidence",
    "apply_ats",
    "apply_matched_title",
    "apply_resolve_evidence",
]


@dataclass
class Resolution:
    company: str
    role: str
    source_url: str
    ats: str = ""
    apply_url: str = ""
    matched_title: str = ""
    location: str = ""
    confidence: str = "none"  # exact | strong | weak | none
    evidence: str = ""
    note: str = ""


def http_json(url: str, *, data: dict | None = None) -> object | None:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def load_board_map() -> dict:
    if not BOARDS_YAML.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        # Tiny YAML subset: enough for our careers_boards.yaml shape.
        return _parse_simple_yaml(BOARDS_YAML.read_text(encoding="utf-8"))
    return yaml.safe_load(BOARDS_YAML.read_text(encoding="utf-8")) or {}


def _parse_simple_yaml(text: str) -> dict:
    """Fallback parser when PyYAML is not installed (common in bare VMs)."""
    root: dict = {}
    section: str | None = None
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            root[section] = {}
            current_key = None
            continue
        if section is None:
            continue
        if indent == 2 and ":" in stripped:
            key, val = stripped.split(":", 1)
            key = key.strip().strip('"').strip("'")
            val = val.strip().strip('"').strip("'")
            if val:
                root[section][key] = val
                current_key = None
            else:
                root[section][key] = {}
                current_key = key
            continue
        if indent >= 4 and current_key is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            root[section][current_key][k.strip()] = v.strip().strip('"').strip("'")
    return root


def slugs_for(company: str) -> list[str]:
    base = company.lower().strip()
    base = re.sub(r"[’'`]", "", base)
    base = re.sub(
        r"\b(inc|llc|ltd|corp|corporation|co|company|technologies|technology|labs|group|the)\b",
        " ",
        base,
    )
    base = re.sub(r"[^a-z0-9]+", " ", base).strip()
    if not base:
        return []
    words = base.split()
    candidates = ["".join(words), "-".join(words), words[0]]
    seen: list[str] = []
    for c in candidates:
        if c and c not in seen:
            seen.append(c)
    return seen


def title_tokens(title: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9+#/ ]", " ", (title or "").lower())
    return {w for w in cleaned.split() if w and w not in STOPWORDS}


def score_title(wanted: str, candidate: str) -> float:
    a, b = title_tokens(wanted), title_tokens(candidate)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def rank(wanted: str, postings: list[tuple[str, str, str]]) -> tuple[float, tuple[str, str, str]] | None:
    best: tuple[float, tuple[str, str, str]] | None = None
    for posting in postings:
        s = score_title(wanted, posting[0])
        if best is None or s > best[0]:
            best = (s, posting)
    return best


def confidence_for(score: float) -> str | None:
    if score >= 0.8:
        return "exact"
    if score >= 0.5:
        return "strong"
    if score >= 0.3:
        return "weak"
    return None


# --- board fetchers ---------------------------------------------------------

def from_greenhouse(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    if not isinstance(data, dict):
        return []
    return [
        (j.get("title") or "", j.get("absolute_url") or "", (j.get("location") or {}).get("name", ""))
        for j in data.get("jobs", [])
    ]


def from_lever(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
    if not isinstance(data, list):
        return []
    out = []
    for job in data:
        categories = job.get("categories") or {}
        out.append((job.get("text") or "", job.get("hostedUrl") or "", categories.get("location") or ""))
    return out


def from_ashby(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    if not isinstance(data, dict):
        return []
    return [
        (j.get("title") or "", j.get("jobUrl") or "", j.get("location") or "")
        for j in data.get("jobs", [])
    ]


def from_smartrecruiters(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings")
    if not isinstance(data, dict):
        return []
    out = []
    for job in data.get("content", []):
        loc = job.get("location") or {}
        city = ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x)
        job_id = job.get("id") or ""
        out.append((job.get("name") or "", f"https://jobs.smartrecruiters.com/{slug}/{job_id}", city))
    return out


def from_workable(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true")
    if not isinstance(data, dict):
        return []
    return [
        (j.get("title") or "", j.get("url") or j.get("application_url") or "", j.get("location") or "")
        for j in data.get("jobs", [])
    ]


def from_recruitee(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://{slug}.recruitee.com/api/offers/")
    if not isinstance(data, dict):
        return []
    return [
        (j.get("title") or "", j.get("careers_url") or j.get("careers_apply_url") or "", j.get("location") or "")
        for j in data.get("offers", [])
    ]


def from_workday(host: str, tenant: str, site: str, search_text: str = "") -> list[tuple[str, str, str]]:
    """Workday CXS search. Returns (title, absolute_apply_url, locationsText).

    Workday rejects limit > 20 on some tenants (HTTP 400), so we page with offset.
    """
    endpoint = f"https://{host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    out: list[tuple[str, str, str]] = []
    offset = 0
    page_size = 20
    while offset < 100:  # hard cap — enough for title matching, not a full scrape
        payload = {
            "appliedFacets": {},
            "limit": page_size,
            "offset": offset,
            "searchText": search_text or "",
        }
        data = http_json(endpoint, data=payload)
        if not isinstance(data, dict):
            break
        batch = data.get("jobPostings") or []
        if not batch:
            break
        for job in batch:
            path = job.get("externalPath") or ""
            if not path:
                continue
            title = job.get("title") or ""
            loc = job.get("locationsText") or ""
            apply = f"https://{host}.myworkdayjobs.com/{site}{path}"
            out.append((title, apply, loc))
        total = int(data.get("total") or 0)
        offset += page_size
        if offset >= total:
            break
    return out


SLUG_BOARDS = (
    ("greenhouse", from_greenhouse),
    ("ashby", from_ashby),
    ("lever", from_lever),
    ("smartrecruiters", from_smartrecruiters),
    ("workable", from_workable),
    ("recruitee", from_recruitee),
)

_CONF_RANK = {"none": 0, "weak": 1, "strong": 2, "exact": 3}


def _consider(
    result: Resolution,
    *,
    ats: str,
    score: float,
    title: str,
    url: str,
    location: str,
    evidence: str,
) -> bool:
    """Update result if this candidate is better. Returns True on exact match."""
    conf = confidence_for(score)
    if not conf:
        return False
    if _CONF_RANK[conf] <= _CONF_RANK[result.confidence]:
        return False
    result.ats = ats
    result.apply_url = url
    result.matched_title = title
    result.location = location
    result.confidence = conf
    result.evidence = evidence
    return conf == "exact"


def resolve(company: str, role: str, source_url: str = "", pause: float = 0.2) -> Resolution:
    result = Resolution(company=company, role=role, source_url=source_url)
    tried: list[str] = []
    boards = load_board_map()

    # 1) Known boards from careers_boards.yaml — highest trust, try first.
    gh = (boards.get("greenhouse") or {}).get(company)
    if gh:
        postings = from_greenhouse(gh)
        time.sleep(pause)
        tried.append(f"greenhouse:{gh}({len(postings)})")
        best = rank(role, postings) if postings else None
        if best and _consider(
            result,
            ats="greenhouse",
            score=best[0],
            title=best[1][0],
            url=best[1][1],
            location=best[1][2],
            evidence=f"title overlap {best[0]:.2f} on known greenhouse '{gh}'",
        ):
            result.note = f"tried {', '.join(tried)}"
            return result

    ash = (boards.get("ashby") or {}).get(company)
    if ash:
        postings = from_ashby(ash)
        time.sleep(pause)
        tried.append(f"ashby:{ash}({len(postings)})")
        best = rank(role, postings) if postings else None
        if best and _consider(
            result,
            ats="ashby",
            score=best[0],
            title=best[1][0],
            url=best[1][1],
            location=best[1][2],
            evidence=f"title overlap {best[0]:.2f} on known ashby '{ash}'",
        ):
            result.note = f"tried {', '.join(tried)}"
            return result

    lev = (boards.get("lever") or {}).get(company)
    if lev:
        postings = from_lever(lev)
        time.sleep(pause)
        tried.append(f"lever:{lev}({len(postings)})")
        best = rank(role, postings) if postings else None
        if best and _consider(
            result,
            ats="lever",
            score=best[0],
            title=best[1][0],
            url=best[1][1],
            location=best[1][2],
            evidence=f"title overlap {best[0]:.2f} on known lever '{lev}'",
        ):
            result.note = f"tried {', '.join(tried)}"
            return result

    wd = (boards.get("workday") or {}).get(company)
    if isinstance(wd, dict) and wd.get("host") and wd.get("tenant") and wd.get("site"):
        # Full title first, then a shorter token query — Workday search is picky.
        queries = [role]
        tokens = [t for t in title_tokens(role) if t not in {"2026", "2027"}]
        if len(tokens) >= 2:
            queries.append(" ".join(tokens[:4]))
        if "intern" in tokens:
            queries.append(" ".join([t for t in tokens if t != "intern"][:3] + ["intern"]))
        seen_q: set[str] = set()
        for q in queries:
            qn = q.strip().lower()
            if not qn or qn in seen_q:
                continue
            seen_q.add(qn)
            postings = from_workday(wd["host"], wd["tenant"], wd["site"], search_text=q)
            time.sleep(pause)
            tried.append(f"workday:{wd['host']}/{wd['site']}[q={q[:24]}]({len(postings)})")
            best = rank(role, postings) if postings else None
            if best and _consider(
                result,
                ats="workday",
                score=best[0],
                title=best[1][0],
                url=best[1][1],
                location=best[1][2],
                evidence=f"title overlap {best[0]:.2f} on known workday '{wd['host']}/{wd['site']}' (q={q[:40]!r})",
            ):
                result.note = f"tried {', '.join(tried)}"
                return result

    # 2) Guess slugs from the company name (existing behaviour).
    for slug in slugs_for(company):
        for ats, fetch in SLUG_BOARDS:
            postings = fetch(slug)
            time.sleep(pause)
            tried.append(f"{ats}:{slug}({len(postings)})")
            if not postings:
                continue
            best = rank(role, postings)
            if not best:
                continue
            if _consider(
                result,
                ats=ats,
                score=best[0],
                title=best[1][0],
                url=best[1][1],
                location=best[1][2],
                evidence=f"title overlap {best[0]:.2f} on {ats} board '{slug}' ({len(postings)} postings)",
            ):
                result.note = f"tried {', '.join(tried)}"
                return result

    if result.confidence == "none":
        result.note = "no public board matched; needs manual lookup"
    result.note = (result.note + f" | tried {', '.join(tried) if tried else 'no slugs'}").strip(" |")
    return result


def load_triage(day: str) -> tuple[Path, list[dict]]:
    path = GENERATED / f"discovery_triage_{day}.csv"
    if not path.exists():
        raise SystemExit(f"no triage file for {day}")
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return path, rows


def enrich_rows(rows: list[dict], *, only_keep: bool = True, pause: float = 0.15) -> list[Resolution]:
    results: list[Resolution] = []
    for row in rows:
        if only_keep and (row.get("decision") or "").lower() != "keep":
            for field in ENRICH_FIELDS:
                row.setdefault(field, "")
            continue
        res = resolve(row.get("company", ""), row.get("role", ""), row.get("url", ""), pause=pause)
        results.append(res)
        row["apply_url"] = res.apply_url if res.confidence in {"exact", "strong"} else ""
        row["apply_url_confidence"] = res.confidence
        row["apply_ats"] = res.ats if row["apply_url"] else ""
        row["apply_matched_title"] = res.matched_title if row["apply_url"] else ""
        row["apply_resolve_evidence"] = res.evidence
        # Weak matches stay recorded in confidence/evidence but do NOT become apply_url —
        # a wrong link is worse than none.
    return results


def write_triage(path: Path, rows: list[dict]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    for field in ENRICH_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--company")
    ap.add_argument("--role")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", help="write results as JSON here")
    ap.add_argument(
        "--write-csv",
        action="store_true",
        help="enrich generated/discovery_triage_${DAY}.csv with apply_url columns",
    )
    ap.add_argument("--all-decisions", action="store_true", help="resolve later/skip too (default: keep only)")
    args = ap.parse_args()

    if args.company and args.role:
        res = resolve(args.company, args.role)
        print(
            f"{res.confidence:6} {res.company[:24]:24} {res.role[:44]:44} {res.apply_url[:70]}"
        )
        if args.out:
            Path(args.out).write_text(json.dumps([asdict(res)], indent=2), encoding="utf-8")
        return 0

    if not args.date:
        ap.error("pass --date or --company/--role")

    path, rows = load_triage(args.date)
    targets = [
        r for r in rows
        if args.all_decisions or (r.get("decision") or "").lower() == "keep"
    ]
    if args.limit:
        # Limit applies to the rows we actually resolve.
        keep_idxs = [i for i, r in enumerate(rows) if r in targets]
        allowed = set(keep_idxs[: args.limit])
        for i, r in enumerate(rows):
            if i not in allowed and (r.get("decision") or "").lower() == "keep":
                # Skip resolving but still leave columns present when writing.
                pass
        # Simpler: just truncate the keep list for resolution by rewriting selectively.
        resolve_set = {id(r) for r in targets[: args.limit]}
    else:
        resolve_set = {id(r) for r in targets}

    results: list[Resolution] = []
    for row in rows:
        if id(row) not in resolve_set:
            for field in ENRICH_FIELDS:
                row.setdefault(field, row.get(field, ""))
            continue
        res = resolve(row.get("company", ""), row.get("role", ""), row.get("url", ""))
        results.append(res)
        usable = res.confidence in {"exact", "strong"}
        row["apply_url"] = res.apply_url if usable else ""
        row["apply_url_confidence"] = res.confidence
        row["apply_ats"] = res.ats if usable else ""
        row["apply_matched_title"] = res.matched_title if usable else ""
        row["apply_resolve_evidence"] = res.evidence
        mark = {"exact": "OK  ", "strong": "OK? ", "weak": "??  ", "none": "MISS"}[res.confidence]
        print(
            f"{mark} {res.company[:24]:24} {res.role[:44]:44} {res.confidence:6} {res.apply_url[:70]}"
        )

    if args.write_csv:
        write_triage(path, rows)
        print(f"\nwrote {path}")

    if args.out:
        Path(args.out).write_text(json.dumps([asdict(r) for r in results], indent=2), encoding="utf-8")
        print(f"wrote {args.out}")

    resolved = sum(1 for r in results if r.confidence in {"exact", "strong"})
    print(f"\nresolved {resolved}/{len(results)} to an employer ATS URL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
