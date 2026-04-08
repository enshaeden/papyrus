from __future__ import annotations

import sqlite3
from pathlib import Path

from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.paths import DB_PATH


class ExportRuntimeUnavailableError(RuntimeError):
    """Raised when static export is requested without a built runtime."""


def approved_export_object_ids(database_path: str | Path = DB_PATH) -> set[str]:
    path = Path(database_path)
    if not path.exists():
        raise ExportRuntimeUnavailableError(
            "runtime database is not available; run `python3 scripts/build_index.py` before building static export"
        )

    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    try:
        has_projection = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='search_documents'"
        ).fetchone()
        if has_projection is None:
            raise ExportRuntimeUnavailableError(
                "runtime search projection is not available; run `python3 scripts/build_index.py` before building static export"
            )

        rows = connection.execute(
            """
            SELECT object_id
            FROM search_documents
            WHERE approval_state = 'approved'
            """
        ).fetchall()
        return {str(row["object_id"]) for row in rows}
    finally:
        connection.close()


def filter_approved_export_documents(
    documents: list[KnowledgeDocument],
    database_path: str | Path = DB_PATH,
) -> list[KnowledgeDocument]:
    approved_ids = approved_export_object_ids(database_path)
    return [document for document in documents if document.knowledge_object_id in approved_ids]
