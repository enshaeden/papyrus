from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_activity_hero(*, structured_events: list[dict[str, object]]) -> str:
    return (
        '<section class="activity-hero" data-component="activity-hero" data-surface="activity">'
        "<h1>See consequences before payload detail.</h1>"
        "<p>Activity is consequence-first: what changed, what it affected, and what to do next stay in the primary scan path. Raw audit payloads stay behind disclosure.</p>"
        '<div class="activity-hero__metrics">'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "service_changes"))}</p><span>Service changes</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "evidence_degradation"))}</p><span>Evidence issues</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "validation_failures"))}</p><span>Validation failures</span></article>'
        f'<article><p>{escape(sum(1 for event in structured_events if event["group"] == "manual_suspect_marks"))}</p><span>Suspect marks</span></article>'
        "</div></section>"
    )
