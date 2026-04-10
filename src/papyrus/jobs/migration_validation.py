from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from papyrus.compat.kb_common import load_articles, load_policy
from papyrus.infrastructure.paths import ROOT

MIGRATION_DIR = ROOT / "migration"
SEED_PLAN_PATH = MIGRATION_DIR / "seed-plan.yml"
ALIASES_PATH = MIGRATION_DIR / "aliases.yml"
EXCLUDED_PATH = MIGRATION_DIR / "excluded.yml"
MANIFEST_PATH = MIGRATION_DIR / "import-manifest.yml"


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping")
    return data


def collection_nodes(seed_plan: dict[str, Any]) -> set[str]:
    nodes = set()
    for collection in seed_plan.get("collections", []):
        path = str(collection["path"])
        parts = path.split("/")
        for index in range(1, len(parts) + 1):
            nodes.add("/".join(parts[:index]))
    for collection in seed_plan.get("synthetic_collections", []):
        nodes.add(str(collection["path"]))
    return nodes


def planned_articles(seed_plan: dict[str, Any]) -> list[tuple[str, str]]:
    entries = []
    for collection in seed_plan.get("collections", []):
        collection_path = str(collection["path"])
        for title in collection.get("articles", []):
            entries.append((collection_path, str(title)))
    return sorted(entries, key=lambda item: (item[0], item[1]))


def render_errors(errors: list[str]) -> int:
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"migration validation failed with {len(errors)} issue(s)", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    seed_plan = load_yaml_file(SEED_PLAN_PATH)
    aliases_data = load_yaml_file(ALIASES_PATH)
    excluded_data = load_yaml_file(EXCLUDED_PATH)
    manifest = load_yaml_file(MANIFEST_PATH)
    policy = load_policy()
    articles = load_articles(policy)

    errors: list[str] = []

    planned = planned_articles(seed_plan)
    canonical_titles = [title for _, title in planned]
    canonical_title_counts = Counter(canonical_titles)
    for title, count in sorted(canonical_title_counts.items()):
        if count > 1:
            errors.append(f"seed plan duplicates canonical title {title!r} {count} times")

    alias_titles: list[str] = []
    alias_to_canonical: dict[str, str] = {}
    for mapping in aliases_data.get("mappings", []):
        canonical = str(mapping["canonical"])
        if canonical not in canonical_title_counts:
            errors.append(f"alias canonical title is not present in seed plan: {canonical}")
        for alias in mapping.get("aliases", []):
            alias_value = str(alias)
            alias_titles.append(alias_value)
            previous = alias_to_canonical.get(alias_value)
            if previous and previous != canonical:
                errors.append(f"alias title {alias_value!r} points to multiple canonicals: {previous!r} and {canonical!r}")
            alias_to_canonical[alias_value] = canonical

    excluded_titles = [str(item["title"]) for item in excluded_data.get("excluded_titles", [])]
    excluded_counts = Counter(excluded_titles)
    for title, count in sorted(excluded_counts.items()):
        if count > 1:
            errors.append(f"excluded title appears multiple times: {title!r}")

    article_title_to_paths: dict[str, list[str]] = defaultdict(list)
    for article in articles:
        article_title_to_paths[str(article.metadata["title"])].append(article.relative_path)

    for title in sorted(canonical_title_counts):
        paths = article_title_to_paths.get(title, [])
        if not paths:
            errors.append(f"missing canonical article for title: {title!r}")
        elif len(paths) > 1:
            errors.append(f"canonical title appears multiple times in repository: {title!r} -> {paths}")

    for title in sorted(set(alias_titles)):
        if article_title_to_paths.get(title):
            errors.append(f"alias title was created as a canonical article: {title!r}")

    for title in sorted(set(excluded_titles)):
        if article_title_to_paths.get(title):
            errors.append(f"excluded title was created as a canonical article: {title!r}")

    expected_collection_paths = sorted(collection_nodes(seed_plan))
    for collection_path in expected_collection_paths:
        candidate = ROOT / "knowledge" / collection_path / "index.md"
        if not candidate.exists():
            errors.append(f"missing collection index: {candidate.relative_to(ROOT).as_posix()}")

    manifest_articles = manifest.get("articles", [])
    manifest_collections = manifest.get("collections", [])
    manifest_article_titles = Counter(str(item.get("title", "")) for item in manifest_articles)
    for title in sorted(canonical_title_counts):
        if manifest_article_titles[title] != 1:
            errors.append(f"manifest must contain exactly one article entry for {title!r}; found {manifest_article_titles[title]}")

    manifest_paths = {str(item.get("path", "")) for item in manifest_articles}
    for _, title in planned:
        repo_paths = article_title_to_paths.get(title, [])
        if len(repo_paths) == 1 and repo_paths[0] not in manifest_paths:
            errors.append(f"manifest is missing repository path for {title!r}: {repo_paths[0]}")

    expected_collection_index_paths = {
        f"knowledge/{collection_path}/index.md"
        for collection_path in expected_collection_paths
    }
    manifest_collection_paths = {str(item.get("path", "")) for item in manifest_collections}
    missing_collection_entries = sorted(expected_collection_index_paths.difference(manifest_collection_paths))
    for path in missing_collection_entries:
        errors.append(f"manifest is missing collection entry for {path}")

    if render_errors(errors):
        return 1

    print(
        "migration validation passed | "
        f"canonical_articles={len(canonical_titles)} | "
        f"aliases={len(alias_titles)} | "
        f"excluded={len(excluded_titles)} | "
        f"collection_indexes={len(expected_collection_paths)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
