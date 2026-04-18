from __future__ import annotations

from papyrus.application.queries import knowledge_object_detail, search_knowledge_objects
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, json_response
from papyrus.interfaces.web.presenters.governed_presenter import (
    projection_state,
    projection_use_guidance,
)


def register(router, runtime) -> None:
    def citation_search_endpoint(request: Request):
        experience = require_experience(request, "operator")
        query = request.query_value("query").strip()
        exclude_object_id = request.query_value("exclude_object_id").strip()
        if len(query) < 2:
            return json_response({"items": []})
        candidates = search_knowledge_objects(
            query, limit=12, database_path=runtime.database_path, role=experience.role
        )
        items: list[dict[str, str]] = []
        for candidate in candidates:
            if exclude_object_id and str(candidate["object_id"]) == exclude_object_id:
                continue
            if candidate.get("current_revision_id") is None:
                continue
            detail = knowledge_object_detail(
                str(candidate["object_id"]),
                database_path=runtime.database_path,
                visibility_role=experience.role,
            )
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
                    "summary": str(
                        reference_projection.get("summary") or use_guidance.get("summary") or ""
                    ),
                    "detail": (
                        f"{state.get('revision_review_state') or candidate.get('revision_review_state') or 'unknown'} review | "
                        f"{state.get('trust_state') or candidate.get('trust_state') or 'unknown'} trust | "
                        f"{reference_projection.get('detail') or use_guidance.get('detail') or 'Reference available.'}"
                    ),
                }
            )
        return json_response({"items": items})

    def related_object_search_endpoint(request: Request):
        experience = require_experience(request, "operator")
        query = request.query_value("query").strip()
        exclude_object_id = request.query_value("exclude_object_id").strip()
        if len(query) < 2:
            return json_response({"items": []})
        candidates = search_knowledge_objects(
            query, limit=12, database_path=runtime.database_path, role=experience.role
        )
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
                        f"{state.get('revision_review_state') or 'unknown'} review | "
                        f"{state.get('trust_state') or 'unknown'} trust"
                    ),
                }
            )
        return json_response({"items": items})

    router.add(
        ["GET"],
        "/write/citations/search",
        citation_search_endpoint,
        minimum_visible_role="operator",
    )
    router.add(
        ["GET"],
        "/write/objects/search",
        related_object_search_endpoint,
        minimum_visible_role="operator",
    )
