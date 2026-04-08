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
        if not actor_id:
            raise ValueError("actor_id is required")
        if not display_name:
            raise ValueError("display_name is required")


def require_actor_id(actor: str) -> str:
    actor_id = str(actor).strip()
    if not actor_id:
        raise ValueError("actor is required")
    return actor_id
