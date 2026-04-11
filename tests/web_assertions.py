from __future__ import annotations

import re


class SemanticHookAssertions:
    def _hook_fragment(self, attribute: str, value: str) -> str:
        return f'{attribute}="{value}"'

    def assert_surface(self, html: str, surface: str) -> None:
        self.assertIn(self._hook_fragment("data-surface", surface), html)

    def assert_component(self, html: str, component: str) -> None:
        self.assertIn(self._hook_fragment("data-component", component), html)

    def assert_not_component(self, html: str, component: str) -> None:
        self.assertNotIn(self._hook_fragment("data-component", component), html)

    def assert_action_id(self, html: str, action_id: str) -> None:
        self.assertIn(self._hook_fragment("data-action-id", action_id), html)

    def assert_surface_count(self, html: str, surface: str, expected: int) -> None:
        self.assertEqual(html.count(self._hook_fragment("data-surface", surface)), expected)

    def assert_component_count(self, html: str, component: str, expected: int) -> None:
        self.assertEqual(html.count(self._hook_fragment("data-component", component)), expected)

    def assert_action_id_count(self, html: str, action_id: str, expected: int) -> None:
        self.assertEqual(html.count(self._hook_fragment("data-action-id", action_id)), expected)

    def assert_primary_surface(self, html: str, surface: str) -> None:
        pattern = (
            r'<main[^>]*class="[^"]*\bmain-column\b[^"]*"[^>]*'
            + re.escape(self._hook_fragment("data-surface", surface))
        )
        self.assertRegex(html, pattern)

    def assert_required_action_ids(self, html: str, *action_ids: str) -> None:
        for action_id in action_ids:
            self.assert_action_id(html, action_id)

    def assert_page_contract(
        self,
        html: str,
        *,
        primary_surface: str,
        components: tuple[str, ...] = (),
        action_ids: tuple[str, ...] = (),
    ) -> None:
        self.assert_primary_surface(html, primary_surface)
        for component in components:
            self.assert_component(html, component)
        self.assert_required_action_ids(html, *action_ids)
