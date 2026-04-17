from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote
from wsgiref.simple_server import make_server

from papyrus.application.queries import (
    KnowledgeObjectNotFoundError,
    RuntimeUnavailableError,
    ServiceNotFoundError,
)
from papyrus.application.role_visibility import (
    normalize_role,
    role_from_actor_id,
    role_meets_minimum,
)
from papyrus.application.workspace import WorkspaceSourceRequiredError
from papyrus.domain.actor import (
    default_actor_id as runtime_default_actor_id,
)
from papyrus.domain.actor import (
    default_actor_id_for_role,
    resolve_actor,
)
from papyrus.infrastructure.observability import get_logger, log_event
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies
from papyrus.interfaces.startup_guard import resolve_runtime_source_root
from papyrus.interfaces.web.experience import RoleAccessDeniedError
from papyrus.interfaces.web.http import (
    Request,
    html_response,
    request_from_environ,
    static_response,
)
from papyrus.interfaces.web.presenters.system_presenter import present_error_page
from papyrus.interfaces.web.rendering import PageRenderer
from papyrus.interfaces.web.route_catalog import register_all_routes
from papyrus.interfaces.web.runtime import WebRuntime

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class Route:
    methods: tuple[str, ...]
    pattern: str
    handler: Callable[[Request], object]
    minimum_visible_role: str


@dataclass(frozen=True)
class RouteMatch:
    route: Route
    request: Request


class Router:
    def __init__(self):
        self._routes: list[Route] = []

    def add(
        self,
        methods: list[str],
        pattern: str,
        handler: Callable[[Request], object],
        *,
        minimum_visible_role: str,
    ) -> None:
        self._routes.append(Route(tuple(methods), pattern, handler, minimum_visible_role))

    def match(self, request: Request) -> RouteMatch | None:
        for route in self._routes:
            params = match_pattern(route.pattern, request.path)
            if params is None:
                continue
            routed_request = request.with_route_params(params)
            if request.method not in route.methods:
                return RouteMatch(
                    Route(
                        ("__method_not_allowed__",),
                        route.pattern,
                        route.handler,
                        route.minimum_visible_role,
                    ),
                    routed_request,
                )
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
    for pattern_part, path_part in zip(pattern_parts, path_parts, strict=False):
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


def app(
    database_path: str | Path = DB_PATH,
    source_root: str | Path | None = None,
    allow_web_ingest_local_paths: bool = False,
    default_actor_id: str | None = None,
    default_role: str | None = None,
) -> Callable:
    resolved_database_path = Path(database_path)
    resolved_source_root = resolve_runtime_source_root(source_root)
    resolved_actor = resolve_actor(default_actor_id or default_actor_id_for_role(default_role or ""))
    resolved_actor_id = resolved_actor.actor_id or runtime_default_actor_id()
    resolved_role = normalize_role(default_role or role_from_actor_id(resolved_actor_id))
    runtime = WebRuntime(
        database_path=resolved_database_path,
        source_root=resolved_source_root,
        allow_web_ingest_local_paths=allow_web_ingest_local_paths,
        page_renderer=PageRenderer(Path(__file__).resolve().parent),
        taxonomies=load_taxonomies(),
        default_actor_id=resolved_actor_id,
        default_role=resolved_role,
    )
    router = Router()
    register_all_routes(router, runtime)

    def application(environ, start_response):
        request = request_from_environ(environ).with_identity(
            actor_id=runtime.default_actor_id,
            role_id=runtime.default_role,
        )
        try:
            if request.path.startswith("/static/"):
                relative_path = request.path.removeprefix("/static/")
                asset = runtime.page_renderer.load_static_asset(relative_path)
                if asset is None:
                    return html_response(
                        _error_page(
                            runtime,
                            title="Asset not found",
                            detail=f"No static asset for {request.path}",
                            status="404",
                            action="Refresh the page or verify the static asset path.",
                            active_nav="manage",
                        ),
                        status="404 Not Found",
                    ).as_wsgi(start_response)
                return static_response(asset[0], asset[1]).as_wsgi(start_response)

            matched_route = router.match(request)
            if matched_route is None:
                return html_response(
                    _error_page(
                        runtime,
                        title="Not found",
                        detail=f"No route for {request.path}",
                        status="404",
                        action="Check the Papyrus route and try again.",
                        active_nav="manage",
                    ),
                    status="404 Not Found",
                ).as_wsgi(start_response)
            route = matched_route.route
            routed_request = matched_route.request
            if route.methods == ("__method_not_allowed__",):
                return html_response(
                    _error_page(
                        runtime,
                        title="Method not allowed",
                        detail="Use the supported GET or POST workflow for this route.",
                        status="405",
                        action="Retry with the documented method for this screen.",
                        active_nav="manage",
                    ),
                    status="405 Method Not Allowed",
                ).as_wsgi(start_response)
            if not role_meets_minimum(routed_request.role_id, route.minimum_visible_role):
                raise RoleAccessDeniedError(
                    f"route denied for role {routed_request.role_id} on {route.pattern}"
                )
            response = route.handler(routed_request)
            return response.as_wsgi(start_response)
        except RoleAccessDeniedError:
            return html_response(
                _error_page(
                    runtime,
                    title="Not found",
                    detail="No route for this role and path.",
                    status="404",
                    action="Use the role-scoped navigation and try again.",
                    active_nav="home",
                ),
                status="404 Not Found",
            ).as_wsgi(start_response)
        except RuntimeUnavailableError as exc:
            log_event(
                LOGGER, logging.ERROR, "web_runtime_unavailable", path=request.path, error=str(exc)
            )
            return html_response(
                _error_page(
                    runtime,
                    title="Runtime unavailable",
                    detail=str(exc),
                    status="503",
                    action="Run `python3 scripts/build_index.py --source-root /path/to/workspace` and reload the page.",
                    active_nav="manage",
                ),
                status="503 Service Unavailable",
            ).as_wsgi(start_response)
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError) as exc:
            log_event(
                LOGGER, logging.ERROR, "web_resource_not_found", path=request.path, error=str(exc)
            )
            return html_response(
                _error_page(
                    runtime,
                    title="Not found",
                    detail=str(exc),
                    status="404",
                    action="Verify the object, revision, or service identifier.",
                    active_nav="manage",
                ),
                status="404 Not Found",
            ).as_wsgi(start_response)
        except WorkspaceSourceRequiredError as exc:
            log_event(
                LOGGER, logging.ERROR, "web_workspace_required", path=request.path, error=str(exc)
            )
            return html_response(
                _error_page(
                    runtime,
                    title="Workspace source root required",
                    detail=str(exc),
                    status="409",
                    action="Retry this source-backed action with an explicit workspace source root.",
                    active_nav="manage",
                ),
                status="409 Conflict",
            ).as_wsgi(start_response)
        except ValueError as exc:
            log_event(
                LOGGER, logging.ERROR, "web_request_rejected", path=request.path, error=str(exc)
            )
            return html_response(
                _error_page(
                    runtime,
                    title="Request rejected",
                    detail=str(exc),
                    status="400",
                    action="Correct the form input or workflow state and try again.",
                    active_nav="manage",
                ),
                status="400 Bad Request",
            ).as_wsgi(start_response)
        except Exception:  # pragma: no cover
            log_event(LOGGER, logging.ERROR, "web_internal_error", path=request.path)
            return html_response(
                _error_page(
                    runtime,
                    title="Internal error",
                    detail="Papyrus could not complete the request safely.",
                    status="500",
                    action="Retry the action. If it persists, inspect local server logs and the audit trail.",
                    active_nav="manage",
                ),
                status="500 Internal Server Error",
            ).as_wsgi(start_response)

    return application


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Serve the Papyrus web interface over WSGI."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8080, help="Bind port. Defaults to 8080.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    parser.add_argument(
        "--source-root",
        default=None,
        help="Workspace source root for source-backed authoring, ingest, and writeback operations.",
    )
    parser.add_argument(
        "--allow-web-ingest-local-paths",
        action="store_true",
        help="Allow the /ingest web form to read an absolute local file path from the machine running Papyrus.",
    )
    identity = parser.add_mutually_exclusive_group()
    identity.add_argument(
        "--actor",
        default=None,
        help="Local actor id for the web runtime role context. Defaults to the local operator actor.",
    )
    identity.add_argument(
        "--role",
        default=None,
        help="Local role for the web runtime role context. Use reader, operator, or admin.",
    )
    args = parser.parse_args()

    application = app(
        args.db,
        args.source_root,
        allow_web_ingest_local_paths=args.allow_web_ingest_local_paths,
        default_actor_id=args.actor,
        default_role=args.role,
    )

    with make_server(args.host, args.port, application) as server:
        print(f"Papyrus web interface listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0
