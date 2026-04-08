from __future__ import annotations

import sqlite3


def apply_legacy_projection_schema(connection: sqlite3.Connection, has_fts5: bool) -> None:
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

