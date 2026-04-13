from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EventBase:
    event_id: str
    event_type: str
    source: str
    entity_type: str
    entity_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    occurred_at: dt.datetime = field(
        default_factory=lambda: dt.datetime.now(dt.UTC).replace(microsecond=0)
    )
    actor: str = "local.operator"

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id is required")
        if not self.event_type.strip():
            raise ValueError("event_type is required")
        if self.source not in {"local", "external", "connector"}:
            raise ValueError("source must be one of: local, external, connector")
        if not self.entity_type.strip():
            raise ValueError("entity_type is required")
        if not self.entity_id.strip():
            raise ValueError("entity_id is required")
        if not self.actor.strip():
            raise ValueError("actor is required")


@dataclass(frozen=True)
class ChangeEvent(EventBase):
    pass


@dataclass(frozen=True)
class ValidationEvent(EventBase):
    pass


@dataclass(frozen=True)
class EvidenceEvent(EventBase):
    pass
