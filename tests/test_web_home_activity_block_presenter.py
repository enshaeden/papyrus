from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.home_activity_block_presenter import (
    render_home_activity_block,
)
from tests.web_assertions import SemanticHookAssertions


class HomeActivityBlockPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_home_activity_block_renders_operator_events_with_next_actions(self) -> None:
        html = render_home_activity_block(
            dashboard={
                "role": "operator",
                "events": [
                    {
                        "what_happened": "VPN guidance changed",
                        "next_action": "Re-open the article before use.",
                    },
                    {
                        "what_happened": "Ignored event",
                        "next_action": "",
                    },
                ],
            }
        )

        self.assert_component(html, "home-activity-block")
        self.assert_surface(html, "home")
        self.assertIn("VPN guidance changed", html)
        self.assertIn("Re-open the article before use.", html)
        self.assertNotIn("Ignored event", html)

    def test_home_activity_block_is_not_rendered_for_non_operator_actors(self) -> None:
        html = render_home_activity_block(
            dashboard={
                "role": "admin",
                "events": [{"what_happened": "Event", "next_action": "Inspect"}],
            }
        )

        self.assertEqual(html, "")

    def test_home_activity_block_keeps_empty_summary_for_operator_without_events(self) -> None:
        html = render_home_activity_block(dashboard={"role": "operator", "events": []})

        self.assert_component(html, "home-activity-block")
        self.assertIn("No consequential changes are active right now.", html)
        self.assertNotIn("Only changes that materially alter today’s next move stay on Home.", html)
        self.assertNotIn("Open the full activity surface for recent decisions", html)
