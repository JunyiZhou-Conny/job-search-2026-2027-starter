#!/usr/bin/env python3
"""Build a calm one-page apply queue for Simplify sessions.

Dimensions (orthogonal):
  - queue_tier A/B/C/D = freshness / backlog / verify-first / older saved
  - geo           = boston_ma | bay_area | other
  - company_class = big_tech | biotech | startup | other

Inputs:
  - generated/discovery_triage_YYYY-MM-DD.csv (decision=keep)
  - data/applications.csv (status discovered/saved)
  - knowledge/company_lists.yaml (optional allowlists)

Output:
  - generated/apply_queue/YYYY-MM-DD.html
  - generated/apply_queue/YYYY-MM-DD.md
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from js_lib import canonical_url  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "data" / "applications.csv"
OUT_DIR = ROOT / "generated" / "apply_queue"
TEMPLATE_DIR = ROOT / "templates" / "apply_queue"
STATIC_DIR = ROOT / "static" / "apply_queue"

DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LISTS = ROOT / "knowledge" / "company_lists.yaml"
GTC_SPONSORS = ROOT / "knowledge" / "market_signals" / "gtc2026_sponsors_exhibitors.json"
JOB_DECISIONS = ROOT / "data" / "job_decisions.csv"

VERIFY_PATTERNS = re.compile(
    r"(performance modeling|gpu software engineer|embedded systems engineer|"
    r"data engineer(?! intern)|all levels|new graduate engineer)",
    re.I,
)

BOSTON_MA_PATTERNS = re.compile(
    r"\b("
    r"boston|cambridge|somerville|brookline|medford|malden|quincy|newton|"
    r"waltham|burlington|woburn|lexington|arlington|watertown|needham|"
    r"boxborough|framingham|natick|bedford|chelmsford|lowell|worcester|"
    r"massachusetts|\bma\b|greater boston|metro.?west"
    r")\b",
    re.I,
)

# SF Bay Area / Silicon Valley — NOT Los Angeles / San Diego.
BAY_AREA_PATTERNS = re.compile(
    r"\b("
    r"san francisco|\bsf\b|bay area|silicon valley|"
    r"san jose|santa clara|sunnyvale|cupertino|mountain view|palo alto|"
    r"menlo park|redwood city|foster city|san mateo|burlingame|millbrae|"
    r"south san francisco|\bssf\b|san bruno|daly city|"
    r"oakland|berkeley(?!\s+heights)|emeryville|fremont|union city|hayward|"
    r"milpitas|campbell|los gatos|saratoga|"
    r"walnut creek|concord|pleasanton|dublin|livermore"
    r")\b",
    re.I,
)


def load_yaml_lists() -> dict[str, list[str]]:
    empty = {"big_tech": [], "biotech": [], "startup_or_scaleup": []}
    if not LISTS.exists():
        return empty
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(LISTS.read_text(encoding="utf-8")) or {}
    except Exception:
        # Minimal fallback parser for plain "- Name" lists
        data = {"big_tech": [], "biotech": [], "startup_or_scaleup": []}
        section = None
        for line in LISTS.read_text(encoding="utf-8").splitlines():
            if line.startswith("big_tech:"):
                section = "big_tech"
            elif line.startswith("biotech:"):
                section = "biotech"
            elif line.startswith("startup_or_scaleup:"):
                section = "startup_or_scaleup"
            elif line.startswith("other_examples:"):
                section = None
            elif section and line.strip().startswith("- "):
                name = line.strip()[2:].split("#")[0].strip()
                data.setdefault(section, []).append(name)
    return {
        "big_tech": list(data.get("big_tech") or []),
        "biotech": list(data.get("biotech") or []),
        "startup_or_scaleup": list(data.get("startup_or_scaleup") or []),
    }


def company_match(company: str, names: list[str]) -> bool:
    """Match company names without short-token false positives (e.g. X ⊂ Exowatt)."""
    c = company.strip().lower()
    if not c:
        return False
    for name in names:
        n = name.strip().lower()
        if not n:
            continue
        # Tiny tokens (X, AI): exact company name only
        if len(n) <= 2:
            if c == n:
                return True
            continue
        if c == n or c.startswith(n + " ") or c.startswith(n + ",") or c.endswith(" " + n):
            return True
        # Allow "TikTok" in "TikTok / ByteDance ..." via word boundary
        if re.search(rf"(?:^|[\s,/|&-]){re.escape(n)}(?:$|[\s,/|&-])", c):
            return True
    return False


def load_gtc_sponsors() -> list[str]:
    if not GTC_SPONSORS.exists():
        return []
    try:
        import json

        data = json.loads(GTC_SPONSORS.read_text(encoding="utf-8"))
        return [str(x).strip() for x in (data.get("companies") or []) if str(x).strip()]
    except Exception:
        return []


def _norm_company_token(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[\u2019']", "", s)
    s = re.sub(r"\b(inc\.?|ltd\.?|llc\.?|corp\.?|co\.?|gmbh|se|plc)\b", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# Manual aliases: job-board name -> tokens that should hit a GTC sponsor name
GTC_ALIASES = {
    "amazon": ["amazon web services", "aws"],
    "google": ["google cloud", "google"],
    "gemini": ["google cloud", "google"],
    "microsoft": ["microsoft azure", "microsoft"],
    "meta": ["meta"],
    "ibm": ["ibm"],
    "oracle": ["oracle"],
    "cisco": ["cisco"],
    "cadence": ["cadence"],
    "databricks": ["databricks"],
    "cloudflare": ["cloudflare"],
    "together ai": ["together ai", "together"],
    "together": ["together ai", "together"],
    "mistral ai": ["mistral ai", "mistral"],
    "fireworks ai": ["fireworks ai", "fireworks"],
    "lambda": ["lambda"],
    "coreweave": ["coreweave"],
    "dell": ["dell technologies", "dell"],
    "hpe": ["hpe", "hewlett packard"],
    "samsung": ["samsung semiconductor", "samsung"],
    "sk hynix": ["sk hynix"],
    "supermicro": ["supermicro"],
    "lenovo": ["lenovo"],
    "nvidia": ["nvidia"],
}


def match_gtc_sponsor(company: str, sponsors: list[str]) -> str:
    """Return matched GTC sponsor display name, or empty string."""
    if not company or not sponsors:
        return ""
    c_norm = _norm_company_token(company)
    if not c_norm:
        return ""

    sponsor_norms = [(_norm_company_token(s), s) for s in sponsors]

    def token_equal_or_prefix(a: str, b: str) -> bool:
        return a == b or a.startswith(b + " ") or b.startswith(a + " ")

    def whole_token(hay: str, needle: str) -> bool:
        # Avoid Capgemini containing gemini as a false positive
        return bool(re.search(rf"(?:^| ){re.escape(needle)}(?: |$)", hay))

    # 1) alias table first (Gemini → Google Cloud, not Capgemini)
    for key, targets in GTC_ALIASES.items():
        if c_norm == key or c_norm.startswith(key + " ") or whole_token(c_norm, key):
            for t in targets:
                tn = _norm_company_token(t)
                for sn, original in sponsor_norms:
                    if token_equal_or_prefix(sn, tn) or whole_token(sn, tn) or whole_token(tn, sn):
                        return original

    # 2) direct / safe containment
    for sn, original in sponsor_norms:
        if not sn or len(sn) < 3:
            continue
        if token_equal_or_prefix(c_norm, sn):
            return original
        if len(c_norm) >= 4 and (whole_token(sn, c_norm) or whole_token(c_norm, sn)):
            return original
    return ""


BIOTECH_NAME_HINT = re.compile(
    r"\b("
    r"bio|biotech|therapeutics?|pharma|genomic|genome|life\s*sciences?|"
    r"medtech|medical|health(?!care\s*proof)|clinical|oncology|therapeutics"
    r")\b",
    re.I,
)


def classify_company(company: str, lists: dict[str, list[str]]) -> str:
    # Precedence: big_tech → biotech → startup → other
    if company_match(company, lists["big_tech"]):
        return "big_tech"
    if company_match(company, lists.get("biotech") or []):
        return "biotech"
    if BIOTECH_NAME_HINT.search(company or ""):
        return "biotech"
    if company_match(company, lists["startup_or_scaleup"]):
        return "startup"
    return "other"


def classify_geo(location: str) -> str:
    loc = location or ""
    if BOSTON_MA_PATTERNS.search(loc):
        return "boston_ma"
    if BAY_AREA_PATTERNS.search(loc):
        return "bay_area"
    return "other"


def latest_triage(day: str | None) -> Path | None:
    gen = ROOT / "generated"
    if day:
        p = gen / f"discovery_triage_{day}.csv"
        return p if p.exists() else None
    files = sorted(gen.glob("discovery_triage_*.csv"), reverse=True)
    return files[0] if files else None


def available_dates() -> list[str]:
    """Dates that have a triage CSV, newest first — drives the date switcher."""
    gen = ROOT / "generated"
    days = [p.stem.replace("discovery_triage_", "") for p in gen.glob("discovery_triage_*.csv")]
    return sorted({d for d in days if DATE_RE.fullmatch(d)}, reverse=True)


def load_apps() -> list[dict]:
    if not APPS.exists():
        return []
    with APPS.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def app_url(row: dict) -> str:
    return (row.get("job_url") or row.get("posting_url") or "").strip()


def norm_url(u: str) -> str:
    """Same posting identity the write-back layer uses (see js_lib.canonical_url)."""
    return canonical_url(u)


def load_keeps(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("decision") or "").lower() == "keep"]

def load_passed_urls() -> set[str]:
    """URLs already passed or closed — do not resurface in the active queue."""
    if not JOB_DECISIONS.exists():
        return set()
    out: set[str] = set()
    with JOB_DECISIONS.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("decision") or "").strip().lower() in {"pass", "closed"}:
                u = norm_url(r.get("url") or "")
                if u:
                    out.add(u)
    # Also hide applications already marked passed/closed/rejected/withdrawn
    for r in load_apps():
        st = (r.get("status") or "").lower()
        if st in {"passed", "closed", "rejected", "withdrawn", "applied", "oa", "offer", "accepted"}:
            u = norm_url(app_url(r))
            if u:
                out.add(u)
    return out



def tier_for(company: str, role: str, source: str) -> tuple[str, str]:
    text = f"{company} {role}"
    if VERIFY_PATTERNS.search(text):
        return ("C", "Verify level/start before apply")
    if source in {"intern_list", "newgrad_jobs", "jobright_matches", "triage_keep"}:
        return ("A", "Today KEEP / fresh")
    if source == "backlog_discovered":
        return ("B", "Backlog discovered")
    if source == "backlog_saved":
        return ("D", "Older saved")
    return ("B", "Queue")


TIER_LABEL = {
    "A": "Today",
    "B": "Backlog",
    "C": "Verify level",
    "D": "Older",
}
CLASS_LABEL = {
    "big_tech": "Big tech",
    "biotech": "Biotech / health",
    "startup": "Startup / scaleup",
    "other": "Other",
}
GEO_LABEL = {
    "boston_ma": "Boston / MA",
    "bay_area": "Bay Area / SF",
    "other": "Other US",
}


def enrich(item: dict, lists: dict[str, list[str]], gtc_sponsors: list[str]) -> dict:
    item["company_class"] = classify_company(item["company"], lists)
    item["geo"] = classify_geo(item.get("location") or "")
    gtc = match_gtc_sponsor(item["company"], gtc_sponsors)
    item["gtc_sponsor"] = "yes" if gtc else "no"
    item["gtc_match"] = gtc
    item["tier_label"] = TIER_LABEL.get(item["tier"], item["tier"])
    item["class_label"] = CLASS_LABEL.get(item["company_class"], item["company_class"])
    item["geo_label"] = GEO_LABEL.get(item["geo"], item["geo"])
    return item


def collect(day: str) -> list[dict]:
    lists = load_yaml_lists()
    gtc_sponsors = load_gtc_sponsors()
    passed = load_passed_urls()
    items: list[dict] = []
    seen: set[str] = set(passed)  # treat passed as already-seen

    triage = latest_triage(day)
    if triage:
        for r in load_keeps(triage):
            discovery_url = (r.get("url") or "").strip()
            apply_url = (r.get("apply_url") or "").strip()
            apply_conf = (r.get("apply_url_confidence") or "").strip().lower()
            # Prefer the employer ATS link when resolution was confident — Jobright
            # discovery URLs cannot be applied to (signup wall).
            usable_apply = apply_url and apply_conf in {"exact", "strong"}
            open_url = apply_url if usable_apply else discovery_url
            if not open_url:
                continue
            # Hide if either the discovery URL or the resolved apply URL was passed.
            keys = {norm_url(open_url)}
            if discovery_url:
                keys.add(norm_url(discovery_url))
            if keys & seen:
                continue
            seen |= keys
            tier, note = tier_for(r.get("company", ""), r.get("role", ""), "triage_keep")
            items.append(
                enrich(
                    {
                        "tier": tier,
                        "note": note,
                        "company": r.get("company") or "",
                        "role": r.get("role") or "",
                        "url": open_url,
                        "discovery_url": discovery_url,
                        "apply_url": apply_url,
                        "apply_url_confidence": apply_conf,
                        "apply_ats": (r.get("apply_ats") or "").strip() if usable_apply else "",
                        "lane": r.get("suggested_lane") or "",
                        "cluster": r.get("suggested_cluster") or "",
                        "grad": r.get("grad_display_hint") or "program_end",
                        "job_id": "",
                        "source": "triage_keep",
                        "location": r.get("location") or "",
                        # The triage agent already explained the judgement —
                        # show it instead of burying it in the CSV.
                        "reason": (r.get("reason") or "").strip(),
                        "confidence": (r.get("confidence") or "").strip(),
                        "track": (r.get("track") or "").strip(),
                        "posted_relative": (r.get("posted_relative") or "").strip(),
                    },
                    lists,
                    gtc_sponsors,
                )
            )

    for r in load_apps():
        st = (r.get("status") or "").lower()
        if st not in {"discovered", "saved"}:
            continue
        url = app_url(r)
        if not url or norm_url(url) in seen:
            continue
        seen.add(norm_url(url))
        src = "backlog_discovered" if st == "discovered" else "backlog_saved"
        tier, note = tier_for(r.get("company", ""), r.get("role", ""), src)
        items.append(
            enrich(
                {
                    "tier": tier,
                    "note": note,
                    "company": r.get("company") or "",
                    "role": r.get("role") or "",
                    "url": url,
                    "lane": r.get("pursuit_lane") or "",
                    "cluster": r.get("role_cluster") or "",
                    "grad": "program_end",
                    "job_id": r.get("job_id") or "",
                    "source": src,
                    "location": r.get("location") or "",
                    "reason": (r.get("label_reason") or "").strip(),
                    "confidence": (r.get("label_confidence") or "").strip(),
                    "track": (r.get("employment_type") or "").strip(),
                    "posted_relative": "",
                },
                lists,
                gtc_sponsors,
            )
        )

    # Sort: Boston → Bay Area → other; then big_tech → startup → other; A→D
    geo_order = {"boston_ma": 0, "bay_area": 1, "other": 2}
    class_order = {"big_tech": 0, "biotech": 1, "startup": 2, "other": 3}
    tier_order = {"A": 0, "B": 1, "C": 2, "D": 3}
    items.sort(
        key=lambda x: (
            0 if x.get("gtc_sponsor") == "yes" else 1,
            geo_order.get(x["geo"], 9),
            class_order.get(x["company_class"], 9),
            tier_order.get(x["tier"], 9),
            x["company"].lower(),
            x["role"].lower(),
        )
    )
    return items


def render_md(day: str, items: list[dict]) -> str:
    boston = [i for i in items if i["geo"] == "boston_ma"]
    bay = [i for i in items if i["geo"] == "bay_area"]
    big = [i for i in items if i["company_class"] == "big_tech"]
    startup = [i for i in items if i["company_class"] == "startup"]
    biotech = [i for i in items if i["company_class"] == "biotech"]
    gtc = [i for i in items if i.get("gtc_sponsor") == "yes"]
    lines = [
        f"# Apply queue — {day}",
        "",
        "Filter layers on top of A/B/C/D:",
        "- **Geo:** Boston / MA · Bay Area / SF (not LA) · other US",
        "- **Company class:** big tech · biotech/health · startup/scaleup · other",
        "- **GTC 2026 sponsor:** matched against NVIDIA GTC sponsor/exhibitor list",
        "",
        f"Total **{len(items)}** · GTC sponsors **{len(gtc)}** · Boston/MA **{len(boston)}** · Bay Area **{len(bay)}** · Big tech **{len(big)}** · Biotech **{len(biotech)}** · Startup **{len(startup)}**",
        "",
        "Open the HTML for filters + Open next.",
        "",
        "## GTC 2026 sponsors in this queue",
        "",
    ]
    if not gtc:
        lines.append("_None matched in this queue._")
        lines.append("")
    for i, it in enumerate(gtc, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += [
        "## Boston / MA",
        "",
    ]
    if not boston:
        lines.append("_None in this queue._")
        lines.append("")
    for i, it in enumerate(boston, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += ["## Bay Area / SF (Silicon Valley — not LA)", ""]
    if not bay:
        lines.append("_None in this queue._")
        lines.append("")
    for i, it in enumerate(bay, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += ["## Big tech", ""]
    for i, it in enumerate(big, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += ["## Biotech / health", ""]
    if not biotech:
        lines.append("_None in this queue._")
        lines.append("")
    for i, it in enumerate(biotech, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += ["## Startup / scaleup", ""]
    for i, it in enumerate(startup, 1):
        lines.append(_md_item(i, it))
        lines.append("")

    lines += ["## Full list (sorted)", ""]
    for i, it in enumerate(items, 1):
        lines.append(_md_item(i, it))
        lines.append("")
    return "\n".join(lines) + "\n"


def _md_item(i: int, it: dict) -> str:
    jid = f" `{it['job_id']}`" if it["job_id"] else ""
    gtc = f" · GTC:{it['gtc_match']}" if it.get("gtc_sponsor") == "yes" else ""
    return (
        f"{i}. **[{it['tier']}] {it['company']} — {it['role']}**{jid}  \n"
        f"   {it['geo_label']} · {it['class_label']}{gtc} · {it['lane']}/{it['cluster']} · "
        f"grad=`{it['grad']}` · {it['tier_label']}  \n"
        f"   {it['url']}"
    )


def _counts(items: list[dict]) -> dict:
    def n(pred) -> int:
        return sum(1 for i in items if pred(i))

    return {
        "total": len(items),
        "gtc": n(lambda i: i.get("gtc_sponsor") == "yes"),
        "boston_ma": n(lambda i: i["geo"] == "boston_ma"),
        "bay_area": n(lambda i: i["geo"] == "bay_area"),
        "big_tech": n(lambda i: i["company_class"] == "big_tech"),
        "biotech": n(lambda i: i["company_class"] == "biotech"),
        "startup": n(lambda i: i["company_class"] == "startup"),
    }


def bootstrap_payload(day: str, items: list[dict], *, live: bool) -> dict:
    """Everything the page needs to render without a second request."""
    payload_items = []
    for it in items:
        row = dict(it)
        row["key"] = norm_url(it.get("url") or "")
        payload_items.append(row)
    return {
        "day": day,
        "dates": available_dates(),
        "live": live,
        "items": payload_items,
        "counts": _counts(items),
    }


def render_html(day: str, items: list[dict], *, live: bool = False, inline: bool = True) -> str:
    """Render the queue page from templates/apply_queue/index.html.

    inline=True  → single self-contained file (static fallback, works via file://)
    inline=False → links to /static/... so the live server can serve real assets
    """
    template = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
    payload = json.dumps(bootstrap_payload(day, items, live=live), ensure_ascii=False)
    # Keep the JSON from terminating the surrounding <script> element.
    payload = payload.replace("</", "<\\/")

    if inline:
        css = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
        spring = (STATIC_DIR / "spring.js").read_text(encoding="utf-8")
        app = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        # file:// blocks ES module imports, so inline as one classic script
        # with the import line stripped and the spring API pulled into scope.
        app_inline = app.replace(
            "import { Spring, SPRINGS, project, rubberband, VelocityTracker, prefersReducedMotion } from './spring.js';",
            "",
        )
        spring_inline = spring.replace("export class", "class").replace("export const", "const").replace("export function", "function")
        head_assets = f"<style>\n{css}\n</style>"
        body_assets = f"<script>\n{spring_inline}\n{app_inline}\n</script>"
    else:
        head_assets = '<link rel="stylesheet" href="/static/apply_queue/styles.css" />'
        body_assets = '<script type="module" src="/static/apply_queue/app.js"></script>'

    return (
        template.replace("__DAY__", html.escape(day))
        .replace("__HEAD_ASSETS__", head_assets)
        .replace("__BOOTSTRAP__", payload)
        .replace("__BODY_ASSETS__", body_assets)
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args()
    day = args.date
    items = collect(day)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / f"{day}.md"
    html_path = OUT_DIR / f"{day}.html"
    md_path.write_text(render_md(day, items), encoding="utf-8")
    html_path.write_text(render_html(day, items), encoding="utf-8")
    boston = sum(1 for i in items if i["geo"] == "boston_ma")
    bay = sum(1 for i in items if i["geo"] == "bay_area")
    big = sum(1 for i in items if i["company_class"] == "big_tech")
    startup = sum(1 for i in items if i["company_class"] == "startup")
    biotech = sum(1 for i in items if i["company_class"] == "biotech")
    print(html_path)
    print(md_path)
    gtc_n = sum(1 for i in items if i.get("gtc_sponsor") == "yes")
    print(f"items={len(items)} gtc={gtc_n} boston_ma={boston} bay_area={bay} big_tech={big} biotech={biotech} startup={startup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
