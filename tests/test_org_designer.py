#!/usr/bin/env python3
"""Domain tests for the org designer. No Bots are hired."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from org_designer.model import (  # noqa: E402
    OWNER,
    CompileFailure,
    DraftSeat,
    EditorDraft,
    IssueCode,
    OwnerDraft,
    Staffing,
    Talks,
    VacantRole,
    compile_draft,
    completeness,
    draft_from_wire,
    empty_draft,
    reparent,
)
from org_designer.service import DesignRejected, OrgDesigner, RevisionConflict, SaveDesign  # noqa: E402
from org_designer.templates import load_template  # noqa: E402


def _seat(sid: str, name: str, parent: str, *, order: int = 1, role: str = "Role") -> DraftSeat:
    return DraftSeat(
        id=sid,
        bot_name=name,
        role=role,
        listens_to=parent,
        does=("does the job",),
        does_not=("Never Submit.",),
        staffing=Staffing(kind="pilot", order=order),
        team="",
    )


def _draft(*seats: DraftSeat, vacancies: tuple[VacantRole, ...] = ()) -> EditorDraft:
    talks_to = seats[0].id if seats else ""
    return EditorDraft(
        company="Test Co",
        project="Apply",
        as_of="2026-08-26",
        owner=OwnerDraft(
            name="Test Owner",
            does=("gates",),
            does_not=("not a bot",),
            gates=(
                "submit",
                "send",
                "two_factor",
                "new_ats_account",
                "mygreenhouse_login",
                "workday_email",
            ),
        ),
        seats=seats,
        vacancies=vacancies,
        talks=Talks(
            owner_talks_only_to=talks_to,
            assign_by="dm",
            assign_detail="",
            team_handoff="Auditor reads the form.",
        ),
        done_when=("Ready for review.",),
    )


class CompileTests(unittest.TestCase):
    def test_empty_compiles(self):
        compiled = compile_draft(empty_draft(owner_name="Junyi"))
        self.assertNotIsInstance(compiled, CompileFailure)

    def test_unnamed_bot_rejected(self):
        draft = _draft(_seat("s1", "", OWNER))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)
        self.assertTrue(any(i.code == IssueCode.REQUIRED for i in result.issues))

    def test_underscore_name_rejected(self):
        draft = _draft(_seat("s1", "_", OWNER))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)

    def test_duplicate_names_rejected(self):
        draft = _draft(_seat("s1", "Ada", OWNER, order=1), _seat("s2", "Ada", OWNER, order=2))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)
        self.assertTrue(any(i.code == IssueCode.DUPLICATE_BOT_NAME for i in result.issues))

    def test_cycle_rejected(self):
        draft = _draft(_seat("a", "Ada", "b", order=1), _seat("b", "Bea", "a", order=2))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)
        self.assertTrue(any(i.code == IssueCode.REPORTING_CYCLE for i in result.issues))

    def test_self_report_rejected(self):
        draft = _draft(_seat("a", "Ada", "a"))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)
        self.assertTrue(any(i.code == IssueCode.SELF_REPORT for i in result.issues))

    def test_reparent_updates_listens_to(self):
        draft = _draft(
            _seat("cos", "Ada", OWNER, order=1, role="Chief of Staff"),
            _seat("ash", "Ashby", "cos", order=2, role="Ashby mind"),
        )
        moved = reparent(draft, "ash", OWNER)
        compiled = compile_draft(moved)
        self.assertNotIsInstance(compiled, CompileFailure)
        ash = next(s for s in compiled.seats if s.source.id == "ash")
        self.assertEqual(ash.listens_to_label, "Test Owner")

    def test_reports_are_derived(self):
        draft = _draft(
            _seat("cos", "Ada", OWNER, order=1),
            _seat("ash", "Ashby", "cos", order=2),
        )
        compiled = compile_draft(draft)
        ada = next(s for s in compiled.seats if s.source.id == "cos")
        self.assertEqual(ada.direct_reports, ("ash",))

    def test_vacancy_blocks_compile(self):
        vac = VacantRole(
            id="v1",
            role="Writer",
            listens_to=OWNER,
            suggested_does=("draft",),
            suggested_does_not=("Submit",),
            staffing=Staffing(kind="on_call", detail="summoned"),
        )
        draft = _draft(_seat("cos", "Ada", OWNER), vacancies=(vac,))
        result = compile_draft(draft)
        self.assertIsInstance(result, CompileFailure)
        self.assertTrue(any(i.code == IssueCode.VACANT_ROLE for i in result.issues))

    def test_completeness_needs_does(self):
        draft = _draft(_seat("cos", "Ada", OWNER))
        draft = EditorDraft(
            company=draft.company,
            project=draft.project,
            as_of=draft.as_of,
            owner=draft.owner,
            seats=(
                DraftSeat(
                    id="cos",
                    bot_name="Ada",
                    role="Chief of Staff",
                    listens_to=OWNER,
                    does=(),
                    does_not=("Never Submit.",),
                    staffing=Staffing(kind="pilot", order=1),
                ),
            ),
            vacancies=(),
            talks=draft.talks,
            done_when=draft.done_when,
        )
        gaps = completeness(draft)
        self.assertTrue(any(g.path.endswith(".does") for g in gaps))


class TemplateTests(unittest.TestCase):
    def test_apply_cell_has_vacancies_not_bots(self):
        draft = load_template("apply-cell", owner_name="Junyi Zhou")
        self.assertEqual(draft.seats, ())
        roles = {v.role for v in draft.vacancies}
        self.assertIn("Chief of Staff", roles)
        self.assertIn("Ashby mind", roles)
        self.assertIn("Writer", roles)
        writer = next(v for v in draft.vacancies if v.role == "Writer")
        self.assertEqual(writer.staffing.kind, "on_call")


class SaveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "grok-bot-management").mkdir(parents=True)
        (self.root / "config").mkdir()
        (self.root / "config" / "profile.yaml").write_text('legal_name: "Junyi Zhou"\n', encoding="utf-8")
        self.handoff = self.root / "docs" / "grok-bot-management" / "GROK_BOT_HANDOFF.md"
        self.handoff.write_text("LIVE PASTE\n", encoding="utf-8")
        self.blank = self.root / "docs" / "grok-bot-management" / "ORG_CHART_BLANK.md"
        self.blank.write_text("Company: `_`\n", encoding="utf-8")
        self.designer = OrgDesigner.at(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_writes_json_and_md_not_handoff(self):
        before = self.handoff.read_text(encoding="utf-8")
        blank_before = self.blank.read_text(encoding="utf-8")
        draft = _draft(
            _seat("cos", "Ada", OWNER, order=1, role="Chief of Staff"),
            _seat("ash", "Ashby", "cos", order=2, role="Ashby mind"),
        )
        saved = self.designer.save(SaveDesign(draft=draft, expected_revision=""))
        self.assertFalse(saved.hire_allowed)
        self.assertIn("docs/grok-bot-management/ORG_CHART.json", saved.artifacts)
        self.assertIn("Ada / Chief of Staff", saved.preview.chart)
        self.assertIn("| Ashby |", saved.preview.chart)
        self.assertNotRegex(saved.preview.chart, r"`_`|: _$|: `_`")
        self.assertEqual(self.handoff.read_text(encoding="utf-8"), before)
        self.assertEqual(self.blank.read_text(encoding="utf-8"), blank_before)
        payload = json.loads((self.root / "docs" / "grok-bot-management" / "ORG_CHART.json").read_text())
        self.assertEqual(payload["mode"], "plan_only")
        self.assertEqual(payload["revision"], saved.revision)

    def test_brief_requires_completeness_and_forbids_hire(self):
        draft = _draft(_seat("cos", "Ada", OWNER, role="Chief of Staff"))
        saved = self.designer.save(SaveDesign(draft=draft, expected_revision="", write_brief=True))
        self.assertIsNotNone(saved.preview.brief)
        self.assertIn("Do not create Bots until Test Owner authorizes", saved.preview.brief)
        self.assertIn("END PASTE", saved.preview.brief)
        self.assertFalse(saved.hire_allowed)
        brief_path = self.root / "docs" / "grok-bot-management" / "ORG_SPAWN_BRIEF.md"
        self.assertTrue(brief_path.is_file())

    def test_stale_revision_writes_nothing(self):
        draft = _draft(_seat("cos", "Ada", OWNER))
        self.designer.save(SaveDesign(draft=draft, expected_revision=""))
        with self.assertRaises(RevisionConflict):
            self.designer.save(SaveDesign(draft=draft, expected_revision="stale"))

    def test_vacancy_cannot_save(self):
        snap = self.designer.read("apply-cell")
        with self.assertRaises(DesignRejected) as ctx:
            self.designer.save(SaveDesign(draft=snap.draft, expected_revision=""))
        self.assertTrue(any(i.code == IssueCode.VACANT_ROLE for i in ctx.exception.issues))

    def test_wire_roundtrip(self):
        draft = _draft(_seat("cos", "Ada", OWNER, role="Chief of Staff"))
        again = draft_from_wire(draft_to := {
            **{
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
                        "id": "cos",
                        "bot_name": "Ada",
                        "role": "Chief of Staff",
                        "listens_to": "owner",
                        "does": ["does the job"],
                        "does_not": ["Never Submit."],
                        "staffing": {"kind": "pilot", "order": 1, "detail": ""},
                        "team": "",
                    }
                ],
                "vacancies": [],
                "talks": {
                    "owner_talks_only_to": "cos",
                    "assign_by": "dm",
                    "assign_detail": "",
                    "team_handoff": "Auditor reads the form.",
                },
                "done_when": ["Ready for review."],
            }
        })
        self.assertEqual(again.seats[0].bot_name, "Ada")
        self.assertEqual(draft_to["seats"][0]["bot_name"], "Ada")


if __name__ == "__main__":
    unittest.main()
