from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link


def _dashboard_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _dashboard_safe_now_html(components: ComponentPresenter, item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    state = projection_state(item.get("ui_projection"))
    return join_html(
        [
            components.badge(
                label="Use",
                value="Safe now" if bool(use_guidance.get("safe_to_use")) else "Review first",
                tone="approved" if bool(use_guidance.get("safe_to_use")) else "warning",
            ),
            components.badge(
                label="Approval",
                value=str(state.get("approval_state") or item.get("approval_state") or "unknown"),
                tone="approved" if str(state.get("approval_state") or item.get("approval_state") or "") == "approved" else "pending",
            ),
            components.badge(
                label="Trust",
                value=str(state.get("trust_state") or item.get("trust_state") or "unknown"),
                tone="approved" if str(state.get("trust_state") or item.get("trust_state") or "") == "trusted" else "warning",
            ),
        ],
        " ",
    )


def _dashboard_why_now(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("summary")
        or use_guidance.get("detail")
        or item.get("posture", {}).get("trust_summary")
        or "Inspect the governed detail before acting."
    )


def _dashboard_next_action(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("next_action")
        or use_guidance.get("detail")
        or "Inspect the governed detail before acting."
    )


def present_trust_dashboard(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_cards_html = join_html(
        [
            components.section_card(
                title="Knowledge in scope",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['object_count'])}</p><p>Operational knowledge objects currently in the runtime.</p>",
                footer_html=link("Open read", "/read", css_class="button button-secondary"),
            ),
            components.section_card(
                title="Review pressure",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['approval_counts'].get('in_review', 0))}</p><p>Revisions currently waiting on a review decision.</p>",
                footer_html=link("Open review / approvals", "/review", css_class="button button-secondary"),
                tone="warning" if dashboard["approval_counts"].get("in_review", 0) else "approved",
            ),
            components.section_card(
                title="Needs revalidation",
                eyebrow="Health",
                body_html=f"<p class=\"metric-value\">{escape(dashboard['trust_counts'].get('stale', 0) + dashboard['trust_counts'].get('weak_evidence', 0) + dashboard['trust_counts'].get('suspect', 0))}</p><p>Guidance that needs evidence, freshness, or trust follow-up.</p>",
                footer_html=link("Open knowledge health", "/health", css_class="button button-secondary"),
                tone="warning" if (dashboard["trust_counts"].get("stale", 0) + dashboard["trust_counts"].get("weak_evidence", 0) + dashboard["trust_counts"].get("suspect", 0)) else "approved",
            ),
            components.section_card(
                title="Evidence posture",
                eyebrow="Health",
                body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["evidence_counts"].items()))) + "</p>",
                footer_html=link("Open activity / history", "/activity", css_class="button button-secondary"),
            ),
        ]
    )
    primary_html = components.section_card(
        title="Needs attention",
        eyebrow="Health",
        body_html=components.queue_table(
            headers=["Guidance", "Safe now?", "Why now", "Next action"],
            rows=[
                [
                    link(item["title"], _dashboard_item_href(item)),
                    _dashboard_safe_now_html(components, item),
                    escape(_dashboard_why_now(item)),
                    escape(_dashboard_next_action(item)),
                ]
                for item in dashboard["queue"]
            ],
            table_id="knowledge-health-queue",
        ),
    )
    secondary_html = components.section_card(
        title="Recent validation runs",
        eyebrow="Activity",
        body_html=components.queue_table(
            headers=["Completed", "Run type", "Status", "Findings", "Next action"],
            rows=[
                [
                    escape(format_timestamp(run["completed_at"])),
                    escape(run["run_type"]),
                    escape(run["status"]),
                    escape(run["finding_count"]),
                    escape("Inspect the recorded run if this affects approval or revalidation work."),
                ]
                for run in dashboard["validation_runs"]
            ],
            table_id="dashboard-validation-runs",
        ),
    )
    aside_html = components.validation_summary(
        title="How to use knowledge health",
        findings=[
            dashboard["validation_posture"]["summary"] + ": " + dashboard["validation_posture"]["detail"],
            "Use this page for stewardship work, not for passive observation.",
            "Every queue item links to the contract-selected next surface so the next decision stays in the right governed context.",
        ],
    )
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Knowledge Health",
        "headline": "Knowledge Health",
        "kicker": "Health",
        "intro": "Track what needs review, revalidation, or evidence follow-up so governance supports operational usefulness instead of eclipsing it.",
        "active_nav": "health",
        "aside_html": aside_html,
        "page_context": {
            "summary_cards_html": summary_cards_html,
            "primary_html": primary_html,
            "secondary_html": secondary_html,
        },
    }
