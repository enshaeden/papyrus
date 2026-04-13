from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from os import path as os_path
from pathlib import Path
from urllib.parse import urlencode

from papyrus.application.export_flow import (
    ExportRuntimeUnavailableError,
    approved_export_object_ids,
)
from papyrus.compat.kb_common import (
    DB_PATH,
    DECISIONS_DIR,
    DOCS_DIR,
    GENERATED_SITE_DOCS_DIR,
    GENERATED_SITE_INDEX_PATHS,
    LEGACY_GENERATED_DOCS_DIR,
    MARKDOWN_LINK_PATTERN,
    articles_missing_list_field,
    collect_decision_paths,
    collect_docs_source_paths,
    date_to_iso,
    find_possible_duplicate_articles,
    inverse_reference_graph,
    is_placeholder_target,
    load_articles,
    load_policy,
    load_taxonomies,
    missing_owner_articles,
    navigation_statuses,
    reference_graph,
    relationless_articles,
    relative_path,
    render_change_log,
    render_list,
    render_reference,
    resolve_local_link,
    similarity_ratio,
    site_article_output_path,
    site_relative_path_for_repo_path,
    stale_articles,
)

WORKFLOW_STARTERS = (
    (
        "Onboarding",
        (
            "kb-onboarding-employee-onboarding-checklist",
            "kb-runbook-laptop-provisioning",
        ),
    ),
    (
        "Offboarding",
        (
            "kb-offboarding-employee-offboarding-checklist",
            "kb-user-lifecycle-offboarding-and-termination-offboarding-and-termination",
        ),
    ),
    (
        "Identity and Access",
        (
            "kb-access-password-reset-account-lockout",
            "kb-access-software-access-request",
        ),
    ),
    (
        "Remote Access",
        (
            "kb-troubleshooting-vpn-connectivity",
            "kb-troubleshooting-network-onsite-network-outage-troubleshooting-sop",
        ),
    ),
    (
        "Workplace Support",
        (
            "kb-troubleshooting-printer-queue",
            "kb-troubleshooting-meeting-room-av-triage",
            "kb-assets-loaners-loaner-laptops",
        ),
    ),
    (
        "Incidents",
        (
            "kb-incidents-incident-response-template",
            "kb-postmortems-postmortem-template",
        ),
    ),
)

SUPPORT_SHORTCUTS = (
    (
        "Front-line troubleshooting",
        "Open current troubleshooting content for service desk operators.",
        {"audience": "service_desk", "type": "troubleshooting"},
    ),
    (
        "Service desk SOPs",
        "Open current SOP content filtered for the service desk audience.",
        {"audience": "service_desk", "type": "SOP"},
    ),
    (
        "Remote access procedures",
        "Jump to remote-access knowledge without browsing the taxonomy tree first.",
        {"audience": "service_desk", "service": "Remote Access"},
    ),
    (
        "Identity and access procedures",
        "Filter to identity and access content used during account recovery or access requests.",
        {"service": "Identity"},
    ),
    (
        "Printing and office support",
        "Jump to printing and collaboration support content for workplace issues.",
        {"service": "Printing"},
    ),
    (
        "Meeting room and AV support",
        "Filter to collaboration content for conference-room and AV support workflows.",
        {"service": "Collaboration"},
    ),
)

AUTHOR_SHORTCUTS = (
    (
        "Taxonomy-driven scaffold",
        "Start a new knowledge object with validated type, audience, team, and optional discovery metadata.",
        None,
    ),
    (
        "Discovery gaps",
        "Review knowledge objects missing service, system, tag, or relationship metadata before adding new content.",
        {"page": "content-health.md"},
    ),
    (
        "Facet explorer",
        "Use the explorer to find nearby knowledge objects before creating a new source-of-truth document.",
        {"page": "explorer.md"},
    ),
)

MANAGER_SHORTCUTS = (
    (
        "Knowledge explorer",
        "Filter by lifecycle, team, audience, service, system, and tag from one place.",
        {"page": "explorer.md"},
    ),
    (
        "Content health",
        "Review discovery gaps, isolated content, stale knowledge objects, and likely duplicate titles.",
        {"page": "content-health.md"},
    ),
    (
        "Coverage matrix",
        "Audit service-by-type coverage with links back into the explorer.",
        {"page": "coverage-matrix.md"},
    ),
    (
        "Knowledge tree",
        "Inspect the canonical knowledge tree grouped by repository path.",
        {"page": "tree.md"},
    ),
)

ORPHAN_PLACEHOLDER_LINK_PATTERN = re.compile(r"\]\((<?[A-Z0-9_]+>?)\)")


def _configure_generated_output_roots(output_root: Path) -> None:
    global GENERATED_SITE_DOCS_DIR, LEGACY_GENERATED_DOCS_DIR

    GENERATED_SITE_DOCS_DIR = output_root
    LEGACY_GENERATED_DOCS_DIR = output_root.parent / "_legacy_generated_docs"

    from papyrus.compat import kb_common
    from papyrus.infrastructure.search import indexer

    kb_common.GENERATED_SITE_DOCS_DIR = GENERATED_SITE_DOCS_DIR
    kb_common.LEGACY_GENERATED_DOCS_DIR = LEGACY_GENERATED_DOCS_DIR
    indexer.GENERATED_SITE_DOCS_DIR = GENERATED_SITE_DOCS_DIR


def render_placeholder_label(label: str) -> str:
    rendered = label.strip()
    if not rendered:
        return ""
    if "<" in rendered or ">" in rendered:
        return f"`{rendered}`"
    return rendered


def exportable_site_target(
    repo_relative: str,
    allowed_repo_paths: set[str] | None = None,
) -> Path | None:
    if allowed_repo_paths is not None and repo_relative not in allowed_repo_paths:
        return None
    return site_relative_path_for_repo_path(repo_relative)


def rewrite_local_markdown_links(
    source_path: Path,
    destination_relative: Path,
    text: str,
    allowed_repo_paths: set[str] | None = None,
) -> str:
    def replace(match) -> str:
        label, target = match.groups()
        clean_target, _, fragment = target.partition("#")
        clean_target = clean_target.strip()
        if is_placeholder_target(clean_target):
            return render_placeholder_label(label)
        resolved = resolve_local_link(source_path, clean_target)
        if resolved is None or not resolved.exists():
            return match.group(0)

        try:
            repo_relative = relative_path(resolved)
        except ValueError:
            return match.group(0)
        site_target = exportable_site_target(repo_relative, allowed_repo_paths)
        if site_target is None:
            return render_placeholder_label(label)

        rewritten = relative_site_link(destination_relative, site_target)
        if fragment:
            rewritten += f"#{fragment}"
        return f"[{label}]({rewritten})"

    rewritten = MARKDOWN_LINK_PATTERN.sub(replace, text)
    return ORPHAN_PLACEHOLDER_LINK_PATTERN.sub("", rewritten)


def normalize_placeholder_links(text: str) -> str:
    def replace(match) -> str:
        label, target = match.groups()
        clean_target = target.split("#", 1)[0].strip()
        if not is_placeholder_target(clean_target):
            return match.group(0)
        return render_placeholder_label(label)

    normalized = MARKDOWN_LINK_PATTERN.sub(replace, text)
    return ORPHAN_PLACEHOLDER_LINK_PATTERN.sub("", normalized)


def copy_source_tree(
    source_root: Path,
    destination_root: Path,
    paths: list[Path],
    *,
    allowed_repo_paths: set[str] | None = None,
) -> None:
    for path in paths:
        target = destination_root / path.relative_to(source_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            rewritten = rewrite_local_markdown_links(
                path,
                target.relative_to(GENERATED_SITE_DOCS_DIR),
                text,
                allowed_repo_paths,
            )
            target.write_text(rewritten, encoding="utf-8")
            continue
        shutil.copy2(path, target)


def site_relative_path_for_article(article) -> Path:
    return site_article_output_path(article).relative_to(GENERATED_SITE_DOCS_DIR)


def relative_site_link(from_relative: Path, to_relative: Path) -> str:
    return os_path.relpath(to_relative.as_posix(), start=from_relative.parent.as_posix())


def site_output_path(doc_relative: Path) -> Path:
    if doc_relative.suffix != ".md":
        return doc_relative
    if doc_relative.name == "index.md":
        if doc_relative.parent == Path("."):
            return Path("index.html")
        return doc_relative.parent / "index.html"
    return doc_relative.with_suffix("") / "index.html"


def site_href(from_relative: Path, to_relative: Path, query: str | None = None) -> str:
    current_output = site_output_path(from_relative)
    target_output = site_output_path(to_relative)
    href = os_path.relpath(target_output.as_posix(), start=current_output.parent.as_posix())
    if href.endswith("index.html"):
        href = href[: -len("index.html")]
    if not href:
        href = "./"
    if query:
        href = f"{href}?{query}"
    return href


def explorer_link(from_relative: Path, **filters: str) -> str:
    target = Path("knowledge/explorer.md")
    base = relative_site_link(from_relative, target)
    clean_filters = {key: value for key, value in filters.items() if value}
    if not clean_filters:
        return base
    return f"{base}?{urlencode(clean_filters)}"


def page_link(from_relative: Path, page_name: str) -> str:
    return relative_site_link(from_relative, Path("knowledge") / page_name)


def repo_doc_link(from_relative: Path, repo_relative: str) -> str:
    target = site_relative_path_for_repo_path(repo_relative)
    if target is None:
        return repo_relative
    return relative_site_link(from_relative, target)


def explorer_href(from_relative: Path, **filters: str) -> str:
    target = Path("knowledge/explorer.md")
    clean_filters = {key: value for key, value in filters.items() if value}
    query = urlencode(clean_filters) if clean_filters else None
    return site_href(from_relative, target, query)


def page_href(from_relative: Path, page_name: str) -> str:
    return site_href(from_relative, Path("knowledge") / page_name)


def repo_doc_href(from_relative: Path, repo_relative: str) -> str:
    target = site_relative_path_for_repo_path(repo_relative)
    if target is None:
        return repo_relative
    if target.suffix == ".md":
        return site_href(from_relative, target)
    return relative_site_link(from_relative, target)


def markdown_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def format_metadata_values(values: list[str], empty: str = "Not classified") -> str:
    if not values:
        return empty
    return ", ".join(f"`{item}`" for item in values)


def format_plain_values(values: list[str], empty: str = "None documented") -> str:
    if not values:
        return empty
    return ", ".join(values)


def primary_object_type(article) -> str:
    metadata = article.metadata
    return metadata.get("knowledge_object_type") or "unknown"


def article_link(article, current_relative: Path) -> str:
    return f"[{article.metadata['title']}]({relative_site_link(current_relative, site_relative_path_for_article(article))})"


def render_article_bullet(article, current_relative: Path) -> str:
    metadata = article.metadata
    services = format_plain_values(metadata["services"], "unclassified service")
    return (
        f"- {article_link(article, current_relative)} - {metadata['summary']} "
        f"(`{primary_object_type(article)}` | `{metadata['audience']}` | `{metadata['object_lifecycle_state']}` | {services})"
    )


def render_card_grid(cards: list[tuple[str, str, str]]) -> str:
    lines = ['<div class="kb-card-grid">']
    for title, description, href in cards:
        lines.append(f'  <a class="kb-card" href="{html.escape(href, quote=True)}">')
        lines.append(f"    <strong>{html.escape(title)}</strong>")
        lines.append(f"    <span>{html.escape(description)}</span>")
        lines.append("  </a>")
    lines.append("</div>")
    return "\n".join(lines)


def render_metric_grid(metrics: list[tuple[str, str]]) -> str:
    lines = ['<div class="kb-metric-grid">']
    for value, label in metrics:
        lines.append('  <div class="kb-metric">')
        lines.append(f"    <strong>{html.escape(value)}</strong>")
        lines.append(f"    <span>{html.escape(label)}</span>")
        lines.append("  </div>")
    lines.append("</div>")
    return "\n".join(lines)


def render_site_home(
    export_articles: list,
    docs_paths: list[Path],
    decision_paths: list[Path],
    excluded_count: int,
) -> str:
    current_relative = Path("index.md")
    doc_markdown_count = len([path for path in docs_paths if path.suffix == ".md"])
    decision_record_count = len(
        [path for path in decision_paths if path.suffix == ".md" and path.name != "index.md"]
    )
    cards = [
        (
            "Approved Knowledge Export",
            "Browse the approved static export of knowledge objects without exposing draft or unreviewed runtime state.",
            site_href(current_relative, Path("knowledge/index.md")),
        ),
        (
            "Operator Docs",
            "Orientation, workflow playbooks, and the concise system model for operating Papyrus.",
            site_href(current_relative, Path("system-design-docs/index.md")),
        ),
        (
            "Governance & Decisions",
            "Accepted repository decisions, structural rules, and durable rationale for operating Papyrus.",
            site_href(current_relative, Path("decisions/index.md")),
        ),
    ]
    metrics = [
        (str(len(export_articles)), "approved knowledge exports"),
        (str(excluded_count), "source knowledge objects excluded from export"),
        (str(doc_markdown_count), "operator docs and references"),
        (
            str(decision_record_count),
            "governance record" if decision_record_count == 1 else "governance records",
        ),
    ]
    return (
        "<!-- Generated from source content. Do not edit here. -->\n\n"
        "# Papyrus\n\n"
        "Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.\n\n"
        "This site is an optional approved-content export from Papyrus.\n\n"
        "The primary operator surfaces are the CLI, the local runtime database, the JSON API, and the server-rendered operator web interface.\n\n"
        "Use this export for browseable approved knowledge and supporting repository documentation. Do not treat it as the operational control plane or source of truth.\n\n"
        f"{render_card_grid(cards)}\n\n"
        f"{render_metric_grid(metrics)}\n\n"
        "## Export Scope\n\n"
        "- Knowledge pages appear here only when the current runtime revision is approved.\n"
        "- Draft, unreviewed, or rejected runtime state is intentionally excluded from this export.\n"
        "- Use [Start Here](knowledge/start-here.md), [Support Discovery](knowledge/support.md), or the [Knowledge Explorer](knowledge/explorer.md) for browse-only discovery of approved knowledge.\n\n"
        "## Area Guide\n\n"
        "### Approved Knowledge Export\n\n"
        "- Approved export of operator-facing procedures, references, troubleshooting content, runbooks, and service records.\n"
        "- Source of truth remains `knowledge/` and `archive/knowledge/`, not this site.\n\n"
        "### Operator Docs\n\n"
        "- Use [Operator Docs](system-design-docs/index.md) for orientation, role-based playbooks, and the concise system model.\n"
        "- Source of truth: `docs/`.\n\n"
        "### Governance & Decisions\n\n"
        "- Use [Governance & Decisions](decisions/index.md) for accepted repository decisions, structural rules, and durable rationale.\n"
        "- Source of truth: `decisions/` for accepted repository decisions, with supporting operator material referenced from `docs/`.\n"
    )


def ordered_group_names(
    grouped: dict[str, list], group_order: list[str] | None = None
) -> list[str]:
    names = list(grouped)
    if not group_order:
        return sorted(names)
    order_index = {name: index for index, name in enumerate(group_order)}
    return sorted(names, key=lambda item: (order_index.get(item, len(order_index)), item))


def render_grouped_index_page(
    title: str,
    intro: str,
    grouped: dict[str, list],
    current_path: str,
    facet_name: str | None = None,
    group_order: list[str] | None = None,
) -> str:
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        f"# {title}",
        "",
        intro,
        "",
    ]
    current_relative = Path(current_path)
    if not grouped:
        lines.append("No matching articles are currently available.")
        lines.append("")
        return "\n".join(lines)

    for group_name in ordered_group_names(grouped, group_order):
        lines.append(f"## {group_name} ({len(grouped[group_name])})")
        lines.append("")
        if facet_name:
            filter_value = "__none__" if group_name == "Unclassified" else group_name
            lines.append(
                f"Explorer view: [Open filtered view]"
                f"({explorer_link(current_relative, **{facet_name: filter_value})})"
            )
            lines.append("")
        for article in sorted(grouped[group_name], key=lambda item: item.metadata["title"]):
            lines.append(render_article_bullet(article, current_relative))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_start_here(by_id: dict[str, object]) -> str:
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Start Here",
        "",
        "Use these task-oriented entry points before creating new summary documents or browsing the taxonomy tree.",
        "",
    ]
    current_relative = Path("knowledge/start-here.md")
    for title, article_ids in WORKFLOW_STARTERS:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(
            f"Explorer view: [Open related content]({explorer_link(current_relative, query=title.lower())})"
        )
        lines.append("")
        for article_id in article_ids:
            article = by_id.get(article_id)
            if not article:
                continue
            lines.append(render_article_bullet(article, current_relative))
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

    lines.append(
        f"Explorer view: [Show archived articles]"
        f"({explorer_link(current_relative, object_lifecycle_state='archived')})"
    )
    lines.append("")
    for article in sorted(archived_articles, key=lambda item: item.metadata["title"]):
        lines.append(
            f"- {article_link(article, current_relative)} - "
            f"{article.metadata['retirement_reason'] or article.metadata['summary']}"
        )
    lines.append("")
    return "\n".join(lines)


def render_related_articles(article, by_id: dict[str, object]) -> str:
    current_relative = site_relative_path_for_article(article)
    related_lines = []
    for related_id in article.metadata["related_articles"]:
        related = by_id.get(related_id)
        if not related:
            related_lines.append(f"- `{related_id}`")
            continue
        related_lines.append(
            f"- {article_link(related, current_relative)} - {related.metadata['summary']}"
        )
    if not related_lines:
        return "- None documented.\n"
    return "\n".join(related_lines) + "\n"


def render_reference_lines(
    article,
    by_id: dict[str, object],
    allowed_repo_paths: set[str],
) -> str:
    current_relative = site_relative_path_for_article(article)
    lines = []
    for reference in article.metadata["references"]:
        article_id = reference.get("article_id")
        path = reference.get("path")
        line = render_reference(reference)
        if article_id and article_id in by_id:
            line = article_link(by_id[article_id], current_relative)
            if reference.get("note"):
                line += f" - {reference['note']}"
        elif path:
            target_relative = exportable_site_target(path, allowed_repo_paths)
            if target_relative is not None:
                href = relative_site_link(current_relative, target_relative)
                line = f"[{reference['title']}]({href})"
                if reference.get("note"):
                    line += f" - {reference['note']}"
        lines.append(f"- {line}")
    if not lines:
        return "- None documented.\n"
    return "\n".join(lines) + "\n"


def render_referenced_by(
    article, by_id: dict[str, object], inbound_graph: dict[str, set[str]]
) -> str:
    current_relative = site_relative_path_for_article(article)
    lines = []
    for article_id in sorted(inbound_graph.get(article.metadata["id"], set())):
        inbound = by_id.get(article_id)
        if not inbound:
            continue
        lines.append(f"- {article_link(inbound, current_relative)} - {inbound.metadata['summary']}")
    if not lines:
        return "- No inbound article links documented.\n"
    return "\n".join(lines) + "\n"


def related_inference_candidates(article, articles: list) -> list[tuple[int, object, list[str]]]:
    results = []
    current_id = article.metadata["id"]
    current_path = Path(article.relative_path)
    for candidate in articles:
        candidate_id = candidate.metadata["id"]
        if candidate_id == current_id:
            continue
        reasons = []
        score = 0

        shared_services = sorted(
            set(article.metadata["services"]).intersection(candidate.metadata["services"])
        )
        if shared_services:
            score += len(shared_services) * 4
            reasons.append(f"shared service: {', '.join(shared_services)}")

        shared_systems = sorted(
            set(article.metadata["systems"]).intersection(candidate.metadata["systems"])
        )
        if shared_systems:
            score += len(shared_systems) * 3
            reasons.append(f"shared system: {', '.join(shared_systems)}")

        shared_tags = sorted(set(article.metadata["tags"]).intersection(candidate.metadata["tags"]))
        if shared_tags:
            score += len(shared_tags) * 2
            reasons.append(f"shared tag: {', '.join(shared_tags)}")

        if article.metadata["audience"] == candidate.metadata["audience"]:
            score += 2
            reasons.append(f"shared audience: {article.metadata['audience']}")

        if article.metadata["team"] == candidate.metadata["team"]:
            score += 1
            reasons.append(f"shared team: {article.metadata['team']}")

        if primary_object_type(article) == primary_object_type(candidate):
            score += 1
            reasons.append(f"shared type: {primary_object_type(article)}")

        if current_path.parent == Path(candidate.relative_path).parent:
            score += 2
            reasons.append("same knowledge-tree section")

        title_similarity = similarity_ratio(article.metadata["title"], candidate.metadata["title"])
        if title_similarity >= 0.62:
            score += 3
            reasons.append(f"similar title ({title_similarity:.2f})")

        if score >= 3:
            results.append((score, candidate, reasons))
    return sorted(results, key=lambda item: (-item[0], item[1].metadata["title"]))


def render_inferred_related(article, articles: list, by_id: dict[str, object]) -> str:
    current_relative = site_relative_path_for_article(article)
    explicit_ids = {article.metadata["id"], *article.metadata["related_articles"]}
    explicit_ids.update(
        reference["article_id"]
        for reference in article.metadata["references"]
        if reference.get("article_id")
    )
    if article.metadata.get("replaced_by"):
        explicit_ids.add(article.metadata["replaced_by"])

    lines = []
    for score, candidate, reasons in related_inference_candidates(article, articles):
        if candidate.metadata["id"] in explicit_ids:
            continue
        lines.append(
            f"- {article_link(candidate, current_relative)} - [Inference] "
            f"{'; '.join(reasons)} (score {score})"
        )
        if len(lines) == 5:
            break
    if not lines:
        return "- [Inference] No strong metadata-based nearby articles were identified.\n"
    return "\n".join(lines) + "\n"


def render_same_section_articles(article, articles: list) -> str:
    current_relative = site_relative_path_for_article(article)
    siblings = [
        candidate
        for candidate in articles
        if candidate.metadata["id"] != article.metadata["id"]
        and Path(candidate.relative_path).parent == Path(article.relative_path).parent
    ]
    if not siblings:
        return "- No other articles share this knowledge-tree section.\n"
    lines = []
    for sibling in sorted(siblings, key=lambda item: item.metadata["title"])[:5]:
        lines.append(f"- {article_link(sibling, current_relative)} - {sibling.metadata['summary']}")
    return "\n".join(lines) + "\n"


def render_lifecycle_links(article, articles: list, by_id: dict[str, object]) -> str:
    current_relative = site_relative_path_for_article(article)
    lines = []
    replaced_by = article.metadata.get("replaced_by")
    if replaced_by and replaced_by in by_id:
        lines.append(f"- Replaced by: {article_link(by_id[replaced_by], current_relative)}")
    elif replaced_by:
        lines.append(f"- Replaced by: `{replaced_by}`")

    replaced_articles = [
        candidate
        for candidate in articles
        if candidate.metadata.get("replaced_by") == article.metadata["id"]
    ]
    for candidate in sorted(replaced_articles, key=lambda item: item.metadata["title"]):
        lines.append(f"- Replaces: {article_link(candidate, current_relative)}")

    if not lines:
        return "- No replacement chain is currently documented.\n"
    return "\n".join(lines) + "\n"


def render_browse_more_links(article) -> str:
    current_relative = site_relative_path_for_article(article)
    lines = [
        f"- [Browse more `{primary_object_type(article)}` articles]"
        f"({explorer_link(current_relative, type=primary_object_type(article))})",
        f"- [Browse more `{article.metadata['audience']}` content]"
        f"({explorer_link(current_relative, audience=article.metadata['audience'])})",
        f"- [Browse more `{article.metadata['team']}` content]"
        f"({explorer_link(current_relative, team=article.metadata['team'])})",
    ]
    for service in article.metadata["services"][:2]:
        lines.append(
            f"- [Browse more `{service}` content]"
            f"({explorer_link(current_relative, service=service)})"
        )
    for tag in article.metadata["tags"][:2]:
        lines.append(f"- [Browse more `{tag}` content]({explorer_link(current_relative, tag=tag)})")
    return "\n".join(lines) + "\n"


def render_article_page(
    article,
    by_id: dict[str, object],
    articles: list,
    inbound_graph: dict[str, set[str]],
    allowed_repo_paths: set[str],
) -> str:
    metadata = article.metadata
    notes_section = ""
    if article.body:
        rewritten_body = rewrite_local_markdown_links(
            article.source_path,
            site_relative_path_for_article(article),
            article.body,
            allowed_repo_paths,
        )
        notes_section = f"\n## Additional Notes\n\n{normalize_placeholder_links(rewritten_body)}\n"

    classification_gaps = []
    if not metadata["services"]:
        classification_gaps.append("services")
    if not metadata["systems"]:
        classification_gaps.append("systems")
    if not metadata["tags"]:
        classification_gaps.append("tags")

    classification_line = "Fully classified for discovery."
    if classification_gaps:
        classification_line = "Missing discovery metadata for: " + ", ".join(classification_gaps)

    owner_team = f"{metadata['owner']} / {metadata['team']}"
    lifecycle_summary = (
        f"{metadata['object_lifecycle_state']} | last reviewed {date_to_iso(metadata['last_reviewed'])} "
        f"| cadence {metadata['review_cadence']}"
    )
    source_summary = f"{metadata['source_type']} from {metadata['source_system']}"

    summary_row = (
        "| Field | Value |\n"
        "| --- | --- |\n"
        f"| Summary | {markdown_table_cell(metadata['summary'])} |\n"
        f"| Audience | {markdown_table_cell(metadata['audience'])} |\n"
        f"| Services | {markdown_table_cell(format_plain_values(metadata['services'], 'Not classified'))} |\n"
        f"| Systems | {markdown_table_cell(format_plain_values(metadata['systems'], 'Not classified'))} |\n"
        f"| Owner / Team | {markdown_table_cell(owner_team)} |\n"
        f"| Lifecycle | {markdown_table_cell(lifecycle_summary)} |\n"
        f"| Source | {markdown_table_cell(source_summary)} |\n"
        f"| Discovery Classification | {markdown_table_cell(classification_line)} |\n"
    )

    return (
        "<!-- Generated from canonical source content. Do not edit here. -->\n\n"
        f"# {metadata['title']}\n\n"
        f"Canonical source: `{article.relative_path}`\n\n"
        "## Operational Snapshot\n\n"
        f"{summary_row}\n"
        "## Applicability\n\n"
        f"- Primary audience: `{metadata['audience']}`\n"
        f"- Service areas: {format_metadata_values(metadata['services'])}\n"
        f"- Systems in scope: {format_metadata_values(metadata['systems'])}\n"
        f"- Tags: {format_metadata_values(metadata['tags'])}\n"
        f"- Lifecycle: `{metadata['object_lifecycle_state']}`\n"
        f"- Review cadence: `{metadata['review_cadence']}`\n\n"
        "## Operational Procedure\n\n"
        "### Prerequisites\n\n"
        f"{render_list(metadata['prerequisites'])}\n"
        "### Steps\n\n"
        f"{render_list(metadata['steps'])}\n"
        "### Verification\n\n"
        f"{render_list(metadata['verification'])}\n"
        "### Rollback\n\n"
        f"{render_list(metadata['rollback'])}\n"
        "## Connected Knowledge\n\n"
        "### Explicitly Related Articles\n\n"
        f"{render_related_articles(article, by_id)}\n"
        "### Referenced By\n\n"
        f"{render_referenced_by(article, by_id, inbound_graph)}\n"
        "### Nearby In The Same Knowledge-Tree Section\n\n"
        f"{render_same_section_articles(article, articles)}\n"
        "### Suggested Nearby Articles [Inference]\n\n"
        f"{render_inferred_related(article, articles, by_id)}\n"
        "### Lifecycle And Replacement\n\n"
        f"{render_lifecycle_links(article, articles, by_id)}\n"
        "### Browse More Like This\n\n"
        f"{render_browse_more_links(article)}\n"
        "## References\n\n"
        f"{render_reference_lines(article, by_id, allowed_repo_paths)}\n"
        "## Change Log\n\n"
        f"{render_change_log(metadata['change_log'])}"
        f"{notes_section}"
    )


def taxonomy_usage_count(articles: list, field_name: str, value: str) -> int:
    if field_name == "type":
        return sum(1 for article in articles if primary_object_type(article) == value)
    sample = articles[0].metadata[field_name] if articles else None
    if isinstance(sample, list):
        return sum(1 for article in articles if value in article.metadata[field_name])
    return sum(1 for article in articles if article.metadata[field_name] == value)


def render_taxonomy_table(
    title: str,
    taxonomy_name: str,
    field_name: str,
    taxonomies: dict[str, dict[str, object]],
    articles: list,
    current_relative: Path,
) -> str:
    lines = [f"## {title}", "", "| Value | Description | Current Usage |", "| --- | --- | --- |"]
    for entry in taxonomies[taxonomy_name]["values"]:
        value = entry["name"] if isinstance(entry, dict) else str(entry)
        description = entry.get("description", "") if isinstance(entry, dict) else ""
        usage = taxonomy_usage_count(articles, field_name, value)
        if usage:
            usage_value = f"[{usage}]({explorer_link(current_relative, **{field_name.rstrip('s'): value if field_name.endswith('s') else value})})"
            if field_name in {"services", "systems", "tags"}:
                usage_value = (
                    f"[{usage}]({explorer_link(current_relative, **{field_name[:-1]: value})})"
                )
        else:
            usage_value = "0"
        lines.append(
            f"| `{markdown_table_cell(value)}` | {markdown_table_cell(description)} | {usage_value} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_explorer_page(
    articles: list,
    taxonomies: dict[str, dict[str, object]],
    default_object_lifecycle_states: list[str],
) -> str:
    article_records = []
    current_relative = Path("knowledge/explorer.md")
    for article in sorted(articles, key=lambda item: item.metadata["title"]):
        article_records.append(
            {
                "id": article.metadata["id"],
                "title": article.metadata["title"],
                "summary": article.metadata["summary"],
                "path": article.relative_path,
                "site_path": site_href(current_relative, site_relative_path_for_article(article)),
                "type": primary_object_type(article),
                "object_lifecycle_state": article.metadata["object_lifecycle_state"],
                "owner": article.metadata["owner"],
                "team": article.metadata["team"],
                "audience": article.metadata["audience"],
                "services": article.metadata["services"],
                "systems": article.metadata["systems"],
                "tags": article.metadata["tags"],
                "source_type": article.metadata["source_type"],
                "last_reviewed": date_to_iso(article.metadata["last_reviewed"]),
                "updated": date_to_iso(article.metadata["updated"]),
                "related_count": len(article.metadata["related_articles"]),
            }
        )

    explorer_taxonomies = {
        "type": [entry["name"] for entry in taxonomies["knowledge_object_types"]["values"]],
        "audience": [entry["name"] for entry in taxonomies["audiences"]["values"]],
        "service": [entry["name"] for entry in taxonomies["services"]["values"]],
        "system": [entry["name"] for entry in taxonomies["systems"]["values"]],
        "tag": [entry["name"] for entry in taxonomies["tags"]["values"]],
        "object_lifecycle_state": [entry["name"] for entry in taxonomies["statuses"]["values"]],
        "team": [entry["name"] for entry in taxonomies["teams"]["values"]],
        "owner": sorted({article.metadata["owner"] for article in articles}),
        "default_object_lifecycle_states": default_object_lifecycle_states,
    }
    data_json = json.dumps(article_records, sort_keys=True, ensure_ascii=True).replace("</", "<\\/")
    taxonomy_json = json.dumps(explorer_taxonomies, sort_keys=True, ensure_ascii=True).replace(
        "</", "<\\/"
    )

    return (
        "<!-- Generated from canonical source content. Do not edit here. -->\n\n"
        "# Knowledge Explorer\n\n"
        "Use the filters below to browse approved export knowledge by audience, type, service, system, tag, "
        "team, owner, and lifecycle state without relying on the repository tree alone.\n\n"
        '<div class="kb-explorer" id="kb-explorer">\n'
        '  <div class="kb-explorer-controls" id="kb-explorer-controls"></div>\n'
        '  <div class="kb-explorer-summary" id="kb-explorer-summary"></div>\n'
        '  <div class="kb-explorer-results" id="kb-explorer-results"></div>\n'
        "</div>\n\n"
        f'<script type="application/json" id="kb-explorer-data">{data_json}</script>\n'
        f'<script type="application/json" id="kb-explorer-taxonomies">{taxonomy_json}</script>\n'
    )


def render_support_page(by_id: dict[str, object]) -> str:
    current_relative = Path("knowledge/support.md")
    cards = [
        (title, description, explorer_href(current_relative, **filters))
        for title, description, filters in SUPPORT_SHORTCUTS
    ]
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Support Discovery",
        "",
        "Use these role-based entry points to find approved operational guidance quickly.",
        "",
        render_card_grid(cards),
        "",
        "## Common Operational Journeys",
        "",
    ]
    for title, article_ids in WORKFLOW_STARTERS:
        lines.append(f"### {title}")
        lines.append("")
        for article_id in article_ids:
            article = by_id.get(article_id)
            if not article:
                continue
            lines.append(render_article_bullet(article, current_relative))
        lines.append("")
    lines.extend(
        [
            "## Broader Browse Views",
            "",
            f"- [Open the faceted explorer]({page_link(current_relative, 'explorer.md')})",
            f"- [Browse by service]({page_link(current_relative, 'by-service.md')})",
            f"- [Browse by system]({page_link(current_relative, 'by-system.md')})",
            f"- [Browse by tag]({page_link(current_relative, 'by-tag.md')})",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_authors_page(
    articles: list,
    taxonomies: dict[str, dict[str, object]],
    duplicate_candidates: list,
) -> str:
    current_relative = Path("knowledge/authors.md")
    cards = []
    for title, description, target in AUTHOR_SHORTCUTS:
        href = (
            target["page"] if target else repo_doc_href(current_relative, "docs/playbooks/write.md")
        )
        cards.append(
            (
                title,
                description,
                href if target is None else page_href(current_relative, target["page"]),
            )
        )

    missing_services = len(articles_missing_list_field(articles, "services"))
    missing_systems = len(articles_missing_list_field(articles, "systems"))
    missing_tags = len(articles_missing_list_field(articles, "tags"))
    isolated = len(relationless_articles(articles))

    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Authoring Discovery",
        "",
        "Use this page before creating or revising a canonical knowledge object so new content lands with valid metadata and usable relationships.",
        "",
        render_card_grid(cards),
        "",
        "## Scaffold Workflow",
        "",
        "```bash",
        'python3 scripts/new_article.py --type runbook --title "Example Procedure" \\',
        '  --team "Service Desk" --audience service_desk \\',
        '  --service "Remote Access" --system "<VPN_SERVICE>" --tag vpn',
        "```",
        "",
        "List valid taxonomy values without opening individual files:",
        "",
        "```bash",
        "python3 scripts/new_article.py --list-taxonomy knowledge_object_types",
        "python3 scripts/new_article.py --list-taxonomy services",
        "python3 scripts/new_article.py --list-taxonomy systems",
        "python3 scripts/new_article.py --list-taxonomy tags",
        "```",
        "",
        "## Interoperability Checklist",
        "",
        "- Choose the narrowest valid `knowledge_object_type`, `audience`, `team`, `service`, `system`, and `tag` values that make the knowledge object discoverable.",
        "- Add `related_object_ids` for prerequisite, follow-on, escalation, or sibling procedures before merge.",
        "- Use `references` for canonical local paths or supporting knowledge-object links instead of duplicating content in `docs/`.",
        "- Review the faceted explorer and the content-health page to avoid creating duplicate or isolated knowledge objects.",
        "",
        render_metric_grid(
            [
                (str(missing_services), "knowledge objects missing service classification"),
                (str(missing_systems), "knowledge objects missing system classification"),
                (str(missing_tags), "knowledge objects missing tag classification"),
                (str(isolated), "isolated knowledge objects"),
                (str(len(duplicate_candidates)), "likely duplicate title pairs"),
            ]
        ),
        "",
        f"Discovery gaps: [content-health.md]({page_link(current_relative, 'content-health.md')})",
        "",
        render_taxonomy_table(
            "Knowledge Object Types",
            "knowledge_object_types",
            "type",
            taxonomies,
            articles,
            current_relative,
        ),
        render_taxonomy_table(
            "Audiences", "audiences", "audience", taxonomies, articles, current_relative
        ),
        render_taxonomy_table(
            "Services", "services", "services", taxonomies, articles, current_relative
        ),
        render_taxonomy_table(
            "Systems", "systems", "systems", taxonomies, articles, current_relative
        ),
        render_taxonomy_table("Tags", "tags", "tags", taxonomies, articles, current_relative),
        render_taxonomy_table("Teams", "teams", "team", taxonomies, articles, current_relative),
        "## Workflow References",
        "",
        f"- [Getting started]({repo_doc_link(current_relative, 'docs/getting-started.md')})",
        f"- [Content playbook]({repo_doc_link(current_relative, 'docs/playbooks/read.md')})",
        f"- [Authoring playbook]({repo_doc_link(current_relative, 'docs/playbooks/write.md')})",
        f"- [Oversight playbook]({repo_doc_link(current_relative, 'docs/playbooks/manage.md')})",
        f"- [System model]({repo_doc_link(current_relative, 'docs/reference/system-model.md')})",
        "",
    ]
    return "\n".join(lines).strip() + "\n"


def render_manager_page(
    articles: list,
    visible_articles: list,
    taxonomies: dict[str, dict[str, object]],
) -> str:
    current_relative = Path("knowledge/managers.md")
    cards = [
        (title, description, page_href(current_relative, target["page"]))
        for title, description, target in MANAGER_SHORTCUTS
    ]
    status_counts = Counter(article.metadata["object_lifecycle_state"] for article in articles)
    team_counts = Counter(article.metadata["team"] for article in articles)
    stale_rows = stale_articles(
        articles,
        taxonomies,
        dt.date.today(),
        {"active", "deprecated"},
    )
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Manager Audit",
        "",
        "This page is for coverage review, lifecycle visibility, and ownership audit across the canonical knowledge base.",
        "",
        render_card_grid(cards),
        "",
        render_metric_grid(
            [
                (str(len(visible_articles)), "current navigation articles"),
                (str(len(articles)), "total canonical knowledge objects"),
                (str(status_counts.get("deprecated", 0)), "deprecated articles"),
                (str(status_counts.get("archived", 0)), "archived articles"),
                (str(len(stale_rows)), "stale current articles"),
            ]
        ),
        "",
        "## Lifecycle Summary",
        "",
        "| Lifecycle | Count | Explorer |",
        "| --- | --- | --- |",
    ]
    for entry in taxonomies["statuses"]["values"]:
        status = entry["name"]
        lines.append(
            f"| `{status}` | {status_counts.get(status, 0)} | "
            f"[open]({explorer_link(current_relative, object_lifecycle_state=status)}) |"
        )
    lines.extend(
        [
            "",
            "## Team Ownership Summary",
            "",
            "| Team | Count | Explorer |",
            "| --- | --- | --- |",
        ]
    )
    for team in sorted(team_counts):
        lines.append(
            f"| `{markdown_table_cell(team)}` | {team_counts[team]} | "
            f"[open]({explorer_link(current_relative, team=team)}) |"
        )

    replacement_pairs = [article for article in articles if article.metadata.get("replaced_by")]
    lines.extend(
        [
            "",
            "## Replacement Chains",
            "",
        ]
    )
    if not replacement_pairs:
        lines.append("No replacement chains are currently documented.")
        lines.append("")
    else:
        for article in sorted(replacement_pairs, key=lambda item: item.metadata["title"]):
            lines.append(
                f"- {article_link(article, current_relative)} -> `{article.metadata['replaced_by']}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Audit Shortcuts",
            "",
            f"- [Content health view]({page_link(current_relative, 'content-health.md')})",
            f"- [Coverage matrix]({page_link(current_relative, 'coverage-matrix.md')})",
            f"- [Knowledge tree]({page_link(current_relative, 'tree.md')})",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_tree_page(articles: list) -> str:
    current_relative = Path("knowledge/tree.md")
    grouped = defaultdict(list)
    for article in articles:
        key = Path(article.relative_path).parent.as_posix()
        grouped[key].append(article)

    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Knowledge Tree",
        "",
        "This view mirrors the canonical repository path layout so managers can audit coverage by section.",
        "",
    ]
    for directory in sorted(grouped):
        lines.append(f"## `{directory}` ({len(grouped[directory])})")
        lines.append("")
        lines.append(
            f"Explorer view: [Search this section]"
            f"({explorer_link(current_relative, query=directory.replace('knowledge/', ''))})"
        )
        lines.append("")
        for article in sorted(grouped[directory], key=lambda item: item.metadata["title"]):
            lines.append(render_article_bullet(article, current_relative))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_articles_section(
    title: str,
    articles: list,
    current_relative: Path,
    filter_link: str | None = None,
    empty_message: str = "None.",
) -> list[str]:
    lines = [f"## {title}", ""]
    if filter_link:
        lines.append(filter_link)
        lines.append("")
    if not articles:
        lines.append(empty_message)
        lines.append("")
        return lines
    for article in sorted(articles, key=lambda item: item.metadata["title"]):
        lines.append(render_article_bullet(article, current_relative))
    lines.append("")
    return lines


def render_content_health_page(
    articles: list,
    taxonomies: dict[str, dict[str, object]],
    policy: dict[str, object],
) -> str:
    current_relative = Path("knowledge/content-health.md")
    duplicate_candidates = find_possible_duplicate_articles(
        articles,
        float(policy["duplicate_detection"]["title_similarity_threshold"]),
    )
    missing_services = articles_missing_list_field(articles, "services")
    missing_systems = articles_missing_list_field(articles, "systems")
    missing_tags = articles_missing_list_field(articles, "tags")
    missing_owners = missing_owner_articles(articles)
    isolated = relationless_articles(articles)
    stale_rows = stale_articles(articles, taxonomies, dt.date.today(), {"active", "deprecated"})
    status_counts = Counter(article.metadata["object_lifecycle_state"] for article in articles)

    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Content Health",
        "",
        "This page exposes discovery and lifecycle gaps as generated browse surfaces rather than CLI-only output.",
        "",
        render_metric_grid(
            [
                (str(len(duplicate_candidates)), "likely duplicate title pairs"),
                (str(len(isolated)), "isolated articles"),
                (str(len(missing_services)), "articles missing services"),
                (str(len(missing_systems)), "articles missing systems"),
                (str(len(missing_tags)), "articles missing tags"),
                (str(len(stale_rows)), "stale active or deprecated articles"),
            ]
        ),
        "",
        "## Lifecycle Visibility",
        "",
        "| Lifecycle | Count | Explorer |",
        "| --- | --- | --- |",
    ]
    for entry in taxonomies["statuses"]["values"]:
        status = entry["name"]
        lines.append(
            f"| `{status}` | {status_counts.get(status, 0)} | "
            f"[open]({explorer_link(current_relative, object_lifecycle_state=status)}) |"
        )
    lines.extend(
        [
            "",
            "## Likely Duplicate Candidates [Inference]",
            "",
        ]
    )
    if not duplicate_candidates:
        lines.append("No likely duplicate title pairs were detected.")
        lines.append("")
    else:
        for candidate in duplicate_candidates:
            left_path = site_relative_path_for_repo_path(candidate.left_path) or Path(
                candidate.left_path
            )
            right_path = site_relative_path_for_repo_path(candidate.right_path) or Path(
                candidate.right_path
            )
            left_href = relative_site_link(current_relative, left_path)
            right_href = relative_site_link(current_relative, right_path)
            lines.append(
                f"- [Inference] `{candidate.left_title}` "
                f"([{candidate.left_path}]({left_href})) and "
                f"`{candidate.right_title}` "
                f"([{candidate.right_path}]({right_href})) "
                f"have title similarity {candidate.similarity:.2f} without explicit linkage."
            )
        lines.append("")

    lines.extend(
        render_articles_section(
            "Missing Owner Assignments",
            missing_owners,
            current_relative,
            f"Explorer view: [owner=unassigned]({explorer_link(current_relative, owner='__none__')})",
            "No owner gaps were detected.",
        )
    )
    lines.extend(
        render_articles_section(
            "Missing Service Classification",
            missing_services,
            current_relative,
            f"Explorer view: [service=unclassified]({explorer_link(current_relative, service='__none__')})",
            "No service-classification gaps were detected.",
        )
    )
    lines.extend(
        render_articles_section(
            "Missing System Classification",
            missing_systems,
            current_relative,
            f"Explorer view: [system=unclassified]({explorer_link(current_relative, system='__none__')})",
            "No system-classification gaps were detected.",
        )
    )
    lines.extend(
        render_articles_section(
            "Missing Tag Classification",
            missing_tags,
            current_relative,
            f"Explorer view: [tag=unclassified]({explorer_link(current_relative, tag='__none__')})",
            "No tag-classification gaps were detected.",
        )
    )
    lines.extend(
        render_articles_section(
            "Isolated Articles",
            isolated,
            current_relative,
            empty_message="No isolated articles were detected.",
        )
    )

    lines.extend(["## Stale Current Content", ""])
    if not stale_rows:
        lines.append("No active or deprecated articles are currently overdue for review.")
        lines.append("")
    else:
        for days_overdue, article, due_date in stale_rows:
            lines.append(
                f"- {article_link(article, current_relative)} - due {due_date.isoformat()} "
                f"({days_overdue} days overdue)"
            )
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_coverage_matrix_page(articles: list, taxonomies: dict[str, dict[str, object]]) -> str:
    current_relative = Path("knowledge/coverage-matrix.md")
    type_order = [entry["name"] for entry in taxonomies["knowledge_object_types"]["values"]]
    service_order = [entry["name"] for entry in taxonomies["services"]["values"]]
    articles_by_service_type = defaultdict(int)
    unclassified_label = "Unclassified"

    for article in articles:
        services = article.metadata["services"] or [unclassified_label]
        for service in services:
            articles_by_service_type[(service, primary_object_type(article))] += 1

    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Coverage Matrix",
        "",
        "Counts below show canonical knowledge-object coverage by service and knowledge-object type. Each count links back into the explorer for follow-up review.",
        "",
        "| Service | " + " | ".join(type_order) + " | Total |",
        "| --- | " + " | ".join("---" for _ in type_order) + " | --- |",
    ]
    for service in [*service_order, unclassified_label]:
        row_total = 0
        cells = []
        for article_type in type_order:
            count = articles_by_service_type[(service, article_type)]
            row_total += count
            if count:
                service_filter = "__none__" if service == unclassified_label else service
                cells.append(
                    f"[{count}]({explorer_link(current_relative, service=service_filter, type=article_type)})"
                )
            else:
                cells.append("0")
        lines.append(f"| `{service}` | " + " | ".join(cells) + f" | {row_total} |")
    lines.append("")
    return "\n".join(lines)


def render_landing_page(
    articles: list,
    visible_articles: list,
    taxonomies: dict[str, dict[str, object]],
) -> str:
    current_relative = Path("knowledge/index.md")
    cards = [
        (
            "Support",
            "Task-oriented entry points for support specialists.",
            page_href(current_relative, "support.md"),
        ),
        (
            "Explorer",
            "Faceted browsing across canonical metadata.",
            page_href(current_relative, "explorer.md"),
        ),
        (
            "Knowledge Tree",
            "Repository-path view for auditing the canonical structure.",
            page_href(current_relative, "tree.md"),
        ),
        (
            "By Service",
            "Browse approved export content grouped by service area.",
            page_href(current_relative, "by-service.md"),
        ),
        (
            "By Type",
            "Browse approved export content grouped by knowledge object type.",
            page_href(current_relative, "by-type.md"),
        ),
    ]
    status_counts = Counter(article.metadata["object_lifecycle_state"] for article in articles)
    metrics = [
        (str(len(visible_articles)), "approved navigation articles"),
        (str(len(articles)), "approved export knowledge objects"),
        (str(len(taxonomies["services"]["values"])), "service taxonomy values"),
        (str(len(taxonomies["systems"]["values"])), "system taxonomy values"),
        (str(status_counts.get("deprecated", 0)), "deprecated approved exports"),
        (str(status_counts.get("archived", 0)), "archived approved exports"),
    ]
    lines = [
        "<!-- Generated from canonical source content. Do not edit here. -->",
        "",
        "# Knowledge Base",
        "",
        "This landing page exposes the approved static export of Papyrus knowledge objects.",
        "",
        "The interactive operator queue, trust dashboard, and impact views live in the runtime-backed web and API surfaces, not in this export.",
        "",
        render_card_grid(cards),
        "",
        render_metric_grid(metrics),
        "",
        "## Faceted Browse Views",
        "",
        f"- [By type]({page_link(current_relative, 'by-type.md')})",
        f"- [By audience]({page_link(current_relative, 'by-audience.md')})",
        f"- [By service]({page_link(current_relative, 'by-service.md')})",
        f"- [By system]({page_link(current_relative, 'by-system.md')})",
        f"- [By tag]({page_link(current_relative, 'by-tag.md')})",
        f"- [By team]({page_link(current_relative, 'by-team.md')})",
        f"- [By lifecycle]({page_link(current_relative, 'by-lifecycle.md')})",
        "",
        "## Workflow Entry Points",
        "",
    ]
    for title, article_ids in WORKFLOW_STARTERS:
        lines.append(f"### {title}")
        lines.append("")
        lines.append(
            f"Explorer view: [Open related content]({explorer_link(current_relative, query=title.lower())})"
        )
        lines.append("")
        for article_id in article_ids:
            article = next((item for item in articles if item.metadata["id"] == article_id), None)
            if not article:
                continue
            lines.append(render_article_bullet(article, current_relative))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the optional approved-only Papyrus static export."
    )
    parser.add_argument(
        "--db",
        default=str(DB_PATH),
        help="Path to the runtime SQLite database used for approval gating.",
    )
    parser.add_argument(
        "--output-root",
        default=str(GENERATED_SITE_DOCS_DIR),
        help="Directory to write the generated site-doc export into.",
    )
    args = parser.parse_args()
    _configure_generated_output_roots(Path(args.output_root).resolve())

    policy = load_policy()
    taxonomies = load_taxonomies()
    source_articles = load_articles(policy)
    docs_paths = collect_docs_source_paths()
    decision_paths = collect_decision_paths()
    try:
        approved_ids = approved_export_object_ids(args.db)
    except ExportRuntimeUnavailableError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    articles = [article for article in source_articles if article.metadata["id"] in approved_ids]
    excluded_count = len(source_articles) - len(articles)
    by_id = {article.metadata["id"]: article for article in articles}
    visible_status_list = navigation_statuses(policy)
    visible_statuses = set(visible_status_list)
    visible_articles = [
        article
        for article in articles
        if article.metadata["object_lifecycle_state"] in visible_statuses
    ]
    archived_articles = [
        article for article in articles if article.metadata["object_lifecycle_state"] == "archived"
    ]
    outbound_graph = reference_graph(articles)
    inbound_graph = inverse_reference_graph(outbound_graph)
    allowed_repo_paths = {
        *(article.relative_path for article in articles),
        *(relative_path(path) for path in docs_paths),
        *(relative_path(path) for path in decision_paths),
    }

    if GENERATED_SITE_DOCS_DIR.exists():
        shutil.rmtree(GENERATED_SITE_DOCS_DIR)
    GENERATED_SITE_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if LEGACY_GENERATED_DOCS_DIR.exists():
        shutil.rmtree(LEGACY_GENERATED_DOCS_DIR)

    copy_source_tree(
        DOCS_DIR,
        GENERATED_SITE_DOCS_DIR / "system-design-docs",
        docs_paths,
        allowed_repo_paths=allowed_repo_paths,
    )
    copy_source_tree(
        DECISIONS_DIR,
        GENERATED_SITE_DOCS_DIR / "decisions",
        decision_paths,
        allowed_repo_paths=allowed_repo_paths,
    )
    (GENERATED_SITE_DOCS_DIR / "index.md").write_text(
        render_site_home(articles, docs_paths, decision_paths, excluded_count),
        encoding="utf-8",
    )

    for article in articles:
        destination = site_article_output_path(article)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            render_article_page(article, by_id, articles, inbound_graph, allowed_repo_paths),
            encoding="utf-8",
        )

    by_type = defaultdict(list)
    by_audience = defaultdict(list)
    by_service = defaultdict(list)
    by_system = defaultdict(list)
    by_tag = defaultdict(list)
    by_team = defaultdict(list)
    by_status = defaultdict(list)

    for article in visible_articles:
        by_type[primary_object_type(article)].append(article)
        by_audience[article.metadata["audience"]].append(article)
        by_team[article.metadata["team"]].append(article)
        for service in article.metadata["services"] or ["Unclassified"]:
            by_service[service].append(article)
        for system in article.metadata["systems"] or ["Unclassified"]:
            by_system[system].append(article)
        for tag in article.metadata["tags"] or ["Unclassified"]:
            by_tag[tag].append(article)

    for article in articles:
        by_status[article.metadata["object_lifecycle_state"]].append(article)

    knowledge_root = GENERATED_SITE_DOCS_DIR / "knowledge"
    knowledge_root.mkdir(parents=True, exist_ok=True)
    (knowledge_root / "index.md").write_text(
        render_landing_page(articles, visible_articles, taxonomies),
        encoding="utf-8",
    )
    (knowledge_root / "start-here.md").write_text(render_start_here(by_id), encoding="utf-8")
    (knowledge_root / "support.md").write_text(render_support_page(by_id), encoding="utf-8")
    (knowledge_root / "explorer.md").write_text(
        render_explorer_page(articles, taxonomies, visible_status_list),
        encoding="utf-8",
    )
    (knowledge_root / "tree.md").write_text(render_tree_page(articles), encoding="utf-8")
    (knowledge_root / "by-type.md").write_text(
        render_grouped_index_page(
            "Knowledge By Type",
            "Browse current knowledge grouped by knowledge-object type.",
            by_type,
            "knowledge/by-type.md",
            "type",
            [entry["name"] for entry in taxonomies["knowledge_object_types"]["values"]],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-audience.md").write_text(
        render_grouped_index_page(
            "Knowledge By Audience",
            "Browse current knowledge grouped by primary audience.",
            by_audience,
            "knowledge/by-audience.md",
            "audience",
            [entry["name"] for entry in taxonomies["audiences"]["values"]],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-service.md").write_text(
        render_grouped_index_page(
            "Knowledge By Service",
            "Browse current knowledge grouped by service area.",
            by_service,
            "knowledge/by-service.md",
            "service",
            [entry["name"] for entry in taxonomies["services"]["values"]] + ["Unclassified"],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-system.md").write_text(
        render_grouped_index_page(
            "Knowledge By System",
            "Browse current knowledge grouped by system.",
            by_system,
            "knowledge/by-system.md",
            "system",
            [entry["name"] for entry in taxonomies["systems"]["values"]] + ["Unclassified"],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-tag.md").write_text(
        render_grouped_index_page(
            "Knowledge By Tag",
            "Browse current knowledge grouped by tag.",
            by_tag,
            "knowledge/by-tag.md",
            "tag",
            [entry["name"] for entry in taxonomies["tags"]["values"]] + ["Unclassified"],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-team.md").write_text(
        render_grouped_index_page(
            "Knowledge By Team",
            "Browse current knowledge grouped by owning team.",
            by_team,
            "knowledge/by-team.md",
            "team",
            [entry["name"] for entry in taxonomies["teams"]["values"]],
        ),
        encoding="utf-8",
    )
    (knowledge_root / "by-lifecycle.md").write_text(
        render_grouped_index_page(
            "Knowledge By Lifecycle",
            "Browse approved export knowledge grouped by lifecycle state.",
            by_status,
            "knowledge/by-lifecycle.md",
            "object_lifecycle_state",
            [entry["name"] for entry in taxonomies["statuses"]["values"]],
        ),
        encoding="utf-8",
    )

    archive_root = GENERATED_SITE_DOCS_DIR / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    (archive_root / "index.md").write_text(
        render_archive_index(archived_articles), encoding="utf-8"
    )

    expected_pages = {relative_path for relative_path in GENERATED_SITE_INDEX_PATHS}
    print(
        f"generated approved static export for {len(articles)} knowledge object(s) "
        f"and excluded {excluded_count} source object(s) across {len(expected_pages)} generated indexes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
