from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActorIdentity:
    actor_id: str
    display_name: str
    role_hint: str

    def __post_init__(self) -> None:
        if not str(self.actor_id).strip():
            raise ValueError("actor_id is required")
        if not str(self.display_name).strip():
            raise ValueError("display_name is required")
        if not str(self.role_hint).strip():
            raise ValueError("role_hint is required")


LOCAL_READER_ACTOR = ActorIdentity(
    actor_id="local.reader",
    display_name="Local Reader",
    role_hint="reader",
)

DEFAULT_LOCAL_ACTOR = ActorIdentity(
    actor_id="local.operator",
    display_name="Local Operator",
    role_hint="operator",
)

LOCAL_ACTORS: tuple[ActorIdentity, ...] = (
    LOCAL_READER_ACTOR,
    DEFAULT_LOCAL_ACTOR,
    ActorIdentity(
        actor_id="local.reviewer",
        display_name="Local Reviewer",
        role_hint="operator",
    ),
    ActorIdentity(
        actor_id="local.manager",
        display_name="Local Manager",
        role_hint="admin",
    ),
)

_ACTORS_BY_ID = {actor.actor_id: actor for actor in LOCAL_ACTORS}
_DEFAULT_ACTOR_BY_ROLE = {
    "reader": LOCAL_READER_ACTOR,
    "operator": DEFAULT_LOCAL_ACTOR,
    "admin": _ACTORS_BY_ID["local.manager"],
}


def resolve_actor(actor_id: str | None = None) -> ActorIdentity:
    normalized = str(actor_id or "").strip()
    if not normalized:
        return DEFAULT_LOCAL_ACTOR
    return _ACTORS_BY_ID.get(normalized, DEFAULT_LOCAL_ACTOR)


def default_actor_id() -> str:
    return DEFAULT_LOCAL_ACTOR.actor_id


def default_actor_id_for_role(role: str | None = None) -> str:
    normalized = str(role or "").strip().lower()
    actor = _DEFAULT_ACTOR_BY_ROLE.get(normalized, DEFAULT_LOCAL_ACTOR)
    return actor.actor_id


def actor_registry() -> tuple[ActorIdentity, ...]:
    return LOCAL_ACTORS


def actor_page_behavior(actor_id: str, page_id: str) -> None:
    del actor_id, page_id
    return None


def require_actor_id(actor: str) -> str:
    actor_id = str(actor).strip()
    if not actor_id:
        raise ValueError("actor is required")
    return actor_id
