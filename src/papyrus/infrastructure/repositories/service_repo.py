from __future__ import annotations

import sqlite3


def upsert_service(
    connection: sqlite3.Connection,
    *,
    service_id: str,
    service_name: str,
    canonical_object_id: str | None,
    owner: str | None,
    team: str | None,
    status: str,
    service_criticality: str,
    support_entrypoints_json: str,
    dependencies_json: str,
    common_failure_modes_json: str,
    source: str,
) -> None:
    connection.execute(
        """
        INSERT INTO services (
            service_id,
            service_name,
            canonical_object_id,
            owner,
            team,
            status,
            service_criticality,
            support_entrypoints_json,
            dependencies_json,
            common_failure_modes_json,
            source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(service_name) DO UPDATE SET
            canonical_object_id = COALESCE(excluded.canonical_object_id, services.canonical_object_id),
            owner = COALESCE(excluded.owner, services.owner),
            team = COALESCE(excluded.team, services.team),
            status = excluded.status,
            service_criticality = excluded.service_criticality,
            support_entrypoints_json = excluded.support_entrypoints_json,
            dependencies_json = excluded.dependencies_json,
            common_failure_modes_json = excluded.common_failure_modes_json,
            source = excluded.source
        """,
        (
            service_id,
            service_name,
            canonical_object_id,
            owner,
            team,
            status,
            service_criticality,
            support_entrypoints_json,
            dependencies_json,
            common_failure_modes_json,
            source,
        ),
    )
