#!/usr/bin/env python3
from __future__ import annotations

import shutil
from collections import defaultdict
from os import path as os_path
from pathlib import Path

from kb_common import (
    DECISIONS_DIR,
    DOCS_DIR,
    GENERATED_SITE_DOCS_DIR,
    LEGACY_GENERATED_DOCS_DIR,
    ROOT,
    collect_decision_paths,
    collect_docs_source_paths,
    date_to_iso,
    load_articles,
    load_policy,
    navigation_statuses,
    render_change_log,
    render_list,
    render_reference,
    site_article_output_path,
)

WORKFLOW_STARTERS = (
    ("Onboarding", ("kb-onboarding-employee-onboarding-checklist", "kb-runbook-laptop-provisioning")),
    ("Offboarding", ("kb-offboarding-employee-offboarding-checklist",)),
    ("Identity and Access", ("kb-access-password-reset-account-lockout", "kb-access-software-access-request")),
    ("Remote Access", ("kb-troubleshooting-vpn-connectivity",)),
    ("Workplace Support", ("kb-troubleshooting-printer-queue", "kb-troubleshooting-meeting-room-av-triage")),
    ("Incidents", ("kb-incident-response-template", "kb-postmortem-template")),
)


def copy_source_tree(source_root: Path, destination_root: Path, paths: list[Path]) -> None:
    for path in paths:
        target = destination_root / path.relative_to(source_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def site_relative_path_for_article(article) -> Path:
    return site_article_output_path(article).relative_to(GENERATED_SITE_DOCS_DIR)


def relative_site_link(from_relative: Path, to_relative: Path) -> str:
    return os_path.relpath(to_relative.as_posix(), start=from_relative.parent.as_posix())


def site_relative_path_for_repo_path(repo_relative: str) -> Path | None:
    candidate = Path(repo_relative)
    if repo_relative.startswith("knowledge/"):
        return candidate
    if repo_relative.startswith("archive/"):
        return candidate
    if repo_relative.startswith("docs/"):
        return candidate.relative_to("docs")
    if repo_relative.startswith("decisions/"):
        return candidate
    return None


def render_related_articles(article, by_id: dict[str, object]) -> str:
    related_lines = []
    current_relative = site_relative_path_for_article(article)
    for related_id in article.metadata["related_articles"]:
        related = by_id.get(related_id)
        if related:
            target_relative = site_relative_path_for_article(related)
            related_lines.append(
                f"- [{related.metadata['title']}]({relative_site_link(current_relative, target_relative)})"
            )
        else:
            related_lines.append(f"- {related_id}")
    if not related_lines:
        return "- None documented.\n"
    return "\n".join(related_lines) + "\n"


def render_reference_lines(article, by_id: dict[str, object]) -> str:
    current_relative = site_relative_path_for_article(article)
    lines = []
    for reference in article.metadata["references"]:
        article_id = reference.get("article_id")
        path = reference.get("path")
        line = render_reference(reference)
        if article_id and article_id in by_id:
            target_relative = site_relative_path_for_article(by_id[article_id])
            line = f"[{reference['title']}]({relative_site_link(current_relative, target_relative)})"
            if reference.get("note"):
                line += f" - {reference['note']}"
        elif path:
            target_relative = site_relative_path_for_repo_path(path)
            if target_relative is not None:
                line = f"[{reference['title']}]({relative_site_link(current_relative, target_relative)})"
                if reference.get("note"):
                    line += f" - {reference['note']}"
        lines.append(f"- {line}")
    if not lines:
        return "- None documented.\n"
    return "\n".join(lines) + "\n"


def render_article_page(article, by_id: dict[str, object]) -> str:
    metadata = article.metadata
    replaced_by = metadata.get("replaced_by")
    replacement_line = "None"
    if replaced_by and replaced_by in by_id:
        target_relative = site_relative_path_for_article(by_id[replaced_by])
        replacement_line = f"[{replaced_by}]({relative_site_link(site_relative_path_for_article(article), target_relative)})"
    elif replaced_by:
        replacement_line = replaced_by

    notes_section = ""
    if article.body:
        notes_section = f"\n## Additional Notes\n\n{article.body}\n"

    return (
        "<!-- Generated from canonical source content. Do not edit here. -->\n\n"
        f"# {metadata['title']}\n\n"
        f"Canonical source: `{article.relative_path}`\n\n"
        "## Summary\n\n"
        f"{metadata['summary']}\n\n"
        "## Metadata\n\n"
        f"- **ID:** {metadata['id']}\n"
        f"- **Canonical Path:** {metadata['canonical_path']}\n"
        f"- **Type:** {metadata['type']}\n"
        f"- **Status:** {metadata['status']}\n"
        f"- **Owner:** {metadata['owner']}\n"
        f"- **Source Type:** {metadata['source_type']}\n"
        f"- **Team:** {metadata['team']}\n"
        f"- **Systems:** {', '.join(metadata['systems']) or 'None'}\n"
        f"- **Services:** {', '.join(metadata['services']) or 'None'}\n"
        f"- **Tags:** {', '.join(metadata['tags']) or 'None'}\n"
        f"- **Created:** {date_to_iso(metadata['created'])}\n"
        f"- **Updated:** {date_to_iso(metadata['updated'])}\n"
        f"- **Last Reviewed:** {date_to_iso(metadata['last_reviewed'])}\n"
        f"- **Review Cadence:** {metadata['review_cadence']}\n"
        f"- **Audience:** {metadata['audience']}\n"
        f"- **Replaced By:** {replacement_line}\n"
        f"- **Retirement Reason:** {metadata['retirement_reason'] or 'None'}\n\n"
        "## Prerequisites\n\n"
        f"{render_list(metadata['prerequisites'])}\n"
        "## Steps\n\n"
        f"{render_list(metadata['steps'])}\n"
        "## Verification\n\n"
        f"{render_list(metadata['verification'])}\n"
        "## Rollback\n\n"
        f"{render_list(metadata['rollback'])}\n"
        "## Related Articles\n\n"
        f"{render_related_articles(article, by_id)}\n"
        "## References\n\n"
        f"{render_reference_lines(article, by_id)}\n"
        "## Change Log\n\n"
        f"{render_change_log(metadata['change_log'])}"
        f"{notes_section}"
    )


def render_index_page(title: str, grouped: dict[str, list], current_path: str) -> str:
    sections = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        f"# {title}",
        "",
    ]
    current_relative = Path(current_path)
    for group_name in sorted(grouped):
        sections.append(f"## {group_name}")
        sections.append("")
        for article in sorted(grouped[group_name], key=lambda item: item.metadata["title"]):
            target_relative = site_relative_path_for_article(article)
            sections.append(
                f"- [{article.metadata['title']}]({relative_site_link(current_relative, target_relative)}) "
                f"({article.metadata['status']}) - {article.metadata['summary']}"
            )
        sections.append("")
    return "\n".join(sections).strip() + "\n"


def render_start_here(by_id: dict[str, object]) -> str:
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Start Here",
        "",
        "Use these workflow entry points before creating new summary documents.",
        "",
    ]
    current_relative = Path("knowledge/start-here.md")
    for title, article_ids in WORKFLOW_STARTERS:
        lines.append(f"## {title}")
        lines.append("")
        for article_id in article_ids:
            article = by_id.get(article_id)
            if not article or article.metadata["status"] == "archived":
                continue
            target_relative = site_relative_path_for_article(article)
            lines.append(
                f"- [{article.metadata['title']}]({relative_site_link(current_relative, target_relative)}) - "
                f"{article.metadata['summary']}"
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_archive_index(archived_articles: list) -> str:
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Archive",
        "",
        "Archived articles are retained for history and audit only.",
        "",
    ]
    current_relative = Path("archive/index.md")
    if not archived_articles:
        lines.append("No archived content is currently present.")
        lines.append("")
        return "\n".join(lines)

    for article in sorted(archived_articles, key=lambda item: item.metadata["title"]):
        target_relative = site_relative_path_for_article(article)
        lines.append(
            f"- [{article.metadata['title']}]({relative_site_link(current_relative, target_relative)}) - "
            f"{article.metadata['retirement_reason'] or article.metadata['summary']}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    policy = load_policy()
    articles = load_articles(policy)
    by_id = {article.metadata["id"]: article for article in articles}
    visible_statuses = set(navigation_statuses(policy))
    visible_articles = [article for article in articles if article.metadata["status"] in visible_statuses]
    archived_articles = [article for article in articles if article.metadata["status"] == "archived"]

    if GENERATED_SITE_DOCS_DIR.exists():
        shutil.rmtree(GENERATED_SITE_DOCS_DIR)
    GENERATED_SITE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if LEGACY_GENERATED_DOCS_DIR.exists():
        shutil.rmtree(LEGACY_GENERATED_DOCS_DIR)

    copy_source_tree(DOCS_DIR, GENERATED_SITE_DOCS_DIR, collect_docs_source_paths())
    copy_source_tree(DECISIONS_DIR, GENERATED_SITE_DOCS_DIR / "decisions", collect_decision_paths())

    for article in articles:
        destination = site_article_output_path(article)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(render_article_page(article, by_id), encoding="utf-8")

    by_type = defaultdict(list)
    by_service = defaultdict(list)
    by_system = defaultdict(list)
    by_tag = defaultdict(list)
    for article in visible_articles:
        by_type[article.metadata["type"]].append(article)
        for service in article.metadata["services"]:
            by_service[service].append(article)
        for system in article.metadata["systems"]:
            by_system[system].append(article)
        for tag in article.metadata["tags"]:
            by_tag[tag].append(article)

    knowledge_root = GENERATED_SITE_DOCS_DIR / "knowledge"
    knowledge_root.mkdir(parents=True, exist_ok=True)
    (knowledge_root / "index.md").write_text(
        render_index_page("Knowledge Base", by_type, "knowledge/index.md"),
        encoding="utf-8",
    )
    (knowledge_root / "start-here.md").write_text(render_start_here(by_id), encoding="utf-8")
    (knowledge_root / "by-service.md").write_text(
        render_index_page("Knowledge By Service", by_service, "knowledge/by-service.md"),
        encoding="utf-8",
    )
    (knowledge_root / "by-system.md").write_text(
        render_index_page("Knowledge By System", by_system, "knowledge/by-system.md"),
        encoding="utf-8",
    )
    (knowledge_root / "by-tag.md").write_text(
        render_index_page("Knowledge By Tag", by_tag, "knowledge/by-tag.md"),
        encoding="utf-8",
    )

    archive_root = GENERATED_SITE_DOCS_DIR / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    (archive_root / "index.md").write_text(render_archive_index(archived_articles), encoding="utf-8")

    print(f"generated site docs for {len(articles)} article(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
