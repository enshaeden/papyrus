from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.queries import knowledge_object_detail, review_detail
from papyrus.application.review_flow import GovernanceWorkflow


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Contract projection for {title.lower()}",
        "knowledge_object_type": "runbook",
        "legacy_article_type": None,
        "status": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["<VPN_SERVICE>"],
        "tags": ["vpn"],
        "created": "2026-04-09",
        "updated": "2026-04-09",
        "last_reviewed": "2026-04-09",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the incident ticket."],
        "steps": ["Perform the primary remediation step."],
        "verification": ["Confirm the workflow completed successfully."],
        "rollback": ["Undo the last remediation step."],
        "citations": [
            {
                "source_title": "Seed import manifest",
                "source_type": "document",
                "source_ref": "migration/import-manifest.yml",
                "note": "Contract projection evidence.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": [],
        "references": [{"title": "Seed import manifest", "path": "migration/import-manifest.yml"}],
        "change_log": [{"date": "2026-04-09", "summary": "Contract projection draft.", "author": "tests"}],
    }


class QueryContractTests(unittest.TestCase):
    def test_detail_and_review_queries_expose_canonical_ui_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)

            created = workflow.create_object(
                object_id="kb-query-contracts",
                object_type="runbook",
                title="Query Contracts",
                summary="Query contract coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/query-contracts.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
                body_markdown="## Use When\n\nExercise query contract coverage.\n",
                actor="tests",
                change_summary="Initial contract revision.",
            )

            detail = knowledge_object_detail(created.object_id, database_path=database_path)
            detail_actions = {
                action["action_id"]: action
                for action in detail["ui_projection"]["actions"]
            }
            self.assertEqual(detail["ui_projection"]["use_guidance"]["code"], "not_ready")
            self.assertEqual(detail_actions["submit_for_review"]["availability"], "allowed")
            self.assertEqual(detail_actions["archive_object"]["availability"], "illegal")
            self.assertEqual(
                detail_actions["supersede_object"]["policy"]["transition"]["semantics"],
                "allowed_transition",
            )

            workflow.submit_for_review(object_id=created.object_id, revision_id=revision.revision_id, actor="tests")
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )

            review = review_detail(created.object_id, revision.revision_id, database_path=database_path)
            review_actions = {
                action["action_id"]: action
                for action in review["ui_projection"]["actions"]
            }
            self.assertEqual(review["ui_projection"]["use_guidance"]["code"], "review_pending")
            self.assertEqual(review_actions["assign_reviewer"]["availability"], "allowed")
            self.assertEqual(review_actions["approve_revision"]["availability"], "allowed")
            self.assertEqual(review_actions["approve_revision"]["policy"]["transition"]["semantics"], "allowed_transition")
            self.assertEqual(review_actions["reject_revision"]["availability"], "allowed")


if __name__ == "__main__":
    unittest.main()
