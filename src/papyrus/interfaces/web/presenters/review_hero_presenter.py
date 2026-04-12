from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_review_hero(*, queue: dict[str, object]) -> str:
    return (
        '<section class="review-hero" data-component="review-hero" data-surface="review">'
        "<h1>Make review decisions with the blocking context visible.</h1>"
        "<p>Review is a dense workbench: each lane is grouped by the decision it needs, not by decorative governance chrome.</p>"
        '<div class="review-hero__metrics">'
        f'<article><p>{escape(len(queue["ready_for_review"]))}</p><span>Ready for review</span></article>'
        f'<article><p>{escape(len(queue["needs_decision"]))}</p><span>Needs decision</span></article>'
        f'<article><p>{escape(len(queue["needs_revalidation"]))}</p><span>Needs revalidation</span></article>'
        f'<article><p>{escape(len(queue["recently_changed"][:10]))}</p><span>Recently changed</span></article>'
        "</div></section>"
    )
