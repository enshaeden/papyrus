from __future__ import annotations

import json

from papyrus.application.ui_projection import build_draft_readiness_projection, workflow_projection_payload
from papyrus.domain.evidence import summarize_evidence_posture
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import action_descriptor, render_action_contract_panel, render_projection_status_panel
from papyrus.interfaces.web.view_helpers import escape, join_html, link, parse_multiline, quoted_path, render_list


def support_details_html(*, title: str, summary: str, body_html: str, open_by_default: bool = False) -> str:
    return (
        f'<details class="support-disclosure"{" open" if open_by_default else ""}>'
        f'<summary><span class="support-disclosure-title">{escape(title)}</span>'
        f'<span class="support-disclosure-summary">{escape(summary)}</span></summary>'
        f'<div class="support-disclosure-body">{body_html}</div>'
        "</details>"
    )


def completion_ratio(values: dict[str, str], fields: list[str]) -> tuple[int, int]:
    total = len(fields)
    completed = sum(1 for field in fields if values.get(field, "").strip())
    return completed, total


def render_object_progress_html(components: ComponentPresenter, *, values: dict[str, str], errors: dict[str, list[str]]) -> str:
    purpose_completed, purpose_total = completion_ratio(values, ["object_type", "title", "summary"])
    stewardship_completed, stewardship_total = completion_ratio(
        values,
        ["owner", "team", "review_cadence", "object_lifecycle_state"],
    )
    source_completed, source_total = completion_ratio(values, ["object_id", "canonical_path"])
    blockers = sum(len(messages) for messages in errors.values())
    return components.context_panel(
        title="Step 1 of 3",
        eyebrow="Progress",
        tone="warning" if blockers else "brand",
        body_html=(
            "<p><strong>Current task:</strong> define the object shell.</p>"
            + render_list(
                [
                    escape(f"Purpose and type: {purpose_completed}/{purpose_total} complete"),
                    escape(f"Ownership and cadence: {stewardship_completed}/{stewardship_total} complete"),
                    escape(f"Reference code and path: {source_completed}/{source_total} complete"),
                ],
                css_class="stack-list",
            )
            + f"<p><strong>Blocking fields:</strong> {escape(blockers)}</p>"
        ),
        footer_html='<p class="section-footer">Next: Papyrus opens the first required section.</p>',
        variant="object-progress",
        surface="write-object",
    )


def render_progress_bar_html(runtime, *, blueprint, completion: dict[str, object], current_section_id: str) -> str:
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


def render_next_action_panel_html(components: ComponentPresenter, *, detail, blueprint, completion: dict[str, object]) -> str:
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
    warning_panels = []
    if reasons:
        warning_panels.append(
            components.context_panel(
                title="Still blocking",
                eyebrow="Review readiness",
                body_html=components.list_body(
                    items=[escape(item) for item in reasons],
                    empty_label="No blocking items recorded.",
                    css_class="validation-findings",
                ),
                tone="warning",
                variant="blocking-findings",
                surface="write-revision",
            )
        )
    if warnings:
        warning_panels.append(
            components.context_panel(
                title="Review before handoff",
                eyebrow="Review readiness",
                body_html=components.list_body(
                    items=[escape(item) for item in warnings],
                    empty_label="No warnings recorded.",
                    css_class="validation-findings",
                ),
                tone="warning",
                variant="warning-findings",
                surface="write-revision",
            )
        )
    return components.context_panel(
        title="Ready for handoff?",
        eyebrow="Progress",
        tone=str(draft_projection.get("tone") or "default"),
        body_html=(
            f"<p>{escape(draft_projection.get('summary') or 'Draft status available.')}</p>"
            + (render_list([escape(item) for item in progress_rows], css_class="stack-list") if progress_rows else "")
            + join_html(warning_panels)
        ),
        footer_html='<p class="section-footer">Keep saving the active section until the draft is ready for review.</p>',
        variant="handoff-readiness",
        surface="write-revision",
    )


def citation_search_status(title: str, reference: str) -> str:
    if title and reference:
        return f"Selected source: {title} -> {reference}"
    return "Search guidance by title, tag, or reference code. Selecting a result fills the fields below."


def evidence_posture_from_form_values(values: dict[str, str]) -> dict[str, object]:
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


def submit_evidence_posture_detail(evidence_posture: dict[str, object]) -> str:
    if int(evidence_posture.get("weak_external_evidence_count") or 0):
        return "External or manual sources still need evidence follow-up before they count as strong support."
    if int(evidence_posture.get("captured_external_evidence_count") or 0) and int(
        evidence_posture.get("internal_reference_count") or 0
    ):
        return "Linked guidance provides traceability. Captured external evidence is the strongest support recorded so far."
    if int(evidence_posture.get("captured_external_evidence_count") or 0):
        return "Captured external or manual evidence has stronger support metadata recorded."
    if int(evidence_posture.get("internal_reference_count") or 0):
        return "Linked guidance provides traceability and review context."
    return "No evidence references are recorded yet."


def evidence_guidance_body_html(*, include_action: bool = False, object_id: str | None = None) -> str:
    action_html = ""
    if include_action and object_id:
        action_html = (
            '<p><strong>Next step:</strong> request evidence follow-up for any source that still needs stronger verification.</p>'
            + f'<p>{link("Request evidence revalidation", f"/manage/objects/{quoted_path(object_id)}/evidence/revalidate", css_class="button button-secondary", attrs={"data-component": "action-link", "data-action-id": "request_evidence_revalidation"})}</p>'
        )
    return (
        "<p>Link existing guidance or record a source title, reference, and note.</p>"
        "<p>If a source still needs stronger verification, complete evidence follow-up after the revision exists so capture time, integrity details, and any required snapshot are recorded.</p>"
        + action_html
    )


def render_citation_lookup_control_html(*, index: int, values: dict[str, str]) -> str:
    lookup_value = values.get(f"citation_{index}_lookup", "")
    return (
        '<div class="citation-picker">'
        f'<input id="citation_{index}_lookup" name="citation_{index}_lookup" type="text" '
        'class="text-input citation-picker-input" '
        f'value="{escape(lookup_value)}" placeholder="Search by title, tag, or reference code" '
        'autocomplete="off" spellcheck="false" />'
        '<div class="citation-picker-results" hidden></div>'
        f'<p class="field-hint citation-picker-status">{escape(citation_search_status(values.get(f"citation_{index}_source_title", ""), values.get(f"citation_{index}_source_ref", "")))}</p>'
        "</div>"
    )


def multi_value_picker_status(selected_values: list[str], *, singular_label: str) -> str:
    if not selected_values:
        return f"No {singular_label} selected yet."
    count = len(selected_values)
    return f"{count} {singular_label}{'' if count == 1 else 's'} selected."


def static_picker_options(values: list[str], *, detail: str) -> list[dict[str, str]]:
    return [{"value": item, "label": item, "detail": detail} for item in values]


def render_multi_value_picker_control_html(
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
        f'<p class="field-hint multi-value-picker-status">{escape(multi_value_picker_status(selected_values, singular_label=singular_label))}</p>'
        "</div>"
    )


def revision_error_label(field_name: str) -> str:
    explicit_labels = {
        "object_id": "Reference code",
        "canonical_path": "Publishing location",
        "object_lifecycle_state": "Lifecycle state",
        "change_summary": "What changed",
        "related_object_ids": "Related guidance",
    }
    if field_name in explicit_labels:
        return explicit_labels[field_name]
    label = field_name.replace("_", " ")
    label = label.replace(" id", " ID")
    label = label.replace(" ids", " IDs")
    return label[:1].upper() + label[1:] if label else field_name


def render_revision_error_summary_html(components: ComponentPresenter, errors: dict[str, list[str]]) -> str:
    items: list[str] = []
    for field_name, messages in errors.items():
        label = escape(revision_error_label(field_name))
        for message in messages:
            items.append(f"{label}: {escape(message)}")
    if not items:
        return ""
    return components.surface_panel(
        title="Blocking validation",
        eyebrow="Validation",
        body_html=components.list_body(items=items, empty_label="", css_class="validation-findings"),
        tone="context",
        variant="blocking-validation",
        surface="write-revision",
    )


def _widget_config(field) -> dict[str, object]:
    widget = field.get("widget")
    return widget if isinstance(widget, dict) else {}


def _taxonomy_picker_control(runtime, *, field, values: dict[str, str]) -> str:
    widget = _widget_config(field)
    taxonomy_name = str(widget.get("taxonomy") or field.get("taxonomy") or "")
    options = runtime.taxonomies.get(taxonomy_name, {}).get("allowed_values", [])
    return render_multi_value_picker_control_html(
        field_name=str(field["name"]),
        values=values,
        placeholder=str(widget.get("placeholder") or f"Search {str(field['label']).lower()}"),
        singular_label=str(widget.get("singular_label") or str(field["label"]).rstrip("s").lower()),
        manual_entry_label=str(widget.get("manual_entry_label") or f"Manual {str(field['label']).lower()} entry"),
        static_options=static_picker_options(list(options), detail="Controlled value"),
    )


def _remote_object_picker_control(runtime, *, field, values: dict[str, str], object_id: str) -> str:
    widget = _widget_config(field)
    return render_multi_value_picker_control_html(
        field_name=str(field["name"]),
        values=values,
        placeholder=str(widget.get("placeholder") or f"Search {str(field['label']).lower()}"),
        singular_label=str(widget.get("singular_label") or "related guidance item"),
        manual_entry_label=str(widget.get("manual_entry_label") or "Manual reference entry"),
        search_url=str(widget.get("search_url") or "/write/objects/search"),
        exclude_object_id=object_id,
    )


def render_section_fields_html(runtime, *, section, values: dict[str, str], errors: dict[str, list[str]], object_id: str) -> str:
    forms = FormPresenter(runtime.template_renderer)
    widget = _widget_config(section.fields[0]) if section.fields else {}
    if str(section.section_type.value) == "references":
        slots = int(widget.get("slots") or 3)
        search_url = str(widget.get("search_url") or "/write/citations/search")
        blocks: list[str] = []
        for index in range(1, slots + 1):
            blocks.append(
                f'<section class="citation-entry" data-citation-picker data-citation-index="{index}" '
                f'data-search-url="{escape(search_url)}" data-exclude-object-id="{escape(object_id)}">'
                f"<h4>Citation {index}</h4>"
                + forms.field(
                    field_id=f"citation_{index}_lookup",
                    label=f"Citation {index} source search",
                    control_html=render_citation_lookup_control_html(index=index, values=values),
                    hint="Search existing guidance by title, tag, or reference code.",
                    errors=errors.get("citations") if index == 1 else None,
                )
                + forms.field(
                    field_id=f"citation_{index}_source_title",
                    label="Source title",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_title",
                        name=f"citation_{index}_source_title",
                        value=values.get(f"citation_{index}_source_title", ""),
                    ),
                    hint="Filled from linked guidance, or enter the source name.",
                )
                + forms.field(
                    field_id=f"citation_{index}_source_type",
                    label="Source type",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_type",
                        name=f"citation_{index}_source_type",
                        value=values.get(f"citation_{index}_source_type", "document"),
                    ),
                    hint="document, url, ticket, or system reference.",
                )
                + forms.field(
                    field_id=f"citation_{index}_source_ref",
                    label="Source reference",
                    control_html=forms.input(
                        field_id=f"citation_{index}_source_ref",
                        name=f"citation_{index}_source_ref",
                        value=values.get(f"citation_{index}_source_ref", ""),
                    ),
                    hint="Use a path, ticket, URL, or other reference.",
                )
                + forms.field(
                    field_id=f"citation_{index}_note",
                    label="Source note",
                    control_html=forms.textarea(
                        field_id=f"citation_{index}_note",
                        name=f"citation_{index}_note",
                        value=values.get(f"citation_{index}_note", ""),
                        rows=2,
                    ),
                    hint="Explain why this source supports the draft and what a reviewer should inspect.",
                )
                + "</section>"
            )
        return "".join(blocks)

    blocks: list[str] = []
    for field in section.fields:
        name = str(field["name"])
        label = str(field["label"])
        kind = str(field.get("kind") or "text")
        hint = str(field.get("hint") or "")
        field_widget = _widget_config(field)
        widget_type = str(field_widget.get("type") or "")
        if widget_type == "taxonomy_multi_select":
            control = _taxonomy_picker_control(runtime, field=field, values=values)
        elif widget_type == "object_search_multi_select":
            control = _remote_object_picker_control(runtime, field=field, values=values, object_id=object_id)
        elif kind == "select":
            control = forms.select(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                options=list(runtime.taxonomies[str(field.get("taxonomy"))]["allowed_values"]),
            )
        elif kind == "list":
            control = forms.textarea(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                rows=5,
                placeholder=str(field.get("placeholder") or ""),
            )
        elif kind == "long_text":
            control = forms.textarea(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                rows=6,
                placeholder=str(field.get("placeholder") or ""),
            )
        else:
            control = forms.input(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                placeholder=str(field.get("placeholder") or ""),
            )
        blocks.append(forms.field(field_id=name, label=label, control_html=control, hint=hint, errors=errors.get(name)))
    return "".join(blocks)
