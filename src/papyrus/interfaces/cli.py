from __future__ import annotations

import argparse
import datetime as dt
import sqlite3
import sys

from papyrus.application.commands import build_projection_command, validate_repository_command
from papyrus.application.queries import CONTENT_HEALTH_SECTIONS, collect_content_health_sections, search_projection
from papyrus.domain.policies import searchable_statuses
from papyrus.infrastructure.markdown.serializer import parse_iso_date
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import load_knowledge_documents, load_policy, load_taxonomies
from papyrus.jobs.stale_scan import stale_documents


def validate_main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository source content and optional rendered site output.")
    parser.add_argument(
        "--include-rendered-site",
        action="store_true",
        help="also validate built site/ HTML href targets",
    )
    args = parser.parse_args()

    try:
        result = validate_repository_command(include_rendered_site=args.include_rendered_site)
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        print(f"validation setup failed: {exc}", file=sys.stderr)
        return 1

    if result.issues:
        for issue in result.issues:
            print(issue.render(), file=sys.stderr)
        print(f"validation failed with {len(result.issues)} issue(s)", file=sys.stderr)
        return 1

    print(f"validated {result.document_count} knowledge object source file(s)")
    return 0


def search_main() -> int:
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

    try:
        rows = search_projection(args.query, args.limit, args.db, statuses)
    except sqlite3.OperationalError as exc:
        print(f"search failed: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("no matches found")
        return 0

    for row in rows:
        print(
            f"{row.object_id} | {row.title} | {row.content_type} | {row.status} | "
            f"{row.path}\n  {row.summary}"
        )
    return 0


def report_stale_main() -> int:
    parser = argparse.ArgumentParser(description="Report active or deprecated articles due for review")
    parser.add_argument(
        "--as-of",
        default=dt.date.today().isoformat(),
        help="Report date in ISO 8601 format. Defaults to today.",
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="Include deprecated content in the stale report.",
    )
    args = parser.parse_args()

    policy = load_policy()
    taxonomies = load_taxonomies()
    documents = load_knowledge_documents(policy)
    statuses = {"active"}
    if args.include_deprecated:
        statuses.add("deprecated")

    rows = stale_documents(documents, taxonomies, parse_iso_date(args.as_of), statuses)
    if not rows:
        print("no stale knowledge objects found")
        return 0

    for days_overdue, document, due_date in rows:
        print(
            f"{days_overdue:>4} days overdue | {due_date.isoformat()} | "
            f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
        )
    return 0


def report_content_health_main() -> int:
    parser = argparse.ArgumentParser(description="Report repository content health and drift signals")
    parser.add_argument(
        "--section",
        choices=CONTENT_HEALTH_SECTIONS,
        action="append",
        help="Limit output to one or more sections.",
    )
    args = parser.parse_args()

    selected = args.section or list(CONTENT_HEALTH_SECTIONS)
    outputs = collect_content_health_sections(selected)
    for section in selected:
        print(f"[{section}]")
        lines = outputs.get(section, [])
        if not lines:
            print("none")
            continue
        for line in lines:
            print(line)
    return 0


def build_index_main() -> int:
    try:
        result = build_projection_command()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"built {result.database_path} with {result.document_count} knowledge object(s) using {result.mode}")
    return 0
