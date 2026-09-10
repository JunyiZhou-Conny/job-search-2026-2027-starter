from __future__ import annotations

import re
from pathlib import Path

from rqe.models import (
    ArenaVote,
    Bank,
    Candidate,
    JobBrief,
    Match,
    ValidationIssue,
    ValidationReport,
)

_NUM = re.compile(
    r"(?<![A-Za-z])"
    r"(?:"
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?"
    r"|\d+\.\d+"
    r"|\d+"
    r")"
    r"(?:\s*(?:%|x|×|hours?\b|h\b|pp))?"
    r"(?![A-Za-z])",
    re.I,
)

PLANNED_DONE = (
    r"trained (a )?grpo",
    r"downloaded (the )?(pannuke|consep|monuseg|lizard|glas|crag)",
    r"miccai 2027 (acceptance|accepted|submitted)",
    r"built diffusion models",
    r"implemented diffusion",
    r"trained diffusion",
)

YEAR_OK = {str(y) for y in range(2021, 2028)}


def strip_tex(tex: str) -> str:
    text = re.sub(r"%.*", " ", tex)
    text = re.sub(r"\\(?:href|textbf|texttt|textit)\{", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def _item_texts(tex: str) -> list[str]:
    items: list[str] = []
    for raw in tex.splitlines():
        line = raw.strip()
        if not line.startswith("\\item "):
            continue
        if "tabular" in line or "resumeSubheading" in line or "resumeItem{" in line:
            continue
        items.append(strip_tex(line[len("\\item ") :]))
    return items


def _number_keys(raw: str) -> set[str]:
    compact = re.sub(r"\s+", "", raw.lower())
    keys = {compact}
    keys.add(re.sub(r"[,%x×hpp]+$", "", compact))
    keys.add(compact.replace(",", ""))
    return {k for k in keys if k}


def _allowed_numbers(bank: Bank, used_claim_ids: tuple[str, ...]) -> set[str]:
    blobs = list(bank.allowed_number_blobs) + list(bank.profile_blobs)
    for project in bank.projects.values():
        for claim in project.claims:
            if claim.id in used_claim_ids:
                blobs.append(claim.claim)
                blobs.extend(claim.allowed_wording.values())
    allowed: set[str] = set()
    for blob in blobs:
        for m in _NUM.finditer(str(blob)):
            allowed.update(_number_keys(m.group(0)))
    allowed.update(YEAR_OK)
    allowed.update({"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "16", "21", "30"})
    return allowed


def validate_tex(bank: Bank, tex: str, used_claim_ids: tuple[str, ...] = ()) -> ValidationReport:
    report = ValidationReport()
    plain = strip_tex(tex).lower()
    for token in bank.forbidden_tokens:
        if token and re.search(rf"\b{re.escape(token)}\b", plain):
            report.issues.append(
                ValidationIssue("fail", "forbidden_token", f"resume names forbidden token {token!r}")
            )
    for pat in PLANNED_DONE:
        if re.search(pat, plain):
            report.issues.append(
                ValidationIssue("fail", "planned_as_done", f"planned work written as completed ({pat})")
            )

    ids = used_claim_ids or infer_used_claims(bank, tex)
    allowed = _allowed_numbers(bank, ids)
    for item in _item_texts(tex):
        if re.match(r"^(Languages|ML|LLM|Backend|Data|Cloud|Certifications)\b", item):
            continue
        if "program requirements complete" in item.lower() or "coursework:" in item.lower():
            continue
        for m in _NUM.finditer(item):
            keys = _number_keys(m.group(0))
            if keys & allowed:
                continue
            raw = re.sub(r"\s+", "", m.group(0).lower())
            if raw.isdigit() and int(raw) <= 31:
                continue
            report.issues.append(
                ValidationIssue(
                    "fail",
                    "unsupported_metric",
                    f"number {m.group(0)!r} in bullet {item!r} is not in the evidence bank",
                )
            )

    if "\\end{document}" not in tex:
        report.issues.append(ValidationIssue("fail", "malformed_tex", "missing \\end{document}"))
    if "Junyi" not in tex:
        report.issues.append(ValidationIssue("fail", "identity", "heading lost the candidate name"))
    return report


def validate_pdf_pages(pdf: Path, limit: int = 1) -> ValidationReport:
    report = ValidationReport()
    if not pdf.is_file():
        report.issues.append(ValidationIssue("warn", "pdf_missing", f"{pdf} was not compiled"))
        return report
    data = pdf.read_bytes()
    if data[:5] != b"%PDF-":
        report.issues.append(ValidationIssue("fail", "pdf_magic", f"{pdf} is not a PDF"))
        return report
    pages = len(re.findall(rb"/Type\s*/Page\b", data))
    if pages == 0:
        report.issues.append(ValidationIssue("warn", "pdf_pages_unknown", "could not count PDF pages"))
    elif pages > limit:
        report.issues.append(
            ValidationIssue("fail", "page_overflow", f"{pdf.name} has {pages} pages, limit {limit}")
        )
    return report


def infer_used_claims(bank: Bank, tex: str) -> tuple[str, ...]:
    plain = strip_tex(tex).lower()
    used: list[str] = []
    for project in bank.projects.values():
        title_key = project.title.lower()[:24]
        if title_key and title_key not in plain:
            continue
        for claim in project.claims:
            if not claim.usable_on_resume:
                continue
            needles = [claim.claim.lower()[:32]]
            needles.extend(w.lower()[:32] for w in claim.allowed_wording.values() if w)
            needles.extend(m.raw.lower() for m in claim.metrics if len(m.raw) >= 3)
            if any(n and n in plain for n in needles):
                used.append(claim.id)
    return tuple(used)


def _used_ids(candidate: Candidate, bank: Bank) -> set[str]:
    if candidate.used_claim_ids:
        return set(candidate.used_claim_ids)
    return set(infer_used_claims(bank, candidate.tex))


def _coverage(candidate: Candidate, job: JobBrief, matches: list[Match], bank: Bank) -> tuple[int, str, str]:
    used = _used_ids(candidate, bank)
    covered = 0
    req_id = ""
    claim_id = ""
    for req in job.requirements:
        if req.kind not in {"required", "preferred", "responsibility", "stack"}:
            continue
        for m in matches:
            if m.requirement_id == req.id and m.claim_id in used and m.strength in {
                "strong_direct",
                "transferable",
            }:
                covered += 1
                if not req_id:
                    req_id, claim_id = req.id, m.claim_id
                break
    return covered, req_id or (job.requirements[0].id if job.requirements else ""), claim_id


def _metric_count(candidate: Candidate, bank: Bank) -> int:
    n = 0
    for pid, cids in candidate.strategy.bullets.items():
        for cid in cids:
            for claim in bank.projects[pid].claims:
                if claim.id == cid:
                    n += len(claim.metrics)
    return n


def _defense_score(candidate: Candidate, bank: Bank) -> int:
    n = 0
    for pid, cids in candidate.strategy.bullets.items():
        for cid in cids:
            for claim in bank.projects[pid].claims:
                if claim.id == cid:
                    n += {"strong": 3, "moderate": 2, "weak": 1}[claim.interview_defensibility]
    return n


def arena(
    job: JobBrief,
    matches: list[Match],
    bank: Bank,
    contestants: dict[str, Candidate],
    validations: dict[str, ValidationReport],
) -> list[ArenaVote]:
    votes: list[ArenaVote] = []
    names = list(contestants)
    for name in names:
        report = validations[name]
        if not report.ok:
            req = job.requirements[0].id if job.requirements else "r00"
            claim = contestants[name].used_claim_ids[0] if contestants[name].used_claim_ids else ""
            votes.append(
                ArenaVote(
                    perspective="evidence_auditor",
                    winner="veto",
                    requirement_id=req,
                    claim_id=claim,
                    reason="factual validation failed: "
                    + "; ".join(i.detail for i in report.issues if i.severity == "fail")[:300],
                    veto=True,
                )
            )
    alive = [n for n in names if validations[n].ok]
    if len(alive) < 2:
        return votes

    def pairwise(a: str, b: str) -> None:
        ca, cb = contestants[a], contestants[b]
        cov_a, req_a, cl_a = _coverage(ca, job, matches, bank)
        cov_b, req_b, cl_b = _coverage(cb, job, matches, bank)
        met_a = _metric_count(ca, bank) if ca.used_claim_ids else len(_used_ids(ca, bank))
        met_b = _metric_count(cb, bank) if cb.used_claim_ids else len(_used_ids(cb, bank))
        def_a = _defense_score(ca, bank) if ca.used_claim_ids else 2 * len(_used_ids(ca, bank))
        def_b = _defense_score(cb, bank) if cb.used_claim_ids else 2 * len(_used_ids(cb, bank))

        def pick(score_a: int, score_b: int, req: str, claim_a: str, claim_b: str, why: str, perspective: str) -> None:
            if score_a == score_b:
                winner = "tie"
                claim = claim_a or claim_b
            elif score_a > score_b:
                winner = a
                claim = claim_a
            else:
                winner = b
                claim = claim_b
            votes.append(
                ArenaVote(
                    perspective=perspective,
                    winner=winner,
                    requirement_id=req,
                    claim_id=claim,
                    reason=f"{why} ({a}={score_a}, {b}={score_b})",
                )
            )

        pick(cov_a, cov_b, req_a or req_b, cl_a, cl_b, "required-signal coverage by used claims", "recruiter")
        pick(
            def_a,
            def_b,
            req_a or req_b,
            cl_a,
            cl_b,
            "interview-defensible claims used",
            "technical_hiring_manager",
        )
        domain_a = sum(1 for s in ca.strategy.dimensions.values() for x in s)
        domain_b = sum(1 for s in cb.strategy.dimensions.values() for x in s)
        pick(domain_a, domain_b, req_a or req_b, cl_a, cl_b, "family-signal density on selected bullets", "domain_expert")
        pick(met_a, met_b, req_a or req_b, cl_a, cl_b, "measured figures on selected claims", "impact_reader")
        pick(def_a, def_b, req_a or req_b, cl_a, cl_b, "survives five minutes of questioning", "skeptical_interviewer")

    engine = [n for n in alive if n != "baseline"]
    if "baseline" in alive:
        for n in engine:
            pairwise("baseline", n)
    for i, a in enumerate(engine):
        for b in engine[i + 1 :]:
            pairwise(a, b)
    return votes


def arena_markdown(votes: list[ArenaVote], validations: dict[str, ValidationReport]) -> str:
    lines = [
        "# Arena report",
        "",
        "Pairwise only. Counts are coverage of structured matches, not an ATS score.",
        "",
    ]
    vetoed = [v for v in votes if v.veto]
    if vetoed:
        lines.append("## Auditor vetoes")
        lines.append("")
        for v in vetoed:
            lines.append(f"- `{v.winner}` blocked. {v.reason} (requirement `{v.requirement_id}`, claim `{v.claim_id}`)")
        lines.append("")
    lines.append("## Votes")
    lines.append("")
    for v in votes:
        if v.veto:
            continue
        lines.append(
            f"- {v.perspective} prefers `{v.winner}` citing requirement `{v.requirement_id}` "
            f"and claim `{v.claim_id}`. {v.reason}"
        )
    tallies: dict[str, int] = {}
    for v in votes:
        if v.veto or v.winner in {"tie", "veto"}:
            continue
        tallies[v.winner] = tallies.get(v.winner, 0) + 1
    if tallies:
        winner = max(tallies, key=lambda k: tallies[k])
        lines.extend(["", f"Plurality of non-veto votes is `{winner}`.", ""])
        for name, n in sorted(tallies.items(), key=lambda kv: -kv[1]):
            lines.append(f"- `{name}` {n}")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for name, report in validations.items():
        status = "pass" if report.ok else "FAIL"
        lines.append(f"- `{name}` {status}")
        for issue in report.issues:
            lines.append(f"  - {issue.severity} `{issue.code}` {issue.detail}")
    lines.append("")
    return "\n".join(lines)


def validation_markdown(report: ValidationReport) -> str:
    lines = ["# Validation report", ""]
    if report.ok:
        lines.append("No hard failures.")
    else:
        lines.append("Hard failures present. This resume is not valid.")
    lines.append("")
    for issue in report.issues:
        lines.append(f"- {issue.severity} `{issue.code}` {issue.detail}")
    lines.append("")
    return "\n".join(lines)
