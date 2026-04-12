from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_service_pressure(*, posture: dict[str, object]) -> str:
    return (
        '<section class="service-pressure" data-component="service-pressure" data-surface="services">'
        "<h2>Service pressure</h2>"
        '<div class="service-pressure__grid">'
        f'<article><p class="service-pressure__metric">{escape(posture["linked_object_count"])}</p><p>Linked guidance items</p></article>'
        f'<article><p class="service-pressure__metric">{escape(posture["review_required_count"])}</p><p>Need review</p></article>'
        f'<article><p class="service-pressure__metric">{escape(posture["degraded_count"])}</p><p>Degraded items</p></article>'
        "</div></section>"
    )
