"""Charter types and the one compile path.

listens_to is stored. Graph, roster, and direct reports are derived.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal

OWNER = "owner"

BASELINE_GATES = (
    "submit",
    "send",
    "two_factor",
    "new_ats_account",
    "mygreenhouse_login",
    "workday_email",
)


class IssueCode(StrEnum):
    REQUIRED = "required"
    DUPLICATE_BOT_NAME = "duplicate_bot_name"
    DUPLICATE_ID = "duplicate_id"
    VACANT_ROLE = "vacant_role"
    UNKNOWN_PARENT = "unknown_parent"
    REPORTING_CYCLE = "reporting_cycle"
    SELF_REPORT = "self_report"
    OWNER_AS_BOT = "owner_as_bot"
    DUPLICATE_PILOT_ORDER = "duplicate_pilot_order"
    BASELINE_GATE_MISSING = "baseline_gate_missing"
    UNKNOWN_SEAT = "unknown_seat"


@dataclass(frozen=True)
class DesignIssue:
    code: IssueCode
    path: str
    message: str


@dataclass(frozen=True)
class Staffing:
    kind: Literal["pilot", "later", "on_call"]
    order: int | None = None
    detail: str = ""


@dataclass(frozen=True)
class DraftSeat:
    id: str
    bot_name: str
    role: str
    listens_to: str  # OWNER or seat id
    does: tuple[str, ...]
    does_not: tuple[str, ...]
    staffing: Staffing
    team: str = ""


@dataclass(frozen=True)
class VacantRole:
    id: str
    role: str
    listens_to: str
    suggested_does: tuple[str, ...]
    suggested_does_not: tuple[str, ...]
    staffing: Staffing
    team: str = ""


@dataclass(frozen=True)
class Talks:
    owner_talks_only_to: str
    assign_by: Literal["group_chat", "dm", "other"]
    assign_detail: str
    team_handoff: str


@dataclass(frozen=True)
class OwnerDraft:
    name: str
    does: tuple[str, ...]
    does_not: tuple[str, ...]
    gates: tuple[str, ...]


@dataclass(frozen=True)
class EditorDraft:
    company: str
    project: str
    as_of: str
    owner: OwnerDraft
    seats: tuple[DraftSeat, ...]
    vacancies: tuple[VacantRole, ...]
    talks: Talks
    done_when: tuple[str, ...]


@dataclass(frozen=True)
class CompiledSeat:
    source: DraftSeat
    listens_to_label: str
    direct_reports: tuple[str, ...]  # seat ids


@dataclass(frozen=True)
class CompiledCharter:
    draft: EditorDraft
    seats: tuple[CompiledSeat, ...]
    digest: str


@dataclass(frozen=True)
class CompileFailure:
    issues: tuple[DesignIssue, ...]


def _clean(value: str) -> str:
    return (value or "").strip()


def _lines(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(item.strip() for item in values if str(item).strip())


def staffing_from_wire(raw: Any) -> Staffing:
    if not isinstance(raw, dict):
        return Staffing(kind="pilot", order=1)
    kind = raw.get("kind") or "pilot"
    if kind not in {"pilot", "later", "on_call"}:
        kind = "pilot"
    order = raw.get("order")
    try:
        order_i = int(order) if order is not None and kind == "pilot" else None
    except (TypeError, ValueError):
        order_i = None
    if kind == "pilot" and order_i is None:
        order_i = 1
    return Staffing(kind=kind, order=order_i, detail=_clean(str(raw.get("detail") or "")))


def draft_from_wire(payload: dict[str, Any]) -> EditorDraft:
    owner_raw = payload.get("owner") or {}
    talks_raw = payload.get("talks") or {}
    assign = talks_raw.get("assign_by") or "dm"
    if assign not in {"group_chat", "dm", "other"}:
        assign = "dm"
    seats: list[DraftSeat] = []
    for item in payload.get("seats") or []:
        seats.append(
            DraftSeat(
                id=_clean(str(item.get("id") or "")),
                bot_name=_clean(str(item.get("bot_name") or "")),
                role=_clean(str(item.get("role") or "")),
                listens_to=_clean(str(item.get("listens_to") or OWNER)) or OWNER,
                does=_lines(tuple(item.get("does") or ())),
                does_not=_lines(tuple(item.get("does_not") or ())),
                staffing=staffing_from_wire(item.get("staffing")),
                team=_clean(str(item.get("team") or "")),
            )
        )
    vacancies: list[VacantRole] = []
    for item in payload.get("vacancies") or []:
        vacancies.append(
            VacantRole(
                id=_clean(str(item.get("id") or "")),
                role=_clean(str(item.get("role") or "")),
                listens_to=_clean(str(item.get("listens_to") or OWNER)) or OWNER,
                suggested_does=_lines(tuple(item.get("suggested_does") or ())),
                suggested_does_not=_lines(tuple(item.get("suggested_does_not") or ())),
                staffing=staffing_from_wire(item.get("staffing")),
                team=_clean(str(item.get("team") or "")),
            )
        )
    return EditorDraft(
        company=_clean(str(payload.get("company") or "")),
        project=_clean(str(payload.get("project") or "")),
        as_of=_clean(str(payload.get("as_of") or "")),
        owner=OwnerDraft(
            name=_clean(str(owner_raw.get("name") or "")),
            does=_lines(tuple(owner_raw.get("does") or ())),
            does_not=_lines(tuple(owner_raw.get("does_not") or ())),
            gates=tuple(_clean(str(g)) for g in (owner_raw.get("gates") or ()) if _clean(str(g))),
        ),
        seats=tuple(seats),
        vacancies=tuple(vacancies),
        talks=Talks(
            owner_talks_only_to=_clean(str(talks_raw.get("owner_talks_only_to") or "")),
            assign_by=assign,
            assign_detail=_clean(str(talks_raw.get("assign_detail") or "")),
            team_handoff=_clean(str(talks_raw.get("team_handoff") or "")),
        ),
        done_when=_lines(tuple(payload.get("done_when") or ())),
    )


def draft_to_wire(draft: EditorDraft) -> dict[str, Any]:
    def staffing_wire(plan: Staffing) -> dict[str, Any]:
        return {"kind": plan.kind, "order": plan.order, "detail": plan.detail}

    return {
        "schema_version": 1,
        "mode": "plan_only",
        "computer_boundary": "shared_per_user",
        "company": draft.company,
        "project": draft.project,
        "as_of": draft.as_of,
        "owner": {
            "name": draft.owner.name,
            "does": list(draft.owner.does),
            "does_not": list(draft.owner.does_not),
            "gates": list(draft.owner.gates),
        },
        "seats": [
            {
                "id": seat.id,
                "bot_name": seat.bot_name,
                "role": seat.role,
                "listens_to": seat.listens_to,
                "does": list(seat.does),
                "does_not": list(seat.does_not),
                "staffing": staffing_wire(seat.staffing),
                "team": seat.team,
            }
            for seat in draft.seats
        ],
        "vacancies": [
            {
                "id": vac.id,
                "role": vac.role,
                "listens_to": vac.listens_to,
                "suggested_does": list(vac.suggested_does),
                "suggested_does_not": list(vac.suggested_does_not),
                "staffing": staffing_wire(vac.staffing),
                "team": vac.team,
            }
            for vac in draft.vacancies
        ],
        "talks": {
            "owner_talks_only_to": draft.talks.owner_talks_only_to,
            "assign_by": draft.talks.assign_by,
            "assign_detail": draft.talks.assign_detail,
            "team_handoff": draft.talks.team_handoff,
        },
        "done_when": list(draft.done_when),
    }


def empty_draft(*, owner_name: str = "", as_of: str = "") -> EditorDraft:
    return EditorDraft(
        company="",
        project="",
        as_of=as_of,
        owner=OwnerDraft(
            name=owner_name,
            does=("Owns Submit, send, 2FA, and new ATS accounts.",),
            does_not=("Not a Bot. Never invent facts for a Bot to paste.",),
            gates=BASELINE_GATES,
        ),
        seats=(),
        vacancies=(),
        talks=Talks(
            owner_talks_only_to="",
            assign_by="dm",
            assign_detail="",
            team_handoff="",
        ),
        done_when=(),
    )


def completeness(draft: EditorDraft) -> tuple[DesignIssue, ...]:
    issues: list[DesignIssue] = []
    if not draft.company:
        issues.append(DesignIssue(IssueCode.REQUIRED, "company", "Company is empty."))
    if not draft.project:
        issues.append(DesignIssue(IssueCode.REQUIRED, "project", "Project is empty."))
    if not draft.as_of:
        issues.append(DesignIssue(IssueCode.REQUIRED, "as_of", "Date is empty."))
    if not draft.owner.name:
        issues.append(DesignIssue(IssueCode.REQUIRED, "owner.name", "Owner name is empty."))
    if not draft.owner.does:
        issues.append(DesignIssue(IssueCode.REQUIRED, "owner.does", "Owner does is empty."))
    if not draft.owner.does_not:
        issues.append(DesignIssue(IssueCode.REQUIRED, "owner.does_not", "Owner does not is empty."))
    if not draft.seats:
        issues.append(DesignIssue(IssueCode.REQUIRED, "seats", "No named bots yet."))
    for seat in draft.seats:
        if not seat.role:
            issues.append(DesignIssue(IssueCode.REQUIRED, f"seats.{seat.id}.role", "Role is empty."))
        if not seat.does:
            issues.append(DesignIssue(IssueCode.REQUIRED, f"seats.{seat.id}.does", "Does is empty."))
        if not seat.does_not:
            issues.append(DesignIssue(IssueCode.REQUIRED, f"seats.{seat.id}.does_not", "Does not is empty."))
    if not draft.talks.owner_talks_only_to:
        issues.append(DesignIssue(IssueCode.REQUIRED, "talks.owner_talks_only_to", "Junyi talks only to is empty."))
    elif draft.talks.owner_talks_only_to not in {seat.id for seat in draft.seats}:
        issues.append(DesignIssue(IssueCode.UNKNOWN_SEAT, "talks.owner_talks_only_to", "Talks-only-to is not a seated bot."))
    if not draft.talks.team_handoff:
        issues.append(DesignIssue(IssueCode.REQUIRED, "talks.team_handoff", "Team handoff is empty."))
    if not draft.done_when:
        issues.append(DesignIssue(IssueCode.REQUIRED, "done_when", "Done when is empty."))
    return tuple(issues)


def compile_draft(draft: EditorDraft) -> CompiledCharter | CompileFailure:
    issues: list[DesignIssue] = []
    ids: set[str] = set()
    names: dict[str, str] = {}

    if draft.vacancies:
        for vac in draft.vacancies:
            issues.append(
                DesignIssue(
                    IssueCode.VACANT_ROLE,
                    f"vacancies.{vac.id}",
                    f"Name a bot for {vac.role or 'this role'}, or delete the slip.",
                )
            )

    for seat in draft.seats:
        if not seat.id:
            issues.append(DesignIssue(IssueCode.REQUIRED, "seats", "A seat is missing an id."))
            continue
        if seat.id in ids:
            issues.append(DesignIssue(IssueCode.DUPLICATE_ID, f"seats.{seat.id}", "Duplicate seat id."))
        ids.add(seat.id)
        if seat.id == OWNER or seat.bot_name.lower() == "nobody":
            issues.append(DesignIssue(IssueCode.OWNER_AS_BOT, f"seats.{seat.id}", "Owner is not a bot."))
        if not seat.bot_name or seat.bot_name == "_":
            issues.append(DesignIssue(IssueCode.REQUIRED, f"seats.{seat.id}.bot_name", "Bot name is empty."))
        else:
            key = seat.bot_name.casefold()
            if key in names:
                issues.append(
                    DesignIssue(
                        IssueCode.DUPLICATE_BOT_NAME,
                        f"seats.{seat.id}.bot_name",
                        f"Bot name {seat.bot_name} is already used.",
                    )
                )
            names[key] = seat.id

    known = {OWNER} | {seat.id for seat in draft.seats if seat.id}
    vacant_ids = {vac.id for vac in draft.vacancies if vac.id}
    for seat in draft.seats:
        parent = seat.listens_to or OWNER
        if parent == seat.id:
            issues.append(DesignIssue(IssueCode.SELF_REPORT, f"seats.{seat.id}", "A bot cannot listen to itself."))
        elif parent not in known:
            if parent in vacant_ids:
                issues.append(
                    DesignIssue(
                        IssueCode.VACANT_ROLE,
                        f"seats.{seat.id}.listens_to",
                        "Parent is still an unnamed role.",
                    )
                )
            else:
                issues.append(DesignIssue(IssueCode.UNKNOWN_PARENT, f"seats.{seat.id}.listens_to", "Parent is not on the chart."))

    children: dict[str, list[str]] = {OWNER: []}
    for seat in draft.seats:
        children.setdefault(seat.id, [])
    for seat in draft.seats:
        parent = seat.listens_to or OWNER
        if parent in children or parent == OWNER:
            children.setdefault(parent, []).append(seat.id)

    def ancestors(start: str) -> bool:
        seen: set[str] = set()
        cur = start
        while cur != OWNER:
            if cur in seen:
                return True
            seen.add(cur)
            match = next((s for s in draft.seats if s.id == cur), None)
            if match is None:
                return False
            cur = match.listens_to or OWNER
        return False

    for seat in draft.seats:
        if seat.listens_to in known and ancestors(seat.id):
            issues.append(
                DesignIssue(IssueCode.REPORTING_CYCLE, f"seats.{seat.id}", "Reporting would loop.")
            )

    missing_gates = [g for g in BASELINE_GATES if g not in draft.owner.gates]
    if missing_gates:
        issues.append(
            DesignIssue(
                IssueCode.BASELINE_GATE_MISSING,
                "owner.gates",
                "Owner is missing baseline gates: " + ", ".join(missing_gates) + ".",
            )
        )

    orders = [s.staffing.order for s in draft.seats if s.staffing.kind == "pilot" and s.staffing.order is not None]
    if len(orders) != len(set(orders)):
        issues.append(DesignIssue(IssueCode.DUPLICATE_PILOT_ORDER, "seats", "Pilot order numbers repeat."))

    # Dedup cycle reports (walk flags every node on a loop).
    seen_codes: set[tuple[IssueCode, str]] = set()
    unique: list[DesignIssue] = []
    for issue in issues:
        key = (issue.code, issue.path)
        if key in seen_codes:
            continue
        seen_codes.add(key)
        unique.append(issue)

    if unique:
        return CompileFailure(issues=tuple(unique))

    by_id = {seat.id: seat for seat in draft.seats}
    compiled: list[CompiledSeat] = []
    for seat in draft.seats:
        parent = seat.listens_to or OWNER
        if parent == OWNER:
            label = draft.owner.name or "Owner"
        else:
            label = by_id[parent].bot_name
        reports = tuple(cid for cid in children.get(seat.id, ()))
        compiled.append(CompiledSeat(source=seat, listens_to_label=label, direct_reports=reports))

    return CompiledCharter(draft=draft, seats=tuple(compiled), digest="")


def reparent(draft: EditorDraft, seat_id: str, new_parent: str) -> EditorDraft:
    seats = []
    for seat in draft.seats:
        if seat.id == seat_id:
            seats.append(
                DraftSeat(
                    id=seat.id,
                    bot_name=seat.bot_name,
                    role=seat.role,
                    listens_to=new_parent or OWNER,
                    does=seat.does,
                    does_not=seat.does_not,
                    staffing=seat.staffing,
                    team=seat.team,
                )
            )
        else:
            seats.append(seat)
    return EditorDraft(
        company=draft.company,
        project=draft.project,
        as_of=draft.as_of,
        owner=draft.owner,
        seats=tuple(seats),
        vacancies=draft.vacancies,
        talks=draft.talks,
        done_when=draft.done_when,
    )


def seat_children(draft: EditorDraft, parent_id: str) -> tuple[DraftSeat, ...]:
    return tuple(s for s in draft.seats if (s.listens_to or OWNER) == parent_id)


def tree_walk(draft: EditorDraft, parent_id: str = OWNER) -> list[tuple[int, DraftSeat]]:
    out: list[tuple[int, DraftSeat]] = []

    def walk(pid: str, depth: int) -> None:
        for seat in seat_children(draft, pid):
            out.append((depth, seat))
            walk(seat.id, depth + 1)

    walk(parent_id, 0)
    return out
