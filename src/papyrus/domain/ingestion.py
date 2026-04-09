from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IngestionStatus(str, Enum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    CLASSIFIED = "classified"
    MAPPED = "mapped"
    REVIEWED = "reviewed"


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
