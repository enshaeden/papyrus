from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_health_validation_board(*, validation_posture: dict[str, str]) -> str:
    return (
        '<section class="health-validation-board" data-component="health-validation-board" data-surface="knowledge-health">'
        "<h2>Validation posture</h2>"
        f'<p>{escape(validation_posture["summary"])}</p>'
        f'<p>{escape(validation_posture["detail"])}</p>'
        "</section>"
    )
