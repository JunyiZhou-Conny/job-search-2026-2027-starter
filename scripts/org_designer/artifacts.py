"""Derived markdown. Never a second source of truth."""

from __future__ import annotations

from org_designer.model import OWNER, CompiledCharter, CompiledSeat, EditorDraft, tree_walk


def _join(lines: tuple[str, ...]) -> str:
    if not lines:
        return ""
    if len(lines) == 1:
        return lines[0]
    return "; ".join(lines)


def _graph(charter: CompiledCharter) -> str:
    owner = charter.draft.owner.name or "Owner"
    lines = [f"Owner: {owner}"]
    kids = [s for s in charter.draft.seats if (s.listens_to or OWNER) == OWNER]
    if not kids:
        return "\n".join(lines)
    lines.append("        |")
    if len(kids) == 1:
        top = kids[0]
        lines.append(f"   {top.bot_name} / {top.role}")
        reports = [s for s in charter.draft.seats if s.listens_to == top.id]
        if reports:
            lines.append("        |")
            names = [s.bot_name for s in reports]
            lines.append("   " + "    ".join(names))
        return "\n".join(lines)
    names = [s.bot_name for s in kids]
    lines.append("   " + "    ".join(names))
    return "\n".join(lines)


def render_chart_markdown(charter: CompiledCharter) -> str:
    draft = charter.draft
    by_id = {c.source.id: c for c in charter.seats}
    exec_seats = [c for c in charter.seats if (c.source.listens_to or OWNER) == OWNER]
    other = [c for c in charter.seats if c not in exec_seats]

    parts = [
        "# Org chart",
        "",
        f"Company: {draft.company}",
        f"Project: {draft.project}",
        f"Date: {draft.as_of}",
        "",
        "Generated from ORG_CHART.json. Do not treat graph or roster as inputs.",
        "",
        "## Graph",
        "",
        "```text",
        _graph(charter),
        "```",
        "",
        "## Owner (human)",
        "",
        f"- Name: {draft.owner.name}",
        "- Listens to: nobody",
        f"- Does: {_join(draft.owner.does)}",
        f"- Does not: {_join(draft.owner.does_not)}",
        f"- Gates: {', '.join(draft.owner.gates)}",
        "",
        "## Executive",
        "",
    ]
    for compiled in exec_seats:
        parts.extend(_seat_block(compiled, by_id, draft, heading="Seat"))
    if other:
        parts.extend(["## Seats", ""])
        for _depth, seat in tree_walk(draft):
            if (seat.listens_to or OWNER) == OWNER:
                continue
            parts.extend(_seat_block(by_id[seat.id], by_id, draft, heading="Seat"))

    parts.extend(
        [
            "## Roster (one row per Bot)",
            "",
            "| Bot name | Team | Title | Listens to | Does | Does not | Wave |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for compiled in charter.seats:
        s = compiled.source
        wave = s.staffing.kind
        parts.append(
            f"| {s.bot_name} | {s.team or ''} | {s.role} | {compiled.listens_to_label} | {_join(s.does)} | {_join(s.does_not)} | {wave} |"
        )
    parts.extend(
        [
            "",
            "## Who talks to whom",
            "",
            f"- Junyi talks only to: {_talks_name(draft)}",
            f"- Chief assigns work by: {_assign_label(draft.talks.assign_by)}"
            + (f" ({draft.talks.assign_detail})" if draft.talks.assign_detail else ""),
            f"- Handoff between teams: {draft.talks.team_handoff}",
            "",
            "## Done when",
            "",
        ]
    )
    for item in draft.done_when:
        parts.append(f"- {item}")
    if not draft.done_when:
        parts.append("-")
    parts.append("")
    return "\n".join(parts)


def _talks_name(draft: EditorDraft) -> str:
    for seat in draft.seats:
        if seat.id == draft.talks.owner_talks_only_to:
            return seat.bot_name
    return draft.talks.owner_talks_only_to


def _assign_label(kind: str) -> str:
    return {"group_chat": "group chat", "dm": "DM", "other": "other"}.get(kind, kind)


def _seat_block(compiled: CompiledSeat, by_id: dict[str, CompiledSeat], draft: EditorDraft, heading: str) -> list[str]:
    s = compiled.source
    reports = [by_id[rid].source.bot_name for rid in compiled.direct_reports if rid in by_id]
    lines = [
        f"### {heading}: {s.role}",
        "",
        f"- Bot name: {s.bot_name}",
        f"- Listens to: {compiled.listens_to_label}",
        f"- Direct reports: {', '.join(reports) if reports else '(none)'}",
        f"- Does: {_join(s.does)}",
        f"- Does not: {_join(s.does_not)}",
        f"- Wave: {s.staffing.kind}",
    ]
    if s.team:
        lines.append(f"- Team: {s.team}")
    if s.staffing.detail:
        lines.append(f"- Staffing note: {s.staffing.detail}")
    lines.append("")
    return lines


def render_brief(charter: CompiledCharter, revision: str) -> str:
    draft = charter.draft
    owner = draft.owner.name or "Junyi"
    pilots = [c for c in charter.seats if c.source.staffing.kind == "pilot"]
    later = [c for c in charter.seats if c.source.staffing.kind == "later"]
    on_call = [c for c in charter.seats if c.source.staffing.kind == "on_call"]
    pilots = sorted(pilots, key=lambda c: c.source.staffing.order or 0)

    paste_lines = [
        f"You are receiving staffing plan {revision}.",
        "This is not permission to create Bots.",
        f"Do not create Bots until {owner} authorizes this exact revision.",
        "",
        f"Company: {draft.company}",
        f"Project: {draft.project}",
        f"Date: {draft.as_of}",
        "",
        f"Owner (human): {owner}",
        f"Owner does: {_join(draft.owner.does)}",
        f"Owner does not: {_join(draft.owner.does_not)}",
        f"Junyi-only gates: {', '.join(draft.owner.gates)}",
        "Shared computer: every Bot on this account shares one VM, cookies, and logins. Roles are not vaults.",
        "Never invent GPA, citizenship, project URLs, or other identity facts.",
        "Never Submit unless Junyi names that URL and writes Submit in the same turn.",
        "",
        f"{owner} talks only to: {_talks_name(draft)}",
        f"Chief assigns work by: {_assign_label(draft.talks.assign_by)}"
        + (f" — {draft.talks.assign_detail}" if draft.talks.assign_detail else ""),
        f"Handoff between teams: {draft.talks.team_handoff}",
        "",
        "Pilot seats, hire order if authorized:",
    ]
    if not pilots:
        paste_lines.append("- (none)")
    for compiled in pilots:
        s = compiled.source
        paste_lines.append(
            f"- {s.staffing.order}. {s.bot_name} — {s.role}. Listens to {compiled.listens_to_label}. "
            f"Does: {_join(s.does)} Stop: {_join(s.does_not)}"
        )
    if later:
        paste_lines.append("")
        paste_lines.append("Later seats. Leave dormant until the written condition holds:")
        for compiled in later:
            s = compiled.source
            paste_lines.append(
                f"- {s.bot_name} — {s.role}. When: {s.staffing.detail or 'unspecified'}. "
                f"Listens to {compiled.listens_to_label}. Stop: {_join(s.does_not)}"
            )
    if on_call:
        paste_lines.append("")
        paste_lines.append("On-call seats. Do not seat until summoned:")
        for compiled in on_call:
            s = compiled.source
            paste_lines.append(
                f"- {s.bot_name} — {s.role}. Trigger: {s.staffing.detail or 'assigned'}. "
                f"Listens to {compiled.listens_to_label}. Stop: {_join(s.does_not)}"
            )
    paste_lines.extend(["", "Done when:"])
    for item in draft.done_when:
        paste_lines.append(f"- {item}")
    paste_lines.extend(
        [
            "",
            "If authorized: create only the named pilot seats, in that order.",
            "Return the live roster for review. Do not create a routine. Do not Submit.",
        ]
    )
    paste = "\n".join(paste_lines)
    return (
        "# Org standup brief\n\n"
        f"generated-from: {revision}\n\n"
        "This file is a staffing plan. It is not a hire. "
        "It is not the live Ashby experiment in GROK_BOT_HANDOFF.md.\n\n"
        "Copy from the next line through `END PASTE`.\n\n"
        "```text\n"
        f"{paste}\n"
        "END PASTE\n"
        "```\n"
    )
