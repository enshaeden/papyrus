from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_health_cleanup_board(*, cleanup_counts: dict[str, object]) -> str:
    return (
        '<section class="health-cleanup-board" data-component="health-cleanup-board" data-surface="knowledge-health">'
        "<h2>Cleanup and trust debt</h2>"
        '<div class="health-cleanup-board__grid">'
        f'<article><p class="health-cleanup-board__metric">{escape(cleanup_counts.get("placeholder-heavy", 0))}</p><p>Placeholder-heavy</p></article>'
        f'<article><p class="health-cleanup-board__metric">{escape(cleanup_counts.get("legacy-blueprint-fallback", 0))}</p><p>Legacy fallback</p></article>'
        f'<article><p class="health-cleanup-board__metric">{escape(cleanup_counts.get("unclear-ownership", 0))}</p><p>Ownership gaps</p></article>'
        f'<article><p class="health-cleanup-board__metric">{escape(cleanup_counts.get("weak-evidence", 0))}</p><p>Weak evidence</p></article>'
        f'<article><p class="health-cleanup-board__metric">{escape(cleanup_counts.get("migration-gaps", 0))}</p><p>Migration gaps</p></article>'
        "</div></section>"
    )
