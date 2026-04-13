from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.view_helpers import escape


def render_revision_comparison_cues(*, components: ComponentPresenter) -> str:
    body_html = components.list_body(
        items=[
            escape("Look for the current marker before using the revision body."),
            escape("Citation counts show evidence drift even without a diff view."),
            escape("Assignment state exposes whether a review actually closed."),
        ],
        empty_label="No comparison cues recorded.",
        css_class="validation-findings",
    )
    return (
        '<section class="revision-comparison-cues" data-component="revision-comparison-cues" data-surface="revision-history">'
        '<p class="revision-comparison-cues__kicker">Content</p>'
        "<h2>Comparison cues</h2>"
        f"{body_html}</section>"
    )
