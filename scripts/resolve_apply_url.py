#!/usr/bin/env python3
"""Resolve a discovery row to the employer's real application URL.

Why this exists: every row discovery produces points at `jobright.ai/jobs/info/...`,
and Jobright puts its own signup wall in front of "Apply". Those links are fine for
reading a summary and useless for actually applying, so the queue and any autofill
run need the posting on the employer's own ATS.

Approach: ask the public job-board APIs the employer already publishes
(Greenhouse, Lever, Ashby), then match on title. No account, no scraping behind a
login, no guessing.

A match is only reported when the title lines up; otherwise the row comes back
unresolved with the reason. Never fabricate an apply URL — a wrong link means
applying to the wrong req.

Usage:
  python3 scripts/resolve_apply_url.py --date 2026-07-28 --limit 10
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

USER_AGENT = "Mozilla/5.0 (compatible; job-search-repo/1.0; personal use)"
TIMEOUT = 15

# Words that carry no signal when comparing two job titles.
STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "for", "to", "in", "at", "with",
    "usa", "us", "united", "states", "remote", "hybrid", "onsite",
}


@dataclass
class Resolution:
    company: str
    role: str
    source_url: str
    ats: str = ""
    apply_url: str = ""
    matched_title: str = ""
    location: str = ""
    confidence: str = "none"      # exact | strong | weak | none
    evidence: str = ""
    note: str = ""


def http_json(url: str) -> object | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def slugs_for(company: str) -> list[str]:
    """Board slugs an employer plausibly uses, most likely first."""
    base = company.lower().strip()
    base = re.sub(r"[’'`]", "", base)
    base = re.sub(r"\b(inc|llc|ltd|corp|corporation|co|company|technologies|technology|labs|group|the)\b", " ", base)
    base = re.sub(r"[^a-z0-9]+", " ", base).strip()
    if not base:
        return []
    words = base.split()
    candidates = [
        "".join(words),
        "-".join(words),
        words[0],
    ]
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
    """postings: (title, url, location). Returns the best (score, posting)."""
    best: tuple[float, tuple[str, str, str]] | None = None
    for posting in postings:
        s = score_title(wanted, posting[0])
        if best is None or s > best[0]:
            best = (s, posting)
    return best


def from_greenhouse(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    if not isinstance(data, dict):
        return []
    out = []
    for job in data.get("jobs", []):
        out.append((job.get("title") or "", job.get("absolute_url") or "", (job.get("location") or {}).get("name", "")))
    return out


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
    out = []
    for job in data.get("jobs", []):
        out.append((job.get("title") or "", job.get("jobUrl") or "", job.get("location") or ""))
    return out


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
    out = []
    for job in data.get("jobs", []):
        out.append((job.get("title") or "", job.get("url") or job.get("application_url") or "", job.get("location") or ""))
    return out


def from_recruitee(slug: str) -> list[tuple[str, str, str]]:
    data = http_json(f"https://{slug}.recruitee.com/api/offers/")
    if not isinstance(data, dict):
        return []
    out = []
    for job in data.get("offers", []):
        out.append((job.get("title") or "", job.get("careers_url") or job.get("careers_apply_url") or "", job.get("location") or ""))
    return out


BOARDS = (
    ("greenhouse", from_greenhouse),
    ("ashby", from_ashby),
    ("lever", from_lever),
    ("smartrecruiters", from_smartrecruiters),
    ("workable", from_workable),
    ("recruitee", from_recruitee),
)


def resolve(company: str, role: str, source_url: str = "", pause: float = 0.3) -> Resolution:
    result = Resolution(company=company, role=role, source_url=source_url)
    tried: list[str] = []

    for slug in slugs_for(company):
        for ats, fetch in BOARDS:
            postings = fetch(slug)
            time.sleep(pause)
            tried.append(f"{ats}:{slug}({len(postings)})")
            if not postings:
                continue
            best = rank(role, postings)
            if not best:
                continue
            score, (title, url, location) = best
            if score >= 0.8:
                confidence = "exact"
            elif score >= 0.5:
                confidence = "strong"
            elif score >= 0.3:
                confidence = "weak"
            else:
                continue

            # Keep the strongest match seen across boards.
            better = {"none": 0, "weak": 1, "strong": 2, "exact": 3}
            if better[confidence] <= better[result.confidence]:
                continue
            result.ats = ats
            result.apply_url = url
            result.matched_title = title
            result.location = location
            result.confidence = confidence
            result.evidence = f"title overlap {score:.2f} on {ats} board '{slug}' ({len(postings)} postings)"
            if confidence == "exact":
                result.note = f"tried {', '.join(tried)}"
                return result

    if result.confidence == "none":
        result.note = "no public board matched; needs manual lookup"
    result.note = (result.note + f" | tried {', '.join(tried) if tried else 'no slugs'}").strip(" |")
    return result


def load_keeps(day: str) -> list[dict]:
    path = GENERATED / f"discovery_triage_{day}.csv"
    if not path.exists():
        raise SystemExit(f"no triage file for {day}")
    with path.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("decision") or "").lower() == "keep"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--company")
    ap.add_argument("--role")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", help="write results as JSON here")
    args = ap.parse_args()

    rows: list[dict]
    if args.company and args.role:
        rows = [{"company": args.company, "role": args.role, "url": ""}]
    elif args.date:
        rows = load_keeps(args.date)
        if args.limit:
            rows = rows[: args.limit]
    else:
        ap.error("pass --date or --company/--role")

    results = []
    for row in rows:
        res = resolve(row.get("company", ""), row.get("role", ""), row.get("url", ""))
        results.append(res)
        mark = {"exact": "OK  ", "strong": "OK? ", "weak": "??  ", "none": "MISS"}[res.confidence]
        print(f"{mark} {res.company[:24]:24} {res.role[:44]:44} {res.confidence:6} {res.apply_url[:70]}")

    if args.out:
        Path(args.out).write_text(json.dumps([asdict(r) for r in results], indent=2), encoding="utf-8")
        print(f"\nwrote {args.out}")

    resolved = sum(1 for r in results if r.confidence in {"exact", "strong"})
    print(f"\nresolved {resolved}/{len(results)} to an employer ATS URL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
