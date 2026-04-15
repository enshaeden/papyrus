from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.experience import experience_for_role
from papyrus.interfaces.web.presenters.object_presenter import (
    present_object_detail,
    render_article_context_panel,
    render_article_section,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


DETAIL = {
    "object": {
        "object_id": "kb-test",
        "object_type": "runbook",
        "title": "Test object",
        "summary": "Structured summary.",
        "object_lifecycle_state": "active",
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
        "revision_review_state": "approved",
        "freshness_rank": 0,
        "citation_health_rank": 0,
        "ownership_rank": 0,
        "tags": ["vpn"],
        "systems": ["Remote Access Gateway"],
        "path": "knowledge/runbooks/test.md",
    },
    "ui_projection": {
        "state": {
            "object_lifecycle_state": "active",
            "revision_review_state": "approved",
            "draft_progress_state": "ready_for_review",
            "source_sync_state": "applied",
            "trust_state": "trusted",
        },
        "use_guidance": {
            "summary": "Safe to use now",
            "detail": "The runtime contract marks this object safe for use.",
            "next_action": "Use the current guidance.",
            "safe_to_use": True,
        },
        "reasons": ["review:approved", "trust:trusted"],
        "actions": [],
    },
    "current_revision": {
        "revision_id": "kb-test-rev-1",
        "revision_number": 1,
        "revision_review_state": "approved",
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
            "source_title": "System model",
            "source_type": "document",
            "source_ref": "docs/reference/system-model.md",
            "note": "Evidence",
            "validity_status": "verified",
        }
    ],
    "related_services": [
        {
            "service_id": "remote-access",
            "service_name": "Remote Access",
            "status": "active",
            "service_criticality": "high",
        }
    ],
    "outbound_relationships": [
        {
            "relationship_type": "related_object",
            "object_id": "kb-other",
            "title": "Other object",
            "path": "knowledge/other.md",
            "status": "active",
        }
    ],
    "inbound_relationships": [],
    "audit_events": [
        {
            "event_type": "revision_approved",
            "actor": "reviewer",
            "occurred_at": "2026-04-07T01:00:00+00:00",
            "details": {},
        }
    ],
}


class ObjectDetailPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_component_owners_render_article_markup_locally(self) -> None:
        section_html = render_article_section(
            section={
                "eyebrow": "Use",
                "title": "Procedure",
                "blocks": [{"kind": "paragraph", "text": "Follow the procedure."}],
            }
        )
        context_html = render_article_context_panel(
            section={
                "section_id": "governance",
                "eyebrow": "Context",
                "title": "Linked service context",
                "blocks": [{"kind": "paragraph", "text": "Context stays in the owner."}],
                "raw_markdown": "## Raw",
            }
        )

        self.assert_component(section_html, "article-section")
        self.assert_component(context_html, "article-context-panel")
        self.assertIn("View revision source", context_html)

    def test_object_presenter_assembles_article_surface_from_local_components(self) -> None:
        page = present_object_detail(
            TEMPLATE_RENDERER, detail=DETAIL, experience=experience_for_role("operator")
        )

        article_html = page["page_context"]["article_html"] + page["page_context"]["appendix_html"]
        self.assert_component(article_html, "article-section")
        self.assert_component(article_html, "article-context-panel")
        self.assertIn("Linked service context", article_html)
        self.assertIn("The runtime contract marks this object safe for use.", article_html)
        self.assertEqual(page["page_header"]["headline"], "Test object")
        self.assertEqual(page["page_header"]["kicker"], "runbook · kb-test")
        self.assertEqual(page["page_header"]["intro"], "Structured summary.")
        self.assertIn("See history", page["page_header"]["actions_html"])

    def test_object_presenter_prefers_projection_truth_over_raw_state_fallbacks(self) -> None:
        detail = dict(DETAIL)
        detail["posture"] = {
            "trust_summary": "Raw posture fallback should not render.",
            "trust_detail": "Raw posture detail should not render.",
        }
        detail["ui_projection"] = {
            "state": DETAIL["ui_projection"]["state"],
            "use_guidance": {
                "summary": "Projection says stop and inspect",
                "detail": "Projection-backed detail should appear instead of any raw-state fallback.",
                "next_action": "Review the projection-backed warning.",
                "safe_to_use": False,
            },
            "actions": [],
        }
        page = present_object_detail(
            TEMPLATE_RENDERER, detail=detail, experience=experience_for_role("operator")
        )

        article_html = page["page_context"]["article_html"] + page["page_context"]["appendix_html"]
        self.assertIn("Projection says stop and inspect", article_html)
        self.assertNotIn("Raw posture fallback should not render.", article_html)
