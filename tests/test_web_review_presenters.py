from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.manage_presenter import present_manage_queue_page
from papyrus.interfaces.web.presenters.review_lane_presenter import render_review_lane
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


QUEUE_ITEM = {
    "object_id": "kb-review",
    "current_revision_id": "kb-review-r1",
    "title": "Review Queue Item",
    "summary": "Needs human review.",
    "change_summary": "Change summary",
    "owner": "reviewer",
    "ui_projection": {
        "use_guidance": {
            "summary": "Review decision pending",
        },
        "reasons": ["review:in_review"],
        "actions": [],
    },
}


class ReviewPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_review_component_owners_render_local_workbench_markup(self) -> None:
        lane_html = render_review_lane(
            role="operator",
            title="Needs decision",
            items=[QUEUE_ITEM],
            active_object_id="kb-review",
            active_revision_id="kb-review-r1",
            action_html_resolver=lambda item: f'<a href="/operator/read/object/{item["object_id"]}">Open</a>',
        )

        self.assert_component(lane_html, "review-lane")
        self.assertIn("Review decision pending", lane_html)

    def test_manage_queue_presenter_assembles_review_surface_from_local_components(self) -> None:
        queue = {
            "cleanup_counts": {"weak-evidence": 1},
            "needs_decision": [QUEUE_ITEM],
            "ready_for_review": [],
            "needs_revalidation": [],
            "draft_items": [],
            "recently_changed": [],
            "superseded_items": [],
        }
        page = present_manage_queue_page(
            TEMPLATE_RENDERER, role="operator", queue=queue, selected_object_id="kb-review"
        )

        tables_html = page["page_context"]["tables_html"]
        self.assertNotIn("overview_html", page["page_context"])
        self.assert_component(tables_html, "review-cleanup-strip")
        self.assert_component(tables_html, "review-lane")
