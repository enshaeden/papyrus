from __future__ import annotations

import datetime as dt
import json
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from papyrus.domain.actor import require_actor_id
from papyrus.infrastructure.markdown.writer import MarkdownWriteResult, MarkdownWriter
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import get_knowledge_object, get_knowledge_revision, load_object_schemas


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass(frozen=True)
class SourceWritebackResult:
    object_id: str
    revision_id: str
    file_path: Path
    previous_text: str | None
    new_text: str


def _ordered_metadata(metadata: dict[str, Any], object_type: str) -> dict[str, Any]:
    object_schema = load_object_schemas().get(object_type)
    if object_schema is None:
        raise ValueError(f"unsupported knowledge object type for writeback: {object_type}")

    ordered: dict[str, Any] = {}
    for field_name, field_spec in object_schema.get("fields", {}).items():
        if field_name not in metadata:
            if not bool(field_spec.get("required", False)):
                continue
            raise ValueError(f"revision payload is missing required writeback field: {field_name}")
        ordered[field_name] = metadata[field_name]

    for key in sorted(metadata):
        if key not in ordered:
            ordered[key] = metadata[key]
    return ordered


def render_revision_markdown(*, object_type: str, metadata: dict[str, Any], body_markdown: str) -> str:
    ordered_metadata = _ordered_metadata(metadata, object_type)
    front_matter = yaml.safe_dump(
        ordered_metadata,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=88,
    ).strip()
    body = body_markdown.strip()
    if body:
        return f"---\n{front_matter}\n---\n\n{body}\n"
    return f"---\n{front_matter}\n---\n"


def write_revision_to_source(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    actor: str,
    root_path: Path = ROOT,
    writer: MarkdownWriter | None = None,
    record_audit: bool = True,
) -> SourceWritebackResult:
    actor = require_actor_id(actor)
    object_row = get_knowledge_object(connection, object_id)
    if object_row is None:
        raise ValueError(f"knowledge object not found: {object_id}")
    revision_row = get_knowledge_revision(connection, revision_id)
    if revision_row is None:
        raise ValueError(f"knowledge revision not found: {revision_id}")
    if revision_row["object_id"] != object_id:
        raise ValueError(f"revision {revision_id} does not belong to knowledge object {object_id}")
    if revision_row["revision_state"] != "approved":
        raise ValueError(f"writeback requires an approved revision: {revision_id}")

    metadata = json.loads(revision_row["normalized_payload_json"])
    markdown = render_revision_markdown(
        object_type=str(object_row["object_type"]),
        metadata=metadata,
        body_markdown=str(revision_row["body_markdown"]),
    )
    current_writer = writer or MarkdownWriter(root_path)
    write_result = current_writer.write_text(
        object_type=str(object_row["object_type"]),
        canonical_path=str(metadata.get("canonical_path") or object_row["canonical_path"]),
        object_id=object_id,
        title=str(metadata.get("title") or object_row["title"]),
        text=markdown,
    )

    if record_audit:
        insert_audit_event(
            connection,
            event_id=_event_id("source-writeback"),
            event_type="source_writeback",
            occurred_at=_now_utc().isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=revision_id,
            details_json=json.dumps(
                {
                    "file_path": str(metadata.get("canonical_path") or object_row["canonical_path"]),
                },
                sort_keys=True,
                ensure_ascii=True,
            ),
        )

    return SourceWritebackResult(
        object_id=object_id,
        revision_id=revision_id,
        file_path=write_result.file_path,
        previous_text=write_result.previous_text,
        new_text=write_result.new_text,
    )


def write_object_to_source(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    root_path: Path = ROOT,
) -> SourceWritebackResult:
    actor = require_actor_id(actor)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        revision_id = str(object_row["current_revision_id"] or "").strip()
        if not revision_id:
            raise ValueError(f"knowledge object has no current revision: {object_id}")
        result = write_revision_to_source(
            connection,
            object_id=object_id,
            revision_id=revision_id,
            actor=actor,
            root_path=root_path,
        )
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def write_all_approved_revisions(
    *,
    database_path: Path = DB_PATH,
    actor: str,
    root_path: Path = ROOT,
) -> list[SourceWritebackResult]:
    actor = require_actor_id(actor)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    results: list[SourceWritebackResult] = []
    try:
        rows = connection.execute(
            """
            SELECT o.object_id, o.current_revision_id
            FROM knowledge_objects AS o
            JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
            WHERE r.revision_state = 'approved'
            ORDER BY o.object_id
            """
        ).fetchall()
        for row in rows:
            results.append(
                write_revision_to_source(
                    connection,
                    object_id=str(row["object_id"]),
                    revision_id=str(row["current_revision_id"]),
                    actor=actor,
                    root_path=root_path,
                )
            )
        connection.commit()
        return results
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
