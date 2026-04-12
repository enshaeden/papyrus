from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_read_queue_hero(*, headline: str, intro: str) -> str:
    return (
        '<section class="read-queue-hero" data-component="read-queue-hero" data-surface="read-queue">'
        f"<h1>{escape(headline)}</h1>"
        f"<p>{escape(intro)}</p>"
        "</section>"
    )
