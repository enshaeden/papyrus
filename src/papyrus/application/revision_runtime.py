from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path
from typing import Any

from papyrus.application.runtime_projection import refresh_current_object_projection
from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.paths import ROOT
from papyrus.infrastructure.repositories.knowledge_repo import (
    delete_search_document,
    get_knowledge_object,
    load_taxonomies,
)
from papyrus.jobs.citation_scan import scan_citations
from papyrus.jobs.stale_scan import cadence_to_days


class RevisionRuntimeServices:
    def __init__(
        self,
        *,
        source_root: Path = ROOT,
        taxonomies: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.source_root = Path(source_root).resolve()
        self._taxonomies = taxonomies

    def taxonomies(self) -> dict[str, dict[str, Any]]:
        if self._taxonomies is None:
            self._taxonomies = load_taxonomies()
        return self._taxonomies

    def build_document(self, metadata: dict[str, Any], body_markdown: str) -> KnowledgeDocument:
        canonical_path = str(metadata.get("canonical_path") or "")
        return KnowledgeDocument(
            source_path=self.source_root / canonical_path if canonical_path else self.source_root,
            relative_path=canonical_path,
            metadata=dict(metadata),
            body=body_markdown,
        )

    def parse_revision(
        self,
        metadata: dict[str, Any],
        body_markdown: str,
        *,
        as_of: dt.date | None = None,
    ):
        review_date = as_of or dt.date.today()
        cadence_days = cadence_to_days(str(metadata["review_cadence"]), self.taxonomies())
        return normalize_object_metadata(
            self.build_document(metadata, body_markdown),
            review_cadence_days=cadence_days,
            as_of=review_date,
        )

    def refresh_object_projection(
        self,
        connection: sqlite3.Connection,
        *,
        object_id: str,
        as_of: dt.date | None = None,
    ) -> None:
        review_date = as_of or dt.date.today()
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            return
        current_revision_id = object_row["current_revision_id"]
        if not current_revision_id:
            delete_search_document(connection, object_id)
            return
        taxonomies = self.taxonomies()
        scan_citations(
            connection,
            taxonomies=taxonomies,
            as_of=review_date,
            object_ids=[object_id],
            persist=True,
        )
        refresh_current_object_projection(
            connection,
            object_id=object_id,
            taxonomies=taxonomies,
            as_of=review_date,
        )
