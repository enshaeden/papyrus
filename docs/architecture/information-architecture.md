# Information Architecture

Papyrus separates canonical authored source, runtime logic, runtime state, and derived exports.

## Directory Contract

- `knowledge/`: active canonical authored knowledge source files.
- `archive/knowledge/`: archived canonical authored knowledge source files.
- `docs/`: explanatory architecture, governance, and workflow documentation.
- `decisions/`: ADR-style structural rationale.
- `src/papyrus/`: application package. This is where domain, application, infrastructure, interface, and job logic belongs.
- `schemas/`: repository policy and source-schema definitions.
- `taxonomies/`: controlled vocabularies.
- `templates/`: approved source templates only.
- `scripts/`: thin operator entrypoints and compatibility shims.
- `generated/`: derived export inputs.
- `build/`: rebuildable local runtime artifacts.
- `site/`: rendered static export output.

## Runtime Boundary

Papyrus now distinguishes:

- authored source
- application logic
- runtime projections
- export surfaces

The repository previously centered the runtime around Markdown articles plus script-local helper code. That center of gravity is being replaced with a knowledge-object-oriented application package under `src/papyrus/`.

## Placement Rubric

- Put operator-executed knowledge in `knowledge/` or `archive/knowledge/`.
- Put control-plane architecture and contributor guidance in `docs/`.
- Put structural rationale and migration decisions in `decisions/`.
- Put durable reusable runtime logic in `src/papyrus/`, not in ad hoc scripts.

## Derived Artifact Rule

- Generated pages under `generated/`, SQLite files under `build/`, and rendered output under `site/` are derived artifacts.
- Derived artifacts must remain reproducible from source and the application package.
- Generated artifacts are inspectable and useful, but they are never authoritative.
