from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.home_presenter import present_home_page
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


class HomePresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_home_presenter_is_a_thin_component_assembler(self) -> None:
        page = present_home_page(
            TEMPLATE_RENDERER,
            dashboard={
                "role": "operator",
                "layout_mode": "launchpad",
                "counts": {
                    "read_ready": 1,
                    "drafts": 1,
                    "review_required": 0,
                    "ready_for_review": 0,
                    "needs_decision": 0,
                    "needs_revalidation": 1,
                    "needs_attention": 0,
                    "weak_evidence": 0,
                    "stale": 0,
                    "services": 0,
                    "recent_activity": 1,
                },
                "read_queue": [
                    {
                        "object_id": "kb-home",
                        "title": "Home Guidance",
                        "summary": "Fallback summary",
                        "object_type": "runbook",
                        "ui_projection": {
                            "use_guidance": {
                                "summary": "Projection-backed summary",
                                "safe_to_use": True,
                            }
                        },
                    }
                ],
                "manage": {
                    "draft_items": [],
                    "needs_revalidation": [],
                    "needs_decision": [],
                },
                "services": [],
                "events": [
                    {"what_happened": "Home changed", "next_action": "Open the activity surface."}
                ],
            },
        )

        self.assertEqual(page["page_template"], "pages/home.html")
        self.assertNotIn("home_hero_html", page["page_context"])
        self.assert_component(page["page_context"]["home_launch_html"], "home-launch-block")
        self.assert_component(page["page_context"]["home_activity_html"], "home-activity-block")
