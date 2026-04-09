from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.authoring_flow import create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.commands import create_object_command


class AuthoringFlowTests(unittest.TestCase):
    def test_blueprint_draft_progress_moves_to_ready_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            create_object_command(
                database_path=database_path,
                source_root=source_root,
                actor="local.operator",
                object_id="kb-blueprint-runbook",
                object_type="runbook",
                title="Blueprint Runbook",
                summary="Guided blueprint coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/blueprint-runbook.md",
                review_cadence="quarterly",
                status="draft",
            )
            created = create_draft_from_blueprint(
                object_id="kb-blueprint-runbook",
                blueprint_id="runbook",
                actor="local.operator",
                database_path=database_path,
                source_root=source_root,
            )
            revision_id = str(created["revision_id"])
            self.assertIn(created["completion"]["draft_state"], {"blocked", "in_progress"})

            updates = {
                "purpose": {"use_when": "Use this when the operator needs guided recovery."},
                "prerequisites": {"prerequisites": ["Open the incident ticket."]},
                "procedure": {"steps": ["Validate the precondition.", "Apply the fix."]},
                "verification": {"verification": ["Confirm the service recovers."]},
                "rollback": {"rollback": ["Undo the applied fix."]},
                "boundaries": {"boundaries_and_escalation": "Escalate after two failed attempts.", "related_knowledge_notes": ""},
                "evidence": {"citations": [{"source_title": "Controlled reference", "source_type": "document", "source_ref": "docs/playbooks/write.md", "note": "Governed internal evidence."}]},
            }
            for section_id, values in updates.items():
                update_section(
                    object_id="kb-blueprint-runbook",
                    revision_id=revision_id,
                    section_id=section_id,
                    values=values,
                    actor="local.operator",
                    database_path=database_path,
                    source_root=source_root,
                )

            progress = validate_draft_progress(
                object_id="kb-blueprint-runbook",
                revision_id=revision_id,
                database_path=database_path,
            )
            self.assertEqual(progress["completion"]["draft_state"], "ready_for_review")
            self.assertEqual(progress["completion"]["completion_percentage"], 100)
