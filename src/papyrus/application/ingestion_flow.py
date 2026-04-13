from __future__ import annotations

import datetime as dt
import json
import mimetypes
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from papyrus.application.blueprint_registry import list_blueprints
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.ui_projection import (
    build_ingestion_projection,
    workflow_projection_payload,
)
from papyrus.domain.ingestion import IngestionStatus, has_mapping_result, truthful_ingestion_status
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.parsers import parse_docx_bytes, parse_markdown_bytes, parse_pdf_bytes
from papyrus.infrastructure.paths import BUILD_DIR, DB_PATH, ROOT
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
    return dt.datetime.now(dt.UTC).replace(microsecond=0)


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


def _policy_authority(authority: PolicyAuthority | None) -> PolicyAuthority:
    return authority or PolicyAuthority.from_repository_policy()


def _truthful_status_from_row(row: sqlite3.Row) -> IngestionStatus:
    return truthful_ingestion_status(
        stored_status=str(row["ingestion_state"] or row["status"]),
        mapping_result=json.loads(str(row["mapping_result_json"])),
        converted_revision_id=str(row["converted_revision_id"])
        if row["converted_revision_id"] is not None
        else None,
    )


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


def _safe_ingestion_filename(file_path: str | Path) -> str:
    raw_name = str(file_path).replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not raw_name or raw_name in {".", ".."}:
        raise ValueError("ingestion file must include a safe filename")
    if any(ord(character) < 32 for character in raw_name):
        raise ValueError("ingestion filename contains unsupported control characters")
    if len(raw_name) > 255:
        raise ValueError("ingestion filename is too long")
    return raw_name


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


def _table_text(rows: list[list[str]]) -> str:
    return "\n".join(
        " | ".join(cell for cell in row if cell) for row in rows if any(cell for cell in row)
    )


def _sanitize_elements(parsed_content: dict[str, Any]) -> list[dict[str, Any]]:
    raw_elements = parsed_content.get("elements")
    if not isinstance(raw_elements, list):
        return []
    sanitized: list[dict[str, Any]] = []
    for element in raw_elements:
        if not isinstance(element, dict):
            continue
        kind = str(element.get("kind") or "").strip()
        if kind == "heading":
            text = str(element.get("text") or "").strip()
            if not text:
                continue
            try:
                level = max(1, int(element.get("level") or 1))
            except (TypeError, ValueError):
                level = 1
            sanitized.append({"kind": "heading", "level": level, "text": text})
            continue
        if kind == "paragraph":
            text = str(element.get("text") or "").strip()
            if text:
                sanitized.append({"kind": "paragraph", "text": text})
            continue
        if kind == "list":
            items = [str(item).strip() for item in element.get("items", []) if str(item).strip()]
            if items:
                sanitized.append({"kind": "list", "items": items, "text": "\n".join(items)})
            continue
        if kind == "table":
            rows: list[list[str]] = []
            for row in element.get("rows", []):
                if isinstance(row, list):
                    rows.append([str(cell).strip() for cell in row])
            if rows:
                sanitized.append({"kind": "table", "rows": rows, "text": _table_text(rows)})
    return sanitized


def _synthesized_elements(
    *,
    headings: list[dict[str, Any]],
    paragraphs: list[str],
    lists: list[list[str]],
    tables: list[list[list[str]]],
) -> list[dict[str, Any]]:
    elements: list[dict[str, Any]] = []
    for heading in headings:
        text = str(heading.get("text") or "").strip()
        if not text:
            continue
        try:
            level = max(1, int(heading.get("level") or 1))
        except (TypeError, ValueError):
            level = 1
        elements.append({"kind": "heading", "level": level, "text": text})
    for paragraph in paragraphs:
        text = str(paragraph).strip()
        if text:
            elements.append({"kind": "paragraph", "text": text})
    for block in lists:
        items = [str(item).strip() for item in block if str(item).strip()]
        if items:
            elements.append({"kind": "list", "items": items, "text": "\n".join(items)})
    for table in tables:
        elements.append({"kind": "table", "rows": table, "text": _table_text(table)})
    return elements


def normalize_content(parsed_content: dict[str, Any]) -> dict[str, Any]:
    headings = (
        parsed_content.get("headings") if isinstance(parsed_content.get("headings"), list) else []
    )
    paragraphs = (
        parsed_content.get("paragraphs")
        if isinstance(parsed_content.get("paragraphs"), list)
        else []
    )
    lists = parsed_content.get("lists") if isinstance(parsed_content.get("lists"), list) else []
    tables = parsed_content.get("tables") if isinstance(parsed_content.get("tables"), list) else []
    links = parsed_content.get("links") if isinstance(parsed_content.get("links"), list) else []
    parser_warnings = (
        [
            str(item).strip()
            for item in parsed_content.get("parser_warnings", [])
            if str(item).strip()
        ]
        if isinstance(parsed_content.get("parser_warnings"), list)
        else []
    )
    degradation_notes = (
        [
            str(item).strip()
            for item in parsed_content.get("degradation_notes", [])
            if str(item).strip()
        ]
        if isinstance(parsed_content.get("degradation_notes"), list)
        else []
    )
    extraction_quality = (
        parsed_content.get("extraction_quality")
        if isinstance(parsed_content.get("extraction_quality"), dict)
        else {}
    )
    title = str(parsed_content.get("title") or "").strip()
    if not title and headings:
        title = str(headings[0].get("text") or "").strip()
    sanitized_elements = _sanitize_elements(parsed_content)
    if not sanitized_elements:
        sanitized_elements = _synthesized_elements(
            headings=headings,
            paragraphs=[str(item).strip() for item in paragraphs if str(item).strip()],
            lists=[[str(item).strip() for item in block if str(item).strip()] for block in lists],
            tables=tables,
        )
    raw_text_parts = [title] if title else []
    raw_text_parts.extend(
        str(element.get("text") or "").strip()
        for element in sanitized_elements
        if str(element.get("text") or "").strip()
    )
    return {
        "title": title,
        "headings": headings,
        "paragraphs": [str(item).strip() for item in paragraphs if str(item).strip()],
        "lists": [[str(item).strip() for item in block if str(item).strip()] for block in lists],
        "tables": tables,
        "elements": sanitized_elements,
        "links": links,
        "raw_text": str(parsed_content.get("raw_text") or "\n".join(raw_text_parts)).strip(),
        "parser_warnings": parser_warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": {
            "state": str(
                extraction_quality.get("state") or ("degraded" if parser_warnings else "clean")
            ),
            "score": float(extraction_quality.get("score") or (0.5 if parser_warnings else 1.0)),
            "summary": str(
                extraction_quality.get("summary")
                or (
                    "Extraction quality is degraded."
                    if parser_warnings
                    else "Extraction quality is clean."
                )
            ),
        },
    }


def classify_document(normalized_content: dict[str, Any]) -> dict[str, Any]:
    title = str(normalized_content.get("title") or "").lower()
    headings = [
        str(item.get("text") or "").lower() for item in normalized_content.get("headings", [])
    ]
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
    selected = (
        candidates[0]
        if candidates
        else {"blueprint_id": "runbook", "score": 0, "matched_terms": []}
    )
    confidence = (
        0.2
        if not candidates or int(selected["score"]) <= 1
        else min(0.95, 0.25 + (int(selected["score"]) * 0.1))
    )
    return {
        "blueprint_id": selected["blueprint_id"],
        "confidence": round(confidence, 2),
        "candidates": candidates,
        "reasons": selected.get("matched_terms", []),
    }


def extract_sections(normalized_content: dict[str, Any]) -> list[dict[str, Any]]:
    elements = (
        normalized_content.get("elements")
        if isinstance(normalized_content.get("elements"), list)
        else []
    )
    has_heading_elements = any(
        str(element.get("kind") or "") == "heading"
        for element in elements
        if isinstance(element, dict)
    )
    title = str(normalized_content.get("title") or "").strip()
    heading_stack: list[dict[str, object]] = (
        [{"level": 1, "text": title}] if title and not has_heading_elements else []
    )
    extracted: list[dict[str, Any]] = []
    for element_index, element in enumerate(elements):
        if not isinstance(element, dict):
            continue
        kind = str(element.get("kind") or "").strip()
        if kind not in {"heading", "paragraph", "list", "table"}:
            continue
        if kind == "heading":
            text = str(element.get("text") or "").strip()
            if not text:
                continue
            try:
                level = max(1, int(element.get("level") or 1))
            except (TypeError, ValueError):
                level = 1
            while heading_stack and int(heading_stack[-1]["level"]) >= level:
                heading_stack.pop()
            heading_stack.append({"level": level, "text": text})
            content: Any = text
            text_value = text
        elif kind == "paragraph":
            text_value = str(element.get("text") or "").strip()
            if not text_value:
                continue
            content = text_value
        elif kind == "list":
            items = [str(item).strip() for item in element.get("items", []) if str(item).strip()]
            if not items:
                continue
            content = items
            text_value = "\n".join(items)
        else:
            rows: list[list[str]] = []
            for row in element.get("rows", []):
                if isinstance(row, list):
                    rows.append([str(cell).strip() for cell in row])
            if not rows:
                continue
            content = rows
            text_value = _table_text(rows)
        active_heading = str(heading_stack[-1]["text"]) if heading_stack else (title or "Document")
        extracted.append(
            {
                "fragment_id": f"fragment-{len(extracted) + 1:04d}",
                "order": len(extracted) + 1,
                "kind": kind,
                "heading": active_heading,
                "heading_path": [dict(item) for item in heading_stack],
                "content": content,
                "text": text_value,
                "source": {
                    "element_index": element_index,
                    "kind": kind,
                },
            }
        )
    return extracted


def ingest_file(
    *,
    file_path: str | Path,
    payload: bytes | None = None,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    resolved_source_root = Path(source_root).resolve()
    path = Path(file_path)
    safe_filename = _safe_ingestion_filename(file_path)
    if payload is None:
        path = current_authority.validate_local_ingest_source_path(
            source_root=resolved_source_root,
            candidate_path=path,
        )
    parser_path = Path(safe_filename) if payload is not None else path
    parser_name, media_type, parsed = parse_file(file_path=parser_path, payload=payload)
    normalized = normalize_content(parsed)
    classification = classify_document(normalized)
    extracted = extract_sections(normalized)
    ingestion_id = _artifact_id("ingestion")
    now = _now_utc()
    storage_dir = _ingestion_root() / ingestion_id
    storage_dir.mkdir(parents=True, exist_ok=True)
    stored_path = storage_dir / safe_filename
    if payload is not None:
        stored_path.write_bytes(payload)
    elif path.resolve() != stored_path.resolve():
        stored_path.write_bytes(path.read_bytes())
    connection = _connection(Path(database_path))
    try:
        insert_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            filename=safe_filename,
            source_path=stored_path.as_posix(),
            media_type=media_type,
            parser_name=parser_name,
            status=IngestionStatus.CLASSIFIED.value,
            ingestion_state=IngestionStatus.CLASSIFIED.value,
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
                "filename": safe_filename,
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
                "completed_stages": ["upload", "parse", "classify"],
                "current_stage": "map",
                "next_action": "Generate and review the mapping before converting this file into a governed draft.",
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
        "filename": safe_filename,
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
        detail = {
            "ingestion_id": str(row["ingestion_id"]),
            "filename": str(row["filename"]),
            "source_path": str(row["source_path"]),
            "media_type": str(row["media_type"]),
            "parser_name": str(row["parser_name"]),
            "ingestion_state": _truthful_status_from_row(row).value,
            "normalized_content": json.loads(str(row["normalized_content_json"])),
            "classification": json.loads(str(row["classification_json"])),
            "mapping_result": json.loads(str(row["mapping_result_json"])),
            "error": json.loads(str(row["error_json"])),
            "blueprint_id": str(row["blueprint_id"]) if row["blueprint_id"] is not None else None,
            "converted_object_id": str(row["converted_object_id"])
            if row["converted_object_id"] is not None
            else None,
            "converted_revision_id": str(row["converted_revision_id"])
            if row["converted_revision_id"] is not None
            else None,
            "created_at": str(row["created_at"]),
            "updated_at": str(row["updated_at"]),
            "artifacts": artifacts,
        }
        detail["workflow_projection"] = workflow_projection_payload(
            build_ingestion_projection(detail=detail)
        )
        return detail
    finally:
        connection.close()


def list_ingestions(*, database_path: Path = DB_PATH) -> list[dict[str, Any]]:
    connection = _connection(Path(database_path))
    try:
        items = [
            {
                "ingestion_id": str(row["ingestion_id"]),
                "filename": str(row["filename"]),
                "ingestion_state": _truthful_status_from_row(row).value,
                "blueprint_id": str(row["blueprint_id"])
                if row["blueprint_id"] is not None
                else None,
                "created_at": str(row["created_at"]),
                "updated_at": str(row["updated_at"]),
                "converted_object_id": str(row["converted_object_id"])
                if row["converted_object_id"] is not None
                else None,
            }
            for row in list_ingestion_jobs(connection)
        ]
        for item in items:
            item["workflow_projection"] = workflow_projection_payload(
                build_ingestion_projection(detail=item)
            )
        return items
    finally:
        connection.close()


def update_ingestion_mapping(
    *,
    ingestion_id: str,
    mapping_result: dict[str, Any],
    blueprint_id: str | None,
    database_path: Path = DB_PATH,
    authority: PolicyAuthority | None = None,
) -> None:
    current_authority = _policy_authority(authority)
    if not has_mapping_result(mapping_result):
        raise ValueError("ingestion cannot be marked mapped before a real mapping result exists")
    connection = _connection(Path(database_path))
    try:
        row = get_ingestion_job(connection, ingestion_id)
        if row is None:
            raise ValueError(f"ingestion job not found: {ingestion_id}")
        current_status = _truthful_status_from_row(row)
        if current_status not in {IngestionStatus.CLASSIFIED, IngestionStatus.MAPPED}:
            raise ValueError(
                "ingestion mapping can only be recorded after classification and before review"
            )
        current_authority.require_ingestion_transition(
            current_status.value, IngestionStatus.MAPPED.value
        )
        created_at = _now_utc().isoformat()
        update_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            status=IngestionStatus.MAPPED.value,
            ingestion_state=IngestionStatus.MAPPED.value,
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
    authority: PolicyAuthority | None = None,
) -> None:
    current_authority = _policy_authority(authority)
    connection = _connection(Path(database_path))
    try:
        row = get_ingestion_job(connection, ingestion_id)
        if row is None:
            raise ValueError(f"ingestion job not found: {ingestion_id}")
        mapping_result = json.loads(str(row["mapping_result_json"]))
        if _truthful_status_from_row(row) != IngestionStatus.MAPPED or not has_mapping_result(
            mapping_result
        ):
            raise ValueError(
                "ingestion must have a real mapping result before it can be reviewed and converted"
            )
        current_authority.require_ingestion_transition(
            IngestionStatus.MAPPED.value, IngestionStatus.CONVERTED.value
        )
        created_at = _now_utc().isoformat()
        update_ingestion_job(
            connection,
            ingestion_id=ingestion_id,
            status=IngestionStatus.CONVERTED.value,
            ingestion_state=IngestionStatus.CONVERTED.value,
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
