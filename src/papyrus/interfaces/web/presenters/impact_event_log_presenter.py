from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, join_html


def render_impact_event_log(
    *, title: str, events: list[dict[str, object]], empty_label: str, surface: str
) -> str:
    body_html = (
        join_html(
            [
                (
                    '<article class="impact-event-log__item">'
                    f"<p><strong>{escape(event['occurred_at'])}</strong> · {escape(event['event_type'])}</p>"
                    f"<p>{escape(event['actor'])} · {escape(event['source'])}</p>"
                    f"<p>{escape(str(event['payload'].get('summary') or event['payload'].get('reason') or 'No event summary.'))}</p>"
                    "</article>"
                )
                for event in events
            ]
        )
        if events
        else f'<p class="impact-event-log__empty">{escape(empty_label)}</p>'
    )
    return (
        f'<section class="impact-event-log" data-component="impact-event-log" data-surface="{escape(surface)}">'
        '<p class="impact-event-log__kicker">Audit</p>'
        f"<h2>{escape(title)}</h2>"
        f"{body_html}</section>"
    )
