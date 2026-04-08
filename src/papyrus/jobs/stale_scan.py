from __future__ import annotations

import datetime as dt
import sqlite3
from dataclasses import dataclass

from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.markdown.serializer import parse_iso_date


def cadence_to_days(cadence: str, taxonomies: dict[str, dict[str, object]]) -> int | None:
    for entry in taxonomies["review_cadences"].get("values", []):
        if isinstance(entry, dict) and entry.get("name") == cadence:
            return entry.get("interval_days")
    return None


def stale_documents(
    documents: list[KnowledgeDocument],
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date,
    allowed_statuses: set[str] | None = None,
) -> list[tuple[int, KnowledgeDocument, dt.date]]:
    stale_rows = []
    for document in documents:
        status = document.metadata.get("status")
        if allowed_statuses and status not in allowed_statuses:
            continue
        cadence_days = cadence_to_days(document.metadata["review_cadence"], taxonomies)
        if cadence_days is None:
            continue
        review_date = parse_iso_date(document.metadata["last_reviewed"])
        due_date = review_date + dt.timedelta(days=cadence_days)
        if due_date < as_of:
            stale_rows.append(((as_of - due_date).days, document, due_date))
    return sorted(stale_rows, key=lambda row: (row[0], row[1].metadata["title"]), reverse=True)


@dataclass(frozen=True)
class RuntimeStaleKnowledgeObject:
    days_overdue: int
    object_id: str
    title: str
    path: str
    due_date: dt.date
    status: str


def stale_runtime_objects(
    connection: sqlite3.Connection,
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date,
    allowed_statuses: set[str] | None = None,
) -> list[RuntimeStaleKnowledgeObject]:
    rows = connection.execute(
        """
        SELECT object_id, title, canonical_path, status, last_reviewed, review_cadence
        FROM knowledge_objects
        ORDER BY title
        """
    ).fetchall()
    stale_rows: list[RuntimeStaleKnowledgeObject] = []
    for row in rows:
        status = str(row["status"])
        if allowed_statuses and status not in allowed_statuses:
            continue
        cadence_days = cadence_to_days(str(row["review_cadence"]), taxonomies)
        if cadence_days is None:
            continue
        review_date = parse_iso_date(row["last_reviewed"])
        due_date = review_date + dt.timedelta(days=cadence_days)
        if due_date < as_of:
            stale_rows.append(
                RuntimeStaleKnowledgeObject(
                    days_overdue=(as_of - due_date).days,
                    object_id=str(row["object_id"]),
                    title=str(row["title"]),
                    path=str(row["canonical_path"]),
                    due_date=due_date,
                    status=status,
                )
            )
    return sorted(stale_rows, key=lambda row: (row.days_overdue, row.title), reverse=True)
