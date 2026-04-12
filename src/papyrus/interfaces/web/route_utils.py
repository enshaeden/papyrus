from __future__ import annotations

from dataclasses import dataclass

from papyrus.domain.actor import Actor, ActorPageBehavior, actor_registry, default_actor_id, resolve_actor


@dataclass(frozen=True)
class ShellLink:
    key: str
    label: str
    href: str
    match_prefixes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShellSection:
    title: str
    description: str
    items: tuple[ShellLink, ...]


@dataclass(frozen=True)
class ShellPageConfig:
    page_id: str
    shell_variant: str = "normal"
    header_variant: str = "compact"
    sidebar_mode: str = "global"
    show_quick_links: bool = False


@dataclass(frozen=True)
class ActorShellConfig:
    actor: Actor
    home_path: str
    nav_sections: tuple[ShellSection, ...]
    quick_links: tuple[ShellLink, ...]
    page_configs: tuple[ShellPageConfig, ...]
    banner_summary: str = ""

    def page_behavior(self, page_id: str) -> ActorPageBehavior | None:
        return self.actor.page_behavior(page_id)

    def page_config(self, page_id: str) -> ShellPageConfig:
        normalized_page_id = str(page_id).strip()
        for config in self.page_configs:
            if config.page_id == normalized_page_id:
                return config
        return ShellPageConfig(page_id=normalized_page_id or "default")


DEFAULT_WEB_ACTOR = resolve_actor(default_actor_id())
HOME_LINK = ShellLink("home", "Home", "/", match_prefixes=("/",))
READ_LINK = ShellLink("read", "Read", "/read", match_prefixes=("/read", "/queue", "/objects/"))
WRITE_LINK = ShellLink("write", "Write", "/write/objects/new", match_prefixes=("/write/",))
INGEST_LINK = ShellLink("import", "Import", "/ingest", match_prefixes=("/ingest",))
REVIEW_LINK = ShellLink("review", "Review / Approvals", "/review", match_prefixes=("/review", "/manage/queue", "/manage/reviews/"))
TRUST_LINK = ShellLink("health", "Knowledge Health", "/health", match_prefixes=("/health", "/dashboard/trust", "/manage/objects/", "/impact/"))
SERVICES_LINK = ShellLink("services", "Services", "/services", match_prefixes=("/services",))
AUDIT_LINK = ShellLink("activity", "Activity / History", "/activity", match_prefixes=("/activity", "/manage/audit", "/manage/validation-runs"))


def _page_configs(*page_ids: str, shell_variant: str = "normal", header_variant: str = "compact") -> tuple[ShellPageConfig, ...]:
    return tuple(
        ShellPageConfig(
            page_id=page_id,
            shell_variant=shell_variant,
            header_variant=header_variant,
        )
        for page_id in page_ids
    )


WEB_ACTOR_SHELLS = (
    ActorShellConfig(
        actor=DEFAULT_WEB_ACTOR,
        home_path=DEFAULT_WEB_ACTOR.landing_path,
        banner_summary="Use current guidance, update gaps, and keep work moving safely.",
        nav_sections=(
            ShellSection(
                title="Operator flow",
                description="Read first, write when guidance is missing, and keep governance in support of the task.",
                items=(HOME_LINK, READ_LINK, WRITE_LINK, SERVICES_LINK, REVIEW_LINK, TRUST_LINK, AUDIT_LINK),
            ),
        ),
        quick_links=(),
        page_configs=_page_configs("home", "read-queue", "object-detail", "services", "review", "knowledge-health", "activity"),
    ),
    ActorShellConfig(
        actor=resolve_actor("local.reviewer"),
        home_path=resolve_actor("local.reviewer").landing_path,
        banner_summary="Steward submitted revisions and block weak guidance from slipping through.",
        nav_sections=(
            ShellSection(
                title="Reviewer flow",
                description="Prioritise decisions, blocked reviews, and exceptions before broad browsing.",
                items=(HOME_LINK, REVIEW_LINK, TRUST_LINK, AUDIT_LINK, READ_LINK, SERVICES_LINK, WRITE_LINK, INGEST_LINK),
            ),
        ),
        quick_links=(),
        page_configs=_page_configs("home", "read-queue", "object-detail", "review", "knowledge-health", "services", "activity"),
    ),
    ActorShellConfig(
        actor=resolve_actor("local.manager"),
        home_path=resolve_actor("local.manager").landing_path,
        banner_summary="Steward risk, review pressure, and change impact.",
        nav_sections=(
            ShellSection(
                title="Manager flow",
                description="Start from portfolio pressure, then drill into service, review, or consequence surfaces.",
                items=(HOME_LINK, TRUST_LINK, REVIEW_LINK, SERVICES_LINK, AUDIT_LINK, READ_LINK, WRITE_LINK, INGEST_LINK),
            ),
        ),
        quick_links=(),
        page_configs=_page_configs("home", "read-queue", "object-detail", "knowledge-health", "review", "services", "activity"),
    ),
)
WEB_ACTOR_OPTIONS = actor_registry()
_WEB_ACTOR_SHELLS_BY_ID = {config.actor.actor_id: config for config in WEB_ACTOR_SHELLS}


def flash_html_for_request(runtime, request) -> str:
    from papyrus.interfaces.web.presenters.form_presenter import FormPresenter

    presenter = FormPresenter(runtime.template_renderer)
    notice = request.query_value("notice").strip()
    if notice:
        return presenter.flash(title="Success", body=notice, tone="success")
    error = request.query_value("error").strip()
    if error:
        return presenter.flash(title="Attention", body=error, tone="warning")
    return ""


def actor_shell_for_id(actor_id: str) -> ActorShellConfig:
    return _WEB_ACTOR_SHELLS_BY_ID.get(str(actor_id).strip(), _WEB_ACTOR_SHELLS_BY_ID[DEFAULT_WEB_ACTOR.actor_id])


def actor_shell_for_request(request) -> ActorShellConfig:
    return actor_shell_for_id(actor_for_request(request))


def actor_home_path(actor_id: str) -> str:
    return actor_shell_for_id(actor_id).home_path


def actor_page_behavior(actor_id: str, page_id: str) -> ActorPageBehavior | None:
    return actor_shell_for_id(actor_id).page_behavior(page_id)


def actor_page_config(actor_id: str, page_id: str) -> ShellPageConfig:
    return actor_shell_for_id(actor_id).page_config(page_id)


def actor_for_request(request) -> str:
    actor = request.cookie_value("papyrus_actor", default_actor_id()).strip()
    return actor_shell_for_id(actor).actor.actor_id
