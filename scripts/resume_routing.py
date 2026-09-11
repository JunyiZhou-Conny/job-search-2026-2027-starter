#!/usr/bin/env python3
"""Deterministic resume family router. No network. No model."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "knowledge" / "resume_routing.yaml"
PHILOSOPHY_PATH = ROOT / "knowledge" / "resume_philosophy.yaml"
REGISTRY_PATH = ROOT / "data" / "resume_versions.csv"

Family = Literal["swe", "ml_ai", "ai_infra", "health_ai", "REVIEW"]
Confidence = Literal["high", "medium", "review"]
PRODUCTION = ("swe", "ml_ai", "ai_infra", "health_ai")

_PUNCT = re.compile(r"[^a-z0-9]+")
_ACTIVE = frozenset({"true", "1", "yes"})
_POLICY: dict[str, Any] | None = None


def normalize(text: str) -> str:
    return " ".join(_PUNCT.sub(" ", (text or "").lower()).split())


def has_phrase(haystack: str, phrase: str) -> bool:
    needle = normalize(phrase)
    if not needle or not haystack:
        return False
    return f" {needle} " in f" {haystack} "


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping")
    return data


def load_policy(path: Path = POLICY_PATH, *, reload: bool = False) -> dict[str, Any]:
    global _POLICY
    if _POLICY is not None and path == POLICY_PATH and not reload:
        return _POLICY
    policy = load_yaml(path)
    families = tuple(policy.get("production_families") or ())
    if tuple(families) != PRODUCTION:
        raise ValueError(f"production_families must be {PRODUCTION}, got {families}")
    if PHILOSOPHY_PATH.is_file():
        philosophy = load_yaml(PHILOSOPHY_PATH)
        known = {
            name
            for name, body in (philosophy.get("role_families") or {}).items()
            if isinstance(body, dict) and body.get("production")
        }
        if known and not set(PRODUCTION) <= known:
            raise ValueError(f"routing families {PRODUCTION} are not all production in resume_philosophy.yaml")
    if path == POLICY_PATH:
        _POLICY = policy
    return policy


@dataclass(frozen=True)
class JobMeta:
    role: str = ""
    company: str = ""
    source: str = ""
    board_category: str = ""
    track: str = ""
    location: str = ""
    short_text: str = ""
    legacy_cluster: str = ""

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "JobMeta":
        def g(*names: str) -> str:
            for name in names:
                value = raw.get(name)
                if value is not None and str(value).strip():
                    return str(value).strip()
            return ""

        return cls(
            role=g("role", "title"),
            company=g("company"),
            source=g("source"),
            board_category=g("board_category", "category"),
            track=g("track"),
            location=g("location"),
            short_text=g("short_text", "notes"),
            legacy_cluster=g("legacy_cluster", "resume_cluster", "suggested_cluster"),
        )


@dataclass(frozen=True)
class RouteDecision:
    family: Family
    confidence: Confidence
    matched_rules: tuple[str, ...]
    reason: str
    legacy_cluster: str = ""
    scores: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "confidence": self.confidence,
            "matched_rules": list(self.matched_rules),
            "reason": self.reason,
            "legacy_cluster": self.legacy_cluster,
            "scores": dict(self.scores),
        }


@dataclass(frozen=True)
class VariantResolution:
    family: Family
    variant: str
    reason: str
    file_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "resume_variant": self.variant,
            "variant_reason": self.reason,
            "file_path": self.file_path,
        }


def _phrases(item: Mapping[str, Any]) -> list[str]:
    raw = item.get("phrases") or []
    return [str(p) for p in raw if str(p).strip()]


def _blob(job: JobMeta) -> str:
    return normalize(" ".join(part for part in (job.role, job.company, job.short_text) if part))


def _title(job: JobMeta) -> str:
    return normalize(job.role)


def _company(job: JobMeta) -> str:
    return normalize(job.company)


def suggest_legacy_cluster(job: JobMeta, policy: Optional[Mapping[str, Any]] = None) -> str:
    spec = policy if policy is not None else load_policy()
    title = _title(job)
    families = spec.get("legacy_title_families") or {}
    hits: list[str] = []
    for name, phrases in families.items():
        if any(has_phrase(title, str(p)) for p in phrases or []):
            hits.append(str(name))
    if len(hits) == 1:
        return hits[0]
    if job.legacy_cluster:
        return job.legacy_cluster
    return ""


def _has_any(text: str, phrases: Iterable[str]) -> bool:
    return any(has_phrase(text, p) for p in phrases)


def _gpu_blocked(title: str, policy: Mapping[str, Any]) -> bool:
    if not policy.get("gpu_requires_ai"):
        return False
    if not has_phrase(title, "gpu"):
        return False
    ai_tokens = ("ai", "ml", "llm", "inference", "training", "machine learning")
    return not _has_any(title, ai_tokens)


_GENERIC_ML_EXCLUSIVE = frozenset({"ml_ai.mle", "ml_ai.modeling"})
_INFRA_EXCLUSIVE = frozenset(
    {
        "ai_infra.ai_infrastructure",
        "ai_infra.inference_role",
        "ai_infra.ai_platform",
    }
)


def _prefer_infra_over_generic_ml(exclusive: dict[str, list[str]]) -> dict[str, list[str]]:
    infra = exclusive.get("ai_infra") or []
    ml = exclusive.get("ml_ai") or []
    if infra and ml and any(item in _INFRA_EXCLUSIVE for item in infra):
        kept = [item for item in ml if item not in _GENERIC_ML_EXCLUSIVE]
        if kept:
            exclusive = dict(exclusive)
            exclusive["ml_ai"] = kept
        else:
            exclusive = {k: v for k, v in exclusive.items() if k != "ml_ai"}
    return exclusive


def _exclusive_hits(title: str, policy: Mapping[str, Any]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {name: [] for name in PRODUCTION}
    for item in policy.get("exclusive_patterns") or []:
        if not isinstance(item, dict):
            continue
        family = str(item.get("family") or "")
        ident = str(item.get("id") or family)
        if family not in hits:
            continue
        if _has_any(title, _phrases(item)):
            hits[family].append(ident)
    if _gpu_blocked(title, policy):
        hits["ai_infra"] = [rid for rid in hits["ai_infra"] if "gpu" not in rid]
    return {k: v for k, v in hits.items() if v}


def _score_signals(title: str, blob: str, policy: Mapping[str, Any]) -> tuple[dict[str, int], list[str]]:
    scores = {name: 0 for name in PRODUCTION}
    rules: list[str] = []
    for item in policy.get("signals") or []:
        if not isinstance(item, dict):
            continue
        family = str(item.get("family") or "")
        if family not in scores:
            continue
        ident = str(item.get("id") or family)
        weight = int(item.get("weight") or 0)
        phrases = _phrases(item)
        if not phrases or weight <= 0:
            continue
        surface = title if family == "health_ai" else blob
        if _has_any(title, phrases) or (family != "health_ai" and _has_any(surface, phrases)):
            if family == "ai_infra" and _gpu_blocked(title, policy):
                non_gpu = [p for p in phrases if normalize(p) != "gpu"]
                if not _has_any(title, non_gpu) and not _has_any(blob, non_gpu):
                    continue
            scores[family] += weight
            rules.append(ident)
    return scores, rules


def _data_overlay(title: str, scores: dict[str, int], policy: Mapping[str, Any]) -> tuple[Optional[Family], list[str]]:
    data = policy.get("data_jobs") or {}
    toward_ml = [str(p) for p in data.get("toward_ml_ai") or []]
    toward_swe = [str(p) for p in data.get("toward_swe") or []]
    review = [str(p) for p in data.get("review") or []]
    rules: list[str] = []
    if _has_any(title, review) and _has_any(title, toward_ml) and _has_any(title, toward_swe):
        return "REVIEW", ["data.mixed_review"]
    if _has_any(title, review) and not _has_any(title, toward_ml) and not _has_any(title, toward_swe):
        if not any(scores[name] >= 4 for name in ("ml_ai", "ai_infra", "health_ai", "swe")):
            return "REVIEW", ["data.analyst_review"]
        rules.append("data.analyst_weak")
    if _has_any(title, toward_swe) and not _has_any(title, toward_ml):
        scores["swe"] += 4
        rules.append("data.toward_swe")
    elif _has_any(title, toward_ml) and not _has_any(title, toward_swe):
        scores["ml_ai"] += 4
        rules.append("data.toward_ml_ai")
    return None, rules


def _health_overlay(job: JobMeta, scores: dict[str, int], policy: Mapping[str, Any]) -> list[str]:
    health = policy.get("health") or {}
    domain = [str(p) for p in health.get("domain_phrases") or []]
    modeling = [str(p) for p in health.get("modeling_phrases") or []]
    title = _title(job)
    blob = normalize(f"{job.role} {job.company}")
    has_domain = _has_any(blob, domain)
    has_model = _has_any(title, modeling)
    rules: list[str] = []
    if has_domain and has_model:
        scores["health_ai"] += max(6, int(scores.get("ml_ai") or 0) + 2)
        rules.append("health.domain_and_modeling")
        return rules
    if has_domain and not has_model:
        rules.append("health.company_or_domain_only")
    return rules


def _board_prior(job: JobMeta, scores: dict[str, int], policy: Mapping[str, Any]) -> list[str]:
    priors = policy.get("board_category_prior") or {}
    category = normalize(job.board_category or job.source)
    rules: list[str] = []
    for slug, body in priors.items():
        if not isinstance(body, dict):
            continue
        if normalize(str(slug)) not in category.split() and normalize(str(slug)) != category:
            continue
        family = str(body.get("family") or "")
        weight = int(body.get("weight") or 0)
        if family == "REVIEW" or weight <= 0:
            rules.append(f"board.{slug}.ignored")
            continue
        if family in scores and scores[family] > 0:
            scores[family] += weight
            rules.append(f"board.{slug}")
        else:
            rules.append(f"board.{slug}.no_prior_without_signal")
    return rules


def _decide(
    scores: dict[str, int],
    exclusive: Mapping[str, Sequence[str]],
    forced: Optional[Family],
    policy: Mapping[str, Any],
) -> tuple[Family, Confidence, str]:
    if forced == "REVIEW":
        return "REVIEW", "review", "data or mixed title is unresolved"
    thresholds = policy.get("thresholds") or {}
    min_score = int(thresholds.get("min_score") or 3)
    min_lead = int(thresholds.get("min_lead") or 2)
    high_lead = int(thresholds.get("high_lead") or 5)
    positive = {name: int(scores.get(name) or 0) for name in PRODUCTION}
    ranked = sorted(PRODUCTION, key=lambda name: (positive[name], name), reverse=True)
    best = ranked[0]
    second = ranked[1]
    best_score = positive[best]
    lead = best_score - positive[second]
    exclusive_families = [name for name, hits in exclusive.items() if hits]
    if best_score < min_score or lead < min_lead:
        return "REVIEW", "review", "no family led by enough title evidence"
    family: Family = best  # type: ignore[assignment]
    if exclusive_families == [best] and lead >= min_lead:
        return family, "high", f"exclusive {best} pattern"
    if lead >= high_lead:
        return family, "high", f"{best} led by {lead}"
    return family, "medium", f"{best} led by {lead}"


def route(job: JobMeta | Mapping[str, Any], policy: Optional[Mapping[str, Any]] = None) -> RouteDecision:
    meta = job if isinstance(job, JobMeta) else JobMeta.from_mapping(job)
    spec = dict(policy) if policy is not None else load_policy()
    legacy = meta.legacy_cluster or suggest_legacy_cluster(meta, spec)
    title = _title(meta)
    if not title:
        return RouteDecision("REVIEW", "review", ("input.empty_role",), "role is empty", legacy, {})
    blob = _blob(meta)
    exclusive = _exclusive_hits(title, spec)
    exclusive = _prefer_infra_over_generic_ml(exclusive)
    scores, rules = _score_signals(title, blob, spec)
    for family, hits in exclusive.items():
        scores[family] += 8 * len(hits)
        rules.extend(hits)
    forced, data_rules = _data_overlay(title, scores, spec)
    rules.extend(data_rules)
    rules.extend(_health_overlay(meta, scores, spec))
    rules.extend(_board_prior(meta, scores, spec))
    family, confidence, reason = _decide(scores, exclusive, forced, spec)
    if family == "REVIEW":
        confidence = "review"
    return RouteDecision(
        family=family,
        confidence=confidence,
        matched_rules=tuple(dict.fromkeys(rules)),
        reason=reason,
        legacy_cluster=legacy,
        scores=scores,
    )


def _registry_rows(path: Path = REGISTRY_PATH) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def resolve_variant(family: str, registry_path: Path = REGISTRY_PATH) -> VariantResolution:
    if family not in PRODUCTION:
        return VariantResolution("REVIEW", "", "unresolved_family")
    typed: Family = family  # type: ignore[assignment]
    rows = _registry_rows(registry_path)
    matches: list[dict[str, str]] = []
    for row in rows:
        cluster = (row.get("cluster") or "").strip()
        active = (row.get("active") or "").strip().lower()
        version = (row.get("resume_version") or "").strip()
        if cluster != family or active not in _ACTIVE or not version:
            continue
        if cluster == "base" or version == "JZ_resume":
            continue
        matches.append(row)
    if not matches:
        return VariantResolution(typed, "", "no_active_family_variant")
    matches.sort(key=lambda row: row.get("created_date") or "", reverse=True)
    chosen = matches[0]
    return VariantResolution(
        typed,
        (chosen.get("resume_version") or "").strip(),
        "active_family_variant",
        (chosen.get("file_path") or "").strip(),
    )


def route_and_resolve(
    job: JobMeta | Mapping[str, Any],
    policy: Optional[Mapping[str, Any]] = None,
    registry_path: Path = REGISTRY_PATH,
) -> dict[str, Any]:
    decision = route(job, policy)
    variant = resolve_variant(decision.family, registry_path)
    payload = decision.as_dict()
    payload.update(variant.as_dict())
    return payload
