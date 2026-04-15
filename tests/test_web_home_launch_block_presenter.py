from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.home_launch_block_presenter import render_home_launch_blocks
from tests.web_assertions import SemanticHookAssertions


class HomeLaunchBlockPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_operator_launch_blocks_render_in_owner_with_projection_and_actions(self) -> None:
        html = render_home_launch_blocks(
            dashboard={
                "role": "operator",
                "counts": {
                    "read_ready": 1,
                    "drafts": 0,
                    "needs_revalidation": 0,
                    "needs_decision": 0,
                    "ready_for_review": 0,
                    "review_required": 0,
                    "needs_attention": 0,
                    "weak_evidence": 0,
                    "stale": 0,
                    "services": 0,
                    "recent_activity": 0,
                },
                "read_queue": [
                    {
                        "object_id": "kb-vpn",
                        "title": "VPN Troubleshooting",
                        "summary": "Fallback summary",
                        "object_type": "runbook",
                        "ui_projection": {
                            "use_guidance": {
                                "summary": "Use the projection-backed guidance first.",
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
                "events": [],
            }
        )

        self.assert_component_count(html, "home-launch-block", 3)
        self.assert_surface(html, "home")
        self.assertIn("Use the projection-backed guidance first.", html)
        self.assertIn('href="/operator/read/object/kb-vpn"', html)
        self.assertIn("runbook", html)
        self.assertIn("Open", html)
        self.assertIn("Start here", html)
        self.assertIn("View all boards", html)
        self.assertNotIn("home-launch-block__summary", html)
        self.assertNotIn("Fallback summary", html)
        self.assertNotIn("runbook · kb-vpn", html)
        self.assertNotIn('<p class="home-launch-block__kicker">Do now</p>', html)
        self.assertNotIn('<p class="home-launch-block__kicker">Continue</p>', html)
        self.assertNotIn('<p class="home-launch-block__kicker">Watch</p>', html)

    def test_admin_launch_blocks_keep_secondary_block_local_to_component_owner(self) -> None:
        html = render_home_launch_blocks(
            dashboard={
                "role": "admin",
                "counts": {
                    "read_ready": 0,
                    "drafts": 0,
                    "needs_revalidation": 2,
                    "needs_decision": 1,
                    "ready_for_review": 3,
                    "review_required": 4,
                    "needs_attention": 0,
                    "weak_evidence": 0,
                    "stale": 0,
                    "services": 0,
                    "recent_activity": 2,
                },
                "read_queue": [],
                "manage": {
                    "draft_items": [],
                    "needs_revalidation": [],
                    "needs_decision": [],
                },
                "services": [],
                "events": [
                    {
                        "what_happened": "Review approval reopened",
                        "next_action": "Inspect the queue.",
                        "entity_type": "revision",
                    }
                ],
            }
        )

        self.assert_component_count(html, "home-launch-block", 4)
        self.assert_component(html, "home-board-links")
        self.assertIn("Pressure summary", html)
        self.assertIn("View all boards", html)
        self.assertNotIn("home-board-links__summary", html)
        self.assertNotIn("Recent changes", html)
        self.assertNotIn('<p class="home-launch-block__kicker">Queue status</p>', html)
        self.assertNotIn('<p class="home-launch-block__kicker">Pending decisions</p>', html)
        self.assertNotIn('<p class="home-launch-block__kicker">Blocked reviews</p>', html)
        self.assertNotIn('<p class="home-launch-block__kicker">Pressure summary</p>', html)
