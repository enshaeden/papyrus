# AGENTS.md

This file governs work under `docs/`.

## Purpose

`docs/` explains the system that exists now and links to the decisions that currently govern it.
Use it to reduce drift, not to preserve transitional language after the implementation moved on.

## Rules

- Update the existing source-of-truth document instead of creating a parallel note when a valid document already exists.
- When code and docs disagree, either fix the code in the same task or update the doc to match the shipped behavior. Do not leave both versions in place.
- Treat route paths, CLI commands, workflow state names, and file paths as contract text. Verify them against the repo before keeping them in docs.
- Mark compatibility shims, temporary redirects, demo-only overlays, and future work explicitly. Do not let them read like the stable product contract.
- For experience docs, use the active role-scoped model as the authority unless a decision record says otherwise.
- Do not describe actor switching, shared shells, or hidden cross-role controls as shipped behavior unless you can verify they still exist and are intended to ship.
- Keep examples runnable. If a command or route changed, update every nearby example in the same edit.

## Decision Records

- `decisions/` records authoritative experience and governance decisions.
- When updating one decision that depends on another, check the linked records for state-name or route-model drift.
- Do not mix lifecycle, review, draft-progress, and flag workflow terms into one status list.

## Validation

- Run the documentation contract tests when changing stable web, workflow, or command descriptions.
- If a documentation claim cannot be verified from code, tests, logs, config, or a decision record, remove it or label it explicitly as pending.
