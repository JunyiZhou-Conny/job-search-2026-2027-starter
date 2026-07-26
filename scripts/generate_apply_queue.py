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
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "data" / "applications.csv"
OUT_DIR = ROOT / "generated" / "apply_queue"
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


def load_apps() -> list[dict]:
    if not APPS.exists():
        return []
    with APPS.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def app_url(row: dict) -> str:
    return (row.get("job_url") or row.get("posting_url") or "").strip()


def norm_url(u: str) -> str:
    return u.strip().rstrip("/").lower()


def load_keeps(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("decision") or "").lower() == "keep"]

def load_passed_urls() -> set[str]:
    """URLs the user already passed — do not resurface in the active queue."""
    if not JOB_DECISIONS.exists():
        return set()
    out: set[str] = set()
    with JOB_DECISIONS.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("decision") or "").strip().lower() == "pass":
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
    "A": "今日 KEEP",
    "B": "积压未投",
    "C": "先核实 level",
    "D": "旧 saved",
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
            url = (r.get("url") or "").strip()
            if not url or norm_url(url) in seen:
                continue
            seen.add(norm_url(url))
            tier, note = tier_for(r.get("company", ""), r.get("role", ""), "triage_keep")
            items.append(
                enrich(
                    {
                        "tier": tier,
                        "note": note,
                        "company": r.get("company") or "",
                        "role": r.get("role") or "",
                        "url": url,
                        "lane": r.get("suggested_lane") or "",
                        "cluster": r.get("suggested_cluster") or "",
                        "grad": r.get("grad_display_hint") or "program_end",
                        "job_id": "",
                        "source": "triage_keep",
                        "location": r.get("location") or "",
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


def render_html(day: str, items: list[dict]) -> str:
    def li(it: dict, idx: int) -> str:
        return f"""
      <li class="item tier-{html.escape(it['tier'])}"
          data-idx="{idx}"
          data-geo="{html.escape(it['geo'])}"
          data-class="{html.escape(it['company_class'])}"
          data-tier="{html.escape(it['tier'])}"
          data-gtc="{html.escape(it.get('gtc_sponsor') or 'no')}"
          data-url="{html.escape(it['url'])}"
          data-company="{html.escape(it['company'])}"
          data-role="{html.escape(it['role'])}"
          data-job-id="{html.escape(it.get('job_id') or '')}">
        <label class="check">
          <input type="checkbox" data-key="{html.escape(norm_url(it['url']))}" title="Applied this session" />
          <span class="badges">
            {"<span class=\"badge gtc\">GTC sponsor</span>" if it.get("gtc_sponsor") == "yes" else ""}
            <span class="badge geo-{html.escape(it['geo'])}">{html.escape(it['geo_label'])}</span>
            <span class="badge class-{html.escape(it['company_class'])}">{html.escape(it['class_label'])}</span>
            <span class="badge tier">{html.escape(it['tier'])} · {html.escape(it['tier_label'])}</span>
          </span>
          <span class="main">
            <span class="title">{html.escape(it['company'])} — {html.escape(it['role'])}</span>
            <span class="meta">{html.escape(it['lane'] or '—')} / {html.escape(it['cluster'] or '—')}
              · resume <code>{html.escape(it['grad'])}</code>
              · {html.escape(it['location'] or 'location ?')}
              {" · " + html.escape(it['job_id']) if it['job_id'] else ""}
            </span>
          </span>
        </label>
        <div class="actions">
          <a class="open" href="{html.escape(it['url'])}" target="_blank" rel="noopener">Open</a>
          <button type="button" class="pass" title="Not for me — archive so it will not return">Pass</button>
        </div>
      </li>"""

    body = "\n".join(li(it, i) for i, it in enumerate(items))
    n_bos = sum(1 for i in items if i["geo"] == "boston_ma")
    n_bay = sum(1 for i in items if i["geo"] == "bay_area")
    n_big = sum(1 for i in items if i["company_class"] == "big_tech")
    n_st = sum(1 for i in items if i["company_class"] == "startup")
    n_bio = sum(1 for i in items if i["company_class"] == "biotech")
    n_gtc = sum(1 for i in items if i.get("gtc_sponsor") == "yes")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Apply queue — {html.escape(day)}</title>
<style>
  :root {{
    --bg: #f6f3ee; --ink: #1c1a17; --muted: #5c564e; --line: #d9d2c7;
    --card: #fffdf9; --accent: #0f5c4c; --warn: #8a4b12; --done: #9a948a;
    --boston: #1f4b7a; --bay: #9a3412; --big: #5b2d8e; --start: #0f5c4c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font: 16px/1.45 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
    color: var(--ink);
    background: radial-gradient(1200px 600px at 10% -10%, #e7efe9 0%, transparent 55%), var(--bg);
  }}
  header {{
    position: sticky; top: 0; z-index: 2;
    backdrop-filter: blur(8px);
    background: color-mix(in srgb, var(--bg) 86%, white);
    border-bottom: 1px solid var(--line);
    padding: 1rem 1.25rem 0.9rem;
  }}
  h1 {{ margin: 0 0 0.25rem; font-size: 1.35rem; letter-spacing: -0.02em; }}
  .sub {{ color: var(--muted); font-size: 0.95rem; max-width: 54rem; }}
  .legend {{
    margin-top: 0.55rem; font-size: 0.88rem; color: var(--muted);
    max-width: 54rem;
  }}
  .filters, .controls {{
    display: flex; flex-wrap: wrap; gap: 0.45rem; align-items: center;
    margin-top: 0.75rem;
  }}
  .filters button, .controls button, .open {{
    font: inherit; cursor: pointer; border-radius: 999px;
    border: 1px solid var(--line); background: white; color: var(--ink);
    padding: 0.35rem 0.8rem; text-decoration: none;
  }}
  .filters button.active {{
    border-color: var(--ink); background: var(--ink); color: white;
  }}
  .controls button.primary {{
    border-color: var(--ink); background: var(--ink); color: white;
  }}
  #progress {{ color: var(--muted); margin-left: 0.25rem; }}
  #counts {{ color: var(--muted); font-size: 0.9rem; }}
  main {{ max-width: 880px; margin: 0 auto; padding: 1.25rem; }}
  ol {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 0.65rem; }}
  .item {{
    display: grid; grid-template-columns: 1fr auto; gap: 0.75rem; align-items: center;
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 0.8rem 0.9rem;
  }}
  .item.hidden {{ display: none; }}
  .item.done {{ opacity: 0.45; }}
  .item.done .title {{ text-decoration: line-through; color: var(--done); }}
  .check {{ display: grid; grid-template-columns: auto 1fr; gap: 0.55rem; align-items: start; }}
  .badges {{ display: none; }}
  .main .title {{ display: block; font-weight: 650; }}
  .main .meta {{ display: block; color: var(--muted); font-size: 0.88rem; margin-top: 0.2rem; }}
  .pillrow {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.35rem; }}
  .badge {{
    font: 11px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
    border: 1px solid var(--line); border-radius: 6px; padding: 0.18rem 0.4rem;
    background: #fff;
  }}
  .geo-boston_ma {{ color: var(--boston); border-color: color-mix(in srgb, var(--boston) 35%, var(--line)); }}
  .geo-bay_area {{ color: var(--bay); border-color: color-mix(in srgb, var(--bay) 35%, var(--line)); }}
  .class-big_tech {{ color: var(--big); border-color: color-mix(in srgb, var(--big) 35%, var(--line)); }}
  .class-biotech {{ color: #9f1239; border-color: color-mix(in srgb, #9f1239 35%, var(--line)); }}
  .class-startup {{ color: var(--start); border-color: color-mix(in srgb, var(--start) 35%, var(--line)); }}
  .badge.gtc {{ color: #76b900; border-color: color-mix(in srgb, #76b900 45%, var(--line)); font-weight: 700; }}
  .actions {{ display: flex; flex-direction: column; gap: 0.35rem; align-items: stretch; }}
  .open {{ color: var(--accent); border-color: var(--accent); text-align: center; }}
  .pass {{
    font: inherit; cursor: pointer; border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--warn) 55%, var(--line));
    background: transparent; color: var(--warn); padding: 0.35rem 0.8rem;
  }}
  .item.passed {{ opacity: 0.35; }}
  .item.passed .title {{ text-decoration: line-through; }}
  .syncbar {{ margin-top: 0.55rem; font-size: 0.9rem; color: var(--warn); }}
  .syncbar strong {{ color: var(--ink); }}
  footer {{ max-width: 880px; margin: 0 auto 2rem; padding: 0 1.25rem; color: var(--muted); font-size: 0.9rem; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.85em; }}
</style>
</head>
<body>
<header>
  <h1>Apply queue — {html.escape(day)}</h1>
  <p class="sub">
    <strong>Open</strong> → 看 JD → 合适就 Simplify 投递后勾选；不合适点 <strong>Pass</strong>（封存）。
    想要实时写入仓库：用 <code>python3 scripts/serve_apply_queue.py</code> 打开本页（LIVE），不要双击静态 HTML。
  </p>
  <p class="legend">
    勾选 = 本轮已投。<strong>Pass</strong> = 不投并封存。LIVE 模式点 Pass 立刻写
    <code>data/job_decisions.csv</code>（有 applications 行则 <code>status=passed</code>）。
  </p>
  <div class="filters" id="geoFilters">
    <span id="counts">GTC {n_gtc} · Boston/MA {n_bos} · Bay Area {n_bay} · Big tech {n_big} · Biotech {n_bio} · Startup {n_st} · All {len(items)}</span>
  </div>
  <div class="filters" id="classFilters"></div>
  <div class="filters" id="gtcFilters"></div>
  <div class="filters" id="tierFilters"></div>
  <div class="filters" id="passFilters"></div>
  <div class="controls">
    <button class="primary" id="openNext" type="button">Open next (visible)</button>
    <button id="exportPasses" type="button">Export passes</button>
    <button id="reset" type="button">Reset checks</button>
    <span id="progress"></span>
  </div>
  <div class="syncbar" id="syncbar"></div>
</header>
<main>
  <ol id="queue">
{body}
  </ol>
</main>
<footer>
  After Export: <code>python3 scripts/sync_queue_decisions.py --file ~/Downloads/queue_decisions_....json</code>
  then regenerate this page.
</footer>
<script>
const KEY = "apply-queue-v2-{html.escape(day)}";
const PASS_KEY = "apply-queue-pass-v1-{html.escape(day)}";
const LIVE = (typeof window !== 'undefined' && window.APPLY_QUEUE_LIVE === true);
const items = [...document.querySelectorAll('.item')];
const boxes = [...document.querySelectorAll('input[type=checkbox]')];
const saved = JSON.parse(localStorage.getItem(KEY) || "{{}}");
let passes = JSON.parse(localStorage.getItem(PASS_KEY) || "{{}}");
const state = {{ geo: 'all', company: 'all', tier: 'all', gtc: 'all', pass: 'active' }};

function mkFilters(el, key, opts) {{
  opts.forEach(([val, label]) => {{
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.dataset.val = val;
    if (val === 'all') b.classList.add('active');
    b.onclick = () => {{
      state[key] = val;
      [...el.querySelectorAll('button')].forEach(x => x.classList.toggle('active', x.dataset.val === val));
      applyFilters();
    }};
    el.appendChild(b);
  }});
}}

mkFilters(document.getElementById('geoFilters'), 'geo', [
  ['all', 'All locations'],
  ['boston_ma', 'Boston / MA only'],
  ['bay_area', 'Bay Area / SF only'],
  ['other', 'Other US'],
]);
mkFilters(document.getElementById('classFilters'), 'company', [
  ['all', 'All companies'],
  ['big_tech', 'Big tech'],
  ['biotech', 'Biotech / health'],
  ['startup', 'Startup / scaleup'],
  ['other', 'Other'],
]);
mkFilters(document.getElementById('gtcFilters'), 'gtc', [
  ['all', 'All · GTC any'],
  ['yes', 'GTC sponsor only'],
  ['no', 'Not GTC sponsor'],
]);
mkFilters(document.getElementById('tierFilters'), 'tier', [
  ['all', 'All tiers'],
  ['A', 'A · 今日 KEEP'],
  ['B', 'B · 积压'],
  ['C', 'C · 先核实'],
  ['D', 'D · 旧 saved'],
]);
mkFilters(document.getElementById('passFilters'), 'pass', [
  ['active', 'Active only'],
  ['passed', 'Passed (archived)'],
  ['all', 'Active + passed'],
]);

// inject pillrow into each item from badges
items.forEach((item) => {{
  const badges = item.querySelector('.badges');
  const main = item.querySelector('.main');
  const row = document.createElement('div');
  row.className = 'pillrow';
  row.innerHTML = badges.innerHTML;
  main.prepend(row);
}});

function urlKey(item) {{
  let u = (item.dataset.url || '').split('?')[0];
  while (u.endsWith('/')) u = u.slice(0, -1);
  return u.toLowerCase();
}}

function visibleBoxes() {{
  return boxes.filter((b) => {{
    const item = b.closest('.item');
    return !item.classList.contains('hidden') && !item.classList.contains('passed');
  }});
}}

function applyFilters() {{
  items.forEach((item) => {{
    const key = urlKey(item);
    const isPassed = !!passes[key];
    item.classList.toggle('passed', isPassed);
    const okGeo = state.geo === 'all' || item.dataset.geo === state.geo;
    const okClass = state.company === 'all' || item.dataset.class === state.company;
    const okTier = state.tier === 'all' || item.dataset.tier === state.tier;
    const okGtc = state.gtc === 'all' || item.dataset.gtc === state.gtc;
    let okPass = true;
    if (state.pass === 'active') okPass = !isPassed;
    if (state.pass === 'passed') okPass = isPassed;
    item.classList.toggle('hidden', !(okGeo && okClass && okTier && okGtc && okPass));
  }});
  paint();
}}

function paint() {{
  let done = 0;
  boxes.forEach((b) => {{
    const on = !!saved[b.dataset.key];
    b.checked = on;
    b.closest('.item').classList.toggle('done', on);
    if (on) done += 1;
  }});
  const vis = boxes.filter((b) => !b.closest('.item').classList.contains('hidden'));
  const visDone = vis.filter((b) => b.checked).length;
  const nPass = Object.keys(passes).length;
  document.getElementById('progress').textContent =
    visDone + ' / ' + vis.length + ' visible checked · passed ' + nPass;
  const bar = document.getElementById('syncbar');
  if (LIVE) {{
    bar.innerHTML = nPass
      ? ('<strong>LIVE</strong> · ' + nPass + ' passed written to repo')
      : '<strong>LIVE</strong> · Pass writes to data/job_decisions.csv immediately';
    const exp = document.getElementById('exportPasses');
    if (exp) exp.style.display = 'none';
  }} else {{
    bar.innerHTML = nPass
      ? ('<strong>' + nPass + ' passed</strong> pending export → Export passes, then sync_queue_decisions.py')
      : 'Static file mode · for instant Pass, run: python3 scripts/serve_apply_queue.py --date {html.escape(day)}';
  }}
}}

boxes.forEach((b) => b.addEventListener('change', () => {{
  saved[b.dataset.key] = b.checked;
  localStorage.setItem(KEY, JSON.stringify(saved));
  paint();
}}));

async function recordPass(item, reason) {{
  const key = urlKey(item);
  const row = {{
    url: item.dataset.url,
    company: item.dataset.company,
    role: item.dataset.role,
    job_id: item.dataset.jobId || '',
    decision: 'pass',
    reason: (reason || '').trim(),
    decided_at: new Date().toISOString(),
    source: LIVE ? 'apply_queue_live' : 'apply_queue',
  }};
  if (LIVE) {{
    const res = await fetch('/api/pass', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(row),
    }});
    if (!res.ok) {{
      alert('Pass failed to save to repo');
      return false;
    }}
  }} else {{
    localStorage.setItem(PASS_KEY, JSON.stringify(Object.assign(passes, {{ [key]: row }})));
  }}
  passes[key] = row;
  if (!LIVE) localStorage.setItem(PASS_KEY, JSON.stringify(passes));
  return true;
}}

items.forEach((item) => {{
  item.querySelector('.pass').addEventListener('click', async () => {{
    const key = urlKey(item);
    const reason = prompt('Pass reason (optional). e.g. needs 1+ YOE / not interested / clearance', passes[key]?.reason || '');
    if (reason === null) return;
    const ok = await recordPass(item, reason);
    if (ok) applyFilters();
  }});
}});

document.getElementById('reset').onclick = () => {{
  Object.keys(saved).forEach((k) => delete saved[k]);
  localStorage.setItem(KEY, JSON.stringify(saved));
  paint();
}};
document.getElementById('openNext').onclick = () => {{
  const next = visibleBoxes().find((b) => !b.checked);
  if (!next) {{ alert('No active unchecked roles in the current filter.'); return; }}
  const link = next.closest('.item').querySelector('a.open');
  window.open(link.href, '_blank', 'noopener');
  next.focus();
}};
document.getElementById('exportPasses').onclick = () => {{
  const decisions = Object.values(passes);
  if (!decisions.length) {{ alert('No passes yet.'); return; }}
  const blob = new Blob([JSON.stringify({{ exported_at: new Date().toISOString(), decisions }}, null, 2)], {{ type: 'application/json' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'queue_decisions_{html.escape(day)}.json';
  a.click();
  URL.revokeObjectURL(a.href);
}};

async function boot() {{
  if (LIVE) {{
    try {{
      const res = await fetch('/api/passes');
      const data = await res.json();
      const map = {{}};
      (data.decisions || []).forEach((d) => {{
        let u = (d.url || '').split('?')[0];
        while (u.endsWith('/')) u = u.slice(0, -1);
        map[u.toLowerCase()] = d;
      }});
      passes = map;
    }} catch (e) {{}}
  }}
  applyFilters();
}}
boot();
</script>
</body>
</html>
"""


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
