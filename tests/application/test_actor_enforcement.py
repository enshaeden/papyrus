from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from papyrus.application.commands import (
    approve_revision_command,
    create_object_command,
    create_revision_command,
    record_validation_run_command,
    submit_for_review_command,
)
from papyrus.application.sync_flow import build_search_projection


class ActorEnforcementTests(unittest.TestCase):
    def test_mutating_commands_reject_missing_actor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            build_search_projection(database_path)

            with self.assertRaisesRegex(ValueError, "actor is required"):
                create_object_command(
                    database_path=database_path,
                    source_root=source_root,
                    object_id="kb-missing-actor-object",
                    object_type="runbook",
                    title="Missing Actor",
                    summary="Should fail before mutating state.",
                    owner="ops",
                    team="IT Operations",
                    canonical_path="knowledge/runbooks/missing-actor.md",
                    actor=" ",
                )

    def test_approval_requires_actor_before_audit_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            build_search_projection(database_path)

            created = create_object_command(
                database_path=database_path,
                source_root=source_root,
                object_id="kb-approval-actor-required",
                object_type="runbook",
                title="Approval Actor Required",
                summary="Used to verify actor enforcement.",
                owner="ops",
                team="IT Operations",
                canonical_path="knowledge/runbooks/approval-actor-required.md",
                actor="tests",
            )
            revision = create_revision_command(
                database_path=database_path,
                source_root=source_root,
                object_id=created.object_id,
                normalized_payload={
                    "id": created.object_id,
                    "title": "Approval Actor Required",
                    "canonical_path": created.canonical_path,
                    "summary": "Used to verify actor enforcement.",
                    "knowledge_object_type": "runbook",
                    "status": "draft",
                    "owner": "ops",
                    "source_type": "native",
                    "source_system": "repository",
                    "source_title": "Approval Actor Required",
                    "team": "IT Operations",
                    "systems": ["<VPN_SERVICE>"],
                    "tags": ["vpn"],
                    "created": "2026-04-08",
                    "updated": "2026-04-08",
                    "last_reviewed": "2026-04-08",
                    "review_cadence": "quarterly",
                    "audience": "service_desk",
                    "citations": [
                        {
                            "source_title": "Operator note",
                            "source_type": "document",
                            "source_ref": "docs/reference/system-model.md",
                            "note": "Seed evidence",
                            "claim_anchor": "actor-check",
                            "captured_at": "2026-04-08T00:00:00+00:00",
                            "validity_status": "verified",
                            "integrity_hash": "abc123",
                        }
                    ],
                    "related_object_ids": [],
                    "services": ["Remote Access"],
                    "related_articles": [],
                    "references": [
                        {
                            "title": "Operator note",
                            "path": "docs/reference/system-model.md",
                            "note": "Seed evidence",
                        }
                    ],
                    "change_log": [{"date": "2026-04-08", "summary": "Seed revision.", "author": "tests"}],
                    "related_services": ["Remote Access"],
                    "prerequisites": ["Open ticket."],
                    "steps": ["Run the procedure."],
                    "verification": ["Confirm the outcome."],
                    "rollback": ["Undo the change."],
                },
                body_markdown="## Procedure\n\nRun the procedure.",
                actor="tests",
                legacy_metadata={},
                change_summary="Seed revision.",
            )
            submit_for_review_command(
                database_path=database_path,
                source_root=source_root,
                object_id=created.object_id,
                revision_id=revision.revision_id,
                actor="tests",
            )

            with self.assertRaisesRegex(ValueError, "actor is required"):
                approve_revision_command(
                    database_path=database_path,
                    source_root=source_root,
                    object_id=created.object_id,
                    revision_id=revision.revision_id,
                    reviewer="reviewer_a",
                    actor="",
                )

    def test_audit_events_store_explicit_actor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            build_search_projection(database_path)

            create_object_command(
                database_path=database_path,
                source_root=source_root,
                object_id="kb-actor-audit-check",
                object_type="runbook",
                title="Actor Audit Check",
                summary="Used to verify audit actor persistence.",
                owner="ops",
                team="IT Operations",
                canonical_path="knowledge/runbooks/actor-audit-check.md",
                actor="local.operator",
            )
            record_validation_run_command(
                database_path=database_path,
                run_id="actor-audit-run",
                run_type="manual_check",
                status="passed",
                finding_count=0,
                details={"summary": "Actor audit smoke test"},
                actor="local.reviewer",
            )

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute(
                    """
                    SELECT event_type, actor
                    FROM audit_events
                    WHERE event_type IN ('object_created', 'validation_run_recorded')
                    ORDER BY event_type
                    """
                ).fetchall()
            finally:
                connection.close()

            actors = {str(row["event_type"]): str(row["actor"]) for row in rows}
            self.assertEqual(actors["object_created"], "local.operator")
            self.assertEqual(actors["validation_run_recorded"], "local.reviewer")


if __name__ == "__main__":
    unittest.main()
