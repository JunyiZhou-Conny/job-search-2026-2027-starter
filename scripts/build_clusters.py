#!/usr/bin/env python3
"""Generate cluster resumes from resumes/base/JZ_resume.tex.

Clusters are the base document with entries selected, regrouped, and reordered --
never rewritten. That keeps one source of truth for wording and metrics, so a
correction made in base propagates everywhere instead of drifting.

    python3 scripts/build_clusters.py            # write all clusters
    python3 scripts/build_clusters.py data_ml    # write one
    python3 scripts/build_clusters.py --list     # show parsed entry ids
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "resumes" / "base" / "JZ_resume.tex"
VERSION = "v1.3"
DATE = "2026-08-24"

# Short id -> distinctive substring of the entry title in base.
ENTRY_KEYS = {
    "sseg_rlvr": "Structure-Verified RLVR",
    "wyss": "Cross-Species Drug Translation",
    "alphafold": "AlphaFold Protein",
    "compleg": "Computational Legislative Studies",
    "autoresearch": "Autonomous Ablation-Search Agent",
    "airway": "Airway Management Simulation Chatbot",
    "transformer": "Reimplementation of Transformer",
    "textvqa": "Parameter-Efficient Fine-Tuning of BLIP-2",
    "caltech": "Image Classification Benchmark",
    "segmentation": "Semantic Segmentation Benchmark",
    "pneumonia": "Pneumonia Detection",
}

# Skills lines are reordered per cluster so the most relevant appear first.
# Labels must match the \resumeItem{<label>} text in base exactly.
ALL_SKILLS = [
    "Languages",
    "ML \\& Deep Learning",
    "LLM \\& Applied AI",
    "Backend \\& DevOps",
    "Data \\& Compute",
    "Cloud",
    "Certifications",
]

CLUSTERS = {
    "cloud_swe": {
        "slug": "cloud-swe",
        "skills": [
            "Languages",
            "Backend \\& DevOps",
            "Cloud",
            "Data \\& Compute",
            "LLM \\& Applied AI",
            "ML \\& Deep Learning",
            "Certifications",
        ],
        "sections": [
            ("Engineering Projects", ["autoresearch", "airway"]),
            ("Research Experience", ["alphafold", "wyss"]),
        ],
    },
    "data_ml": {
        "slug": "data-ml",
        "skills": [
            "Languages",
            "ML \\& Deep Learning",
            "LLM \\& Applied AI",
            "Data \\& Compute",
            "Backend \\& DevOps",
            "Cloud",
            "Certifications",
        ],
        "sections": [
            ("Machine Learning Projects", ["textvqa", "airway"]),
            ("Research Experience", ["wyss", "autoresearch"]),
        ],
    },
    "health_ai": {
        "slug": "health-ai",
        "skills": [
            "Languages",
            "ML \\& Deep Learning",
            "LLM \\& Applied AI",
            "Data \\& Compute",
            "Cloud",
            "Backend \\& DevOps",
            "Certifications",
        ],
        "sections": [
            ("Clinical AI Experience", ["sseg_rlvr", "airway"]),
            ("Machine Learning Projects", ["pneumonia", "wyss"]),
        ],
    },
}


class Base:
    """Parsed view of the base resume."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.preamble, self.header = self._split_head()
        self.education = self._section("Education")
        self.skill_lines = self._skill_lines()
        self.entries = self._entries()

    def _split_head(self) -> tuple[str, str]:
        start = self.text.index("\\begin{document}") + len("\\begin{document}")
        end = self.text.index("% Education")
        return self.text[:start], self.text[start:end]

    def _section(self, name: str) -> str:
        start = self.text.index(f"\\section{{{name}}}")
        end = self.text.index("\\resumeSubHeadingListEnd", start) + len(
            "\\resumeSubHeadingListEnd"
        )
        return self.text[start:end]

    def _skill_lines(self) -> dict[str, str]:
        block = self._section("Technical Skills")
        lines = {}
        for raw in block.splitlines():
            m = re.match(r"\s*\\resumeItem\{(.+?)\}\{", raw)
            if m:
                lines[m.group(1)] = raw.strip()
        return lines

    def _entries(self) -> dict[str, str]:
        # Everything from the first project section onward.
        body = self.text[self.text.index("% Research Experience") :]
        chunks = re.split(r"(?=  \\resumeSubheading)", body)
        found: dict[str, str] = {}
        for chunk in chunks:
            if "\\resumeSubheading" not in chunk:
                continue
            # Trim trailing section scaffolding that belongs to the next block.
            for marker in ("\\resumeSubHeadingListEnd", "\\end{document}"):
                if marker in chunk:
                    chunk = chunk[: chunk.index(marker)]
            entry = chunk.rstrip() + "\n"
            for key, needle in ENTRY_KEYS.items():
                if needle in entry:
                    found[key] = entry
                    break
        return found


def render(base: Base, name: str, spec: dict) -> str:
    parts = [base.preamble, base.header, base.education, "\n\n"]

    parts.append("% Technical Skills\n\\section{Technical Skills}\n")
    parts.append("\\resumeSubHeadingListStart\n")
    for label in spec.get("skills", ALL_SKILLS):
        line = base.skill_lines.get(label)
        if line is None:
            raise SystemExit(f"{name}: no skills line labelled {label!r} in base")
        parts.append("  " + line + "\n")
    parts.append("\\resumeSubHeadingListEnd\n\n")

    for title, ids in spec["sections"]:
        parts.append(f"% {title}\n\\section{{{title}}}\n")
        parts.append("\\resumeSubHeadingListStart\n\n")
        for eid in ids:
            if eid not in base.entries:
                raise SystemExit(f"{name}: entry id {eid!r} not found in base")
            parts.append(base.entries[eid] + "\n")
        parts.append("\\resumeSubHeadingListEnd\n\n")

    parts.append("\\end{document}\n")
    return "".join(parts)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    base = Base(BASE.read_text())

    if "--list" in sys.argv:
        print(f"parsed {len(base.entries)} entries from {BASE.relative_to(ROOT)}:")
        for eid in base.entries:
            print(f"  {eid}")
        print(f"\nskills lines: {', '.join(base.skill_lines)}")
        return

    targets = args or list(CLUSTERS)
    for name in targets:
        if name not in CLUSTERS:
            raise SystemExit(f"unknown cluster {name!r}; choose from {list(CLUSTERS)}")
        spec = CLUSTERS[name]
        out = ROOT / "resumes" / name / f"{DATE}_{spec['slug']}_{VERSION}.tex"
        out.write_text(render(base, name, spec))
        n = sum(len(ids) for _, ids in spec["sections"])
        print(f"wrote {out.relative_to(ROOT)}  ({n} entries)")


if __name__ == "__main__":
    main()
