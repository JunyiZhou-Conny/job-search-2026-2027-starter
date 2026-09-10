"""Domain types for the Resume Quality Engine.

Illegal combinations are split into variants instead of optional flags
that can disagree. External YAML is parsed into these types at the boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Verification = Literal["verified", "planned", "forbidden"]
Defensibility = Literal["strong", "moderate", "weak"]
MatchStrength = Literal["strong_direct", "transferable", "weak_adjacent", "unsupported"]
ReqKind = Literal[
    "required",
    "preferred",
    "responsibility",
    "stack",
    "seniority",
    "domain",
    "engineering",
    "research",
    "product",
]
RoleFamily = Literal["swe", "ml_ai", "data", "health_ai"]
StrategyName = Literal["recruiter", "hiring_manager", "impact", "narrative"]
Confidence = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class Metric:
    raw: str
    source: str


@dataclass(frozen=True)
class Claim:
    id: str
    project_id: str
    claim: str
    evidence: tuple[str, ...]
    verification_status: Verification
    confidence: Confidence
    resume_eligible: bool
    interview_defensibility: Defensibility
    signals: tuple[str, ...]
    relevant_role_families: tuple[str, ...]
    allowed_wording: dict[str, str]
    forbidden_claims: tuple[str, ...]
    metrics: tuple[Metric, ...]
    notes: str = ""

    def wording_for(self, family: str) -> str:
        return self.allowed_wording.get(family) or self.allowed_wording.get("default") or self.claim

    @property
    def usable_on_resume(self) -> bool:
        return self.verification_status == "verified" and self.resume_eligible


@dataclass(frozen=True)
class Project:
    id: str
    title: str
    org: str
    role: str
    dates: str
    source_url: str
    technologies: tuple[str, ...]
    claims: tuple[Claim, ...]
    entry_key: str


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str
    kind: ReqKind
    signals: tuple[str, ...]
    tokens: tuple[str, ...]


@dataclass(frozen=True)
class JobBrief:
    slug: str
    company: str
    title: str
    source: str
    family: RoleFamily
    raw_text: str
    requirements: tuple[Requirement, ...]


@dataclass(frozen=True)
class Match:
    requirement_id: str
    claim_id: str
    project_id: str
    strength: MatchStrength
    reason: str
    score: int


@dataclass(frozen=True)
class Strategy:
    name: StrategyName
    family: RoleFamily
    narrative: str
    include_projects: tuple[str, ...]
    exclude_projects: tuple[str, ...]
    section_order: tuple[tuple[str, tuple[str, ...]], ...]
    bullets: dict[str, tuple[str, ...]]
    skills_order: tuple[str, ...]
    dimensions: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class Candidate:
    name: StrategyName
    strategy: Strategy
    tex: str
    used_claim_ids: tuple[str, ...]


@dataclass
class ValidationIssue:
    severity: Literal["fail", "warn"]
    code: str
    detail: str


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "fail" for i in self.issues)


@dataclass(frozen=True)
class ArenaVote:
    perspective: str
    winner: str
    requirement_id: str
    claim_id: str
    reason: str
    veto: bool = False


@dataclass
class Bank:
    projects: dict[str, Project]
    skill_tokens: dict[str, bool]
    forbidden_tokens: tuple[str, ...]
    allowed_number_blobs: tuple[str, ...]
    profile_blobs: tuple[str, ...]
