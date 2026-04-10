from __future__ import annotations

import json
from urllib.parse import quote_plus

from papyrus.application.authoring_flow import compute_completion_state, create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.blueprint_registry import get_blueprint, list_blueprints
from papyrus.application.commands import create_object_command, create_revision_command, submit_for_review_command
from papyrus.application.queries import knowledge_object_detail, review_detail, search_knowledge_objects
from papyrus.application.ui_projection import build_draft_readiness_projection, workflow_projection_payload
from papyrus.domain.evidence import summarize_evidence_posture
from papyrus.interfaces.web.forms.object_forms import default_object_values, validate_object_form
from papyrus.interfaces.web.forms.revision_forms import build_revision_defaults, build_submission_findings, validate_revision_form
from papyrus.interfaces.web.forms.review_forms import validate_submit_form
from papyrus.interfaces.web.http import Request, html_response, json_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    action_descriptor,
    projection_state,
    projection_use_guidance,
)
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, join_html, link, parse_multiline, quoted_path, render_list


def _support_details_html(*, title: str, summary: str, body_html: str, open_by_default: bool = False) -> str:
    return (
        f'<details class="support-disclosure"{" open" if open_by_default else ""}>'
        f'<summary><span class="support-disclosure-title">{escape(title)}</span>'
        f'<span class="support-disclosure-summary">{escape(summary)}</span></summary>'
        f'<div class="support-disclosure-body">{body_html}</div>'
        "</details>"
    )


def _render_object_form(runtime, values: dict[str, str], errors: dict[str, list[str]], *, form_action: str) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    primary_controls = [
        forms.field(
            field_id="object_type",
            label="Content type",
            control_html=forms.select(
                field_id="object_type",
                name="object_type",
                value=values["object_type"],
                options=[blueprint.blueprint_id for blueprint in list_blueprints()],
            ),
            hint="Choose the structure that best fits the guidance you are starting.",
            errors=errors.get("object_type"),
        ),
        forms.field(
<<<<<<< HEAD
            field_id="object_id",
            label="Object ID",
            control_html=forms.input(field_id="object_id", name="object_id", value=values["object_id"]),
            hint="Stable control-plane identifier in kb-slug format.",
            errors=errors.get("object_id"),
        ),
        forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(field_id="title", name="title", value=values["title"]),
            hint="Operator-facing title used in read surfaces and audit history.",
=======
            field_id="title",
            label="Title",
            control_html=forms.input(field_id="title", name="title", value=values["title"], placeholder="Name the guidance clearly"),
            hint="Use the name readers will recognize in search and review.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
            errors=errors.get("title"),
        ),
        forms.field(
            field_id="summary",
            label="Summary",
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
            control_html=forms.textarea(field_id="summary", name="summary", value=values["summary"], rows=3),
            hint="Short operational summary shown above the fold.",
=======
            control_html=forms.textarea(
                field_id="summary",
                name="summary",
                value=values["summary"],
                rows=3,
                placeholder="Summarize the outcome and when to use it.",
            ),
            hint="Keep it short and action-focused.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
            errors=errors.get("summary"),
        ),
        forms.field(
            field_id="owner",
            label="Owner",
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
            control_html=forms.input(field_id="owner", name="owner", value=values["owner"]),
            hint="Visible ownership is required for trust posture.",
=======
            control_html=forms.input(field_id="owner", name="owner", value=values["owner"], placeholder="Team or person responsible"),
            hint="Name the person or team accountable for keeping this guidance current.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
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
            hint="Choose the team responsible for this guidance.",
            errors=errors.get("team"),
        ),
        forms.field(
<<<<<<< HEAD
            field_id="canonical_path",
            label="Canonical path",
            control_html=forms.input(field_id="canonical_path", name="canonical_path", value=values["canonical_path"]),
            hint="Guidance only at this stage, but it must remain under knowledge/ for durable source placement.",
            errors=errors.get("canonical_path"),
        ),
        forms.field(
=======
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(
                field_id="review_cadence",
                name="review_cadence",
                value=values["review_cadence"],
                options=runtime.taxonomies["review_cadences"]["allowed_values"],
            ),
            hint="Set how often this guidance should be checked.",
            errors=errors.get("review_cadence"),
        ),
        forms.field(
            field_id="status",
            label="Status",
            control_html=forms.select(
                field_id="status",
                name="status",
                value=values["status"],
                options=runtime.taxonomies["statuses"]["allowed_values"],
            ),
            hint="New guidance usually starts as draft.",
            errors=errors.get("status"),
        ),
        forms.field(
            field_id="systems",
<<<<<<< HEAD
            label="Systems",
            control_html=forms.input(field_id="systems", name="systems", value=values["systems"]),
            hint="Comma-separated controlled system references.",
=======
            label="Related systems",
            control_html=forms.input(
                field_id="systems",
                name="systems",
                value=values["systems"],
                placeholder="List related systems, separated by commas",
            ),
            hint="Add the systems this guidance applies to.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
            errors=errors.get("systems"),
        ),
        forms.field(
            field_id="tags",
            label="Tags",
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
            control_html=forms.input(field_id="tags", name="tags", value=values["tags"]),
            hint="Comma-separated controlled tags for discovery and reporting.",
=======
            control_html=forms.input(
                field_id="tags",
                name="tags",
                value=values["tags"],
                placeholder="Add search tags, separated by commas",
            ),
            hint="Use a few tags that will help readers find this quickly.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
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
            hint="Use lowercase words separated by hyphens. This stays with the guidance in links and search.",
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
            hint="Where the published source will live in the knowledge library.",
            errors=errors.get("canonical_path"),
        ),
    ]
    validation_html = _revision_error_summary_html(components, errors) if errors else ""
    body_html = (
        f'<form class="governed-form" method="post" action="{escape(form_action)}">'
<<<<<<< HEAD
        + "".join(controls)
        + forms.button(label="Start draft")
        + "</form>"
    )
    guidance_html = _support_details_html(
        title="Why this step matters",
        summary="Identity, ownership, and source placement become the durable draft anchor.",
        body_html=(
            "<p>Start by choosing the blueprint, defining the purpose, and recording accountable ownership. Papyrus then carries the object shell into guided section-by-section drafting.</p>"
        ),
=======
        + '<section class="form-section"><h3>Draft details</h3>'
        + "".join(primary_controls)
        + "</section>"
        + '<section class="form-section"><h3>Publishing details</h3><p class="section-intro">Keep the draft traceable and ready to publish.</p>'
        + "".join(publishing_controls)
        + "</section>"
        + forms.button(label="Start drafting")
        + "</form>"
    )
    guidance_html = components.section_card(
        title="What happens next",
        eyebrow="Write",
        body_html="<p>After setup, you will complete the first draft one section at a time and then send it for review.</p>",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
    )
    return {
        "validation_html": validation_html,
        "progress_html": _object_progress_html(components, values=values, errors=errors),
<<<<<<< Updated upstream
        "form_html": components.section_card(title="Create draft shell", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }

=======
<<<<<<< HEAD
        "form_html": components.section_card(title="Create draft shell", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }

=======
        "form_html": components.section_card(title="Set up the draft", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }


def _common_revision_aside(runtime, detail) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    item = detail["object"]
    current_revision = detail.get("current_revision")
    submit_action = action_descriptor(detail.get("ui_projection"), "submit_for_review")
    return join_html(
        [
            render_projection_status_panel(
                components,
                title="Governed posture",
                ui_projection=detail.get("ui_projection"),
            ),
            render_action_contract_panel(
                components,
                title="Submission contract",
                action=submit_action,
            ),
            components.metadata_list(
                title="Revision context",
                rows=[
                    (
                        "Current revision",
                        escape(
                            f"#{current_revision['revision_number']} · {current_revision['revision_review_state']}"
                            if current_revision
                            else "No revision attached yet"
                        ),
                    ),
                    ("Owner", escape(item["owner"])),
                    ("Publishing location", escape(item["canonical_path"])),
                ],
            ),
        ]
    )


>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
def _completion_ratio(values: dict[str, str], fields: list[str]) -> tuple[int, int]:
    total = len(fields)
    completed = sum(1 for field in fields if values.get(field, "").strip())
    return completed, total


def _object_progress_html(components, *, values: dict[str, str], errors: dict[str, list[str]]) -> str:
    purpose_completed, purpose_total = _completion_ratio(values, ["object_type", "title", "summary"])
    stewardship_completed, stewardship_total = _completion_ratio(values, ["owner", "team", "review_cadence", "status"])
    source_completed, source_total = _completion_ratio(values, ["object_id", "canonical_path"])
    blockers = sum(len(messages) for messages in errors.values())
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
    return components.section_card(
        title="Step 1 of 3",
        eyebrow="Progress",
        tone="warning" if blockers else "brand",
        body_html=(
            "<p><strong>Current task:</strong> define the shell that future revisions will inherit.</p>"
            + render_list(
                [
                    escape(f"Purpose and type: {purpose_completed}/{purpose_total} complete"),
                    escape(f"Ownership and cadence: {stewardship_completed}/{stewardship_total} complete"),
                    escape(f"Durable ID and path: {source_completed}/{source_total} complete"),
                ],
                css_class="stack-list",
            )
            + f"<p><strong>Blocking fields:</strong> {escape(blockers)}</p>"
        ),
        footer_html='<p class="section-footer">Next: Papyrus opens the first required section for guided drafting.</p>',
<<<<<<< Updated upstream
=======
=======
    return join_html(
        [
            _progress_card(components, title="Define the draft", completed=purpose_completed, total=purpose_total, detail="Choose the content type, title, and summary readers will see first.", tone="brand"),
            _progress_card(components, title="Set ownership", completed=stewardship_completed, total=stewardship_total, detail="Owner, team, cadence, and status keep the guidance accountable."),
            _progress_card(components, title="Set publishing details", completed=source_completed, total=source_total, detail="Reference code and publishing location keep the draft traceable."),
            components.section_card(
                title="Readiness",
                eyebrow="Progress",
                tone="warning" if blockers else "approved",
                body_html=(
                    f"<p><strong>Blocking fields:</strong> {escape(blockers)}</p>"
                    "<p>Start drafting once the required setup, ownership, and publishing details are complete.</p>"
                ),
            ),
        ]
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
    )


def _revision_progress_html(components, *, object_type: str, values: dict[str, str], errors: dict[str, list[str]], findings: list[str] | None) -> str:
    purpose_completed, purpose_total = _completion_ratio(values, ["title", "summary", "owner", "team", "status"])
    linkage_completed, linkage_total = _completion_ratio(values, ["review_cadence", "audience", "related_services", "related_object_ids", "change_summary"])
    evidence_completed, evidence_total = _completion_ratio(values, ["citation_1_source_title", "citation_1_source_ref"])
    evidence_posture = _evidence_posture_from_form_values(values)
    type_specific_fields = {
        "runbook": ["prerequisites", "steps", "verification", "rollback", "use_when", "boundaries_and_escalation"],
        "known_error": ["symptoms", "scope", "cause", "diagnostic_checks", "mitigations", "detection_notes", "escalation_threshold"],
        "service_record": ["service_name", "dependencies", "support_entrypoints", "common_failure_modes", "scope_notes", "operational_notes"],
        "policy": ["policy_scope", "controls"],
        "system_design": ["architecture", "dependencies", "interfaces", "common_failure_modes", "operational_notes"],
    }
    if object_type not in type_specific_fields:
        raise ValueError(f"unsupported object type for revision progress: {object_type}")
    content_completed, content_total = _completion_ratio(values, type_specific_fields)
    blockers = sum(len(messages) for messages in errors.values())
    warnings = len(findings or [])
    return components.section_card(
        title="Advanced editor status",
        eyebrow="Progress",
        tone="warning" if blockers or warnings else "approved",
        body_html=(
            "<p><strong>Current task:</strong> keep the full draft coherent before handoff.</p>"
            + render_list(
                [
                    escape(f"Purpose and stewardship: {purpose_completed}/{purpose_total} complete"),
                    escape(f"Core structured content: {content_completed}/{content_total} complete"),
                    escape(f"Links and evidence: {linkage_completed + evidence_completed}/{linkage_total + evidence_total} complete"),
                ],
                css_class="stack-list",
            )
            + f"<p><strong>Validation blockers:</strong> {escape(blockers)}</p>"
            + f"<p><strong>Warnings to review:</strong> {escape(warnings)}</p>"
            + f"<p>{escape(_revision_evidence_progress_detail(evidence_posture))}</p>"
        ),
        footer_html='<p class="section-footer">Use the guided editor for routine section work and keep this editor for cross-section changes.</p>',
    )


<<<<<<< Updated upstream
=======
<<<<<<< HEAD
=======
def _write_timeline_html(*, stage: str, is_first_revision: bool = False) -> str:
    step_two_label = "Draft first revision" if is_first_revision else "Draft revision"
    steps = [
        {
            "index": "1",
            "title": "Set up draft",
            "detail": "Name the guidance, set ownership, and confirm publishing details.",
            "state": "current" if stage == "object" else "complete",
        },
        {
            "index": "2",
            "title": step_two_label,
            "detail": "Fill in the guided sections and supporting evidence.",
            "state": "current" if stage == "revision" else "complete" if stage == "submit" else "upcoming",
        },
        {
            "index": "3",
            "title": "Submit for review",
            "detail": "Send the draft to review with the right context.",
            "state": "current" if stage == "submit" else "upcoming",
        },
    ]

    parts: list[str] = ['<div class="workflow-top" aria-label="Write workflow">']
    for position, step in enumerate(steps):
        parts.append(
            f'<section class="workflow-top-step is-{escape(step["state"])}">'
            f'<span class="workflow-top-index">{escape(step["index"])}</span>'
            '<div class="workflow-top-copy">'
            f'<p class="workflow-top-label">{escape(step["title"])}</p>'
            f'<p class="workflow-top-detail">{escape(step["detail"])}</p>'
            f'<p class="workflow-top-state">{escape("Current step" if step["state"] == "current" else "Complete" if step["state"] == "complete" else "Next")}</p>'
            "</div>"
            "</section>"
        )
        if position < len(steps) - 1:
            parts.append('<span class="workflow-top-arrow" aria-hidden="true">→</span>')
    parts.append("</div>")
    return "".join(parts)


>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
def _citation_search_status(title: str, reference: str) -> str:
    if title and reference:
        return f"Selected source: {title} -> {reference}"
    return "Search guidance by title, tag, or reference code. Selecting a result fills the fields below."


def _evidence_posture_from_form_values(values: dict[str, str]) -> dict[str, object]:
    citations: list[dict[str, str | None]] = []
    for index in range(1, 4):
        source_title = values.get(f"citation_{index}_source_title", "").strip()
        source_ref = values.get(f"citation_{index}_source_ref", "").strip()
        note = values.get(f"citation_{index}_note", "").strip() or None
        if not any([source_title, source_ref, note]):
            continue
        citations.append(
            {
                "source_title": source_title,
                "source_ref": source_ref,
                "note": note,
                "captured_at": None,
                "integrity_hash": None,
            }
        )
    return summarize_evidence_posture(citations)


def _revision_evidence_progress_detail(evidence_posture: dict[str, object]) -> str:
    if int(evidence_posture.get("weak_external_evidence_count") or 0):
        return (
            f"{evidence_posture['summary']}. External or manual sources still need evidence follow-up before they count as strong support."
        )
    if int(evidence_posture.get("internal_reference_count") or 0):
        return (
            f"{evidence_posture['summary']}. Linked guidance supports traceability and review context, not captured source evidence."
        )
    return "Related services, linked guidance, and evidence posture stay visible here. Adding a source does not automatically make it strong evidence."


def _submit_evidence_posture_detail(evidence_posture: dict[str, object]) -> str:
    if int(evidence_posture.get("weak_external_evidence_count") or 0):
        return "External or manual sources still need evidence follow-up before they count as strong support."
    if int(evidence_posture.get("captured_external_evidence_count") or 0) and int(
        evidence_posture.get("internal_reference_count") or 0
    ):
        return "Linked guidance provides traceability. Captured external evidence is the strongest support recorded so far."
    if int(evidence_posture.get("captured_external_evidence_count") or 0):
        return "Captured external/manual evidence has stronger support metadata recorded."
    if int(evidence_posture.get("internal_reference_count") or 0):
        return "Linked guidance provides traceability and review context."
    return "No evidence references are recorded yet."


def _evidence_guidance_section(
    components,
    *,
    title: str,
    include_action: bool = False,
    object_id: str | None = None,
) -> str:
    action_html = ""
    if include_action and object_id:
        action_html = (
            '<p><strong>Next step:</strong> request evidence follow-up for any source that still needs stronger verification.</p>'
            + f'<p>{link("Request evidence revalidation", f"/manage/objects/{quoted_path(object_id)}/evidence/revalidate", css_class="button button-secondary")}</p>'
        )
    return components.section_card(
        title=title,
        eyebrow="Evidence",
        body_html=(
            "<p>Use this form to link existing guidance or record a source title, reference, and note.</p>"
            "<p>If a source needs stronger verification, complete evidence follow-up after the draft is saved so capture time, integrity details, and any needed snapshot are recorded.</p>"
            + action_html
        ),
        tone="default",
    )


def _citation_lookup_control_html(*, index: int, values: dict[str, str]) -> str:
    lookup_value = values.get(f"citation_{index}_lookup", "")
    return (
        '<div class="citation-picker">'
        f'<input id="citation_{index}_lookup" name="citation_{index}_lookup" type="text" '
        'class="text-input citation-picker-input" '
        f'value="{escape(lookup_value)}" placeholder="Search by title, tag, or reference code" '
        'autocomplete="off" spellcheck="false" />'
        '<div class="citation-picker-results" hidden></div>'
        f'<p class="field-hint citation-picker-status">{escape(_citation_search_status(values.get(f"citation_{index}_source_title", ""), values.get(f"citation_{index}_source_ref", "")))}</p>'
        "</div>"
    )


def _multi_value_picker_status(selected_values: list[str], *, singular_label: str) -> str:
    if not selected_values:
        return f"No {singular_label} selected yet."
    count = len(selected_values)
    return f"{count} {singular_label}{'' if count == 1 else 's'} selected."


def _static_picker_options(values: list[str], *, detail: str) -> list[dict[str, str]]:
    return [
        {
            "value": item,
            "label": item,
            "detail": detail,
        }
        for item in values
    ]


def _multi_value_picker_control_html(
    *,
    field_name: str,
    values: dict[str, str],
    placeholder: str,
    singular_label: str,
    manual_entry_label: str,
    static_options: list[dict[str, str]] | None = None,
    search_url: str | None = None,
    exclude_object_id: str | None = None,
) -> str:
    selected_values = parse_multiline(values.get(field_name, ""))
    search_attr = f' data-search-url="{escape(search_url)}"' if search_url else ""
    exclude_attr = f' data-exclude-object-id="{escape(exclude_object_id)}"' if exclude_object_id else ""
    static_options_attr = escape(json.dumps(static_options or [], ensure_ascii=True))
    return (
        f'<div class="multi-value-picker" data-multi-value-picker data-empty-label="{escape(f"No {singular_label} selected yet.")}"'
        f' data-static-options="{static_options_attr}"{search_attr}{exclude_attr}>'
        '<div class="multi-value-picker-selected"></div>'
        f'<input id="{escape(field_name)}" type="text" class="text-input multi-value-picker-input" '
        f'placeholder="{escape(placeholder)}" autocomplete="off" spellcheck="false" />'
        '<div class="multi-value-picker-results" hidden></div>'
        '<details class="multi-value-picker-manual">'
        f'<summary>{escape(manual_entry_label)}</summary>'
        f'<textarea id="{escape(field_name)}_storage" name="{escape(field_name)}" rows="3" class="multi-value-picker-storage">{escape(chr(10).join(selected_values))}</textarea>'
        "</details>"
        f'<p class="field-hint multi-value-picker-status">{escape(_multi_value_picker_status(selected_values, singular_label=singular_label))}</p>'
        "</div>"
    )


def _revision_error_label(field_name: str) -> str:
    explicit_labels = {
        "object_id": "Reference code",
        "canonical_path": "Publishing location",
        "status": "Status",
        "change_summary": "What changed",
        "related_object_ids": "Related guidance",
    }
    if field_name in explicit_labels:
        return explicit_labels[field_name]
    label = field_name.replace("_", " ")
    label = label.replace(" id", " ID")
    label = label.replace(" ids", " IDs")
    return label[:1].upper() + label[1:] if label else field_name


def _revision_error_summary_html(components, errors: dict[str, list[str]]) -> str:
    items: list[str] = []
    for field_name, messages in errors.items():
        label = escape(_revision_error_label(field_name))
        for message in messages:
            items.append(f"{label}: {escape(message)}")
    if not items:
        return ""
    return components.validation_summary(title="Blocking validation", findings=items, empty_label="")


def _section_form_values(section, stored_values: dict[str, object]) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in section.fields:
        name = str(field["name"])
        kind = str(field.get("kind") or "text")
        current = stored_values.get(name, [] if kind in {"list", "references"} else "")
        if kind == "list":
            values[name] = "\n".join(str(item) for item in current if str(item).strip()) if isinstance(current, list) else str(current or "")
        else:
            values[name] = str(current or "")
    if section.section_type.name == "REFERENCES":
        citations = stored_values.get("citations", []) if isinstance(stored_values.get("citations", []), list) else []
        for index in range(1, 4):
            citation = citations[index - 1] if index - 1 < len(citations) and isinstance(citations[index - 1], dict) else {}
            values[f"citation_{index}_source_title"] = str(citation.get("source_title") or "")
            values[f"citation_{index}_source_type"] = str(citation.get("source_type") or "document")
            values[f"citation_{index}_source_ref"] = str(citation.get("source_ref") or "")
            values[f"citation_{index}_note"] = str(citation.get("note") or "")
    return values


def _parse_section_submission(section, request: Request) -> dict[str, object]:
    if str(section.section_type.value) == "references":
        citations: list[dict[str, str | None]] = []
        for index in range(1, 4):
            source_title = request.form_value(f"citation_{index}_source_title").strip()
            source_type = request.form_value(f"citation_{index}_source_type", "document").strip() or "document"
            source_ref = request.form_value(f"citation_{index}_source_ref").strip()
            note = request.form_value(f"citation_{index}_note").strip() or None
            if not any([source_title, source_ref, note]):
                continue
            citations.append(
                {
                    "source_title": source_title,
                    "source_type": source_type,
                    "source_ref": source_ref,
                    "note": note,
                }
            )
        return {"citations": citations}
    values: dict[str, object] = {}
    for field in section.fields:
        name = str(field["name"])
        kind = str(field.get("kind") or "text")
        raw_value = request.form_value(name)
        if kind == "list":
            values[name] = parse_multiline(raw_value)
        else:
            values[name] = raw_value.strip()
    return values


def _section_errors(
    *,
    blueprint,
    section_id: str,
    section_content: dict[str, dict[str, object]],
    candidate_values: dict[str, object],
    taxonomies: dict[str, dict[str, object]],
) -> dict[str, list[str]]:
    merged = {key: dict(value) for key, value in section_content.items()}
    merged[section_id] = dict(candidate_values)
    completion = compute_completion_state(blueprint=blueprint, section_content=merged, taxonomies=taxonomies)
    section_progress = completion["section_completion_map"].get(section_id, {})
    errors: dict[str, list[str]] = {}
    messages = list(section_progress.get("errors", []))
    if not messages:
        return {}
    if str(blueprint.section(section_id).section_type.value) == "references":
        errors["citations"] = messages
        return errors
    current_index = 0
    for field in blueprint.section(section_id).fields:
        field_name = str(field["name"])
        field_messages: list[str] = []
        while current_index < len(messages) and messages[current_index]:
            message = str(messages[current_index])
            if message.startswith("'"):
                field_messages.append(message)
                current_index += 1
                continue
            if "Citation " in message and field_name != "citations":
                break
            field_messages.append(message)
            current_index += 1
            break
        if field_messages:
            errors[field_name] = field_messages
    if not errors and messages:
        errors["_section"] = messages
    return errors


def _progress_bar_html(runtime, *, blueprint, completion: dict[str, object], current_section_id: str) -> str:
    items = []
    section_map = completion["section_completion_map"]
    for section_id in blueprint.ordering:
        section_status = section_map.get(section_id, {})
        items.append(
            {
                "label": blueprint.section(section_id).display_name,
                "state": (
                    "current"
                    if section_id == current_section_id
                    else "complete"
                    if section_status.get("completed")
                    else "upcoming"
                ),
                "required": section_id in blueprint.required_sections,
            }
        )
    return runtime.template_renderer.render(
        "partials/progress_bar.html",
        {
            "percentage": escape(completion["completion_percentage"]),
            "summary": escape(
                f"{completion['completed_required_sections']} of {completion['required_section_count']} required sections complete"
            ),
            "items_json": escape(json.dumps(items, ensure_ascii=True)),
        },
    )


def _next_action_panel_html(components, *, detail, blueprint, completion: dict[str, object]) -> str:
    submit_action = action_descriptor(detail.get("ui_projection"), "submit_for_review")
    draft_projection = workflow_projection_payload(
        build_draft_readiness_projection(
            blueprint=blueprint,
            completion=completion,
            submit_action=submit_action,
        )
    )
    progress_rows = [
        f"{row['label']}: {row['value']}"
        for row in draft_projection.get("rows", [])
        if row.get("label") and row.get("value")
    ]
    reasons = [str(reason) for reason in draft_projection.get("reasons", [])]
    warnings = [str(warning) for warning in draft_projection.get("warnings", [])]
    return components.section_card(
        title="Ready for handoff?",
        eyebrow="Progress",
        tone=str(draft_projection.get("tone") or "default"),
        body_html=(
            f"<p>{escape(draft_projection.get('summary') or 'Draft status available.')}</p>"
            + (render_list([escape(item) for item in progress_rows], css_class="stack-list") if progress_rows else "")
            + (components.validation_findings(title="Still blocking", items=[escape(item) for item in reasons], tone="warning") if reasons else "")
            + (components.validation_findings(title="Review before handoff", items=[escape(item) for item in warnings], tone="warning") if warnings else "")
        ),
        footer_html='<p class="section-footer">Keep saving the active section until the draft is ready for reviewer handoff.</p>',
    )


def _fallback_revision_href(*, object_id: str, revision_id: str) -> str:
    return f"/write/objects/{quoted_path(object_id)}/revisions/fallback?revision_id={quoted_path(revision_id)}"


def _guided_fallback_html(components, *, object_id: str, revision_id: str) -> str:
    return _support_details_html(
        title="Need the advanced editor?",
        summary="Use it only for cross-section edits, citation lookup, or searchable pickers.",
        body_html=(
<<<<<<< Updated upstream
            "<p>Guided section editing stays the default path. Move to the advanced editor only when you need to change multiple sections in one pass or use the search-assisted reference tools.</p>"
            f'<p>{link("Use advanced editor", _fallback_revision_href(object_id=object_id, revision_id=revision_id), css_class="button button-secondary")}</p>'
=======
<<<<<<< HEAD
            "<p>Guided section editing stays the default path. Move to the advanced editor only when you need to change multiple sections in one pass or use the search-assisted reference tools.</p>"
            f'<p>{link("Use advanced editor", _fallback_revision_href(object_id=object_id, revision_id=revision_id), css_class="button button-secondary")}</p>'
=======
            "<p>Guided editing is the primary path. Use bulk edit only when you need a wider form, source lookup, or multi-select helpers.</p>"
            f'<p>{link("Switch to bulk edit", _fallback_revision_href(object_id=object_id, revision_id=revision_id), css_class="button button-secondary")}</p>'
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
        ),
    )


def _load_draft_context(runtime, *, object_id: str, actor_id: str, requested_revision_id: str | None) -> dict[str, object]:
    initial_detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
    draft = create_draft_from_blueprint(
        object_id=object_id,
        blueprint_id=initial_detail["object"]["object_type"],
        actor=actor_id,
        database_path=runtime.database_path,
        source_root=runtime.source_root,
    )
    revision_id = requested_revision_id or str(draft["revision_id"])
    draft_status = validate_draft_progress(
        object_id=object_id,
        revision_id=revision_id,
        database_path=runtime.database_path,
        source_root=runtime.source_root,
    )
    detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
    return {
        "initial_detail": initial_detail,
        "detail": detail,
        "draft_status": draft_status,
        "revision_id": revision_id,
        "is_first_revision": initial_detail["current_revision"] is None,
    }


def _section_fields_html(runtime, *, blueprint, section, values: dict[str, str], errors: dict[str, list[str]]) -> str:
    forms = FormPresenter(runtime.template_renderer)
    blocks: list[str] = []
    if str(section.section_type.value) == "references":
        for index in range(1, 4):
            blocks.append(
                '<section class="citation-entry">'
                f"<h4>Citation {index}</h4>"
                + forms.field(
                    field_id=f"citation_{index}_source_title",
                    label="Source title",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_title",
                        name=f"citation_{index}_source_title",
                        value=values.get(f"citation_{index}_source_title", ""),
                    ),
                    errors=errors.get("citations") if index == 1 else None,
                )
                + forms.field(
                    field_id=f"citation_{index}_source_type",
                    label="Source type",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_type",
                        name=f"citation_{index}_source_type",
                        value=values.get(f"citation_{index}_source_type", "document"),
                    ),
                )
                + forms.field(
                    field_id=f"citation_{index}_source_ref",
                    label="Source reference",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_ref",
                        name=f"citation_{index}_source_ref",
                        value=values.get(f"citation_{index}_source_ref", ""),
                    ),
                )
                + forms.field(
                    field_id=f"citation_{index}_note",
                    label="Note",
                    control_html=forms.textarea(
                        field_id=f"citation_{index}_note",
                        name=f"citation_{index}_note",
                        value=values.get(f"citation_{index}_note", ""),
                        rows=2,
                    ),
                )
                + "</section>"
            )
        return "".join(blocks)

    for field in section.fields:
        name = str(field["name"])
        label = str(field["label"])
        kind = str(field.get("kind") or "text")
        hint = str(field.get("hint") or "")
        if kind == "select":
            control = forms.select(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                options=list(runtime.taxonomies[str(field.get("taxonomy"))]["allowed_values"]),
            )
        elif kind == "list":
            control = forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=5)
        elif kind == "long_text":
            control = forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=6)
        else:
            control = forms.input(field_id=name, name=name, value=values.get(name, ""))
        blocks.append(forms.field(field_id=name, label=label, control_html=control, hint=hint, errors=errors.get(name)))
    return "".join(blocks)


def _render_guided_revision_page(
    runtime,
    *,
    object_detail: dict[str, object],
    draft_status: dict[str, object],
    revision_id: str,
    section_id: str,
    is_first_revision: bool,
    form_values: dict[str, str] | None = None,
    form_errors: dict[str, list[str]] | None = None,
    page_flash_html: str = "",
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    blueprint = draft_status["blueprint"]
    section = blueprint.section(section_id)
    stored_values = draft_status["section_content"].get(section_id, {})
    values = form_values or _section_form_values(section, stored_values)
    errors = form_errors or {}
    completion = draft_status["completion"]
    progress_html = _progress_bar_html(runtime, blueprint=blueprint, completion=completion, current_section_id=section_id)
    validation_html = (
        runtime.template_renderer.render(
            "partials/validation_inline.html",
            {
                "title": escape("Section blockers"),
                "items_html": ComponentPresenter(runtime.template_renderer).validation_findings(
                    title="Section blockers",
                    items=[escape(item) for item in errors.get("_section", [])],
                    tone="warning",
                ),
            },
        )
        if errors.get("_section")
        else ""
    )
    section_form_html = (
        f'<form class="governed-form" method="post" action="/write/objects/{quoted_path(object_detail["object"]["object_id"])}/revisions/new?revision_id={quoted_path(revision_id)}&section={quoted_path(section_id)}">'
        f'<input type="hidden" name="section_id" value="{escape(section_id)}" />'
        + _section_fields_html(runtime, blueprint=blueprint, section=section, values=values, errors=errors)
        + '<div class="section-editor-actions">'
        + forms.button(label="Save and continue")
        + (
            forms.link_button(
                label="Check review handoff",
                href=f"/write/objects/{quoted_path(object_detail['object']['object_id'])}/submit?revision_id={quoted_path(revision_id)}",
                variant="secondary",
            )
            if completion["completion_percentage"] > 0
            else ""
        )
        + "</div></form>"
    )
    return {
        "stage_label_html": (
            '<p class="write-stage-label">Step 2 of 3 · Draft the first revision</p>'
            if is_first_revision
            else '<p class="write-stage-label">Step 2 of 3 · Continue the revision</p>'
        ),
        "progress_html": progress_html,
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
        "next_action_html": _next_action_panel_html(
            components,
            detail=object_detail,
            blueprint=blueprint,
            completion=completion,
        ),
        "guidance_html": _guided_fallback_html(
            components,
            object_id=str(object_detail["object"]["object_id"]),
            revision_id=revision_id,
        ),
    }


def _render_fallback_revision_form(
    runtime,
    detail,
    values: dict[str, str],
    errors: dict[str, list[str]],
    findings: list[str] | None = None,
    *,
    form_action: str,
    is_first_revision: bool = False,
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    object_info = detail["object"]
    object_type = object_info["object_type"]

    def multiline_field(name: str, label: str, hint: str) -> str:
        return forms.field(
            field_id=name,
            label=label,
            control_html=forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=4),
            hint=hint,
            errors=errors.get(name),
        )

    sections = [
        forms.field(field_id="title", label="Title", control_html=forms.input(field_id="title", name="title", value=values["title"]), errors=errors.get("title")),
        forms.field(field_id="summary", label="Summary", control_html=forms.textarea(field_id="summary", name="summary", value=values["summary"], rows=3), errors=errors.get("summary")),
        forms.field(field_id="change_summary", label="What changed", control_html=forms.input(field_id="change_summary", name="change_summary", value=values["change_summary"]), hint="Summarize the change in one short line.", errors=errors.get("change_summary")),
        forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=values["owner"]), errors=errors.get("owner")),
        forms.field(field_id="team", label="Team", control_html=forms.select(field_id="team", name="team", value=values["team"], options=runtime.taxonomies["teams"]["allowed_values"]), errors=errors.get("team")),
        forms.field(field_id="status", label="Status", control_html=forms.select(field_id="status", name="status", value=values["status"], options=runtime.taxonomies["statuses"]["allowed_values"]), errors=errors.get("status")),
        forms.field(field_id="review_cadence", label="Review cadence", control_html=forms.select(field_id="review_cadence", name="review_cadence", value=values["review_cadence"], options=runtime.taxonomies["review_cadences"]["allowed_values"]), errors=errors.get("review_cadence")),
        forms.field(field_id="audience", label="Audience", control_html=forms.select(field_id="audience", name="audience", value=values["audience"], options=runtime.taxonomies["audiences"]["allowed_values"]), errors=errors.get("audience")),
        multiline_field("systems", "Related systems", "Add one related system per line."),
        forms.field(
            field_id="tags",
            label="Tags",
            control_html=_multi_value_picker_control_html(
                field_name="tags",
                values=values,
                placeholder="Search controlled tags",
                singular_label="tag",
                manual_entry_label="Manual tag entry",
                static_options=_static_picker_options(runtime.taxonomies["tags"]["allowed_values"], detail="Controlled tag"),
            ),
            hint="Search and select one or more controlled tags.",
            errors=errors.get("tags"),
        ),
        forms.field(
            field_id="related_services",
            label="Related services",
            control_html=_multi_value_picker_control_html(
                field_name="related_services",
                values=values,
                placeholder="Search related services",
                singular_label="service",
                manual_entry_label="Manual service entry",
                static_options=_static_picker_options(runtime.taxonomies["services"]["allowed_values"], detail="Controlled service"),
            ),
            hint="Search and select one or more related services.",
            errors=errors.get("related_services"),
        ),
        forms.field(
            field_id="related_object_ids",
            label="Related guidance",
            control_html=_multi_value_picker_control_html(
                field_name="related_object_ids",
                values=values,
                placeholder="Search related guidance by title, tag, or reference code",
                singular_label="related guidance item",
                manual_entry_label="Manual reference entry",
                search_url="/write/objects/search",
                exclude_object_id=str(object_info["object_id"]),
            ),
            hint="Link related guidance so reviewers can assess impact quickly.",
            errors=errors.get("related_object_ids"),
        ),
    ]
    if object_type == "runbook":
        sections.extend(
            [
                multiline_field("prerequisites", "Prerequisites", "Operator prerequisites, access, or approvals."),
                multiline_field("steps", "Steps", "One operator step per line."),
                multiline_field("verification", "Verification", "How to confirm the expected outcome."),
                multiline_field("rollback", "Rollback", "Recovery actions if the procedure fails."),
                multiline_field("use_when", "Use when", "Narrative trigger condition and intended operator outcome."),
                multiline_field("boundaries_and_escalation", "Boundaries and escalation", "Where the runbook stops and escalation begins."),
                multiline_field("related_knowledge_notes", "Related knowledge notes", "Notes about adjacent procedures or follow-on documentation."),
            ]
        )
    elif object_type == "known_error":
        sections.extend(
            [
                multiline_field("symptoms", "Symptoms", "Observable failure signals."),
                forms.field(field_id="scope", label="Scope", control_html=forms.textarea(field_id="scope", name="scope", value=values["scope"], rows=3), errors=errors.get("scope")),
                forms.field(field_id="cause", label="Cause", control_html=forms.textarea(field_id="cause", name="cause", value=values["cause"], rows=3), errors=errors.get("cause")),
                multiline_field("diagnostic_checks", "Diagnostic checks", "One diagnostic check per line."),
                multiline_field("mitigations", "Mitigations", "One mitigation or containment step per line."),
                forms.field(field_id="permanent_fix_status", label="Permanent fix status", control_html=forms.select(field_id="permanent_fix_status", name="permanent_fix_status", value=values["permanent_fix_status"], options=runtime.taxonomies["permanent_fix_status"]["allowed_values"]), errors=errors.get("permanent_fix_status")),
                multiline_field("detection_notes", "Detection notes", "How operators recognize the issue."),
                multiline_field("escalation_threshold", "Escalation threshold", "When mitigations are exhausted or specialist takeover is required."),
                multiline_field("evidence_notes", "Evidence notes", "Any evidence handling notes relevant to operators or reviewers."),
            ]
        )
    elif object_type == "service_record":
        sections.extend(
            [
                forms.field(field_id="service_name", label="Service name", control_html=forms.input(field_id="service_name", name="service_name", value=values["service_name"]), errors=errors.get("service_name")),
                forms.field(field_id="service_criticality", label="Service criticality", control_html=forms.select(field_id="service_criticality", name="service_criticality", value=values["service_criticality"], options=runtime.taxonomies["service_criticality"]["allowed_values"]), errors=errors.get("service_criticality")),
                multiline_field("dependencies", "Dependencies", "One dependency per line."),
                multiline_field("support_entrypoints", "Support entrypoints", "Primary support channels or escalation doors."),
                multiline_field("common_failure_modes", "Common failure modes", "One common failure mode per line."),
                multiline_field("related_runbooks", "Related runbooks", "Add one related runbook reference per line."),
                multiline_field("related_known_errors", "Related known errors", "Add one related known error reference per line."),
                multiline_field("scope_notes", "Scope", "Narrative service boundary and exclusions."),
                multiline_field("operational_notes", "Operational notes", "Support posture, caveats, and operating model."),
                multiline_field("evidence_notes", "Evidence notes", "Evidence caveats or capture instructions."),
            ]
        )
    elif object_type == "policy":
        sections.extend(
            [
                multiline_field("policy_scope", "Policy scope", "Narrative purpose and boundary of the policy."),
                multiline_field("controls", "Controls", "One control or mandatory requirement per line."),
                multiline_field("exceptions", "Exceptions", "Optional waiver, exception, or boundary notes."),
            ]
        )
    elif object_type == "system_design":
        sections.extend(
            [
                multiline_field("architecture", "Architecture", "High-level design and component intent."),
                multiline_field("dependencies", "Dependencies", "One dependency per line."),
                multiline_field("interfaces", "Interfaces", "One interface or integration per line."),
                multiline_field("common_failure_modes", "Common failure modes", "One operational failure mode per line."),
                multiline_field("support_entrypoints", "Support entrypoints", "Optional support channels or handoff paths."),
                multiline_field("operational_notes", "Operational notes", "Support posture, caveats, and operating model."),
            ]
        )
    else:
        raise ValueError(f"unsupported object type for revision form rendering: {object_type}")

    citation_fields = []
    for index in range(1, 4):
        citation_fields.append(
            f'<section class="citation-entry" data-citation-picker data-citation-index="{index}" '
            f'data-search-url="/write/citations/search" data-exclude-object-id="{escape(object_info["object_id"])}">'
            f"<h4>Citation {index}</h4>"
            '<p class="citation-entry-intro">Link existing guidance when it supports this draft. Add a manual source only when the support comes from outside the library.</p>'
            + forms.field(
                field_id=f"citation_{index}_lookup",
                label=f"Citation {index} source search",
                control_html=_citation_lookup_control_html(index=index, values=values),
                hint="Search existing guidance by title, tag, or reference code.",
                errors=errors.get("citations") if index == 1 else None,
            )
            + forms.field(
                field_id=f"citation_{index}_source_title",
                label="Source title",
                control_html=forms.input(field_id=f"citation_{index}_source_title", name=f"citation_{index}_source_title", value=values.get(f"citation_{index}_source_title", "")),
                hint="Filled from linked guidance, or enter the source name.",
            )
            + forms.field(
                field_id=f"citation_{index}_source_type",
                label="Source type",
                control_html=forms.input(field_id=f"citation_{index}_source_type", name=f"citation_{index}_source_type", value=values.get(f"citation_{index}_source_type", "document")),
                hint="document, url, ticket, or system reference.",
            )
            + forms.field(
                field_id=f"citation_{index}_source_ref",
                label="Source reference",
                control_html=forms.input(field_id=f"citation_{index}_source_ref", name=f"citation_{index}_source_ref", value=values.get(f"citation_{index}_source_ref", "")),
                hint="Use a path, ticket, URL, or other reference.",
            )
            + forms.field(
                field_id=f"citation_{index}_note",
                label="Source note",
                control_html=forms.textarea(field_id=f"citation_{index}_note", name=f"citation_{index}_note", value=values.get(f"citation_{index}_note", ""), rows=2),
                hint="Explain why this source supports the draft and what a reviewer should inspect.",
            )
            + "</section>"
        )

    validation_sections: list[str] = []
    if errors:
        validation_sections.append(_revision_error_summary_html(components, errors))
    if findings:
        validation_sections.append(
            components.validation_findings(title="Pre-submit findings", items=[escape(item) for item in findings], tone="warning")
        )
    validation_html = "".join(validation_sections)

    body_html = (
        f'<form class="governed-form" method="post" action="{escape(form_action)}">'
        + "".join(sections)
        + '<section class="form-section"><h3>Evidence</h3>'
        + "".join(citation_fields)
        + "</section>"
        + forms.button(label="Save draft")
        + "</form>"
    )
    current_revision = detail.get("current_revision") or {}
    guided_return_href = (
        f"/write/objects/{quoted_path(object_info['object_id'])}/revisions/new?revision_id={quoted_path(str(current_revision.get('revision_id') or ''))}#revision-form"
    )
<<<<<<< Updated upstream
    guidance_html = _support_details_html(
        title="Return to guided drafting",
        summary="Use the guided flow when you only need one active section at a time.",
        body_html=(
            "<p>This editor keeps the full draft in one place. Switch back to guided drafting when you want the next required section surfaced automatically.</p>"
            if is_first_revision
            else "<p>This editor still writes the same draft, but guided section editing remains the primary route for day-to-day authoring.</p>"
        )
        + f'<p>{link("Return to guided flow", guided_return_href, css_class="button button-secondary")}</p>'
        + "<p>Evidence note: governed Papyrus citations are lightweight internal references. External or manual evidence stays weak until later follow-up records capture time, integrity metadata, and any needed snapshot.</p>",
=======
<<<<<<< HEAD
    guidance_html = _support_details_html(
        title="Return to guided drafting",
        summary="Use the guided flow when you only need one active section at a time.",
        body_html=(
            "<p>This editor keeps the full draft in one place. Switch back to guided drafting when you want the next required section surfaced automatically.</p>"
            if is_first_revision
            else "<p>This editor still writes the same draft, but guided section editing remains the primary route for day-to-day authoring.</p>"
        )
        + f'<p>{link("Return to guided flow", guided_return_href, css_class="button button-secondary")}</p>'
        + "<p>Evidence note: governed Papyrus citations are lightweight internal references. External or manual evidence stays weak until later follow-up records capture time, integrity metadata, and any needed snapshot.</p>",
=======
    guidance_html = components.section_card(
        title="Bulk edit",
        eyebrow="Fallback",
        tone="context",
        body_html=(
            "<p>Use this wider editor only when guided drafting is not enough for the change you need to make.</p>"
            if is_first_revision
            else "<p>This editor updates the same draft, but guided section editing remains the primary route for day-to-day work.</p>"
        )
        + f'<p>{link("Return to guided editing", guided_return_href, css_class="button button-secondary")}</p>'
        + "<p>Linked guidance helps with traceability. External or manual sources still need evidence follow-up before they count as strong support.</p>",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
    )
    return {
        "validation_html": validation_html,
        "progress_html": _revision_progress_html(components, object_type=object_type, values=values, errors=errors, findings=findings),
<<<<<<< Updated upstream
        "form_html": components.section_card(title="Advanced draft editor", eyebrow="Write", body_html=body_html),
=======
<<<<<<< HEAD
        "form_html": components.section_card(title="Advanced draft editor", eyebrow="Write", body_html=body_html),
=======
        "form_html": components.section_card(title="Bulk edit", eyebrow="Fallback", body_html=body_html, tone="context"),
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
        "guidance_html": guidance_html + _evidence_guidance_section(components, title="How evidence gets strengthened"),
    }


def _render_submit_page(
    runtime,
    detail,
    object_detail,
    completion: dict[str, object],
    findings: list[str],
    form_errors: dict[str, list[str]],
    values: dict[str, str],
) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    revision = detail["revision"]
    evidence_posture = completion.get("evidence_posture") or summarize_evidence_posture(detail.get("citations", []))
    submit_action = action_descriptor(object_detail.get("ui_projection"), "submit_for_review")
    draft_projection = workflow_projection_payload(
        build_draft_readiness_projection(
            blueprint=get_blueprint(str(revision["blueprint_id"] or detail["object"]["object_type"])),
            completion=completion,
            submit_action=submit_action,
        )
    )
    form_html = components.section_card(
        title="Send to review",
        eyebrow="Write",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(
                field_id="notes",
                label="Submission notes",
                control_html=forms.textarea(field_id="notes", name="notes", value=values.get("notes", ""), rows=3),
                hint="Optional notes for reviewers and assignment triage.",
                errors=form_errors.get("notes"),
            )
<<<<<<< Updated upstream
            + forms.button(label="Send to review")
            + "</form>"
        ),
    )
    summary_html = components.section_card(
        title="Review handoff summary",
        eyebrow="Write",
        body_html=(
            f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_review_state'])}</p>"
            f"<p><strong>Change summary:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
            f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
            f"<p><strong>Evidence posture:</strong> {escape(evidence_posture['summary'])}</p>"
            f"<p><strong>Evidence note:</strong> {escape(_submit_evidence_posture_detail(evidence_posture))}</p>"
            f"<p><strong>Canonical target:</strong> {escape(detail['object']['canonical_path'])}</p>"
        ),
=======
<<<<<<< HEAD
            + forms.button(label="Send to review")
            + "</form>"
        ),
    )
    summary_html = components.section_card(
        title="Review handoff summary",
        eyebrow="Write",
        body_html=(
            f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_review_state'])}</p>"
            f"<p><strong>Change summary:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
            f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
            f"<p><strong>Evidence posture:</strong> {escape(evidence_posture['summary'])}</p>"
            f"<p><strong>Evidence note:</strong> {escape(_submit_evidence_posture_detail(evidence_posture))}</p>"
            f"<p><strong>Canonical target:</strong> {escape(detail['object']['canonical_path'])}</p>"
        ),
=======
            + forms.button(label="Send for review")
            + "</form>"
        ),
    )
    summary_html = join_html(
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
            components.section_card(
                title="Submission summary",
                eyebrow="Write",
                body_html=(
                    f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_review_state'])}</p>"
                    f"<p><strong>What changed:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
                    f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
                    f"<p><strong>Evidence posture:</strong> {escape(evidence_posture['summary'])}</p>"
                    f"<p><strong>Evidence note:</strong> {escape(_submit_evidence_posture_detail(evidence_posture))}</p>"
                    f"<p><strong>Publishing location:</strong> {escape(detail['object']['canonical_path'])}</p>"
                ),
            ),
        ]
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
    )
    findings_html = components.validation_findings(title="Pre-submit validation", items=[escape(item) for item in findings] or ["No blocking findings detected."], tone="warning" if findings else "approved")
    progress_rows = [
        f"{row['label']}: {row['value']}"
        for row in draft_projection.get("rows", [])
        if row.get("label") and row.get("value")
    ]
    progress_html = components.section_card(
        title="Step 3 of 3",
        eyebrow="Progress",
        tone=str(draft_projection.get("tone") or "default"),
        body_html=(
            f"<p>{escape(draft_projection.get('summary') or 'Submission status available.')}</p>"
            + (render_list([escape(item) for item in progress_rows], css_class="stack-list") if progress_rows else "")
            + f"<p><strong>Warnings to review:</strong> {escape(len(findings))}</p>"
        ),
        footer_html='<p class="section-footer">Send the revision only after the remaining warnings are understood.</p>',
    )
    guidance_html = ""
    if any("Evidence posture:" in item for item in findings):
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
        guidance_html = _support_details_html(
            title="How to strengthen weak evidence",
            summary="Use the manage flow when reviewer confidence depends on stronger capture metadata.",
            body_html=_evidence_guidance_section(
                components,
                title="How evidence gets strengthened",
                include_action=True,
                object_id=str(detail["object"]["object_id"]),
            ),
<<<<<<< Updated upstream
=======
=======
        guidance_html = _evidence_guidance_section(
            components,
            title="Strengthen evidence before approval",
            include_action=True,
            object_id=str(detail["object"]["object_id"]),
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
        )
    return {
        "summary_html": summary_html,
        "progress_html": progress_html,
        "findings_html": findings_html,
        "guidance_html": guidance_html,
        "form_html": form_html,
    }


def register(router, runtime) -> None:
    def create_object_page(request: Request):
        values = default_object_values()
        errors: dict[str, list[str]] = {}
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
        if request.method == "POST":
            values = {key: request.form_value(key) for key in values}
            result = validate_object_form(values, taxonomies=runtime.taxonomies)
            if result.is_valid:
                created = create_object_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    actor=actor_for_request(request),
                    **result.cleaned_data,
                )
                return redirect_response(
                    f"/write/objects/{quoted_path(created.object_id)}/revisions/new?notice={quote_plus('Draft setup saved. Step 2 of 3: complete the first draft below.')}#revision-form"
                )
            errors = result.errors
            if errors:
                page_flash_html = FormPresenter(runtime.template_renderer).flash(
                    title="Attention",
                    body="Draft setup not saved. Fix the blocking fields below.",
                    tone="warning",
                )
        page_context = _render_object_form(runtime, values, errors, form_action=request.path)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_object_new.html",
                page_title="Choose blueprint",
                headline="Start a guided draft",
                kicker="Write",
<<<<<<< Updated upstream
                intro="Define the shell once, then move into guided section-by-section drafting.",
=======
<<<<<<< HEAD
                intro="Define the shell once, then move into guided section-by-section drafting.",
=======
                intro="Choose the content type, name the guidance, and confirm who owns it.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_for_request(request),
                current_path=request.path,
                action_bar_html="",
                aside_html="",
                shell_variant="focus",
                header_mode="compact",
                page_context=page_context,
            )
        )

    def create_revision_page(request: Request):
        object_id = request.route_value("object_id")
        actor_id = actor_for_request(request)
        draft_context = _load_draft_context(
            runtime,
            object_id=object_id,
            actor_id=actor_id,
            requested_revision_id=request.query_value("revision_id") or None,
        )
        initial_detail = draft_context["initial_detail"]
        detail = draft_context["detail"]
        draft_status = draft_context["draft_status"]
        revision_id = str(draft_context["revision_id"])
        section_id = request.query_value("section") or str(draft_status["completion"]["next_section_id"])
        blueprint = draft_status["blueprint"]
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""

        if request.method == "POST" and request.form_value("section_id"):
            section_id = request.form_value("section_id").strip() or section_id
            section = blueprint.section(section_id)
            candidate_values = _parse_section_submission(section, request)
            form_errors = _section_errors(
                blueprint=blueprint,
                section_id=section_id,
                section_content=draft_status["section_content"],
                candidate_values=candidate_values,
                taxonomies=runtime.taxonomies,
            )
            if form_errors:
                page_flash_html = FormPresenter(runtime.template_renderer).flash(
                    title="Attention",
                    body="Section not saved. Fix the inline blockers below.",
                    tone="warning",
                )
                page_context = _render_guided_revision_page(
                    runtime,
                    object_detail=detail,
                    draft_status=draft_status,
                    revision_id=revision_id,
                    section_id=section_id,
                    is_first_revision=initial_detail["current_revision"] is None,
                    form_values=_section_form_values(section, candidate_values),
                    form_errors=form_errors,
                    page_flash_html=page_flash_html,
                )
                return html_response(
                    runtime.page_renderer.render_page(
                        page_template="pages/write_revision_edit.html",
                        page_title=f"Draft {section.display_name}",
                        headline=f"Continue {blueprint.display_name}",
                        kicker="Write",
<<<<<<< Updated upstream
                        intro="Finish the active section, save it, and move to the next required gap.",
=======
<<<<<<< HEAD
                        intro="Finish the active section, save it, and move to the next required gap.",
=======
                        intro="Complete this draft one section at a time.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                        active_nav="write",
                        flash_html=page_flash_html,
                        actor_id=actor_id,
                        current_path=request.path,
                        aside_html="",
                        shell_variant="focus",
                        header_mode="compact",
                        page_context=page_context,
                    )
                )
            updated = update_section(
                object_id=object_id,
                revision_id=revision_id,
                section_id=section_id,
                values=candidate_values,
                actor=actor_id,
                database_path=runtime.database_path,
                source_root=runtime.source_root,
            )
            next_section_id = str(updated["completion"]["next_section_id"])
            redirect_target = (
                f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision_id)}"
                if updated["completion"]["draft_progress_state"] == "ready_for_review" and next_section_id == section_id
                else f"/write/objects/{quoted_path(object_id)}/revisions/new?revision_id={quoted_path(revision_id)}&section={quoted_path(next_section_id)}"
            )
            notice = f"Section saved. Next: {blueprint.section(next_section_id).display_name}."
            return redirect_response(f"{redirect_target}&notice={quote_plus(notice)}")

        if request.method == "POST":
            return redirect_response(
<<<<<<< Updated upstream
                f"{_fallback_revision_href(object_id=object_id, revision_id=revision_id)}&notice={quote_plus('Advanced draft editing moved to its own route. Continue there if the guided step is not enough.')}"
=======
<<<<<<< HEAD
                f"{_fallback_revision_href(object_id=object_id, revision_id=revision_id)}&notice={quote_plus('Advanced draft editing moved to its own route. Continue there if the guided step is not enough.')}"
=======
                f"{_fallback_revision_href(object_id=object_id, revision_id=revision_id)}&notice={quote_plus('Bulk edit is on its own page. Continue there if you need the wider editor.')}"
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
            )

        page_context = _render_guided_revision_page(
            runtime,
            object_detail=detail,
            draft_status=draft_status,
            revision_id=revision_id,
            section_id=section_id,
            is_first_revision=initial_detail["current_revision"] is None,
            page_flash_html=page_flash_html,
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_revision_edit.html",
                page_title=f"Draft {blueprint.display_name}",
                headline=f"Continue {blueprint.display_name}",
                kicker="Write",
<<<<<<< Updated upstream
                intro="Finish the active section, save it, and move to the next required gap.",
=======
<<<<<<< HEAD
                intro="Finish the active section, save it, and move to the next required gap.",
=======
                intro="Complete this draft one section at a time.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_id,
                current_path=request.path,
                aside_html="",
                shell_variant="focus",
                header_mode="compact",
                page_context=page_context,
            )
        )

    def fallback_revision_page(request: Request):
        object_id = request.route_value("object_id")
        actor_id = actor_for_request(request)
        draft_context = _load_draft_context(
            runtime,
            object_id=object_id,
            actor_id=actor_id,
            requested_revision_id=request.query_value("revision_id") or None,
        )
        detail = draft_context["detail"]
        revision_id = str(draft_context["revision_id"])
        is_first_revision = bool(draft_context["is_first_revision"])
        page_flash_html = flash_html_for_request(runtime, request) if request.method != "POST" else ""
        current_revision = detail.get("current_revision") or {}

        if request.method == "POST":
            values = build_revision_defaults(detail)
            values.update({key: request.form_value(key) for key in values})
            result = validate_revision_form(
                values=values,
                object_detail=detail,
                taxonomies=runtime.taxonomies,
                actor=actor_id,
            )
            findings = result.cleaned_data["validation_findings"]
            if result.is_valid:
                revision = create_revision_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    normalized_payload=result.cleaned_data["normalized_payload"],
                    body_markdown=result.cleaned_data["body_markdown"],
                    actor=actor_id,
                    legacy_metadata=detail.get("metadata") or {},
                    change_summary=result.cleaned_data["change_summary"],
                )
                return redirect_response(
<<<<<<< Updated upstream
                    f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision.revision_id)}&notice={quote_plus('Advanced draft saved')}"
=======
<<<<<<< HEAD
                    f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision.revision_id)}&notice={quote_plus('Advanced draft saved')}"
=======
                    f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision.revision_id)}&notice={quote_plus('Bulk edit saved')}"
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                )
            page_flash_html = FormPresenter(runtime.template_renderer).flash(
                title="Attention",
                body="Draft not saved. Fix the blocking fields below.",
                tone="warning",
            )
            page_context = _render_fallback_revision_form(
                runtime,
                detail,
                values,
                result.errors,
                findings,
                form_action=_fallback_revision_href(object_id=object_id, revision_id=revision_id),
                is_first_revision=is_first_revision,
            )
            return html_response(
                runtime.page_renderer.render_page(
                    page_template="pages/write_revision_new.html",
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
                    page_title="Advanced draft editor",
                    headline="Advanced draft editor",
                    kicker="Write",
                    intro="Use this editor only when the guided step is not enough for the change you need to make.",
<<<<<<< Updated upstream
=======
=======
                    page_title="Bulk edit",
                    headline="Bulk Edit",
                    kicker="Write",
                    intro="Use bulk edit only when guided drafting is not enough.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                    active_nav="write",
                    flash_html=page_flash_html,
                    actor_id=actor_id,
                    current_path=request.path,
                    aside_html="",
                    scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
                    shell_variant="focus",
                    header_mode="compact",
                    page_context=page_context,
                )
            )

        values = build_revision_defaults(detail)
        findings = build_submission_findings(
            object_type=detail["object"]["object_type"],
            payload=current_revision.get("metadata") or detail.get("metadata") or {},
        )
        page_context = _render_fallback_revision_form(
            runtime,
            detail,
            values,
            {},
            findings,
            form_action=_fallback_revision_href(object_id=object_id, revision_id=revision_id),
            is_first_revision=is_first_revision,
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_revision_new.html",
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
>>>>>>> Stashed changes
                page_title="Advanced draft editor",
                headline="Advanced draft editor",
                kicker="Write",
                intro="Use this editor only when the guided step is not enough for the change you need to make.",
<<<<<<< Updated upstream
=======
=======
                page_title="Bulk edit",
                headline="Bulk Edit",
                kicker="Write",
                intro="Use bulk edit only when guided drafting is not enough.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_id,
                current_path=request.path,
                aside_html="",
                scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
                shell_variant="focus",
                header_mode="compact",
                page_context=page_context,
            )
        )

    def citation_search_endpoint(request: Request):
        query = request.query_value("query").strip()
        exclude_object_id = request.query_value("exclude_object_id").strip()
        if len(query) < 2:
            return json_response({"items": []})
        candidates = search_knowledge_objects(query, limit=12, database_path=runtime.database_path)
        items: list[dict[str, str]] = []
        for candidate in candidates:
            if exclude_object_id and str(candidate["object_id"]) == exclude_object_id:
                continue
            if candidate.get("current_revision_id") is None:
                continue
            detail = knowledge_object_detail(str(candidate["object_id"]), database_path=runtime.database_path)
            reference_projection = detail.get("reference_projection") or {}
            if not bool(reference_projection.get("eligible")):
                continue
            state = projection_state(candidate.get("ui_projection"))
            use_guidance = projection_use_guidance(candidate.get("ui_projection"))
            items.append(
                {
                    "object_id": str(candidate["object_id"]),
                    "title": str(candidate["title"]),
                    "path": str(candidate["path"]),
                    "object_type": str(candidate["object_type"]),
                    "summary": str(reference_projection.get("summary") or use_guidance.get("summary") or ""),
                    "detail": (
                        f"{state.get('approval_state') or candidate.get('approval_state') or 'unknown'} approval | "
                        f"{state.get('trust_state') or candidate.get('trust_state') or 'unknown'} trust | "
                        f"{reference_projection.get('detail') or use_guidance.get('detail') or 'Reference available.'}"
                    ),
                }
            )
        return json_response({"items": items})

    def related_object_search_endpoint(request: Request):
        query = request.query_value("query").strip()
        exclude_object_id = request.query_value("exclude_object_id").strip()
        if len(query) < 2:
            return json_response({"items": []})
        candidates = search_knowledge_objects(query, limit=12, database_path=runtime.database_path)
        items: list[dict[str, str]] = []
        for candidate in candidates:
            if exclude_object_id and str(candidate["object_id"]) == exclude_object_id:
                continue
            state = projection_state(candidate.get("ui_projection"))
            use_guidance = projection_use_guidance(candidate.get("ui_projection"))
            items.append(
                {
                    "value": str(candidate["object_id"]),
                    "label": str(candidate["title"]),
                    "detail": (
                        f"Ref {candidate['object_id']} | {candidate['path']} | "
                        f"{use_guidance.get('summary') or 'Guidance summary unavailable'} | "
                        f"{state.get('approval_state') or 'unknown'} approval | "
                        f"{state.get('trust_state') or 'unknown'} trust"
                    ),
                }
            )
        return json_response({"items": items})

    def submit_revision_page(request: Request):
        object_id = request.route_value("object_id")
        object_detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        revision_id = request.query_value("revision_id") or str((object_detail["current_revision"] or {})["revision_id"])
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        values = {"notes": request.form_value("notes")}
        form_errors: dict[str, list[str]] = {}
        draft_status = validate_draft_progress(
            object_id=object_id,
            revision_id=revision_id,
            database_path=runtime.database_path,
            source_root=runtime.source_root,
        )
        findings = [
            *draft_status["completion"]["blockers"],
            *draft_status["completion"]["warnings"],
            *build_submission_findings(
            object_type=detail["object"]["object_type"],
            payload=detail["revision"]["metadata"],
            ),
        ]
        if request.method == "POST":
            result = validate_submit_form(values)
            if result.is_valid and not draft_status["completion"]["blockers"]:
                submit_for_review_command(
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                    object_id=object_id,
                    revision_id=revision_id,
                    actor=actor_for_request(request),
                    notes=result.cleaned_data["notes"],
                )
                return redirect_response(
                    f"/manage/reviews/{quoted_path(object_id)}/{quoted_path(revision_id)}/assign?notice={quote_plus('Revision submitted for review')}"
                )
            form_errors = result.errors
            if draft_status["completion"]["blockers"]:
                form_errors.setdefault("notes", []).append("Clear the draft blockers before submitting for review.")
        page_context = _render_submit_page(
            runtime,
            detail,
            object_detail,
            draft_status["completion"],
            findings,
            form_errors,
            values,
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/review_submit.html",
                page_title="Submit for review",
                headline="Send to review",
                kicker="Write",
<<<<<<< Updated upstream
                intro="Review the blockers, confirm the evidence posture, and hand the revision to a reviewer.",
=======
<<<<<<< HEAD
                intro="Review the blockers, confirm the evidence posture, and hand the revision to a reviewer.",
=======
                intro="Check readiness, then send the draft for review.",
>>>>>>> fa7e1337802c3001927a331483a6133ab2648dde
>>>>>>> Stashed changes
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                aside_html="",
                shell_variant="focus",
                header_mode="compact",
                page_context=page_context,
            )
        )

    router.add(["GET", "POST"], "/write/objects/new", create_object_page)
    router.add(["GET"], "/write/citations/search", citation_search_endpoint)
    router.add(["GET"], "/write/objects/search", related_object_search_endpoint)
    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/new", create_revision_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/fallback", fallback_revision_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/submit", submit_revision_page)
