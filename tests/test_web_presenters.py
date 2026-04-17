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
    render_projection_status_panel,
    render_workflow_projection_panel,
)
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import PageRenderer, TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")
PAGE_RENDERER = PageRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web")


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
            summary="Decorative summary",
            surface="test-surface",
        )

        self.assertIn('class="section-card content-section', content_html)
        self.assertIn('class="section-card context-panel', context_html)
        self.assert_component(content_html, "surface-panel")
        self.assert_component(context_html, "surface-panel")
        self.assertNotIn("Decorative summary", context_html)

    def test_component_presenter_collapses_duplicate_eyebrow_and_title(self) -> None:
        components = ComponentPresenter(TEMPLATE_RENDERER)

        html = components.content_section(
            title="Continue",
            eyebrow="Continue",
            body_html="<p>Resume the active workflow.</p>",
            surface="test-surface",
        )

        self.assertIn("<h2>Continue</h2>", html)
        self.assertNotIn('class="panel-kicker"', html)

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
        self.assertIn('class="section-card context-panel', action_html)
        self.assertIn("Papyrus will move the canonical file under archive/knowledge", action_html)
        self.assert_surface(acknowledgement_html, "acknowledgements")
        self.assertIn('class="section-card context-panel', acknowledgement_html)
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
        self.assertIn('class="section-card context-panel', html)
        self.assertIn("Continue guided authoring before routing this revision into review.", html)
        self.assertIn("References: 1 external/manual citation remains weak.", html)
        self.assertIn("Verification: This field is required.", html)

    def test_projection_status_panel_renders_as_context_panel(self) -> None:
        components = ComponentPresenter(TEMPLATE_RENDERER)
        html = render_projection_status_panel(
            components,
            title="Current governed posture",
            ui_projection={
                "state": {
                    "object_lifecycle_state": "active",
                    "revision_review_state": "approved",
                    "draft_progress_state": "ready_for_review",
                    "source_sync_state": "applied",
                    "trust_state": "trusted",
                },
                "use_guidance": {
                    "summary": "Safe to use now",
                    "detail": "The runtime contract marks this object safe for use.",
                    "next_action": "Use the current guidance.",
                    "safe_to_use": True,
                },
                "reasons": ["review:approved"],
            },
        )

        self.assert_component(html, "surface-panel")
        self.assert_surface(html, "posture")
        self.assertIn('class="section-card context-panel', html)
        self.assertIn("Safe to use now", html)

    def test_page_renderer_does_not_emit_removed_header_or_sidebar_blurbs(self) -> None:
        body = PAGE_RENDERER.render_page(
            page_template="pages/home.html",
            page_title="Home",
            active_nav="read",
            page_header={"headline": "Home", "intro": "Decorative page intro"},
            role_id="operator",
            current_path="/read",
            page_context={"home_launch_html": "", "home_activity_html": ""},
            page_surface="home",
        )

        self.assertNotIn("Decorative page intro", body)
        self.assertNotIn("page-intro", body)
        self.assertNotIn("sidebar-copy", body)

    def test_web_copy_contract_blocks_known_decorative_blurb_patterns(self) -> None:
        web_root = ROOT / "src" / "papyrus" / "interfaces" / "web"
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(web_root.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        )

        forbidden_tokens = (
            '"intro":',
            "page-intro",
            "sidebar-copy",
            "home-launch-block__summary",
            "home-board-links__summary",
            "oversight-board__summary",
            "ingest-stage-board__summary",
            "ingest-mapping-gaps__summary",
            "support-disclosure-summary",
            "section-intro",
            "table-support",
        )

        for token in forbidden_tokens:
            self.assertNotIn(token, source_text, msg=f"forbidden decorative copy token found: {token}")


if __name__ == "__main__":
    unittest.main()
