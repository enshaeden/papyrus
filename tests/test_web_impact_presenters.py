from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.impact_presenter import present_object_impact, present_service_impact
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


OBJECT_IMPACT = {
    "entity": {"object_id": "kb-test", "title": "Test object"},
    "current_impact": {
        "what_changed": "Procedure updated",
        "why_impacted": "Linked objects inherit the change",
        "revalidate": ["Evidence", "Dependencies"],
    },
    "impacted_objects": [
        {
            "object_id": "kb-dependent",
            "revision_id": "kb-dependent-r2",
            "title": "Dependent object",
            "reason": "Shares the same escalation path",
            "trust_state": "suspect",
            "what_changed": "Escalation path",
            "propagation_path": ["Test object", "Dependent object"],
            "revalidate": ["Procedure"],
        }
    ],
    "recent_events": [
        {
            "occurred_at": "2026-04-10",
            "event_type": "revision_approved",
            "actor": "reviewer",
            "source": "workflow",
            "payload": {"summary": "Approved"},
        }
    ],
    "inbound_relationships": [{"relationship_type": "uses", "object_id": "kb-parent", "title": "Parent object"}],
    "citation_dependents": [{"object_id": "kb-citation", "title": "Citation child", "citation_status": "verified"}],
    "related_services": [{"service_id": "remote-access", "service_name": "Remote Access"}],
}


class ImpactPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_object_impact_presenter_assembles_local_impact_components(self) -> None:
        page = present_object_impact(TEMPLATE_RENDERER, role="operator", impact=OBJECT_IMPACT, selected_object_id="kb-dependent")

        self.assert_component(page["page_context"]["summary_html"], "impact-summary")
        self.assert_component(page["page_context"]["impacts_html"], "impact-trace")
        self.assert_component(page["aside_html"], "impact-profile")
        self.assert_component(page["aside_html"], "impact-selected-item")
        self.assert_component(page["aside_html"], "impact-event-log")
        self.assert_component(page["aside_html"], "impact-relationship-list")

    def test_service_impact_presenter_reuses_traceable_impact_owners(self) -> None:
        page = present_service_impact(
            TEMPLATE_RENDERER,
            role="operator",
            impact={
                "entity": {"service_id": "remote-access", "service_name": "Remote Access"},
                "current_impact": OBJECT_IMPACT["current_impact"],
                "impacted_objects": OBJECT_IMPACT["impacted_objects"],
                "recent_events": OBJECT_IMPACT["recent_events"],
            },
            selected_object_id="kb-dependent",
        )

        self.assert_component(page["page_context"]["summary_html"], "impact-summary")
        self.assert_component(page["page_context"]["impacts_html"], "impact-trace")
        self.assert_component(page["aside_html"], "impact-profile")
        self.assert_component(page["aside_html"], "impact-event-log")
