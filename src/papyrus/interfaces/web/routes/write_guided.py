from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.authoring_flow import compute_completion_state, create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.queries import knowledge_object_detail
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.write_presenter import present_guided_revision_page
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import parse_multiline, quoted_path


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
            values[f"citation_{index}_lookup"] = str(citation.get("source_title") or "")
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


def register(router, runtime) -> None:
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
                    body="Section not saved. Fix the blocking fields below.",
                    tone="warning",
                )
                page_context = present_guided_revision_page(
                    runtime,
                    object_detail=detail,
                    draft_status=draft_status,
                    revision_id=revision_id,
                    section_id=section_id,
                    is_first_revision=initial_detail["current_revision"] is None,
                    form_values=_section_form_values(section, candidate_values),
                    form_errors=form_errors,
                )
                return html_response(
                    runtime.page_renderer.render_page(
                        page_template="pages/write_revision_edit.html",
                        page_title=f"Draft {section.display_name}",
                        page_header={
                            "headline": f"Draft {blueprint.display_name}",
                            "show_actor_banner": True,
                            "show_actor_links": True,
                        },
                        active_nav="write",
                        flash_html=page_flash_html,
                        actor_id=actor_id,
                        current_path=request.path,
                        aside_html="",
                        scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
                        shell_variant="normal",
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

        page_context = present_guided_revision_page(
            runtime,
            object_detail=detail,
            draft_status=draft_status,
            revision_id=revision_id,
            section_id=section_id,
            is_first_revision=initial_detail["current_revision"] is None,
            form_values=_section_form_values(blueprint.section(section_id), draft_status["section_content"].get(section_id, {})),
            form_errors={},
        )
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_revision_edit.html",
                page_title=f"Draft {blueprint.display_name}",
                page_header={
                    "headline": f"Draft {blueprint.display_name}",
                    "show_actor_banner": True,
                    "show_actor_links": True,
                },
                active_nav="write",
                flash_html=page_flash_html,
                actor_id=actor_id,
                current_path=request.path,
                aside_html="",
                scripts=["/static/js/citation_picker.js", "/static/js/multi_value_picker.js"],
                shell_variant="normal",
                page_context=page_context,
            )
        )

    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/new", create_revision_page)
