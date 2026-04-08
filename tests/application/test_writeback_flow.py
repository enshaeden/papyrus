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
from papyrus.application.writeback_flow import render_revision_markdown, write_object_to_source
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.paths import FRONT_MATTER_PATTERN


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": "Writeback flow test payload.",
        "knowledge_object_type": "runbook",
        "legacy_article_type": "runbook",
        "status": "active",
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
                "source_title": "Seed manifest",
                "source_type": "document",
                "source_ref": "migration/import-manifest.yml",
                "note": "Deterministic local evidence.",
                "claim_anchor": None,
                "excerpt": None,
                "captured_at": None,
                "validity_status": "verified",
                "integrity_hash": None,
                "article_id": None,
            }
        ],
        "related_object_ids": ["kb-troubleshooting-vpn-connectivity"],
        "superseded_by": None,
        "replaced_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": ["kb-troubleshooting-vpn-connectivity"],
        "references": [{"title": "Seed manifest", "path": "migration/import-manifest.yml"}],
        "change_log": [{"date": "2026-04-08", "summary": "Initial draft.", "author": "tests"}],
    }


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
                normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
                body_markdown="## Use When\n\nUse draft-only coverage.",
                actor="tests",
                change_summary="Draft writeback should fail.",
            )

            with self.assertRaisesRegex(ValueError, "approved revision"):
                write_object_to_source(database_path=database_path, object_id=created.object_id, actor="tests", root_path=source_root)

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
            body_markdown = "## Use When\n\nWriteback is approved.\n"
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=payload,
                body_markdown=body_markdown,
                actor="tests",
                change_summary="Approved writeback coverage.",
            )
            workflow.submit_for_review(object_id=created.object_id, revision_id=revision.revision_id, actor="tests")
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
                actor="tests",
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
            self.assertEqual(body, "## Use When\n\nWriteback is approved.")

            write_object_to_source(database_path=database_path, object_id=created.object_id, actor="tests", root_path=source_root)
            self.assertEqual(target_path.read_text(encoding="utf-8"), expected_text)

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                audit_row = connection.execute(
                    """
                    SELECT event_type, actor, details_json
                    FROM audit_events
                    WHERE object_id = ? AND revision_id = ? AND event_type = 'source_writeback'
                    ORDER BY occurred_at DESC
                    LIMIT 1
                    """,
                    (created.object_id, revision.revision_id),
                ).fetchone()
            finally:
                connection.close()

            self.assertIsNotNone(audit_row)
            self.assertEqual(audit_row["event_type"], "source_writeback")
            self.assertEqual(audit_row["actor"], "tests")
            self.assertIn("knowledge/runbooks/writeback-approved.md", str(audit_row["details_json"]))


if __name__ == "__main__":
    unittest.main()
