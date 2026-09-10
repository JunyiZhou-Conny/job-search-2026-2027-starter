"""Extract a compact job brief. Heuristics only. No model call."""

from __future__ import annotations

import re
from pathlib import Path

from rqe.load import load_philosophy
from rqe.models import JobBrief, ReqKind, Requirement, RoleFamily

FAMILY_TITLE = (
    ("health_ai", ("health", "clinical", "pathology", "biomed", "digital health")),
    ("ml_ai", ("machine learning", "ml engineer", "applied ai", "ai engineer", "llm", "search ml", "ranking")),
    ("data", ("data scientist", "data engineer", "data science", "analyst", "etl")),
    ("swe", ("software engineer", "backend", "platform", "infrastructure", "sre", "full-stack", "full stack")),
)

KIND_HINTS: list[tuple[ReqKind, tuple[str, ...]]] = [
    ("required", ("required", "must have", "you have", "minimum", "qualifications")),
    ("preferred", ("preferred", "bonus", "nice to have", "plus", "you might")),
    ("responsibility", ("you will", "responsibilities", "what you", "your objectives", "you'll do")),
    ("stack", ("python", "sql", "java", "react", "aws", "pytorch", "spark")),
    ("seniority", ("years", "senior", "new grad", "intern", "bachelor", "master")),
    ("domain", ("finance", "invest", "clinical", "health", "search", "commerce")),
    ("engineering", ("architect", "scalable", "api", "deploy", "distributed", "reliability")),
    ("research", ("research", "experiment", "paper", "evaluation", "ablation")),
    ("product", ("customer", "viewer", "user", "product", "stakeholder")),
]

SIGNAL_WORDS = {
    "architecture": ("architect", "scalable", "schema"),
    "apis": ("api", "service", "endpoint"),
    "deployment": ("deploy", "ecs", "lambda", "production"),
    "distributed": ("distributed", "concurrent", "scale", "cluster"),
    "reliability": ("reliable", "fault", "robust"),
    "ownership": ("ownership", "end-to-end", "lead"),
    "model": ("model", "pytorch", "tensorflow", "jax"),
    "training": ("train", "fine-tun"),
    "evaluation": ("evaluat", "metric", "offline", "a/b"),
    "inference": ("inferen", "serving", "ranking", "retrieval"),
    "llm": ("llm", "rag", "language model"),
    "agents": ("agent",),
    "etl": ("clean", "acquire", "etl", "pipeline", "unstructured"),
    "analysis": ("analy", "insight", "thesis"),
    "experimentation": ("experiment", "test "),
    "statistics": ("statistic", "time-series", "regression"),
    "pipelines": ("pipeline", "workflow"),
    "data_scale": ("large", "million", "unstructured data"),
    "clinical": ("clinical", "health"),
    "product": ("customer", "viewer", "consumer"),
}

TECH = (
    "python",
    "sql",
    "excel",
    "pytorch",
    "tensorflow",
    "jax",
    "react",
    "typescript",
    "golang",
    "go",
    "java",
    "aws",
    "docker",
    "mongodb",
    "flask",
    "rag",
    "llm",
    "spark",
    "hadoop",
    "rust",
    "cuda",
    "triton",
    "dynamodb",
    "lambda",
    "sqs",
    "ecs",
)


def _slugify(company: str, title: str) -> str:
    raw = f"{company}-{title}".lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw[:80] or "job"


def _family(title: str, body: str) -> RoleFamily:
    blob = f"{title}\n{body}".lower()
    for family, needles in FAMILY_TITLE:
        if any(n in blob for n in needles):
            return family  # type: ignore[return-value]
    return "swe"


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9+#.]{2,}", text.lower())
    return [w for w in words if w not in {"the", "and", "for", "with", "you", "our", "this"}]


def _signals(text: str) -> list[str]:
    low = text.lower()
    hits = [name for name, needles in SIGNAL_WORDS.items() if any(n in low for n in needles)]
    return hits


def _kind(text: str, section: str) -> ReqKind:
    blob = f"{section} {text}".lower()
    for kind, needles in KIND_HINTS:
        if any(n in blob for n in needles):
            return kind
    return "responsibility"


def _frontmatter(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            block = text[3:end]
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"')
    for line in text.splitlines()[:20]:
        if line.lower().startswith("company:"):
            meta.setdefault("company", line.split(":", 1)[1].strip())
        if line.lower().startswith("title:") or line.lower().startswith("role:"):
            meta.setdefault("title", line.split(":", 1)[1].strip())
        if line.lower().startswith("source:"):
            meta.setdefault("source", line.split(":", 1)[1].strip())
    return meta


def _job_body(text: str) -> str:
    for marker in ("## Job text", "## Job description", "## Description"):
        idx = text.lower().find(marker.lower())
        if idx != -1:
            rest = text[idx + len(marker) :]
            nxt = re.search(r"\n## ", rest)
            return rest[1 : nxt.start()] if nxt else rest
    return text


def parse_jd(text: str, *, path: Path | None = None) -> JobBrief:
    philosophy = load_philosophy()
    known_signals = set(philosophy.get("signals") or [])
    meta = _frontmatter(text)
    company = meta.get("company") or "unknown"
    title = meta.get("title") or meta.get("role") or ""
    body = _job_body(text)
    if not title:
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = path.stem if path else "untitled"
    source = meta.get("source") or (str(path) if path else "inline")
    family = _family(title, body)

    section = ""
    reqs: list[Requirement] = []
    n = 0
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("---"):
            continue
        if re.match(r"^#{1,3} ", line) or line.endswith(":") and len(line) < 60:
            section = line.lstrip("#").rstrip(":").strip()
            continue
        if line.startswith("|") or line.startswith("<!--"):
            continue
        bullet = re.sub(r"^[-*•]\s+", "", line)
        if bullet == line and not re.match(r"^(you |required|preferred|bonus|qualif)", line.lower()):
            if len(line) > 160 or line.startswith("http"):
                continue
        n += 1
        tokens = _tokens(bullet)
        signals = [s for s in _signals(bullet) if s in known_signals or s in SIGNAL_WORDS]
        techs = tuple(t for t in TECH if t in bullet.lower())
        reqs.append(
            Requirement(
                id=f"r{n:02d}",
                text=bullet,
                kind=_kind(bullet, section),
                signals=tuple(dict.fromkeys(signals)),
                tokens=tuple(dict.fromkeys((*tokens, *techs))),
            )
        )

    if not reqs:
        n = 1
        reqs.append(
            Requirement(
                id="r01",
                text=title,
                kind="required",
                signals=(),
                tokens=tuple(_tokens(title)),
            )
        )

    slug = meta.get("slug") or _slugify(company, title)
    return JobBrief(
        slug=slug,
        company=company,
        title=title,
        source=source,
        family=family,
        raw_text=text,
        requirements=tuple(reqs),
    )


def parse_jd_file(path: Path) -> JobBrief:
    return parse_jd(path.read_text(), path=path)
