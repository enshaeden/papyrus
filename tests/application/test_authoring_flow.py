from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.authoring_flow import (
    create_draft_from_blueprint,
    ensure_draft_revision,
    load_draft_context,
)
from papyrus.application.review_flow import GovernanceWorkflow


def read_count(database_path: Path, query: str, parameters: tuple = ()) -> int:
    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(query, parameters).fetchone()
        return int(row[0] if row is not None else 0)
    finally:
        connection.close()


class AuthoringFlowTests(unittest.TestCase):
    def test_load_draft_context_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            created = workflow.create_object(
                object_id="kb-authoring-load-only",
                object_type="runbook",
                title="Authoring Load Only",
                summary="Load-only draft context coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/authoring-load-only.md",
                actor="tests",
            )
            draft = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            revision_count_before = read_count(
                database_path,
                "SELECT COUNT(*) FROM knowledge_revisions WHERE object_id = ?",
                (created.object_id,),
            )
            audit_count_before = read_count(
                database_path,
                "SELECT COUNT(*) FROM audit_events WHERE object_id = ? AND event_type = 'revision_created'",
                (created.object_id,),
            )

            loaded = load_draft_context(
                object_id=created.object_id,
                revision_id=str(draft["revision_id"]),
                database_path=database_path,
                source_root=source_root,
            )

            self.assertEqual(loaded["revision_id"], draft["revision_id"])
            self.assertEqual(
                read_count(
                    database_path,
                    "SELECT COUNT(*) FROM knowledge_revisions WHERE object_id = ?",
                    (created.object_id,),
                ),
                revision_count_before,
            )
            self.assertEqual(
                read_count(
                    database_path,
                    "SELECT COUNT(*) FROM audit_events WHERE object_id = ? AND event_type = 'revision_created'",
                    (created.object_id,),
                ),
                audit_count_before,
            )

    def test_ensure_draft_revision_reuses_only_compatible_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            created = workflow.create_object(
                object_id="kb-authoring-compatibility",
                object_type="runbook",
                title="Authoring Compatibility",
                summary="Compatible draft reuse coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/authoring-compatibility.md",
                actor="tests",
            )

            first = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            second = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(second["revision_id"], first["revision_id"])

            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    "UPDATE knowledge_revisions SET revision_review_state = 'rejected' WHERE revision_id = ?",
                    (str(first["revision_id"]),),
                )
                connection.commit()
            finally:
                connection.close()

            rejected = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(rejected["revision_id"], first["revision_id"])

            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    "UPDATE knowledge_revisions SET revision_review_state = 'approved' WHERE revision_id = ?",
                    (str(first["revision_id"]),),
                )
                connection.commit()
            finally:
                connection.close()

            approved_follow_up = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            self.assertNotEqual(approved_follow_up["revision_id"], first["revision_id"])

    def test_create_draft_from_blueprint_remains_compatible_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            created = workflow.create_object(
                object_id="kb-authoring-wrapper",
                object_type="runbook",
                title="Authoring Wrapper",
                summary="Wrapper compatibility coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/authoring-wrapper.md",
                actor="tests",
            )

            created_draft = create_draft_from_blueprint(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            ensured_draft = ensure_draft_revision(
                object_id=created.object_id,
                blueprint_id=created.object_type,
                actor="tests",
                database_path=database_path,
                source_root=source_root,
            )
            self.assertEqual(created_draft["revision_id"], ensured_draft["revision_id"])


if __name__ == "__main__":
    unittest.main()
