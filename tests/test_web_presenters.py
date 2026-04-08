from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.object_presenter import present_object_detail
from papyrus.interfaces.web.presenters.queue_presenter import present_queue_page
from papyrus.interfaces.web.rendering import TemplateRenderer


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


class WebPresenterTests(unittest.TestCase):
    def test_queue_presenter_keeps_trust_and_filters_visible(self) -> None:
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[
                {
                    "object_id": "kb-test",
                    "title": "Test title",
                    "object_type": "runbook",
                    "trust_state": "suspect",
                    "approval_state": "in_review",
                    "reasons": ["approval:in_review", "trust:suspect"],
                    "owner": "tester",
                    "path": "knowledge/runbooks/test.md",
                    "citation_health_rank": 1,
                    "freshness_rank": 0,
                }
            ],
            query="vpn",
            selected_type="runbook",
            selected_trust="suspect",
            selected_approval="in_review",
        )
        self.assertEqual(page["page_title"], "Knowledge Queue")
        self.assertIn("Queue posture", page["aside_html"])
        self.assertIn("Queue filters", page["page_context"]["filter_bar_html"])
        self.assertIn("approval:in_review", page["page_context"]["queue_html"])

    def test_object_presenter_surfaces_citations_relationships_and_audit(self) -> None:
        page = present_object_detail(
            TEMPLATE_RENDERER,
            detail={
                "object": {
                    "object_id": "kb-test",
                    "object_type": "runbook",
                    "title": "Test object",
                    "summary": "Structured summary.",
                    "status": "active",
                    "owner": "tester",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/test.md",
                    "source_type": "native",
                    "source_system": "repository",
                    "source_title": "Test object",
                    "created_date": "2026-04-07",
                    "updated_date": "2026-04-07",
                    "last_reviewed": "2026-04-07",
                    "review_cadence": "quarterly",
                    "trust_state": "trusted",
                    "approval_state": "approved",
                    "freshness_rank": 0,
                    "citation_health_rank": 0,
                    "ownership_rank": 0,
                    "tags": ["vpn"],
                    "systems": ["<VPN_SERVICE>"],
                    "path": "knowledge/runbooks/test.md",
                },
                "current_revision": {
                    "revision_id": "kb-test-rev-1",
                    "revision_number": 1,
                    "revision_state": "approved",
                    "imported_at": "2026-04-07T00:00:00+00:00",
                    "change_summary": "Initial",
                    "body_markdown": "## Use When\n\nUse the runbook.",
                },
                "metadata": {
                    "prerequisites": ["Have the ticket."],
                    "steps": ["Run the step."],
                    "verification": ["Confirm the result."],
                    "rollback": ["Undo the step."],
                },
                "citations": [
                    {
                        "source_title": "Seed manifest",
                        "source_type": "document",
                        "source_ref": "migration/import-manifest.yml",
                        "note": "Evidence",
                        "validity_status": "verified",
                    }
                ],
                "related_services": [{"service_id": "remote-access", "service_name": "Remote Access", "status": "active", "service_criticality": "high"}],
                "outbound_relationships": [{"relationship_type": "related_object", "object_id": "kb-other", "title": "Other object", "path": "knowledge/other.md", "status": "active"}],
                "inbound_relationships": [],
                "audit_events": [{"event_type": "revision_approved", "actor": "reviewer", "occurred_at": "2026-04-07T01:00:00+00:00", "details": {}}],
            },
        )
        self.assertIn("Supporting citations", page["page_context"]["related_sections_html"])
        self.assertIn("Related services", page["page_context"]["related_sections_html"])
        self.assertIn("Recent audit", page["aside_html"])


if __name__ == "__main__":
    unittest.main()
