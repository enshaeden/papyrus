from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_approval: str,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    summary_html = components.trust_summary(
        title="Queue posture",
        badges=[
            components.badge(label="Items", value=len(items), tone="approved"),
            components.badge(label="Approval pending", value=sum(1 for item in items if item["approval_state"] != "approved"), tone="pending"),
            components.badge(label="Weak evidence", value=sum(1 for item in items if item["citation_health_rank"] > 0), tone="warning"),
            components.badge(label="Stale", value=sum(1 for item in items if item["freshness_rank"] > 0), tone="danger"),
        ],
        summary="Trust metadata stays visible in queue triage so operators can judge fitness before opening an article.",
    )
    filter_controls_html = (
        '<form class="filter-form" method="get" action="/queue">'
        f'<input type="search" name="query" placeholder="Filter queue" value="{escape(query)}" data-filter-input="true" />'
        '<select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All types</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbooks</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known errors</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service records</option>'
        "</select>"
        '<select name="trust">'
        f'<option value=""{" selected" if not selected_trust else ""}>All trust</option>'
        f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        "</select>"
        '<select name="approval">'
        f'<option value=""{" selected" if not selected_approval else ""}>All approval</option>'
        f'<option value="approved"{" selected" if selected_approval == "approved" else ""}>Approved</option>'
        f'<option value="in_review"{" selected" if selected_approval == "in_review" else ""}>In review</option>'
        f'<option value="draft"{" selected" if selected_approval == "draft" else ""}>Draft</option>'
        f'<option value="rejected"{" selected" if selected_approval == "rejected" else ""}>Rejected</option>'
        "</select>"
        '<button class="button button-secondary" type="submit">Apply</button>'
        "</form>"
    )
    rows = [
        [
            f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}"
            f'<p class="cell-meta">{escape(item["object_id"])}</p>',
            escape(item["object_type"]),
            components.badge(label="Trust", value=item["trust_state"], tone="approved" if item["trust_state"] == "trusted" else "warning"),
            components.badge(label="Approval", value=item["approval_state"], tone="approved" if item["approval_state"] == "approved" else "pending"),
            escape(", ".join(item["reasons"])),
            escape(item["owner"]),
            escape(item["path"]),
        ]
        for item in items
    ]
    queue_html = (
        components.section_card(
            title="Knowledge queue",
            eyebrow="Read",
            body_html=components.queue_table(
                headers=["Title", "Type", "Trust", "Approval", "Reasons", "Owner", "Path"],
                rows=rows,
                table_id="knowledge-queue",
            ),
            footer_html='<p class="section-footer">Ordered for approval risk, trust posture, evidence quality, and ownership clarity.</p>',
        )
        if rows
        else components.empty_state(
            title="No matching queue items",
            description="Adjust filters or search terms to widen the queue scope.",
        )
    )
    secondary_html = components.section_card(
        title="Operator guidance",
        eyebrow="Read",
        body_html=(
            "<p>Use the queue for rapid triage. Trust state, approval state, and reasons stay in-line so the first click is informed, not blind.</p>"
        ),
    )
    aside_html = join_html(
        [
            summary_html,
            components.validation_summary(
                title="What to look for",
                findings=[
                    "Non-approved revisions before active use.",
                    "Weak citations before escalation-heavy work.",
                    "Review-due items before following stale runbooks.",
                ],
            ),
        ]
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Knowledge Queue",
        "headline": "Knowledge Queue",
        "kicker": "Read",
        "intro": "Find the right operational knowledge quickly, with visible trust posture and governance signals.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "filter_bar_html": components.filter_bar(title="Queue filters", controls_html=filter_controls_html),
            "summary_html": summary_html,
            "queue_html": queue_html,
            "secondary_html": secondary_html,
        },
    }
