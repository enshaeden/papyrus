from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.interfaces.web.presenters.dashboard_presenter import present_trust_dashboard
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.home_presenter import present_home_page
from papyrus.interfaces.web.presenters.governed_presenter import (
    render_acknowledgement_panel,
    render_action_contract_panel,
    render_workflow_projection_panel,
)
from papyrus.interfaces.web.presenters.object_presenter import present_object_detail
from papyrus.interfaces.web.presenters.queue_presenter import present_queue_page
from papyrus.interfaces.web.presenters.revision_presenter import present_revision_history
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

    def test_dashboard_presenter_uses_governed_projection_for_queue_actions(self) -> None:
        page = present_trust_dashboard(
            TEMPLATE_RENDERER,
            dashboard={
                "object_count": 1,
                "review_counts": {"in_review": 1},
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
                        "revision_review_state": "in_review",
                        "trust_state": "suspect",
                        "current_revision_id": "kb-review-r1",
                        "posture": {"trust_summary": "Governance review is still open."},
                        "ui_projection": {
                            "state": {
                                "trust_state": "suspect",
                                "revision_review_state": "in_review",
                            },
                            "use_guidance": {
                                "summary": "Review decision pending",
                                "detail": "Papyrus requires a review decision before use.",
                                "next_action": "Review the decision.",
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
        self.assert_component(page["page_context"]["primary_html"], "table")
        self.assert_action_id(page["page_context"]["primary_html"], "open-primary-surface")
        self.assertIn("Review the decision.", page["page_context"]["primary_html"])
        self.assertIn("Review decision pending", page["aside_html"])

    def test_queue_presenter_keeps_trust_and_filters_visible(self) -> None:
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[
                {
                    "object_id": "kb-test",
                    "title": "Test title",
                    "object_type": "runbook",
                    "trust_state": "suspect",
                    "revision_review_state": "in_review",
                    "reasons": ["review:in_review", "trust:suspect"],
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
            selected_review_state="in_review",
        )
        self.assertEqual(page["page_title"], "Read Guidance")
        self.assertEqual(page["aside_html"], "")
        self.assert_component(page["page_context"]["filter_bar_html"], "filter-bar")
        self.assert_component(page["page_context"]["summary_html"], "summary-strip")
        self.assert_component(page["page_context"]["queue_html"], "decision-card")
        self.assert_surface(page["page_context"]["queue_html"], "read-queue")
        self.assertIn(
            "Backend contract says this guidance is still in review.",
            page["page_context"]["queue_html"],
        )

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
                    "revision_review_state": "approved",
                    "freshness_rank": 0,
                    "citation_health_rank": 0,
                    "ownership_rank": 0,
                    "tags": ["vpn"],
                    "systems": ["Remote Access Gateway"],
                    "path": "knowledge/runbooks/test.md",
                },
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
                        "detail": "The runtime contract marks this object safe for use.",
                        "next_action": "Use the current guidance.",
                        "safe_to_use": True,
                    },
                    "reasons": ["review:approved", "trust:trusted"],
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
        self.assertIn("Supporting evidence", page["aside_html"])
        self.assertIn("Recent audit trail", page["aside_html"])
        self.assertIn("Linked service context", page["aside_html"])
        self.assertNotIn("Current status", page["aside_html"])
        self.assert_component(page["page_context"]["content_sections_html"], "surface-panel")
        self.assert_action_id(page["aside_html"], "mark_suspect")
        self.assertIn("The runtime contract marks this object safe for use.", page["page_context"]["content_sections_html"])
        self.assert_not_component(page["page_context"]["content_sections_html"], "object-header")

    def test_object_presenter_prefers_projection_truth_over_raw_state_fallbacks(self) -> None:
        page = present_object_detail(
            TEMPLATE_RENDERER,
            detail={
                "object": {
                    "object_id": "kb-projection-wins",
                    "object_type": "runbook",
                    "title": "Projection Wins",
                    "summary": "Projection-backed truth should win.",
                    "object_lifecycle_state": "active",
                    "owner": "tester",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/projection-wins.md",
                    "source_type": "native",
                    "source_system": "repository",
                    "source_title": "Projection Wins",
                    "created_date": "2026-04-09",
                    "updated_date": "2026-04-09",
                    "last_reviewed": "2026-04-09",
                    "review_cadence": "quarterly",
                    "trust_state": "trusted",
                    "revision_review_state": "approved",
                    "freshness_rank": 0,
                    "citation_health_rank": 0,
                    "ownership_rank": 0,
                    "tags": [],
                    "systems": [],
                    "path": "knowledge/runbooks/projection-wins.md",
                },
                "posture": {
                    "trust_summary": "Raw posture fallback should not render.",
                    "trust_detail": "Raw posture detail should not render.",
                },
                "ui_projection": {
                    "state": {
                        "object_lifecycle_state": "active",
                        "revision_review_state": "approved",
                        "draft_progress_state": "ready_for_review",
                        "source_sync_state": "conflicted",
                        "trust_state": "trusted",
                    },
                    "use_guidance": {
                        "summary": "Projection says stop and inspect",
                        "detail": "Projection-backed detail should appear instead of any raw-state fallback.",
                        "next_action": "Review the projection-backed warning.",
                        "safe_to_use": False,
                    },
                    "reasons": ["source_sync:conflicted"],
                    "actions": [],
                },
                "current_revision": {
                    "revision_id": "kb-projection-wins-rev-1",
                    "revision_number": 1,
                    "revision_review_state": "approved",
                    "imported_at": "2026-04-09T00:00:00+00:00",
                    "change_summary": "Projection sentinel coverage.",
                    "body_markdown": "## Use When\n\nUse the projection sentinel.\n",
                },
                "metadata": {
                    "prerequisites": [],
                    "steps": [],
                    "verification": [],
                    "rollback": [],
                },
                "citations": [],
                "related_services": [],
                "outbound_relationships": [],
                "inbound_relationships": [],
                "audit_events": [],
            },
        )
        self.assertIn("Projection says stop and inspect", page["page_context"]["content_sections_html"])
        self.assertIn(
            "Projection-backed detail should appear instead of any raw-state fallback.",
            page["page_context"]["content_sections_html"],
        )
        self.assertNotIn("Raw posture fallback should not render.", page["page_context"]["content_sections_html"])
        self.assertNotIn("Safe to use now", page["page_context"]["content_sections_html"])

    def test_queue_presenter_prefers_projection_guidance_over_raw_status_copy(self) -> None:
        page = present_queue_page(
            TEMPLATE_RENDERER,
            items=[
                {
                    "object_id": "kb-queue-projection",
                    "title": "Queue Projection",
                    "object_type": "runbook",
                    "trust_state": "trusted",
                    "revision_review_state": "approved",
                    "reasons": ["review:approved"],
                    "owner": "tester",
                    "path": "knowledge/runbooks/queue-projection.md",
                    "citation_health_rank": 0,
                    "freshness_rank": 0,
                    "posture": {"trust_summary": "Raw queue fallback should not render."},
                    "ui_projection": {
                        "use_guidance": {
                            "summary": "Projection summary wins",
                            "detail": "Projection detail wins",
                            "next_action": "Follow the projection-backed next step.",
                            "safe_to_use": False,
                        }
                    },
                }
            ],
            query="projection",
            selected_type="runbook",
            selected_trust="all",
            selected_review_state="all",
        )
        queue_html = page["page_context"]["queue_html"]
        self.assertIn("Projection summary wins", queue_html)
        self.assertIn("Follow the projection-backed next step.", queue_html)
        self.assert_component(queue_html, "decision-card")
        self.assertNotIn("Raw queue fallback should not render.", queue_html)
        self.assertNotIn("Safe to use now", queue_html)

    def test_home_presenter_uses_flat_sections_instead_of_grid_cards(self) -> None:
        page = present_home_page(
            TEMPLATE_RENDERER,
            counts={
                "read_ready": 4,
                "drafts": 1,
                "review_required": 2,
                "needs_revalidation": 1,
                "needs_attention": 2,
                "services": 3,
                "recent_activity": 2,
            },
            next_actions=[
                {"title": "Use current guidance", "detail": "Read the best answer first.", "href": "/read", "label": "Read guidance", "count": 4},
                {"title": "Continue authoring", "detail": "Finish a draft.", "href": "/write/objects/new", "label": "Start a draft", "count": 1},
            ],
            work_areas=[
                {"title": "Read", "metric_label": "Guidance items", "metric_value": 4, "description": "Find the current answer fast.", "href": "/read", "action_label": "Read guidance", "tone": "brand"},
                {"title": "Write", "metric_label": "Drafts", "metric_value": 1, "description": "Create a draft.", "href": "/write/objects/new", "action_label": "Start a draft", "tone": "default"},
            ],
            events=[],
            summary_variant="local.operator",
        )

        self.assertIn("next-action-row", page["page_context"]["next_actions_html"])
        self.assertIn("work-area-row", page["page_context"]["work_areas_html"])
        self.assertNotIn("dual-grid", page["page_context"]["next_actions_html"])
        self.assertIn('class="section-card content-section', page["page_context"]["next_actions_html"])

    def test_revision_history_renders_single_current_governed_actions_panel(self) -> None:
        page = present_revision_history(
            TEMPLATE_RENDERER,
            history={
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
            },
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
        self.assert_action_id_count(page["aside_html"], "mark_suspect", 1)
        self.assert_surface(page["aside_html"], "posture")


if __name__ == "__main__":
    unittest.main()
