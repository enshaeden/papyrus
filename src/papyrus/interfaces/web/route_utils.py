from __future__ import annotations

from dataclasses import dataclass

from papyrus.domain.actor import Actor, actor_registry, default_actor_id, resolve_actor


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
class ActorShellConfig:
    actor: Actor
    home_path: str
    summary: str
    nav_sections: tuple[ShellSection, ...]
    quick_links: tuple[ShellLink, ...]


DEFAULT_WEB_ACTOR = resolve_actor(default_actor_id())
READ_LINK = ShellLink("read", "Read", "/read", match_prefixes=("/read", "/queue", "/objects/"))
WRITE_LINK = ShellLink("write", "Write", "/write/objects/new", match_prefixes=("/write/",))
INGEST_LINK = ShellLink("import", "Import", "/ingest", match_prefixes=("/ingest",))
REVIEW_LINK = ShellLink("review", "Review / Approvals", "/review", match_prefixes=("/review", "/manage/queue", "/manage/reviews/"))
TRUST_LINK = ShellLink("health", "Knowledge Health", "/health", match_prefixes=("/health", "/dashboard/trust", "/manage/objects/", "/impact/"))
SERVICES_LINK = ShellLink("services", "Services", "/services", match_prefixes=("/services",))
AUDIT_LINK = ShellLink("activity", "Activity / History", "/activity", match_prefixes=("/activity", "/manage/audit", "/manage/validation-runs"))
LIFECYCLE_LINKS = (READ_LINK, WRITE_LINK, INGEST_LINK, REVIEW_LINK, TRUST_LINK, SERVICES_LINK, AUDIT_LINK)

WEB_ACTOR_SHELLS = (
    ActorShellConfig(
        actor=DEFAULT_WEB_ACTOR,
        home_path="/",
        summary="Use current guidance, revise gaps you find, and keep work moving through the next safe lifecycle step.",
        nav_sections=(
            ShellSection(
                title="Lifecycle",
                description="Move from use to revision, review, health checks, and history without leaving the operator shell.",
                items=LIFECYCLE_LINKS,
            ),
            ShellSection(
                title="Start Here",
                description="Frontline work starts with guided use and only pivots into authoring when the current guidance is not enough.",
                items=(READ_LINK, WRITE_LINK, INGEST_LINK, SERVICES_LINK),
            ),
        ),
        quick_links=(READ_LINK, WRITE_LINK, SERVICES_LINK),
    ),
    ActorShellConfig(
        actor=resolve_actor("local.reviewer"),
        home_path="/",
        summary="Steward submitted revisions, make explicit decisions, and keep weak evidence or stale guidance from reaching operators silently.",
        nav_sections=(
            ShellSection(
                title="Lifecycle",
                description="The same lifecycle frame stays visible while you move from review to health and activity history.",
                items=LIFECYCLE_LINKS,
            ),
            ShellSection(
                title="Start Here",
                description="Reviewers should begin with pending decisions, then fall back to health and activity for supporting context.",
                items=(REVIEW_LINK, TRUST_LINK, AUDIT_LINK),
            ),
        ),
        quick_links=(REVIEW_LINK, TRUST_LINK, AUDIT_LINK),
    ),
    ActorShellConfig(
        actor=resolve_actor("local.manager"),
        home_path="/",
        summary="Shepherd knowledge health, review pressure, and recent change consequences without dropping straight into raw queues.",
        nav_sections=(
            ShellSection(
                title="Lifecycle",
                description="Use the lifecycle map to move between operational use, stewardship decisions, and consequence history.",
                items=LIFECYCLE_LINKS,
            ),
            ShellSection(
                title="Start Here",
                description="Managers usually begin with health and review load, then drill into services and activity when risk is rising.",
                items=(TRUST_LINK, REVIEW_LINK, INGEST_LINK, AUDIT_LINK, SERVICES_LINK),
            ),
        ),
        quick_links=(TRUST_LINK, REVIEW_LINK, AUDIT_LINK),
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


def actor_for_request(request) -> str:
    actor = request.cookie_value("papyrus_actor", default_actor_id()).strip()
    return actor_shell_for_id(actor).actor.actor_id
