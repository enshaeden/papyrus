from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html


def render_revision_audit_sequence(
    *, components: ComponentPresenter, history: dict[str, Any]
) -> str:
    del components
    body_html = (
        join_html(
            [
                f'<div class="revision-audit-sequence__item"><strong>{escape(format_timestamp(event["occurred_at"]))}</strong><p>{escape(event["event_type"])} · {escape(event["actor"])}</p></div>'
                for event in history["audit_events"]
            ]
        )
        or '<p class="empty-state-copy">No audit events recorded.</p>'
    )
    return (
        '<section class="revision-audit-sequence" data-component="revision-audit-sequence" data-surface="revision-history">'
        '<p class="revision-audit-sequence__kicker">Governance</p>'
        "<h2>Audit sequence</h2>"
        f"{body_html}</section>"
    )
