from __future__ import annotations

from dataclasses import dataclass

from papyrus.application.role_visibility import (
    ADMIN_ROLE,
    OPERATOR_ROLE,
    READER_ROLE,
    normalize_role,
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
    route_prefix: str
    home_path: str
    shell_summary: str
    audit_actor_id: str | None
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
    route_prefix="/reader",
    home_path="/reader/browse",
    shell_summary="Read current guidance without governance-heavy control surfaces.",
    audit_actor_id=None,
    nav_sections=(
        ShellSection(
            title="Knowledge",
            description="Browse current guidance and open content-first object views.",
            items=(ShellLink("read", "Browse", "/reader/browse", match_prefixes=("/reader",)),),
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
    route_prefix="/operator",
    home_path="/operator",
    shell_summary="Work the current guidance, draft, import, review, and follow-up surfaces safely.",
    audit_actor_id="local.operator",
    nav_sections=(
        ShellSection(
            title="Operator workflow",
            description="Read first, write only when guidance is missing, and keep governance tied to the current task.",
            items=(
                ShellLink("home", "Home", "/operator", match_prefixes=()),
                ShellLink("read", "Read", "/operator/read", match_prefixes=("/operator/read",)),
                ShellLink(
                    "write", "Write", "/operator/write/new", match_prefixes=("/operator/write",)
                ),
                ShellLink(
                    "import", "Import", "/operator/import", match_prefixes=("/operator/import",)
                ),
                ShellLink(
                    "review",
                    "Review / Approvals",
                    "/operator/review",
                    match_prefixes=("/operator/review",),
                ),
                ShellLink(
                    "health",
                    "Knowledge Health",
                    "/operator/review/governance",
                    match_prefixes=("/operator/review/governance", "/operator/review/impact"),
                ),
                ShellLink(
                    "services",
                    "Services",
                    "/operator/read/services",
                    match_prefixes=("/operator/read/services",),
                ),
                ShellLink(
                    "activity",
                    "Activity / History",
                    "/operator/review/activity",
                    match_prefixes=(
                        "/operator/review/activity",
                        "/operator/review/validation-runs",
                    ),
                ),
            ),
        ),
    ),
    page_behaviors=(
        ExperiencePageBehavior("home", mode="launchpad", density="comfortable", columns="single"),
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
            "knowledge-health",
            mode="review-stewardship",
            density="dense",
            columns="wide",
            show_context_rail=True,
        ),
        ExperiencePageBehavior(
            "activity", mode="consequence-feed", density="medium", columns="wide"
        ),
        ExperiencePageBehavior("services", mode="entry-map", density="comfortable", columns="wide"),
    ),
    page_configs=(
        *_page_configs(
            "home",
            "read-queue",
            "object-detail",
            "services",
            "review",
            "knowledge-health",
            "activity",
        ),
        *_page_configs("impact-object", "impact-service"),
        *_page_configs("revision-history", header_variant="compact"),
    ),
)

ADMIN_EXPERIENCE = ExperienceContext(
    role=ADMIN_ROLE,
    label="Admin",
    route_prefix="/admin",
    home_path="/admin/overview",
    shell_summary="Use the control-plane subset for oversight, governance, audit, and service impact inspection.",
    audit_actor_id="local.manager",
    nav_sections=(
        ShellSection(
            title="Admin control plane",
            description="Inspect oversight, approvals, governance pressure, service impact, and audit history without blending in operator authoring routes.",
            items=(
                ShellLink("home", "Overview", "/admin/overview", match_prefixes=()),
                ShellLink(
                    "inspect", "Inspect", "/admin/inspect", match_prefixes=("/admin/inspect",)
                ),
                ShellLink("review", "Review", "/admin/review", match_prefixes=("/admin/review",)),
                ShellLink(
                    "health",
                    "Governance",
                    "/admin/governance",
                    match_prefixes=("/admin/governance", "/admin/impact"),
                ),
                ShellLink(
                    "services", "Services", "/admin/services", match_prefixes=("/admin/services",)
                ),
                ShellLink(
                    "activity",
                    "Audit",
                    "/admin/audit",
                    match_prefixes=("/admin/audit", "/admin/validation-runs"),
                ),
            ),
        ),
    ),
    page_behaviors=(
        ExperiencePageBehavior("home", mode="control-room", density="dense", columns="wide"),
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
            "knowledge-health",
            mode="control-governance",
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
            "home",
            "read-queue",
            "object-detail",
            "services",
            "review",
            "knowledge-health",
            "activity",
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


def experience_for_path(path: str) -> ExperienceContext:
    normalized_path = str(path or "/").strip() or "/"
    if normalized_path == "/reader" or normalized_path.startswith("/reader/"):
        return READER_EXPERIENCE
    if normalized_path == "/admin" or normalized_path.startswith("/admin/"):
        return ADMIN_EXPERIENCE
    return OPERATOR_EXPERIENCE


def experience_for_request(request) -> ExperienceContext:
    return experience_for_path(request.path)


def require_experience(request, *allowed_roles: str) -> ExperienceContext:
    experience = experience_for_request(request)
    normalized_allowed = {normalize_role(role) for role in allowed_roles}
    if normalized_allowed and experience.role not in normalized_allowed:
        raise RoleAccessDeniedError(f"route denied for role {experience.role}")
    return experience
