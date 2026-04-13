from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.revision_presenter import (
    present_revision_history,
    render_revision_history_table,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from tests.web_assertions import SemanticHookAssertions


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


HISTORY = {
    "object": {
        "object_id": "kb-history",
        "title": "Revision History",
        "canonical_path": "knowledge/runbooks/history.md",
    },
    "revisions": [
        {
            "revision_number": 1,
            "revision_review_state": "approved",
            "change_summary": "Initial",
            "citations": {"verified": 1},
            "review_assignments": [{"reviewer": "reviewer_a", "state": "approved"}],
            "imported_at": "2026-04-09T00:00:00+00:00",
            "is_current": True,
        }
    ],
    "audit_events": [
        {
            "occurred_at": "2026-04-09T00:00:00+00:00",
            "event_type": "revision_approved",
            "actor": "reviewer_a",
        }
    ],
}


class RevisionPresenterTests(SemanticHookAssertions, unittest.TestCase):
    def test_revision_history_owner_renders_traceable_table_component(self) -> None:
        html = render_revision_history_table(
            components=ComponentPresenter(TEMPLATE_RENDERER), history=HISTORY, role="operator"
        )

        self.assert_component(html, "revision-history-table")
        self.assertIn("Evidence and assignments", html)

    def test_revision_history_presenter_assembles_revision_components(self) -> None:
        page = present_revision_history(
            TEMPLATE_RENDERER,
            role="operator",
            history=HISTORY,
            detail={
                "ui_projection": {
                    "state": {
                        "object_lifecycle_state": "active",
                        "revision_review_state": "approved",
                        "draft_progress_state": "ready_for_review",
                        "source_sync_state": "applied",
                        "trust_state": "trusted",
                    },
                    "use_guidance": {
                        "summary": "Safe to use now",
                        "detail": "Current revision is approved and trusted.",
                        "next_action": "Use the current guidance.",
                        "safe_to_use": True,
                    },
                    "actions": [
                        {
                            "action_id": "mark_suspect",
                            "label": "Mark suspect",
                            "availability": "allowed",
                            "summary": "Mark suspect",
                            "detail": "Escalate suspect posture when needed.",
                            "policy": None,
                        }
                    ],
                },
                "current_revision": {"revision_id": "kb-history-rev-1"},
            },
        )

        page_html = (
            page["page_context"]["history_table_html"]
            + page["page_context"]["timeline_html"]
            + page["aside_html"]
        )
        self.assert_component(page_html, "revision-history-table")
        self.assert_component(page_html, "revision-audit-sequence")
        self.assert_component(page_html, "revision-comparison-cues")
        self.assert_action_id_count(page["aside_html"], "mark_suspect", 1)
