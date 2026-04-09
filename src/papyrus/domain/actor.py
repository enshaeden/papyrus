from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    actor_id: str
    display_name: str
    role_hint: str

    def __post_init__(self) -> None:
        actor_id = str(self.actor_id).strip()
        display_name = str(self.display_name).strip()
        role_hint = str(self.role_hint).strip()
        if not actor_id:
            raise ValueError("actor_id is required")
        if not display_name:
            raise ValueError("display_name is required")
        if not role_hint:
            raise ValueError("role_hint is required")


DEFAULT_LOCAL_ACTOR = Actor(
    actor_id="local.operator",
    display_name="Local Operator",
    role_hint="reader_writer",
)
LOCAL_ACTORS: tuple[Actor, ...] = (
    DEFAULT_LOCAL_ACTOR,
    Actor(
        actor_id="local.reviewer",
        display_name="Local Reviewer",
        role_hint="reviewer",
    ),
    Actor(
        actor_id="local.manager",
        display_name="Local Manager",
        role_hint="manager",
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


def require_actor_id(actor: str) -> str:
    actor_id = str(actor).strip()
    if not actor_id:
        raise ValueError("actor is required")
    return actor_id
