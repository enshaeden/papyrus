from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.activity_event_list_presenter import render_activity_event_list
from papyrus.interfaces.web.presenters.activity_hero_presenter import render_activity_hero
from papyrus.interfaces.web.presenters.manage_presenter import present_audit_page
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


STRUCTURED_EVENT = {
    "group": "service_changes",
    "occurred_at": "2026-04-09",
    "what_happened": "Remote Access changed",
    "entity_type": "service",
    "entity_id": "remote-access",
    "next_action": "Check linked guidance.",
    "payload": {"summary": "Config changed"},
}


class ActivityPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_activity_component_owners_render_primary_consequence_views(self) -> None:
        hero_html = render_activity_hero(structured_events=[STRUCTURED_EVENT])
        event_html = render_activity_event_list(structured_events=[STRUCTURED_EVENT])

        self.assert_component(hero_html, "activity-hero")
        self.assert_component(event_html, "activity-event")
        self.assertIn("Check linked guidance.", event_html)

    def test_audit_page_presenter_assembles_local_activity_components(self) -> None:
        page = present_audit_page(
            TEMPLATE_RENDERER,
            role="operator",
            events=[{"event_type": "revision_approved", "occurred_at": "2026-04-09T00:00:00+00:00", "actor": "reviewer", "object_id": "kb-test", "revision_id": "kb-test-r1"}],
            structured_events=[STRUCTURED_EVENT],
            validation_runs=[{"run_type": "import", "status": "passed", "finding_count": 0, "completed_at": "2026-04-09T01:00:00+00:00"}],
            object_id=None,
            selected_group="all",
        )

        page_html = (
            page["page_context"]["summary_html"]
            + page["page_context"]["filter_bar_html"]
            + page["page_context"]["event_html"]
            + page["page_context"]["audit_html"]
            + page["page_context"]["validation_html"]
        )
        self.assert_component(page_html, "activity-hero")
        self.assert_component(page_html, "activity-filter-bar")
        self.assert_component(page_html, "activity-event")
        self.assert_component(page_html, "activity-audit-log")
        self.assert_component(page_html, "activity-validation-log")
