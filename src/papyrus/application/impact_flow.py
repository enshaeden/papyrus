from __future__ import annotations

from typing import Any

import yaml

from papyrus.domain.entities import DocsPlacementWarning, DuplicateCandidate, KnowledgeDocument
from papyrus.infrastructure.markdown.parser import extract_markdown_title
from papyrus.infrastructure.markdown.serializer import similarity_ratio
from papyrus.infrastructure.paths import (
    DOCS_OPERATOR_LANGUAGE_PATTERNS,
    FRONT_MATTER_PATTERN,
    OPERATIONAL_HEADING_PATTERN,
    ROOT,
)
from papyrus.infrastructure.repositories.knowledge_repo import collect_docs_source_paths, load_schema


def explicitly_linked(left: KnowledgeDocument, right: KnowledgeDocument) -> bool:
    left_related = set(left.metadata.get("related_articles", []))
    right_related = set(right.metadata.get("related_articles", []))
    replacements = {
        left.metadata.get("replaced_by"),
        right.metadata.get("replaced_by"),
    }
    return (
        right.knowledge_object_id in left_related
        or left.knowledge_object_id in right_related
        or left.knowledge_object_id in replacements
        or right.knowledge_object_id in replacements
    )


def find_possible_duplicate_documents(
    documents: list[KnowledgeDocument],
    threshold: float,
) -> list[DuplicateCandidate]:
    duplicates: list[DuplicateCandidate] = []
    for index, left in enumerate(documents):
        for right in documents[index + 1 :]:
            if explicitly_linked(left, right):
                continue
            similarity = similarity_ratio(left.metadata.get("title", ""), right.metadata.get("title", ""))
            if similarity >= threshold:
                duplicates.append(
                    DuplicateCandidate(
                        left_path=left.relative_path,
                        right_path=right.relative_path,
                        left_title=left.metadata.get("title", ""),
                        right_title=right.metadata.get("title", ""),
                        similarity=similarity,
                    )
                )
    return duplicates


def reference_graph(documents: list[KnowledgeDocument]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for document in documents:
        links = set(document.metadata.get("related_articles", []))
        replaced_by = document.metadata.get("replaced_by")
        if replaced_by:
            links.add(replaced_by)
        for reference in document.metadata.get("references", []):
            article_id = reference.get("article_id")
            if article_id:
                links.add(article_id)
        graph[document.knowledge_object_id] = links
    return graph


def inverse_reference_graph(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    inverse: dict[str, set[str]] = {key: set() for key in graph}
    for source, targets in graph.items():
        for target in targets:
            inverse.setdefault(target, set()).add(source)
    return inverse


def docs_knowledge_like_warnings(
    schema: dict[str, Any] | None = None,
) -> list[DocsPlacementWarning]:
    article_fields = set((schema or load_schema()).get("fields", {}))
    warnings: list[DocsPlacementWarning] = []

    for path in collect_docs_source_paths():
        if path.suffix != ".md":
            continue

        text = path.read_text(encoding="utf-8")
        body = text
        signals: list[str] = []
        score = 0
        has_front_matter_signal = False

        match = FRONT_MATTER_PATTERN.match(text)
        if match:
            metadata = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
            if isinstance(metadata, dict):
                overlapping_fields = sorted(set(metadata).intersection(article_fields))
                strong_fields = [
                    field
                    for field in overlapping_fields
                    if field
                    in {
                        "canonical_path",
                        "last_reviewed",
                        "prerequisites",
                        "review_cadence",
                        "rollback",
                        "source_type",
                        "steps",
                        "verification",
                    }
                ]
                if strong_fields or len(overlapping_fields) >= 5:
                    has_front_matter_signal = True
                    preview_fields = strong_fields or overlapping_fields[:6]
                    preview = ", ".join(preview_fields)
                    if len(overlapping_fields) > len(preview_fields):
                        preview += ", ..."
                    signals.append(f"front matter overlaps article schema: {preview}")
                    score += 5 + len(strong_fields)

        heading_hits = sorted({item.group(1).title() for item in OPERATIONAL_HEADING_PATTERN.finditer(body)})
        if heading_hits:
            signals.append("operational headings: " + ", ".join(heading_hits))
            score += len(heading_hits) * 2

        phrase_hits = [label for label, pattern in DOCS_OPERATOR_LANGUAGE_PATTERNS if pattern.search(body)]
        if phrase_hits:
            signals.append("operator-oriented language: " + ", ".join(phrase_hits))
            score += len(phrase_hits)

        has_procedural_language_signal = "procedural phrasing" in phrase_hits
        should_warn = (
            has_front_matter_signal
            or len(heading_hits) >= 2
            or (len(heading_hits) >= 1 and len(phrase_hits) >= 1)
            or (has_procedural_language_signal and len(phrase_hits) >= 2)
        )
        if should_warn:
            warnings.append(
                DocsPlacementWarning(
                    path=path.relative_to(ROOT).as_posix(),
                    score=score,
                    signals=signals,
                )
            )

    return sorted(warnings, key=lambda item: (-item.score, item.path))


def relationless_documents(documents: list[KnowledgeDocument]) -> list[KnowledgeDocument]:
    graph = reference_graph(documents)
    inverse = inverse_reference_graph(graph)
    isolated = []
    for document in documents:
        outbound = graph.get(document.knowledge_object_id, set())
        inbound = inverse.get(document.knowledge_object_id, set())
        if not outbound and not inbound:
            isolated.append(document)
    return isolated


def missing_owner_documents(documents: list[KnowledgeDocument]) -> list[KnowledgeDocument]:
    return [document for document in documents if not str(document.metadata.get("owner", "")).strip()]


def documents_missing_list_field(documents: list[KnowledgeDocument], field_name: str) -> list[KnowledgeDocument]:
    return [document for document in documents if not document.metadata.get(field_name)]

