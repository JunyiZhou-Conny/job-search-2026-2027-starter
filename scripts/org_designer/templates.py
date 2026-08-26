"""Paper org shapes as vacant roles. No bot names are invented."""

from __future__ import annotations

from org_designer.model import OWNER, EditorDraft, Staffing, VacantRole, empty_draft


def _v(
    vid: str,
    role: str,
    parent: str,
    does: tuple[str, ...],
    does_not: tuple[str, ...],
    *,
    kind: str = "pilot",
    order: int | None = None,
    detail: str = "",
    team: str = "",
) -> VacantRole:
    return VacantRole(
        id=vid,
        role=role,
        listens_to=parent,
        suggested_does=does,
        suggested_does_not=does_not,
        staffing=Staffing(kind=kind, order=order, detail=detail),  # type: ignore[arg-type]
        team=team,
    )


TEMPLATES: dict[str, tuple[str, tuple[VacantRole, ...]]] = {
    "shop-of-four": (
        "Shop of four",
        (
            _v("v-cos", "Chief of Staff", OWNER, ("Assigns work and still cooks in this roster.",), ("Never Submit.",), order=1, team="Office of the Chief"),
            _v("v-res", "Researcher", "v-cos", ("Owns facts and URLs.",), ("Never Autofill. Never Submit.",), order=2, team="Specialists"),
            _v("v-wri", "Writer", "v-cos", ("Owns drafts and Why-us.",), ("A draft file is not a Submit.",), order=3, team="Specialists"),
            _v("v-ops", "Ops", "v-cos", ("Owns tracking and routines.",), ("Never apply-click.",), order=4, team="Specialists"),
        ),
    ),
    "apply-cell": (
        "Apply cell",
        (
            _v("v-cos", "Chief of Staff", OWNER, ("Pick the next named job. Assign one cook.",), ("Never Autofill. Never paste Why-us. Never Submit.",), order=1, team="Office of the Chief"),
            _v("v-tri", "Triage", "v-cos", ("Open the URL. Label the ATS.",), ("Never fill the form.",), order=2, team="Intake"),
            _v("v-ash", "Ashby mind", "v-cos", ("One Ashby sticky note, one Autofill, leftover correction.",), ("Stop before Submit. Never invent GPA, citizenship, or project URLs.",), order=3, team="Ashby cell"),
            _v("v-aud", "Auditor", "v-cos", ("Read the visible form against standing rules.",), ("Never click.",), order=4, team="Quality"),
            _v("v-ops", "Ops", "v-cos", ("Wall-clock, thought-chain length, token budget.",), ("Never apply-click.",), order=5, team="Finance"),
            _v("v-wri", "Writer", "v-cos", ("Why-us only when assigned.",), ("A file in docs/apply/written_answers/ is not a Submit.",), kind="on_call", detail="Summoned when CoS assigns a draft.", team="Copy"),
        ),
    ),
    "depth-then-factory": (
        "Depth, then factory",
        (
            _v("v-cos", "Chief of Staff", OWNER, ("Owns assignment.",), ("Never cook. Never Submit.",), order=1, team="Office of the Chief"),
            _v("v-cook", "Cook", "v-cos", ("One job through verification on the real artifact.",), ("Never Submit. Never invent facts.",), order=2, team="Cooking"),
            _v("v-aud", "Auditor", "v-cos", ("Reads the artifact, not the story.",), ("Never click.",), order=3, team="Quality"),
        ),
    ),
    "job-search-hybrid": (
        "Job-search hybrid",
        (
            _v("v-cos", "Chief of Staff", OWNER, ("Owns assignment.",), ("Never Autofill. Never Submit.",), order=1, team="Office of the Chief"),
            _v("v-tri", "Triage", "v-cos", ("ATS label only.",), ("Never fill the form.",), order=2, team="Intake"),
            _v("v-ash", "Ashby mind", "v-cos", ("One Ashby job through leftover correction.",), ("Stop before Submit. Never invent facts.",), order=3, team="Ashby cell"),
            _v("v-aud", "Auditor", "v-cos", ("Form review.",), ("Never click.",), order=4, team="Quality"),
            _v("v-ops", "Ops", "v-cos", ("Time, tokens, weekly prune list.",), ("Never apply-click.",), order=5, team="Finance"),
            _v("v-wri", "Writer", "v-cos", ("Assigned drafts only.",), ("A file is not a Submit.",), kind="on_call", detail="Summoned, not seated.", team="Copy"),
            _v("v-far", "Farmer", "v-cos", ("Discovery complaints and closed URLs after apply-cell works.",), ("Never Autofill. Never Submit.",), kind="later", detail="After apply-cell works.", team="Outer loop"),
        ),
    ),
}


def list_templates() -> list[dict[str, str]]:
    return [{"id": key, "name": name} for key, (name, _) in TEMPLATES.items()]


def load_template(template_id: str, *, owner_name: str = "", as_of: str = "") -> EditorDraft:
    if template_id not in TEMPLATES:
        raise KeyError(template_id)
    _name, vacancies = TEMPLATES[template_id]
    base = empty_draft(owner_name=owner_name, as_of=as_of)
    return EditorDraft(
        company=base.company,
        project=_name,
        as_of=base.as_of,
        owner=base.owner,
        seats=(),
        vacancies=vacancies,
        talks=base.talks,
        done_when=base.done_when,
    )
