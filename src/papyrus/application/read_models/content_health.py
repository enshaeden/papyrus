from __future__ import annotations

from pathlib import Path

from papyrus.application.impact_flow import (
    docs_knowledge_like_warnings,
    documents_missing_list_field,
    find_possible_duplicate_documents,
    missing_owner_documents,
    relationless_documents,
)
from papyrus.application.validation_flow import orphaned_files
from papyrus.infrastructure.markdown.parser import collect_broken_markdown_links
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    collect_source_paths,
    load_current_runtime_documents,
    load_knowledge_documents,
    load_policy,
    load_taxonomies,
)
from papyrus.jobs.stale_scan import stale_runtime_objects

from .support import runtime_connection

CONTENT_HEALTH_SECTIONS = (
    "duplicates",
    "orphaned-files",
    "broken-links",
    "missing-owners",
    "missing-services",
    "missing-systems",
    "missing-tags",
    "isolated-articles",
    "citation-health",
    "suspect-objects",
    "knowledge-like-docs",
)

def stale_projection(
    *,
    as_of,
    include_deprecated: bool = False,
    database_path: str | Path = DB_PATH,
) -> list[tuple[int, str, str, str, object]]:
    taxonomies = load_taxonomies()
    statuses = {"active"}
    if include_deprecated:
        statuses.add("deprecated")

    connection = runtime_connection(database_path)
    if connection is None:
        documents = load_knowledge_documents(load_policy())
        from papyrus.jobs.stale_scan import stale_documents

        return [
            (days_overdue, document.metadata["id"], document.metadata["title"], document.relative_path, due_date)
            for days_overdue, document, due_date in stale_documents(documents, taxonomies, as_of, statuses)
        ]

    try:
        return [
            (row.days_overdue, row.object_id, row.title, row.path, row.due_date)
            for row in stale_runtime_objects(connection, taxonomies, as_of, statuses)
        ]
    finally:
        connection.close()

def collect_content_health_sections(
    selected: list[str] | None = None,
    database_path: str | Path = DB_PATH,
) -> dict[str, list[str]]:
    policy = load_policy()
    source_documents = load_knowledge_documents(policy)
    selected_sections = selected or list(CONTENT_HEALTH_SECTIONS)
    outputs: dict[str, list[str]] = {}
    connection = runtime_connection(database_path)
    runtime_documents = load_current_runtime_documents(connection) if connection is not None else source_documents

    try:
        if "duplicates" in selected_sections:
            duplicates = find_possible_duplicate_documents(
                runtime_documents,
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
            outputs["orphaned-files"] = orphaned_files(policy, source_documents)

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
                for document in missing_owner_documents(runtime_documents)
            ]

        if "missing-services" in selected_sections:
            outputs["missing-services"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "services")
            ]

        if "missing-systems" in selected_sections:
            outputs["missing-systems"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "systems")
            ]

        if "missing-tags" in selected_sections:
            outputs["missing-tags"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "tags")
            ]

        if "isolated-articles" in selected_sections:
            outputs["isolated-articles"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in relationless_documents(runtime_documents)
            ]

        if "citation-health" in selected_sections:
            outputs["citation-health"] = []
            if connection is not None:
                rows = connection.execute(
                    """
                    SELECT
                        o.object_id,
                        o.title,
                        o.canonical_path,
                        SUM(CASE WHEN c.validity_status = 'verified' THEN 1 ELSE 0 END) AS verified_count,
                        SUM(CASE WHEN c.validity_status = 'unverified' THEN 1 ELSE 0 END) AS unverified_count,
                        SUM(CASE WHEN c.validity_status = 'stale' THEN 1 ELSE 0 END) AS stale_count,
                        SUM(CASE WHEN c.validity_status = 'broken' THEN 1 ELSE 0 END) AS broken_count
                    FROM knowledge_objects AS o
                    JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
                    LEFT JOIN citations AS c ON c.revision_id = r.revision_id
                    GROUP BY o.object_id, o.title, o.canonical_path
                    HAVING SUM(CASE WHEN c.validity_status = 'unverified' THEN 1 ELSE 0 END) > 0
                        OR SUM(CASE WHEN c.validity_status = 'stale' THEN 1 ELSE 0 END) > 0
                        OR SUM(CASE WHEN c.validity_status = 'broken' THEN 1 ELSE 0 END) > 0
                    ORDER BY broken_count DESC, stale_count DESC, unverified_count DESC, o.title
                    """
                ).fetchall()
                outputs["citation-health"] = [
                    (
                        f"{row['object_id']} | {row['title']} | {row['canonical_path']} | "
                        f"verified={int(row['verified_count'] or 0)} | "
                        f"unverified={int(row['unverified_count'] or 0)} | "
                        f"stale={int(row['stale_count'] or 0)} | "
                        f"broken={int(row['broken_count'] or 0)}"
                    )
                    for row in rows
                ]

        if "suspect-objects" in selected_sections:
            outputs["suspect-objects"] = []
            if connection is not None:
                rows = connection.execute(
                    """
                    SELECT object_id, title, path, object_lifecycle_state, revision_review_state, trust_state, freshness_rank, citation_health_rank, ownership_rank
                    FROM search_documents
                    WHERE trust_state != 'trusted'
                       OR revision_review_state != 'approved'
                       OR freshness_rank > 0
                       OR citation_health_rank > 0
                       OR ownership_rank > 0
                    ORDER BY
                        CASE trust_state
                            WHEN 'stale' THEN 0
                            WHEN 'weak_evidence' THEN 1
                            WHEN 'suspect' THEN 2
                            ELSE 3
                        END,
                        title
                    """
                ).fetchall()
                outputs["suspect-objects"] = [
                    (
                        f"{row['object_id']} | {row['title']} | {row['path']} | "
                        f"lifecycle={row['object_lifecycle_state']} | review={row['revision_review_state']} | trust={row['trust_state']} | "
                        f"freshness_rank={row['freshness_rank']} | citation_health_rank={row['citation_health_rank']} | "
                        f"ownership_rank={row['ownership_rank']}"
                    )
                    for row in rows
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
    finally:
        if connection is not None:
            connection.close()

