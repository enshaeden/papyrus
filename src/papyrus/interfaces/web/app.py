from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import unquote
from urllib.parse import urlencode
from wsgiref.simple_server import make_server

from papyrus.application.queries import KnowledgeObjectNotFoundError, RuntimeUnavailableError, ServiceNotFoundError
from papyrus.infrastructure.observability import get_logger, log_event
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies
from papyrus.interfaces.web.experience import RoleAccessDeniedError
from papyrus.interfaces.web.http import Request, html_response, redirect_response, request_from_environ, static_response
from papyrus.interfaces.web.presenters.system_presenter import present_error_page
from papyrus.interfaces.web.rendering import PageRenderer
from papyrus.interfaces.web.runtime import WebRuntime
from papyrus.interfaces.web.routes import dashboard, home, impact, ingest, manage, objects, queue, services, write
from papyrus.interfaces.startup_guard import prepare_operator_source_root

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class Route:
    methods: tuple[str, ...]
    pattern: str
    handler: Callable[[Request], object]


@dataclass(frozen=True)
class RouteMatch:
    route: Route
    request: Request


class Router:
    def __init__(self):
        self._routes: list[Route] = []

    def add(self, methods: list[str], pattern: str, handler: Callable[[Request], object]) -> None:
        self._routes.append(Route(tuple(methods), pattern, handler))

    def match(self, request: Request) -> RouteMatch | None:
        for route in self._routes:
            params = match_pattern(route.pattern, request.path)
            if params is None:
                continue
            routed_request = request.with_route_params(params)
            if request.method not in route.methods:
                return RouteMatch(Route(("__method_not_allowed__",), route.pattern, route.handler), routed_request)
            return RouteMatch(route, routed_request)
        return None


def match_pattern(pattern: str, path: str) -> dict[str, str] | None:
    pattern_parts = [part for part in pattern.strip("/").split("/") if part]
    path_parts = [part for part in path.strip("/").split("/") if part]
    if pattern == "/" and path == "/":
        return {}
    if len(pattern_parts) != len(path_parts):
        return None
    params: dict[str, str] = {}
    for pattern_part, path_part in zip(pattern_parts, path_parts):
        if pattern_part.startswith("{") and pattern_part.endswith("}"):
            params[pattern_part[1:-1]] = unquote(path_part)
            continue
        if pattern_part != path_part:
            return None
    return params


def _error_page(
    runtime: WebRuntime,
    *,
    title: str,
    detail: str,
    status: str,
    action: str,
    active_nav: str = "manage",
) -> str:
    return runtime.page_renderer.render_page(
        **present_error_page(
            runtime.template_renderer,
            title=title,
            detail=detail,
            status=status,
            action=action,
            active_nav=active_nav,
        )
    )


def _redirect_target(pattern: str, params: dict[str, str], request: Request) -> str:
    location = pattern
    for key, value in params.items():
        location = location.replace("{" + key + "}", value)
    query_values = {
        key: values
        for key, values in request.query.items()
        if values
    }
    if not query_values:
        return location
    return f"{location}?{urlencode(query_values, doseq=True)}"


def _register_legacy_redirect(router: Router, pattern: str, target_pattern: str) -> None:
    def legacy_redirect(request: Request):
        return redirect_response(_redirect_target(target_pattern, request.route_params, request))

    router.add(["GET", "POST"], pattern, legacy_redirect)


def app(
    database_path: str | Path = DB_PATH,
    source_root: str | Path = ROOT,
    *,
    allow_noncanonical_source_root: bool = False,
    allow_web_ingest_local_paths: bool = False,
) -> Callable:
    resolved_database_path = Path(database_path)
    resolved_source_root = prepare_operator_source_root(
        source_root,
        allow_noncanonical=allow_noncanonical_source_root,
    )
    runtime = WebRuntime(
        database_path=resolved_database_path,
        source_root=resolved_source_root,
        allow_web_ingest_local_paths=allow_web_ingest_local_paths,
        page_renderer=PageRenderer(Path(__file__).resolve().parent),
        taxonomies=load_taxonomies(),
    )
    router = Router()
    home.register(router, runtime)
    queue.register(router, runtime)
    objects.register(router, runtime)
    services.register(router, runtime)
    dashboard.register(router, runtime)
    impact.register(router, runtime)
    write.register(router, runtime)
    ingest.register(router, runtime)
    manage.register(router, runtime)

    legacy_redirects = (
        ("/", "/operator"),
        ("/queue", "/operator/read"),
        ("/read", "/operator/read"),
        ("/objects/{object_id}", "/operator/read/object/{object_id}"),
        ("/objects/{object_id}/revisions", "/operator/read/object/{object_id}/revisions"),
        ("/services", "/operator/read/services"),
        ("/services/{service_id}", "/operator/read/services/{service_id}"),
        ("/dashboard/trust", "/operator/review/governance"),
        ("/health", "/operator/review/governance"),
        ("/review", "/operator/review"),
        ("/manage/queue", "/operator/review"),
        ("/manage/objects/{object_id}/supersede", "/operator/review/object/{object_id}/supersede"),
        ("/manage/objects/{object_id}/archive", "/operator/review/object/{object_id}/archive"),
        ("/manage/objects/{object_id}/suspect", "/operator/review/object/{object_id}/suspect"),
        ("/manage/objects/{object_id}/evidence/revalidate", "/operator/review/object/{object_id}/evidence/revalidate"),
        ("/manage/reviews/{object_id}/{revision_id}/assign", "/operator/review/object/{object_id}/{revision_id}/assign"),
        ("/manage/reviews/{object_id}/{revision_id}", "/operator/review/object/{object_id}/{revision_id}"),
        ("/manage/audit", "/operator/review/activity"),
        ("/activity", "/operator/review/activity"),
        ("/manage/validation-runs", "/operator/review/validation-runs"),
        ("/manage/validation-runs/new", "/operator/review/validation-runs/new"),
        ("/impact/object/{object_id}", "/operator/review/impact/object/{object_id}"),
        ("/impact/service/{service_id}", "/operator/review/impact/service/{service_id}"),
        ("/write/objects/new", "/operator/write/new"),
        ("/write/objects/{object_id}/revisions/start", "/operator/write/object/{object_id}/start"),
        ("/write/objects/{object_id}/revisions/new", "/operator/write/object/{object_id}"),
        ("/write/objects/{object_id}/submit", "/operator/write/object/{object_id}/submit"),
        ("/write/citations/search", "/operator/write/citations/search"),
        ("/write/objects/search", "/operator/write/objects/search"),
        ("/ingest", "/operator/import"),
        ("/ingest/{ingestion_id}", "/operator/import/{ingestion_id}"),
        ("/ingest/{ingestion_id}/review", "/operator/import/{ingestion_id}/review"),
    )
    for pattern, target in legacy_redirects:
        _register_legacy_redirect(router, pattern, target)

    def application(environ, start_response):
        request = request_from_environ(environ)
        try:
            if request.path.startswith("/static/"):
                relative_path = request.path.removeprefix("/static/")
                asset = runtime.page_renderer.load_static_asset(relative_path)
                if asset is None:
                    return html_response(
                        _error_page(runtime, title="Asset not found", detail=f"No static asset for {request.path}", status="404", action="Refresh the page or verify the static asset path.", active_nav="manage"),
                        status="404 Not Found",
                    ).as_wsgi(start_response)
                return static_response(asset[0], asset[1]).as_wsgi(start_response)

            matched_route = router.match(request)
            if matched_route is None:
                return html_response(
                    _error_page(runtime, title="Not found", detail=f"No route for {request.path}", status="404", action="Check the Papyrus route and try again.", active_nav="manage"),
                    status="404 Not Found",
                ).as_wsgi(start_response)
            route = matched_route.route
            routed_request = matched_route.request
            if route.methods == ("__method_not_allowed__",):
                return html_response(
                    _error_page(runtime, title="Method not allowed", detail="Use the supported GET or POST workflow for this route.", status="405", action="Retry with the documented method for this screen.", active_nav="manage"),
                    status="405 Method Not Allowed",
                ).as_wsgi(start_response)
            response = route.handler(routed_request)
            return response.as_wsgi(start_response)
        except RoleAccessDeniedError:
            return html_response(
                _error_page(runtime, title="Not found", detail="No route for this role and path.", status="404", action="Use the role-scoped navigation and try again.", active_nav="home"),
                status="404 Not Found",
            ).as_wsgi(start_response)
        except RuntimeUnavailableError as exc:
            log_event(LOGGER, logging.ERROR, "web_runtime_unavailable", path=request.path, error=str(exc))
            return html_response(
                _error_page(runtime, title="Runtime unavailable", detail=str(exc), status="503", action="Run `python3 scripts/build_index.py` and reload the page.", active_nav="manage"),
                status="503 Service Unavailable",
            ).as_wsgi(start_response)
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            log_event(LOGGER, logging.ERROR, "web_resource_not_found", path=request.path, error=str(exc))
            return html_response(
                _error_page(runtime, title="Not found", detail=str(exc), status="404", action="Verify the object, revision, or service identifier.", active_nav="manage"),
                status="404 Not Found",
            ).as_wsgi(start_response)
        except ValueError as exc:
            log_event(LOGGER, logging.ERROR, "web_request_rejected", path=request.path, error=str(exc))
            return html_response(
                _error_page(runtime, title="Request rejected", detail=str(exc), status="400", action="Correct the form input or workflow state and try again.", active_nav="manage"),
                status="400 Bad Request",
            ).as_wsgi(start_response)
        except Exception:  # pragma: no cover
            log_event(LOGGER, logging.ERROR, "web_internal_error", path=request.path)
            return html_response(
                _error_page(runtime, title="Internal error", detail="Papyrus could not complete the request safely.", status="500", action="Retry the action. If it persists, inspect local server logs and the audit trail.", active_nav="manage"),
                status="500 Internal Server Error",
            ).as_wsgi(start_response)

    return application


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Papyrus operator web interface over WSGI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8080, help="Bind port. Defaults to 8080.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    parser.add_argument("--source-root", default=str(ROOT), help="Canonical source root for governed writeback.")
    parser.add_argument(
        "--allow-noncanonical-source-root",
        action="store_true",
        help="Allow a non-repository source root for advanced sandbox or demo use.",
    )
    parser.add_argument(
        "--allow-web-ingest-local-paths",
        action="store_true",
        help="Allow the /ingest web form to read an absolute local file path from the machine running Papyrus.",
    )
    args = parser.parse_args()

    try:
        application = app(
            args.db,
            args.source_root,
            allow_noncanonical_source_root=args.allow_noncanonical_source_root,
            allow_web_ingest_local_paths=args.allow_web_ingest_local_paths,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    with make_server(args.host, args.port, application) as server:
        print(f"Papyrus web interface listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0
