from __future__ import annotations

import copy
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.impact_flow import mark_object_suspect_due_to_change
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.sync_flow import build_search_projection
from papyrus.application.validation_flow import record_validation_run
from papyrus.infrastructure.markdown.parser import parse_knowledge_document
from papyrus.infrastructure.transactional_mutation import TransactionalMutation
from tests.source_workspace import copy_fixture_source_workspace, fixture_source_root


def read_row(database_path: Path, query: str, parameters: tuple = ()) -> sqlite3.Row | None:
    connection = sqlite3.connect(database_path)
    try:
        connection.row_factory = sqlite3.Row
        return connection.execute(query, parameters).fetchone()
    finally:
        connection.close()


def read_rows(database_path: Path, query: str, parameters: tuple = ()) -> list[sqlite3.Row]:
    connection = sqlite3.connect(database_path)
    try:
        connection.row_factory = sqlite3.Row
        return connection.execute(query, parameters).fetchall()
    finally:
        connection.close()


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Runbook for {title.lower()}",
        "knowledge_object_type": "runbook",
        "object_lifecycle_state": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["<VPN_SERVICE>"],
        "tags": ["vpn"],
        "created": "2026-04-07",
        "updated": "2026-04-07",
        "last_reviewed": "2026-04-07",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the incident ticket."],
        "steps": ["Perform the primary remediation step."],
        "verification": ["Confirm the workflow completed successfully."],
        "rollback": ["Undo the last remediation step."],
        "citations": [
            {
                "source_title": "System model",
                "source_type": "document",
                "source_ref": "knowledge/system-model.md",
                "note": "Used as an internal provenance placeholder for the test.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "references": [{"title": "System model", "path": "knowledge/system-model.md"}],
        "change_log": [{"date": "2026-04-07", "summary": "Initial draft.", "author": "tests"}],
    }


def ready_runbook_body(
    use_when: str,
    *,
    boundaries: str = "Stay within the documented workflow boundary and escalate when scope changes.",
) -> str:
    return "## Use When\n\n" + use_when + "\n\n## Boundaries And Escalation\n\n" + boundaries + "\n"


class GovernanceWorkflowTests(unittest.TestCase):
    def test_source_mutation_review_operations_recover_pending_workspace_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())
            source_root = Path(temp_dir) / "repo"
            pending_target = (
                source_root / "knowledge" / "runbooks" / "pending-governance-recovery.md"
            )
            pending_target.parent.mkdir(parents=True, exist_ok=True)
            pending_target.write_text("original review content\n", encoding="utf-8")

            pending_mutation = TransactionalMutation(
                source_root=source_root,
                mutation_id="mutation-governance-recovery",
                mutation_type="archive",
                object_id="kb-governance-recovery",
            ).start()
            pending_mutation.stage_write(
                target_path=pending_target,
                previous_text="original review content\n",
                new_text="interrupted review content\n",
            )
            pending_mutation.apply_files()
            pending_mutation.close()

            self.assertEqual(
                pending_target.read_text(encoding="utf-8"), "interrupted review content\n"
            )

            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            self.assertEqual(
                pending_target.read_text(encoding="utf-8"), "interrupted review content\n"
            )

            created = workflow.create_object(
                object_id="kb-governance-recovery-target",
                object_type="runbook",
                title="Governance Recovery Target",
                summary="Workflow constructor recovery coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/governance-recovery-target.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(
                    created.object_id, created.canonical_path, created.title
                ),
                body_markdown=ready_runbook_body(
                    "Recover pending review mutations before approval."
                ),
                actor="tests",
                change_summary="Governance recovery coverage.",
            )
            workflow.submit_for_review(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                actor="tests",
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
            )

            self.assertEqual(
                pending_target.read_text(encoding="utf-8"), "original review content\n"
            )
            self.assertEqual(created.object_id, "kb-governance-recovery-target")

    def test_existing_object_revision_review_flow_updates_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())
            source_root = Path(temp_dir) / "repo"
            copy_fixture_source_workspace(source_root)
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            document = parse_knowledge_document(
                fixture_source_root() / "knowledge" / "troubleshooting" / "vpn-connectivity.md"
            )
            payload = copy.deepcopy(document.metadata)
            payload["summary"] = "Diagnose VPN failures with explicit workflow review coverage."
            payload["change_log"] = [
                *payload["change_log"],
                {
                    "date": "2026-04-07",
                    "summary": "Workflow review test revision.",
                    "author": "tests",
                },
            ]
            revision = workflow.create_revision(
                object_id=payload["id"],
                normalized_payload=payload,
                body_markdown=f"{document.body}\n\nWorkflow review test note.",
                actor="tests",
                legacy_metadata=document.metadata,
                change_summary="Workflow review test revision.",
            )
            workflow.submit_for_review(
                object_id=payload["id"], revision_id=revision.revision_id, actor="tests"
            )
            assignment = workflow.assign_reviewer(
                object_id=payload["id"],
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
                notes="Review the updated diagnostic wording.",
            )
            approved = workflow.approve_revision(
                object_id=payload["id"],
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approved during test execution.",
            )

            revision_row = read_row(
                database_path,
                "SELECT revision_review_state, revision_number FROM knowledge_revisions WHERE revision_id = ?",
                (approved.revision_id,),
            )
            self.assertIsNotNone(revision_row)
            self.assertEqual(revision_row["revision_review_state"], "approved")
            self.assertGreater(revision_row["revision_number"], 1)

            assignment_row = read_row(
                database_path,
                "SELECT state, reviewer FROM review_assignments WHERE assignment_id = ?",
                (assignment.assignment_id,),
            )
            self.assertIsNotNone(assignment_row)
            self.assertEqual(assignment_row["state"], "approved")
            self.assertEqual(assignment_row["reviewer"], "reviewer_a")

            search_row = read_row(
                database_path,
                "SELECT revision_id, revision_review_state FROM search_documents WHERE object_id = ?",
                (payload["id"],),
            )
            self.assertIsNotNone(search_row)
            self.assertEqual(search_row["revision_id"], approved.revision_id)
            self.assertEqual(search_row["revision_review_state"], "approved")

            audit_event_types = {
                row["event_type"]
                for row in read_rows(
                    database_path,
                    "SELECT event_type FROM audit_events WHERE object_id = ?",
                    (payload["id"],),
                )
            }
            self.assertIn("revision_created", audit_event_types)
            self.assertIn("revision_submitted_for_review", audit_event_types)
            self.assertIn("reviewer_assigned", audit_event_types)
            self.assertIn("revision_approved", audit_event_types)

    def test_runtime_created_objects_support_reject_supersede_suspect_and_validation_run(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            object_a = workflow.create_object(
                object_id="kb-runbook-phase5-a",
                object_type="runbook",
                title="Phase 5 Workflow A",
                summary="Object A for governance workflow testing.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/phase5-a.md",
                actor="tests",
            )
            object_b = workflow.create_object(
                object_id="kb-runbook-phase5-b",
                object_type="runbook",
                title="Phase 5 Workflow B",
                summary="Object B for governance workflow testing.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/phase5-b.md",
                actor="tests",
            )

            revision_a = workflow.create_revision(
                object_id=object_a.object_id,
                normalized_payload=runbook_payload(
                    object_a.object_id, object_a.canonical_path, object_a.title
                ),
                body_markdown=ready_runbook_body("Execute workflow A."),
                actor="tests",
                change_summary="Initial workflow A revision.",
            )
            workflow.submit_for_review(
                object_id=object_a.object_id, revision_id=revision_a.revision_id, actor="tests"
            )
            workflow.assign_reviewer(
                object_id=object_a.object_id,
                revision_id=revision_a.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.reject_revision(
                object_id=object_a.object_id,
                revision_id=revision_a.revision_id,
                reviewer="reviewer_a",
                actor="tests",
                notes="Rejected during workflow testing.",
            )

            revision_b = workflow.create_revision(
                object_id=object_b.object_id,
                normalized_payload=runbook_payload(
                    object_b.object_id, object_b.canonical_path, object_b.title
                ),
                body_markdown=ready_runbook_body("Execute workflow B."),
                actor="tests",
                change_summary="Initial workflow B revision.",
            )
            workflow.submit_for_review(
                object_id=object_b.object_id, revision_id=revision_b.revision_id, actor="tests"
            )
            workflow.assign_reviewer(
                object_id=object_b.object_id,
                revision_id=revision_b.revision_id,
                reviewer="reviewer_b",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=object_b.object_id,
                revision_id=revision_b.revision_id,
                reviewer="reviewer_b",
                actor="local.reviewer",
                notes="Approved during workflow testing.",
            )

            citation_row = read_row(
                database_path,
                "SELECT COUNT(*) AS item_count, MIN(validity_status) AS validity_status FROM citations WHERE revision_id = ?",
                (revision_b.revision_id,),
            )
            self.assertIsNotNone(citation_row)
            self.assertEqual(citation_row["item_count"], 1)
            self.assertEqual(citation_row["validity_status"], "unverified")

            search_row = read_row(
                database_path,
                "SELECT trust_state, citation_health_rank, revision_review_state FROM search_documents WHERE object_id = ?",
                (object_b.object_id,),
            )
            self.assertIsNotNone(search_row)
            self.assertEqual(search_row["revision_review_state"], "approved")
            self.assertEqual(search_row["citation_health_rank"], 1)
            self.assertEqual(search_row["trust_state"], "weak_evidence")

            workflow.supersede_object(
                object_id=object_a.object_id,
                replacement_object_id=object_b.object_id,
                actor="tests",
                notes="Object B replaces object A.",
            )
            mark_object_suspect_due_to_change(
                database_path=database_path,
                object_id=object_b.object_id,
                actor="tests",
                reason="Related service changed during test execution.",
                changed_entity_type="service",
                changed_entity_id="remote-access",
            )
            record_validation_run(
                database_path=database_path,
                run_id="phase5-validation-run",
                run_type="workflow_test",
                status="passed",
                finding_count=0,
                details={"suite": "test_governance_workflow"},
                actor="tests",
            )

            object_a_row = read_row(
                database_path,
                "SELECT object_lifecycle_state FROM knowledge_objects WHERE object_id = ?",
                (object_a.object_id,),
            )
            self.assertIsNotNone(object_a_row)
            self.assertEqual(object_a_row["object_lifecycle_state"], "deprecated")

            relationship_row = read_row(
                database_path,
                """
                SELECT relationship_type, target_entity_id
                FROM relationships
                WHERE source_entity_id = ? AND provenance = 'workflow'
                """,
                (object_a.object_id,),
            )
            self.assertIsNotNone(relationship_row)
            self.assertEqual(relationship_row["relationship_type"], "superseded_by")
            self.assertEqual(relationship_row["target_entity_id"], object_b.object_id)

            suspect_row = read_row(
                database_path,
                "SELECT trust_state FROM knowledge_objects WHERE object_id = ?",
                (object_b.object_id,),
            )
            self.assertIsNotNone(suspect_row)
            self.assertEqual(suspect_row["trust_state"], "suspect")

            validation_row = read_row(
                database_path,
                "SELECT run_type, status FROM validation_runs WHERE run_id = ?",
                ("phase5-validation-run",),
            )
            self.assertIsNotNone(validation_row)
            self.assertEqual(validation_row["run_type"], "workflow_test")
            self.assertEqual(validation_row["status"], "passed")

            audit_event_types = {
                row["event_type"]
                for row in read_rows(database_path, "SELECT event_type FROM audit_events")
            }
            self.assertIn("object_created", audit_event_types)
            self.assertIn("revision_rejected", audit_event_types)
            self.assertIn("object_superseded", audit_event_types)
            self.assertIn("object_marked_suspect_due_to_change", audit_event_types)
            self.assertIn("validation_run_recorded", audit_event_types)

    def test_approval_rolls_back_source_sync_when_later_approval_audit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            source_root = Path(temp_dir) / "repo"
            target_path = source_root / "knowledge" / "runbooks" / "approval-rollback.md"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-approval-rollback",
                object_type="runbook",
                title="Approval Rollback",
                summary="Rollback coverage for approval.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/approval-rollback.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(
                    created.object_id, created.canonical_path, created.title
                ),
                body_markdown=ready_runbook_body("Exercise rollback."),
                actor="tests",
                change_summary="Approval rollback coverage.",
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

            original_insert_audit_event = __import__(
                "papyrus.application.review_flow", fromlist=["insert_audit_event"]
            ).insert_audit_event

            def fail_revision_approved(connection, *, event_type, **kwargs):
                if event_type == "revision_approved":
                    raise RuntimeError("forced approval audit failure")
                return original_insert_audit_event(connection, event_type=event_type, **kwargs)

            with mock.patch(
                "papyrus.application.review_flow.insert_audit_event",
                side_effect=fail_revision_approved,
            ):
                with self.assertRaisesRegex(RuntimeError, "forced approval audit failure"):
                    workflow.approve_revision(
                        object_id=created.object_id,
                        revision_id=revision.revision_id,
                        reviewer="reviewer_a",
                        actor="local.reviewer",
                        notes="Should roll back.",
                    )

            self.assertFalse(target_path.exists())
            revision_row = read_row(
                database_path,
                "SELECT revision_review_state FROM knowledge_revisions WHERE revision_id = ?",
                (revision.revision_id,),
            )
            object_row = read_row(
                database_path,
                "SELECT object_lifecycle_state, source_sync_state, current_revision_id FROM knowledge_objects WHERE object_id = ?",
                (created.object_id,),
            )
            audit_types = {
                row["event_type"]
                for row in read_rows(
                    database_path,
                    "SELECT event_type FROM audit_events WHERE object_id = ?",
                    (created.object_id,),
                )
            }
            self.assertEqual(revision_row["revision_review_state"], "in_review")
            self.assertEqual(object_row["object_lifecycle_state"], "active")
            self.assertEqual(object_row["source_sync_state"], "not_required")
            self.assertEqual(object_row["current_revision_id"], revision.revision_id)
            self.assertNotIn("revision_approved", audit_types)
            self.assertNotIn("source_writeback", audit_types)

    def test_sync_preserves_runtime_suspect_state_for_unchanged_source_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())

            object_id = "kb-troubleshooting-vpn-connectivity"
            mark_object_suspect_due_to_change(
                database_path=database_path,
                object_id=object_id,
                actor="tests",
                reason="Gateway configuration changed outside the repository.",
                changed_entity_type="service",
                changed_entity_id="remote-access",
            )
            build_search_projection(database_path, workspace_root=fixture_source_root())

            object_row = read_row(
                database_path,
                "SELECT trust_state FROM knowledge_objects WHERE object_id = ?",
                (object_id,),
            )
            self.assertIsNotNone(object_row)
            self.assertEqual(object_row["trust_state"], "suspect")

            search_row = read_row(
                database_path,
                "SELECT trust_state, revision_review_state FROM search_documents WHERE object_id = ?",
                (object_id,),
            )
            self.assertIsNotNone(search_row)
            self.assertEqual(search_row["trust_state"], "suspect")
            self.assertEqual(search_row["revision_review_state"], "approved")


if __name__ == "__main__":
    unittest.main()
