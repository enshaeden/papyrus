from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.application.impact_flow import propagate_change_event
from papyrus.domain.actor import require_actor_id
from papyrus.domain.events import ChangeEvent, EvidenceEvent, EventBase, ValidationEvent
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.event_repo import insert_event
from papyrus.infrastructure.search.indexer import fts5_available


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id() -> str:
    return f"evt-{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class EventIngestResult:
    event: EventBase
    impacted_objects: list[dict[str, Any]]


def _coerce_occurred_at(value: str | dt.datetime | None) -> dt.datetime:
    if value is None:
        return _now_utc()
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.timezone.utc).replace(microsecond=0)
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc).replace(microsecond=0)


def _event_class(event_type: str) -> type[EventBase]:
    if event_type.startswith("validation_"):
        return ValidationEvent
    if event_type.startswith("evidence_"):
        return EvidenceEvent
    return ChangeEvent


def _build_event(
    *,
    event_type: str,
    source: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any] | None,
    occurred_at: str | dt.datetime | None,
    actor: str,
    event_id: str | None = None,
) -> EventBase:
    actor = require_actor_id(actor)
    event_class = _event_class(event_type)
    return event_class(
        event_id=event_id or _event_id(),
        event_type=event_type,
        source=source,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=dict(payload or {}),
        occurred_at=_coerce_occurred_at(occurred_at),
        actor=actor,
    )


def ingest_event(
    *,
    database_path: Path = DB_PATH,
    event_type: str,
    source: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any] | None,
    actor: str,
    occurred_at: str | dt.datetime | None = None,
    event_id: str | None = None,
) -> EventIngestResult:
    event = _build_event(
        event_type=event_type,
        source=source,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        occurred_at=occurred_at,
        actor=actor,
        event_id=event_id,
    )

    connection = open_runtime_database(Path(database_path), minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    try:
        apply_runtime_schema(connection, has_fts5=fts5_available(connection))
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
        )
        insert_event(
            connection,
            event_id=event.event_id,
            event_type=event.event_type,
            source=event.source,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            payload_json=json_dump(event.payload),
            occurred_at=event.occurred_at.isoformat(),
            actor=event.actor,
        )
        insert_audit_event(
            connection,
            event_id=f"audit-{event.event_id}",
            event_type="event_ingested",
            occurred_at=event.occurred_at.isoformat(),
            actor=event.actor,
            object_id=event.entity_id if event.entity_type == "knowledge_object" else None,
            revision_id=None,
            details_json=json_dump(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "source": event.source,
                    "entity_type": event.entity_type,
                    "entity_id": event.entity_id,
                }
            ),
        )
        impacts = propagate_change_event(connection, event=event)
        connection.commit()
        return EventIngestResult(event=event, impacted_objects=impacts)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
