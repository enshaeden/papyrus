from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Protocol

from papyrus.application.role_visibility import role_meets_minimum
from papyrus.interfaces.web.routes import (
    admin,
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
    minimum_visible_role: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class RouteRegistrar(Protocol):
    def add(
        self,
        methods: list[str],
        pattern: str,
        handler: Callable[[object], object],
        *,
        minimum_visible_role: str,
    ) -> None: ...


@dataclass(frozen=True)
class ShellNavItem:
    key: str
    label: str
    href: str
    minimum_visible_role: str
    section: str
    section_label: str
    match_prefixes: tuple[str, ...] | None = None


_SHELL_NAV_ITEMS: tuple[ShellNavItem, ...] = (
    ShellNavItem(
        key="read",
        label="Read",
        href="/read",
        minimum_visible_role="reader",
        section="knowledge",
        section_label="Knowledge",
        match_prefixes=("/read",),
    ),
    ShellNavItem(
        key="write",
        label="Write",
        href="/write/new",
        minimum_visible_role="operator",
        section="operations",
        section_label="Operations",
        match_prefixes=("/write",),
    ),
    ShellNavItem(
        key="import",
        label="Import",
        href="/import",
        minimum_visible_role="operator",
        section="operations",
        section_label="Operations",
        match_prefixes=("/import",),
    ),
    ShellNavItem(
        key="review",
        label="Review",
        href="/review",
        minimum_visible_role="operator",
        section="operations",
        section_label="Operations",
        match_prefixes=("/review",),
    ),
    ShellNavItem(
        key="governance",
        label="Governance",
        href="/governance",
        minimum_visible_role="operator",
        section="governed-context",
        section_label="Governed Context",
        match_prefixes=("/governance",),
    ),
    ShellNavItem(
        key="services",
        label="Services",
        href="/governance/services",
        minimum_visible_role="operator",
        section="governed-context",
        section_label="Governed Context",
        match_prefixes=("/governance/services",),
    ),
    ShellNavItem(
        key="activity",
        label="Activity",
        href="/review/activity",
        minimum_visible_role="operator",
        section="governed-context",
        section_label="Governed Context",
        match_prefixes=("/review/activity", "/review/validation-runs"),
    ),
    ShellNavItem(
        key="activity",
        label="Audit",
        href="/admin/audit",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/audit",),
    ),
    ShellNavItem(
        key="overview",
        label="Overview",
        href="/admin/overview",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/overview",),
    ),
    ShellNavItem(
        key="users",
        label="Users",
        href="/admin/users",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/users",),
    ),
    ShellNavItem(
        key="access",
        label="Access",
        href="/admin/access",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/access",),
    ),
    ShellNavItem(
        key="spaces",
        label="Spaces",
        href="/admin/spaces",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/spaces",),
    ),
    ShellNavItem(
        key="templates",
        label="Templates",
        href="/admin/templates",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/templates",),
    ),
    ShellNavItem(
        key="schemas",
        label="Schemas",
        href="/admin/schemas",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/schemas",),
    ),
    ShellNavItem(
        key="settings",
        label="Settings",
        href="/admin/settings",
        minimum_visible_role="admin",
        section="admin-control",
        section_label="Admin Control",
        match_prefixes=("/admin/settings",),
    ),
)


def register_all_routes(router: RouteRegistrar, runtime: object) -> None:
    home.register(router, runtime)
    admin.register(router, runtime)
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

    def add(
        self,
        methods: list[str],
        pattern: str,
        handler: Callable[[object], object],
        *,
        minimum_visible_role: str,
    ) -> None:
        self.routes.append(
            RegisteredRoute(
                methods=tuple(methods),
                pattern=pattern,
                handler_module=handler.__module__,
                handler_name=handler.__name__,
                minimum_visible_role=minimum_visible_role,
            )
        )


def collect_registered_routes() -> tuple[RegisteredRoute, ...]:
    router = _CatalogRouter()
    register_all_routes(router, runtime=object())
    return tuple(router.routes)


def collect_shell_nav_items(*, role: str) -> tuple[ShellNavItem, ...]:
    return tuple(
        item for item in _SHELL_NAV_ITEMS if role_meets_minimum(role, item.minimum_visible_role)
    )
