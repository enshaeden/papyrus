from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_review_cleanup_strip(*, cleanup_counts: dict[str, object]) -> str:
    return (
        '<section class="review-cleanup-strip" data-component="review-cleanup-strip" data-surface="review">'
        f"<span>Placeholder-heavy {escape(cleanup_counts.get('placeholder-heavy', 0))}</span>"
        f"<span>Legacy fallback {escape(cleanup_counts.get('legacy-blueprint-fallback', 0))}</span>"
        f"<span>Ownership gaps {escape(cleanup_counts.get('unclear-ownership', 0))}</span>"
        f"<span>Weak evidence {escape(cleanup_counts.get('weak-evidence', 0))}</span>"
        f"<span>Migration gaps {escape(cleanup_counts.get('migration-gaps', 0))}</span>"
        "</section>"
    )
