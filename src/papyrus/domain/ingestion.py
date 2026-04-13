from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Any

from papyrus.domain.lifecycle import IngestionLifecycleState

IngestionStatus = IngestionLifecycleState


def has_mapping_result(mapping_result: dict[str, Any] | None) -> bool:
    if not isinstance(mapping_result, dict) or not mapping_result:
        return False
    sections = mapping_result.get("sections")
    blueprint_id = str(mapping_result.get("blueprint_id") or "").strip()
    return bool(blueprint_id) and isinstance(sections, dict) and bool(sections)


def truthful_ingestion_status(
    *,
    stored_status: str | IngestionStatus,
    mapping_result: dict[str, Any] | None,
    converted_revision_id: str | None,
) -> IngestionStatus:
    status = IngestionStatus(str(stored_status))
    if converted_revision_id:
        return IngestionStatus.CONVERTED
    if has_mapping_result(mapping_result):
        return IngestionStatus.MAPPED
    if status in {IngestionStatus.CLASSIFIED, IngestionStatus.MAPPED, IngestionStatus.CONVERTED}:
        return IngestionStatus.CLASSIFIED
    return status


@dataclass(frozen=True)
class IngestionArtifact:
    artifact_id: str
    ingestion_id: str
    artifact_type: str
    content: dict[str, Any]
    created_at: dt.datetime | None = None


@dataclass(frozen=True)
class IngestionJob:
    ingestion_id: str
    filename: str
    source_path: str
    media_type: str
    status: IngestionStatus
    parser_name: str
    normalized_content: dict[str, Any] = field(default_factory=dict)
    classification: dict[str, Any] = field(default_factory=dict)
    mapping_result: dict[str, Any] = field(default_factory=dict)
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    converted_object_id: str | None = None
    converted_revision_id: str | None = None
