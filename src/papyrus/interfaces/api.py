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
    reject_revision_command,
    submit_for_review_command,
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
from papyrus.infrastructure.paths import DB_PATH


def _json_response(start_response, status: str, payload: object) -> list[bytes]:
    body = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store"),
    ]
    start_response(status, headers)
    return [body]


def app(database_path: str | Path = DB_PATH) -> Callable:
    resolved_database_path = Path(database_path)

    def application(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/") or "/"
        query = parse_qs(environ.get("QUERY_STRING", ""))
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
        raw_body = environ["wsgi.input"].read(content_length) if content_length else b""
        request_payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        if raw_body and not isinstance(request_payload, dict):
            return _json_response(start_response, "400 Bad Request", {"error": "invalid_request_body"})

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

            if method == "POST" and path == "/objects":
                created = create_object_command(database_path=resolved_database_path, **request_payload)
                return _json_response(
                    start_response,
                    "201 Created",
                    {"object_id": created.object_id, "object_type": created.object_type, "title": created.title},
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
                    created = create_revision_command(
                        database_path=resolved_database_path,
                        object_id=parts[1],
                        normalized_payload=request_payload["normalized_payload"],
                        body_markdown=request_payload["body_markdown"],
                        actor=str(request_payload.get("actor") or "papyrus-api"),
                        legacy_metadata=request_payload.get("legacy_metadata") or {},
                        change_summary=request_payload.get("change_summary"),
                    )
                    return _json_response(
                        start_response,
                        "201 Created",
                        {
                            "revision_id": created.revision_id,
                            "object_id": created.object_id,
                            "revision_number": created.revision_number,
                            "state": created.state,
                        },
                    )

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
                result = submit_for_review_command(
                    database_path=resolved_database_path,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    actor=str(request_payload.get("actor") or "papyrus-api"),
                    notes=request_payload.get("notes"),
                )
                return _json_response(start_response, "200 OK", {"event_type": result.event.event_type})

            if method == "POST" and path == "/reviews/assign":
                due_at_raw = request_payload.get("due_at")
                due_at = None
                if isinstance(due_at_raw, str) and due_at_raw:
                    due_at = dt.datetime.fromisoformat(due_at_raw)
                assignment = assign_reviewer_command(
                    database_path=resolved_database_path,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=str(request_payload.get("actor") or "papyrus-api"),
                    due_at=due_at,
                    notes=request_payload.get("notes"),
                )
                return _json_response(
                    start_response,
                    "200 OK",
                    {"assignment_id": assignment.assignment_id, "reviewer": assignment.reviewer, "state": assignment.state},
                )

            if method == "POST" and path == "/reviews/approve":
                approved = approve_revision_command(
                    database_path=resolved_database_path,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=str(request_payload.get("actor") or "papyrus-api"),
                    notes=request_payload.get("notes"),
                )
                return _json_response(
                    start_response,
                    "200 OK",
                    {"revision_id": approved.revision_id, "state": approved.state},
                )

            if method == "POST" and path == "/reviews/reject":
                rejected = reject_revision_command(
                    database_path=resolved_database_path,
                    object_id=str(request_payload["object_id"]),
                    revision_id=str(request_payload["revision_id"]),
                    reviewer=str(request_payload["reviewer"]),
                    actor=str(request_payload.get("actor") or "papyrus-api"),
                    notes=str(request_payload["notes"]),
                )
                return _json_response(
                    start_response,
                    "200 OK",
                    {"revision_id": rejected.revision_id, "state": rejected.state},
                )

            if method not in {"GET", "POST"}:
                return _json_response(start_response, "405 Method Not Allowed", {"error": "method_not_allowed"})

            return _json_response(start_response, "404 Not Found", {"error": "not_found", "path": path})
        except RuntimeUnavailableError as exc:
            return _json_response(start_response, "503 Service Unavailable", {"error": "runtime_unavailable", "detail": str(exc)})
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            return _json_response(start_response, "404 Not Found", {"error": "not_found", "detail": str(exc)})
        except ValueError as exc:
            return _json_response(start_response, "400 Bad Request", {"error": "bad_request", "detail": str(exc)})
        except Exception as exc:  # pragma: no cover - exercised through interface integration tests
            return _json_response(start_response, "500 Internal Server Error", {"error": "internal_error", "detail": str(exc)})

    return application


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Papyrus JSON API over WSGI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8081, help="Bind port. Defaults to 8081.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    args = parser.parse_args()

    with make_server(args.host, args.port, app(args.db)) as server:
        print(f"Papyrus JSON API listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
