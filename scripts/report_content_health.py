#!/usr/bin/env python3
from __future__ import annotations

import argparse

from kb_common import (
    articles_missing_list_field,
    collect_article_paths,
    collect_broken_markdown_links,
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    find_possible_duplicate_articles,
    load_articles,
    load_policy,
    missing_owner_articles,
    orphaned_files,
    relationless_articles,
)

SECTIONS = (
    "duplicates",
    "orphaned-files",
    "broken-links",
    "missing-owners",
    "missing-services",
    "missing-systems",
    "missing-tags",
    "isolated-articles",
)


def render_section(title: str, lines: list[str]) -> None:
    print(f"[{title}]")
    if not lines:
        print("none")
        return
    for line in lines:
        print(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report repository content health and drift signals")
    parser.add_argument(
        "--section",
        choices=SECTIONS,
        action="append",
        help="Limit output to one or more sections.",
    )
    args = parser.parse_args()

    policy = load_policy()
    articles = load_articles(policy)
    selected = args.section or list(SECTIONS)
    outputs: dict[str, list[str]] = {}

    if "duplicates" in selected:
        duplicates = find_possible_duplicate_articles(
            articles,
            float(policy["duplicate_detection"]["title_similarity_threshold"]),
        )
        outputs["duplicates"] = [
            (
                f"{duplicate.similarity:.2f} | {duplicate.left_title} | {duplicate.left_path} | "
                f"{duplicate.right_title} | {duplicate.right_path}"
            )
            for duplicate in duplicates
        ]

    if "orphaned-files" in selected:
        outputs["orphaned-files"] = orphaned_files(policy, articles)

    if "broken-links" in selected:
        markdown_paths = (
            collect_root_markdown_paths()
            + collect_docs_source_paths()
            + collect_decision_paths()
            + collect_article_paths(policy)
        )
        broken_links = collect_broken_markdown_links(markdown_paths)
        outputs["broken-links"] = [
            f"{item.source_path} | {item.target} | {item.reason}" for item in broken_links
        ]

    if "missing-owners" in selected:
        outputs["missing-owners"] = [
            f"{article.metadata['id']} | {article.relative_path}" for article in missing_owner_articles(articles)
        ]

    if "missing-services" in selected:
        outputs["missing-services"] = [
            f"{article.metadata['id']} | {article.metadata['title']} | {article.relative_path}"
            for article in articles_missing_list_field(articles, "services")
        ]

    if "missing-systems" in selected:
        outputs["missing-systems"] = [
            f"{article.metadata['id']} | {article.metadata['title']} | {article.relative_path}"
            for article in articles_missing_list_field(articles, "systems")
        ]

    if "missing-tags" in selected:
        outputs["missing-tags"] = [
            f"{article.metadata['id']} | {article.metadata['title']} | {article.relative_path}"
            for article in articles_missing_list_field(articles, "tags")
        ]

    if "isolated-articles" in selected:
        outputs["isolated-articles"] = [
            f"{article.metadata['id']} | {article.metadata['title']} | {article.relative_path}"
            for article in relationless_articles(articles)
        ]

    for section in selected:
        render_section(section, outputs.get(section, []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
