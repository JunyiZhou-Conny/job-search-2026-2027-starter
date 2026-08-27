"""Read, review, save. Callers do not orchestrate compile or render."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from org_designer.artifacts import render_brief, render_chart_markdown
from org_designer.model import (
    CompiledCharter,
    CompileFailure,
    DesignIssue,
    EditorDraft,
    completeness,
    compile_draft,
    draft_from_wire,
    draft_to_wire,
    empty_draft,
)
from org_designer.templates import list_templates, load_template

SCHEMA_VERSION = 1


class DesignRejected(ValueError):
    def __init__(self, issues: tuple[DesignIssue, ...]) -> None:
        super().__init__("design rejected")
        self.issues = issues


class RevisionConflict(RuntimeError):
    def __init__(self, expected: str, actual: str) -> None:
        super().__init__("revision conflict")
        self.expected = expected
        self.actual = actual


@dataclass(frozen=True)
class SaveDesign:
    draft: EditorDraft
    expected_revision: str
    write_brief: bool = False


@dataclass(frozen=True)
class ArtifactPreview:
    chart: str
    brief: str | None
    ready_for_brief: bool
    completeness: tuple[DesignIssue, ...]


@dataclass(frozen=True)
class DesignReview:
    issues: tuple[DesignIssue, ...]
    preview: ArtifactPreview | None


@dataclass(frozen=True)
class EditorSnapshot:
    revision: str
    draft: EditorDraft
    review: DesignReview
    templates: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class SaveReceipt:
    revision: str
    artifacts: tuple[str, ...]
    preview: ArtifactPreview
    changed: bool
    hire_allowed: bool = False


class OrgDesigner:
    def __init__(self, repo_root: Path) -> None:
        self.root = repo_root
        self.org_dir = repo_root / "docs" / "grok-bot-management"
        self.charter_path = self.org_dir / "ORG_CHART.json"
        self.chart_md_path = self.org_dir / "ORG_CHART.md"
        self.brief_path = self.org_dir / "ORG_SPAWN_BRIEF.md"
        self.blank_path = self.org_dir / "ORG_CHART_BLANK.md"
        self.live_handoff_path = self.org_dir / "GROK_BOT_HANDOFF.md"
        self.profile_path = repo_root / "config" / "profile.yaml"

    @classmethod
    def at(cls, repo_root: Path) -> OrgDesigner:
        return cls(repo_root)

    def _owner_name(self) -> str:
        if not self.profile_path.is_file():
            return ""
        for line in self.profile_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("legal_name:"):
                return line.split(":", 1)[1].strip().strip('"')
        return ""

    def read(self, template_id: str | None = None, *, fresh: bool = False) -> EditorSnapshot:
        if template_id:
            draft = load_template(template_id, owner_name=self._owner_name(), as_of=date.today().isoformat())
            return EditorSnapshot(
                revision=self._current_revision(),
                draft=draft,
                review=self.review(draft),
                templates=tuple(list_templates()),
            )
        if fresh:
            draft = empty_draft(owner_name=self._owner_name(), as_of=date.today().isoformat())
            return EditorSnapshot(
                revision=self._current_revision(),
                draft=draft,
                review=self.review(draft),
                templates=tuple(list_templates()),
            )
        if self.charter_path.is_file():
            payload = json.loads(self.charter_path.read_text(encoding="utf-8"))
            draft = draft_from_wire(payload)
            revision = payload.get("revision") or self._digest_bytes(self._canonical_bytes(draft))
        else:
            draft = empty_draft(owner_name=self._owner_name(), as_of=date.today().isoformat())
            revision = ""
        return EditorSnapshot(
            revision=revision,
            draft=draft,
            review=self.review(draft),
            templates=tuple(list_templates()),
        )

    def review(self, draft: EditorDraft) -> DesignReview:
        compiled = compile_draft(draft)
        if isinstance(compiled, CompileFailure):
            return DesignReview(issues=compiled.issues, preview=None)
        compiled = self._with_digest(compiled)
        gaps = completeness(draft)
        chart = render_chart_markdown(compiled)
        brief = render_brief(compiled, compiled.digest) if not gaps else None
        return DesignReview(
            issues=(),
            preview=ArtifactPreview(
                chart=chart,
                brief=brief,
                ready_for_brief=not gaps,
                completeness=gaps,
            ),
        )

    def save(self, command: SaveDesign) -> SaveReceipt:
        actual = self._current_revision()
        if command.expected_revision != actual:
            raise RevisionConflict(command.expected_revision, actual)
        compiled = compile_draft(command.draft)
        if isinstance(compiled, CompileFailure):
            raise DesignRejected(compiled.issues)
        compiled = self._with_digest(compiled)
        gaps = completeness(command.draft)
        if command.write_brief and gaps:
            raise DesignRejected(gaps)
        chart_md = render_chart_markdown(compiled)
        brief = render_brief(compiled, compiled.digest) if (command.write_brief and not gaps) else None
        payload = draft_to_wire(command.draft)
        payload["revision"] = compiled.digest
        body = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        self.org_dir.mkdir(parents=True, exist_ok=True)
        written = [
            self._replace(self.charter_path, body.encode("utf-8")),
            self._replace(self.chart_md_path, chart_md.encode("utf-8")),
        ]
        artifacts = [
            "docs/grok-bot-management/ORG_CHART.json",
            "docs/grok-bot-management/ORG_CHART.md",
        ]
        if brief is not None:
            written.append(self._replace(self.brief_path, brief.encode("utf-8")))
            artifacts.append("docs/grok-bot-management/ORG_SPAWN_BRIEF.md")
        return SaveReceipt(
            revision=compiled.digest,
            artifacts=tuple(artifacts),
            preview=ArtifactPreview(
                chart=chart_md,
                brief=brief,
                ready_for_brief=not gaps,
                completeness=gaps,
            ),
            changed=any(written),
            hire_allowed=False,
        )

    def assert_live_handoff_untouched(self, before: str | None = None) -> None:
        if before is None:
            return
        if not self.live_handoff_path.is_file():
            return
        after = self.live_handoff_path.read_text(encoding="utf-8")
        if after != before:
            raise RuntimeError("live handoff was written")

    def _current_revision(self) -> str:
        if not self.charter_path.is_file():
            return ""
        payload = json.loads(self.charter_path.read_text(encoding="utf-8"))
        return str(payload.get("revision") or "")

    def _canonical_bytes(self, draft: EditorDraft) -> bytes:
        payload = draft_to_wire(draft)
        payload.pop("revision", None)
        return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")

    def _digest_bytes(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()[:16]

    def _with_digest(self, compiled: CompiledCharter) -> CompiledCharter:
        digest = self._digest_bytes(self._canonical_bytes(compiled.draft))
        return CompiledCharter(draft=compiled.draft, seats=compiled.seats, digest=digest)

    def _replace(self, path: Path, data: bytes) -> bool:
        if path.is_file() and path.read_bytes() == data:
            return False
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)
        return True


def issues_to_wire(issues: tuple[DesignIssue, ...]) -> list[dict[str, Any]]:
    return [{"code": i.code.value, "path": i.path, "message": i.message} for i in issues]


def snapshot_to_wire(snap: EditorSnapshot) -> dict[str, Any]:
    return {
        "revision": snap.revision,
        "draft": draft_to_wire(snap.draft),
        "review": review_to_wire(snap.review),
        "templates": list(snap.templates),
        "hire_allowed": False,
    }


def review_to_wire(review: DesignReview) -> dict[str, Any]:
    preview = None
    if review.preview:
        preview = {
            "chart": review.preview.chart,
            "brief": review.preview.brief,
            "ready_for_brief": review.preview.ready_for_brief,
            "completeness": issues_to_wire(review.preview.completeness),
        }
    return {"issues": issues_to_wire(review.issues), "preview": preview}


def receipt_to_wire(receipt: SaveReceipt) -> dict[str, Any]:
    return {
        "revision": receipt.revision,
        "artifacts": list(receipt.artifacts),
        "changed": receipt.changed,
        "hire_allowed": False,
        "preview": {
            "chart": receipt.preview.chart,
            "brief": receipt.preview.brief,
            "ready_for_brief": receipt.preview.ready_for_brief,
            "completeness": issues_to_wire(receipt.preview.completeness),
        },
    }
