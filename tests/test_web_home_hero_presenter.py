from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.home_hero_presenter import render_home_hero
from tests.web_assertions import SemanticHookAssertions


class HomeHeroPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_home_hero_renders_role_owned_copy(self) -> None:
        html = render_home_hero(
            dashboard={
                "role": "admin",
                "layout_mode": "control-room",
            }
        )

        self.assert_component(html, "home-hero")
        self.assert_surface(html, "home")
        self.assertIn("control room", html)
        self.assertIn("Control-plane pressure before item detail.", html)
        self.assertIn("Admin overview surfaces governance pressure", html)
