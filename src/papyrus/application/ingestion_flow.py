from __future__ import annotations

import datetime as dt
import json
import mimetypes
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from papyrus.application.blueprint_registry import get_blueprint, list_blueprints
from papyrus.domain.ingestion import IngestionStatus
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.parsers import parse_docx_bytes, parse_markdown_bytes, parse_pdf_bytes
from papyrus.infrastructure.paths import BUILD_DIR, DB_PATH
from papyrus.infrastructure.repositories.ingestion_repo import (
    get_ingestion_job,
    insert_ingestion_artifact,
    insert_ingestion_job,
    list_ingestion_artifacts,
    list_ingestion_jobs,
    update_ingestion_job,
)
from papyrus.infrastructure.search.indexer import fts5_available


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _connection(database_path: Path) -> sqlite3.Connection:
    connection = open_runtime_database(database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    apply_runtime_schema(connection, has_fts5=fts5_available(connection))
    connection.execute(
        "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
        (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
    )
    return connection


def _artifact_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _record_artifact(
    connection: sqlite3.Connection,
    *,
    ingestion_id: str,
    artifact_type: str,
    content: dict[str, Any],
    created_at: str,
) -> None:
    insert_ingestion_artifact(
        connection,
        artifact_id=_artifact_id("artifact"),
        ingestion_id=ingestion_id,
        artifact_type=artifact_type,
        content_json=json_dump(content),
        created_at=created_at,
    )


def _ingestion_root() -> Path:
    return BUILD_DIR / "ingestions"


def _guess_media_type(path: Path) -> str:
    guessed, _ = mimetypes.guess_type(str(path))
    if guessed:
        return guessed
    if path.suffix.lower() == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if path.suffix.lower() == ".pdf":
        return "application/pdf"
    return "text/markdown"


def parse_file(*, file_path: Path, payload: bytes | None = None) -> tuple[str, str, dict[str, Any]]:
    resolved_payload = payload if payload is not None else file_path.read_bytes()
    suffix = file_path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "markdown", _guess_media_type(file_path), parse_markdown_bytes(resolved_payload)
    if suffix == ".docx":
        return "docx", _guess_media_type(file_path), parse_docx_bytes(resolved_payload)
    if suffix == ".pdf":
        return "pdf", _guess_media_type(file_path), parse_pdf_bytes(resolved_payload)
    raise ValueError(f"unsupported ingestion file type: {file_path.suffix}")


def normalize_content(parsed_content: dict[str, Any]) -> dict[str, Any]:
    headings = parsed_content.get("headings") if isinstance(parsed_content.get("headings"), list) else []
    paragraphs = parsed_content.get("paragraphs") if isinstance(parsed_content.get("paragraphs"), list) else []
    lists = parsed_content.get("lists") if isinstance(parsed_content.get("lists"), list) else []
    tables = parsed_content.get("tables") if isinstance(parsed_content.get("tables"), list) else []
    links = parsed_content.get("links") if isinstance(parsed_content.get("links"), list) else []
    title = str(parsed_content.get("title") or "").strip()
    if not title and headings:
        title = str(headings[0].get("text") or "").strip()
    return {
        "title": title,
        "headings": headings,
        "paragraphs": [str(item).strip() for item in paragraphs if str(item).strip()],
        "lists": [[str(item).strip() for item in block if str(item).strip()] for block in lists],
        "tables": tables,
        "links": links,
        "raw_text": str(parsed_content.get("raw_text") or "\n".join(str(item) for item in paragraphs)).strip(),
    }


def classify_document(normalized_content: dict[str, Any]) -> dict[str, Any]:
    title = str(normalized_content.get("title") or "").lower()
    headings = [str(item.get("text") or "").lower() for item in normalized_content.get("headings", [])]
    raw_text = str(normalized_content.get("raw_text") or "").lower()
    candidates: list[dict[str, Any]] = []
    heuristics = {
        "runbook": ["step", "rollback", "verify", "procedure", "runbook"],
        "known_error": ["symptom", "mitigation", "diagnostic", "known error", "cause"],
        "service_record": ["service", "dependency", "support", "entrypoint", "failure mode"],
        "policy": ["policy", "control", "must", "shall", "exception"],
        "system_design": ["architecture", "interface", "component", "design", "dependency"],
    }
    for blueprint in list_blueprints():
        score = 0
        matched_terms: list[str] = []
        for token in heuristics.get(blueprint.blueprint_id, []):
            if token in title:
                score += 3
                matched_terms.append(token)
            if any(token in heading for heading in headings):
                score += 2
                matched_terms.append(token)
            if token in raw_text:
                score += 1
                matched_terms.append(token)
        candidates.append(
            {
                "blueprint_id": blueprint.blueprint_id,
                "display_name": blueprint.display_name,
                "score": score,
                "matched_terms": sorted(set(matched_terms)),
            }
        )
    candidates.sort(key=lambda item: (-int(item["score"]), str(item["blueprint_id"])))
    selected = candidates[0] if candidates else {"blueprint_id": "runbook", "score": 0, "matched_terms": []}
    confidence = 0.2 if not candidates or int(selected["score"]) <= 1 else min(0.95, 0.25 + (int(selected["score"]) * 0.1))
    return {
        "blueprint_id": selected["blueprint_id"],
        "confidence": round(confidence, 2),
        "candidates": candidates,
        "reasons": selected.get("matched_terms", []),
    }


def extract_sections(normalized_content: dict[str, Any]) -> list[dict[str, Any]]:
    extracted: list[dict[str, Any]] = []
    current_heading = normalized_content.get("title") or "Document"
    extracted.append(
        {
            "heading": current_heading,
            "content": str(normalized_content.get("title") or "").strip(),
            "kind": "title",
        }
    )
    for heading in normalized_content.get("headings", []):
        current_heading = str(heading.get("text") or "").strip() or current_heading
        extracted.append({"heading": current_heading, "content": current_heading, "kind": "heading"})
    for paragraph in normalized_content.get("paragraphs", []):
        extracted.append({"heading": current_heading, "content": str(paragraph), "kind": "paragraph"})
    for items in normalized_content.get("lists", []):
        extracted.append({"heading": current_heading, "content": [str(item) for item in items], "kind": "list"})
    for table in normalized_content.get("tables", []):
        extracted.append({"heading": current_heading, "content": table, "kind": "table"})
    return extracted


def ingest_file(
    *,
    file_path: str | Path,
    payload: bytes | None = None,
    database_path: Path = DB_PATH,
) -> dict[str, Any]:
    path = Path(file_path)
    parser_name, media_type, parsed = parse_file(file_path=path, payload=payload)
    normalized = normalize_content(parsed)
    classification = classify_document(normalized)
    extracted = extract_sections(normalized)
    ingestion_id = _artifact_id("ingestion")
    now = _now_utc()
    storage_dir = _ingestion_root() / ingestion_id
    storage_dir.mkdir(parents=True, exist_ok=True)
    stored_path = storage_dir / path.name
    if payload is not None:
        stored_path.write_bytes(payload)
    elif path.resolve() != stored_path.resolve():
        stored_path.write_bytes(path.read_bytes())
    connection = _connection(Path(database_path))
    try:
        insert_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            filename=path.name,
            source_path=stored_path.as_posix(),
            media_type=media_type,
            parser_name=parser_name,
            status=IngestionStatus.MAPPED.value,
            normalized_content_json=json_dump(normalized),
            classification_json=json_dump(classification),
            mapping_result_json=json_dump({}),
            error_json=json_dump({}),
            blueprint_id=str(classification["blueprint_id"]),
            converted_object_id=None,
            converted_revision_id=None,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="uploaded",
            content={
                "filename": path.name,
                "source_path": stored_path.as_posix(),
                "media_type": media_type,
            },
            created_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="parsed",
            content=parsed,
            created_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="normalized",
            content=normalized,
            created_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="classified",
            content=classification,
            created_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="sections",
            content={"sections": extracted},
            created_at=now.isoformat(),
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="stage_progress",
            content={
                "completed_stages": ["upload", "parse", "classify", "map"],
                "current_stage": "review",
                "next_action": "Review the mapping before converting this file into a governed draft.",
            },
            created_at=now.isoformat(),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {
        "ingestion_id": ingestion_id,
        "filename": path.name,
        "parser_name": parser_name,
        "media_type": media_type,
        "normalized_content": normalized,
        "classification": classification,
        "sections": extracted,
    }


def ingestion_detail(*, ingestion_id: str, database_path: Path = DB_PATH) -> dict[str, Any]:
    connection = _connection(Path(database_path))
    try:
        row = get_ingestion_job(connection, ingestion_id)
        if row is None:
            raise ValueError(f"ingestion job not found: {ingestion_id}")
        artifacts = [
            {
                "artifact_id": str(artifact["artifact_id"]),
                "artifact_type": str(artifact["artifact_type"]),
                "content": json.loads(str(artifact["content_json"])),
                "created_at": str(artifact["created_at"]),
            }
            for artifact in list_ingestion_artifacts(connection, ingestion_id)
        ]
        return {
            "ingestion_id": str(row["ingestion_id"]),
            "filename": str(row["filename"]),
            "source_path": str(row["source_path"]),
            "media_type": str(row["media_type"]),
            "parser_name": str(row["parser_name"]),
            "status": str(row["status"]),
            "normalized_content": json.loads(str(row["normalized_content_json"])),
            "classification": json.loads(str(row["classification_json"])),
            "mapping_result": json.loads(str(row["mapping_result_json"])),
            "error": json.loads(str(row["error_json"])),
            "blueprint_id": str(row["blueprint_id"]) if row["blueprint_id"] is not None else None,
            "converted_object_id": str(row["converted_object_id"]) if row["converted_object_id"] is not None else None,
            "converted_revision_id": str(row["converted_revision_id"]) if row["converted_revision_id"] is not None else None,
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "artifacts": artifacts,
        }
    finally:
        connection.close()


def list_ingestions(*, database_path: Path = DB_PATH) -> list[dict[str, Any]]:
    connection = _connection(Path(database_path))
    try:
        return [
            {
                "ingestion_id": str(row["ingestion_id"]),
                "filename": str(row["filename"]),
                "status": str(row["status"]),
                "blueprint_id": str(row["blueprint_id"]) if row["blueprint_id"] is not None else None,
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
                "converted_object_id": str(row["converted_object_id"]) if row["converted_object_id"] is not None else None,
            }
            for row in list_ingestion_jobs(connection)
        ]
    finally:
        connection.close()


def update_ingestion_mapping(
    *,
    ingestion_id: str,
    mapping_result: dict[str, Any],
    status: str,
    blueprint_id: str | None,
    database_path: Path = DB_PATH,
) -> None:
    connection = _connection(Path(database_path))
    try:
        created_at = _now_utc().isoformat()
        update_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            status=status,
            mapping_result_json=json_dump(mapping_result),
            blueprint_id=blueprint_id,
            updated_at=created_at,
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="mapping_result",
            content=mapping_result,
            created_at=created_at,
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="stage_progress",
            content={
                "completed_stages": ["upload", "parse", "classify", "map"],
                "current_stage": "review",
                "next_action": "Review missing sections, low-confidence matches, and unmapped content before conversion.",
            },
            created_at=created_at,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def mark_ingestion_converted(
    *,
    ingestion_id: str,
    object_id: str,
    revision_id: str,
    database_path: Path = DB_PATH,
) -> None:
    connection = _connection(Path(database_path))
    try:
        created_at = _now_utc().isoformat()
        update_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            status=IngestionStatus.REVIEWED.value,
            converted_object_id=object_id,
            converted_revision_id=revision_id,
            updated_at=created_at,
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="conversion_result",
            content={
                "object_id": object_id,
                "revision_id": revision_id,
            },
            created_at=created_at,
        )
        _record_artifact(
            connection,
            ingestion_id=ingestion_id,
            artifact_type="stage_progress",
            content={
                "completed_stages": ["upload", "parse", "classify", "map", "review", "convert"],
                "current_stage": "convert",
                "next_action": "Continue the structured draft in the normal write and review workflow.",
            },
            created_at=created_at,
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
