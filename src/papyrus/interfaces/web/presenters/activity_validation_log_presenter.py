from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html


def render_activity_validation_log(*, validation_runs: list[dict[str, object]]) -> str:
    return (
        '<section class="activity-validation-log" data-component="activity-validation-log" data-surface="activity">'
        "<h2>Validation runs</h2>"
        '<div class="activity-validation-log__list">'
        + join_html(
            [
                (
                    '<article class="activity-validation-log__item">'
                    f'<p>{escape(run["run_type"])} · {escape(run["status"])} · findings {escape(run["finding_count"])}</p>'
                    f'<p>{escape(format_timestamp(run["completed_at"]))}</p>'
                    "</article>"
                )
                for run in validation_runs[:20]
            ]
        )
        + "</div></section>"
    )
