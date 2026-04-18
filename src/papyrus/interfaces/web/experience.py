from __future__ import annotations

from dataclasses import dataclass

from papyrus.application.role_visibility import (
    ADMIN_ROLE,
    OPERATOR_ROLE,
    READER_ROLE,
    normalize_role,
    role_meets_minimum,
)


class RoleAccessDeniedError(Exception):
    pass


@dataclass(frozen=True)
class ShellLink:
    key: str
    label: str
    href: str
    match_prefixes: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ShellSection:
    title: str
    description: str
    items: tuple[ShellLink, ...]


@dataclass(frozen=True)
class ExperiencePageBehavior:
    page_id: str
    mode: str
    density: str = "comfortable"
    columns: str = "single"
    show_context_rail: bool = False
    allowed_secondary_sections: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShellPageConfig:
    page_id: str
    shell_variant: str = "normal"
    header_variant: str = "compact"
    show_quick_links: bool = False


@dataclass(frozen=True)
class ExperienceContext:
    role: str
    label: str
    home_path: str
    shell_summary: str
    nav_sections: tuple[ShellSection, ...]
    page_behaviors: tuple[ExperiencePageBehavior, ...]
    page_configs: tuple[ShellPageConfig, ...]
    quick_links: tuple[ShellLink, ...] = ()

    def page_behavior(self, page_id: str) -> ExperiencePageBehavior | None:
        normalized_page_id = str(page_id).strip()
        for behavior in self.page_behaviors:
            if behavior.page_id == normalized_page_id:
                return behavior
        return None

    def page_config(self, page_id: str) -> ShellPageConfig:
        normalized_page_id = str(page_id).strip()
        for config in self.page_configs:
            if config.page_id == normalized_page_id:
                return config
        return ShellPageConfig(page_id=normalized_page_id or "default")


def _page_configs(
    *page_ids: str, shell_variant: str = "normal", header_variant: str = "compact"
) -> tuple[ShellPageConfig, ...]:
    return tuple(
        ShellPageConfig(
            page_id=page_id,
            shell_variant=shell_variant,
            header_variant=header_variant,
        )
        for page_id in page_ids
    )


READER_EXPERIENCE = ExperienceContext(
    role=READER_ROLE,
    label="Reader",
    home_path="/read",
    shell_summary="Open dependable content without operator controls.",
    nav_sections=(
        ShellSection(
            title="Knowledge",
            description="Open dependable content and content-first object views.",
            items=(ShellLink("read", "Read", "/read", match_prefixes=("/read",)),),
        ),
    ),
    page_behaviors=(
        ExperiencePageBehavior(
            "read-queue", mode="library", density="comfortable", columns="single"
        ),
        ExperiencePageBehavior(
            "object-detail",
            mode="document",
            density="comfortable",
            columns="article",
            allowed_secondary_sections=("governance",),
        ),
    ),
    page_configs=_page_configs("read-queue", "object-detail"),
)

OPERATOR_EXPERIENCE = ExperienceContext(
    role=OPERATOR_ROLE,
    label="Operator",
    home_path="/review",
    shell_summary="Use dependable content first, then author, review, and oversee backend knowledge work.",
    nav_sections=(
        ShellSection(
            title="Core modes",
            description="Read dependable guidance first, then move into writing, import, or review only when the work truly branches.",
            items=(
                ShellLink("read", "Read", "/read", match_prefixes=("/read",)),
                ShellLink("write", "Write", "/write/new", match_prefixes=("/write",)),
                ShellLink("import", "Import", "/import", match_prefixes=("/import",)),
                ShellLink("review", "Review", "/review", match_prefixes=("/review",)),
            ),
        ),
        ShellSection(
            title="Context",
            description="Open broader portfolio context only when the active mode needs a wider health, service, or activity view.",
            items=(
                ShellLink(
                    "governance",
                    "Governance",
                    "/governance",
                    match_prefixes=("/governance",),
                ),
                ShellLink(
                    "services",
                    "Services",
                    "/governance/services",
                    match_prefixes=("/governance/services",),
                ),
                ShellLink(
                    "activity",
                    "Activity",
                    "/review/activity",
                    match_prefixes=(
                        "/review/activity",
                        "/review/validation-runs",
                    ),
                ),
            ),
        ),
    ),
    page_behaviors=(
        ExperiencePageBehavior(
            "read-queue", mode="article-first", density="comfortable", columns="single"
        ),
        ExperiencePageBehavior(
            "object-detail",
            mode="article-first",
            density="comfortable",
            columns="article",
            allowed_secondary_sections=("governance", "evidence", "source"),
        ),
        ExperiencePageBehavior(
            "review",
            mode="review-workbench",
            density="dense",
            columns="wide",
            show_context_rail=True,
        ),
        ExperiencePageBehavior(
            "governance",
            mode="review-oversight",
            density="dense",
            columns="wide",
            show_context_rail=True,
        ),
        ExperiencePageBehavior("activity", mode="history-feed", density="medium", columns="wide"),
        ExperiencePageBehavior("services", mode="entry-map", density="comfortable", columns="wide"),
    ),
    page_configs=(
        *_page_configs(
            "read-queue",
            "object-detail",
            "services",
            "review",
            "governance",
            "activity",
        ),
        *_page_configs("impact-object", "impact-service"),
        *_page_configs("revision-history", header_variant="compact"),
    ),
)

ADMIN_EXPERIENCE = ExperienceContext(
    role=ADMIN_ROLE,
    label="Admin",
    home_path="/admin/overview",
    shell_summary="Use the control-plane subset for content oversight, service impact, and audit inspection.",
    nav_sections=(
        ShellSection(
            title="Shared work",
            description="Admin sees the shared product routes plus stronger control surfaces.",
            items=(
                ShellLink("read", "Read", "/read", match_prefixes=("/read",)),
                ShellLink("write", "Write", "/write/new", match_prefixes=("/write",)),
                ShellLink("import", "Import", "/import", match_prefixes=("/import",)),
                ShellLink("review", "Review", "/review", match_prefixes=("/review",)),
                ShellLink(
                    "governance",
                    "Governance",
                    "/governance",
                    match_prefixes=("/governance",),
                ),
                ShellLink(
                    "services",
                    "Services",
                    "/governance/services",
                    match_prefixes=("/governance/services",),
                ),
                ShellLink(
                    "activity",
                    "Audit",
                    "/admin/audit",
                    match_prefixes=("/admin/audit", "/review/activity", "/review/validation-runs"),
                ),
            ),
        ),
        ShellSection(
            title="Admin control plane",
            description="Control access, spaces, governed definitions, and system settings.",
            items=(
                ShellLink("overview", "Overview", "/admin/overview", match_prefixes=("/admin/overview",)),
                ShellLink("users", "Users", "/admin/users", match_prefixes=("/admin/users",)),
                ShellLink("access", "Access", "/admin/access", match_prefixes=("/admin/access",)),
                ShellLink("spaces", "Spaces", "/admin/spaces", match_prefixes=("/admin/spaces",)),
                ShellLink(
                    "templates", "Templates", "/admin/templates", match_prefixes=("/admin/templates",)
                ),
                ShellLink("schemas", "Schemas", "/admin/schemas", match_prefixes=("/admin/schemas",)),
                ShellLink("settings", "Settings", "/admin/settings", match_prefixes=("/admin/settings",)),
            ),
        ),
    ),
    page_behaviors=(
        ExperiencePageBehavior("overview", mode="control-room", density="dense", columns="wide"),
        ExperiencePageBehavior(
            "read-queue",
            mode="triage-workbench",
            density="dense",
            columns="split",
            show_context_rail=True,
        ),
        ExperiencePageBehavior(
            "object-detail",
            mode="inspection-workbench",
            density="medium",
            columns="article-supporting",
            show_context_rail=True,
            allowed_secondary_sections=("governance", "evidence", "audit", "source"),
        ),
        ExperiencePageBehavior(
            "review", mode="control-review", density="dense", columns="wide", show_context_rail=True
        ),
        ExperiencePageBehavior(
            "governance",
            mode="control-oversight",
            density="dense",
            columns="wide",
            show_context_rail=True,
        ),
        ExperiencePageBehavior("activity", mode="audit-feed", density="medium", columns="wide"),
        ExperiencePageBehavior(
            "services", mode="service-oversight", density="comfortable", columns="wide"
        ),
    ),
    page_configs=(
        *_page_configs(
            "overview",
            "read-queue",
            "object-detail",
            "services",
            "review",
            "governance",
            "activity",
            "users",
            "access",
            "spaces",
            "templates",
            "schemas",
            "settings",
        ),
        *_page_configs("impact-object", "impact-service"),
        *_page_configs("revision-history", header_variant="compact"),
    ),
)

_EXPERIENCES_BY_ROLE = {
    READER_ROLE: READER_EXPERIENCE,
    OPERATOR_ROLE: OPERATOR_EXPERIENCE,
    ADMIN_ROLE: ADMIN_EXPERIENCE,
}


def experience_for_role(role: str | None = None) -> ExperienceContext:
    return _EXPERIENCES_BY_ROLE[normalize_role(role)]


def experience_for_request(request) -> ExperienceContext:
    return experience_for_role(request.role_id)


def require_experience(request, *allowed_roles: str) -> ExperienceContext:
    experience = experience_for_request(request)
    normalized_allowed = {normalize_role(role) for role in allowed_roles}
    if normalized_allowed and not any(
        role_meets_minimum(experience.role, role) for role in normalized_allowed
    ):
        raise RoleAccessDeniedError(f"route denied for role {experience.role}")
    return experience
