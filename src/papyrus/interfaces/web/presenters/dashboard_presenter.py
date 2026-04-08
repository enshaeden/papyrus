from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path


def present_trust_dashboard(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_cards_html = join_html(
        [
            components.section_card(title="Objects", eyebrow="Manage", body_html=f"<p class=\"metric-value\">{escape(dashboard['object_count'])}</p>"),
            components.section_card(title="Trust states", eyebrow="Manage", body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["trust_counts"].items()))) + "</p>"),
            components.section_card(title="Approval states", eyebrow="Manage", body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["approval_counts"].items()))) + "</p>"),
            components.section_card(title="Evidence states", eyebrow="Manage", body_html="<p>" + escape(", ".join(f"{key}={value}" for key, value in sorted(dashboard["evidence_counts"].items()))) + "</p>"),
        ]
    )
    primary_html = components.section_card(
        title="Priority queue",
        eyebrow="Manage",
        body_html=components.queue_table(
            headers=["Title", "Trust", "Approval", "Reasons"],
            rows=[
                [
                    link(item["title"], f"/objects/{quoted_path(item['object_id'])}"),
                    escape(item["trust_state"]),
                    escape(item["approval_state"]),
                    escape(item["posture"]["trust_summary"]),
                ]
                for item in dashboard["queue"]
            ],
            table_id="dashboard-queue",
        ),
    )
    secondary_html = components.section_card(
        title="Recent validation runs",
        eyebrow="Manage",
        body_html=components.queue_table(
            headers=["Completed", "Run type", "Status", "Findings"],
            rows=[
                [
                    escape(format_timestamp(run["completed_at"])),
                    escape(run["run_type"]),
                    escape(run["status"]),
                    escape(run["finding_count"]),
                ]
                for run in dashboard["validation_runs"]
            ],
            table_id="dashboard-validation-runs",
        ),
    )
    aside_html = components.validation_summary(
        title="Actionability",
        findings=[
            dashboard["validation_posture"]["summary"] + ": " + dashboard["validation_posture"]["detail"],
            "Every priority item links straight to the object detail and audit trail.",
            "Approval state and trust posture are shown separately so review status does not hide evidence or freshness risk.",
        ],
    )
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Trust Dashboard",
        "headline": "Trust Dashboard",
        "kicker": "Manage",
        "intro": "Trust posture is summarized with direct paths into queue triage, validation runs, and governed object review.",
        "active_nav": "manage",
        "aside_html": aside_html,
        "page_context": {
            "summary_cards_html": summary_cards_html,
            "primary_html": primary_html,
            "secondary_html": secondary_html,
        },
    }
