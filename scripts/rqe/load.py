from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from rqe.models import Bank, Claim, Confidence, Defensibility, Metric, Project, Verification

ROOT = Path(__file__).resolve().parents[2]
BANK_PATH = ROOT / "knowledge" / "evidence_bank.yaml"
PHILOSOPHY_PATH = ROOT / "knowledge" / "resume_philosophy.yaml"
CATALOG_PATH = ROOT / "knowledge" / "resume_claim_catalog.yaml"
PROFILE_PATH = ROOT / "config" / "profile.yaml"

ENTRY_KEYS = {
    "sseg_rlvr": "sseg_rlvr",
    "cellot_wyss": "wyss",
    "alphafold_pipeline": "alphafold",
    "compleg_uk_nz": "compleg",
    "autoresearch_cellot": "autoresearch",
    "airway_chatbot": "airway",
    "transformer_reimpl": "transformer",
    "vlm_textvqa_lora": "textvqa",
    "cv_caltech101": "caltech",
    "cv_segmentation_voc": "segmentation",
    "cv_pneumonia": "pneumonia",
    "mixhvg_py": "mixhvg",
    "job_search_os": "jobsearch",
}

SIGNAL_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("architecture", ("architect", "full-stack", "rest", "schema", "platform")),
    ("migration", ("port", "ported", "migrat", "cpu-only", "legacy")),
    ("apis", ("api", "rest", "cli", "endpoint")),
    ("reliability", ("checkpoint", "preempt", "fallback", "idempotent", "resume")),
    ("automation", ("automat", "loop", "harness", "batch", "schedul")),
    ("deployment", ("deploy", "beanstalk", "cloudfront", "docker")),
    ("distributed", ("slurm", "cluster", "hpc", "job array", "fairshare", "gpu node")),
    ("ownership", ("sole author", "scrum", "led an", "team of")),
    ("model", ("pytorch", "tensorflow", "transformer", "vae", "lora", "blip", "cellot", "alphafold")),
    ("training", ("train", "fine-tun", "lora", "grpo")),
    ("evaluation", ("bleu", "accuracy", "r^2", "r²", "miou", "leaderboard", "plddt", "metric")),
    ("ablations", ("ablat", "one-delta", "single-factor")),
    ("generalization", ("ood", "out-of-distribution", "held-out", "generalization")),
    ("inference", ("inferen", "serving", "alphafold")),
    ("llm", ("llm", "openai", "prompt", "rag", "blip", "opt-2.7")),
    ("agents", ("agent", "multi-turn", "planner", "director")),
    ("etl", ("etl", "scraper", "scrapers", "normalize", "extract")),
    ("analysis", ("analy", "diagnos", "investigat")),
    ("experimentation", ("experiment", "ablat", "split")),
    ("statistics", ("r^2", "r²", "statistic", "p-value", "regression")),
    ("pipelines", ("pipeline", "scanpy", "orchestr")),
    ("reproducibility", ("json", "frozen", "baseline", "reproduc")),
    ("data_scale", ("22,606", "338", "8,677", "57,000", "records", "images")),
    ("clinical", ("clinical", "hipaa", "clinician", "resident", "pathology", "chest")),
    ("translational", ("cross-species", "animal-to-human", "translation")),
    ("medical_ai", ("pathology", "pneumonia", "radiograph", "nuclei", "medical")),
]

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


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text()) or {}


def load_philosophy() -> dict[str, Any]:
    return load_yaml(PHILOSOPHY_PATH)


def _signals_from_text(text: str) -> list[str]:
    low = text.lower()
    hits: list[str] = []
    for signal, needles in SIGNAL_HINTS:
        if any(n in low for n in needles):
            hits.append(signal)
    return hits


def _families_from_signals(signals: list[str], philosophy: dict[str, Any]) -> list[str]:
    families: list[str] = []
    for name, spec in (philosophy.get("role_families") or {}).items():
        lead = set(spec.get("lead_signals") or [])
        if lead & set(signals):
            families.append(name)
    if not families:
        families = ["swe", "ml_ai", "data"]
    return families


def _metrics_from_text(text: str, source: str) -> list[Metric]:
    return [Metric(raw=m.group(0), source=source) for m in _NUM.finditer(text)]


def _parse_authored(project_id: str, raw: dict[str, Any]) -> Claim:
    wording = raw.get("allowed_wording") or {}
    if not isinstance(wording, dict):
        wording = {}
    metrics = tuple(
        Metric(str(m.get("raw", m) if isinstance(m, dict) else m), str(m.get("source", "authored") if isinstance(m, dict) else "authored"))
        for m in (raw.get("metrics") or [])
    )
    if not metrics:
        blob = " ".join([str(raw.get("claim") or ""), *wording.values()])
        metrics = tuple(_metrics_from_text(blob, f"{project_id}.{raw.get('id', 'claim')}"))
    status = raw.get("verification_status") or "verified"
    if status not in ("verified", "planned", "forbidden"):
        raise ValueError(f"{project_id}: bad verification_status {status!r}")
    conf = raw.get("confidence") or "high"
    if conf not in ("high", "medium", "low"):
        conf = "medium"
    defense = raw.get("interview_defensibility") or "moderate"
    if defense not in ("strong", "moderate", "weak"):
        defense = "moderate"
    return Claim(
        id=str(raw["id"]),
        project_id=project_id,
        claim=str(raw.get("claim") or "").strip(),
        evidence=tuple(str(x) for x in (raw.get("evidence") or [])),
        verification_status=status,
        confidence=conf,
        resume_eligible=bool(raw.get("resume_eligible", True)),
        interview_defensibility=defense,
        signals=tuple(str(x) for x in (raw.get("signals") or [])),
        relevant_role_families=tuple(str(x) for x in (raw.get("relevant_role_families") or [])),
        allowed_wording={str(k): str(v) for k, v in wording.items()},
        forbidden_claims=tuple(str(x) for x in (raw.get("forbidden_claims") or [])),
        metrics=metrics,
        notes=str(raw.get("notes") or ""),
    )


def _synth(
    project_id: str,
    i: int,
    text: str,
    status: Verification,
    eligible: bool,
    defense: Defensibility,
    confidence: Confidence,
    evidence: str,
    extra_forbidden: tuple[str, ...] = (),
    philosophy: dict[str, Any] | None = None,
) -> Claim:
    phil = philosophy or {}
    signals = _signals_from_text(text)
    return Claim(
        id=f"{project_id}.synth_{i}",
        project_id=project_id,
        claim=text.strip(),
        evidence=(evidence,),
        verification_status=status,
        confidence=confidence,
        resume_eligible=eligible,
        interview_defensibility=defense,
        signals=tuple(signals),
        relevant_role_families=tuple(_families_from_signals(signals, phil)),
        allowed_wording={"default": text.strip()},
        forbidden_claims=extra_forbidden,
        metrics=tuple(_metrics_from_text(text, evidence)),
        notes="synthesized from evidence_bank fields",
    )


def _norm_fact(text: str) -> str:
    return (
        text.lower()
        .replace("–", "-")
        .replace("—", "-")
        .replace("×", "x")
        .replace(",", "")
    )


def evidence_text(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("text") or item.get("claim") or "")
    return str(item)


def evidence_resume_ok(item: Any) -> bool:
    if isinstance(item, dict) and "resume_ok" in item:
        return bool(item.get("resume_ok"))
    return True


def fact_texts(body: dict[str, Any]) -> list[str]:
    parts = [
        str(body.get("title") or ""),
        str(body.get("org") or ""),
        str(body.get("role") or ""),
        str(body.get("dates") or ""),
    ]
    for field in (
        "software_engineering_evidence",
        "measurable_results",
        "verified_now",
        "research_evidence",
        "technologies",
    ):
        for item in body.get(field) or []:
            parts.append(evidence_text(item))
    return [p for p in parts if p]


def fact_blob(body: dict[str, Any]) -> str:
    return _norm_fact(" ".join(fact_texts(body)))


def _number_cores(text: str) -> set[str]:
    cores: set[str] = set()
    for m in _NUM.finditer(text):
        core = re.sub(r"[^0-9.]", "", m.group(0).replace(",", ""))
        if core:
            cores.add(core)
    return cores


def assert_catalog_grounded(raw: dict[str, Any], body: dict[str, Any]) -> None:
    allowed = _number_cores(" ".join(fact_texts(body)))
    wording = raw.get("allowed_wording") or {}
    if not isinstance(wording, dict):
        wording = {}
    text = " ".join([str(raw.get("claim") or ""), *wording.values()])
    cid = raw.get("id")
    for core in _number_cores(text):
        if core in allowed:
            continue
        whole = fact_blob(body).replace(" ", "")
        if core.isdigit() and f"{core}k" in whole:
            continue
        raise ValueError(f"catalog {cid} invents number {core!r}")


def load_catalog() -> dict[str, list[dict[str, Any]]]:
    if not CATALOG_PATH.is_file():
        return {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for raw in load_yaml(CATALOG_PATH).get("claims") or []:
        if not isinstance(raw, dict) or not raw.get("project_id"):
            continue
        grouped.setdefault(str(raw["project_id"]), []).append(raw)
    return grouped


def _project_claims(project_id: str, body: dict[str, Any], philosophy: dict[str, Any]) -> list[Claim]:
    claims: list[Claim] = []
    authored = body.get("claims") or []
    if authored:
        for raw in authored:
            claims.append(_parse_authored(project_id, raw))
    else:
        n = 0
        defense: Defensibility = "moderate"
        depth = str(body.get("interview_depth") or "moderate")
        if depth in ("strong", "moderate", "weak"):
            defense = depth
        for field in ("software_engineering_evidence", "measurable_results", "verified_now"):
            for item in body.get(field) or []:
                text = evidence_text(item)
                if not text:
                    continue
                n += 1
                claims.append(
                    _synth(
                        project_id,
                        n,
                        text,
                        "verified",
                        evidence_resume_ok(item),
                        defense,
                        "high" if field != "verified_now" else "medium",
                        f"{project_id}.{field}",
                        philosophy=philosophy,
                    )
                )
    n = 1000
    for item in body.get("not_yet_built") or []:
        n += 1
        claims.append(
            _synth(
                project_id,
                n,
                str(item),
                "planned",
                False,
                "weak",
                "high",
                f"{project_id}.not_yet_built",
                philosophy=philosophy,
            )
        )
    for item in body.get("do_not") or []:
        n += 1
        claims.append(
            _synth(
                project_id,
                n,
                str(item),
                "forbidden",
                False,
                "weak",
                "high",
                f"{project_id}.do_not",
                extra_forbidden=(str(item),),
                philosophy=philosophy,
            )
        )
    return claims


def load_bank() -> Bank:
    raw = load_yaml(BANK_PATH)
    philosophy = load_philosophy()
    profile = load_yaml(PROFILE_PATH)
    projects: dict[str, Project] = {}
    number_blobs: list[str] = []
    catalog = load_catalog()
    for pid, body in (raw.get("projects") or {}).items():
        if not isinstance(body, dict):
            continue
        authored = catalog.get(pid) or []
        if authored:
            for item in authored:
                assert_catalog_grounded(item, body)
            body = dict(body)
            body["claims"] = authored
        claims = tuple(_project_claims(pid, body, philosophy))
        techs = tuple(str(t) for t in (body.get("technologies") or []))
        for c in claims:
            number_blobs.append(c.claim)
            number_blobs.extend(c.allowed_wording.values())
            number_blobs.extend(m.raw for m in c.metrics)
        for field in ("measurable_results", "verified_now", "software_engineering_evidence"):
            for item in body.get(field) or []:
                number_blobs.append(str(item))
        projects[pid] = Project(
            id=pid,
            title=str(body.get("title") or pid),
            org=str(body.get("org") or ""),
            role=str(body.get("role") or ""),
            dates=str(body.get("dates") or ""),
            source_url=str(body.get("source_url") or ""),
            technologies=techs,
            claims=claims,
            entry_key=ENTRY_KEYS.get(pid, ""),
        )

    skill_tokens: dict[str, bool] = {}
    for key, body in (raw.get("skills") or {}).items():
        if not isinstance(body, dict):
            continue
        name = str(body.get("name") or key).lower()
        ok = bool(body.get("verified")) and bool(body.get("resume_eligible"))
        skill_tokens[name] = ok
        skill_tokens[str(key).lower()] = ok

    forbidden = [t.lower() for t in (philosophy.get("global_forbidden_tokens") or [])]
    for name, ok in skill_tokens.items():
        if not ok:
            forbidden.append(name)

    profile_blobs = [
        str(profile.get("legal_name") or ""),
        str(profile.get("degree") or ""),
        str(profile.get("school") or ""),
        str((profile.get("education_history") or [{}])[0].get("gpa") or ""),
        "3.925",
        "2026",
        "2027",
        "2025",
        "2024",
        "2023",
    ]
    for cert in profile.get("certifications") or []:
        profile_blobs.append(str(cert))

    return Bank(
        projects=projects,
        skill_tokens=skill_tokens,
        forbidden_tokens=tuple(dict.fromkeys(forbidden)),
        allowed_number_blobs=tuple(number_blobs),
        profile_blobs=tuple(profile_blobs),
    )


def all_usable_claims(bank: Bank) -> list[Claim]:
    out: list[Claim] = []
    for project in bank.projects.values():
        for claim in project.claims:
            if claim.usable_on_resume:
                out.append(claim)
    return out


def claim_by_id(bank: Bank, claim_id: str) -> Claim | None:
    for project in bank.projects.values():
        for claim in project.claims:
            if claim.id == claim_id:
                return claim
    return None
