from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server

from papyrus.application.queries import (
    KnowledgeObjectNotFoundError,
    RuntimeUnavailableError,
    ServiceNotFoundError,
    impact_view_for_object,
    impact_view_for_service,
    knowledge_object_detail,
    knowledge_queue,
    revision_history,
    service_detail,
    trust_dashboard,
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
        if method != "GET":
            return _json_response(start_response, "405 Method Not Allowed", {"error": "method_not_allowed"})

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

            if path == "/queue":
                limit = int(query.get("limit", ["100"])[0])
                return _json_response(
                    start_response,
                    "200 OK",
                    {
                        "queue": knowledge_queue(limit=limit, database_path=resolved_database_path),
                    },
                )

            if path == "/dashboard/trust":
                return _json_response(
                    start_response,
                    "200 OK",
                    trust_dashboard(database_path=resolved_database_path),
                )

            if path.startswith("/objects/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if len(parts) == 2:
                    return _json_response(
                        start_response,
                        "200 OK",
                        knowledge_object_detail(parts[1], database_path=resolved_database_path),
                    )
                if len(parts) == 3 and parts[2] == "revisions":
                    return _json_response(
                        start_response,
                        "200 OK",
                        revision_history(parts[1], database_path=resolved_database_path),
                    )

            if path.startswith("/services/"):
                parts = [unquote(part) for part in path.strip("/").split("/")]
                if len(parts) == 2:
                    return _json_response(
                        start_response,
                        "200 OK",
                        service_detail(parts[1], database_path=resolved_database_path),
                    )

            if path.startswith("/impact/object/"):
                object_id = unquote(path.removeprefix("/impact/object/"))
                return _json_response(
                    start_response,
                    "200 OK",
                    impact_view_for_object(object_id, database_path=resolved_database_path),
                )

            if path.startswith("/impact/service/"):
                service_id = unquote(path.removeprefix("/impact/service/"))
                return _json_response(
                    start_response,
                    "200 OK",
                    impact_view_for_service(service_id, database_path=resolved_database_path),
                )

            return _json_response(start_response, "404 Not Found", {"error": "not_found", "path": path})
        except RuntimeUnavailableError as exc:
            return _json_response(start_response, "503 Service Unavailable", {"error": "runtime_unavailable", "detail": str(exc)})
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            return _json_response(start_response, "404 Not Found", {"error": "not_found", "detail": str(exc)})
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
