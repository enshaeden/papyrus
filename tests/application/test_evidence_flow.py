from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.evidence_flow import (
    attach_evidence_snapshot,
    mark_evidence_stale,
    request_evidence_revalidation,
)
from papyrus.application.review_flow import GovernanceWorkflow


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": "Evidence lifecycle test payload.",
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
                "source_title": "Evidence note",
                "source_type": "document",
                "source_ref": "knowledge/system-model.md",
                "note": "Snapshot-managed test evidence.",
                "claim_anchor": None,
                "excerpt": None,
                "captured_at": None,
                "validity_status": "unverified",
                "integrity_hash": None,
                "object_id": None,
                "evidence_snapshot_path": None,
                "evidence_expiry_at": None,
                "evidence_last_validated_at": None,
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "replaced_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "references": [{"title": "Evidence note", "path": "knowledge/system-model.md"}],
        "change_log": [{"date": "2026-04-08", "summary": "Initial draft.", "author": "tests"}],
    }


def ready_runbook_body(
    use_when: str, *, boundaries: str = "Stay within the documented scope."
) -> str:
    return "## Use When\n\n" + use_when + "\n\n## Boundaries And Escalation\n\n" + boundaries + "\n"


class EvidenceFlowTests(unittest.TestCase):
    def test_snapshot_attach_stale_marking_and_revalidation_affect_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_root = Path(temp_dir) / "repo"
            (source_root / "knowledge" / "runbooks").mkdir(parents=True)
            database_path = Path(temp_dir) / "runtime.db"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-evidence-flow",
                object_type="runbook",
                title="Evidence Flow",
                summary="Evidence lifecycle coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/evidence-flow.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(
                    created.object_id, created.canonical_path, created.title
                ),
                body_markdown=ready_runbook_body("Evidence lifecycle coverage."),
                actor="tests",
                change_summary="Evidence lifecycle coverage.",
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
                notes="Approved for evidence lifecycle coverage.",
            )

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                citation_row = connection.execute(
                    """
                    SELECT citation_id
                    FROM citations
                    WHERE revision_id = ?
                    ORDER BY citation_id
                    LIMIT 1
                    """,
                    (revision.revision_id,),
                ).fetchone()
            finally:
                connection.close()
            self.assertIsNotNone(citation_row)
            citation_id = str(citation_row["citation_id"])

            source_file = Path(temp_dir) / "evidence.txt"
            source_file.write_text("captured evidence snapshot", encoding="utf-8")

            snapshot_result = attach_evidence_snapshot(
                database_path=database_path,
                citation_id=citation_id,
                snapshot_source_path=source_file,
                actor="tests",
                expires_at="2026-04-09T00:00:00+00:00",
                root_path=source_root,
            )
            self.assertEqual(snapshot_result.object_id, created.object_id)
            self.assertIsNotNone(snapshot_result.snapshot_path)
            snapshot_path = snapshot_result.snapshot_path
            assert snapshot_path is not None
            self.assertTrue((source_root / snapshot_path).exists())

            stale_result = mark_evidence_stale(
                database_path=database_path,
                citation_id=citation_id,
                actor="tests",
                reason="Snapshot is out of date.",
            )
            self.assertEqual(stale_result.object_id, created.object_id)

            revalidation_result = request_evidence_revalidation(
                database_path=database_path,
                object_id=created.object_id,
                actor="tests",
                notes="Re-run evidence validation.",
            )
            self.assertEqual(revalidation_result.object_id, created.object_id)
            self.assertEqual(revalidation_result.citation_ids, [citation_id])

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                citation_after = connection.execute(
                    """
                    SELECT validity_status, evidence_snapshot_path, evidence_expiry_at, evidence_last_validated_at
                    FROM citations
                    WHERE citation_id = ?
                    """,
                    (citation_id,),
                ).fetchone()
                object_after = connection.execute(
                    """
                    SELECT trust_state
                    FROM knowledge_objects
                    WHERE object_id = ?
                    """,
                    (created.object_id,),
                ).fetchone()
                revalidation_audit = connection.execute(
                    """
                    SELECT event_type
                    FROM audit_events
                    WHERE object_id = ? AND event_type = 'evidence_revalidation_requested'
                    ORDER BY occurred_at DESC
                    LIMIT 1
                    """,
                    (created.object_id,),
                ).fetchone()
            finally:
                connection.close()

            self.assertIsNotNone(citation_after)
            self.assertEqual(citation_after["validity_status"], "stale")
            self.assertIsNotNone(citation_after["evidence_snapshot_path"])
            self.assertIsNotNone(citation_after["evidence_expiry_at"])
            self.assertIsNotNone(citation_after["evidence_last_validated_at"])
            self.assertIsNotNone(object_after)
            self.assertEqual(object_after["trust_state"], "weak_evidence")
            self.assertIsNotNone(revalidation_audit)


if __name__ == "__main__":
    unittest.main()
