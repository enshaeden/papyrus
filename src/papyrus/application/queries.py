from __future__ import annotations

import sqlite3
from pathlib import Path

from papyrus.application.impact_flow import (
    docs_knowledge_like_warnings,
    documents_missing_list_field,
    find_possible_duplicate_documents,
    missing_owner_documents,
    relationless_documents,
)
from papyrus.application.validation_flow import orphaned_files
from papyrus.domain.entities import SearchHit
from papyrus.domain.policies import searchable_statuses, status_rank_map
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    collect_source_paths,
    load_knowledge_documents,
    load_policy,
)
from papyrus.infrastructure.markdown.parser import collect_broken_markdown_links


CONTENT_HEALTH_SECTIONS = (
    "duplicates",
    "orphaned-files",
    "broken-links",
    "missing-owners",
    "missing-services",
    "missing-systems",
    "missing-tags",
    "isolated-articles",
    "knowledge-like-docs",
)


def build_status_filter_clause(statuses: list[str]) -> tuple[str, tuple[str, ...]]:
    placeholders = ", ".join("?" for _ in statuses)
    return f"({placeholders})", tuple(statuses)


def search_projection(
    query: str,
    limit: int,
    database_path: str | Path = DB_PATH,
    statuses: list[str] | None = None,
) -> list[SearchHit]:
    policy = load_policy()
    requested_statuses = list(statuses or searchable_statuses(policy))
    status_rank = status_rank_map(policy)
    status_clause, status_values = build_status_filter_clause(requested_statuses)

    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    try:
        has_fts = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
        ).fetchone()
        case_sql = "CASE " + " ".join(
            f"WHEN d.status = '{status}' THEN {rank}" for status, rank in status_rank.items()
        ) + " ELSE 999 END"
        governance_sql = (
            "d.freshness_rank, d.citation_health_rank, d.ownership_rank, "
            "CASE WHEN d.approval_state = 'approved' THEN 0 ELSE 1 END"
        )
        if has_fts:
            rows = connection.execute(
                f"""
                SELECT d.object_id, d.title, d.summary, d.object_type, d.status, d.path
                FROM knowledge_search AS s
                JOIN search_documents AS d ON d.object_id = s.object_id
                WHERE knowledge_search MATCH ?
                  AND d.status IN {status_clause}
                ORDER BY {case_sql}, {governance_sql}, bm25(knowledge_search), d.title
                LIMIT ?
                """,
                (query, *status_values, limit),
            ).fetchall()
        else:
            like_query = f"%{query}%"
            rows = connection.execute(
                f"""
                SELECT object_id, title, summary, object_type, status, path
                FROM search_documents AS d
                WHERE search_text LIKE ?
                  AND status IN {status_clause}
                ORDER BY {case_sql}, {governance_sql}, title
                LIMIT ?
                """,
                (like_query, *status_values, limit),
            ).fetchall()
    finally:
        connection.close()

    return [
        SearchHit(
            object_id=row["object_id"],
            title=row["title"],
            summary=row["summary"],
            content_type=row["object_type"],
            status=row["status"],
            path=row["path"],
        )
        for row in rows
    ]


def collect_content_health_sections(selected: list[str] | None = None) -> dict[str, list[str]]:
    policy = load_policy()
    documents = load_knowledge_documents(policy)
    selected_sections = selected or list(CONTENT_HEALTH_SECTIONS)
    outputs: dict[str, list[str]] = {}

    if "duplicates" in selected_sections:
        duplicates = find_possible_duplicate_documents(
            documents,
            float(policy["duplicate_detection"]["title_similarity_threshold"]),
        )
        outputs["duplicates"] = [
            (
                f"{duplicate.similarity:.2f} | {duplicate.left_title} | {duplicate.left_path} | "
                f"{duplicate.right_title} | {duplicate.right_path}"
            )
            for duplicate in duplicates
        ]

    if "orphaned-files" in selected_sections:
        outputs["orphaned-files"] = orphaned_files(policy, documents)

    if "broken-links" in selected_sections:
        markdown_paths = (
            collect_root_markdown_paths()
            + collect_docs_source_paths()
            + collect_decision_paths()
            + collect_source_paths(policy)
        )
        broken_links = collect_broken_markdown_links(markdown_paths)
        outputs["broken-links"] = [
            f"{item.source_path} | {item.target} | {item.reason}" for item in broken_links
        ]

    if "missing-owners" in selected_sections:
        outputs["missing-owners"] = [
            f"{document.metadata['id']} | {document.relative_path}"
            for document in missing_owner_documents(documents)
        ]

    if "missing-services" in selected_sections:
        outputs["missing-services"] = [
            f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
            for document in documents_missing_list_field(documents, "services")
        ]

    if "missing-systems" in selected_sections:
        outputs["missing-systems"] = [
            f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
            for document in documents_missing_list_field(documents, "systems")
        ]

    if "missing-tags" in selected_sections:
        outputs["missing-tags"] = [
            f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
            for document in documents_missing_list_field(documents, "tags")
        ]

    if "isolated-articles" in selected_sections:
        outputs["isolated-articles"] = [
            f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
            for document in relationless_documents(documents)
        ]

    if "knowledge-like-docs" in selected_sections:
        outputs["knowledge-like-docs"] = [
            (
                f"{warning.score} | {warning.path} | may contain operational-knowledge signals | "
                f"{'; '.join(warning.signals)}"
            )
            for warning in docs_knowledge_like_warnings()
        ]

    return outputs
