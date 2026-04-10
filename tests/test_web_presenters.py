from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.dashboard_presenter import present_trust_dashboard
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_acknowledgement_panel, render_action_contract_panel
from papyrus.interfaces.web.presenters.object_presenter import present_object_detail
from papyrus.interfaces.web.presenters.queue_presenter import present_queue_page
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer


TEMPLATE_RENDERER = TemplateRenderer(ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates")


class WebPresenterTests(unittest.TestCase):
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

        self.assertIn("Papyrus will move the canonical file under archive/knowledge", action_html)
        self.assertIn("Review the archive acknowledgement before continuing.", acknowledgement_html)
        self.assertIn("canonical path will move to archive", acknowledgement_html)

    def test_dashboard_presenter_uses_governed_projection_for_queue_actions(self) -> None:
        page = present_trust_dashboard(
            TEMPLATE_RENDERER,
            dashboard={
                "object_count": 1,
                "approval_counts": {"in_review": 1},
                "trust_counts": {"suspect": 1},
                "evidence_counts": {"verified": 1},
                "validation_posture": {
                    "summary": "Latest validation: import",
                    "detail": "Most recent validation passed.",
                },
                "validation_runs": [],
                "queue": [
                    {
                        "object_id": "kb-review",
                        "title": "Review Queue Item",
                        "approval_state": "in_review",
                        "trust_state": "suspect",
                        "current_revision_id": "kb-review-r1",
                        "posture": {"trust_summary": "Governance review is still open."},
                        "ui_projection": {
                            "state": {
                                "approval_state": "in_review",
                                "trust_state": "suspect",
                                "revision_review_state": "in_review",
                            },
                            "use_guidance": {
                                "summary": "Review decision pending",
                                "detail": "Papyrus requires a review decision before use.",
                                "next_action": "Open the review decision.",
                                "safe_to_use": False,
                            },
                            "actions": [
                                {
                                    "action_id": "review_decision",
                                    "label": "Review decision",
                                    "availability": "allowed",
                                }
                            ],
                        },
                    }
                ],
            },
        )
        self.assertIn("/manage/reviews/kb-review/kb-review-r1", page["page_context"]["primary_html"])
        self.assertIn("Open the review decision.", page["page_context"]["primary_html"])
        self.assertIn("Review decision pending", page["page_context"]["primary_html"])

    def test_queue_presenter_keeps_trust_and_filters_visible(self) -> None:
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[
                {
                    "object_id": "kb-test",
                    "title": "Test title",
                    "object_type": "runbook",
                    "trust_state": "suspect",
                    "approval_state": "in_review",
                    "reasons": ["approval:in_review", "trust:suspect"],
                    "owner": "tester",
                    "path": "knowledge/runbooks/test.md",
                    "citation_health_rank": 1,
                    "freshness_rank": 0,
                    "ui_projection": {
                        "use_guidance": {
                            "summary": "Review decision pending",
                            "detail": "Backend contract says this guidance is still in review.",
                            "next_action": "Route the revision through review before use.",
                            "safe_to_use": False,
                        }
                    },
                }
            ],
            query="vpn",
            selected_type="runbook",
            selected_trust="suspect",
            selected_approval="in_review",
        )
        self.assertEqual(page["page_title"], "Read Guidance")
        self.assertIn("Read posture", page["aside_html"])
        self.assertIn("Read filters", page["page_context"]["filter_bar_html"])
        self.assertIn("approval:in_review", page["page_context"]["queue_html"])

    def test_object_presenter_surfaces_citations_relationships_and_audit(self) -> None:
        page = present_object_detail(
            TEMPLATE_RENDERER,
            detail={
                "object": {
                    "object_id": "kb-test",
                    "object_type": "runbook",
                    "title": "Test object",
                    "summary": "Structured summary.",
                    "object_lifecycle_state": "active",
                    "owner": "tester",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/test.md",
                    "source_type": "native",
                    "source_system": "repository",
                    "source_title": "Test object",
                    "created_date": "2026-04-07",
                    "updated_date": "2026-04-07",
                    "last_reviewed": "2026-04-07",
                    "review_cadence": "quarterly",
                    "trust_state": "trusted",
                    "approval_state": "approved",
                    "freshness_rank": 0,
                    "citation_health_rank": 0,
                    "ownership_rank": 0,
                    "tags": ["vpn"],
                    "systems": ["<VPN_SERVICE>"],
                    "path": "knowledge/runbooks/test.md",
                },
                "ui_projection": {
                    "state": {
                        "object_lifecycle_state": "active",
                        "revision_review_state": "approved",
                        "draft_progress_state": "ready_for_review",
                        "source_sync_state": "applied",
                        "trust_state": "trusted",
                        "approval_state": "approved",
                    },
                    "use_guidance": {
                        "summary": "Safe to use now",
                        "detail": "The runtime contract marks this object safe for use.",
                        "next_action": "Use the current guidance.",
                        "safe_to_use": True,
                    },
                    "reasons": ["approval:approved", "trust:trusted"],
                    "actions": [
                        {
                            "action_id": "mark_suspect",
                            "label": "Mark suspect",
                            "availability": "allowed",
                            "summary": "Mark suspect",
                            "detail": "Mark the object suspect when an upstream change invalidates the guidance.",
                            "policy": None,
                        }
                    ],
                },
                "current_revision": {
                    "revision_id": "kb-test-rev-1",
                    "revision_number": 1,
                    "revision_review_state": "approved",
                    "imported_at": "2026-04-07T00:00:00+00:00",
                    "change_summary": "Initial",
                    "body_markdown": "## Use When\n\nUse the runbook.",
                },
                "metadata": {
                    "prerequisites": ["Have the ticket."],
                    "steps": ["Run the step."],
                    "verification": ["Confirm the result."],
                    "rollback": ["Undo the step."],
                },
                "citations": [
                    {
                        "source_title": "Seed manifest",
                        "source_type": "document",
                        "source_ref": "migration/import-manifest.yml",
                        "note": "Evidence",
                        "validity_status": "verified",
                    }
                ],
                "related_services": [{"service_id": "remote-access", "service_name": "Remote Access", "status": "active", "service_criticality": "high"}],
                "outbound_relationships": [{"relationship_type": "related_object", "object_id": "kb-other", "title": "Other object", "path": "knowledge/other.md", "status": "active"}],
                "inbound_relationships": [],
                "audit_events": [{"event_type": "revision_approved", "actor": "reviewer", "occurred_at": "2026-04-07T01:00:00+00:00", "details": {}}],
            },
        )
        self.assertIn("Supporting evidence", page["page_context"]["related_sections_html"])
        self.assertIn("Recent audit trail", page["page_context"]["related_sections_html"])
        self.assertIn("Linked service context", page["page_context"]["content_sections_html"])
        self.assertIn("Safety and lifecycle", page["aside_html"])
        self.assertIn("Governed actions", page["page_context"]["content_sections_html"])
        self.assertIn("The runtime contract marks this object safe for use.", page["page_context"]["content_sections_html"])
        self.assertEqual(page["page_context"]["content_sections_html"].count("Governed actions"), 1)


if __name__ == "__main__":
    unittest.main()
