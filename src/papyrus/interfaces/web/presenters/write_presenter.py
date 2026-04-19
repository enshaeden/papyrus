from __future__ import annotations

from papyrus.application.blueprint_registry import (
    list_primary_authoring_blueprints,
)
from papyrus.application.ui_projection import (
    build_draft_readiness_projection,
    workflow_projection_payload,
)
from papyrus.domain.blueprints import Blueprint
from papyrus.domain.evidence import summarize_evidence_posture
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    action_descriptor,
    render_action_contract_panel,
    render_projection_status_panel,
)
from papyrus.interfaces.web.presenters.write_support_presenter import (
    evidence_guidance_body_html,
    render_next_action_panel_html,
    render_object_progress_html,
    render_progress_bar_html,
    render_revision_error_summary_html,
    render_section_fields_html,
    submit_evidence_posture_detail,
    support_details_html,
)
from papyrus.interfaces.web.urls import write_object_url, write_submit_url
from papyrus.interfaces.web.view_helpers import escape, join_html, render_list


def _blueprint_select_html(
    *,
    field_id: str,
    field_name: str,
    value: str,
    blueprints: list[Blueprint],
) -> str:
    option_html = "".join(
        f'<option value="{escape(blueprint.blueprint_id)}"{" selected" if blueprint.blueprint_id == value else ""}>'
        f"{escape(blueprint.display_name)}</option>"
        for blueprint in blueprints
    )
    return (
        f'<select id="{escape(field_id)}" name="{escape(field_name)}" '
        'data-component="form-control" data-control-type="select">'
        f"{option_html}</select>"
    )


def _blueprint_scope_list_html(blueprints: list[Blueprint]) -> str:
    return (
        '<ul class="stack-list">'
        + join_html(
            [
                (
                    "<li><strong>"
                    + escape(blueprint.display_name)
                    + ":</strong> "
                    + escape(blueprint.description)
                    + "</li>"
                )
                for blueprint in blueprints
            ]
        )
        + "</ul>"
    )


def _primary_guidance_html() -> str:
    primary_blueprints = list_primary_authoring_blueprints()
    return _blueprint_scope_list_html(primary_blueprints)


def present_object_setup_page(
    runtime,
    values: dict[str, str],
    errors: dict[str, list[str]],
    *,
    form_action: str,
    authoring_blueprints: list[Blueprint],
    authoring_mode: str,
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    primary_controls = [
        forms.field(
            field_id="object_type",
            label="Content type",
            control_html=_blueprint_select_html(
                field_id="object_type",
                field_name="object_type",
                value=values["object_type"],
                blueprints=authoring_blueprints,
            ),
            hint="Choose the primary template that best fits the guidance.",
            errors=errors.get("object_type"),
        ),
        forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(
                field_id="title",
                name="title",
                value=values["title"],
                placeholder="Name the guidance clearly",
            ),
            hint="Use the name readers will recognize in search and review.",
            errors=errors.get("title"),
        ),
        forms.field(
            field_id="summary",
            label="Summary",
            control_html=forms.textarea(
                field_id="summary",
                name="summary",
                value=values["summary"],
                rows=3,
                placeholder="Summarize the outcome and when to use it.",
            ),
            hint="Keep it short and action-focused.",
            errors=errors.get("summary"),
        ),
        forms.field(
            field_id="owner",
            label="Owner",
            control_html=forms.input(
                field_id="owner",
                name="owner",
                value=values["owner"],
                placeholder="Team or person responsible",
            ),
            hint="Name the team or person accountable for keeping this guidance current.",
            errors=errors.get("owner"),
        ),
        forms.field(
            field_id="team",
            label="Team",
            control_html=forms.select(
                field_id="team",
                name="team",
                value=values["team"],
                options=runtime.taxonomies["teams"]["allowed_values"],
            ),
            errors=errors.get("team"),
        ),
        forms.field(
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(
                field_id="review_cadence",
                name="review_cadence",
                value=values["review_cadence"],
                options=runtime.taxonomies["review_cadences"]["allowed_values"],
            ),
            errors=errors.get("review_cadence"),
        ),
        forms.field(
            field_id="object_lifecycle_state",
            label="Lifecycle state",
            control_html=forms.select(
                field_id="object_lifecycle_state",
                name="object_lifecycle_state",
                value=values["object_lifecycle_state"],
                options=runtime.taxonomies["statuses"]["allowed_values"],
            ),
            errors=errors.get("object_lifecycle_state"),
        ),
        forms.field(
            field_id="systems",
            label="Related systems",
            control_html=forms.input(
                field_id="systems",
                name="systems",
                value=values["systems"],
                placeholder="List related systems, separated by commas",
            ),
            errors=errors.get("systems"),
        ),
        forms.field(
            field_id="tags",
            label="Tags",
            control_html=forms.input(
                field_id="tags",
                name="tags",
                value=values["tags"],
                placeholder="Add search tags, separated by commas",
            ),
            errors=errors.get("tags"),
        ),
    ]
    publishing_controls = [
        forms.field(
            field_id="object_id",
            label="Reference code",
            control_html=forms.input(
                field_id="object_id",
                name="object_id",
                value=values["object_id"],
                placeholder="Created from the title if left blank",
            ),
            errors=errors.get("object_id"),
        ),
        forms.field(
            field_id="canonical_path",
            label="Publishing location",
            control_html=forms.input(
                field_id="canonical_path",
                name="canonical_path",
                value=values["canonical_path"],
                placeholder="Created from the title if left blank",
            ),
            errors=errors.get("canonical_path"),
        ),
    ]
    validation_html = render_revision_error_summary_html(components, errors) if errors else ""
    body_html = (
        f'<form class="governed-form" method="post" action="{escape(form_action)}">'
        + '<section class="form-section"><h3>Draft details</h3>'
        + "".join(primary_controls)
        + "</section>"
        + '<section class="form-section"><h3>Publishing details</h3>'
        + "".join(publishing_controls)
        + "</section>"
        + forms.button(label="Start drafting")
        + "</form>"
    )
    return {
        "validation_html": validation_html,
        "progress_html": render_object_progress_html(components, values=values, errors=errors),
        "form_html": components.content_section(
            title="Start from a primary template",
            eyebrow="Authoring",
            body_html=body_html,
        ),
        "guidance_html": support_details_html(
            title="Primary template set",
            summary="Papyrus organizes visible authoring around runbooks, known errors, and service records.",
            body_html=_primary_guidance_html(),
        ),
    }


def present_guided_revision_page(
    runtime,
    *,
    role: str,
    object_detail: dict[str, object],
    draft_status: dict[str, object],
    revision_id: str,
    section_id: str,
    is_first_revision: bool,
    form_values: dict[str, str],
    form_errors: dict[str, list[str]],
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    blueprint = draft_status["blueprint"]
    section = blueprint.section(section_id)
    completion = draft_status["completion"]
    validation_html = (
        render_revision_error_summary_html(components, form_errors) if form_errors else ""
    )
    section_form_html = (
        f'<form class="governed-form" method="post" action="{escape(write_object_url(str(object_detail["object"]["object_id"]), revision_id=revision_id, section_id=section_id))}">'
        f'<input type="hidden" name="section_id" value="{escape(section_id)}" />'
        + render_section_fields_html(
            runtime,
            role=role,
            section=section,
            values=form_values,
            errors=form_errors,
            object_id=str(object_detail["object"]["object_id"]),
        )
        + '<div class="section-editor-actions">'
        + forms.button(label="Save and continue")
        + (
            forms.link_button(
                label="Check review handoff",
                href=write_submit_url(str(object_detail["object"]["object_id"]), revision_id),
                variant="secondary",
            )
            if completion["completion_percentage"] > 0
            else ""
        )
        + "</div></form>"
    )
    guidance_html = ""
    if str(section.section_type.value) == "references":
        guidance_html = support_details_html(
            title="Evidence handling",
            summary="Link existing guidance first and enter manual sources only when needed.",
            body_html=evidence_guidance_body_html(role=role),
        )
    return {
        "stage_label_html": "",
        "progress_html": render_progress_bar_html(
            runtime, blueprint=blueprint, completion=completion, current_section_id=section_id
        ),
        "validation_html": validation_html,
        "section_editor_html": runtime.template_renderer.render(
            "partials/section_editor.html",
            {
                "section_title": escape(section.display_name),
                "section_description": escape(section.description),
                "section_help_text": escape(section.help_text),
                "fields_html": section_form_html,
            },
        ),
        "next_action_html": render_next_action_panel_html(
            components,
            detail=object_detail,
            blueprint=blueprint,
            completion=completion,
        ),
        "guidance_html": guidance_html,
    }


def present_submit_page(
    runtime,
    *,
    role: str,
    detail,
    object_detail,
    blueprint,
    completion: dict[str, object],
    findings: list[str],
    form_errors: dict[str, list[str]],
    values: dict[str, str],
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    revision = detail["revision"]
    evidence_posture = completion.get("evidence_posture") or summarize_evidence_posture(
        detail.get("citations", [])
    )
    submit_action = action_descriptor(object_detail.get("ui_projection"), "submit_for_review")
    draft_projection = workflow_projection_payload(
        build_draft_readiness_projection(
            blueprint=blueprint,
            completion=completion,
            submit_action=submit_action,
        )
    )
    form_html = components.content_section(
        title="Send to review",
        eyebrow="Authoring",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(
                field_id="notes",
                label="Submission notes",
                control_html=forms.textarea(
                    field_id="notes", name="notes", value=values.get("notes", ""), rows=3
                ),
                hint="Optional notes for reviewers and assignment triage.",
                errors=form_errors.get("notes"),
            )
            + forms.button(label="Send to review", action_id="submit_for_review")
            + "</form>"
        ),
        variant="submit-form",
        surface="write-submit",
    )
    summary_html = components.content_section(
        title="Submission summary",
        eyebrow="Authoring",
        body_html=(
            f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_review_state'])}</p>"
            f"<p><strong>What changed:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
            f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
            f"<p><strong>Evidence posture:</strong> {escape(evidence_posture['summary'])}</p>"
            f"<p><strong>Evidence note:</strong> {escape(submit_evidence_posture_detail(evidence_posture))}</p>"
            f"<p><strong>Publishing location:</strong> {escape(detail['object']['canonical_path'])}</p>"
        ),
        variant="submission-summary",
        surface="write-submit",
    )
    findings_html = components.context_panel(
        title="Pre-submit validation",
        eyebrow="Validation",
        body_html=components.list_body(
            items=[escape(item) for item in findings] or ["No blocking findings detected."],
            empty_label="No blocking findings detected.",
            css_class="validation-findings",
        ),
        tone="warning" if findings else "approved",
        variant="pre-submit-validation",
        surface="write-submit",
    )
    progress_rows = [
        f"{row['label']}: {row['value']}"
        for row in draft_projection.get("rows", [])
        if row.get("label") and row.get("value")
    ]
    progress_html = components.context_panel(
        title="Step 3 of 3",
        eyebrow="Progress",
        tone=str(draft_projection.get("tone") or "default"),
        body_html=(
            f"<p>{escape(draft_projection.get('summary') or 'Submission status available.')}</p>"
            + (
                render_list([escape(item) for item in progress_rows], css_class="stack-list")
                if progress_rows
                else ""
            )
            + f"<p><strong>Warnings to review:</strong> {escape(len(findings))}</p>"
        ),
        footer_html='<p class="section-footer">Send the revision only after the remaining warnings are understood.</p>',
        variant="submission-progress",
        surface="write-submit",
    )
    guidance_sections = [
        support_details_html(
            title="Review the submission contract",
            summary="See the governed posture and handoff rules without pinning them beside the form.",
            body_html=join_html(
                [
                    render_projection_status_panel(
                        components,
                        title="Current governed posture",
                        ui_projection=object_detail.get("ui_projection"),
                    ),
                    render_action_contract_panel(
                        components,
                        title="Submission contract",
                        action=submit_action,
                    ),
                ]
            ),
        )
    ]
    if any("Evidence posture:" in item for item in findings):
        guidance_sections.append(
            support_details_html(
                title="How to strengthen weak evidence",
                summary="Use the manage flow when reviewer confidence depends on stronger capture metadata.",
                body_html=evidence_guidance_body_html(
                    role=role,
                    include_action=True,
                    object_id=str(detail["object"]["object_id"]),
                ),
            )
        )
    return {
        "summary_html": summary_html,
        "progress_html": progress_html,
        "findings_html": findings_html,
        "guidance_html": join_html(guidance_sections),
        "form_html": form_html,
    }
