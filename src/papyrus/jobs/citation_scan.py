from __future__ import annotations

import datetime as dt
import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from papyrus.domain.policies import normalize_citation_validity_status, worse_citation_validity
from papyrus.infrastructure.markdown.serializer import parse_iso_date, parse_iso_date_or_datetime
from papyrus.infrastructure.paths import ROOT
from papyrus.infrastructure.repositories.citation_repo import (
    list_current_citations,
    update_citation_validity_status,
)
from papyrus.infrastructure.repositories.knowledge_repo import (
    get_knowledge_object_by_canonical_path,
)
from papyrus.infrastructure.storage.evidence_store import EvidenceStore
from papyrus.jobs.stale_scan import cadence_to_days

LOCAL_EVIDENCE_PREFIXES = ("knowledge/", "archive/knowledge/", "docs/", "decisions/")
WORKSPACE_LOCAL_EVIDENCE_PREFIXES = ("knowledge/", "archive/knowledge/")
REPOSITORY_LOCAL_EVIDENCE_PREFIXES = ("docs/", "decisions/")


@dataclass(frozen=True)
class CitationFinding:
    citation_id: str
    object_id: str
    revision_id: str
    validity_status: str
    source_ref: str
    reason: str


@dataclass(frozen=True)
class CitationScanResult:
    scanned_count: int
    findings: list[CitationFinding]
    counts_by_object: dict[str, dict[str, int]]


def resolve_local_evidence_path(source_ref: str, *, root_path: Path = ROOT) -> Path | None:
    normalized = source_ref.strip()
    if not normalized.startswith(LOCAL_EVIDENCE_PREFIXES):
        return None
    if normalized.startswith(WORKSPACE_LOCAL_EVIDENCE_PREFIXES):
        return (root_path / normalized).resolve()
    if normalized.startswith(REPOSITORY_LOCAL_EVIDENCE_PREFIXES):
        return (ROOT / normalized).resolve()
    return None


def current_integrity_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def classify_citation(
    connection: sqlite3.Connection,
    row: sqlite3.Row,
    *,
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date,
    root_path: Path = ROOT,
) -> tuple[str, list[str]]:
    status = normalize_citation_validity_status(str(row["validity_status"]))
    reasons: list[str] = []
    source_ref = str(row["source_ref"] or "").strip()
    captured_at = row["captured_at"]
    integrity_hash = str(row["integrity_hash"]).strip() if row["integrity_hash"] else None
    evidence_snapshot_path = (
        str(row["evidence_snapshot_path"]).strip() if row["evidence_snapshot_path"] else None
    )
    evidence_expiry_at = row["evidence_expiry_at"]
    evidence_last_validated_at = row["evidence_last_validated_at"]
    object_last_reviewed = parse_iso_date(row["object_last_reviewed"])
    cadence_days = cadence_to_days(str(row["object_review_cadence"]), taxonomies)
    local_path = resolve_local_evidence_path(source_ref, root_path=root_path)
    evidence_store = EvidenceStore(root_path=root_path)

    if evidence_snapshot_path:
        snapshot_path = evidence_store.resolve_snapshot_path(evidence_snapshot_path)
        if not snapshot_path.exists():
            status = worse_citation_validity(status, "broken")
            reasons.append("evidence snapshot path does not exist")
        elif integrity_hash is not None and current_integrity_hash(snapshot_path) != integrity_hash:
            status = worse_citation_validity(status, "stale")
            reasons.append("evidence snapshot changed since the stored integrity hash")
    if evidence_expiry_at is not None and parse_iso_date_or_datetime(evidence_expiry_at) < as_of:
        status = worse_citation_validity(status, "stale")
        reasons.append("evidence snapshot expired")
    if evidence_snapshot_path and evidence_last_validated_at is None:
        status = worse_citation_validity(status, "unverified")
        reasons.append("evidence snapshot lacks last_validated timestamp")

    if local_path is not None:
        if not local_path.exists():
            status = worse_citation_validity(status, "broken")
            reasons.append("local evidence target does not exist")
            return status, reasons

        if integrity_hash is not None and current_integrity_hash(local_path) != integrity_hash:
            status = worse_citation_validity(status, "stale")
            reasons.append("local evidence changed since the stored integrity hash")

        if source_ref.startswith(("knowledge/", "archive/knowledge/")):
            target_object = get_knowledge_object_by_canonical_path(connection, source_ref)
            if target_object is None:
                status = worse_citation_validity(status, "unverified")
                reasons.append("cited knowledge object is not present in runtime")
            else:
                target_status = str(target_object["object_lifecycle_state"])
                if target_status in {"deprecated", "archived"}:
                    status = worse_citation_validity(status, "stale")
                    reasons.append(f"cited knowledge object is {target_status}")
                if parse_iso_date(target_object["updated_date"]) > object_last_reviewed:
                    status = worse_citation_validity(status, "stale")
                    reasons.append(
                        "cited knowledge object changed after the current object was last reviewed"
                    )
        return status, reasons

    if captured_at is None:
        status = worse_citation_validity(status, "unverified")
        reasons.append("non-local evidence lacks captured_at")
        return status, reasons

    captured_on = parse_iso_date_or_datetime(captured_at)
    if cadence_days is not None and captured_on + dt.timedelta(days=cadence_days) < as_of:
        status = worse_citation_validity(status, "stale")
        reasons.append("captured evidence is older than the review cadence window")

    if integrity_hash is None:
        status = worse_citation_validity(status, "unverified")
        reasons.append("non-local evidence lacks integrity_hash")

    return status, reasons


def scan_citations(
    connection: sqlite3.Connection,
    *,
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date | None = None,
    object_ids: list[str] | None = None,
    persist: bool = True,
    root_path: Path = ROOT,
) -> CitationScanResult:
    rows = list_current_citations(connection, tuple(object_ids) if object_ids else None)
    findings: list[CitationFinding] = []
    counts_by_object: dict[str, dict[str, int]] = {}
    scan_date = as_of or dt.date.today()

    for row in rows:
        status, reasons = classify_citation(
            connection,
            row,
            taxonomies=taxonomies,
            as_of=scan_date,
            root_path=root_path,
        )
        if persist and status != row["validity_status"]:
            update_citation_validity_status(connection, str(row["citation_id"]), status)

        object_counts = counts_by_object.setdefault(
            str(row["object_id"]),
            {"verified": 0, "unverified": 0, "stale": 0, "broken": 0},
        )
        object_counts[status] += 1

        if reasons or status != row["validity_status"]:
            findings.append(
                CitationFinding(
                    citation_id=str(row["citation_id"]),
                    object_id=str(row["object_id"]),
                    revision_id=str(row["revision_id"]),
                    validity_status=status,
                    source_ref=source_ref_for_row(row),
                    reason="; ".join(reasons) if reasons else f"status set to {status}",
                )
            )

    return CitationScanResult(
        scanned_count=len(rows),
        findings=findings,
        counts_by_object=counts_by_object,
    )


def source_ref_for_row(row: sqlite3.Row) -> str:
    return str(row["source_ref"] or "")


def run(
    connection: sqlite3.Connection,
    *,
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date | None = None,
    root_path: Path = ROOT,
) -> CitationScanResult:
    return scan_citations(
        connection, taxonomies=taxonomies, as_of=as_of, persist=True, root_path=root_path
    )
