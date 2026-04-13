from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.ingestion_flow import ingest_file, ingestion_detail, list_ingestions
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.domain.ingestion import has_mapping_result
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.ingest_presenter import (
    present_ingest_list_page,
    present_ingestion_detail_page,
    present_mapping_review_page,
)
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.urls import import_detail_url, write_object_url


def _render_page(runtime, request: Request, page: dict[str, object]):
    experience = require_experience(request, "operator")
    return html_response(
        runtime.page_renderer.render_page(
            flash_html=flash_html_for_request(runtime, request),
            role_id=experience.role,
            current_path=request.path,
            search_value=request.query_value("query"),
            **page,
        )
    )


def register(router, runtime) -> None:
    def ingest_list_page(request: Request):
        require_experience(request, "operator")
        errors: list[str] = []
        if request.method == "POST":
            upload = request.uploaded_file("upload")
            source_path = request.form_value("source_path").strip()
            if upload is not None and source_path:
                errors.append("Choose either a file upload or a local source file, not both.")
            elif upload is None and not source_path:
                errors.append(
                    "Select a file upload before starting ingestion."
                    if not runtime.allow_web_ingest_local_paths
                    else "Select a file upload or provide a local source file before starting import."
                )
            elif upload is None and source_path and not runtime.allow_web_ingest_local_paths:
                errors.append("Local source file import is unavailable in this session.")
            else:
                try:
                    result = (
                        ingest_file(
                            file_path=upload.filename,
                            payload=upload.body,
                            database_path=runtime.database_path,
                            source_root=runtime.source_root,
                        )
                        if upload is not None
                        else ingest_file(
                            file_path=source_path,
                            database_path=runtime.database_path,
                            source_root=runtime.source_root,
                        )
                    )
                    return redirect_response(
                        import_detail_url(str(result["ingestion_id"]))
                        + f"?notice={quote_plus('Import started. Review the mapping before creating the draft.')}"
                    )
                except ValueError as exc:
                    errors.append(str(exc))

        page = present_ingest_list_page(
            runtime.template_renderer,
            ingestions=list_ingestions(database_path=runtime.database_path),
            errors=errors,
            allow_web_ingest_local_paths=runtime.allow_web_ingest_local_paths,
        )
        return _render_page(runtime, request, page)

    def ingest_detail_page(request: Request):
        detail = ingestion_detail(
            ingestion_id=request.route_value("ingestion_id"), database_path=runtime.database_path
        )
        page = present_ingestion_detail_page(runtime.template_renderer, detail=detail)
        return _render_page(runtime, request, page)

    def ingest_review_page(request: Request):
        experience = require_experience(request, "operator")
        ingestion_id = request.route_value("ingestion_id")
        detail = ingestion_detail(ingestion_id=ingestion_id, database_path=runtime.database_path)
        existing_mapping = (
            detail.get("mapping_result")
            if has_mapping_result(detail.get("mapping_result"))
            else None
        )
        mapping = existing_mapping or map_to_blueprint(
            ingestion_id=ingestion_id,
            blueprint_id=detail.get("blueprint_id") or detail["classification"]["blueprint_id"],
            database_path=runtime.database_path,
        )
        if existing_mapping is None:
            detail = ingestion_detail(
                ingestion_id=ingestion_id, database_path=runtime.database_path
            )
        errors: list[str] = []
        if request.method == "POST":
            required_fields = [
                "object_id",
                "title",
                "canonical_path",
                "owner",
                "team",
                "review_cadence",
                "status",
                "audience",
            ]
            missing = [field for field in required_fields if not request.form_value(field).strip()]
            if missing:
                field_labels = {
                    "object_id": "Reference code",
                    "title": "Title",
                    "canonical_path": "Publishing location",
                    "owner": "Owner",
                    "team": "Team",
                    "review_cadence": "Review cadence",
                    "status": "Status",
                    "audience": "Audience",
                }
                errors = [f"{field_labels[field]} is required." for field in missing]
            else:
                converted = convert_to_draft(
                    ingestion_id=ingestion_id,
                    object_id=request.form_value("object_id").strip(),
                    title=request.form_value("title").strip(),
                    canonical_path=request.form_value("canonical_path").strip(),
                    owner=request.form_value("owner").strip(),
                    team=request.form_value("team").strip(),
                    review_cadence=request.form_value("review_cadence").strip(),
                    object_lifecycle_state=request.form_value("status").strip(),
                    audience=request.form_value("audience").strip(),
                    actor=str(experience.audit_actor_id),
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                )
                return redirect_response(
                    write_object_url(
                        str(converted["object_id"]), revision_id=str(converted["revision_id"])
                    )
                    + f"&notice={quote_plus('Draft created from the imported document.')}"
                )

        page = present_mapping_review_page(
            runtime.template_renderer,
            detail=detail,
            mapping=mapping,
            errors=errors,
            taxonomies=runtime.taxonomies,
        )
        return _render_page(runtime, request, page)

    router.add(["GET", "POST"], "/operator/import", ingest_list_page)
    router.add(["GET"], "/operator/import/{ingestion_id}", ingest_detail_page)
    router.add(["GET", "POST"], "/operator/import/{ingestion_id}/review", ingest_review_page)
