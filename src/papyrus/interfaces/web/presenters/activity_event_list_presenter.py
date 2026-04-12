from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, join_html


def render_activity_event_list(*, structured_events: list[dict[str, object]]) -> str:
    return (
        join_html(
            [
                (
                    '<article class="activity-event" data-component="activity-event" data-surface="activity">'
                    f'<p class="activity-event__kicker">{escape(event["group"].replace("_", " "))} · {escape(event["occurred_at"])}</p>'
                    f'<h2>{escape(event["what_happened"])}</h2>'
                    f'<p class="activity-event__affected">{escape(str(event["entity_type"]) + ":" + str(event["entity_id"]))}</p>'
                    f'<p class="activity-event__next">{escape(event["next_action"])}</p>'
                    '<details class="activity-event__details"><summary>Show audit details</summary>'
                    f'<pre>{escape(", ".join(str(key) + "=" + str(value) for key, value in event["payload"].items() if value) or "No extra payload details")}</pre>'
                    "</details></article>"
                )
                for event in structured_events
            ]
        )
        if structured_events
        else '<section class="activity-empty"><h2>No matching activity</h2><p>Adjust the filter or wait for the next recorded event.</p></section>'
    )
