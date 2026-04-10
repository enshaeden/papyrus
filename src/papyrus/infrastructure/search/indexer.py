from __future__ import annotations

import sqlite3
from pathlib import Path

from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.markdown.serializer import normalize_whitespace
from papyrus.infrastructure.paths import GENERATED_SITE_DOCS_DIR, KNOWLEDGE_DIR, SYSTEM_DESIGN_DOCS_SITE_ROOT


def summarize_for_search(document: KnowledgeDocument) -> str:
    metadata = document.metadata
    object_type = metadata.get("knowledge_object_type") or metadata.get("type") or ""
    related_services = metadata.get("related_services") or metadata.get("services") or []
    values: list[str] = [
        metadata.get("title", ""),
        metadata.get("summary", ""),
        object_type,
        metadata.get("legacy_article_type", ""),
        metadata.get("object_lifecycle_state", ""),
        metadata.get("owner", ""),
        metadata.get("team", ""),
        metadata.get("source_type", ""),
        " ".join(metadata.get("systems", [])),
        " ".join(related_services),
        " ".join(metadata.get("tags", [])),
        metadata.get("service_name", ""),
        " ".join(metadata.get("support_entrypoints", [])),
        " ".join(metadata.get("common_failure_modes", [])),
        " ".join(metadata.get("symptoms", [])),
        metadata.get("scope", ""),
        metadata.get("cause", ""),
        document.body,
    ]
    return normalize_whitespace(" ".join(str(value) for value in values if value))


def site_relative_path_for_repo_path(repo_relative: str) -> Path | None:
    candidate = Path(repo_relative)
    if repo_relative.startswith("knowledge/"):
        return candidate
    if repo_relative.startswith("archive/knowledge/"):
        return candidate
    if repo_relative.startswith("docs/"):
        return SYSTEM_DESIGN_DOCS_SITE_ROOT / candidate.relative_to("docs")
    if repo_relative.startswith("decisions/"):
        return candidate
    return None


def site_knowledge_output_path(document: KnowledgeDocument) -> Path:
    if document.metadata.get("object_lifecycle_state") == "archived":
        from papyrus.infrastructure.paths import ROOT

        return GENERATED_SITE_DOCS_DIR / document.source_path.relative_to(ROOT)
    return GENERATED_SITE_DOCS_DIR / "knowledge" / document.source_path.relative_to(KNOWLEDGE_DIR)


def fts5_available(connection: sqlite3.Connection) -> bool:
    try:
        connection.execute("CREATE VIRTUAL TABLE temp.fts_probe USING fts5(content)")
        connection.execute("DROP TABLE temp.fts_probe")
    except sqlite3.OperationalError:
        return False
    return True
