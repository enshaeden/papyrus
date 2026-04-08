from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server

from papyrus.application.commands import (
    approve_revision_command,
    assign_reviewer_command,
    create_object_command,
    create_revision_command,
    ingest_event_command,
    mark_object_suspect_due_to_change_command,
    record_validation_run_command,
    reject_revision_command,
    submit_for_review_command,
    supersede_object_command,
)
from papyrus.application.queries import (
    KnowledgeObjectNotFoundError,
    RuntimeUnavailableError,
    ServiceNotFoundError,
    audit_view,
    impact_view_for_object,
    impact_view_for_service,
    knowledge_object_detail,
    knowledge_queue,
    manage_queue,
    review_detail,
    revision_history,
    service_catalog,
    service_detail,
    trust_dashboard,
    validation_run_history,
)
from papyrus.domain.actor import require_actor_id
from papyrus.infrastructure.paths import DB_PATH, ROOT


def _json_response(start_response, status: str, payload: object) -> list[bytes]:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ]
    start_response(status, headers)
    return [body]


def _error_payload(*, error: str, title: str, detail: str, action: str, category: str) -> dict[str, str]:
    return {
        "error": error,
        "title": title,
        "detail": detail,
        "action": action,
        "category": category,
    }


def _links_for_object(object_id: str, revision_id: str | None = None) -> dict[str, str]:
    links = {
        "object": f"/objects/{object_id}",
        "revision_history": f"/objects/{object_id}/revisions",
        "manage_queue": "/manage/queue",
        "queue": "/queue",
    }
    if revision_id:
        links["review"] = f"/reviews/{object_id}/{revision_id}"
        links["review_assignment"] = f"/manage/reviews/{object_id}/{revision_id}/assign"
        links["review_decision"] = f"/manage/reviews/{object_id}/{revision_id}"
    return links


def _actor_from_payload(request_payload: dict[str, object], *, require_explicit: bool) -> str:
    actor = str(request_payload.get("actor") or "").strip()
    if require_explicit and not actor:
        raise ValueError("actor is required for governed API actions")
    return require_actor_id(actor) if require_explicit else actor


def _object_result_payload(
    *,
    object_id: str,
    database_path: Path,
    message: str,
    actor: str,
    revision_id: str | None = None,
) -> dict[str, object]:
    detail = knowledge_object_detail(object_id, database_path=database_path)
    payload: dict[str, object] = {
        "message": message,
        "actor": actor,
        "object": detail["object"],
        "object_id": detail["object"]["object_id"],
        "object_type": detail["object"]["object_type"],
        "title": detail["object"]["title"],
        "posture": detail["posture"],
        "links": _links_for_object(object_id, revision_id),
    }
    if revision_id:
        payload["revision_id"] = revision_id
        payload["review"] = review_detail(object_id, revision_id, database_path=database_path)
    return payload


def app(database_path: str | Path = DB_PATH, source_root: str | Path = ROOT) -> Callable:
    resolved_database_path = Path(database_path)
    resolved_source_root = Path(source_root).resolve()

    def application(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/") or "/"
        query = parse_qs(environ.get("QUERY_STRING", ""))
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
        raw_body = environ["wsgi.input"].read(content_length) if content_length else b""
        try:
            request_payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            return _json_response(
                start_response,
                "400 Bad Request",
                _error_payload(
                    error="invalid_request_body",
                    title="Invalid JSON body",
                    detail="The API received malformed JSON and could not parse the request body.",
                    action="Send a valid JSON object payload.",
                    category="user_action_needed",
                ),
            )
        if raw_body and not isinstance(request_payload, dict):
            return _json_response(
                start_response,
                "400 Bad Request",
                _error_payload(
                    error="invalid_request_body",
                    title="Invalid JSON body",
                    detail="The API expects a top-level JSON object payload for operator actions.",
                    action="Wrap request properties in a JSON object.",
                    category="user_action_needed",
                ),
            )

        try:
            if path == "/" or path == "/health":
                return _json_response(
                    start_response,
                    "200 OK",
                    {
                        "status": "ok",
                        "runtime_database": str(resolved_database_path),
                    },
                )

            if method == "GET" and path == "/queue":
                limit = int(query.get("limit", ["100"])[0])
                return _json_response(
                    start_response,
                    "200 OK",
                    {
                        "queue": knowledge_queue(limit=limit, database_path=resolved_database_path),
                    },
                )

            if method == "GET" and path == "/dashboard/trust":
                return _json_response(
                    start_response,
                    "200 OK",
                    trust_dashboard(database_path=resolved_database_path),
                )

            if method == "GET" and path == "/services":
                return _json_response(
                    start_response,
                    "200 OK",
                    {"services": service_catalog(database_path=resolved_database_path)},
                )

            if method == "GET" and path == "/manage/queue":
                return _json_response(
                    start_response,
                    "200 OK",
                    manage_queue(database_path=resolved_database_path),
                )

            if method == "GET" and path == "/manage/audit":
                return _json_response(
                    start_response,
                    "200 OK",
                    {"events": audit_view(object_id=query.get("object_id", [None])[0], database_path=resolved_database_path)},
                )

            if method == "GET" and path == "/manage/validation-runs":
                return _json_response(
                    start_response,
                    "200 OK",
                    {"validation_runs": validation_run_history(database_path=resolved_database_path)},
                )

            if method == "POST" and path == "/events":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                result = ingest_event_command(
                    database_path=resolved_database_path,
                    event_type=str(request_payload["event_type"]),
                    source=str(request_payload.get("source") or "local"),
                    entity_type=str(request_payload["entity_type"]),
                    entity_id=str(request_payload["entity_id"]),
                    payload=request_payload.get("payload") or {},
                    actor=actor,
                    occurred_at=request_payload.get("occurred_at"),
                    event_id=str(request_payload["event_id"]) if request_payload.get("event_id") else None,
                )
                return _json_response(
                    start_response,
                    "201 Created",
                    {
                        "message": "Event ingested.",
                        "actor": actor,
                        "event_id": result.event_id,
                        "event_type": result.event_type,
                        "entity_type": result.entity_type,
                        "entity_id": result.entity_id,
                        "impacted_count": result.impacted_count,
                        "links": {
                            "queue": "/queue",
                            "audit": "/manage/audit",
                        },
                    },
                )

            if method == "POST" and path == "/objects":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                created = create_object_command(
                    database_path=resolved_database_path,
                    source_root=resolved_source_root,
                    actor=actor,
                    **{key: value for key, value in request_payload.items() if key != "actor"},
                )
                return _json_response(
                    start_response,
                    "201 Created",
                    _object_result_payload(
                        object_id=created.object_id,
                        database_path=resolved_database_path,
                        message="Knowledge object shell created.",
                        actor=actor,
                    ),
                )

            if path.startswith("/objects/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if method == "GET" and len(parts) == 2:
                    return _json_response(
                        start_response,
                        "200 OK",
                        knowledge_object_detail(parts[1], database_path=resolved_database_path),
                    )
                if method == "GET" and len(parts) == 3 and parts[2] == "revisions":
                    return _json_response(
                        start_response,
                        "200 OK",
                        revision_history(parts[1], database_path=resolved_database_path),
                    )
                if method == "POST" and len(parts) == 3 and parts[2] == "revisions":
                    actor = _actor_from_payload(request_payload, require_explicit=True)
                    created = create_revision_command(
                        database_path=resolved_database_path,
                        source_root=resolved_source_root,
                        object_id=parts[1],
                        normalized_payload=request_payload["normalized_payload"],
                        body_markdown=request_payload["body_markdown"],
                        actor=actor,
                        legacy_metadata=request_payload.get("legacy_metadata") or {},
                        change_summary=request_payload.get("change_summary"),
                    )
                    return _json_response(
                        start_response,
                        "201 Created",
                        _object_result_payload(
                            object_id=created.object_id,
                            revision_id=created.revision_id,
                            database_path=resolved_database_path,
                            message="Draft revision created.",
                            actor=actor,
                        ),
                    )
                if method == "POST" and len(parts) == 3 and parts[2] == "supersede":
                    actor = _actor_from_payload(request_payload, require_explicit=True)
                    supersede_object_command(
                        database_path=resolved_database_path,
                        source_root=resolved_source_root,
                        object_id=parts[1],
                        replacement_object_id=str(request_payload["replacement_object_id"]),
                        actor=actor,
                        notes=str(request_payload["notes"]),
                    )
                    return _json_response(
                        start_response,
                        "200 OK",
                        _object_result_payload(
                            object_id=parts[1],
                            database_path=resolved_database_path,
                            message="Object superseded and replacement captured in audit history.",
                            actor=actor,
                        ),
                    )
                if method == "POST" and len(parts) == 3 and parts[2] == "mark-suspect":
                    actor = _actor_from_payload(request_payload, require_explicit=True)
                    result = mark_object_suspect_due_to_change_command(
                        database_path=resolved_database_path,
                        object_id=parts[1],
                        actor=actor,
                        reason=str(request_payload["reason"]),
                        changed_entity_type=str(request_payload["changed_entity_type"]),
                        changed_entity_id=str(request_payload.get("changed_entity_id") or "") or None,
                    )
                    payload = _object_result_payload(
                        object_id=parts[1],
                        database_path=resolved_database_path,
                        message="Object marked suspect with explicit change rationale.",
                        actor=actor,
                    )
                    payload["audit_event"] = {
                        "event_type": result.event.event_type,
                        "occurred_at": result.event.occurred_at.isoformat(),
                        "details": result.event.details,
                    }
                    return _json_response(start_response, "200 OK", payload)

            if method == "GET" and path.startswith("/services/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if len(parts) == 2:
                    return _json_response(
                        start_response,
                        "200 OK",
                        service_detail(parts[1], database_path=resolved_database_path),
                    )

            if method == "GET" and path.startswith("/impact/object/"):
                object_id = unquote(path.removeprefix("/impact/object/"))
                return _json_response(
                    start_response,
                    "200 OK",
                    impact_view_for_object(object_id, database_path=resolved_database_path),
                )

            if method == "GET" and path.startswith("/impact/service/"):
                service_id = unquote(path.removeprefix("/impact/service/"))
                return _json_response(
                    start_response,
                    "200 OK",
                    impact_view_for_service(service_id, database_path=resolved_database_path),
                )

            if method == "GET" and path.startswith("/reviews/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if len(parts) == 3:
                    return _json_response(
                        start_response,
                        "200 OK",
                        review_detail(parts[1], parts[2], database_path=resolved_database_path),
                    )

            if method == "POST" and path == "/reviews/submit":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                result = submit_for_review_command(
                    database_path=resolved_database_path,
                    source_root=resolved_source_root,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    actor=actor,
                    notes=request_payload.get("notes"),
                )
                payload = _object_result_payload(
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    database_path=resolved_database_path,
                    message="Revision submitted for review.",
                    actor=actor,
                )
                payload["audit_event"] = {"event_type": result.event.event_type}
                return _json_response(start_response, "200 OK", payload)

            if method == "POST" and path == "/reviews/assign":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                due_at_raw = request_payload.get("due_at")
                due_at = None
                if isinstance(due_at_raw, str) and due_at_raw:
                    due_at = dt.datetime.fromisoformat(due_at_raw)
                assignment = assign_reviewer_command(
                    database_path=resolved_database_path,
                    source_root=resolved_source_root,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=actor,
                    due_at=due_at,
                    notes=request_payload.get("notes"),
                )
                payload = _object_result_payload(
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    database_path=resolved_database_path,
                    message="Reviewer assigned.",
                    actor=actor,
                )
                payload["assignment"] = {
                    "assignment_id": assignment.assignment_id,
                    "reviewer": assignment.reviewer,
                    "state": assignment.state,
                }
                return _json_response(
                    start_response,
                    "200 OK",
                    payload,
                )

            if method == "POST" and path == "/reviews/approve":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                approved = approve_revision_command(
                    database_path=resolved_database_path,
                    source_root=resolved_source_root,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=actor,
                    notes=request_payload.get("notes"),
                )
                return _json_response(
                    start_response,
                    "200 OK",
                    _object_result_payload(
                        object_id=approved.object_id,
                        revision_id=approved.revision_id,
                        database_path=resolved_database_path,
                        message="Revision approved.",
                        actor=actor,
                    ),
                )

            if method == "POST" and path == "/reviews/reject":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                rejected = reject_revision_command(
                    database_path=resolved_database_path,
                    source_root=resolved_source_root,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=actor,
                    notes=str(request_payload["notes"]),
                )
                return _json_response(
                    start_response,
                    "200 OK",
                    _object_result_payload(
                        object_id=rejected.object_id,
                        revision_id=rejected.revision_id,
                        database_path=resolved_database_path,
                        message="Revision rejected.",
                        actor=actor,
                    ),
                )

            if method == "POST" and path == "/validation-runs":
                actor = _actor_from_payload(request_payload, require_explicit=True)
                run_id = record_validation_run_command(
                    database_path=resolved_database_path,
                    run_id=str(request_payload["run_id"]),
                    run_type=str(request_payload["run_type"]),
                    status=str(request_payload["status"]),
                    finding_count=int(request_payload.get("finding_count") or 0),
                    details=request_payload.get("details") or {},
                    actor=actor,
                )
                return _json_response(
                    start_response,
                    "201 Created",
                    {
                        "message": "Validation run recorded.",
                        "actor": actor,
                        "run_id": run_id,
                        "links": {
                            "validation_runs": "/manage/validation-runs",
                            "audit": "/manage/audit",
                        },
                    },
                )

            if method not in {"GET", "POST"}:
                return _json_response(
                    start_response,
                    "405 Method Not Allowed",
                    _error_payload(
                        error="method_not_allowed",
                        title="Method not allowed",
                        detail="This endpoint only supports the documented GET or POST operator flow.",
                        action="Retry with GET for reads or POST for governed mutations.",
                        category="user_action_needed",
                    ),
                )

            return _json_response(
                start_response,
                "404 Not Found",
                _error_payload(
                    error="not_found",
                    title="Route not found",
                    detail=f"No API route matches {path}.",
                    action="Check the operator API path and try again.",
                    category="user_action_needed",
                ),
            )
        except RuntimeUnavailableError as exc:
            return _json_response(
                start_response,
                "503 Service Unavailable",
                _error_payload(
                    error="runtime_unavailable",
                    title="Runtime unavailable",
                    detail=str(exc),
                    action="Run `python3 scripts/build_index.py` to rebuild the runtime projection.",
                    category="runtime_rebuild_needed",
                ),
            )
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            return _json_response(
                start_response,
                "404 Not Found",
                _error_payload(
                    error="not_found",
                    title="Record not found",
                    detail=str(exc),
                    action="Verify the object, revision, or service identifier and try again.",
                    category="user_action_needed",
                ),
            )
        except ValueError as exc:
            return _json_response(
                start_response,
                "400 Bad Request",
                _error_payload(
                    error="bad_request",
                    title="Request rejected",
                    detail=str(exc),
                    action="Correct the request payload and retry the governed action.",
                    category="user_action_needed",
                ),
            )
        except Exception:  # pragma: no cover - exercised through interface integration tests
            return _json_response(
                start_response,
                "500 Internal Server Error",
                _error_payload(
                    error="internal_error",
                    title="Internal error",
                    detail="Papyrus could not complete the request safely.",
                    action="Retry the action. If the failure persists, inspect the local server logs and audit trail.",
                    category="admin_action_needed",
                ),
            )

    return application


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Papyrus JSON API over WSGI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8081, help="Bind port. Defaults to 8081.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    parser.add_argument("--source-root", default=str(ROOT), help="Canonical source root for governed writeback.")
    args = parser.parse_args()

    with make_server(args.host, args.port, app(args.db, args.source_root)) as server:
        print(f"Papyrus JSON API listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
