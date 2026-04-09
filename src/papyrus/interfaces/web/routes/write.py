from __future__ import annotations

import json
from urllib.parse import quote_plus

from papyrus.application.authoring_flow import compute_completion_state, create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.blueprint_registry import get_blueprint, list_blueprints
from papyrus.application.commands import create_object_command, create_revision_command, submit_for_review_command
from papyrus.application.queries import knowledge_object_detail, review_detail, search_knowledge_objects
from papyrus.domain.evidence import summarize_evidence_posture
from papyrus.interfaces.web.forms.object_forms import default_object_values, validate_object_form
from papyrus.interfaces.web.forms.revision_forms import build_revision_defaults, build_submission_findings, validate_revision_form
from papyrus.interfaces.web.forms.review_forms import validate_submit_form
from papyrus.interfaces.web.http import Request, html_response, json_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, join_html, link, parse_multiline, quoted_path


def _render_object_form(runtime, values: dict[str, str], errors: dict[str, list[str]], *, form_action: str) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    controls = [
        forms.field(
            field_id="object_type",
            label="Blueprint",
            control_html=forms.select(
                field_id="object_type",
                name="object_type",
                value=values["object_type"],
                options=[blueprint.blueprint_id for blueprint in list_blueprints()],
            ),
            hint="Choose the structured blueprint before drafting the first revision.",
            errors=errors.get("object_type"),
        ),
        forms.field(
            field_id="object_id",
            label="Object ID",
            control_html=forms.input(field_id="object_id", name="object_id", value=values["object_id"], placeholder="kb-remote-access-example"),
            hint="Stable control-plane identifier in kb-slug format.",
            errors=errors.get("object_id"),
        ),
        forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(field_id="title", name="title", value=values["title"], placeholder="Remote Access VPN recovery"),
            hint="Operator-facing title used in read surfaces and audit history.",
            errors=errors.get("title"),
        ),
        forms.field(
            field_id="summary",
            label="Summary",
            control_html=forms.textarea(field_id="summary", name="summary", value=values["summary"], rows=3, placeholder="Concise operational summary."),
            hint="Short operational summary shown above the fold.",
            errors=errors.get("summary"),
        ),
        forms.field(
            field_id="owner",
            label="Owner",
            control_html=forms.input(field_id="owner", name="owner", value=values["owner"], placeholder="team_or_person"),
            hint="Visible ownership is required for trust posture.",
            errors=errors.get("owner"),
        ),
        forms.field(
            field_id="team",
            label="Team",
            control_html=forms.select(field_id="team", name="team", value=values["team"], options=runtime.taxonomies["teams"]["allowed_values"]),
            hint="Primary accountable team.",
            errors=errors.get("team"),
        ),
        forms.field(
            field_id="canonical_path",
            label="Canonical path",
            control_html=forms.input(field_id="canonical_path", name="canonical_path", value=values["canonical_path"], placeholder="knowledge/runbooks/remote-access-vpn-recovery.md"),
            hint="Guidance only at this stage, but it must remain under knowledge/ for durable source placement.",
            errors=errors.get("canonical_path"),
        ),
        forms.field(
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(field_id="review_cadence", name="review_cadence", value=values["review_cadence"], options=runtime.taxonomies["review_cadences"]["allowed_values"]),
            hint="Controls stale posture in the trust model.",
            errors=errors.get("review_cadence"),
        ),
        forms.field(
            field_id="status",
            label="Lifecycle status",
            control_html=forms.select(field_id="status", name="status", value=values["status"], options=runtime.taxonomies["statuses"]["allowed_values"]),
            hint="New operator-authored objects should usually begin as draft.",
            errors=errors.get("status"),
        ),
        forms.field(
            field_id="systems",
            label="Systems",
            control_html=forms.input(field_id="systems", name="systems", value=values["systems"], placeholder="<VPN_SERVICE>, <IDENTITY_PROVIDER>"),
            hint="Comma-separated controlled system references.",
            errors=errors.get("systems"),
        ),
        forms.field(
            field_id="tags",
            label="Tags",
            control_html=forms.input(field_id="tags", name="tags", value=values["tags"], placeholder="vpn, service-desk"),
            hint="Comma-separated controlled tags for discovery and reporting.",
            errors=errors.get("tags"),
        ),
    ]
    validation_html = _revision_error_summary_html(components, errors) if errors else ""
    body_html = (
        f'<form class="governed-form" method="post" action="{escape(form_action)}">'
        + "".join(controls)
        + forms.button(label="Create object shell")
        + "</form>"
    )
    guidance_html = components.section_card(
        title="Blueprint guidance",
        eyebrow="Write",
        body_html=(
            "<p>Start by choosing the blueprint, defining the purpose, and recording accountable ownership. Papyrus then carries the object shell into guided section-by-section drafting.</p>"
        ),
    )
    return {
        "validation_html": validation_html,
        "progress_html": _object_progress_html(components, values=values, errors=errors),
        "form_html": components.section_card(title="Choose blueprint and create draft shell", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }


def _common_revision_aside(runtime, detail) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    item = detail["object"]
    current_revision = detail.get("current_revision")
    return join_html(
        [
            components.trust_summary(
                title="Current object posture",
                badges=[
                    components.badge(label="Trust", value=item["trust_state"], tone="approved" if item["trust_state"] == "trusted" else "warning"),
                    components.badge(label="Approval", value=item["approval_state"] or "unknown", tone="approved" if item["approval_state"] == "approved" else "pending"),
                    components.badge(label="Owner", value=item["owner"], tone="muted"),
                ],
                summary="Lifecycle guardrails stay visible while the author moves work toward review.",
            ),
            components.section_card(
                title="Current revision context",
                eyebrow="Lifecycle",
                body_html=(
                    f"<p><strong>Current attached revision:</strong> {escape(current_revision['revision_review_state'])} · #{escape(current_revision['revision_number'])}</p>"
                    if current_revision
                    else "<p>No revision is attached yet. The first approved revision becomes the first canonical guidance for this object.</p>"
                )
                + f"<p><strong>Canonical path:</strong> {escape(item['canonical_path'])}</p>"
                + "<p><strong>If approved:</strong> this revision becomes canonical guidance for operators.</p>",
            ),
            components.section_card(
                title="Next steward role",
                eyebrow="Lifecycle",
                body_html="<p>After submission, the next explicit step is reviewer assignment and a recorded approval or rejection decision.</p>",
            ),
        ]
    )


def _completion_ratio(values: dict[str, str], fields: list[str]) -> tuple[int, int]:
    total = len(fields)
    completed = sum(1 for field in fields if values.get(field, "").strip())
    return completed, total


def _progress_card(components, *, title: str, completed: int, total: int, detail: str, tone: str = "default") -> str:
    return components.section_card(
        title=title,
        eyebrow="Progress",
        tone=tone,
        body_html=(
            f'<p class="metric-value">{escape(f"{completed}/{total}")}</p>'
            f"<p>{escape(detail)}</p>"
        ),
    )


def _object_progress_html(components, *, values: dict[str, str], errors: dict[str, list[str]]) -> str:
    purpose_completed, purpose_total = _completion_ratio(values, ["object_type", "title", "summary"])
    stewardship_completed, stewardship_total = _completion_ratio(values, ["owner", "team", "review_cadence", "status"])
    source_completed, source_total = _completion_ratio(values, ["object_id", "canonical_path"])
    blockers = sum(len(messages) for messages in errors.values())
    return join_html(
        [
            _progress_card(components, title="Choose type and purpose", completed=purpose_completed, total=purpose_total, detail="Define what this knowledge object is for and how readers will recognize it.", tone="brand"),
            _progress_card(components, title="Record stewardship", completed=stewardship_completed, total=stewardship_total, detail="Owner, team, cadence, and lifecycle status keep the object accountable."),
            _progress_card(components, title="Set durable source placement", completed=source_completed, total=source_total, detail="The shell needs a stable ID and canonical Markdown path."),
            components.section_card(
                title="Readiness",
                eyebrow="Progress",
                tone="warning" if blockers else "approved",
                body_html=(
                    f"<p><strong>Blocking fields:</strong> {escape(blockers)}</p>"
                    "<p>Create the shell once the required purpose, stewardship, and source fields are complete.</p>"
                ),
            ),
        ]
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
    return join_html(
        [
            _progress_card(components, title="Purpose and scope", completed=purpose_completed, total=purpose_total, detail="Make the reader-facing purpose explicit before filling in deeper structure.", tone="brand"),
            _progress_card(components, title="Core structured content", completed=content_completed, total=content_total, detail="Capture the steps, checks, or service structure that will become the live guidance."),
            _progress_card(
                components,
                title="Links and evidence posture",
                completed=linkage_completed + evidence_completed,
                total=linkage_total + evidence_total,
                detail=_revision_evidence_progress_detail(evidence_posture),
            ),
            components.section_card(
                title="Submission readiness",
                eyebrow="Progress",
                tone="warning" if blockers else "approved",
                body_html=(
                    f"<p><strong>Validation blockers:</strong> {escape(blockers)}</p>"
                    f"<p><strong>Warnings to review:</strong> {escape(warnings)}</p>"
                    "<p>Save the draft once blockers are clear. Submit it when the warnings are understood and acceptable to reviewers.</p>"
                ),
            ),
        ]
    )


def _write_timeline_html(*, stage: str, is_first_revision: bool = False) -> str:
    step_two_label = "Draft first revision" if is_first_revision else "Draft revision"
    steps = [
        {
            "index": "1",
            "title": "Create object shell",
            "detail": "Define the governed object ID, owner, and source path.",
            "state": "current" if stage == "object" else "complete",
        },
        {
            "index": "2",
            "title": step_two_label,
            "detail": "Capture the structured fields, narrative sections, and citations.",
            "state": "current" if stage == "revision" else "complete" if stage == "submit" else "upcoming",
        },
        {
            "index": "3",
            "title": "Submit for review",
            "detail": "Hand the draft into governance review and assignment.",
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


def _citation_search_status(title: str, reference: str) -> str:
    if title and reference:
        return f"Selected source: {title} -> {reference}"
    return "Search existing knowledge objects by title, tag, or object ID. Selecting a result fills the fields below."


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
            f"{evidence_posture['summary']}. External/manual evidence entered here stays weak until manage-side follow-up "
            "records capture time, integrity metadata, and any needed snapshot."
        )
    if int(evidence_posture.get("internal_reference_count") or 0):
        return (
            f"{evidence_posture['summary']}. Governed Papyrus references support traceability and review context, "
            "not captured external evidence."
        )
    return "Related services, related knowledge, and evidence posture stay visible. Citations entered here do not automatically mean strong evidence."


def _submit_evidence_posture_detail(evidence_posture: dict[str, object]) -> str:
    if int(evidence_posture.get("weak_external_evidence_count") or 0):
        return (
            "External/manual evidence remains weak until manage-side follow-up records capture time, "
            "integrity metadata, and any needed snapshot."
        )
    if int(evidence_posture.get("captured_external_evidence_count") or 0) and int(
        evidence_posture.get("internal_reference_count") or 0
    ):
        return (
            "Governed Papyrus references remain lightweight internal references. Captured external/manual evidence "
            "provides the stronger support recorded so far."
        )
    if int(evidence_posture.get("captured_external_evidence_count") or 0):
        return "Captured external/manual evidence has stronger support metadata recorded."
    if int(evidence_posture.get("internal_reference_count") or 0):
        return "Governed Papyrus references remain lightweight internal references for traceability and review context."
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
            '<p><strong>Next step:</strong> use the manage-side evidence flow to request follow-up on these citations.</p>'
            + f'<p>{link("Request evidence revalidation", f"/manage/objects/{quoted_path(object_id)}/evidence/revalidate", css_class="button button-secondary")}</p>'
        )
    return components.section_card(
        title=title,
        eyebrow="Evidence",
        body_html=(
            "<p>This write form can link governed Papyrus articles as lightweight internal references and can record a manual source title, reference, and note for external/manual evidence.</p>"
            "<p>Current web boundary: the write form does not record capture time, integrity hash, expiry metadata, or evidence snapshots directly.</p>"
            "<p>External, migration, or other manual evidence stays weak until the manage-side follow-up path records that stronger evidence metadata.</p>"
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
        f'value="{escape(lookup_value)}" placeholder="Search by title, tag, or object ID" '
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


def _next_action_panel_html(components, *, blueprint, completion: dict[str, object]) -> str:
    next_section_id = str(completion.get("next_section_id") or "")
    next_label = blueprint.section(next_section_id).display_name if next_section_id else "Review readiness"
    tone = "warning" if completion["draft_progress_state"] != "ready_for_review" else "approved"
    evidence_posture = completion.get("evidence_posture") or {}
    evidence_summary = str(evidence_posture.get("summary") or "No evidence references recorded yet.")
    return components.section_card(
        title="Next action",
        eyebrow="Guidance",
        tone=tone,
        body_html=(
            f"<p><strong>Current draft state:</strong> {escape(completion['draft_progress_state'])}</p>"
            f"<p><strong>Continue with:</strong> {escape(next_label)}</p>"
            f"<p><strong>Evidence posture:</strong> {escape(evidence_summary)}</p>"
            "<p>Required sections unlock sequentially through the visible progress bar. Review stays blocked until blockers are cleared.</p>"
        ),
    )


def _fallback_revision_href(*, object_id: str, revision_id: str) -> str:
    return f"/write/objects/{quoted_path(object_id)}/revisions/fallback?revision_id={quoted_path(revision_id)}"


def _guided_fallback_html(components, *, object_id: str, revision_id: str) -> str:
    return components.section_card(
        title="Operator fallback",
        eyebrow="Fallback",
        tone="context",
        body_html=(
            "<p>Guided section editing is the primary authoring path. Use the separate bulk draft fallback only when you need cross-section editing, citation lookup, or searchable multi-select helpers.</p>"
            f'<p>{link("Open bulk draft fallback", _fallback_revision_href(object_id=object_id, revision_id=revision_id), css_class="button button-secondary")}</p>'
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
        placeholder = str(field.get("placeholder") or "")
        if kind == "select":
            control = forms.select(
                field_id=name,
                name=name,
                value=values.get(name, ""),
                options=list(runtime.taxonomies[str(field.get("taxonomy"))]["allowed_values"]),
            )
        elif kind == "list":
            control = forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=5, placeholder=placeholder)
        elif kind == "long_text":
            control = forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=6, placeholder=placeholder)
        else:
            control = forms.input(field_id=name, name=name, value=values.get(name, ""), placeholder=placeholder)
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
        + forms.button(label="Save section")
        + (
            forms.link_button(
                label="Review readiness",
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
            '<p class="page-kicker">Step 2: Draft First Revision</p>'
            if is_first_revision
            else '<p class="page-kicker">Draft Revision</p>'
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
        "next_action_html": _next_action_panel_html(components, blueprint=blueprint, completion=completion),
        "fallback_html": _guided_fallback_html(
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
        forms.field(field_id="change_summary", label="Change summary", control_html=forms.input(field_id="change_summary", name="change_summary", value=values["change_summary"]), hint="Short audit-facing summary of this revision.", errors=errors.get("change_summary")),
        forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=values["owner"]), errors=errors.get("owner")),
        forms.field(field_id="team", label="Team", control_html=forms.select(field_id="team", name="team", value=values["team"], options=runtime.taxonomies["teams"]["allowed_values"]), errors=errors.get("team")),
        forms.field(field_id="status", label="Lifecycle status", control_html=forms.select(field_id="status", name="status", value=values["status"], options=runtime.taxonomies["statuses"]["allowed_values"]), errors=errors.get("status")),
        forms.field(field_id="review_cadence", label="Review cadence", control_html=forms.select(field_id="review_cadence", name="review_cadence", value=values["review_cadence"], options=runtime.taxonomies["review_cadences"]["allowed_values"]), errors=errors.get("review_cadence")),
        forms.field(field_id="audience", label="Audience", control_html=forms.select(field_id="audience", name="audience", value=values["audience"], options=runtime.taxonomies["audiences"]["allowed_values"]), errors=errors.get("audience")),
        multiline_field("systems", "Systems", "One controlled system reference per line."),
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
            label="Related object IDs",
            control_html=_multi_value_picker_control_html(
                field_name="related_object_ids",
                values=values,
                placeholder="Search related objects by title, tag, or object ID",
                singular_label="related object",
                manual_entry_label="Manual object ID entry",
                search_url="/write/objects/search",
                exclude_object_id=str(object_info["object_id"]),
            ),
            hint="Search existing knowledge objects and select one or more related objects for impact tracing.",
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
                multiline_field("related_runbooks", "Related runbooks", "One related runbook object ID per line."),
                multiline_field("related_known_errors", "Related known errors", "One related known error object ID per line."),
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
            '<p class="citation-entry-intro">Reference an existing Papyrus article first for lightweight internal traceability. Use the manual fields below only when the supporting source is external or otherwise outside Papyrus.</p>'
            + forms.field(
                field_id=f"citation_{index}_lookup",
                label=f"Citation {index} source search",
                control_html=_citation_lookup_control_html(index=index, values=values),
                hint="Search existing article titles, tags, or object IDs.",
                errors=errors.get("citations") if index == 1 else None,
            )
            + forms.field(
                field_id=f"citation_{index}_source_title",
                label=f"Citation {index} selected title",
                control_html=forms.input(field_id=f"citation_{index}_source_title", name=f"citation_{index}_source_title", value=values.get(f"citation_{index}_source_title", "")),
                hint="Filled from a selected Papyrus article, or enter the source title for manual/external evidence.",
            )
            + forms.field(
                field_id=f"citation_{index}_source_type",
                label=f"Citation {index} type",
                control_html=forms.input(field_id=f"citation_{index}_source_type", name=f"citation_{index}_source_type", value=values.get(f"citation_{index}_source_type", "document")),
                hint="document, url, ticket, or system reference.",
            )
            + forms.field(
                field_id=f"citation_{index}_source_ref",
                label=f"Citation {index} selected reference",
                control_html=forms.input(field_id=f"citation_{index}_source_ref", name=f"citation_{index}_source_ref", value=values.get(f"citation_{index}_source_ref", "")),
                hint="Papyrus path or manual/external reference. The write form does not capture snapshots or integrity metadata here.",
            )
            + forms.field(
                field_id=f"citation_{index}_note",
                label=f"Citation {index} note",
                control_html=forms.textarea(field_id=f"citation_{index}_note", name=f"citation_{index}_note", value=values.get(f"citation_{index}_note", ""), rows=2),
                hint="Why this reference supports the draft and what a reviewer should inspect.",
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
        + forms.button(label="Save first draft revision" if is_first_revision else "Save draft revision")
        + "</form>"
    )
    current_revision = detail.get("current_revision") or {}
    guided_return_href = (
        f"/write/objects/{quoted_path(object_info['object_id'])}/revisions/new?revision_id={quoted_path(str(current_revision.get('revision_id') or ''))}#revision-form"
    )
    guidance_html = components.section_card(
        title="Bulk draft fallback",
        eyebrow="Fallback",
        tone="context",
        body_html=(
            "<p>This separate fallback keeps the older bulk draft form available when you need cross-section editing, citation lookup, or searchable multi-select helpers.</p>"
            if is_first_revision
            else "<p>This fallback still writes the same governed draft, but guided section editing remains the primary route for day-to-day authoring.</p>"
        )
        + f'<p>{link("Return to guided section flow", guided_return_href, css_class="button button-secondary")}</p>'
        + "<p>Evidence note: governed Papyrus citations are lightweight internal references. External or manual evidence stays weak until later follow-up records capture time, integrity metadata, and any needed snapshot.</p>",
    )
    return {
        "validation_html": validation_html,
        "progress_html": _revision_progress_html(components, object_type=object_type, values=values, errors=errors, findings=findings),
        "form_html": components.section_card(title="Bulk draft fallback", eyebrow="Fallback", body_html=body_html, tone="context"),
        "guidance_html": guidance_html + _evidence_guidance_section(components, title="How evidence gets strengthened"),
    }


def _render_submit_page(runtime, detail, completion: dict[str, object], findings: list[str], form_errors: dict[str, list[str]], values: dict[str, str]) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    revision = detail["revision"]
    evidence_posture = completion.get("evidence_posture") or summarize_evidence_posture(detail.get("citations", []))
    form_html = components.section_card(
        title="Submit for review",
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
            + forms.button(label="Submit revision")
            + "</form>"
        ),
    )
    summary_html = components.section_card(
        title="Submission summary",
        eyebrow="Write",
        body_html=(
            f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_review_state'])}</p>"
            f"<p><strong>Change summary:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
            f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
            f"<p><strong>Evidence posture:</strong> {escape(evidence_posture['summary'])}</p>"
            f"<p><strong>Evidence note:</strong> {escape(_submit_evidence_posture_detail(evidence_posture))}</p>"
            f"<p><strong>If approved:</strong> this revision becomes canonical guidance at {escape(detail['object']['canonical_path'])}</p>"
        ),
    )
    findings_html = components.validation_findings(title="Pre-submit validation", items=[escape(item) for item in findings] or ["No blocking findings detected."], tone="warning" if findings else "approved")
    progress_html = components.section_card(
        title="Submission readiness",
        eyebrow="Progress",
        tone="warning" if findings else "approved",
        body_html=(
            f"<p><strong>Warnings to review:</strong> {escape(len(findings))}</p>"
            "<p>Submit once the warnings are understood and the reviewer can make a clear decision from the linked references, any evidence caveats, and the change summary.</p>"
        ),
    )
    guidance_html = ""
    if any("Evidence posture:" in item for item in findings):
        guidance_html = _evidence_guidance_section(
            components,
            title="How to strengthen weak evidence",
            include_action=True,
            object_id=str(detail["object"]["object_id"]),
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
                    f"/write/objects/{quoted_path(created.object_id)}/revisions/new?notice={quote_plus('Object shell created. Step 2 of 3: draft the first revision below.')}#revision-form"
                )
            errors = result.errors
            if errors:
                page_flash_html = FormPresenter(runtime.template_renderer).flash(
                    title="Attention",
                    body="Object shell not created. Fix the blocking fields below.",
                    tone="warning",
                )
        page_context = _render_object_form(runtime, values, errors, form_action=request.path)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_object_new.html",
                page_title="Choose blueprint",
                headline="Start A Guided Draft",
                kicker="Write",
                intro="Choose the blueprint, define the purpose, and set the durable source path before Papyrus opens the guided section editor.",
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_for_request(request),
                current_path=request.path,
                header_detail_html=_write_timeline_html(stage="object", is_first_revision=True),
                action_bar_html="",
                aside_html="",
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
                        headline=f"Draft {blueprint.display_name}",
                        kicker="Write",
                        intro="Papyrus moves one section at a time, shows progress continuously, and keeps the next required action visible.",
                        active_nav="write",
                        flash_html=page_flash_html,
                        actor_id=actor_id,
                        current_path=request.path,
                        header_detail_html=_write_timeline_html(stage="revision", is_first_revision=initial_detail["current_revision"] is None),
                        aside_html=_common_revision_aside(runtime, detail),
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
                f"{_fallback_revision_href(object_id=object_id, revision_id=revision_id)}&notice={quote_plus('Bulk draft fallback moved to its own route. Continue there if you need the older cross-section editor.')}"
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
                headline=f"Draft {blueprint.display_name}",
                kicker="Write",
                intro="Papyrus moves one section at a time, shows progress continuously, and keeps the next required action visible.",
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_id,
                current_path=request.path,
                header_detail_html=_write_timeline_html(stage="revision", is_first_revision=initial_detail["current_revision"] is None),
                aside_html=_common_revision_aside(runtime, detail),
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
                    f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision.revision_id)}&notice={quote_plus('Bulk draft fallback saved')}"
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
                    page_title="Bulk draft fallback",
                    headline="Bulk Draft Fallback",
                    kicker="Write",
                    intro="Use this separate fallback only when you need cross-section editing, citation lookup, or searchable multi-select helpers. Guided section editing remains the primary authoring path.",
                    active_nav="write",
                    flash_html=page_flash_html,
                    actor_id=actor_id,
                    current_path=request.path,
                    header_detail_html=_write_timeline_html(stage="revision", is_first_revision=is_first_revision),
                    aside_html=_common_revision_aside(runtime, detail),
                    scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
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
                page_title="Bulk draft fallback",
                headline="Bulk Draft Fallback",
                kicker="Write",
                intro="Use this separate fallback only when you need cross-section editing, citation lookup, or searchable multi-select helpers. Guided section editing remains the primary authoring path.",
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_id,
                current_path=request.path,
                header_detail_html=_write_timeline_html(stage="revision", is_first_revision=is_first_revision),
                aside_html=_common_revision_aside(runtime, detail),
                scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
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
            current_revision = detail.get("current_revision") or {}
            if (
                str(candidate.get("approval_state") or "") == "draft"
                and not str(current_revision.get("body_markdown") or "").strip()
                and not detail.get("citations")
            ):
                continue
            items.append(
                {
                    "object_id": str(candidate["object_id"]),
                    "title": str(candidate["title"]),
                    "path": str(candidate["path"]),
                    "object_type": str(candidate["object_type"]),
                    "approval_state": str(candidate["approval_state"]),
                    "trust_state": str(candidate["trust_state"]),
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
            items.append(
                {
                    "value": str(candidate["object_id"]),
                    "label": str(candidate["title"]),
                    "detail": (
                        f"{candidate['object_id']} | {candidate['path']} | "
                        f"{candidate['approval_state']} approval | {candidate['trust_state']} trust"
                    ),
                }
            )
        return json_response({"items": items})

    def submit_revision_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.query_value("revision_id") or str(knowledge_object_detail(object_id, database_path=runtime.database_path)["current_revision"]["revision_id"])
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
        page_context = _render_submit_page(runtime, detail, draft_status["completion"], findings, form_errors, values)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/review_submit.html",
                page_title="Submit for review",
                headline="Submit For Review",
                kicker="Write",
                intro="Check readiness before handoff so reviewers can see the lifecycle state, the evidence posture, and what will become canonical if approved.",
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                header_detail_html=_write_timeline_html(stage="submit", is_first_revision=detail["revision"]["revision_number"] == 1),
                aside_html=_common_revision_aside(runtime, {"object": detail["object"]}),
                page_context=page_context,
            )
        )

    router.add(["GET", "POST"], "/write/objects/new", create_object_page)
    router.add(["GET"], "/write/citations/search", citation_search_endpoint)
    router.add(["GET"], "/write/objects/search", related_object_search_endpoint)
    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/new", create_revision_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/fallback", fallback_revision_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/submit", submit_revision_page)
