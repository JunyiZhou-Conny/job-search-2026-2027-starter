"""Paper org shapes as vacant roles. No bot names are invented."""

from __future__ import annotations

from org_designer.model import OWNER, EditorDraft, Staffing, Talks, VacantRole, empty_draft


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
    "junyi-architect-lanes": (
        "Architect lanes (Junyi sketch)",
        (
            _v(
                "v-arch",
                "Architect",
                OWNER,
                ("Stand up the org from the charter. Junyi talks only to this seat.",),
                ("Never Autofill. Never Submit. Never hire unless Junyi authorizes the revision.",),
                order=1,
                team="Office of the Architect",
            ),
            _v(
                "v-chief-apply",
                "Chief of ____ (apply)",
                "v-arch",
                ("Own the ATS desks. Assign one cook to one job.",),
                ("Never Autofill. Never Submit. Never write Why-us.",),
                order=2,
                team="Apply chiefs",
            ),
            _v(
                "v-chief-2",
                "Chief of ____",
                "v-arch",
                ("Own one desk Junyi names.",),
                ("Never Autofill. Never Submit.",),
                kind="later",
                detail="Title left blank on the 2026-08-26 sketch.",
                team="Open chiefs",
            ),
            _v(
                "v-chief-3",
                "Chief (open seat)",
                "v-arch",
                ("Own one desk Junyi names.",),
                ("Never Autofill. Never Submit.",),
                kind="later",
                detail="Empty oval on the sketch.",
                team="Open chiefs",
            ),
            _v(
                "v-chief-4",
                "Chief (open seat)",
                "v-arch",
                ("Own one desk Junyi names.",),
                ("Never Autofill. Never Submit.",),
                kind="later",
                detail="Empty oval on the sketch.",
                team="Open chiefs",
            ),
            _v(
                "v-ashby-lane",
                "Ashby Application",
                "v-chief-apply",
                ("Own the Ashby lane. Hand one URL to one autofiller.",),
                ("Never Submit. Never invent GPA, citizenship, or project URLs.",),
                order=3,
                team="Ashby",
            ),
            _v(
                "v-ash-fill",
                "Autofiller / clicker",
                "v-ashby-lane",
                ("One Ashby job: Autofill once, correct leftovers, stop.",),
                ("Stop before Submit. Never invent facts. Never Run Autofill Again.",),
                order=4,
                team="Ashby",
            ),
            _v(
                "v-ash-fill-n",
                "Autofiller bench",
                "v-ashby-lane",
                ("More Ashby cooks, one job each, after the first cook is trusted.",),
                ("Do not seat 10 first. Never Submit. Shared computer is not isolation.",),
                kind="later",
                detail="Sketch says x10. Seat up to 9 more only after the first cook works without Junyi steering clicks.",
                team="Ashby",
            ),
            _v(
                "v-email",
                "Email verification",
                "v-ashby-lane",
                ("Park the job and ask Junyi for login or an email code.",),
                ("Never complete 2FA. Never create a new ATS account. Never Submit.",),
                kind="on_call",
                detail="Sketch says x1. Ask Junyi. Do not hold the code.",
                team="Ashby",
            ),
            _v(
                "v-wri",
                "Writer",
                "v-ashby-lane",
                ("Draft a Why-us or leftover essay when asked. File in docs/apply/written_answers/.",),
                ("A file is not a Submit. Never invent facts.",),
                kind="on_call",
                detail="Sketch says x1, or maybe 2.",
                team="Copy",
            ),
            _v(
                "v-wri-2",
                "Writer",
                "v-ashby-lane",
                ("Second copy seat if one writer is not enough.",),
                ("A file is not a Submit. Never invent facts.",),
                kind="later",
                detail="The sketch says or maybe 2.",
                team="Copy",
            ),
            _v(
                "v-workday",
                "Workday",
                "v-chief-apply",
                ("One named study job. Map pages. Write rules. No account create.",),
                ("Never N-way parallel. Never complete email verify. Never Submit.",),
                kind="later",
                detail="0 until one study. Email verify is Junyi.",
                team="Workday",
            ),
            _v(
                "v-misc",
                "Miscellaneous / unknown portal",
                "v-chief-apply",
                ("Label the portal. Stop if it is a signup wall or unknown ATS.",),
                ("Never invent a sibling job. Never apply on Jobright. Never Submit.",),
                kind="later",
                detail="Sketch: other application portal I am not aware of yet.",
                team="Unknown ATS",
            ),
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
    talks = base.talks
    if template_id == "junyi-architect-lanes":
        talks = Talks(
            owner_talks_only_to="v-arch",
            assign_by=base.talks.assign_by,
            assign_detail="Junyi talks only to the Architect. Chiefs talk to the Architect.",
            team_handoff="Ashby cook returns a visible form. Email and login park for Junyi. Workday and unknown portals stay later.",
        )
    return EditorDraft(
        company="Job search" if template_id == "junyi-architect-lanes" else base.company,
        project=_name,
        as_of=base.as_of,
        owner=base.owner,
        seats=(),
        vacancies=vacancies,
        talks=talks,
        done_when=("Pilot seats named. Later seats stay dormant until Junyi says so.",),
    )
