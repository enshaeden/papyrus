from __future__ import annotations

import datetime as dt

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

