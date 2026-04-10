from __future__ import annotations

import json
import sqlite3
from collections import deque
from typing import Any

import yaml

from papyrus.application.runtime_projection import refresh_current_object_projection
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.domain.events import EventBase
from papyrus.domain.entities import AuditEvent, DocsPlacementWarning, DuplicateCandidate, KnowledgeDocument
from papyrus.domain.policies import worse_trust_state
from papyrus.infrastructure.markdown.parser import extract_markdown_title
from papyrus.infrastructure.markdown.serializer import json_dump, similarity_ratio
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.paths import (
    DOCS_OPERATOR_LANGUAGE_PATTERNS,
    FRONT_MATTER_PATTERN,
    OPERATIONAL_HEADING_PATTERN,
    ROOT,
)
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_docs_source_paths,
    load_object_schemas,
    load_schema,
    update_knowledge_object_runtime_state,
)
from papyrus.infrastructure.repositories.knowledge_repo import get_knowledge_object
from papyrus.infrastructure.repositories.knowledge_repo import get_knowledge_revision
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies


def explicitly_linked(left: KnowledgeDocument, right: KnowledgeDocument) -> bool:
    left_related = set(left.metadata.get("related_object_ids", []) or left.metadata.get("related_articles", []))
    right_related = set(right.metadata.get("related_object_ids", []) or right.metadata.get("related_articles", []))
    replacements = {
        left.metadata.get("superseded_by") or left.metadata.get("replaced_by"),
        right.metadata.get("superseded_by") or right.metadata.get("replaced_by"),
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
        links = set(document.metadata.get("related_object_ids", []) or document.metadata.get("related_articles", []))
        replaced_by = document.metadata.get("superseded_by") or document.metadata.get("replaced_by")
        if replaced_by:
            links.add(replaced_by)
        references = document.metadata.get("citations") or document.metadata.get("references", [])
        for reference in references:
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
    if schema is None:
        article_fields = set(load_schema().get("fields", {}))
        for object_schema in load_object_schemas().values():
            article_fields.update(object_schema.get("fields", {}))
    else:
        article_fields = set(schema.get("fields", {}))
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
                    signals.append(f"front matter overlaps knowledge-object schemas: {preview}")
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


def mark_object_suspect_due_to_change(
    *,
    object_id: str,
    actor: str,
    reason: str,
    changed_entity_type: str,
    changed_entity_id: str | None = None,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
    database_path=DB_PATH,
) -> AuditEvent:
    from papyrus.application.review_flow import mark_object_suspect_due_to_change as review_flow_mark_suspect

    return review_flow_mark_suspect(
        database_path=database_path,
        source_root=source_root,
        object_id=object_id,
        actor=actor,
        reason=reason,
        changed_entity_type=changed_entity_type,
        changed_entity_id=changed_entity_id,
        authority=authority,
    )


def _event_summary(event_type: str, entity_type: str, entity_id: str, payload: dict[str, Any]) -> str:
    return str(payload.get("summary") or payload.get("reason") or f"{event_type} on {entity_type} {entity_id}")


def _json_dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return loaded if isinstance(loaded, dict) else {}
    return {}


def _object_rows(connection: sqlite3.Connection, object_ids: set[str]) -> dict[str, sqlite3.Row]:
    if not object_ids:
        return {}
    placeholders = ", ".join("?" for _ in object_ids)
    rows = connection.execute(
        f"""
        SELECT object_id, object_type, title, canonical_path, trust_state, current_revision_id
        FROM knowledge_objects
        WHERE object_id IN ({placeholders})
        """,
        tuple(sorted(object_ids)),
    ).fetchall()
    return {str(row["object_id"]): row for row in rows}


def _service_seed_impacts(
    connection: sqlite3.Connection,
    *,
    entity_id: str,
    summary: str,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT DISTINCT
            s.service_id,
            s.service_name,
            o.object_id,
            o.title
        FROM services AS s
        JOIN relationships AS r
          ON r.target_entity_type = 'service'
         AND r.target_entity_id = s.service_id
        JOIN knowledge_objects AS o
          ON o.object_id = r.source_entity_id
        WHERE s.service_id = ? OR s.service_name = ?
        ORDER BY o.title
        """,
        (entity_id, entity_id),
    ).fetchall()
    impacts: list[dict[str, Any]] = []
    for row in rows:
        impacts.append(
            {
                "object_id": str(row["object_id"]),
                "score": 0.9,
                "reason": f"Linked to changed service {row['service_name']}.",
                "path": [f"service:{row['service_name']}", f"object:{row['object_id']}"],
                "what_changed": summary,
                "changed_entity_type": "service",
                "changed_entity_id": str(row["service_id"]),
            }
        )
    return impacts


def _citation_seed_impacts(
    connection: sqlite3.Connection,
    *,
    source_ref: str,
    summary: str,
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT DISTINCT o.object_id
        FROM citations AS c
        JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
        JOIN knowledge_objects AS o ON o.object_id = r.object_id
        WHERE o.current_revision_id = r.revision_id
          AND c.source_ref = ?
        ORDER BY o.object_id
        """,
        (source_ref,),
    ).fetchall()
    return [
        {
            "object_id": str(row["object_id"]),
            "score": 0.85,
            "reason": f"Cites changed evidence source {source_ref}.",
            "path": [f"evidence:{source_ref}", f"object:{row['object_id']}"],
            "what_changed": summary,
            "changed_entity_type": "evidence",
            "changed_entity_id": source_ref,
        }
        for row in rows
    ]


def _seed_impacts(
    connection: sqlite3.Connection,
    *,
    changed_entity_type: str,
    changed_entity_id: str,
    payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    summary = _event_summary("change", changed_entity_type, changed_entity_id, payload or {})
    payload = payload or {}

    if changed_entity_type == "service":
        return _service_seed_impacts(connection, entity_id=changed_entity_id, summary=summary)
    if changed_entity_type in {"citation_target", "source_path", "evidence"}:
        return _citation_seed_impacts(connection, source_ref=changed_entity_id, summary=summary)

    seed_object_ids = [changed_entity_id] if changed_entity_type == "knowledge_object" else []
    seed_object_ids.extend(str(item) for item in payload.get("object_ids", []) if str(item).strip())
    return [
        {
            "object_id": object_id,
            "score": 1.0,
            "reason": f"Changed entity directly references {object_id}.",
            "path": [f"{changed_entity_type}:{changed_entity_id}", f"object:{object_id}"],
            "what_changed": summary,
            "changed_entity_type": changed_entity_type,
            "changed_entity_id": changed_entity_id,
        }
        for object_id in dict.fromkeys(seed_object_ids)
    ]


def _relationship_adjacency(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT
            relationship_type,
            relationship_strength,
            relationship_direction,
            source_entity_id,
            target_entity_id
        FROM relationships
        WHERE source_entity_type = 'knowledge_object'
          AND target_entity_type = 'knowledge_object'
        """
    ).fetchall()
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        strength = float(row["relationship_strength"] or 0)
        if strength <= 0:
            continue
        source_id = str(row["source_entity_id"])
        target_id = str(row["target_entity_id"])
        relationship_type = str(row["relationship_type"])
        direction = str(row["relationship_direction"])
        if direction in {"forward", "bidirectional"}:
            adjacency.setdefault(source_id, []).append(
                {"next_object_id": target_id, "relationship_type": relationship_type, "strength": strength}
            )
        if direction in {"reverse", "bidirectional"}:
            adjacency.setdefault(target_id, []).append(
                {"next_object_id": source_id, "relationship_type": relationship_type, "strength": strength}
            )
    return adjacency


def _citation_dependents(connection: sqlite3.Connection, source_ref: str, *, exclude_object_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT DISTINCT o.object_id
        FROM citations AS c
        JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
        JOIN knowledge_objects AS o ON o.object_id = r.object_id
        WHERE o.current_revision_id = r.revision_id
          AND c.source_ref = ?
          AND o.object_id != ?
        ORDER BY o.object_id
        """,
        (source_ref, exclude_object_id),
    ).fetchall()
    return [
        {"next_object_id": str(row["object_id"]), "relationship_type": "citation_dependency", "strength": 0.8}
        for row in rows
    ]


def _revalidation_actions(object_row: sqlite3.Row, reason: str) -> list[str]:
    object_type = str(object_row["object_type"])
    if object_type == "runbook":
        return [
            f"Revalidate prerequisites, steps, and verification because {reason.lower()}",
            "Confirm rollback guidance still matches the changed dependency.",
        ]
    if object_type == "known_error":
        return [
            f"Revalidate diagnostics and mitigations because {reason.lower()}",
            "Confirm citations still support the failure pattern and scope.",
        ]
    return [
        f"Revalidate dependencies and support entrypoints because {reason.lower()}",
        "Confirm common failure modes still describe the current service posture.",
    ]


def calculate_blast_radius(
    connection: sqlite3.Connection,
    *,
    changed_entity_type: str,
    changed_entity_id: str,
    payload: dict[str, Any] | None = None,
    max_depth: int = 3,
    min_score: float = 0.35,
) -> list[dict[str, Any]]:
    seeds = _seed_impacts(
        connection,
        changed_entity_type=changed_entity_type,
        changed_entity_id=changed_entity_id,
        payload=payload,
    )
    if not seeds:
        return []

    adjacency = _relationship_adjacency(connection)
    object_ids = {item["object_id"] for item in seeds}
    best_scores: dict[str, float] = {}
    impacts: dict[str, dict[str, Any]] = {}
    queue = deque((item, 0) for item in seeds)

    while queue:
        impact, depth = queue.popleft()
        object_id = str(impact["object_id"])
        score = float(impact["score"])
        if score < min_score or score <= best_scores.get(object_id, 0.0):
            continue
        best_scores[object_id] = score
        impacts[object_id] = {
            **impact,
            "depth": depth,
        }

        if depth >= max_depth:
            continue

        for edge in adjacency.get(object_id, []):
            next_score = round(score * float(edge["strength"]), 3)
            if next_score < min_score:
                continue
            next_object_id = str(edge["next_object_id"])
            queue.append(
                (
                    {
                        "object_id": next_object_id,
                        "score": next_score,
                        "reason": f"Depends on {object_id} via {edge['relationship_type']}.",
                        "path": [*impact["path"], f"object:{next_object_id}"],
                        "what_changed": impact["what_changed"],
                        "changed_entity_type": impact["changed_entity_type"],
                        "changed_entity_id": impact["changed_entity_id"],
                    },
                    depth + 1,
                )
            )

        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            continue
        for edge in _citation_dependents(connection, str(object_row["canonical_path"]), exclude_object_id=object_id):
            next_object_id = str(edge["next_object_id"])
            next_score = round(score * float(edge["strength"]), 3)
            if next_score < min_score:
                continue
            queue.append(
                (
                    {
                        "object_id": next_object_id,
                        "score": next_score,
                        "reason": f"Cites changed object {object_id}.",
                        "path": [*impact["path"], f"object:{next_object_id}"],
                        "what_changed": impact["what_changed"],
                        "changed_entity_type": impact["changed_entity_type"],
                        "changed_entity_id": impact["changed_entity_id"],
                    },
                    depth + 1,
                )
            )

    rows = _object_rows(connection, set(impacts))
    enriched: list[dict[str, Any]] = []
    for object_id, impact in impacts.items():
        row = rows.get(object_id)
        if row is None:
            continue
        enriched.append(
            {
                "object_id": object_id,
                "object_type": str(row["object_type"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "trust_state": str(row["trust_state"]),
                "current_revision_id": str(row["current_revision_id"]) if row["current_revision_id"] is not None else None,
                "impact_score": float(impact["score"]),
                "reason": str(impact["reason"]),
                "propagation_path": list(impact["path"]),
                "what_changed": str(impact["what_changed"]),
                "revalidate": _revalidation_actions(row, str(impact["reason"])),
                "changed_entity_type": str(impact["changed_entity_type"]),
                "changed_entity_id": str(impact["changed_entity_id"]),
            }
        )
    enriched.sort(key=lambda item: (-float(item["impact_score"]), item["title"]))
    return enriched


def determine_trust_degradation(
    *,
    current_trust_state: str,
    impact_score: float,
    event_type: str,
    payload: dict[str, Any] | None = None,
) -> str:
    payload = payload or {}
    proposed = str(payload.get("trust_state") or "").strip()
    if proposed:
        return worse_trust_state(current_trust_state, proposed)
    if event_type.startswith("evidence_"):
        return worse_trust_state(current_trust_state, "weak_evidence")
    if event_type.startswith("validation_"):
        return worse_trust_state(current_trust_state, "suspect")
    if impact_score >= 0.35:
        return worse_trust_state(current_trust_state, "suspect")
    return current_trust_state


def propagate_change_event(
    connection: sqlite3.Connection,
    *,
    event: EventBase,
) -> list[dict[str, Any]]:
    impacts = calculate_blast_radius(
        connection,
        changed_entity_type=event.entity_type,
        changed_entity_id=event.entity_id,
        payload=event.payload,
    )
    if not impacts:
        return []

    taxonomies = load_taxonomies()
    for impact in impacts:
        object_row = get_knowledge_object(connection, impact["object_id"])
        if object_row is None:
            continue
        next_trust_state = determine_trust_degradation(
            current_trust_state=str(object_row["trust_state"]),
            impact_score=float(impact["impact_score"]),
            event_type=event.event_type,
            payload=event.payload,
        )
        update_knowledge_object_runtime_state(
            connection,
            object_id=impact["object_id"],
            trust_state=next_trust_state,
        )
        refresh_current_object_projection(
            connection,
            object_id=impact["object_id"],
            taxonomies=taxonomies,
        )
        refreshed = get_knowledge_object(connection, impact["object_id"])
        impact["trust_state_before"] = str(object_row["trust_state"])
        impact["trust_state_after"] = str(refreshed["trust_state"]) if refreshed is not None else next_trust_state
        revision_id = str(refreshed["current_revision_id"]) if refreshed and refreshed["current_revision_id"] is not None else None
        insert_audit_event(
            connection,
            event_id=f"impact-{event.event_id}-{impact['object_id']}",
            event_type="impact_propagated",
            occurred_at=event.occurred_at.isoformat(),
            actor=event.actor,
            object_id=impact["object_id"],
            revision_id=revision_id,
            details_json=json_dump(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "changed_entity_type": event.entity_type,
                    "changed_entity_id": event.entity_id,
                    "what_changed": impact["what_changed"],
                    "reason": impact["reason"],
                    "impact_score": impact["impact_score"],
                    "propagation_path": impact["propagation_path"],
                    "revalidate": impact["revalidate"],
                    "trust_state_before": impact["trust_state_before"],
                    "trust_state_after": impact["trust_state_after"],
                }
            ),
        )
    return impacts
