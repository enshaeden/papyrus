from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.writeback_flow import (
    preview_revision_writeback,
    render_revision_markdown,
    restore_last_writeback,
    write_object_to_source,
)
from papyrus.infrastructure.transactional_mutation import TransactionalMutation
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.paths import FRONT_MATTER_PATTERN


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": "Writeback flow test payload.",
        "knowledge_object_type": "runbook",
        "object_lifecycle_state": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["<VPN_SERVICE>"],
        "tags": ["vpn"],
        "created": "2026-04-08",
        "updated": "2026-04-08",
        "last_reviewed": "2026-04-08",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the ticket."],
        "steps": ["Execute the operator step."],
        "verification": ["Confirm the expected result."],
        "rollback": ["Undo the operator step."],
        "citations": [
            {
                "source_title": "System model",
                "source_type": "document",
                "source_ref": "knowledge/system-model.md",
                "note": "Deterministic local evidence.",
                "claim_anchor": None,
                "excerpt": None,
                "captured_at": None,
                "validity_status": "verified",
                "integrity_hash": None,
                "object_id": None,
            }
        ],
        "related_object_ids": ["kb-troubleshooting-vpn-connectivity"],
        "superseded_by": None,
        "replaced_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "references": [{"title": "System model", "path": "knowledge/system-model.md"}],
        "change_log": [{"date": "2026-04-08", "summary": "Initial draft.", "author": "tests"}],
    }


def ready_runbook_body(
    use_when: str, *, boundaries: str = "Stay within the documented scope."
) -> str:
    return "## Use When\n\n" + use_when + "\n\n## Boundaries And Escalation\n\n" + boundaries + "\n"


class WritebackFlowTests(unittest.TestCase):
    def test_writeback_requires_approved_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            (source_root / "knowledge" / "runbooks").mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-draft-only",
                object_type="runbook",
                title="Draft Only",
                summary="Draft-only object.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/draft-only.md",
                actor="tests",
            )
            workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(
                    created.object_id, created.canonical_path, created.title
                ),
                body_markdown=ready_runbook_body("Use draft-only coverage."),
                actor="tests",
                change_summary="Draft writeback should fail.",
            )

            with self.assertRaisesRegex(ValueError, "approved revision"):
                write_object_to_source(
                    database_path=database_path,
                    object_id=created.object_id,
                    actor="tests",
                    root_path=source_root,
                )

    def test_approval_writes_deterministic_markdown_and_records_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "writeback-approved.md"
            target_path.parent.mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-approved",
                object_type="runbook",
                title="Writeback Approved",
                summary="Writeback integration object.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/writeback-approved.md",
                actor="tests",
            )
            payload = runbook_payload(created.object_id, created.canonical_path, created.title)
            body_markdown = ready_runbook_body("Writeback is approved.")
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=payload,
                body_markdown=body_markdown,
                actor="tests",
                change_summary="Approved writeback coverage.",
            )
            workflow.submit_for_review(
                object_id=created.object_id, revision_id=revision.revision_id, actor="tests"
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approved for writeback coverage.",
            )

            self.assertTrue(target_path.exists())
            expected_text = render_revision_markdown(
                object_type="runbook",
                metadata=json.loads(json_dump(payload)),
                body_markdown=body_markdown,
            )
            actual_text = target_path.read_text(encoding="utf-8")
            self.assertEqual(actual_text, expected_text)
            match = FRONT_MATTER_PATTERN.match(actual_text)
            self.assertIsNotNone(match)
            metadata = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            self.assertEqual(metadata["id"], created.object_id)
            self.assertEqual(metadata["knowledge_object_type"], "runbook")
            self.assertEqual(metadata["canonical_path"], created.canonical_path)
            self.assertEqual(body, ready_runbook_body("Writeback is approved.").strip())

            write_object_to_source(
                database_path=database_path,
                object_id=created.object_id,
                actor="tests",
                root_path=source_root,
            )
            self.assertEqual(target_path.read_text(encoding="utf-8"), expected_text)

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                audit_rows = connection.execute(
                    """
                    SELECT event_type, actor, details_json
                    FROM audit_events
                    WHERE object_id = ? AND revision_id = ? AND event_type = 'source_writeback'
                    ORDER BY occurred_at ASC
                    """,
                    (created.object_id, revision.revision_id),
                ).fetchall()
            finally:
                connection.close()

            self.assertEqual(len(audit_rows), 2)
            self.assertEqual(audit_rows[0]["event_type"], "source_writeback")
            self.assertEqual(audit_rows[0]["actor"], "local.reviewer")
            self.assertEqual(audit_rows[1]["actor"], "tests")
            first_audit = json.loads(str(audit_rows[0]["details_json"]))
            self.assertIn(
                "knowledge/runbooks/writeback-approved.md", str(audit_rows[0]["details_json"])
            )
            self.assertEqual(first_audit["transition"]["to_state"], "applied")
            self.assertEqual(
                first_audit["required_acknowledgements"], ["canonical_source_will_change"]
            )
            self.assertEqual(first_audit["acknowledgements"], [])
            self.assertIn("policy_decision", first_audit)

    def test_manual_writeback_requires_acknowledgement_when_transition_changes_source_state(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "writeback-manual-ack.md"
            target_path.parent.mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-manual-ack",
                object_type="runbook",
                title="Writeback Manual Ack",
                summary="Manual writeback acknowledgement coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/writeback-manual-ack.md",
                actor="tests",
            )
            payload = runbook_payload(created.object_id, created.canonical_path, created.title)
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=payload,
                body_markdown=ready_runbook_body("Manual acknowledgement coverage."),
                actor="tests",
                change_summary="Approved revision for manual acknowledgement coverage.",
            )
            workflow.submit_for_review(
                object_id=created.object_id, revision_id=revision.revision_id, actor="tests"
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approve for manual acknowledgement coverage.",
            )

            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    """
                    UPDATE knowledge_objects
                    SET source_sync_state = 'not_required'
                    WHERE object_id = ?
                    """,
                    (created.object_id,),
                )
                connection.commit()
            finally:
                connection.close()

            with self.assertRaisesRegex(ValueError, "missing required acknowledgements"):
                write_object_to_source(
                    database_path=database_path,
                    object_id=created.object_id,
                    actor="tests",
                    root_path=source_root,
                )

            result = write_object_to_source(
                database_path=database_path,
                object_id=created.object_id,
                actor="tests",
                root_path=source_root,
                acknowledgements=["canonical_source_will_change"],
            )
            self.assertEqual(result.acknowledgements, ("canonical_source_will_change",))
            self.assertTrue(target_path.exists())

    def test_manual_writeback_recovers_pending_mutation_before_applying(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            pending_target = (
                source_root / "knowledge" / "runbooks" / "pending-writeback-recovery.md"
            )
            pending_target.parent.mkdir(parents=True)
            pending_target.write_text("original pending content\n", encoding="utf-8")

            pending_mutation = TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-writeback-recovery",
                mutation_type="source_writeback",
                object_id="kb-pending-writeback-recovery",
            ).start()
            pending_mutation.stage_write(
                target_path=pending_target,
                previous_text="original pending content\n",
                new_text="interrupted pending content\n",
            )
            pending_mutation.apply_files()
            pending_mutation.close()

            self.assertEqual(
                pending_target.read_text(encoding="utf-8"), "interrupted pending content\n"
            )

            target_path = source_root / "knowledge" / "runbooks" / "writeback-recovery-target.md"
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-recovery-target",
                object_type="runbook",
                title="Writeback Recovery Target",
                summary="Direct writeback recovery coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/writeback-recovery-target.md",
                actor="tests",
            )
            payload = runbook_payload(created.object_id, created.canonical_path, created.title)
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=payload,
                body_markdown=ready_runbook_body("Recovery runs before manual writeback."),
                actor="tests",
                change_summary="Manual writeback recovery coverage.",
            )
            workflow.submit_for_review(
                object_id=created.object_id, revision_id=revision.revision_id, actor="tests"
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approve for direct recovery coverage.",
            )

            result = write_object_to_source(
                database_path=database_path,
                object_id=created.object_id,
                actor="tests",
                root_path=source_root,
                acknowledgements=["canonical_source_will_change"],
            )

            self.assertEqual(result.acknowledgements, ("canonical_source_will_change",))
            self.assertEqual(
                pending_target.read_text(encoding="utf-8"), "original pending content\n"
            )
            self.assertTrue(target_path.exists())

    def test_preview_reports_changed_sections_and_detects_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "writeback-preview.md"
            target_path.parent.mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-preview",
                object_type="runbook",
                title="Writeback Preview",
                summary="Preview integration object.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/writeback-preview.md",
                actor="local.operator",
            )
            initial_payload = runbook_payload(
                created.object_id, created.canonical_path, created.title
            )
            initial_revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=initial_payload,
                body_markdown=ready_runbook_body("Use the original guidance."),
                actor="local.operator",
                change_summary="Seed approved revision.",
            )
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=initial_revision.revision_id,
                actor="local.operator",
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=initial_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.operator",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=initial_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approved seed revision.",
            )

            updated_payload = runbook_payload(
                created.object_id, created.canonical_path, created.title
            )
            updated_payload["summary"] = "Preview the changed guidance before approval."
            preview_revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=updated_payload,
                body_markdown=ready_runbook_body("Use the updated guidance."),
                actor="local.operator",
                change_summary="Preview changed guidance.",
            )

            preview = preview_revision_writeback(
                database_path=database_path,
                object_id=created.object_id,
                revision_id=preview_revision.revision_id,
                root_path=source_root,
            )
            self.assertIn("summary", preview.changed_fields)
            self.assertIn("Use When", preview.changed_sections)
            self.assertFalse(preview.conflict_detected)

            target_path.write_text("manual conflict\n", encoding="utf-8")
            conflicted_preview = preview_revision_writeback(
                database_path=database_path,
                object_id=created.object_id,
                revision_id=preview_revision.revision_id,
                root_path=source_root,
            )
            self.assertTrue(conflicted_preview.conflict_detected)
            self.assertIn(
                "Canonical source changed unexpectedly", str(conflicted_preview.conflict_reason)
            )

    def test_restore_last_writeback_recovers_previous_canonical_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            target_path = (
                source_root / "knowledge" / "runbooks" / "writeback-restore.md"
            ).resolve()
            target_path.parent.mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-writeback-restore",
                object_type="runbook",
                title="Writeback Restore",
                summary="Restore integration object.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/writeback-restore.md",
                actor="local.operator",
            )
            first_payload = runbook_payload(
                created.object_id, created.canonical_path, created.title
            )
            first_body = ready_runbook_body("Use revision one.")
            first_revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=first_payload,
                body_markdown=first_body,
                actor="local.operator",
                change_summary="Approved revision one.",
            )
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=first_revision.revision_id,
                actor="local.operator",
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=first_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.operator",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=first_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approved first revision.",
            )
            first_text = target_path.read_text(encoding="utf-8")

            second_payload = runbook_payload(
                created.object_id, created.canonical_path, created.title
            )
            second_payload["summary"] = "Second approved guidance."
            second_body = ready_runbook_body("Use revision two.")
            second_revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=second_payload,
                body_markdown=second_body,
                actor="local.operator",
                change_summary="Approved revision two.",
            )
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=second_revision.revision_id,
                actor="local.operator",
            )
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=second_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.operator",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=second_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approved second revision.",
            )
            self.assertNotEqual(target_path.read_text(encoding="utf-8"), first_text)

            restore_result = restore_last_writeback(
                database_path=database_path,
                object_id=created.object_id,
                actor="local.manager",
                root_path=source_root,
                acknowledgements=["restore_can_remove_current_canonical_text"],
            )
            self.assertEqual(target_path.read_text(encoding="utf-8"), first_text)
            self.assertIsNotNone(restore_result.backup_path)
            self.assertFalse(restore_result.restored_to_missing)
            self.assertEqual(
                restore_result.acknowledgements,
                ("restore_can_remove_current_canonical_text",),
            )

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                restored_row = connection.execute(
                    """
                    SELECT event_type, actor, details_json
                    FROM audit_events
                    WHERE object_id = ? AND event_type = 'source_writeback_restored'
                    ORDER BY occurred_at DESC
                    LIMIT 1
                    """,
                    (created.object_id,),
                ).fetchone()
            finally:
                connection.close()

            self.assertIsNotNone(restored_row)
            self.assertEqual(restored_row["event_type"], "source_writeback_restored")
            self.assertEqual(restored_row["actor"], "local.manager")
            restored_details = json.loads(str(restored_row["details_json"]))
            self.assertIn(
                "knowledge/runbooks/writeback-restore.md", str(restored_row["details_json"])
            )
            self.assertEqual(restored_details["transition"]["to_state"], "restored")
            self.assertEqual(
                restored_details["required_acknowledgements"],
                ["restore_can_remove_current_canonical_text"],
            )
            self.assertEqual(
                restored_details["acknowledgements"],
                ["restore_can_remove_current_canonical_text"],
            )
            self.assertIn("policy_decision", restored_details)


if __name__ == "__main__":
    unittest.main()
