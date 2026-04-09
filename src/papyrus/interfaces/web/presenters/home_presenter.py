from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link


LIFECYCLE_STAGES: tuple[tuple[str, str], ...] = (
    ("Draft", "Create a new knowledge object or start a new revision."),
    ("Revise", "Clarify scope, update guidance, and record what changed."),
    ("Review", "Route the revision to a reviewer with supporting evidence."),
    ("Approve", "Decide whether it is ready to become canonical guidance."),
    ("Use", "Rely on the approved guidance with visible freshness and safety cues."),
    ("Revalidate", "Recheck evidence and assumptions after change or time-based drift."),
    ("Supersede / Archive", "Retire or replace guidance with a clear transition path."),
)


def _area_card(
    components: ComponentPresenter,
    *,
    eyebrow: str,
    title: str,
    metric_label: str,
    metric_value: object,
    description: str,
    href: str,
    action_label: str,
    tone: str = "default",
) -> str:
    return components.section_card(
        title=title,
        eyebrow=eyebrow,
        tone=tone,
        body_html=(
            f'<p class="metric-value">{escape(metric_value)}</p>'
            f'<p><strong>{escape(metric_label)}</strong></p>'
            f"<p>{escape(description)}</p>"
        ),
        footer_html=link(action_label, href, css_class="button button-secondary"),
    )


def _next_action_definitions(actor_id: str, *, counts: dict[str, int]) -> list[dict[str, str | int]]:
    shared = {
        "review": counts["review_required"],
        "revalidate": counts["needs_revalidation"],
        "activity": counts["recent_activity"],
        "drafts": counts["drafts"],
        "health": counts["needs_attention"],
    }
    if actor_id == "local.reviewer":
        return [
            {
                "title": "Make review decisions",
                "detail": "Start with the revisions that already need a reviewer decision and make the next step explicit.",
                "href": "/review",
                "label": "Open review work",
                "count": shared["review"],
            },
            {
                "title": "Revalidate weak guidance",
                "detail": "Clear stale or weak-evidence items before they become invisible operational risk.",
                "href": "/health",
                "label": "Open knowledge health",
                "count": shared["revalidate"],
            },
            {
                "title": "Inspect recent consequences",
                "detail": "Use the activity history when the reason for a queue item is not obvious from status alone.",
                "href": "/activity",
                "label": "Open activity",
                "count": shared["activity"],
            },
        ]
    if actor_id == "local.manager":
        return [
            {
                "title": "Shepherd knowledge health",
                "detail": "Review what needs attention across stale guidance, weak evidence, and suspect posture.",
                "href": "/health",
                "label": "Open knowledge health",
                "count": shared["health"],
            },
            {
                "title": "Reduce review pressure",
                "detail": "Keep review demand moving so drafts and pending decisions do not stall the lifecycle.",
                "href": "/review",
                "label": "Open approvals",
                "count": shared["review"],
            },
            {
                "title": "Inspect recent activity",
                "detail": "Use recent events and validation outcomes to understand where the next stewardship action belongs.",
                "href": "/activity",
                "label": "Open activity",
                "count": shared["activity"],
            },
        ]
    return [
        {
            "title": "Use current guidance",
            "detail": "Start with read surfaces that keep operational guidance, freshness, and service context visible together.",
            "href": "/read",
            "label": "Open read",
            "count": counts["read_ready"],
        },
        {
            "title": "Continue authoring",
            "detail": "Move a gap or rejected revision forward instead of leaving it stuck as an unresolved draft.",
            "href": "/write/objects/new",
            "label": "Open write",
            "count": shared["drafts"],
        },
        {
            "title": "Escalate unsafe guidance",
            "detail": "When the current answer looks stale or weak, hand it into review and health flows instead of guessing.",
            "href": "/health",
            "label": "Open knowledge health",
            "count": shared["revalidate"],
        },
    ]


def _activity_rows(events: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for event in events:
        summary = (
            str(event.get("what_happened") or "")
            or str(event.get("payload", {}).get("summary") or event.get("payload", {}).get("reason") or "No summary recorded.")
        )
        next_action = str(event.get("next_action") or "Inspect the affected object or service for the next step.")
        rows.append(
            [
                escape(format_timestamp(event["occurred_at"])),
                escape(summary),
                escape(f"{event['entity_type']}:{event['entity_id']}"),
                escape(next_action),
            ]
        )
    return rows


def present_home_page(
    renderer: TemplateRenderer,
    *,
    actor_id: str,
    counts: dict[str, int],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    next_actions_html = join_html(
        [
            _area_card(
                components,
                eyebrow="Next",
                title=str(item["title"]),
                metric_label="Outstanding work",
                metric_value=item["count"],
                description=str(item["detail"]),
                href=str(item["href"]),
                action_label=str(item["label"]),
                tone="brand" if index == 0 else "default",
            )
            for index, item in enumerate(_next_action_definitions(actor_id, counts=counts))
        ]
    )
    work_areas_html = join_html(
        [
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Read",
                metric_label="Guidance items",
                metric_value=counts["read_ready"],
                description="Find current guidance, check whether it is safe to use, and move into service context when needed.",
                href="/read",
                action_label="Open read",
                tone="brand",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Write",
                metric_label="Drafts or rework items",
                metric_value=counts["drafts"],
                description="Create a new object shell, revise existing guidance, and move a draft toward submission.",
                href="/write/objects/new",
                action_label="Open write",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Review / Approvals",
                metric_label="Review items",
                metric_value=counts["review_required"],
                description="Assign reviewers, inspect changes, and make approval or rejection decisions with context.",
                href="/review",
                action_label="Open review",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Knowledge Health",
                metric_label="Needs attention",
                metric_value=counts["needs_attention"],
                description="Track stale content, weak evidence, suspect guidance, and review load as stewardship work.",
                href="/health",
                action_label="Open knowledge health",
                tone="warning" if counts["needs_attention"] else "approved",
            ),
            _area_card(
                components,
                eyebrow="Context",
                title="Services",
                metric_label="Services in scope",
                metric_value=counts["services"],
                description="Move from a service issue into the linked guidance path instead of browsing unrelated objects.",
                href="/services",
                action_label="Open services",
            ),
            _area_card(
                components,
                eyebrow="Context",
                title="Activity / History",
                metric_label="Recent events",
                metric_value=counts["recent_activity"],
                description="Understand what changed, what it affected, and what should be reviewed or revalidated next.",
                href="/activity",
                action_label="Open activity",
            ),
        ]
    )
    summary_html = components.trust_summary(
        title="Needs attention now",
        badges=[
            components.badge(label="Review needed", value=counts["review_required"], tone="pending"),
            components.badge(label="Needs revalidation", value=counts["needs_revalidation"], tone="warning"),
            components.badge(label="Weak evidence", value=counts["weak_evidence"], tone="warning"),
            components.badge(label="Stale", value=counts["stale"], tone="danger"),
            components.badge(label="Activity", value=counts["recent_activity"], tone="brand"),
        ],
        summary="Papyrus should tell each actor what is safe to use, what is moving forward, and what needs stewardship next.",
    )
    activity_html = components.section_card(
        title="Recent activity",
        eyebrow="Activity",
        body_html=(
            components.queue_table(
                headers=["When", "What happened", "Affected", "Next action"],
                rows=_activity_rows(events),
                table_id="home-activity",
            )
            if events
            else '<p class="empty-state-copy">No recent activity is recorded yet.</p>'
        ),
    )
    aside_html = join_html(
        [
            components.section_card(
                title="Knowledge lifecycle",
                eyebrow="Lifecycle",
                body_html=join_html(
                    [
                        '<div class="lifecycle-stage">'
                        f'<p class="lifecycle-stage-title">{escape(title)}</p>'
                        f'<p class="lifecycle-stage-detail">{escape(detail)}</p>'
                        "</div>"
                        for title, detail in LIFECYCLE_STAGES
                    ]
                ),
            ),
            components.validation_summary(
                title="How to use this home page",
                findings=[
                    "Start with the next-action cards instead of dropping straight into a raw queue.",
                    "Use Knowledge Health for stewardship work and Activity / History for consequence tracing.",
                    "Move into review only after the revision and evidence context are clear enough to decide.",
                ],
            ),
        ]
    )
    return {
        "page_template": "pages/home.html",
        "page_title": "Home",
        "headline": "Guided Operational Knowledge",
        "kicker": "Lifecycle",
        "intro": "Papyrus guides people through drafting, reviewing, using, revalidating, and retiring operational knowledge without hiding the guardrails.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "summary_html": summary_html,
            "next_actions_html": next_actions_html,
            "work_areas_html": work_areas_html,
            "activity_html": activity_html,
        },
    }
