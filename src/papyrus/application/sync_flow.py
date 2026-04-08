from __future__ import annotations

import sys
from pathlib import Path

from papyrus.application.validation_flow import validate_knowledge_documents
from papyrus.infrastructure.db import recreate_database
from papyrus.infrastructure.migrations import apply_legacy_projection_schema
from papyrus.infrastructure.repositories.knowledge_repo import (
    load_knowledge_documents,
    load_policy,
    load_schema,
    load_taxonomies,
)
from papyrus.infrastructure.markdown.serializer import date_to_iso, json_dump
from papyrus.infrastructure.search.indexer import fts5_available, summarize_for_search


def build_search_projection(database_path: Path) -> tuple[int, str]:
    policy = load_policy()
    documents = load_knowledge_documents(policy)
    schema = load_schema()
    taxonomies = load_taxonomies()
    issues = validate_knowledge_documents(documents, schema, taxonomies, policy)
    if issues:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        raise ValueError("index build aborted because validation failed")

    connection = recreate_database(database_path)
    try:
        has_fts5 = fts5_available(connection)
        apply_legacy_projection_schema(connection, has_fts5=has_fts5)

        for document in documents:
            metadata = document.metadata
            connection.execute(
                """
                INSERT INTO articles (
                    id,
                    path,
                    canonical_path,
                    title,
                    summary,
                    type,
                    status,
                    owner,
                    source_type,
                    team,
                    systems_json,
                    services_json,
                    tags_json,
                    created,
                    updated,
                    last_reviewed,
                    review_cadence,
                    audience,
                    prerequisites_json,
                    steps_json,
                    verification_json,
                    rollback_json,
                    related_articles_json,
                    replaced_by,
                    retirement_reason,
                    references_json,
                    change_log_json,
                    body_markdown,
                    search_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata["id"],
                    document.relative_path,
                    metadata["canonical_path"],
                    metadata["title"],
                    metadata["summary"],
                    metadata["type"],
                    metadata["status"],
                    metadata["owner"],
                    metadata["source_type"],
                    metadata["team"],
                    json_dump(metadata["systems"]),
                    json_dump(metadata["services"]),
                    json_dump(metadata["tags"]),
                    date_to_iso(metadata["created"]),
                    date_to_iso(metadata["updated"]),
                    date_to_iso(metadata["last_reviewed"]),
                    metadata["review_cadence"],
                    metadata["audience"],
                    json_dump(metadata["prerequisites"]),
                    json_dump(metadata["steps"]),
                    json_dump(metadata["verification"]),
                    json_dump(metadata["rollback"]),
                    json_dump(metadata["related_articles"]),
                    metadata["replaced_by"],
                    metadata["retirement_reason"],
                    json_dump(metadata["references"]),
                    json_dump(metadata["change_log"]),
                    document.body,
                    summarize_for_search(document),
                ),
            )

            if has_fts5:
                connection.execute(
                    """
                    INSERT INTO article_search (id, title, summary, body, tags, systems, services)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        metadata["id"],
                        metadata["title"],
                        metadata["summary"],
                        document.body,
                        " ".join(metadata["tags"]),
                        " ".join(metadata["systems"]),
                        " ".join(metadata["services"]),
                    ),
                )

        connection.commit()
    finally:
        connection.close()

    return len(documents), "fts5" if has_fts5 else "like-fallback"

