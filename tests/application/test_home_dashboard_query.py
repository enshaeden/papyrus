from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.queries import home_dashboard
from papyrus.application.review_flow import GovernanceWorkflow


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Home dashboard payload for {title.lower()}",
        "knowledge_object_type": "runbook",
        "legacy_article_type": None,
        "object_lifecycle_state": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": ["Remote Access Gateway"],
        "tags": ["vpn"],
        "created": "2026-04-09",
        "updated": "2026-04-09",
        "last_reviewed": "2026-04-09",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the incident ticket."],
        "steps": ["Perform the remediation step."],
        "verification": ["Confirm the outcome."],
        "rollback": ["Undo the remediation step."],
        "citations": [
            {
                "source_title": "Seed import manifest",
                "source_type": "document",
                "source_ref": "docs/migration/seed-migration-rationale.md",
                "note": "Home dashboard coverage.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": [],
        "references": [{"title": "Seed import manifest", "path": "docs/migration/seed-migration-rationale.md"}],
        "change_log": [{"date": "2026-04-09", "summary": "Initial draft.", "author": "tests"}],
    }


class HomeDashboardQueryTests(unittest.TestCase):
    def test_home_dashboard_returns_actor_scoped_grouped_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            created = workflow.create_object(
                object_id="kb-home-dashboard",
                object_type="runbook",
                title="Home Dashboard",
                summary="Home dashboard query coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/home-dashboard.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
                body_markdown="## Use When\n\nExercise home dashboard query coverage.\n",
                actor="tests",
                change_summary="Home dashboard query coverage.",
            )
            workflow.submit_for_review(object_id=created.object_id, revision_id=revision.revision_id, actor="tests")

            reviewer_dashboard = home_dashboard(actor_id="local.reviewer", database_path=database_path)
            manager_dashboard = home_dashboard(actor_id="local.manager", database_path=database_path)

            self.assertIn("counts", reviewer_dashboard)
            self.assertIn("events", reviewer_dashboard)
            self.assertIn("primary_blocks", reviewer_dashboard)
            self.assertIn("secondary_blocks", reviewer_dashboard)
            self.assertEqual(reviewer_dashboard["actor_id"], "local.reviewer")
            self.assertEqual(manager_dashboard["actor_id"], "local.manager")
            self.assertEqual(reviewer_dashboard["layout_mode"], "review-launchpad")
            self.assertEqual(manager_dashboard["layout_mode"], "pressure-launchpad")
            self.assertEqual(reviewer_dashboard["primary_blocks"][0]["block_id"], "queue_status")
            self.assertEqual(manager_dashboard["primary_blocks"][0]["block_id"], "risk_pressure")


if __name__ == "__main__":
    unittest.main()
