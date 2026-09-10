"""Match requirements to claims, then pick a resume strategy."""

from __future__ import annotations

from collections import defaultdict

from rqe.load import all_usable_claims, load_philosophy
from rqe.models import (
    Bank,
    JobBrief,
    Match,
    MatchStrength,
    Requirement,
    Strategy,
    StrategyName,
)

STRENGTH_POINTS = {
    "strong_direct": 4,
    "transferable": 2,
    "weak_adjacent": 1,
    "unsupported": 0,
}

STOPWORDS = {
    "and",
    "for",
    "the",
    "with",
    "you",
    "our",
    "this",
    "that",
    "from",
    "into",
    "over",
    "than",
    "then",
    "have",
    "has",
    "was",
    "were",
    "are",
    "not",
    "but",
    "plus",
    "will",
    "can",
    "may",
    "each",
    "only",
    "also",
    "using",
    "used",
    "use",
    "via",
    "per",
    "on",
    "in",
    "to",
    "of",
    "or",
    "as",
    "at",
    "by",
    "is",
    "be",
    "it",
    "its",
    "your",
    "their",
    "them",
    "must",
    "required",
}

SPECIFIC_TECH = {
    "cuda",
    "triton",
    "kubernetes",
    "k8s",
    "pinecone",
    "golang",
    "rust",
    "jax",
    "dynamodb",
    "sqs",
}

SKILL_LABELS = (
    "Languages",
    "ML \\& Deep Learning",
    "LLM \\& Applied AI",
    "Backend \\& DevOps",
    "Data \\& Compute",
    "Cloud",
    "Certifications",
)

FAMILY_SKILLS = {
    "swe": (
        "Languages",
        "Backend \\& DevOps",
        "Cloud",
        "Data \\& Compute",
        "LLM \\& Applied AI",
        "ML \\& Deep Learning",
        "Certifications",
    ),
    "ml_ai": (
        "Languages",
        "ML \\& Deep Learning",
        "LLM \\& Applied AI",
        "Data \\& Compute",
        "Backend \\& DevOps",
        "Cloud",
        "Certifications",
    ),
    "data": (
        "Languages",
        "Data \\& Compute",
        "ML \\& Deep Learning",
        "Cloud",
        "Backend \\& DevOps",
        "LLM \\& Applied AI",
        "Certifications",
    ),
    "health_ai": (
        "Languages",
        "ML \\& Deep Learning",
        "LLM \\& Applied AI",
        "Data \\& Compute",
        "Cloud",
        "Backend \\& DevOps",
        "Certifications",
    ),
}


def _norm_tokens(text: str) -> set[str]:
    return {
        t
        for t in text.lower().replace("/", " ").replace("-", " ").split()
        if len(t) > 2 and t not in STOPWORDS
    }


def classify(req: Requirement, claim: Claim, project_techs: tuple[str, ...]) -> Match | None:
    req_tokens = {t for t in (set(req.tokens) | _norm_tokens(req.text)) if t not in STOPWORDS}
    claim_tokens = _norm_tokens(claim.claim)
    for wording in claim.allowed_wording.values():
        claim_tokens |= _norm_tokens(wording)
    tech_tokens = {t.lower() for t in project_techs}
    for part in project_techs:
        claim_tokens |= _norm_tokens(part)
    claim_lex = claim_tokens | tech_tokens

    missing_specific = {t for t in (req_tokens & SPECIFIC_TECH) if t not in claim_lex}
    if missing_specific:
        return None

    overlap = req_tokens & claim_lex
    signal_overlap = set(req.signals) & set(claim.signals)

    score = 2 * len(overlap) + 3 * len(signal_overlap)
    strength: MatchStrength
    reason: str
    if len(overlap) >= 2 or (len(overlap) >= 1 and signal_overlap):
        strength = "strong_direct"
        reason = f"shared tokens {sorted(overlap)[:6]} signals {sorted(signal_overlap)}"
        score += 4
    elif overlap or signal_overlap:
        strength = "transferable"
        reason = f"partial tokens {sorted(overlap)[:6]} signals {sorted(signal_overlap)}"
        score += 2
    else:
        return None
    return Match(
        requirement_id=req.id,
        claim_id=claim.id,
        project_id=claim.project_id,
        strength=strength,
        reason=reason,
        score=score,
    )


def match_job(bank: Bank, job: JobBrief) -> list[Match]:
    matches: list[Match] = []
    usable = all_usable_claims(bank)
    covered: set[str] = set()
    for req in job.requirements:
        best_for_req: list[Match] = []
        for claim in usable:
            project = bank.projects[claim.project_id]
            hit = classify(req, claim, project.technologies)
            if hit is None:
                # weak family adjacency
                if job.family in claim.relevant_role_families and req.kind in {
                    "required",
                    "preferred",
                    "responsibility",
                    "stack",
                }:
                    hit = Match(
                        requirement_id=req.id,
                        claim_id=claim.id,
                        project_id=claim.project_id,
                        strength="weak_adjacent",
                        reason=f"same family {job.family}",
                        score=1,
                    )
                else:
                    continue
            best_for_req.append(hit)
        best_for_req.sort(key=lambda m: m.score, reverse=True)
        for hit in best_for_req[:3]:
            matches.append(hit)
            covered.add(req.id)
        if not best_for_req:
            matches.append(
                Match(
                    requirement_id=req.id,
                    claim_id="",
                    project_id="",
                    strength="unsupported",
                    reason="no usable claim overlapped this requirement",
                    score=0,
                )
            )
    return matches


def project_scores(matches: list[Match]) -> dict[str, int]:
    scores: dict[str, int] = defaultdict(int)
    for m in matches:
        if m.project_id:
            scores[m.project_id] += STRENGTH_POINTS[m.strength]
    return dict(scores)


def _rank_claims_for_project(
    bank: Bank,
    project_id: str,
    matches: list[Match],
    family: str,
    strategy: StrategyName,
) -> list[str]:
    project = bank.projects[project_id]
    claim_score: dict[str, int] = defaultdict(int)
    for m in matches:
        if m.project_id == project_id and m.claim_id:
            claim_score[m.claim_id] += m.score
    ranked: list[tuple[int, str]] = []
    for claim in project.claims:
        if not claim.usable_on_resume:
            continue
        if family not in claim.relevant_role_families and claim.relevant_role_families:
            # still allow if it matched
            if claim.id not in claim_score:
                continue
        score = claim_score.get(claim.id, 0)
        if strategy == "impact":
            score += 2 * len(claim.metrics)
        elif strategy == "hiring_manager":
            if claim.interview_defensibility == "strong":
                score += 3
            score += 1 if "architecture" in claim.signals or "ownership" in claim.signals else 0
        elif strategy == "recruiter":
            score += 1 if family in claim.relevant_role_families else 0
        elif strategy == "narrative":
            score += 1 if family in claim.relevant_role_families else 0
            if claim.interview_defensibility == "strong":
                score += 1
        ranked.append((score, claim.id))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return [cid for _, cid in ranked]


def build_strategy(
    bank: Bank,
    job: JobBrief,
    matches: list[Match],
    name: StrategyName,
) -> Strategy:
    philosophy = load_philosophy()
    family_spec = (philosophy.get("role_families") or {}).get(job.family) or {}
    max_projects = int(philosophy.get("max_projects") or 4)
    max_bullets = int(philosophy.get("max_bullets_per_project") or 3)
    scores = project_scores(matches)

    # sseg_rlvr stays off swe/data one-pagers unless the JD is health/RL.
    hidden = set()
    jd_blob = f"{job.title}\n{job.raw_text}".lower()
    if job.family in {"swe", "data"} and "reinforcement" not in jd_blob and "pathology" not in jd_blob:
        hidden.add("sseg_rlvr")

    fallback_order = {
        "swe": [
            "airway_chatbot",
            "job_search_os",
            "mixhvg_py",
            "compleg_uk_nz",
            "autoresearch_cellot",
            "alphafold_pipeline",
        ],
        "ml_ai": [
            "vlm_textvqa_lora",
            "autoresearch_cellot",
            "cellot_wyss",
            "airway_chatbot",
            "transformer_reimpl",
        ],
        "data": [
            "compleg_uk_nz",
            "mixhvg_py",
            "autoresearch_cellot",
            "cellot_wyss",
            "alphafold_pipeline",
        ],
        "health_ai": [
            "sseg_rlvr",
            "cv_pneumonia",
            "airway_chatbot",
            "cellot_wyss",
            "vlm_textvqa_lora",
        ],
    }
    prior = fallback_order.get(job.family, [])
    for i, pid in enumerate(prior):
        if pid in hidden:
            continue
        scores[pid] = scores.get(pid, 0) + max(2, 20 - 3 * i)

    ranked_projects = sorted(
        (pid for pid in scores if pid not in hidden and pid in bank.projects),
        key=lambda p: (-scores[p], p),
    )

    if name == "narrative":
        # Prefer one coherent pair (systems+data or ml+eval) over a grab bag.
        prefer = fallback_order.get(job.family, [])
        ranked_projects = [p for p in prefer if p in ranked_projects] + [
            p for p in ranked_projects if p not in prefer
        ]

    include = tuple(p for p in ranked_projects if p in bank.projects)[:max_projects]
    if job.family == "data" and "compleg_uk_nz" in include:
        include = ("compleg_uk_nz",) + tuple(p for p in include if p != "compleg_uk_nz")
    exclude = tuple(pid for pid in bank.projects if pid not in include)

    bullets: dict[str, tuple[str, ...]] = {}
    dimensions: dict[str, tuple[str, ...]] = {}
    for pid in include:
        claim_ids = _rank_claims_for_project(bank, pid, matches, job.family, name)[:max_bullets]
        if not claim_ids:
            # last resort: first usable claims
            claim_ids = [c.id for c in bank.projects[pid].claims if c.usable_on_resume][:max_bullets]
        bullets[pid] = tuple(claim_ids)
        dims: list[str] = []
        for cid in claim_ids:
            for c in bank.projects[pid].claims:
                if c.id == cid:
                    dims.extend(c.signals)
        dimensions[pid] = tuple(dict.fromkeys(dims))

    titles = list(family_spec.get("section_titles") or ["Experience", "Additional Experience"])
    if len(include) <= 2:
        sections = ((titles[0], include),)
    else:
        mid = 2
        sections = (
            (titles[0], include[:mid]),
            (titles[1] if len(titles) > 1 else "Additional Experience", include[mid:]),
        )

    narrative = str(family_spec.get("narrative") or f"{job.family} candidate")
    if name == "hiring_manager":
        narrative = narrative + ". Emphasize ownership and systems decisions."
    elif name == "impact":
        narrative = narrative + ". Lead with measured results."
    elif name == "recruiter":
        narrative = narrative + ". Front-load phrases the posting uses when they are true."
    elif name == "narrative":
        narrative = narrative + ". Keep one coherent story across entries."

    return Strategy(
        name=name,
        family=job.family,
        narrative=narrative,
        include_projects=include,
        exclude_projects=exclude,
        section_order=sections,
        bullets=bullets,
        skills_order=FAMILY_SKILLS.get(job.family, SKILL_LABELS),
        dimensions=dimensions,
    )


def all_strategies(bank: Bank, job: JobBrief, matches: list[Match]) -> list[Strategy]:
    names: tuple[StrategyName, ...] = ("recruiter", "hiring_manager", "impact", "narrative")
    return [build_strategy(bank, job, matches, name) for name in names]
