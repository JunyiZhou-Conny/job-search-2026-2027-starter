"""Render a candidate resume and audit files from a strategy."""

from __future__ import annotations

import re
from pathlib import Path

from rqe.models import Bank, Candidate, Claim, JobBrief, Match, Project, Strategy

ROOT = Path(__file__).resolve().parents[2]
BASE_TEX = ROOT / "resumes" / "base" / "JZ_resume.tex"

TITLE_ALIASES = {
    "cellot_wyss": ("speciesot", "cross-species", "wyss"),
    "autoresearch_cellot": ("closed-loop cluster", "autonomous ablation", "autoresearch"),
    "mixhvg_py": ("mixhvg",),
    "job_search_os": ("job search os",),
    "vlm_textvqa_lora": ("textvqa", "blip-2"),
    "cv_caltech101": ("caltech-101", "caltech"),
    "cv_segmentation_voc": ("pascal voc", "semantic segmentation"),
    "cv_pneumonia": ("pneumonia detection",),
    "sseg_rlvr": ("structure-verified", "s-seg-rlvr"),
    "airway_chatbot": ("airway management",),
    "compleg_uk_nz": ("legislative studies", "compleg"),
    "alphafold_pipeline": ("alphafold",),
    "transformer_reimpl": ("transformer architecture",),
}


def latex_escape(text: str) -> str:
    text = text.replace("\\", r"\textbackslash{}")
    repl = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = []
    for ch in text:
        out.append(repl.get(ch, ch))
    return "".join(out)


def bold_known_tech(text: str, techs: tuple[str, ...]) -> str:
    # Longest first so "MongoDB Atlas Vector Search" wins over "MongoDB".
    ordered = sorted({t for t in techs if t}, key=len, reverse=True)
    result = text
    for tech in ordered:
        pattern = re.compile(re.escape(tech), re.I)
        if pattern.search(result):
            result = pattern.sub(lambda m: r"\textbf{" + m.group(0) + "}", result, count=1)
    return result


class BaseDoc:
    def __init__(self, text: str) -> None:
        self.text = text
        start = text.index("\\begin{document}") + len("\\begin{document}")
        end = text.index("% Education")
        self.preamble = text[:start]
        self.header = text[start:end]
        self.education = self._section("Education")
        self.skill_lines = self._skill_lines()
        self.entries = self._entries()
        self.bound: dict[str, str] = {}

    def _section(self, name: str) -> str:
        start = self.text.index(f"\\section{{{name}}}")
        end = self.text.index("\\resumeSubHeadingListEnd", start) + len("\\resumeSubHeadingListEnd")
        return self.text[start:end]

    def _skill_lines(self) -> dict[str, str]:
        block = self._section("Technical Skills")
        lines: dict[str, str] = {}
        for raw in block.splitlines():
            m = re.match(r"\s*\\resumeItem\{(.+?)\}\{", raw)
            if m:
                lines[m.group(1)] = raw.strip()
        return lines

    def _entries(self) -> list[str]:
        marker = "% Research Experience"
        start = self.text.find(marker)
        if start < 0:
            start = self.text.find("\\section{Research Experience}")
        if start < 0:
            start = self.text.find("\\section{Engineering Projects}")
        body = self.text[start:] if start >= 0 else self.text
        chunks = re.split(r"(?=  \\resumeSubheading)", body)
        found: list[str] = []
        for chunk in chunks:
            if "\\resumeSubheading" not in chunk:
                continue
            for stop in ("\\resumeSubHeadingListEnd", "\\end{document}"):
                if stop in chunk:
                    chunk = chunk[: chunk.index(stop)]
            if "M.S. in Health Data Science" in chunk:
                continue
            found.append(chunk.rstrip() + "\n")
        return found

    def bind(self, bank: Bank) -> None:
        unused = list(self.entries)
        bound: dict[str, str] = {}
        for project in bank.projects.values():
            hit = self._find_entry(project, unused)
            if hit is not None:
                bound[project.id] = hit
                unused.remove(hit)
        self.bound = bound

    def _find_entry(self, project: Project, unused: list[str]) -> str | None:
        needles = [project.title.split(".")[0].strip().lower()]
        needles.extend(TITLE_ALIASES.get(project.id, ()))
        if project.entry_key:
            needles.append(project.entry_key.lower())
        needles = [n for n in needles if n]
        for needle in needles:
            for entry in unused:
                if needle in entry.lower():
                    return entry
        return None


def _heading_only(entry: str) -> str:
    start = entry.find("\\resumeItemListStart")
    if start == -1:
        return entry
    return entry[:start]


def _heading_from_bank(project: Project) -> str:
    title = latex_escape(project.title)
    if project.source_url:
        title = (
            f"{title} \\href{{{project.source_url}}}"
            r"{\normalfont\small [GitHub]}"
        )
    role = latex_escape(project.role)
    org = latex_escape(project.org)
    mid = f"{role} $|$ {org}" if role and org else (role or org)
    dates = latex_escape(project.dates)
    return (
        "  \\resumeSubheading\n"
        f"    {{{title}}}{{}}\n"
        f"    {{{mid}}}{{{dates}}}\n"
    )


def _claim(bank: Bank, claim_id: str) -> Claim:
    for project in bank.projects.values():
        for claim in project.claims:
            if claim.id == claim_id:
                return claim
    raise KeyError(claim_id)


def render_tex(bank: Bank, strategy: Strategy, base: BaseDoc | None = None) -> tuple[str, tuple[str, ...]]:
    doc = base or BaseDoc(BASE_TEX.read_text())
    if not doc.bound:
        doc.bind(bank)
    used: list[str] = []
    parts = [doc.preamble, doc.header, doc.education, "\n\n"]
    parts.append("% Technical Skills\n\\section{Technical Skills}\n")
    parts.append("\\resumeSubHeadingListStart\n")
    labels = [lab for lab in strategy.skills_order if lab in doc.skill_lines]
    if not labels:
        labels = [lab for lab in doc.skill_lines if not lab.startswith("#")]
    for label in labels:
        parts.append("  " + doc.skill_lines[label] + "\n")
    parts.append("\\resumeSubHeadingListEnd\n\n")

    for title, project_ids in strategy.section_order:
        parts.append(f"% {title}\n\\section{{{title}}}\n")
        parts.append("\\resumeSubHeadingListStart\n\n")
        for pid in project_ids:
            project = bank.projects[pid]
            entry = doc.bound.get(pid)
            heading = _heading_only(entry) if entry else _heading_from_bank(project)
            parts.append(heading)
            parts.append("    \\resumeItemListStart\n")
            for cid in strategy.bullets.get(pid, ()):
                claim = _claim(bank, cid)
                used.append(cid)
                wording = claim.wording_for(strategy.family)
                wording = bold_known_tech(latex_escape(wording), project.technologies)
                parts.append(f"      \\item {wording}\n")
            parts.append("    \\resumeItemListEnd\n\n")
        parts.append("\\resumeSubHeadingListEnd\n\n")
    parts.append("\\end{document}\n")
    return "".join(parts), tuple(used)


def build_candidate(bank: Bank, strategy: Strategy, base: BaseDoc | None = None) -> Candidate:
    tex, used = render_tex(bank, strategy, base)
    return Candidate(name=strategy.name, strategy=strategy, tex=tex, used_claim_ids=used)


def dump_requirement_map(job: JobBrief) -> dict:
    return {
        "company": job.company,
        "title": job.title,
        "family": job.family,
        "source": job.source,
        "requirements": [
            {
                "id": r.id,
                "kind": r.kind,
                "text": r.text,
                "signals": list(r.signals),
                "tokens": list(r.tokens)[:20],
            }
            for r in job.requirements
        ],
    }


def dump_claim_map(matches: list[Match]) -> dict:
    return {
        "matches": [
            {
                "requirement_id": m.requirement_id,
                "claim_id": m.claim_id or None,
                "project_id": m.project_id or None,
                "strength": m.strength,
                "reason": m.reason,
            }
            for m in matches
        ]
    }


def strategy_markdown(job: JobBrief, strategy: Strategy, bank: Bank) -> str:
    lines = [
        f"# Strategy ({strategy.name})",
        "",
        f"Target family is {job.family} for {job.company} {job.title}.",
        "",
        strategy.narrative,
        "",
        "## Projects to include",
        "",
    ]
    for pid in strategy.include_projects:
        dims = ", ".join(strategy.dimensions.get(pid, ())) or "none listed"
        lines.append(f"- `{pid}` uses dimensions {dims}.")
        for cid in strategy.bullets.get(pid, ()):
            claim = _claim(bank, cid)
            lines.append(f"  - `{cid}` {claim.wording_for(strategy.family)}")
    lines.extend(["", "## Projects to exclude", ""])
    for pid in strategy.exclude_projects:
        lines.append(f"- `{pid}`")
    lines.extend(["", "## Skills order", ""])
    for label in strategy.skills_order:
        lines.append(f"- {label}")
    lines.append("")
    return "\n".join(lines)


def rejected_markdown(bank: Bank, strategy: Strategy, matches: list[Match]) -> str:
    lines = ["# Rejected claims", ""]
    used = {cid for ids in strategy.bullets.values() for cid in ids}
    for project in bank.projects.values():
        for claim in project.claims:
            if claim.id in used:
                continue
            if claim.verification_status == "forbidden":
                why = "forbidden by the evidence bank"
            elif claim.verification_status == "planned":
                why = "planned work, not completed"
            elif not claim.resume_eligible:
                why = "not resume-eligible"
            elif project.id not in strategy.include_projects:
                why = f"project `{project.id}` lost the one-page slot"
            else:
                why = "lower match score than the bullets that were kept"
            lines.append(f"- `{claim.id}` {why}. {claim.claim}")
    unmatched = [m for m in matches if m.strength == "unsupported"]
    if unmatched:
        lines.extend(["", "## Unsupported JD requirements", ""])
        for m in unmatched:
            lines.append(f"- `{m.requirement_id}` {m.reason}")
    lines.append("")
    return "\n".join(lines)


def interview_defense_markdown(bank: Bank, strategy: Strategy) -> str:
    lines = [
        "# Interview defense",
        "",
        "Each selected claim has likely follow-ups and the bank field that backs it.",
        "",
    ]
    for pid in strategy.include_projects:
        project = bank.projects[pid]
        lines.append(f"## {project.title}")
        lines.append("")
        if project.source_url:
            lines.append(f"Repo or demo: {project.source_url}")
            lines.append("")
        for cid in strategy.bullets.get(pid, ()):
            claim = _claim(bank, cid)
            lines.append(f"### `{claim.id}`")
            lines.append("")
            lines.append(claim.wording_for(strategy.family))
            lines.append("")
            lines.append(f"Evidence pointers: {', '.join(claim.evidence) or 'project record'}.")
            lines.append(f"Interview defensibility is {claim.interview_defensibility}.")
            lines.append("")
            lines.append("Likely follow-ups:")
            lines.append("")
            lines.append(f"- How did you build this, step by step, on {project.title}?")
            if claim.metrics:
                lines.append(
                    f"- Where did the figure {claim.metrics[0].raw} come from, and what would change it?"
                )
            else:
                lines.append("- What did you measure, and what did you refuse to invent?")
            lines.append("- What would you delete if an interviewer asked for the weakest part of this line?")
            lines.append("")
    return "\n".join(lines)
