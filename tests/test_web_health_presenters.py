from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.dashboard_presenter import present_oversight_dashboard
from papyrus.interfaces.web.presenters.dashboard_presenter import render_oversight_board
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


QUEUE_ITEM = {
    "object_id": "kb-review",
    "title": "Review Queue Item",
    "object_type": "runbook",
    "revision_review_state": "in_review",
    "trust_state": "suspect",
    "current_revision_id": "kb-review-r1",
    "owner": "team",
    "ui_projection": {
        "state": {
            "trust_state": "suspect",
            "revision_review_state": "in_review",
        },
        "use_guidance": {
            "summary": "Review decision pending",
            "detail": "Papyrus requires a review decision before use.",
            "next_action": "Review the decision.",
            "safe_to_use": False,
        },
    },
}


class HealthPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_oversight_board_owner_groups_interventions_locally(self) -> None:
        html = render_oversight_board(role="operator", queue=[QUEUE_ITEM])

        self.assert_component(html, "oversight-board")
        self.assert_component(html, "oversight-column")
        self.assert_component(html, "oversight-card")
        self.assertIn('class="oversight-board__grid"', html)
        self.assertIn("Review the decision.", html)

    def test_dashboard_presenter_assembles_health_components(self) -> None:
        page = present_oversight_dashboard(
            TEMPLATE_RENDERER,
            role="operator",
            dashboard={
                "queue": [QUEUE_ITEM],
                "cleanup_counts": {"placeholder-heavy": 1},
                "validation_posture": {
                    "summary": "Latest validation: import",
                    "detail": "Most recent validation passed.",
                },
            },
        )

        board_html = page["page_context"]["summary_cards_html"]
        self.assert_component(board_html, "oversight-board")
        self.assert_component(board_html, "oversight-cleanup-board")
        self.assert_component(board_html, "oversight-validation-board")
