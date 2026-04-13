from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.queue_presenter import (
    present_queue_page,
    render_read_filter_bar,
    queue_item_href,
    render_read_result_cards,
    render_read_selected_context,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


QUEUE_ITEM = {
    "object_id": "kb-test",
    "title": "Test title",
    "summary": "Fallback summary",
    "object_type": "runbook",
    "trust_state": "suspect",
    "revision_review_state": "in_review",
    "reasons": ["review:in_review", "trust:suspect"],
    "owner": "tester",
    "path": "knowledge/runbooks/test.md",
    "citation_health_rank": 1,
    "freshness_rank": 0,
    "linked_services": [{"service_id": "remote-access", "service_name": "Remote Access"}],
    "ui_projection": {
        "use_guidance": {
            "summary": "Review decision pending",
            "detail": "Backend contract says this guidance is still in review.",
            "next_action": "Route the revision through review before use.",
            "safe_to_use": False,
        }
    },
}


class ReadQueuePresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_component_owners_render_traceable_read_surface_markup(self) -> None:
        filter_html = render_read_filter_bar(
            role="operator",
            query="vpn",
            selected_type="runbook",
            selected_trust="suspect",
            selected_review_state="in_review",
        )
        results_html = render_read_result_cards(role="operator", items=[QUEUE_ITEM])
        context_html = render_read_selected_context(role="operator", item=QUEUE_ITEM)

        self.assert_component(filter_html, "read-filter-bar")
        self.assert_component(results_html, "read-result-card")
        self.assert_component(context_html, "read-selected-context")
        self.assertIn("Review decision pending", results_html)
        self.assertIn("Selected context", context_html)

    def test_queue_presenter_assembles_dense_reviewer_surface_with_local_components(self) -> None:
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[QUEUE_ITEM],
            query="vpn",
            selected_type="runbook",
            selected_trust="suspect",
            selected_review_state="in_review",
            role="admin",
            selected_object_id="kb-test",
        )

        workspace_html = page["page_context"]["workspace_html"]
        self.assert_component(workspace_html, "read-filter-bar")
        self.assert_component(workspace_html, "read-results-table")
        self.assert_component(page["aside_html"], "read-selected-context")
        self.assert_surface(workspace_html, "read-queue")
        self.assertEqual(page["page_header"]["headline"], "Inspect")

    def test_queue_presenter_prefers_projection_guidance_over_raw_status_copy(self) -> None:
        item = dict(QUEUE_ITEM)
        item["posture"] = {"trust_summary": "Raw queue fallback should not render."}
        item["ui_projection"] = {
            "use_guidance": {
                "summary": "Projection summary wins",
                "detail": "Projection detail wins",
                "next_action": "Follow the projection-backed next step.",
                "safe_to_use": False,
            }
        }
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[item],
            query="projection",
            selected_type="runbook",
            selected_trust="all",
            selected_review_state="all",
            role="operator",
        )

        workspace_html = page["page_context"]["workspace_html"]
        self.assertIn("Projection summary wins", workspace_html)
        self.assert_component(workspace_html, "read-result-card")
        self.assertNotIn("Raw queue fallback should not render.", workspace_html)

    def test_reader_queue_links_fail_closed_to_reader_object_surface(self) -> None:
        item = dict(QUEUE_ITEM)
        item["current_revision_id"] = "kb-test-rev-1"
        item["ui_projection"] = {
            "actions": [
                {
                    "action_id": "mark_suspect",
                    "label": "Mark suspect",
                    "availability": "allowed",
                }
            ]
        }

        self.assertEqual(queue_item_href(item, role="reader"), "/reader/object/kb-test")
        reader_html = render_read_result_cards(role="reader", items=[item])
        self.assertIn('href="/reader/object/kb-test"', reader_html)
        self.assertNotIn("/operator/review/object/kb-test/suspect", reader_html)
