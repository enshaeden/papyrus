from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActorPageBehavior:
    page_id: str
    mode: str
    density: str = "comfortable"
    default_filters: tuple[tuple[str, str], ...] = ()
    primary_sections: tuple[str, ...] = ()
    secondary_sections: tuple[str, ...] = ()
    primary_actions: tuple[str, ...] = ()
    action_labels: tuple[tuple[str, str], ...] = ()
    columns: str = "single"
    show_context_rail: bool = False
    copy_style: str = "operational"
    emphasis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not str(self.page_id).strip():
            raise ValueError("page_id is required")
        if not str(self.mode).strip():
            raise ValueError("mode is required")

    def defaults(self) -> dict[str, str]:
        return {str(key): str(value) for key, value in self.default_filters}

    def label_for(self, action_id: str, fallback: str) -> str:
        return {str(key): str(value) for key, value in self.action_labels}.get(str(action_id), fallback)


@dataclass(frozen=True)
class Actor:
    actor_id: str
    display_name: str
    role_hint: str
    landing_path: str
    page_behaviors: tuple[ActorPageBehavior, ...]

    def __post_init__(self) -> None:
        actor_id = str(self.actor_id).strip()
        display_name = str(self.display_name).strip()
        role_hint = str(self.role_hint).strip()
        landing_path = str(self.landing_path).strip()
        if not actor_id:
            raise ValueError("actor_id is required")
        if not display_name:
            raise ValueError("display_name is required")
        if not role_hint:
            raise ValueError("role_hint is required")
        if not landing_path:
            raise ValueError("landing_path is required")

    def page_behavior(self, page_id: str) -> ActorPageBehavior | None:
        normalized_page_id = str(page_id).strip()
        for behavior in self.page_behaviors:
            if behavior.page_id == normalized_page_id:
                return behavior
        return None


def _page(
    page_id: str,
    *,
    mode: str,
    density: str,
    default_filters: tuple[tuple[str, str], ...] = (),
    primary_sections: tuple[str, ...] = (),
    secondary_sections: tuple[str, ...] = (),
    primary_actions: tuple[str, ...] = (),
    action_labels: tuple[tuple[str, str], ...] = (),
    columns: str = "single",
    show_context_rail: bool = False,
    copy_style: str = "operational",
    emphasis: tuple[str, ...] = (),
) -> ActorPageBehavior:
    return ActorPageBehavior(
        page_id=page_id,
        mode=mode,
        density=density,
        default_filters=default_filters,
        primary_sections=primary_sections,
        secondary_sections=secondary_sections,
        primary_actions=primary_actions,
        action_labels=action_labels,
        columns=columns,
        show_context_rail=show_context_rail,
        copy_style=copy_style,
        emphasis=emphasis,
    )


DEFAULT_LOCAL_ACTOR = Actor(
    actor_id="local.operator",
    display_name="Local Operator",
    role_hint="reader_writer",
    landing_path="/",
    page_behaviors=(
        _page(
            "home",
            mode="launchpad",
            density="comfortable",
            primary_sections=("do_now", "continue", "watch"),
            secondary_sections=("recent_activity",),
            primary_actions=("read", "write"),
            action_labels=(("read", "Read guidance"), ("write", "Start draft")),
            columns="single",
            emphasis=("today", "article-first"),
        ),
        _page(
            "read-queue",
            mode="article-first",
            density="comfortable",
            primary_sections=("search", "results"),
            secondary_sections=("watch",),
            primary_actions=("open_article", "start_draft"),
            action_labels=(("open", "Open article"),),
            columns="single",
            show_context_rail=False,
            emphasis=("relevance", "clarity"),
        ),
        _page(
            "object-detail",
            mode="article-first",
            density="comfortable",
            primary_sections=(
                "hero",
                "when_to_use",
                "scope",
                "guidance",
                "verification",
                "rollback",
                "escalation",
                "service_context",
            ),
            secondary_sections=("governance", "evidence", "source"),
            primary_actions=("revise", "history"),
            action_labels=(("revise", "Revise guidance"),),
            columns="article",
            show_context_rail=False,
            emphasis=("readability", "operator-flow"),
        ),
        _page(
            "review",
            mode="secondary-workbench",
            density="dense",
            primary_sections=("review_queue", "exceptions"),
            primary_actions=("review",),
            columns="wide",
            show_context_rail=False,
            copy_style="operational",
            emphasis=("handoff",),
        ),
        _page(
            "knowledge-health",
            mode="secondary-board",
            density="medium",
            primary_sections=("risk_board",),
            columns="wide",
            show_context_rail=False,
            emphasis=("supporting-context",),
        ),
        _page(
            "services",
            mode="entry-map",
            density="comfortable",
            primary_sections=("service_map", "paths"),
            columns="wide",
            show_context_rail=False,
            emphasis=("entry-points",),
        ),
        _page(
            "activity",
            mode="consequence-feed",
            density="medium",
            primary_sections=("activity_feed",),
            columns="wide",
            show_context_rail=False,
            emphasis=("what-changed",),
        ),
    ),
)
LOCAL_ACTORS: tuple[Actor, ...] = (
    DEFAULT_LOCAL_ACTOR,
    Actor(
        actor_id="local.reviewer",
        display_name="Local Reviewer",
        role_hint="reviewer",
        landing_path="/review",
        page_behaviors=(
            _page(
                "home",
                mode="review-launchpad",
                density="dense",
                primary_sections=("queue_status", "pending_decisions", "blocked_reviews"),
                secondary_sections=("trust_exceptions", "governance_consequences"),
                primary_actions=("review", "inspect_exceptions"),
                action_labels=(("review", "Work review queue"), ("inspect_exceptions", "Inspect exceptions")),
                columns="wide",
                show_context_rail=False,
                copy_style="review",
                emphasis=("decision-context", "exceptions"),
            ),
            _page(
                "read-queue",
                mode="triage-workbench",
                density="dense",
                primary_sections=("search", "triage_table"),
                secondary_sections=("selected_context",),
                primary_actions=("open", "review"),
                action_labels=(("open", "Inspect article"), ("review", "Open review context")),
                columns="split",
                show_context_rail=True,
                copy_style="review",
                emphasis=("triage", "decision-readiness"),
            ),
            _page(
                "object-detail",
                mode="article-with-review-context",
                density="medium",
                primary_sections=(
                    "hero",
                    "when_to_use",
                    "scope",
                    "guidance",
                    "verification",
                    "rollback",
                    "escalation",
                    "service_context",
                ),
                secondary_sections=("review_state", "evidence", "audit", "source"),
                primary_actions=("review", "revise"),
                action_labels=(("review", "Review revision"), ("revise", "Revise guidance")),
                columns="article-supporting",
                show_context_rail=True,
                copy_style="review",
                emphasis=("decision-context",),
            ),
            _page(
                "review",
                mode="review-workbench",
                density="dense",
                primary_sections=("review_queue", "decision_panels"),
                secondary_sections=("selected_context",),
                primary_actions=("assign", "decide"),
                columns="split",
                show_context_rail=True,
                copy_style="review",
                emphasis=("decision-speed", "exceptions"),
            ),
            _page(
                "knowledge-health",
                mode="review-stewardship-board",
                density="dense",
                primary_sections=("intervention_groups", "validation"),
                secondary_sections=("selected_context",),
                columns="split",
                show_context_rail=True,
                copy_style="review",
                emphasis=("trust-exceptions", "cleanup"),
            ),
            _page(
                "services",
                mode="service-map",
                density="medium",
                primary_sections=("service_map", "linked_guidance"),
                columns="wide",
                show_context_rail=False,
                copy_style="review",
                emphasis=("affected-guidance",),
            ),
            _page(
                "activity",
                mode="consequence-feed",
                density="dense",
                primary_sections=("activity_feed", "follow_up"),
                columns="wide",
                show_context_rail=False,
                copy_style="review",
                emphasis=("consequences", "audit"),
            ),
        ),
    ),
    Actor(
        actor_id="local.manager",
        display_name="Local Manager",
        role_hint="manager",
        landing_path="/health",
        page_behaviors=(
            _page(
                "home",
                mode="pressure-launchpad",
                density="portfolio",
                primary_sections=("risk_pressure", "review_pressure", "service_pressure", "cleanup_pressure"),
                secondary_sections=("portfolio_trends",),
                primary_actions=("health", "services", "activity"),
                action_labels=(("health", "Open risk board"), ("services", "Open service map")),
                columns="wide",
                show_context_rail=False,
                copy_style="manager",
                emphasis=("portfolio", "pressure"),
            ),
            _page(
                "read-queue",
                mode="portfolio-triage",
                density="dense",
                primary_sections=("search", "triage_table"),
                secondary_sections=("selected_context",),
                primary_actions=("open", "inspect_service"),
                action_labels=(("open", "Inspect article"),),
                columns="split",
                show_context_rail=True,
                copy_style="manager",
                emphasis=("risk", "service-context"),
            ),
            _page(
                "object-detail",
                mode="article-with-portfolio-context",
                density="medium",
                primary_sections=(
                    "hero",
                    "when_to_use",
                    "scope",
                    "guidance",
                    "verification",
                    "rollback",
                    "escalation",
                    "service_context",
                ),
                secondary_sections=("risk_context", "governance", "audit", "source"),
                primary_actions=("history", "services"),
                columns="article-supporting",
                show_context_rail=True,
                copy_style="manager",
                emphasis=("portfolio-risk",),
            ),
            _page(
                "review",
                mode="pressure-workbench",
                density="dense",
                primary_sections=("review_queue", "blocked_reviews", "service_impact"),
                secondary_sections=("selected_context",),
                columns="split",
                show_context_rail=True,
                copy_style="manager",
                emphasis=("throughput",),
            ),
            _page(
                "knowledge-health",
                mode="risk-board",
                density="dense",
                primary_sections=("risk_board", "cleanup_board", "validation"),
                secondary_sections=("selected_context",),
                primary_actions=("inspect",),
                columns="split",
                show_context_rail=True,
                copy_style="manager",
                emphasis=("portfolio-risk", "cleanup"),
            ),
            _page(
                "services",
                mode="service-map",
                density="medium",
                primary_sections=("service_map", "critical_paths"),
                secondary_sections=("risk_summary",),
                columns="wide",
                show_context_rail=False,
                copy_style="manager",
                emphasis=("criticality", "ownership"),
            ),
            _page(
                "activity",
                mode="consequence-feed",
                density="medium",
                primary_sections=("activity_feed", "portfolio_effect"),
                columns="wide",
                show_context_rail=False,
                copy_style="manager",
                emphasis=("portfolio-impact",),
            ),
        ),
    ),
)
_ACTORS_BY_ID = {actor.actor_id: actor for actor in LOCAL_ACTORS}


def resolve_actor(actor_id: str | None = None) -> Actor:
    normalized = str(actor_id or "").strip()
    if not normalized:
        return DEFAULT_LOCAL_ACTOR
    return _ACTORS_BY_ID.get(normalized, DEFAULT_LOCAL_ACTOR)


def default_actor_id() -> str:
    return DEFAULT_LOCAL_ACTOR.actor_id


def actor_registry() -> tuple[Actor, ...]:
    return LOCAL_ACTORS


def actor_page_behavior(actor_id: str, page_id: str) -> ActorPageBehavior | None:
    return resolve_actor(actor_id).page_behavior(page_id)


def require_actor_id(actor: str) -> str:
    actor_id = str(actor).strip()
    if not actor_id:
        raise ValueError("actor is required")
    return actor_id
