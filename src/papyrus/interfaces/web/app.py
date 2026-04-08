from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import unquote
from wsgiref.simple_server import make_server

from papyrus.application.queries import KnowledgeObjectNotFoundError, RuntimeUnavailableError, ServiceNotFoundError
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies
from papyrus.interfaces.web.http import Request, html_response, redirect_response, request_from_environ, static_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import PageRenderer
from papyrus.interfaces.web.runtime import WebRuntime
from papyrus.interfaces.web.routes import dashboard, impact, manage, objects, queue, services, write


@dataclass(frozen=True)
class Route:
    methods: tuple[str, ...]
    pattern: str
    handler: Callable[[Request], object]


class Router:
    def __init__(self):
        self._routes: list[Route] = []

    def add(self, methods: list[str], pattern: str, handler: Callable[[Request], object]) -> None:
        self._routes.append(Route(tuple(methods), pattern, handler))

    def match(self, request: Request) -> Route | None:
        for route in self._routes:
            params = match_pattern(route.pattern, request.path)
            if params is None:
                continue
            object.__setattr__(request, "route_params", params)
            if request.method not in route.methods:
                return Route(("__method_not_allowed__",), route.pattern, route.handler)
            return route
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


def _error_page(runtime: WebRuntime, *, title: str, detail: str, status: str, active_nav: str = "manage") -> str:
    components = ComponentPresenter(runtime.template_renderer)
    error_html = components.section_card(
        title=title,
        eyebrow="System",
        body_html=f"<p>{detail}</p><p class=\"section-footer\">HTTP status: {status}</p>",
        tone="danger" if status.startswith("5") else "default",
    )
    return runtime.page_renderer.render_page(
        page_template="pages/error.html",
        page_title=title,
        headline=title,
        kicker="System",
        intro="Papyrus keeps failures explicit so operators can diagnose state rather than guess.",
        active_nav=active_nav,
        aside_html="",
        page_context={"error_html": error_html},
    )


def app(database_path: str | Path = DB_PATH) -> Callable:
    resolved_database_path = Path(database_path)
    runtime = WebRuntime(
        database_path=resolved_database_path,
        page_renderer=PageRenderer(Path(__file__).resolve().parent),
        taxonomies=load_taxonomies(),
    )
    router = Router()
    queue.register(router, runtime)
    objects.register(router, runtime)
    services.register(router, runtime)
    dashboard.register(router, runtime)
    impact.register(router, runtime)
    write.register(router, runtime)
    manage.register(router, runtime)

    def application(environ, start_response):
        request = request_from_environ(environ)
        try:
            if request.path == "/":
                return redirect_response("/queue").as_wsgi(start_response)
            if request.path.startswith("/static/"):
                relative_path = request.path.removeprefix("/static/")
                asset = runtime.page_renderer.load_static_asset(relative_path)
                if asset is None:
                    return html_response(
                        _error_page(runtime, title="Asset not found", detail=f"No static asset for {request.path}", status="404", active_nav="manage"),
                        status="404 Not Found",
                    ).as_wsgi(start_response)
                return static_response(asset[0], asset[1]).as_wsgi(start_response)

            route = router.match(request)
            if route is None:
                return html_response(
                    _error_page(runtime, title="Not found", detail=f"No route for {request.path}", status="404", active_nav="manage"),
                    status="404 Not Found",
                ).as_wsgi(start_response)
            if route.methods == ("__method_not_allowed__",):
                return html_response(
                    _error_page(runtime, title="Method not allowed", detail="Use the supported GET or POST workflow for this route.", status="405", active_nav="manage"),
                    status="405 Method Not Allowed",
                ).as_wsgi(start_response)
            response = route.handler(request)
            return response.as_wsgi(start_response)
        except RuntimeUnavailableError as exc:
            return html_response(
                _error_page(runtime, title="Runtime unavailable", detail=str(exc), status="503", active_nav="manage"),
                status="503 Service Unavailable",
            ).as_wsgi(start_response)
        except (KnowledgeObjectNotFoundError, ServiceNotFoundError, ValueError) as exc:
            return html_response(
                _error_page(runtime, title="Not found", detail=str(exc), status="404", active_nav="manage"),
                status="404 Not Found",
            ).as_wsgi(start_response)
        except Exception as exc:  # pragma: no cover
            return html_response(
                _error_page(runtime, title="Internal error", detail=str(exc), status="500", active_nav="manage"),
                status="500 Internal Server Error",
            ).as_wsgi(start_response)

    return application


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the Papyrus operator web interface over WSGI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8080, help="Bind port. Defaults to 8080.")
    parser.add_argument("--db", default=str(DB_PATH), help="Runtime SQLite database path.")
    args = parser.parse_args()

    with make_server(args.host, args.port, app(args.db)) as server:
        print(f"Papyrus web interface listening on http://{args.host}:{args.port}")
        server.serve_forever()
    return 0
