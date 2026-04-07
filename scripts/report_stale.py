#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt

from kb_common import load_articles, load_policy, load_taxonomies, parse_iso_date, stale_articles


def main() -> int:
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
    articles = load_articles(policy)
    statuses = {"active"}
    if args.include_deprecated:
        statuses.add("deprecated")

    rows = stale_articles(articles, taxonomies, parse_iso_date(args.as_of), statuses)
    if not rows:
        print("no stale articles found")
        return 0

    for days_overdue, article, due_date in rows:
        print(
            f"{days_overdue:>4} days overdue | {due_date.isoformat()} | "
            f"{article.metadata['id']} | {article.metadata['title']} | {article.relative_path}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
