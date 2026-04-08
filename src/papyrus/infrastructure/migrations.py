from __future__ import annotations

import sqlite3


def apply_runtime_schema(connection: sqlite3.Connection, has_fts5: bool) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_objects (
            object_id TEXT PRIMARY KEY,
            object_type TEXT NOT NULL,
            legacy_type TEXT,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            status TEXT NOT NULL,
            owner TEXT NOT NULL,
            team TEXT NOT NULL,
            canonical_path TEXT NOT NULL UNIQUE,
            source_type TEXT NOT NULL,
            source_system TEXT NOT NULL,
            source_title TEXT NOT NULL,
            created_date TEXT NOT NULL,
            updated_date TEXT NOT NULL,
            last_reviewed TEXT NOT NULL,
            review_cadence TEXT NOT NULL,
            trust_state TEXT NOT NULL,
            current_revision_id TEXT,
            tags_json TEXT NOT NULL,
            systems_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_revisions (
            revision_id TEXT PRIMARY KEY,
            object_id TEXT NOT NULL REFERENCES knowledge_objects(object_id),
            revision_number INTEGER NOT NULL,
            revision_state TEXT NOT NULL,
            source_path TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            body_markdown TEXT NOT NULL,
            normalized_payload_json TEXT NOT NULL,
            legacy_metadata_json TEXT NOT NULL,
            imported_at TEXT NOT NULL,
            change_summary TEXT,
            UNIQUE(object_id, revision_number)
        );

        CREATE TABLE IF NOT EXISTS citations (
            citation_id TEXT PRIMARY KEY,
            revision_id TEXT NOT NULL REFERENCES knowledge_revisions(revision_id),
            claim_anchor TEXT,
            source_type TEXT NOT NULL,
            source_ref TEXT NOT NULL,
            source_title TEXT NOT NULL,
            note TEXT,
            excerpt TEXT,
            captured_at TEXT,
            validity_status TEXT NOT NULL,
            integrity_hash TEXT,
            evidence_snapshot_path TEXT,
            evidence_expiry_at TEXT,
            evidence_last_validated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS services (
            service_id TEXT PRIMARY KEY,
            service_name TEXT NOT NULL UNIQUE,
            canonical_object_id TEXT,
            owner TEXT,
            team TEXT,
            status TEXT NOT NULL,
            service_criticality TEXT NOT NULL,
            support_entrypoints_json TEXT NOT NULL,
            dependencies_json TEXT NOT NULL,
            common_failure_modes_json TEXT NOT NULL,
            source TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS relationships (
            relationship_id TEXT PRIMARY KEY,
            source_entity_type TEXT NOT NULL,
            source_entity_id TEXT NOT NULL,
            target_entity_type TEXT NOT NULL,
            target_entity_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            provenance TEXT NOT NULL,
            relationship_strength REAL NOT NULL,
            relationship_direction TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS review_assignments (
            assignment_id TEXT PRIMARY KEY,
            object_id TEXT NOT NULL,
            revision_id TEXT,
            reviewer TEXT NOT NULL,
            state TEXT NOT NULL,
            assigned_at TEXT NOT NULL,
            due_at TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS validation_runs (
            run_id TEXT PRIMARY KEY,
            run_type TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            status TEXT NOT NULL,
            finding_count INTEGER NOT NULL,
            details_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            actor TEXT NOT NULL,
            object_id TEXT,
            revision_id TEXT,
            details_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            source TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            actor TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS search_documents (
            object_id TEXT PRIMARY KEY REFERENCES knowledge_objects(object_id),
            revision_id TEXT NOT NULL REFERENCES knowledge_revisions(revision_id),
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            object_type TEXT NOT NULL,
            legacy_type TEXT,
            status TEXT NOT NULL,
            owner TEXT NOT NULL,
            team TEXT NOT NULL,
            trust_state TEXT NOT NULL,
            approval_state TEXT NOT NULL,
            freshness_rank INTEGER NOT NULL,
            citation_health_rank INTEGER NOT NULL,
            ownership_rank INTEGER NOT NULL,
            path TEXT NOT NULL,
            search_text TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_objects_type_status ON knowledge_objects(object_type, status);
        CREATE INDEX IF NOT EXISTS idx_revisions_object ON knowledge_revisions(object_id);
        CREATE INDEX IF NOT EXISTS idx_citations_revision ON citations(revision_id);
        CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_entity_type, source_entity_id);
        CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_entity_type, target_entity_id);
        CREATE INDEX IF NOT EXISTS idx_services_name ON services(service_name);
        CREATE INDEX IF NOT EXISTS idx_search_documents_status ON search_documents(status);
        CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_events_occurred_at ON events(occurred_at);
        """
    )

    if has_fts5:
        connection.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_search USING fts5(
                object_id UNINDEXED,
                title,
                summary,
                body,
                tags,
                systems,
                services
            )
            """
        )
