#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
import sys

from kb_common import DB_PATH, load_policy, searchable_statuses, status_rank_map


def build_status_filter_clause(statuses: list[str]) -> tuple[str, tuple[str, ...]]:
    placeholders = ", ".join("?" for _ in statuses)
    return f"({placeholders})", tuple(statuses)


def run_search(query: str, limit: int, database_path: str, statuses: list[str]) -> int:
    policy = load_policy()
    status_rank = status_rank_map(policy)
    status_clause, status_values = build_status_filter_clause(statuses)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        has_fts = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='article_search'"
        ).fetchone()
        case_sql = "CASE " + " ".join(
            f"WHEN a.status = '{status}' THEN {rank}" for status, rank in status_rank.items()
        ) + " ELSE 999 END"
        if has_fts:
            rows = connection.execute(
                f"""
                SELECT a.id, a.title, a.summary, a.type, a.status, a.path
                FROM article_search AS s
                JOIN articles AS a ON a.id = s.id
                WHERE article_search MATCH ?
                  AND a.status IN {status_clause}
                ORDER BY {case_sql}, bm25(article_search), a.title
                LIMIT ?
                """,
                (query, *status_values, limit),
            ).fetchall()
        else:
            like_query = f"%{query}%"
            rows = connection.execute(
                f"""
                SELECT id, title, summary, type, status, path
                FROM articles AS a
                WHERE search_text LIKE ?
                  AND status IN {status_clause}
                ORDER BY {case_sql}, title
                LIMIT ?
                """,
                (like_query, *status_values, limit),
            ).fetchall()
    except sqlite3.OperationalError as exc:
        print(f"search failed: {exc}", file=sys.stderr)
        return 1
    finally:
        connection.close()

    if not rows:
        print("no matches found")
        return 0

    for row in rows:
        print(
            f"{row['id']} | {row['title']} | {row['type']} | {row['status']} | "
            f"{row['path']}\n  {row['summary']}"
        )
    return 0


def main() -> int:
    policy = load_policy()
    parser = argparse.ArgumentParser(description="Search the local knowledge index")
    parser.add_argument("query", help="FTS or substring query")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the SQLite database")
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include archived content in search results.",
    )
    parser.add_argument(
        "--include-draft",
        action="store_true",
        help="Include draft content in search results.",
    )
    args = parser.parse_args()

    statuses = list(searchable_statuses(policy))
    if args.include_draft and "draft" not in statuses:
        statuses.append("draft")
    if args.include_archived and "archived" not in statuses:
        statuses.append("archived")
    return run_search(args.query, args.limit, args.db, statuses)


if __name__ == "__main__":
    raise SystemExit(main())
