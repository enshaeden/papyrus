from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.service_map_presenter import render_service_map
from papyrus.interfaces.web.presenters.service_presenter import present_service_catalog, present_service_detail
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


SERVICE = {
    "service_id": "remote-access",
    "service_name": "Remote Access",
    "service_criticality": "high",
    "status": "active",
    "owner": "network",
    "team": "IT Operations",
    "linked_object_count": 2,
    "support_entrypoints": ["VPN client", "SSO portal"],
    "dependencies": ["Identity"],
    "common_failure_modes": ["Certificate drift"],
}


class ServicePresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_service_map_owner_renders_cards_with_local_component_names(self) -> None:
        html = render_service_map(role="operator", services=[SERVICE])

        self.assert_component(html, "service-map")
        self.assert_component(html, "service-map-card")
        self.assertIn("Open service path", html)

    def test_service_presenters_stay_thin_and_traceable(self) -> None:
        catalog_page = present_service_catalog(TEMPLATE_RENDERER, services=[SERVICE], role="operator")
        detail_page = present_service_detail(
            TEMPLATE_RENDERER,
            role="operator",
            detail={
                "service": SERVICE,
                "service_posture": {
                    "linked_object_count": 2,
                    "review_required_count": 1,
                    "degraded_count": 0,
                },
                "canonical_object": None,
                "linked_objects": [
                    {
                        "object_id": "kb-remote-access",
                        "title": "Remote Access Runbook",
                        "relationship_type": "supports",
                        "object_type": "runbook",
                        "path": "knowledge/runbooks/remote-access.md",
                        "trust_state": "trusted",
                        "revision_review_state": "approved",
                    }
                ],
            },
        )

        self.assert_component(catalog_page["page_context"]["services_html"], "service-map")
        detail_html = (
            detail_page["page_context"]["overview_html"]
            + detail_page["page_context"]["linked_objects_html"]
        )
        self.assert_component(detail_html, "service-pressure")
        self.assert_component(detail_html, "service-path")
        self.assertEqual(detail_page["page_header"]["headline"], "Remote Access")
        self.assertEqual(detail_page["page_header"]["kicker"], "high · active")
        self.assertIn("Support entrypoints", detail_page["page_header"]["detail_html"])
