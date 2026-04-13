from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol

from papyrus.interfaces.web.routes import (
    dashboard,
    home,
    impact,
    ingest,
    manage,
    objects,
    queue,
    services,
    write,
)


@dataclass(frozen=True)
class RegisteredRoute:
    methods: tuple[str, ...]
    pattern: str
    handler_module: str
    handler_name: str
    role_group: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class RouteRegistrar(Protocol):
    def add(
        self, methods: list[str], pattern: str, handler: Callable[[object], object]
    ) -> None: ...


def role_group_for_pattern(pattern: str) -> str:
    if pattern == "/":
        return "shared"
    if pattern == "/reader" or pattern.startswith("/reader/"):
        return "reader"
    if pattern == "/operator" or pattern.startswith("/operator/"):
        return "operator"
    if pattern == "/admin" or pattern.startswith("/admin/"):
        return "admin"
    return "shared"


def register_all_routes(router: RouteRegistrar, runtime: object) -> None:
    home.register(router, runtime)
    queue.register(router, runtime)
    objects.register(router, runtime)
    services.register(router, runtime)
    dashboard.register(router, runtime)
    impact.register(router, runtime)
    write.register(router, runtime)
    ingest.register(router, runtime)
    manage.register(router, runtime)


class _CatalogRouter:
    def __init__(self) -> None:
        self.routes: list[RegisteredRoute] = []

    def add(self, methods: list[str], pattern: str, handler: Callable[[object], object]) -> None:
        self.routes.append(
            RegisteredRoute(
                methods=tuple(methods),
                pattern=pattern,
                handler_module=handler.__module__,
                handler_name=handler.__name__,
                role_group=role_group_for_pattern(pattern),
            )
        )


def collect_registered_routes() -> tuple[RegisteredRoute, ...]:
    router = _CatalogRouter()
    register_all_routes(router, runtime=object())
    return tuple(router.routes)
