# AGENTS.md

This file governs work under `knowledge/`.

## Purpose

`knowledge/` explains the system that exists now and links to the decisions that currently govern it.
Folders and files contained with knowledge serve the express purpose of acting as the system knowledge base.
Knowledge objects (articles) in `knowledge/` should explain things like:
- Papyrus system design
- Practical use cases of Papyrus
- Papyrus system troubleshooting
- How to navigate Papyrus as a a Reader, Operator, or Admin
- Papyrus API guidance or use
- When to use the API, CLI, or web UI for Papyrus
Use it to reduce drift, not to preserve transitional language after the implementation moved on.

## Rules

- Keep `knowledge/` focused on the system that exists now.
- Update the existing source-of-truth document instead of creating a parallel note when a valid document already exists.
- Remove or rewrite stale implementation language when the product changes. Do not preserve transitional wording once it no longer describes the shipped system.
- When code and docs disagree, either fix the code in the same task or update the doc to match shipped behavior. Do not leave both versions in place.
- Treat route paths, CLI commands, workflow state names, API fields, and file paths as contract text. Verify them against the repo before keeping them in docs.
- Mark compatibility shims, temporary redirects, demo-only overlays, deprecated flows, and future work explicitly. Do not let them read like the stable product contract.
- For experience guidance, use the active role-scoped model as the authority unless a decision record says otherwise.
- Do not describe actor switching, shared shells, hidden cross-role controls, or legacy article-centric behavior as shipped unless verified in the current system and intended to remain.
- Keep examples runnable and current. If a command, route, payload, or workflow changed, update every nearby example in the same edit.
- Prefer explanation of durable system behavior over implementation-era narrative, migration notes, or speculative intent.
- Use `knowledge/` to reduce drift in the live system, not to archive how the system used to work.

## Decision Records

- `decisions/` contains the authoritative governance and experience decisions that shape the current system.
- `knowledge/` should explain the system in terms consistent with those decisions and link to them where they govern behavior, scope, or terminology.
- When updating one decision that depends on another, check linked records for route-model, role-model, schema, and terminology drift.
- If a decision has been superseded, deprecated, or narrowed, reflect that clearly in both the record and any affected knowledge docs.
- Do not mix lifecycle, review, draft-progress, publication, and flag workflow terms into one status model unless a decision explicitly defines that model.

## Validation

- Run the documentation contract tests when changing stable web behavior, workflow descriptions, CLI commands, API guidance, or other contract text.
- Verify documentation claims against code, tests, config, schemas, logs, or a decision record before keeping them.
- If a claim cannot be verified, remove it or label it explicitly as pending.
- When changing terminology, routes, commands, or workflow states, update adjacent docs in the same task so the knowledge base remains internally consistent.
- Treat broken examples, stale screenshots, and outdated path references as drift and fix or remove them before merging.
