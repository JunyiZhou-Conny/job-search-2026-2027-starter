#!/usr/bin/env python3
"""Read an Ashby application form before any browser opens.

Ashby exposes the public job posting and its application form through an
unauthenticated GraphQL endpoint. Reading it tells us, per posting: is it
still open, which fields are required, whether a free-response essay is
required, and whether a sponsorship or export-control question exists.
These are the facts the G2 gate in docs/policy/SUBMIT_ROLLOUT.md needs.

    python3 scripts/ashby_form.py https://jobs.ashbyhq.com/<org>/<posting-id>
    python3 scripts/ashby_form.py --json <url> [<url> ...]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from typing import Dict, List, Optional

ENDPOINT = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobPosting"
QUERY = (
    "query ApiJobPosting($organizationHostedJobsPageName: String!, $jobPostingId: String!) {"
    " jobPosting(organizationHostedJobsPageName: $organizationHostedJobsPageName, jobPostingId: $jobPostingId) {"
    " id title locationName workplaceType employmentType publishedDate"
    " applicationForm { sections { title fieldEntries { isRequired field } } } } }"
)

SPONSORSHIP = re.compile(r"sponsor", re.I)
H1B_NAMED = re.compile(r"h-?1b", re.I)
# Broad "now or in the future" widgets often list H-1B as an example.
# Those stay broad; only a question that is specifically about H-1B is named-only.
BROAD_SPONSORSHIP = re.compile(r"now or in the future|in the future", re.I)
H1B_AS_EXAMPLE = re.compile(r"e\.?g\.?|for example|including|such as", re.I)
EXPORT = re.compile(r"ITAR|export control|U\.?S\.? person", re.I)
EEO = re.compile(r"gender|race|ethnic|veteran|disabilit", re.I)


def _h1b_named_only(title: str) -> bool:
    """True when the question is specifically about H-1B, not a broad visa ask."""
    if not H1B_NAMED.search(title):
        return False
    if BROAD_SPONSORSHIP.search(title) or H1B_AS_EXAMPLE.search(title):
        return False
    return True


def parse_url(url: str) -> Optional[Dict[str, str]]:
    m = re.match(r"https?://jobs\.ashbyhq\.com/([^/]+)/([0-9a-f-]{36})", url.strip())
    return {"org": m.group(1), "id": m.group(2)} if m else None


def fetch(url: str, timeout: int = 20) -> Dict:
    ref = parse_url(url)
    if not ref:
        return {"url": url, "error": "not an Ashby posting URL"}
    body = json.dumps({"operationName": "ApiJobPosting", "query": QUERY,
                       "variables": {"organizationHostedJobsPageName": ref["org"], "jobPostingId": ref["id"]}}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=timeout))
    except Exception as exc:  # network, HTTP, or JSON failure is a blocked probe, not a crash
        return {"url": url, "org": ref["org"], "error": f"{type(exc).__name__}: {exc}"[:200]}
    if data.get("errors"):
        return {"url": url, "org": ref["org"], "error": f"graphql: {data['errors'][0].get('message', '')}"[:200]}
    posting = (data.get("data") or {}).get("jobPosting")
    if posting is None:
        return {"url": url, "org": ref["org"], "open": False}
    fields: List[Dict] = []
    for section in posting["applicationForm"]["sections"]:
        for entry in section["fieldEntries"]:
            f = entry["field"]
            fields.append({
                "title": f.get("title", ""),
                "type": f.get("type", ""),
                "required": bool(entry["isRequired"]),
                "options": [v.get("label") for v in (f.get("selectableValues") or [])],
            })
    return summarize({
        "url": url, "org": ref["org"], "open": True, "title": posting["title"],
        "location": posting.get("locationName"), "workplace": posting.get("workplaceType"),
        "employment": posting.get("employmentType"), "published": posting.get("publishedDate"),
        "fields": fields,
    })


def summarize(form: Dict) -> Dict:
    req = [f for f in form["fields"] if f["required"]]
    essays = [f["title"] for f in req if f["type"] == "LongText"]
    sponsorship = [f["title"] for f in form["fields"] if SPONSORSHIP.search(f["title"])]
    broad = [t for t in sponsorship if not _h1b_named_only(t)]
    form["summary"] = {
        "required_count": len(req),
        "required_essays": essays,
        "sponsorship_questions": sponsorship,
        "broad_sponsorship_question": bool(broad),
        "export_control_question": any(EXPORT.search(f["title"]) for f in form["fields"]),
        "eeo_fields": [f["title"] for f in form["fields"] if EEO.search(f["title"])],
        "external_artifact": [f["title"] for f in req if f["type"] == "Url" and not re.search(r"linkedin", f["title"], re.I)],
    }
    s = form["summary"]
    blockers = []
    if s["required_essays"]:
        blockers.append("required_essay")
    if s["broad_sponsorship_question"]:
        blockers.append("broad_sponsorship_question")
    if s["export_control_question"]:
        blockers.append("export_control_question")
    if s["external_artifact"]:
        blockers.append("external_artifact")
    form["g2_blockers"] = blockers
    return form


def render(form: Dict) -> str:
    if form.get("error"):
        return f"{form['url']}: PROBE ERROR {form['error']}"
    if not form["open"]:
        return f"{form['url']}: CLOSED (posting not found)"
    lines = [f"== {form['org']} | {form['title']} | {form['location']} | {form['workplace']} | {form['employment']} | published {form['published']}"]
    for f in form["fields"]:
        opts = f" {f['options'][:6]}" if f["options"] else ""
        lines.append(f"   [{'REQ' if f['required'] else 'opt'}] {f['type']:<16} {f['title'][:110]}{opts}")
    lines.append(f"   G2 blockers: {form['g2_blockers'] or 'none'}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("urls", nargs="+")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    forms = [fetch(u) for u in args.urls]
    if args.json:
        print(json.dumps(forms, indent=1))
    else:
        for form in forms:
            print(render(form))
    return 0


if __name__ == "__main__":
    sys.exit(main())
