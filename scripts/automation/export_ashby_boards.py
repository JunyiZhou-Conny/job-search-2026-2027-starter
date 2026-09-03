#!/usr/bin/env python3
"""Sweep known Ashby job boards and emit fresh, already-resolved candidate rows.

Ashby publishes every board through an unauthenticated list endpoint, and each
posting's application form through the GraphQL probe in scripts/ashby_form.py.
Reading both gives the apply stage what Jobright cannot: the true publishedAt
(Jobright's "posted N hours ago" is repost time) and the form facts the G2 gate
in docs/policy/SUBMIT_ROLLOUT.md needs, before any browser opens.

    python3 scripts/automation/export_ashby_boards.py --days 7
    python3 scripts/automation/export_ashby_boards.py --days 3 --only kayak notion

Writes generated/ashby_sweep_{RUN}.csv and a digest .md next to it, RUN being
the UTC hour stamp YYYY-MM-DDTHH. Discovery only: nothing under data/ changes.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import ashby_form  # noqa: E402

ORGS_PATH = ROOT / "knowledge" / "ashby_orgs.yaml"
ROLES_PATH = ROOT / "knowledge" / "target_roles.yaml"
BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
TIMEOUT = 20
PAUSE = 0.5

COLUMNS = (
    "company", "slug", "title", "location", "employmentType", "publishedAt", "jobUrl", "applyUrl",
    "required_count", "required_essays", "broad_sponsorship_question", "export_control_question",
    "external_artifact", "g2_blockers", "g2_candidate", "notes",
)

# Title filter: DOMAIN must match, EXCLUDE must not, and a DROP hit stands
# unless STRONG overrides it ("Silicon Validation Engineer, Software" stays,
# "Hardware Engineer, Test" goes). Same shape as export_board_lists.py.
DOMAIN_WORDS = [
    r"software", r"engineer", r"developer", r"\bswe\b", r"\bdata\b", r"machine\s*learning", r"\bml\b",
    r"\bai\b", r"\bllm\b", r"\bnlp\b", r"computer\s*vision", r"deep\s*learning", r"platform",
    r"infrastructure", r"\binfra\b", r"cloud", r"back[\s-]?end", r"full[\s-]?stack", r"devops", r"\bsre\b",
    r"site\s*reliability", r"research\s*scientist", r"applied\s*scientist", r"member\s*of\s*technical\s*staff",
]
# Perplexity titles every engineer "Member of Technical Staff", so that one
# Staff is a title, not a level.
EXCLUDE = re.compile(
    r"(\bsenior\b|\bsr\.?\b|(?<!technical\s)\bstaff\b|\bprincipal\b|\blead\b|\bmanager\b|\bdirector\b|"
    r"\bhead\b|\bchief\b|\bvp\b|vice\s*president|\bc[tef]o\b|\btpm\b|\barchitect\b|\bdistinguished\b|"
    r"\bphd\b|\bpostdoc|\b2026\b)",
    re.I,
)
DROP = re.compile(
    r"(sales|marketing|account|recruit|\bhr\b|\bpeople\b|finance|revenue|legal|counsel|hardware|mechanical|"
    r"electrical|manufactur|\brf\b|fpga|\bdsp\b|\bpcb\b|antenna|silicon|packag|layout|supply\s*chain|inventory|"
    r"purchasing|technician|designer|copywriter|\bwriter\b|producer|support|customer|success|\bgtm\b|growth|"
    r"operations|strateg|policy|events|community|talent)",
    re.I,
)
STRONG = re.compile(
    r"(software|developer|machine\s*learning|\bml\b|\bai\b|\bswe\b|\bdata\b|research\s*engineer|back[\s-]?end|"
    r"full[\s-]?stack|platform|infrastructure|cloud)",
    re.I,
)
REMOTE_LOCATION = re.compile(r"^\s*remote\s*$|\(remote\)|[-,/]\s*remote\s*$|^\s*remote\s*[-,/:]", re.I)
G2_EMPLOYMENT = {"FullTime", "Intern"}


def run_stamp(now: datetime) -> str:
    return now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H")


def load_orgs(path: Path = ORGS_PATH) -> List[Dict[str, str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    orgs = data.get("orgs") or {}
    return [{"slug": slug, "company": (meta or {}).get("company") or slug, "kind": (meta or {}).get("kind") or "employer"}
            for slug, meta in sorted(orgs.items())]


def load_role_titles(path: Path = ROLES_PATH) -> List[str]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    titles: List[str] = []
    for cluster in (data.get("role_clusters") or {}).values():
        titles.extend((cluster or {}).get("titles") or [])
    return titles


def compile_domain(titles: Iterable[str]) -> "re.Pattern[str]":
    phrases = set()
    for title in titles:
        for part in title.split("/"):
            words = part.split()
            if words:
                phrases.add(r"\b" + r"\s*".join(re.escape(w) for w in words) + r"\b")
    return re.compile("|".join(sorted(phrases) + DOMAIN_WORDS), re.I)


def title_ok(title: str, domain: "re.Pattern[str]") -> bool:
    if not domain.search(title) or EXCLUDE.search(title):
        return False
    return not (DROP.search(title) and not STRONG.search(title))


def published_at(job: Dict) -> Optional[datetime]:
    try:
        dt = datetime.fromisoformat(job.get("publishedAt") or "")
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def published_within(job: Dict, now: datetime, days: int) -> bool:
    dt = published_at(job)
    return dt is not None and now - dt <= timedelta(days=days)


def remote_only(job: Dict) -> bool:
    """Ashby sets isRemote for Hybrid too, so workplaceType decides when present."""
    workplace = job.get("workplaceType")
    if workplace:
        return workplace == "Remote"
    if job.get("isRemote") is True:
        return True
    return bool(REMOTE_LOCATION.search(job.get("location") or ""))


def select_jobs(jobs: Iterable[Dict], domain: "re.Pattern[str]", now: datetime, days: int) -> List[Dict]:
    return [j for j in jobs
            if published_within(j, now, days) and not remote_only(j) and title_ok(j.get("title") or "", domain)]


def g2_candidate(org: Dict[str, str], job: Dict, form: Dict) -> bool:
    """An agency board (a recruiter posting on behalf of clients) is not the
    employer's own application, so it is triage material, never a G2 row."""
    return org.get("kind", "employer") == "employer" and bool(form.get("open")) and not form.get("g2_blockers") \
        and job.get("employmentType") in G2_EMPLOYMENT and not remote_only(job)


def row_for(org: Dict[str, str], job: Dict, form: Dict) -> Dict:
    notes = []
    if org.get("kind", "employer") != "employer":
        notes.append(f"kind={org['kind']}")
    if form.get("error"):
        notes.append(f"form: {form['error']}")
    elif not form.get("open"):
        notes.append("form: closed")
    for key in ("workplaceType", "department"):
        if job.get(key):
            notes.append(f"{key}={job[key]}")
    summary = form.get("summary") if form.get("open") else None
    facts = {
        "required_count": summary["required_count"] if summary else "",
        "required_essays": ";".join(summary["required_essays"]) if summary else "",
        "broad_sponsorship_question": summary["broad_sponsorship_question"] if summary else "",
        "export_control_question": summary["export_control_question"] if summary else "",
        "external_artifact": bool(summary["external_artifact"]) if summary else "",
        "g2_blockers": ";".join(form.get("g2_blockers") or []),
    }
    return {
        "company": org["company"], "slug": org["slug"], "title": (job.get("title") or "").strip(),
        "location": job.get("location") or "", "employmentType": job.get("employmentType") or "",
        "publishedAt": job.get("publishedAt") or "", "jobUrl": job.get("jobUrl") or "", "applyUrl": job.get("applyUrl") or "",
        **facts, "g2_candidate": g2_candidate(org, job, form), "notes": ";".join(notes),
    }


def error_row(org: Dict[str, str], note: str) -> Dict:
    row = {c: "" for c in COLUMNS}
    row.update({"company": org["company"], "slug": org["slug"], "g2_candidate": False, "notes": note})
    return row


def fetch_board(slug: str, timeout: int = TIMEOUT) -> List[Dict]:
    req = urllib.request.Request(BOARD_URL.format(slug=slug), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)["jobs"]


def sweep(orgs: List[Dict[str, str]], domain: "re.Pattern[str]", now: datetime, days: int,
          fetch_board: Callable[[str], List[Dict]] = fetch_board,
          fetch_form: Callable[[str], Dict] = ashby_form.fetch,
          pause: float = PAUSE) -> Tuple[List[Dict], Dict[str, int]]:
    rows: List[Dict] = []
    stats = {"orgs": len(orgs), "orgs_failed": 0, "jobs_seen": 0, "kept": 0, "g2_candidates": 0}
    for org in orgs:
        try:
            jobs = fetch_board(org["slug"])
        except Exception as exc:
            stats["orgs_failed"] += 1
            rows.append(error_row(org, f"board: {type(exc).__name__}: {exc}"[:200]))
            time.sleep(pause)
            continue
        stats["jobs_seen"] += len(jobs)
        selected = select_jobs(jobs, domain, now, days)
        print(f"{org['slug']:<16} jobs={len(jobs):>4} kept={len(selected)}", file=sys.stderr)
        for job in selected:
            time.sleep(pause)
            try:
                form = fetch_form(job["jobUrl"])
            except Exception as exc:
                form = {"error": f"{type(exc).__name__}: {exc}"[:200]}
            rows.append(row_for(org, job, form))
            stats["kept"] += 1
        time.sleep(pause)
    stats["g2_candidates"] = sum(1 for r in rows if r["g2_candidate"])
    return rows, stats


def write_csv(rows: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)


def _cell(value) -> str:
    return str(value).replace("|", "/").replace("\n", " ")


def _table(header: List[str], lines: List[List[str]]) -> List[str]:
    return (["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
            + ["| " + " | ".join(_cell(v) for v in line) + " |" for line in lines])


def digest(rows: List[Dict], stats: Dict[str, int], run: str, days: int) -> str:
    newest_first = sorted(rows, key=lambda r: r["publishedAt"], reverse=True)
    candidates = [r for r in newest_first if r["g2_candidate"]]
    others = [r for r in newest_first if r["title"] and not r["g2_candidate"]]
    errors = [r for r in rows if not r["title"]]
    out = [f"# Ashby board sweep {run}", "",
           f"Window {days} days. Orgs swept {stats['orgs']}, failed {stats['orgs_failed']}. "
           f"Jobs seen {stats['jobs_seen']}, kept {stats['kept']}, G2 candidates {stats['g2_candidates']}.", "",
           "G2 candidate means the posting is open, the form has no G2 blocker, the type is FullTime or Intern, "
           "and the posting is not remote-only. Location, cycle year, and fit are still triage calls.", "",
           "## G2 candidates", ""]
    out += _table(["Company", "Title", "Location", "Type", "Published", "Apply"],
                  [[r["company"], r["title"], r["location"], r["employmentType"], r["publishedAt"][:10], r["applyUrl"]] for r in candidates]) if candidates else ["none"]
    out += ["", "## Kept, blocked or closed", ""]
    out += _table(["Company", "Title", "Location", "Published", "Blockers or note"],
                  [[r["company"], r["title"], r["location"], r["publishedAt"][:10], r["g2_blockers"] or r["notes"]] for r in others]) if others else ["none"]
    out += ["", "## Board errors", ""]
    out += [f"- {r['slug']}: {r['notes']}" for r in errors] or ["none"]
    return "\n".join(out) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--days", type=int, default=7, help="keep postings published within this many days")
    p.add_argument("--out", default="generated/ashby_sweep_{RUN}.csv", help="CSV path; {RUN} expands to the UTC hour stamp")
    p.add_argument("--only", nargs="+", metavar="SLUG", help="sweep only these board slugs")
    p.add_argument("--orgs", type=Path, default=ORGS_PATH)
    args = p.parse_args(argv)

    now = datetime.now(timezone.utc)
    run = run_stamp(now)
    orgs = load_orgs(args.orgs)
    if args.only:
        orgs = [o for o in orgs if o["slug"] in set(args.only)]
    if not orgs:
        print("no orgs selected", file=sys.stderr)
        return 2
    domain = compile_domain(load_role_titles())
    rows, stats = sweep(orgs, domain, now, args.days)

    out = Path(args.out.replace("{RUN}", run))
    if not out.is_absolute():
        out = ROOT / out
    write_csv(rows, out)
    md = out.with_suffix(".md")
    md.write_text(digest(rows, stats, run, args.days), encoding="utf-8")
    print(" ".join(f"{k}={v}" for k, v in stats.items()))
    print(f"csv={out}")
    print(f"digest={md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
