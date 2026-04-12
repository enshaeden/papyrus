from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    render_acknowledgement_panel,
    render_action_contract_panel,
    render_workflow_projection_panel,
)
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


class WebPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_component_presenter_splits_flat_content_and_bordered_context(self) -> None:
        components = ComponentPresenter(TEMPLATE_RENDERER)

        content_html = components.content_section(
            title="Primary content",
            eyebrow="Read",
            body_html="<p>Flat reading section.</p>",
            surface="test-surface",
        )
        context_html = components.context_panel(
            title="Context",
            eyebrow="Metadata",
            body_html="<p>Bordered support panel.</p>",
            surface="test-surface",
        )

        self.assertIn('class="section-card content-section', content_html)
        self.assertIn('class="section-card context-panel', context_html)
        self.assert_component(content_html, "surface-panel")
        self.assert_component(context_html, "surface-panel")

    def test_governed_panels_render_operator_message_and_acknowledgements(self) -> None:
        components = ComponentPresenter(TEMPLATE_RENDERER)
        forms = FormPresenter(TEMPLATE_RENDERER)

        action_html = render_action_contract_panel(
            components,
            title="Archive contract",
            action={
                "label": "Archive object",
                "summary": "Archive deprecated guidance.",
                "detail": "Papyrus will move the canonical file under archive/knowledge before completing this action.",
                "availability": "allowed",
                "policy": {
                    "transition": {
                        "from_state": "deprecated",
                        "to_state": "archived",
                        "semantics": "allowed",
                    },
                    "required_acknowledgements": ["canonical_path_will_move_to_archive"],
                },
            },
        )
        acknowledgement_html = render_acknowledgement_panel(
            components,
            forms,
            title="Required acknowledgements",
            required_acknowledgements=["canonical_path_will_move_to_archive"],
            selected_acknowledgements=[],
            operator_message="Review the archive acknowledgement before continuing.",
        )

        self.assert_component(action_html, "surface-panel")
        self.assert_surface(action_html, "contract")
        self.assertIn("Papyrus will move the canonical file under archive/knowledge", action_html)
        self.assert_surface(acknowledgement_html, "acknowledgements")
        self.assertIn("Review the archive acknowledgement before continuing.", acknowledgement_html)
        self.assertIn("canonical path will move to archive", acknowledgement_html)

    def test_workflow_projection_panel_renders_rows_warnings_and_operator_message(self) -> None:
        components = ComponentPresenter(TEMPLATE_RENDERER)
        html = render_workflow_projection_panel(
            components,
            title="Draft readiness contract",
            projection={
                "summary": "Draft has blocking gaps",
                "detail": "Required sections are still incomplete.",
                "operator_message": "Continue guided authoring before routing this revision into review.",
                "tone": "warning",
                "rows": [
                    {"label": "Draft progress", "value": "blocked"},
                    {"label": "Next section", "value": "Procedure"},
                ],
                "warnings": ["References: 1 external/manual citation remains weak."],
                "reasons": ["Verification: This field is required."],
            },
        )
        self.assert_component(html, "surface-panel")
        self.assert_surface(html, "workflow")
        self.assertIn("Continue guided authoring before routing this revision into review.", html)
        self.assertIn("References: 1 external/manual citation remains weak.", html)
        self.assertIn("Verification: This field is required.", html)


if __name__ == "__main__":
    unittest.main()
