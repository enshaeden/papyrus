from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import activity_url, validation_run_new_url
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link


def _page_definition(
    *,
    page_template: str,
    page_title: str,
    headline: str,
    active_nav: str,
    page_context: dict[str, Any],
    aside_html: str = "",
    shell_variant: str | None = None,
    show_actor_links: bool = False,
    actions_html: str = "",
) -> dict[str, Any]:
    page = {
        "page_template": page_template,
        "page_title": page_title,
        "page_header": {
            "headline": headline,
            "show_actor_links": show_actor_links,
        },
        "active_nav": active_nav,
        "aside_html": aside_html,
        "page_context": page_context,
    }
    if actions_html:
        page["page_header"]["actions_html"] = actions_html
    if shell_variant is not None:
        page["shell_variant"] = shell_variant
    return page


def render_activity_filter_bar(*, role: str, object_id: str | None, selected_group: str) -> str:
    return (
        f'<form class="activity-filter-bar" method="get" action="{escape(activity_url(role))}" data-component="activity-filter-bar" data-surface="activity">'
        f'<input type="text" name="object_id" placeholder="Filter object ID" value="{escape(object_id or "")}" />'
        '<select name="group">'
        f'<option value=""{" selected" if not selected_group else ""}>All activity groups</option>'
        f'<option value="service_changes"{" selected" if selected_group == "service_changes" else ""}>Service changes</option>'
        f'<option value="evidence_degradation"{" selected" if selected_group == "evidence_degradation" else ""}>Evidence degradation</option>'
        f'<option value="validation_failures"{" selected" if selected_group == "validation_failures" else ""}>Validation failures</option>'
        f'<option value="manual_suspect_marks"{" selected" if selected_group == "manual_suspect_marks" else ""}>Manual suspect marks</option>'
        "</select>"
        '<button class="button button-primary" type="submit">Show activity</button>'
        "</form>"
    )


def render_activity_audit_log(*, events: list[dict[str, object]]) -> str:
    return (
        '<section class="activity-audit-log" data-component="activity-audit-log" data-surface="activity">'
        '<p class="activity-log__kicker">Audit</p>'
        "<h2>Audit log</h2>"
        '<div class="activity-audit-log__list">'
        + join_html(
            [
                (
                    '<article class="activity-audit-log__item">'
                    f"<p>{escape(event['event_type'])} · {escape(format_timestamp(event['occurred_at']))} · {escape(event['actor'])}</p>"
                    f"<p>{escape(event['object_id'] or 'No object')} · {escape(event['revision_id'] or 'No revision')}</p>"
                    "</article>"
                )
                for event in events[:20]
            ]
        )
        + "</div></section>"
    )


def render_activity_event_list(*, structured_events: list[dict[str, object]]) -> str:
    return (
        join_html(
            [
                (
                    '<article class="activity-event" data-component="activity-event" data-surface="activity">'
                    f'<p class="activity-event__kicker">{escape(event["group"].replace("_", " "))} · {escape(event["occurred_at"])}</p>'
                    f"<h2>{escape(event['what_happened'])}</h2>"
                    f'<p class="activity-event__affected">{escape(str(event["entity_type"]) + ":" + str(event["entity_id"]))}</p>'
                    f'<p class="activity-event__next">{escape(event["next_action"])}</p>'
                    '<details class="activity-event__details"><summary>Show audit details</summary>'
                    f"<pre>{escape(', '.join(str(key) + '=' + str(value) for key, value in event['payload'].items() if value) or 'No extra payload details')}</pre>"
                    "</details></article>"
                )
                for event in structured_events
            ]
        )
        if structured_events
        else '<section class="activity-empty"><h2>No matching activity</h2><p>Adjust the filter or wait for the next recorded event.</p></section>'
    )


def render_activity_validation_log(*, validation_runs: list[dict[str, object]]) -> str:
    return (
        '<section class="activity-validation-log" data-component="activity-validation-log" data-surface="activity">'
        '<p class="activity-log__kicker">Validation</p>'
        "<h2>Validation runs</h2>"
        '<div class="activity-validation-log__list">'
        + join_html(
            [
                (
                    '<article class="activity-validation-log__item">'
                    f"<p>{escape(run['run_type'])} · {escape(run['status'])} · findings {escape(run['finding_count'])}</p>"
                    f"<p>{escape(format_timestamp(run['completed_at']))}</p>"
                    "</article>"
                )
                for run in validation_runs[:20]
            ]
        )
        + "</div></section>"
    )


def present_audit_page(
    renderer: TemplateRenderer,
    *,
    role: str,
    events: list[dict[str, Any]],
    structured_events: list[dict[str, Any]],
    validation_runs: list[dict[str, Any]],
    object_id: str | None,
    selected_group: str,
) -> dict[str, Any]:
    del renderer
    is_admin = role == "admin"
    return _page_definition(
        page_template="pages/manage_audit.html",
        page_title="Audit" if is_admin else "Activity",
        headline="Audit" if is_admin else "Activity",
        active_nav="activity",
        show_actor_links=False,
        page_context={
            "filter_bar_html": render_activity_filter_bar(
                role=role, object_id=object_id, selected_group=selected_group
            ),
            "audit_html": render_activity_audit_log(events=events),
            "event_html": render_activity_event_list(structured_events=structured_events),
            "validation_html": render_activity_validation_log(validation_runs=validation_runs),
        },
    )


def present_validation_runs_page(
    renderer: TemplateRenderer,
    *,
    role: str,
    runs: list[dict[str, Any]],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    add_run_html = components.action_bar(
        items=[
            link(
                "Record validation run",
                validation_run_new_url(role),
                css_class="button button-primary",
            )
        ]
    )
    validation_table_html = components.section_card(
        title="Validation runs",
        eyebrow="Validation",
        body_html=components.queue_table(
            headers=["Run", "Status", "Findings", "Completed"],
            rows=[
                [
                    components.decision_cell(
                        title_html=escape(run["run_type"]),
                        meta=[escape(run["run_id"])],
                    ),
                    escape(run["status"]),
                    escape(run["finding_count"]),
                    escape(format_timestamp(run["completed_at"])),
                ]
                for run in runs
            ],
            table_id="validation-runs",
        ),
    )
    return _page_definition(
        page_template="pages/manage_validation_runs.html",
        page_title="Validation runs",
        headline="Validation runs",
        active_nav="activity",
        show_actor_links=True,
        actions_html=add_run_html,
        page_context={"validation_table_html": validation_table_html},
    )


def present_validation_run_new_page(
    renderer: TemplateRenderer,
    *,
    values: dict[str, str],
    errors: dict[str, list[str]],
) -> dict[str, Any]:
    forms = FormPresenter(renderer)
    components = ComponentPresenter(renderer)
    form_html = components.section_card(
        title="Record validation run",
        eyebrow="Validation",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(
                field_id="run_id",
                label="Run ID",
                control_html=forms.input(field_id="run_id", name="run_id", value=values["run_id"]),
                errors=errors.get("run_id"),
            )
            + forms.field(
                field_id="run_type",
                label="Run type",
                control_html=forms.input(
                    field_id="run_type",
                    name="run_type",
                    value=values["run_type"],
                    placeholder="manual_operator_check",
                ),
                errors=errors.get("run_type"),
            )
            + forms.field(
                field_id="status",
                label="Status",
                control_html=forms.input(
                    field_id="status", name="status", value=values["status"], placeholder="passed"
                ),
                errors=errors.get("status"),
            )
            + forms.field(
                field_id="finding_count",
                label="Finding count",
                control_html=forms.input(
                    field_id="finding_count",
                    name="finding_count",
                    value=values["finding_count"],
                    input_type="number",
                ),
                errors=errors.get("finding_count"),
            )
            + forms.field(
                field_id="details",
                label="Details",
                control_html=forms.textarea(
                    field_id="details", name="details", value=values["details"], rows=4
                ),
                hint="Optional operator-readable summary stored with the run.",
            )
            + forms.button(label="Record validation run")
            + "</form>"
        ),
    )
    return _page_definition(
        page_template="pages/manage_validation_run_new.html",
        page_title="Record validation run",
        headline="Record validation run",
        active_nav="activity",
        shell_variant="minimal",
        page_context={"form_html": form_html},
    )
