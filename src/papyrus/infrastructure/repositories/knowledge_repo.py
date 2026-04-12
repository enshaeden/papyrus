from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml

from papyrus.domain.entities import KnowledgeDocument
from papyrus.domain.policies import relationship_direction_for, relationship_strength_for
from papyrus.infrastructure.markdown.parser import parse_knowledge_document
from papyrus.infrastructure.paths import (
    ARTICLE_SCHEMA_PATH,
    DECISIONS_DIR,
    DOCS_DIR,
    GENERATED_SITE_DOCS_DIR,
    OBJECT_SCHEMA_DIR,
    POLICY_PATH,
    REPORTS_DIR,
    ROOT,
    TAXONOMY_DIR,
    TEMPLATE_DIR,
)


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping")
    return data


def load_schema(schema_path: Path = ARTICLE_SCHEMA_PATH) -> dict[str, Any]:
    return load_yaml_file(schema_path)


def load_object_schemas(schema_dir: Path = OBJECT_SCHEMA_DIR) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for path in sorted(schema_dir.glob("*.yml")):
        results[path.stem] = load_yaml_file(path)
    return results


def load_policy(policy_path: Path = POLICY_PATH) -> dict[str, Any]:
    return load_yaml_file(policy_path)


def load_taxonomies(taxonomy_dir: Path = TAXONOMY_DIR) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for path in sorted(taxonomy_dir.glob("*.yml")):
        data = load_yaml_file(path)
        values = data.get("values", [])
        allowed = []
        for entry in values:
            if isinstance(entry, dict) and "name" in entry:
                allowed.append(entry["name"])
            elif isinstance(entry, str):
                allowed.append(entry)
            else:
                raise ValueError(f"{path} contains an invalid taxonomy entry: {entry!r}")
        data["allowed_values"] = allowed
        results[path.stem] = data
    return results


def knowledge_source_roots(policy: dict[str, Any] | None = None) -> list[Path]:
    current_policy = policy or load_policy()
    return [ROOT / item for item in current_policy["directories"]["canonical_article_roots"]]


def collect_source_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    for root in knowledge_source_roots(policy):
        if root.exists():
            paths.extend(
                sorted(
                    path
                    for path in root.rglob("*.md")
                    if path.is_file() and path.name != "AGENTS.md"
                )
            )
    return sorted(paths)


def load_knowledge_documents(policy: dict[str, Any] | None = None) -> list[KnowledgeDocument]:
    return [parse_knowledge_document(path) for path in collect_source_paths(policy)]


def collect_docs_source_paths() -> list[Path]:
    if not DOCS_DIR.exists():
        return []
    paths = []
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(DOCS_DIR)
        except ValueError:
            continue
        if relative.parts and relative.parts[0] == "generated":
            continue
        paths.append(path)
    return paths


def collect_decision_paths() -> list[Path]:
    if not DECISIONS_DIR.exists():
        return []
    return sorted(path for path in DECISIONS_DIR.rglob("*") if path.is_file())


def collect_root_markdown_paths() -> list[Path]:
    candidates = [ROOT / "README.md", ROOT / "AGENTS.md"]
    return [path for path in candidates if path.exists()]


def collect_sanitization_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    scan_roots = [
        *knowledge_source_roots(policy),
        DOCS_DIR,
        DECISIONS_DIR,
        GENERATED_SITE_DOCS_DIR,
        ROOT / "migration",
        TEMPLATE_DIR,
        TAXONOMY_DIR,
        REPORTS_DIR,
    ]
    for root in scan_roots:
        if not root.exists():
            continue
        paths.extend(
            path
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix in {".md", ".yml", ".yaml"}
        )
    paths.extend(collect_root_markdown_paths())
    return sorted(set(paths))


def collect_article_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    return collect_source_paths(policy)


def load_articles(policy: dict[str, Any] | None = None) -> list[KnowledgeDocument]:
    return load_knowledge_documents(policy)


def load_current_runtime_documents(connection: sqlite3.Connection) -> list[KnowledgeDocument]:
    rows = connection.execute(
        """
        SELECT o.canonical_path, r.normalized_payload_json, r.body_markdown
        FROM knowledge_objects AS o
        JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
        ORDER BY o.object_id
        """
    ).fetchall()
    documents: list[KnowledgeDocument] = []
    for row in rows:
        metadata = json.loads(row["normalized_payload_json"])
        relative = str(row["canonical_path"])
        documents.append(
            KnowledgeDocument(
                source_path=ROOT / relative,
                relative_path=relative,
                metadata=metadata,
                body=str(row["body_markdown"]),
            )
        )
    return documents


def get_knowledge_object(connection: sqlite3.Connection, object_id: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM knowledge_objects WHERE object_id = ?",
        (object_id,),
    ).fetchone()


def get_knowledge_object_by_canonical_path(connection: sqlite3.Connection, canonical_path: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM knowledge_objects WHERE canonical_path = ?",
        (canonical_path,),
    ).fetchone()


def get_knowledge_revision(connection: sqlite3.Connection, revision_id: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM knowledge_revisions WHERE revision_id = ?",
        (revision_id,),
    ).fetchone()


def latest_revision_for_object(connection: sqlite3.Connection, object_id: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT *
        FROM knowledge_revisions
        WHERE object_id = ?
        ORDER BY revision_number DESC
        LIMIT 1
        """,
        (object_id,),
    ).fetchone()


def find_revision_by_content_hash(
    connection: sqlite3.Connection,
    object_id: str,
    content_hash: str,
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT *
        FROM knowledge_revisions
        WHERE object_id = ? AND content_hash = ?
        ORDER BY revision_number DESC
        LIMIT 1
        """,
        (object_id, content_hash),
    ).fetchone()


def next_revision_number(connection: sqlite3.Connection, object_id: str) -> int:
    row = connection.execute(
        "SELECT COALESCE(MAX(revision_number), 0) FROM knowledge_revisions WHERE object_id = ?",
        (object_id,),
    ).fetchone()
    return int((row[0] if row else 0) or 0) + 1


def delete_source_sync_relationships(connection: sqlite3.Connection, object_id: str) -> None:
    delete_projected_relationships(connection, object_id, ("source_sync",))


def delete_projected_relationships(
    connection: sqlite3.Connection,
    object_id: str,
    provenances: tuple[str, ...] = ("source_sync", "workflow_projection"),
) -> None:
    placeholders = ", ".join("?" for _ in provenances)
    connection.execute(
        f"""
        DELETE FROM relationships
        WHERE source_entity_type = 'knowledge_object'
          AND source_entity_id = ?
          AND provenance IN ({placeholders})
        """,
        (object_id, *provenances),
    )


def upsert_relationship(
    connection: sqlite3.Connection,
    *,
    relationship_id: str,
    source_entity_type: str,
    source_entity_id: str,
    target_entity_type: str,
    target_entity_id: str,
    relationship_type: str,
    provenance: str,
    relationship_strength: float | None = None,
    relationship_direction: str | None = None,
) -> None:
    resolved_strength = (
        relationship_strength
        if relationship_strength is not None
        else relationship_strength_for(relationship_type, target_entity_type)
    )
    resolved_direction = (
        relationship_direction
        if relationship_direction is not None
        else relationship_direction_for(relationship_type, target_entity_type)
    )
    connection.execute(
        """
        INSERT INTO relationships (
            relationship_id,
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            relationship_type,
            provenance,
            relationship_strength,
            relationship_direction
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(relationship_id) DO UPDATE SET
            source_entity_type = excluded.source_entity_type,
            source_entity_id = excluded.source_entity_id,
            target_entity_type = excluded.target_entity_type,
            target_entity_id = excluded.target_entity_id,
            relationship_type = excluded.relationship_type,
            provenance = excluded.provenance,
            relationship_strength = excluded.relationship_strength,
            relationship_direction = excluded.relationship_direction
        """,
        (
            relationship_id,
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            relationship_type,
            provenance,
            resolved_strength,
            resolved_direction,
        ),
    )


def upsert_search_document(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    title: str,
    summary: str,
    object_type: str,
    legacy_type: str | None,
    object_lifecycle_state: str,
    owner: str,
    team: str,
    trust_state: str,
    revision_review_state: str,
    draft_progress_state: str,
    source_sync_state: str,
    freshness_rank: int,
    citation_health_rank: int,
    ownership_rank: int,
    path: str,
    search_text: str,
) -> None:
    connection.execute(
        """
        INSERT INTO search_documents (
            object_id,
            revision_id,
            title,
            summary,
            object_type,
            legacy_type,
            object_lifecycle_state,
            owner,
            team,
            trust_state,
            revision_review_state,
            draft_progress_state,
            source_sync_state,
            freshness_rank,
            citation_health_rank,
            ownership_rank,
            path,
            search_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(object_id) DO UPDATE SET
            revision_id = excluded.revision_id,
            title = excluded.title,
            summary = excluded.summary,
            object_type = excluded.object_type,
            legacy_type = excluded.legacy_type,
            object_lifecycle_state = excluded.object_lifecycle_state,
            owner = excluded.owner,
            team = excluded.team,
            trust_state = excluded.trust_state,
            revision_review_state = excluded.revision_review_state,
            draft_progress_state = excluded.draft_progress_state,
            source_sync_state = excluded.source_sync_state,
            freshness_rank = excluded.freshness_rank,
            citation_health_rank = excluded.citation_health_rank,
            ownership_rank = excluded.ownership_rank,
            path = excluded.path,
            search_text = excluded.search_text
        """,
        (
            object_id,
            revision_id,
            title,
            summary,
            object_type,
            legacy_type,
            object_lifecycle_state,
            owner,
            team,
            trust_state,
            revision_review_state,
            draft_progress_state,
            source_sync_state,
            freshness_rank,
            citation_health_rank,
            ownership_rank,
            path,
            search_text,
        ),
    )


def replace_fts_document(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    title: str,
    summary: str,
    body: str,
    tags: list[str],
    systems: list[str],
    services: list[str],
) -> None:
    has_fts = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
    ).fetchone()
    if not has_fts:
        return
    connection.execute("DELETE FROM knowledge_search WHERE object_id = ?", (object_id,))
    connection.execute(
        """
        INSERT INTO knowledge_search (object_id, title, summary, body, tags, systems, services)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            object_id,
            title,
            summary,
            body,
            " ".join(tags),
            " ".join(systems),
            " ".join(services),
        ),
    )


def delete_search_document(connection: sqlite3.Connection, object_id: str) -> None:
    connection.execute("DELETE FROM search_documents WHERE object_id = ?", (object_id,))
    has_fts = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
    ).fetchone()
    if has_fts:
        connection.execute("DELETE FROM knowledge_search WHERE object_id = ?", (object_id,))


def insert_knowledge_object(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    object_type: str,
    legacy_type: str | None,
    title: str,
    summary: str,
    object_lifecycle_state: str,
    owner: str,
    team: str,
    canonical_path: str,
    source_type: str,
    source_system: str,
    source_title: str,
    created_date: str,
    updated_date: str,
    last_reviewed: str,
    review_cadence: str,
    trust_state: str,
    source_sync_state: str | None = None,
    source_sync_revision_id: str | None = None,
    source_sync_content_hash: str | None = None,
    source_sync_mutation_id: str | None = None,
    current_revision_id: str | None,
    tags_json: str,
    systems_json: str,
) -> None:
    connection.execute(
        """
        INSERT INTO knowledge_objects (
            object_id,
            object_type,
            legacy_type,
            title,
            summary,
            object_lifecycle_state,
            owner,
            team,
            canonical_path,
            source_type,
            source_system,
            source_title,
            created_date,
            updated_date,
            last_reviewed,
            review_cadence,
            trust_state,
            source_sync_state,
            source_sync_revision_id,
            source_sync_content_hash,
            source_sync_mutation_id,
            current_revision_id,
            tags_json,
            systems_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            object_id,
            object_type,
            legacy_type,
            title,
            summary,
            object_lifecycle_state,
            owner,
            team,
            canonical_path,
            source_type,
            source_system,
            source_title,
            created_date,
            updated_date,
            last_reviewed,
            review_cadence,
            trust_state,
            source_sync_state or "not_required",
            source_sync_revision_id,
            source_sync_content_hash,
            source_sync_mutation_id,
            current_revision_id,
            tags_json,
            systems_json,
        ),
    )


def upsert_knowledge_object(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    object_type: str,
    legacy_type: str | None,
    title: str,
    summary: str,
    object_lifecycle_state: str,
    owner: str,
    team: str,
    canonical_path: str,
    source_type: str,
    source_system: str,
    source_title: str,
    created_date: str,
    updated_date: str,
    last_reviewed: str,
    review_cadence: str,
    trust_state: str,
    source_sync_state: str | None = None,
    source_sync_revision_id: str | None = None,
    source_sync_content_hash: str | None = None,
    source_sync_mutation_id: str | None = None,
    current_revision_id: str | None,
    tags_json: str,
    systems_json: str,
) -> None:
    connection.execute(
        """
        INSERT INTO knowledge_objects (
            object_id,
            object_type,
            legacy_type,
            title,
            summary,
            object_lifecycle_state,
            owner,
            team,
            canonical_path,
            source_type,
            source_system,
            source_title,
            created_date,
            updated_date,
            last_reviewed,
            review_cadence,
            trust_state,
            source_sync_state,
            source_sync_revision_id,
            source_sync_content_hash,
            source_sync_mutation_id,
            current_revision_id,
            tags_json,
            systems_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(object_id) DO UPDATE SET
            object_type = excluded.object_type,
            legacy_type = excluded.legacy_type,
            title = excluded.title,
            summary = excluded.summary,
            object_lifecycle_state = excluded.object_lifecycle_state,
            owner = excluded.owner,
            team = excluded.team,
            canonical_path = excluded.canonical_path,
            source_type = excluded.source_type,
            source_system = excluded.source_system,
            source_title = excluded.source_title,
            created_date = excluded.created_date,
            updated_date = excluded.updated_date,
            last_reviewed = excluded.last_reviewed,
            review_cadence = excluded.review_cadence,
            trust_state = excluded.trust_state,
            source_sync_state = excluded.source_sync_state,
            source_sync_revision_id = excluded.source_sync_revision_id,
            source_sync_content_hash = excluded.source_sync_content_hash,
            source_sync_mutation_id = excluded.source_sync_mutation_id,
            current_revision_id = excluded.current_revision_id,
            tags_json = excluded.tags_json,
            systems_json = excluded.systems_json
        """,
        (
            object_id,
            object_type,
            legacy_type,
            title,
            summary,
            object_lifecycle_state,
            owner,
            team,
            canonical_path,
            source_type,
            source_system,
            source_title,
            created_date,
            updated_date,
            last_reviewed,
            review_cadence,
            trust_state,
            source_sync_state or "not_required",
            source_sync_revision_id,
            source_sync_content_hash,
            source_sync_mutation_id,
            current_revision_id,
            tags_json,
            systems_json,
        ),
    )


def insert_knowledge_revision(
    connection: sqlite3.Connection,
    *,
    revision_id: str,
    object_id: str,
    revision_number: int,
    revision_review_state: str,
    blueprint_id: str = "",
    draft_progress_state: str = "ready_for_review",
    source_path: str,
    content_hash: str,
    body_markdown: str,
    normalized_payload_json: str,
    section_content_json: str = "{}",
    section_completion_json: str = "{}",
    legacy_metadata_json: str,
    imported_at: str,
    change_summary: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO knowledge_revisions (
            revision_id,
            object_id,
            revision_number,
            revision_review_state,
            blueprint_id,
            draft_progress_state,
            source_path,
            content_hash,
            body_markdown,
            normalized_payload_json,
            section_content_json,
            section_completion_json,
            legacy_metadata_json,
            imported_at,
            change_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            revision_id,
            object_id,
            revision_number,
            revision_review_state,
            blueprint_id,
            draft_progress_state,
            source_path,
            content_hash,
            body_markdown,
            normalized_payload_json,
            section_content_json,
            section_completion_json,
            legacy_metadata_json,
            imported_at,
            change_summary,
        ),
    )


def update_knowledge_revision_content(
    connection: sqlite3.Connection,
    *,
    revision_id: str,
    content_hash: str,
    body_markdown: str,
    normalized_payload_json: str,
    blueprint_id: str,
    draft_progress_state: str,
    section_content_json: str,
    section_completion_json: str,
    change_summary: str | None,
) -> None:
    connection.execute(
        """
        UPDATE knowledge_revisions
        SET content_hash = ?,
            body_markdown = ?,
            normalized_payload_json = ?,
            blueprint_id = ?,
            draft_progress_state = ?,
            section_content_json = ?,
            section_completion_json = ?,
            change_summary = ?
        WHERE revision_id = ?
        """,
        (
            content_hash,
            body_markdown,
            normalized_payload_json,
            blueprint_id,
            draft_progress_state,
            section_content_json,
            section_completion_json,
            change_summary,
            revision_id,
        ),
    )


def update_knowledge_object_runtime_state(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    canonical_path: str | None = None,
    object_lifecycle_state: str | None = None,
    trust_state: str | None = None,
    source_sync_state: str | None = None,
    source_sync_revision_id: str | None = None,
    source_sync_content_hash: str | None = None,
    source_sync_mutation_id: str | None = None,
    current_revision_id: str | None = None,
    updated_date: str | None = None,
) -> None:
    assignments: list[str] = []
    values: list[str | None] = []
    if canonical_path is not None:
        assignments.append("canonical_path = ?")
        values.append(canonical_path)
    if object_lifecycle_state is not None:
        assignments.append("object_lifecycle_state = ?")
        values.append(object_lifecycle_state)
    if trust_state is not None:
        assignments.append("trust_state = ?")
        values.append(trust_state)
    if source_sync_state is not None:
        assignments.append("source_sync_state = ?")
        values.append(source_sync_state)
    if source_sync_revision_id is not None:
        assignments.append("source_sync_revision_id = ?")
        values.append(source_sync_revision_id)
    if source_sync_content_hash is not None:
        assignments.append("source_sync_content_hash = ?")
        values.append(source_sync_content_hash)
    if source_sync_mutation_id is not None:
        assignments.append("source_sync_mutation_id = ?")
        values.append(source_sync_mutation_id)
    if current_revision_id is not None:
        assignments.append("current_revision_id = ?")
        values.append(current_revision_id)
    if updated_date is not None:
        assignments.append("updated_date = ?")
        values.append(updated_date)
    if not assignments:
        return
    values.append(object_id)
    connection.execute(
        f"UPDATE knowledge_objects SET {', '.join(assignments)} WHERE object_id = ?",
        tuple(values),
    )


def update_knowledge_revision_state(
    connection: sqlite3.Connection,
    *,
    revision_id: str,
    revision_review_state: str,
    draft_progress_state: str | None = None,
) -> None:
    assignments = ["revision_review_state = ?"]
    values: list[str] = [revision_review_state]
    if draft_progress_state is not None:
        assignments.append("draft_progress_state = ?")
        values.append(draft_progress_state)
    values.append(revision_id)
    connection.execute(
        f"UPDATE knowledge_revisions SET {', '.join(assignments)} WHERE revision_id = ?",
        tuple(values),
    )
