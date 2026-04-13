# Papyrus Docs

Papyrus is a governed knowledge management database that provides end users with dependable content, while IT operators maintain backend authorship and oversight.

Use this documentation set to operate Papyrus from the repository as it exists now.

## Orientation

- [Getting started](getting-started.md): shortest path to a working local runtime and the main entrypoints.

## Playbooks

- [Content](playbooks/read.md): search, inspect trust posture, follow related objects, and spot stale or suspect knowledge.
- [Authoring](playbooks/write.md): start primary templates, continue governed revisions, review imports before draft creation, and prepare review handoff.
- [Oversight](playbooks/manage.md): review queues, inspect revision history and audit trails, and run content-health checks.

## System Model

- [System model](reference/system-model.md): the object, revision, trust, citation, validation, runtime, and export rules in one place, including the primary template scope and advanced blueprint boundary.
- [Operator web UI](reference/operator-web-ui.md): server-rendered operator shell for content, primary template authoring, import review, advanced authoring, review, and oversight workflows.
- [Operator readiness](reference/operator-readiness.md): implementation hardening notes, demo/runtime path, operator CLI parity, and structured findings.
- [Placeholder glossary](reference/placeholder-glossary.md): stable definitions for the sanitization placeholders still used across source and migration artifacts.

## Supporting Reference

- [Governance and decisions](../decisions/index.md): the single authoritative index for Papyrus governance records.
- [Migration rationale](migration/seed-migration-rationale.md): historical reference for the sanitized seed and import boundary.
