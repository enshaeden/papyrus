# Papyrus Docs

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Use this documentation set to operate Papyrus from the repository as it exists now.

Runtime/workspace contract:
- The committed seed corpus was removed from this repository.
- Canonical source, when used, lives in an explicit workspace source tree such as `knowledge/` and `archive/knowledge/`.
- Read-only runtime starts from the runtime DB plus retained derived artifacts.
- Source-backed authoring, ingest conversion, and source sync are workspace-only operations.

## Orientation

- [Getting started](getting-started.md): shortest path to a working local runtime and the main entrypoints.

## Playbooks

- [Read](read.md): search, inspect trust posture, follow related objects, and spot stale or suspect knowledge.
- [Write](write.md): start primary templates, continue governed revisions, review imports before draft creation, and prepare review handoff.
- [Review And Health](manage.md): review queues, inspect revision history and audit trails, and run content-health checks.

## System Model

- [System model](system-model.md): the object, revision, trust, citation, validation, and runtime/build rules in one place, including the primary template scope and advanced blueprint boundary.
- [Operator web UI](operator-web-ui.md): server-rendered operator shell for Home, Read, Write, Import, Review, and supporting health or audit workflows.
- [Operator readiness](operator-readiness.md): implementation hardening notes, demo/runtime path, operator CLI parity, and structured findings.
- [Placeholder glossary](placeholder-glossary.md): stable definitions for the sanitization placeholders still used across source and migration artifacts.

## Supporting Reference

- [Governance and decisions](../decisions/index.md): the single authoritative index for Papyrus governance records.
