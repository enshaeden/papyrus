from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html


def render_activity_audit_log(*, events: list[dict[str, object]]) -> str:
    return (
        '<section class="activity-audit-log" data-component="activity-audit-log" data-surface="activity">'
        "<h2>Audit log</h2>"
        '<div class="activity-audit-log__list">'
        + join_html(
            [
                (
                    '<article class="activity-audit-log__item">'
                    f"<p>{escape(event['event_type'])} · {escape(format_timestamp(event['occurred_at']))} · {escape(event['actor'])}</p>"
                    f"<p>{escape(event['object_id'] or 'No object')} · {escape(event['revision_id'] or 'No revision')}</p>"
                    "</article>"
                )
                for event in events[:20]
            ]
        )
        + "</div></section>"
    )
