# AGENTS.md

This file governs work under `src/papyrus/jobs/`.

## Purpose

Jobs build, export, or report on repository state.
They must preserve canonical-versus-derived boundaries, reproducibility, and low-risk local operation.

## Output Rules

- Derived artifacts must write only to explicit generated-output roots.
- Do not hardcode tests or helper flows to mutate canonical repository roots when a temporary output root is sufficient.
- If a build job needs a different destination for tests or sandbox runs, add an explicit argument and keep the default behavior unchanged for normal operators.
- Never make generated output authoritative. If an export is wrong, fix the generator or the source data.

## Safety Rules

- Jobs that delete or replace generated output must scope that deletion to the configured derived-artifact root only.
- Avoid hidden writes outside `build/`, `generated/`, or an explicitly requested temporary directory.
- Keep export behavior reproducible from repository source and declared runtime inputs.

## Maintenance Rules

- When changing a job entrypoint or CLI argument, update the matching script wrapper, tests, and relevant docs in the same task.
- When a job depends on repository constants for output paths, make test isolation explicit rather than relying on the working tree state.
