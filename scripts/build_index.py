#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
import sys

from kb_common import (
    BUILD_DIR,
    DB_PATH,
    date_to_iso,
    fts5_available,
    json_dump,
    load_articles,
    load_policy,
    load_schema,
    load_taxonomies,
    summarize_for_search,
    validate_articles,
)


def build_database() -> int:
    policy = load_policy()
    articles = load_articles(policy)
    schema = load_schema()
    taxonomies = load_taxonomies()
    issues = validate_articles(articles, schema, taxonomies, policy)
    if issues:
        for issue in issues:
            print(issue.render(), file=sys.stderr)
        print("index build aborted because validation failed", file=sys.stderr)
        return 1

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-shm", "-wal"):
        candidate = DB_PATH.with_name(DB_PATH.name + suffix)
        if candidate.exists():
            candidate.unlink()

    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            """
            CREATE TABLE articles (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                canonical_path TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT NOT NULL,
                owner TEXT NOT NULL,
                source_type TEXT NOT NULL,
                team TEXT NOT NULL,
                systems_json TEXT NOT NULL,
                services_json TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                created TEXT NOT NULL,
                updated TEXT NOT NULL,
                last_reviewed TEXT NOT NULL,
                review_cadence TEXT NOT NULL,
                audience TEXT NOT NULL,
                prerequisites_json TEXT NOT NULL,
                steps_json TEXT NOT NULL,
                verification_json TEXT NOT NULL,
                rollback_json TEXT NOT NULL,
                related_articles_json TEXT NOT NULL,
                replaced_by TEXT,
                retirement_reason TEXT,
                references_json TEXT NOT NULL,
                change_log_json TEXT NOT NULL,
                body_markdown TEXT NOT NULL,
                search_text TEXT NOT NULL
            )
            """
        )
        has_fts5 = fts5_available(connection)
        if has_fts5:
            connection.execute(
                """
                CREATE VIRTUAL TABLE article_search USING fts5(
                    id UNINDEXED,
                    title,
                    summary,
                    body,
                    tags,
                    systems,
                    services
                )
                """
            )

        for article in articles:
            metadata = article.metadata
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
                    article.relative_path,
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
                    article.body,
                    summarize_for_search(article),
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
                        article.body,
                        " ".join(metadata["tags"]),
                        " ".join(metadata["systems"]),
                        " ".join(metadata["services"]),
                    ),
                )

        connection.commit()
    finally:
        connection.close()

    mode = "fts5" if has_fts5 else "like-fallback"
    print(f"built {DB_PATH} with {len(articles)} article(s) using {mode}")
    return 0


def main() -> int:
    return build_database()


if __name__ == "__main__":
    raise SystemExit(main())
