from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.experience import experience_for_role
from papyrus.interfaces.web.view_models.article_projection import build_article_projection


class ArticleProjectionTests(unittest.TestCase):
    def test_operator_projection_keeps_article_sections_ahead_of_governance_context(self) -> None:
        projection = build_article_projection(
            item={
                "object_id": "kb-article",
                "object_type": "runbook",
                "title": "Article Projection",
                "summary": "Operator-readable summary.",
                "owner": "workflow_owner",
                "team": "IT Operations",
                "review_cadence": "quarterly",
                "last_reviewed": "2026-04-11",
                "object_lifecycle_state": "active",
                "trust_state": "trusted",
                "revision_review_state": "approved",
                "systems": ["Remote Access Gateway"],
                "tags": ["vpn"],
            },
            revision={
                "revision_id": "kb-article-r1",
                "revision_number": 1,
                "revision_review_state": "approved",
                "blueprint_id": "runbook",
                "imported_at": "2026-04-11T00:00:00+00:00",
                "change_summary": "Initial projection.",
                "body_markdown": "## Use When\n\nUse this runbook.\n",
            },
            metadata={
                "audience": "service_desk",
                "prerequisites": ["Have the incident ticket."],
                "steps": ["Run the first step."],
                "verification": ["Confirm the result."],
                "rollback": ["Undo the first step."],
            },
            section_content={
                "purpose": {"use_when": "Use this when the VPN gateway is failing."},
                "prerequisites": {"prerequisites": ["Have the incident ticket."]},
                "procedure": {"steps": ["Run the first step."]},
                "verification": {"verification": ["Confirm the result."]},
                "rollback": {"rollback": ["Undo the first step."]},
                "boundaries": {"boundaries_and_escalation": "Escalate if the gateway is degraded."},
            },
            related_services=[
                {
                    "service_id": "remote-access",
                    "service_name": "Remote Access",
                    "service_criticality": "high",
                    "status": "active",
                }
            ],
            citations=[{"source_title": "Gateway SOP", "validity_status": "verified"}],
            evidence_status={
                "summary": "1 citation",
                "total_citations": 1,
                "snapshot_count": 1,
                "revalidation_count": 0,
                "stale_count": 0,
            },
            audit_events=[],
            ui_projection={
                "state": {
                    "trust_state": "trusted",
                    "revision_review_state": "approved",
                    "object_lifecycle_state": "active",
                },
                "use_guidance": {
                    "summary": "Safe to use now",
                    "detail": "Current guidance is approved and trusted.",
                },
            },
            experience=experience_for_role("operator"),
        )

        self.assertEqual(
            [section["section_id"] for section in projection["sections"][:7]],
            [
                "when_to_use",
                "scope",
                "guidance",
                "verification",
                "rollback",
                "escalation",
                "service_context",
            ],
        )
        self.assertEqual(
            [section["section_id"] for section in projection["secondary_sections"]],
            ["governance", "evidence", "source"],
        )
        self.assertFalse(projection["show_context_rail"])

    def test_admin_projection_keeps_audit_context_in_secondary_rail(self) -> None:
        projection = build_article_projection(
            item={
                "object_id": "kb-review-article",
                "object_type": "known_error",
                "title": "Admin Projection",
                "summary": "Admin summary.",
                "owner": "workflow_owner",
                "team": "IT Operations",
                "review_cadence": "after_change",
                "last_reviewed": "2026-04-11",
                "object_lifecycle_state": "active",
                "trust_state": "suspect",
                "revision_review_state": "in_review",
                "systems": [],
                "tags": [],
            },
            revision={
                "revision_id": "kb-review-article-r1",
                "revision_number": 2,
                "revision_review_state": "in_review",
                "blueprint_id": "known_error",
                "imported_at": "2026-04-11T00:00:00+00:00",
                "change_summary": "Queued for review.",
                "body_markdown": "## Escalation Threshold\n\nEscalate if more than one user reports it.\n",
            },
            metadata={},
            section_content={},
            related_services=[],
            citations=[],
            evidence_status={},
            audit_events=[
                {
                    "event_type": "revision_submitted_for_review",
                    "occurred_at": "2026-04-11T01:00:00+00:00",
                    "actor": "tests",
                }
            ],
            ui_projection={
                "state": {
                    "trust_state": "suspect",
                    "revision_review_state": "in_review",
                    "object_lifecycle_state": "active",
                },
                "use_guidance": {
                    "summary": "Review before use",
                    "detail": "Admin inspection context is required.",
                },
            },
            experience=experience_for_role("admin"),
        )

        self.assertTrue(projection["show_context_rail"])
        self.assertEqual(
            [section["section_id"] for section in projection["secondary_sections"]],
            ["governance", "evidence", "audit", "source"],
        )


if __name__ == "__main__":
    unittest.main()
