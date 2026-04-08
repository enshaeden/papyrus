from __future__ import annotations

from dataclasses import dataclass

from papyrus.domain.actor import Actor


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


DEFAULT_WEB_ACTOR = Actor(actor_id="local.operator", display_name="Local Operator", role_hint="operator")
READ_LINK = ShellLink("read", "Knowledge Queue", "/queue", match_prefixes=("/queue", "/objects/"))
WRITE_LINK = ShellLink("write", "Write Draft", "/write/objects/new", match_prefixes=("/write/",))
REVIEW_LINK = ShellLink("review", "Review Queue", "/manage/queue", match_prefixes=("/manage/queue", "/manage/reviews/"))
TRUST_LINK = ShellLink("manage", "Trust Dashboard", "/dashboard/trust", match_prefixes=("/dashboard/trust", "/manage/objects/"))
SERVICES_LINK = ShellLink("services", "Services", "/services", match_prefixes=("/services",))
VALIDATION_LINK = ShellLink("validation", "Validation Runs", "/manage/validation-runs", match_prefixes=("/manage/validation-runs",))
AUDIT_LINK = ShellLink("audit", "Audit Trail", "/manage/audit", match_prefixes=("/manage/audit",))

WEB_ACTOR_SHELLS = (
    ActorShellConfig(
        actor=DEFAULT_WEB_ACTOR,
        home_path="/queue",
        summary="Read approved guidance, inspect service context, and draft updates when frontline work exposes a gap.",
        nav_sections=(
            ShellSection(
                title="Frontline Read",
                description="Start with trusted knowledge and service context.",
                items=(READ_LINK, SERVICES_LINK),
            ),
            ShellSection(
                title="Authoring",
                description="Create or extend governed knowledge when the queue exposes a gap.",
                items=(WRITE_LINK,),
            ),
        ),
        quick_links=(READ_LINK, SERVICES_LINK, WRITE_LINK),
    ),
    ActorShellConfig(
        actor=Actor(actor_id="local.reviewer", display_name="Local Reviewer", role_hint="reviewer"),
        home_path="/manage/queue",
        summary="Inspect submitted revisions, verify evidence posture, and record review decisions with explicit audit context.",
        nav_sections=(
            ShellSection(
                title="Review Workflow",
                description="Prioritize in-review items before broader governance work.",
                items=(REVIEW_LINK, TRUST_LINK),
            ),
            ShellSection(
                title="Evidence Checks",
                description="Keep validation history and audit evidence close to each decision.",
                items=(VALIDATION_LINK, AUDIT_LINK),
            ),
        ),
        quick_links=(REVIEW_LINK, TRUST_LINK, VALIDATION_LINK),
    ),
    ActorShellConfig(
        actor=Actor(actor_id="local.manager", display_name="Local Manager", role_hint="approver"),
        home_path="/dashboard/trust",
        summary="Oversee trust posture, workload, and governance signals across the corpus without dropping into authoring first.",
        nav_sections=(
            ShellSection(
                title="Corpus Oversight",
                description="Track trust, queue pressure, and governance events across the whole system.",
                items=(TRUST_LINK, REVIEW_LINK, AUDIT_LINK),
            ),
            ShellSection(
                title="Operational Controls",
                description="Inspect supporting service and validation posture when escalation is needed.",
                items=(VALIDATION_LINK, SERVICES_LINK),
            ),
        ),
        quick_links=(TRUST_LINK, REVIEW_LINK, AUDIT_LINK),
    ),
    ActorShellConfig(
        actor=Actor(actor_id="papyrus-demo", display_name="Papyrus Demo", role_hint="demo"),
        home_path="/dashboard/trust",
        summary="Walk the strongest demo paths first: trust posture, queue signals, and governed review flow.",
        nav_sections=(
            ShellSection(
                title="Demo Tour",
                description="Use the highest-signal screens for a fast product walkthrough.",
                items=(TRUST_LINK, READ_LINK, SERVICES_LINK),
            ),
            ShellSection(
                title="Governance Tour",
                description="Show how review and audit evidence stay attached to operational knowledge.",
                items=(REVIEW_LINK, AUDIT_LINK),
            ),
        ),
        quick_links=(TRUST_LINK, READ_LINK, REVIEW_LINK),
    ),
)
WEB_ACTOR_OPTIONS = tuple(config.actor for config in WEB_ACTOR_SHELLS)
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
    actor = request.cookie_value("papyrus_actor", DEFAULT_WEB_ACTOR.actor_id).strip()
    return actor_shell_for_id(actor).actor.actor_id
