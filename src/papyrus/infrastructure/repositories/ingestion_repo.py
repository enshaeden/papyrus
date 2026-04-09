from __future__ import annotations

import sqlite3


def insert_ingestion_job(
    connection: sqlite3.Connection,
    *,
    ingestion_id: str,
    filename: str,
    source_path: str,
    media_type: str,
    parser_name: str,
    status: str,
    normalized_content_json: str,
    classification_json: str,
    mapping_result_json: str,
    error_json: str,
    blueprint_id: str | None,
    converted_object_id: str | None,
    converted_revision_id: str | None,
    created_at: str,
    updated_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO ingestion_jobs (
            ingestion_id,
            filename,
            source_path,
            media_type,
            parser_name,
            status,
            normalized_content_json,
            classification_json,
            mapping_result_json,
            error_json,
            blueprint_id,
            converted_object_id,
            converted_revision_id,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ingestion_id,
            filename,
            source_path,
            media_type,
            parser_name,
            status,
            normalized_content_json,
            classification_json,
            mapping_result_json,
            error_json,
            blueprint_id,
            converted_object_id,
            converted_revision_id,
            created_at,
            updated_at,
        ),
    )


def update_ingestion_job(
    connection: sqlite3.Connection,
    *,
    ingestion_id: str,
    status: str,
    normalized_content_json: str | None = None,
    classification_json: str | None = None,
    mapping_result_json: str | None = None,
    error_json: str | None = None,
    blueprint_id: str | None = None,
    converted_object_id: str | None = None,
    converted_revision_id: str | None = None,
    updated_at: str,
) -> None:
    assignments = ["status = ?", "updated_at = ?"]
    values: list[str | None] = [status, updated_at]
    if normalized_content_json is not None:
        assignments.append("normalized_content_json = ?")
        values.append(normalized_content_json)
    if classification_json is not None:
        assignments.append("classification_json = ?")
        values.append(classification_json)
    if mapping_result_json is not None:
        assignments.append("mapping_result_json = ?")
        values.append(mapping_result_json)
    if error_json is not None:
        assignments.append("error_json = ?")
        values.append(error_json)
    if blueprint_id is not None:
        assignments.append("blueprint_id = ?")
        values.append(blueprint_id)
    if converted_object_id is not None:
        assignments.append("converted_object_id = ?")
        values.append(converted_object_id)
    if converted_revision_id is not None:
        assignments.append("converted_revision_id = ?")
        values.append(converted_revision_id)
    values.append(ingestion_id)
    connection.execute(
        f"UPDATE ingestion_jobs SET {', '.join(assignments)} WHERE ingestion_id = ?",
        tuple(values),
    )


def get_ingestion_job(connection: sqlite3.Connection, ingestion_id: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM ingestion_jobs WHERE ingestion_id = ?",
        (ingestion_id,),
    ).fetchone()


def list_ingestion_jobs(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT *
        FROM ingestion_jobs
        ORDER BY updated_at DESC, created_at DESC
        """
    ).fetchall()


def insert_ingestion_artifact(
    connection: sqlite3.Connection,
    *,
    artifact_id: str,
    ingestion_id: str,
    artifact_type: str,
    content_json: str,
    created_at: str,
) -> None:
    connection.execute(
        """
        INSERT INTO ingestion_artifacts (
            artifact_id,
            ingestion_id,
            artifact_type,
            content_json,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (artifact_id, ingestion_id, artifact_type, content_json, created_at),
    )


def list_ingestion_artifacts(connection: sqlite3.Connection, ingestion_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT *
        FROM ingestion_artifacts
        WHERE ingestion_id = ?
        ORDER BY created_at ASC, artifact_id ASC
        """,
        (ingestion_id,),
    ).fetchall()
